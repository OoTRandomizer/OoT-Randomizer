from __future__ import annotations
from dataclasses import dataclass
from os import path, walk
from typing import Any, Optional
import xml.etree.ElementTree as ET
import logging

from FileDataRelocator import segment_address_offset, create_segment_address, DataRecord, FileDataRelocator, FileType
from Utils import data_path
from SceneList import SCENE_TABLE, RecordType, SCENE_EXTERNAL_REFERENCES, SCENE_TABLE_ADDRESS
from Cutscenes import Cutscene, CutsceneCommandID, ACTOR_CUE_COMMANDS, GENERIC_COMMANDS, CAMERA_COMMANDS, NULL_COMMANDS
from FileList import SCENE_AND_ROOM_FILES
from Rom import Rom, Vec3s
from SaveContext import SceneIDs

class SceneFileAddressException(Exception):
    def __init__(self, file: FileDataRelocator, segment: int, cursor: int, resource_name: str) -> None:
        super().__init__(f'Unsupported room segment address segment 0x{segment:0>2x} for {resource_name} address at offset 0x{cursor - file.start:0>6x} (address 0x{cursor:0>8x}) in {file.name}. Offsets are only supported within the current scene file (segment 0x02).')


class RoomFileAddressException(Exception):
    def __init__(self, file: FileDataRelocator, segment: int, cursor: int, resource_name: str) -> None:
        super().__init__(f'Unsupported room segment address segment 0x{segment:0>2x} for {resource_name} address at offset 0x{cursor - file.start:0>6x} (address 0x{cursor:0>8x}) in {file.name}. Offsets are only supported within the current room file (segment 0x03) or parent scene file (segment 0x02).')


def str_to_s16(raw_bytes: str) -> int:
    return int.from_bytes(int(raw_bytes, 16).to_bytes(2, 'big', signed=False), 'big', signed=True)


def s32_to_u32(num: int) -> int:
    return int.from_bytes(num.to_bytes(4, 'big', signed=True), 'big', signed=False)


class SceneDataRelocator(FileDataRelocator):
    def __init__(self, rom: Rom, name: str, start: int, end: int) -> None:
        self.rooms: list[RoomDataRelocator] = []
        self.headers: list[Optional[SceneHeader]] = [None]
        self.id: int = -1
        self.description: str = ''
        for scene_id, scene_name, scene_description, _, _, _, _, _, _, _, _ in SCENE_TABLE.values():
            if scene_name == name:
                self.id = scene_id
                self.description = scene_description
                break
        if scene_id == -1:
            raise Exception(f'Could not locate scene file {name} in vanilla scene table')
        super().__init__(rom, name, start, end, FileType.Scene)

    def parse_file_header(self, alternate: Optional[int] = None) -> DataRecord:
        self.headers[0] = SceneHeader.decode(self)
        return self.headers[0]

    def get_offset(self, cursor: int) -> tuple[int, Optional[FileDataRelocator]]:
        segment = self.rom.read_byte(cursor)
        offset = self.rom.read_int24(cursor + 1)
        if segment == 0x00 and offset == 0:
            return (0, None)  # null
        if segment == 0x02:
            return (offset, self)  # scene
        return (-1, None)  # unknown

    # Assumes MQ Dungeons only change the main/first header
    def apply_mq_patch(self, patch: dict) -> None:
        scene = self.headers[0]
        if 'TActors' in patch.keys() and len(patch['TActors']) > 0:
            scene.transition_actor_list.apply_patch(patch['TActors'])
        if 'Paths' in patch.keys() and len(patch['Paths']) > 0:
            scene.path_list = ScenePathList.from_json(self, patch['Paths'])
        else:
            scene.path_list = None
        if 'ColDelta' in patch.keys():
            scene.collision_header.bgCamList.apply_patch(patch['ColDelta']['Cams'])
            scene.collision_header.polyList.apply_patch(patch['ColDelta']['Polys'])
            scene.collision_header.surfaceTypeList.apply_patch(patch['ColDelta']['PolyTypes'])
        if 'Rooms' in patch.keys():
            for room_data in patch['Rooms']:
                room: RoomHeader = self.rooms[room_data['Id']].headers[0]
                if 'Objects' in room_data.keys():
                    if room.object_list == None:
                        room.object_list = RoomObjectList(room.file, room.file.end + 1)
                    room.object_list.apply_patch(room_data['Objects'])
                if 'Actors' in room_data.keys():
                    if room.actor_list == None:
                        room.actor_list = RoomActorList(room.file, room.file.end + 2)
                    room.actor_list.apply_patch(room_data['Actors'])
        if self.id == SceneIDs.ICE_CAVERN:
            # Delete alternate header command.
            # This does not delete the alternate headers
            # themselves, but they become unused data when
            # not referenced in the main header
            self.headers[0].alt_header_list = None
        if self.id == SceneIDs.SPIRIT_TEMPLE:
            # Create an alternate room setup for the
            # shortcut hallway as adult. Modify the main header
            # so that the silver block is always outside the
            # hole to permit shooting the switch to drop the chest there.
            room6 = self.rooms[6]
            adult_header = room6.headers[0].copy()
            room6.headers[0].alt_header_list = SceneAltHeaderList(room6, adult_header.offset + 1)
            room6.headers[0].alt_header_list.headers.append(None)
            room6.headers[0].alt_header_list.headers.append(adult_header)
            room6.headers[0].alt_header_list.headers.append(None)
            room6.headers[0].alt_header_list.headers.append(None)
            room6.headers[0].alt_header_list.headers.append(None)
            room6.headers[0].alt_header_list.headers.append(None)
            room6.headers.extend(room6.headers[0].alt_header_list.headers)
            room6.headers[0].actor_list.actors.pop(0)


    def write(self, rom: Rom) -> int:
        aligned_file_end = super().write(rom)
        addresses = bytearray()
        addresses.extend(self.start.to_bytes(4, 'big'))
        addresses.extend(self.end.to_bytes(4, 'big'))
        rom.write_bytes(SCENE_TABLE_ADDRESS + self.id * 0x14, addresses)
        return aligned_file_end

    def to_json(self) -> dict[str, Any]:
        return {
            **super().to_json(),
            'rooms': [x.to_json() for x in self.rooms],
        }


# Always 16 byte aligned in vanilla
class SceneHeader(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> None:
        super().__init__(file, RecordType.SceneHeader, file.start, offset, length)
        self.alt_header_list: SceneAltHeaderList = None
        self.sound_settings: SceneSoundSettings = None
        self.room_list: SceneRoomList = None
        self.transition_actor_list: SceneTransitionActorList = None
        self.misc_settings: SceneMiscSettings = None
        self.collision_header: SceneCollisionHeader = None
        self.entrance_list: SceneEntranceList = None
        self.special_objects: SceneSpecialSettings = None
        self.path_list: ScenePathList = None
        self.spawn_points: SceneSpawnPointList = None
        self.skybox_settings: SceneSkyboxSettings = None
        self.exit_list: SceneExitList = None
        self.light_settings: SceneLightSettingsList = None
        self.cutscene_data: SceneCutsceneData = None
        self.actor_list: RoomActorList = None
        self.align = 16

    @staticmethod
    def decode(file: FileDataRelocator, offset: int = 0, length: Optional[int] = -1) -> SceneHeader:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.SceneHeader)
        if existing_record is not None:
            return existing_record
        setup = SceneHeader(file, offset, length)
        command = 0
        setup_start = setup.start + setup.offset
        cursor = setup_start
        # Process the current setup header.
        # Command byte conditions are listed in the same order as
        # the convention used in the rom.
        while command != 0x14: # header terminator
            command = file.rom.read_byte(cursor)
            if command == 0x18: # Alternate header list
                list_offset, list_file = file.get_offset(cursor + 0x04)
                if list_file is None:
                    raise SceneFileAddressException(file, file.rom.read_byte(cursor + 0x04), cursor + 0x04, 'alternate header list')
                setup.alt_header_list = SceneAltHeaderList.decode(list_file, list_offset)
                file.add_record(list_file.data_records, setup.alt_header_list)
            elif command == 0x15: # sound settings
                setup.sound_settings = SceneSoundSettings.decode(file.rom, cursor)
            elif command == 0x04: # room list
                list_offset, list_file = file.get_offset(cursor + 0x04)
                if list_file is None:
                    raise SceneFileAddressException(file, file.rom.read_byte(cursor + 0x04), cursor + 0x04, 'room list')
                num_rooms = file.rom.read_byte(cursor + 0x01)
                setup.room_list = SceneRoomList.decode(list_file, list_offset, num_rooms * 0x08)
                file.add_record(list_file.data_records, setup.room_list)
            elif command == 0x0E: # Transition actor list
                list_offset, list_file = file.get_offset(cursor + 0x04)
                if list_file is None:
                    raise SceneFileAddressException(file, file.rom.read_byte(cursor + 0x04), cursor + 0x04, 'transition actor list')
                num_actors = file.rom.read_byte(cursor + 0x01)
                setup.transition_actor_list = SceneTransitionActorList.decode(list_file, list_offset, num_actors * 0x10)
                file.add_record(list_file.data_records, setup.transition_actor_list)
            elif command == 0x19: # Misc settings
                setup.misc_settings = SceneMiscSettings.decode(file.rom, cursor)
            elif command == 0x03: # Collision Header
                header_offset, header_file = file.get_offset(cursor + 0x04)
                if header_file is None:
                    raise SceneFileAddressException(file, file.rom.read_byte(cursor + 0x04), cursor + 0x04, 'collision header list')
                setup.collision_header = SceneCollisionHeader.decode(file, header_offset, 0x2C)
                file.add_record(header_file.data_records, setup.collision_header)
            elif command == 0x06: # Entrance List
                # Size of entrance list is undefined.
                # ZAPD parses all data from the entrance
                # list segment address to the next resource
                # segment address, or the end of the file.
                list_offset, list_file = file.get_offset(cursor + 0x04)
                if list_file is None:
                    raise SceneFileAddressException(file, file.rom.read_byte(cursor + 0x04), cursor + 0x04, 'entrance list')
                setup.entrance_list = SceneEntranceList.decode(list_file, list_offset)
                file.add_record(list_file.data_records, setup.entrance_list)
            elif command == 0x07: # Special object
                setup.special_objects = SceneSpecialSettings.decode(file.rom, cursor)
            elif command == 0x0D: # Path list
                # Most scenes only have 1 path list, if any.
                # Some have a second. None of the list lengths
                # are defined in the ROM. Some path lists are
                # defined in the ZAPD XML files and will have
                # valid records defined before the header is
                # processed.
                list_offset, list_file = file.get_offset(cursor + 0x04)
                if list_file is None:
                    raise SceneFileAddressException(file, file.rom.read_byte(cursor + 0x04), cursor + 0x04, 'path list')
                setup.path_list = ScenePathList.decode(list_file, list_offset)
                file.add_record(list_file.data_records, setup.path_list)
            elif command == 0x00: # Spawn point list
                list_offset, list_file = file.get_offset(cursor + 0x04)
                num_actors = file.rom.read_byte(cursor + 0x01)
                if list_file is None:
                    raise SceneFileAddressException(file, file.rom.read_byte(cursor + 0x04), cursor + 0x04, 'spawn point list')
                setup.spawn_points = SceneSpawnPointList.decode(list_file, list_offset, num_actors * 0x10)
                file.add_record(list_file.data_records, setup.spawn_points)
            elif command == 0x11: # Skybox settings
                setup.skybox_settings = SceneSkyboxSettings.decode(file.rom, cursor)
            elif command == 0x13: # Exit List
                # Same deal as the entrance list
                list_offset, list_file = file.get_offset(cursor + 0x04)
                if list_file is None:
                    raise SceneFileAddressException(file, file.rom.read_byte(cursor + 0x04), cursor + 0x04, 'exit list')
                setup.exit_list = SceneExitList.decode(list_file, list_offset)
                file.add_record(list_file.data_records, setup.exit_list)
            elif command == 0x0F: # Lighting settings
                list_offset, list_file = file.get_offset(cursor + 0x04)
                num_lights = file.rom.read_byte(cursor + 0x01)
                if list_file is None:
                    raise SceneFileAddressException(file, file.rom.read_byte(cursor + 0x04), cursor + 0x04, 'light settings list')
                setup.light_settings = SceneLightSettingsList.decode(list_file, list_offset, num_lights * 0x16)
                file.add_record(list_file.data_records, setup.light_settings)
            elif command == 0x17: # Cutscene List
                # Not all cutscenes are listed in scene headers.
                # Unreferenced cutscenes are defined in the XMLs
                # and do not need to be linked here.
                cutscene_offset, cutscene_file = file.get_offset(cursor + 0x04)
                if cutscene_file is None:
                    raise SceneFileAddressException(file, file.rom.read_byte(cursor + 0x04), cursor + 0x04, 'cutscene data')
                setup.cutscene_data = SceneCutsceneData.decode(cutscene_file, cutscene_offset)
                file.add_record(cutscene_file.data_records, setup.cutscene_data)
            elif command == 0x01: # actor list
                # Scene files do not typically have actor lists,
                # but the following do:
                #   Spirit Temple
                #   Gerudo's Fortress
                #   Death Mountain Trail
                #   Goron City
                list_offset, list_file = file.get_offset(cursor + 0x04)
                if list_file is None:
                    raise SceneFileAddressException(file, file.rom.read_byte(cursor + 0x04), cursor + 0x04, 'actor list')
                num_actors = file.rom.read_byte(cursor + 0x01)
                setup.actor_list = RoomActorList.decode(list_file, list_offset, num_actors * 0x10)
                file.add_record(list_file.data_records, setup.actor_list)
            elif command == 0x14: # end list
                pass
            else:
                raise Exception(
                    f'Unexpected command 0x{command:02X} at 0x{cursor - setup.start:08X} in {file.name}')
            cursor += 0x08
        setup.length = cursor - setup_start
        setup.refresh_rom_data()
        return setup

    def encode(self) -> bytearray:
        bytes = bytearray()
        if self.alt_header_list is not None:
            bytes.extend(int.to_bytes(0x18 << 0x18, 4, 'big'))
            bytes.extend(self.alt_header_list.get_segment_address_bytes())
        if self.sound_settings is not None:
            bytes.extend(int.to_bytes(0x15, 1, 'big'))
            bytes.extend(self.sound_settings.specID.to_bytes(1, 'big'))
            bytes.extend(int.to_bytes(0, 4, 'big'))
            bytes.extend(self.sound_settings.natureAmbienceId.to_bytes(1, 'big'))
            bytes.extend(self.sound_settings.seqId.to_bytes(1, 'big'))
        if self.room_list is not None:
            bytes.extend(int.to_bytes(0x04, 1, 'big'))
            bytes.extend(len(self.room_list.rooms).to_bytes(1, 'big'))
            bytes.extend(int.to_bytes(0, 2, 'big'))
            bytes.extend(self.room_list.get_segment_address_bytes())
        if self.transition_actor_list is not None:
            bytes.extend(int.to_bytes(0x0E, 1, 'big'))
            bytes.extend(len(self.transition_actor_list.actors).to_bytes(1, 'big'))
            bytes.extend(int.to_bytes(0, 2, 'big'))
            bytes.extend(self.transition_actor_list.get_segment_address_bytes())
        if self.misc_settings is not None:
            bytes.extend(int.to_bytes(0x19, 1, 'big'))
            bytes.extend(self.misc_settings.sceneCamType.to_bytes(1, 'big'))
            bytes.extend(int.to_bytes(0, 5, 'big'))
            bytes.extend(self.misc_settings.worldMapLocation.to_bytes(1, 'big'))
        if self.collision_header is not None:
            bytes.extend(int.to_bytes(0x03 << 0x18, 4, 'big'))
            bytes.extend(self.collision_header.get_segment_address_bytes())
        if self.entrance_list is not None:
            bytes.extend(int.to_bytes(0x06 << 0x18, 4, 'big'))
            bytes.extend(self.entrance_list.get_segment_address_bytes())
        if self.special_objects is not None:
            bytes.extend(int.to_bytes(0x07, 1, 'big'))
            bytes.extend(self.special_objects.naviQuestHintFileId.to_bytes(1, 'big'))
            bytes.extend(int.to_bytes(0, 4, 'big'))
            bytes.extend(self.special_objects.keepObjectId.to_bytes(2, 'big'))
        if self.path_list is not None:
            bytes.extend(int.to_bytes(0x0D << 0x18, 4, 'big'))
            bytes.extend(self.path_list.get_segment_address_bytes())
        if self.spawn_points is not None:
            bytes.extend(int.to_bytes(0x00, 1, 'big'))
            bytes.extend(len(self.spawn_points.spawns).to_bytes(1, 'big'))
            bytes.extend(int.to_bytes(0, 2, 'big'))
            bytes.extend(self.spawn_points.get_segment_address_bytes())
        if self.actor_list is not None:
            bytes.extend(int.to_bytes(0x01, 1, 'big'))
            bytes.extend(len(self.actor_list.actors).to_bytes(1, 'big'))
            bytes.extend(int.to_bytes(0, 2, 'big'))
            bytes.extend(self.actor_list.get_segment_address_bytes())
        if self.skybox_settings is not None:
            bytes.extend(int.to_bytes(0x11, 1, 'big'))
            bytes.extend(int.to_bytes(0, 3, 'big'))
            bytes.extend(self.skybox_settings.skyboxID.to_bytes(1, 'big'))
            bytes.extend(self.skybox_settings.skyboxConfig.to_bytes(1, 'big'))
            bytes.extend(self.skybox_settings.envLightMode.to_bytes(1, 'big'))
            bytes.extend(int.to_bytes(0, 1, 'big'))
        if self.exit_list is not None:
            bytes.extend(int.to_bytes(0x13 << 0x18, 4, 'big'))
            bytes.extend(self.exit_list.get_segment_address_bytes())
        if self.light_settings is not None:
            bytes.extend(int.to_bytes(0x0F, 1, 'big'))
            bytes.extend(len(self.light_settings.lights).to_bytes(1, 'big'))
            bytes.extend(int.to_bytes(0, 2, 'big'))
            bytes.extend(self.light_settings.get_segment_address_bytes())
        if self.cutscene_data is not None:
            bytes.extend(int.to_bytes(0x17 << 0x18, 4, 'big'))
            bytes.extend(self.cutscene_data.get_segment_address_bytes())
        bytes.extend(int.to_bytes(0x14 << 0x18, 4, 'big'))
        bytes.extend(int.to_bytes(0, 4, 'big'))
        return bytes


# Always 8 byte aligned in vanilla, but may be artifact of only coming after the first header
# with 8 byte long commands
class SceneAltHeaderList(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> None:
        super().__init__(file, RecordType.AlternateHeaders, file.start, offset, length, True)
        self.headers: list[Optional[SceneHeader | RoomHeader]] = []
        self.align = 8

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> SceneAltHeaderList:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.AlternateHeaders)
        if existing_record is not None:
            return existing_record
        return SceneAltHeaderList(file, offset, length)

    def decode_late(self) -> None:
        cursor = self.start + self.offset
        self.length = self.file.get_record_length_from_neighbor(self)
        self.refresh_rom_data()
        num_headers = int(self.length / 0x04)
        for _ in range(0, num_headers):
            header_offset, header_file = self.file.get_offset(cursor)
            if header_offset == 0 and header_file is None:
                self.headers.append(None) # NULL entry
            elif header_file is None:
                raise SceneFileAddressException(self.file, self.file.rom.read_byte(cursor), cursor, 'alternate header')
            else:
                if self.file.type == FileType.Scene:
                    setup = SceneHeader.decode(header_file, header_offset)
                elif self.file.type == FileType.Room:
                    setup = RoomHeader.decode(header_file, header_offset)
                else:
                    raise Exception(f'Unsupported file type {self.file.type} for alternate header list parsing in {self.file.name} at offset 0x{self.offset:0>6x}.')
                self.file.add_record(header_file.data_records, setup)
                self.headers.append(setup)
            cursor += 0x04
        if isinstance(self.file, SceneDataRelocator) or isinstance(self.file, RoomDataRelocator):
            if len(self.file.headers) > 1:
                raise Exception(f'Unable to parse multiple alternate header lists in {self.file.name}')
            self.file.headers.extend(self.headers)
        self.delay_parsing = False

    def encode(self) -> bytearray:
        bytes = bytearray()
        for setup in self.headers:
            if setup is None:
                bytes.extend(int.to_bytes(0, 4, 'big'))
            else:
                bytes.extend(setup.get_segment_address_bytes())
        return bytes


# Data only, part of the scene header
class SceneSoundSettings():
    def __init__(self, specId: int, natureAmbienceId: int, seqId: int) -> None:
        self.specID: int = specId
        self.natureAmbienceId: int = natureAmbienceId
        self.seqId: int = seqId

    @staticmethod
    def decode(rom: Rom, scene_cmd_addr: int) -> SceneSoundSettings:
        return SceneSoundSettings(
            rom.read_byte(scene_cmd_addr + 1),
            rom.read_byte(scene_cmd_addr + 6),
            rom.read_byte(scene_cmd_addr + 7),
        )

    def encode(self) -> bytearray:
        bytes: bytearray = bytearray()
        bytes.extend(int.to_bytes(0x15, 1, 'big'))
        bytes.extend(self.specID.to_bytes(1, 'big'))
        bytes.extend(bytearray([0, 0, 0, 0]))
        bytes.extend(self.natureAmbienceId.to_bytes(1, 'big'))
        bytes.extend(self.seqId.to_bytes(1, 'big'))
        return bytes


# 4 byte aligned in vanilla
class SceneRoomList(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> None:
        super().__init__(file, RecordType.RoomList, file.start, offset, length)
        self.rooms: list[RoomDataRelocator] = []

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int) -> SceneRoomList:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.RoomList)
        if existing_record is not None:
            return existing_record
        if not isinstance(file, SceneDataRelocator):
            raise Exception(f'Cannot process room list in non-scene file {file.name}')
        num_rooms = int(length / 0x08)
        room_list = SceneRoomList(file, offset, length)
        cursor = room_list.start + room_list.offset
        for i in range(0, num_rooms):
            room_start = file.rom.read_int32(cursor)
            room_end = file.rom.read_int32(cursor + 0x04)
            room_entry: RoomDataRelocator = None
            for room in file.rooms:
                if room.start == room_start and room.end == room_end:
                    room_entry = room
                    break
            if room_entry is None:
                room_entry = RoomDataRelocator(file.rom, f'{file.name.replace("_scene", "_room")}_{i}', room_start, room_end, file)
                file.rooms.append(room_entry)
            room_list.rooms.append(room_entry)
            cursor += 0x08
        return room_list

    def encode(self) -> bytearray:
        bytes: bytearray = bytearray()
        for room in self.rooms:
            bytes.extend(room.start.to_bytes(4, 'big'))
            bytes.extend(room.end.to_bytes(4, 'big'))
        return bytes


# 4 byte aligned in vanilla
class SceneTransitionActorList(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> None:
        super().__init__(file, RecordType.TransitionActorList, file.start, offset, length)
        self.actors: list[TransitionActor] = []

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int) -> SceneTransitionActorList:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.TransitionActorList)
        if existing_record is not None:
            return existing_record
        num_actors = int(length / 0x10)
        actor_list = SceneTransitionActorList(file, offset, length)
        cursor = actor_list.start + actor_list.offset
        for i in range(0, num_actors):
            actor_list.actors.append(TransitionActor.decode(file.rom, cursor + i * 0x10))
        return actor_list

    def apply_patch(self, patch_data: list[str]) -> None:
        self.actors = []
        for actor in patch_data:
            self.actors.append(TransitionActor.from_json(actor))

    def encode(self) -> bytearray:
        bytes: bytearray = bytearray()
        for actor in self.actors:
            bytes.extend(actor.encode())
        return bytes


# Data only, parent class used by room actor lists, scene spawn position lists,
# and scene transition actor lists in order to iterate through different actor
# types when patching. See get_actor_list in Patches.py.
class ActorData:
    id: int
    pos: Vec3s
    rot: Vec3s
    params: int


# Data only, part of the transition actor list
class TransitionActor(ActorData):
    def __init__(self, front: TransitionActorSide, back: TransitionActorSide, id: int, pos: Vec3s, rot: Vec3s, params: int):
        self.sides: list[TransitionActorSide] = [front, back]
        self.id: int = id
        self.pos: Vec3s = pos
        self.rot: Vec3s = rot # only y variable is used
        self.params: int = params

    def decode(rom: Rom, cursor: int) -> TransitionActor:
        return TransitionActor(
            TransitionActorSide(
                rom.read_byte(cursor),
                rom.read_byte(cursor + 0x01)
            ),
            TransitionActorSide(
                rom.read_byte(cursor + 0x02),
                rom.read_byte(cursor + 0x03)
            ),
            rom.read_s16(cursor + 0x04),
            Vec3s.decode(rom, cursor + 0x06),
            Vec3s(0, rom.read_s16(cursor + 0x0C), 0),
            rom.read_s16(cursor + 0x0E)
        )

    @staticmethod
    def from_json(patch_data: str) -> TransitionActor:
        raw_bytes = patch_data.replace(' ', '')
        return TransitionActor(
            TransitionActorSide(
                int(raw_bytes[0:2], 16),
                int(raw_bytes[2:4], 16)
            ),
            TransitionActorSide(
                int(raw_bytes[4:6], 16),
                int(raw_bytes[6:8], 16)
            ),
            str_to_s16(raw_bytes[8:12]),
            Vec3s(
                str_to_s16(raw_bytes[12:16]),
                str_to_s16(raw_bytes[16:20]),
                str_to_s16(raw_bytes[20:24])
            ),
            Vec3s(0, str_to_s16(raw_bytes[24:28]), 0),
            str_to_s16(raw_bytes[28:32])
        )

    def encode(self) -> bytearray:
        bytes: bytearray = bytearray()
        bytes.extend(self.sides[0].room.to_bytes(1, 'big'))
        bytes.extend(self.sides[0].bgCamIndex.to_bytes(1, 'big'))
        bytes.extend(self.sides[1].room.to_bytes(1, 'big'))
        bytes.extend(self.sides[1].bgCamIndex.to_bytes(1, 'big'))
        bytes.extend(self.id.to_bytes(2, 'big', signed=True))
        bytes.extend(self.pos.encode())
        bytes.extend(self.rot.y.to_bytes(2, 'big', signed=True))
        bytes.extend(self.params.to_bytes(2, 'big', signed=True))
        return bytes


@dataclass
class TransitionActorSide:
    room: int
    bgCamIndex: int


# Data only, part of the scene header
class SceneMiscSettings():
    def __init__(self, sceneCamType: int, worldMapLocation: int) -> None:
        self.sceneCamType: int = sceneCamType
        self.worldMapLocation: int = worldMapLocation

    @staticmethod
    def decode(rom: Rom, cursor: int) -> SceneMiscSettings:
        return SceneMiscSettings(
            rom.read_byte(cursor + 0x01),
            rom.read_byte(cursor + 0x07),
        )


# 4 byte aligned in vanilla
class SceneCollisionHeader(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> None:
        super().__init__(file, RecordType.CollisionHeader, file.start, offset, length)
        self.minBounds: Vec3s = None
        self.maxBounds: Vec3s = None
        self.numVertices: int = 0
        self.vtxList: CollisionVtxList = None
        self.numPolygons: int = 0
        self.polyList: CollisionPolyList = None
        self.surfaceTypeList: CollisionSurfaceTypeList = None
        self.bgCamList: CollisionBgCamInfoList = None
        self.numWaterBoxes: int = 0
        self.waterBoxes: Optional[CollisionWaterBoxList] = None

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int) -> SceneCollisionHeader:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.CollisionHeader)
        if existing_record is not None:
            return existing_record
        collision_header = SceneCollisionHeader(file, offset, length)
        cursor = collision_header.start + collision_header.offset
        vtx_list_address = file.rom.read_int32(cursor + 0x10)
        poly_list_address = file.rom.read_int32(cursor + 0x18)
        surface_list_address = file.rom.read_int32(cursor + 0x1C)
        camdata_list_address = file.rom.read_int32(cursor + 0x20)
        waterbox_list_address = file.rom.read_int32(cursor + 0x28)
        collision_header.minBounds = Vec3s.decode(file.rom, cursor + 0x00)
        collision_header.maxBounds = Vec3s.decode(file.rom, cursor + 0x06)
        collision_header.numVertices = file.rom.read_int16(cursor + 0x0C)
        vtx_list_offset, vtx_list_file = file.get_offset(cursor + 0x10)
        if vtx_list_file is None:
            raise SceneFileAddressException(file, file.rom.read_byte(cursor + 0x10), cursor + 0x10, 'vertex list')
        collision_header.vtxList = CollisionVtxList.decode(vtx_list_file, vtx_list_offset, collision_header.numVertices * 0x06)
        file.add_record(vtx_list_file.data_records, collision_header.vtxList)
        collision_header.numPolygons = file.rom.read_int16(cursor + 0x14)
        poly_list_offset, poly_list_file = file.get_offset(cursor + 0x18)
        if poly_list_file is None:
            raise SceneFileAddressException(file, file.rom.read_byte(cursor + 0x18), cursor + 0x18, 'polygon list')
        collision_header.polyList = CollisionPolyList.decode(poly_list_file, poly_list_offset, collision_header.numPolygons * 0x10)
        file.add_record(poly_list_file.data_records, collision_header.polyList)
        surface_list_offset, surface_list_file = file.get_offset(cursor + 0x1C)
        if surface_list_file is None:
            raise SceneFileAddressException(file, file.rom.read_byte(cursor + 0x1C), cursor + 0x1C, 'surface type')
        collision_header.surfaceTypeList = CollisionSurfaceTypeList.decode(surface_list_file, surface_list_offset, collision_header.polyList.numPolygonTypes * 0x08)
        file.add_record(surface_list_file.data_records, collision_header.surfaceTypeList)
        # ZAPD heuristics to guess the bgCamList size.
        # See ZCollision.cpp line 93
        if camdata_list_address != 0:
            upper_camera_boundary = segment_address_offset(surface_list_address)
            if not upper_camera_boundary:
                upper_camera_boundary = segment_address_offset(poly_list_address)
            if not upper_camera_boundary:
                upper_camera_boundary = segment_address_offset(vtx_list_address)
            if not upper_camera_boundary:
                upper_camera_boundary = segment_address_offset(waterbox_list_address)
            if not upper_camera_boundary:
                upper_camera_boundary = cursor
            if upper_camera_boundary < segment_address_offset(camdata_list_address):
                offset = segment_address_offset(camdata_list_address)
                cam_search1 = file.rom.read_byte(file.start + offset)
                cam_search2 = file.rom.read_byte(file.start + offset + 0x04)
                while cam_search1 == 0x00 and cam_search2 == 0x02:
                    offset += 0x08
                    cam_search1 = file.rom.read_byte(file.start + offset)
                    cam_search2 = file.rom.read_byte(file.start + offset + 0x20)
                upper_camera_boundary = offset
            camdata_list_length = upper_camera_boundary - segment_address_offset(camdata_list_address)
            if camdata_list_length <= 0:
                raise Exception(f'Camera data list length could not be determined for file {file.name} at segment address 0x{camdata_list_address:0>8x}')
            camdata_list_offset, camdata_list_file = file.get_offset(cursor + 0x20)
            if camdata_list_file is None:
                raise SceneFileAddressException(file, file.rom.read_byte(cursor + 0x20), cursor + 0x20, 'camera definitions')
            collision_header.bgCamList = CollisionBgCamInfoList.decode(camdata_list_file, camdata_list_offset, camdata_list_length)
            file.add_record(camdata_list_file.data_records, collision_header.bgCamList)
        collision_header.numWaterBoxes = file.rom.read_int16(cursor + 0x24)
        waterbox_list_offset, waterbox_list_file = file.get_offset(cursor + 0x28)
        if waterbox_list_file is None and waterbox_list_offset != 0:
            raise SceneFileAddressException(file, file.rom.read_byte(cursor + 0x28), cursor + 0x28, 'waterbox list')
        if waterbox_list_file is not None:
            collision_header.waterBoxes = CollisionWaterBoxList.decode(waterbox_list_file, waterbox_list_offset, collision_header.numWaterBoxes * 0x10)
            file.add_record(waterbox_list_file.data_records, collision_header.waterBoxes)
        return collision_header

    def encode(self) -> bytearray:
        bytes: bytearray = bytearray()
        bytes.extend(self.minBounds.encode())
        bytes.extend(self.maxBounds.encode())
        bytes.extend(len(self.vtxList.vertices).to_bytes(2, 'big', signed=True))
        bytes.extend(int.to_bytes(0, 2, 'big'))
        bytes.extend(self.vtxList.get_segment_address_bytes())
        bytes.extend(len(self.polyList.polygons).to_bytes(2, 'big', signed=True))
        bytes.extend(int.to_bytes(0, 2, 'big'))
        bytes.extend(self.polyList.get_segment_address_bytes())
        bytes.extend(self.surfaceTypeList.get_segment_address_bytes())
        bytes.extend(self.bgCamList.get_segment_address_bytes())
        if self.waterBoxes is not None:
            bytes.extend(len(self.waterBoxes.waterboxes).to_bytes(2, 'big', signed=True))
            bytes.extend(int.to_bytes(0, 2, 'big'))
            bytes.extend(self.waterBoxes.get_segment_address_bytes())
        else:
            bytes.extend(int.to_bytes(0, 8, 'big'))
        return bytes


# 4 byte aligned in vanilla
class CollisionVtxList(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> None:
        super().__init__(file, RecordType.Vertices, file.start, offset, length)
        self.vertices: list[Vec3s] = []

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int) -> CollisionVtxList:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.Vertices)
        if existing_record is not None:
            return existing_record
        num_vertices = int(length / 0x06)
        vtx_list = CollisionVtxList(file, offset, length)
        cursor = vtx_list.start + vtx_list.offset
        for i in range(0, num_vertices):
            vtx_list.vertices.append(Vec3s.decode(file.rom, cursor + 0x06 * i))
        return vtx_list

    def encode(self) -> bytearray:
        bytes = bytearray()
        for vtx in self.vertices:
            bytes.extend(vtx.encode())
        return bytes


# 4 byte aligned in vanilla
class CollisionPolyList(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> None:
        super().__init__(file, RecordType.Polys, file.start, offset, length)
        self.polygons: list[CollisionPoly] = []
        self.numPolygonTypes: int = 0

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int) -> CollisionPolyList:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.Polys)
        if existing_record is not None:
            return existing_record
        num_polygons = int(length / 0x10)
        poly_list = CollisionPolyList(file, offset, length)
        cursor = poly_list.start + poly_list.offset
        for i in range(0, num_polygons):
            poly = CollisionPoly.decode(file.rom, cursor + 0x10 * i)
            poly_list.polygons.append(poly)
            if poly.type > poly_list.numPolygonTypes:
                poly_list.numPolygonTypes = poly.type
        poly_list.numPolygonTypes += 1
        return poly_list

    def apply_patch(self, patch_data: list[dict[str, int]]) -> None:
        for item in patch_data:
            id = item['Id']
            t = item['Type']
            flags = item['Flags']
            poly = self.polygons[id]
            poly.type = t
            poly.flags_vIA = (flags << 13)

    def encode(self) -> bytearray:
        bytes = bytearray()
        for poly in self.polygons:
            bytes.extend(poly.encode())
        return bytes


# Data only, part of collision polygon lists
class CollisionPoly:
    def __init__(self) -> None:
        self.type: int = 0
        self.vtxData: tuple[int, int, int] = (0, 0, 0)
        self.flags_vIA: int = 0
        self.flags_vIB: int = 0
        self.flags_vIC: int = 0
        self.normal: Vec3s = Vec3s()
        self.dist: int = 0

    @staticmethod
    def decode(rom: Rom, cursor: int) -> CollisionPoly:
        poly = CollisionPoly()
        poly.type = rom.read_int16(cursor)
        vtx1 = rom.read_int16(cursor + 0x02)
        vtx2 = rom.read_int16(cursor + 0x04)
        vtx3 = rom.read_int16(cursor + 0x06)
        poly.vtxData = (
            vtx1 & 0x1FFF,
            vtx2 & 0x1FFF,
            vtx3 & 0x1FFF
        )
        poly.flags_vIA = vtx1 & 0xE000
        poly.flags_vIB = vtx2 & 0xE000
        poly.flags_vIC = vtx3 & 0xE000
        poly.normal = Vec3s.decode(rom, cursor + 0x08)
        poly.dist = rom.read_s16(cursor + 0x0E)
        return poly

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.type.to_bytes(2, 'big'))
        bytes.extend((self.vtxData[0] | self.flags_vIA).to_bytes(2, 'big'))
        bytes.extend((self.vtxData[1] | self.flags_vIB).to_bytes(2, 'big'))
        bytes.extend((self.vtxData[2] | self.flags_vIC).to_bytes(2, 'big'))
        bytes.extend(self.normal.encode())
        bytes.extend(self.dist.to_bytes(2, 'big', signed=True))
        return bytes


# 4 byte aligned
class CollisionSurfaceTypeList(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> None:
        super().__init__(file, RecordType.SurfaceTypes, file.start, offset, length)
        self.surfaces: list[CollisionSurfaceType] = []

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int) -> CollisionSurfaceTypeList:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.Polys)
        if existing_record is not None:
            return existing_record
        surface_list = CollisionSurfaceTypeList(file, offset, length)
        num_surfaces = int(length / 0x08)
        cursor = surface_list.start + surface_list.offset
        for i in range(0, num_surfaces):
            surface_list.surfaces.append(CollisionSurfaceType.decode(file.rom, cursor + 0x08 * i))
        return surface_list

    def apply_patch(self, patch_data: list[dict[str, int]]) -> None:
        for item in patch_data:
            id = item['Id']
            high = s32_to_u32(item['High'])
            low = s32_to_u32(item['Low'])
            if id == len(self.surfaces):
                self.surfaces.append(CollisionSurfaceType(high, low))
            else:
                self.surfaces[id].data = (high, low)

    def encode(self) -> bytearray:
        bytes = bytearray()
        for surface in self.surfaces:
            bytes.extend(surface.encode())
        return bytes


# Data only, part of collision surface type lists
class CollisionSurfaceType:
    def __init__(self, type1: int = 0, type2: int = 0) -> None:
        self.data: tuple[int, int] = (type1, type2)

    @staticmethod
    def decode(rom: Rom, cursor: int) -> CollisionSurfaceType:
        surface = CollisionSurfaceType()
        surface.data = (
            rom.read_int32(cursor),
            rom.read_int32(cursor + 0x04)
        )
        return surface

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.data[0].to_bytes(4, 'big'))
        bytes.extend(self.data[1].to_bytes(4, 'big'))
        return bytes


# 4 byte aligned in vanilla
class CollisionBgCamInfoList(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> None:
        super().__init__(file, RecordType.Cams, file.start, offset, length)
        self.cams: list[CollisionBgCamInfo] = []

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int) -> CollisionBgCamInfoList:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.Cams)
        if existing_record is not None:
            return existing_record
        cam_info_list = CollisionBgCamInfoList(file, offset, length)
        cursor = cam_info_list.start + cam_info_list.offset
        list_end_address = cam_info_list.start + cam_info_list.offset + cam_info_list.length
        while cursor < list_end_address:
            cam_info_list.cams.append(CollisionBgCamInfo.decode(file.rom, cursor, file, cam_info_list.offset))
            cursor += 0x08
        return cam_info_list

    def apply_patch(self, patch_data: list[dict[str, int]]) -> None:
        vanilla_cams = self.cams
        self.cams = []
        for cam in patch_data:
            pos_index = cam['PositionIndex']
            cam_data = cam['Data']
            if pos_index < 0:
                cam_record = None
            else:
                cam_record = vanilla_cams[pos_index].bgCamFuncData
            cam_setting = int.from_bytes(cam_data.to_bytes(4, 'big')[0:2], 'big')
            cam_count = int.from_bytes(cam_data.to_bytes(4, 'big')[2:4], 'big', signed=True)
            self.cams.append(CollisionBgCamInfo(cam_setting, cam_count, cam_record))

    def encode(self) -> bytearray:
        bytes = bytearray()
        for cam in self.cams:
            bytes.extend(cam.encode())
        return bytes

# Data only, part of collision camera lists
class CollisionBgCamInfo:
    def __init__(self, setting: int = 0, count: int = 0, data: Optional[CollisionCamPosData] = None) -> None:
        self.setting: int = setting
        self.count: int = count
        self.bgCamFuncData: Optional[CollisionCamPosData] = data

    @staticmethod
    def decode(rom: Rom, cursor: int, file: FileDataRelocator, cam_info_list_offset: int) -> CollisionBgCamInfo:
        cam_info = CollisionBgCamInfo()
        cam_info.setting = rom.read_int16(cursor)
        cam_info.count = rom.read_s16(cursor + 0x02)
        cam_data_offset, cam_data_file = file.get_offset(cursor + 0x04)
        if cam_data_file is None and cam_data_offset != 0:
            raise SceneFileAddressException(file, file.rom.read_byte(cursor + 0x04), cursor + 0x04, 'camera function data')
        if cam_data_file is not None:
            # ZAPD assumes all data between the CamPosData list start and the start of
            # the camera settings list belongs to the CamPosData list. Note that this
            # is not true for modded scenes produced from SharpOcarina, which apparently
            # stores the data after the settings. CollisionBgCamFuncData only supports
            # the vanilla scene file behavior of position data before camera settings.
            cam_info.bgCamFuncData = CollisionCamPosData.decode(file, cam_data_offset, cam_info_list_offset - cam_data_offset)
            file.add_record(cam_data_file.data_records, cam_info.bgCamFuncData.record)
        return cam_info

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.setting.to_bytes(2, 'big'))
        bytes.extend(self.count.to_bytes(2, 'big', signed=True))
        if self.bgCamFuncData is not None:
            bytes.extend(self.bgCamFuncData.get_segment_address_bytes())
        else:
            bytes.extend(int.to_bytes(0, 4, 'big'))
        return bytes


# Wrapper class to allow merging records and referencing via array index/pointer offset
class CollisionCamPosData:
    def __init__(self, record: CollisionBgCamFuncData, record_offset: int = 0) -> None:
        self.record: CollisionBgCamFuncData = record
        self.record_offset: int = record_offset

    def get_segment_address_bytes(self) -> bytes:
        record_address = create_segment_address(int(self.record.file.type.value), self.record.offset + self.record_offset)
        return record_address.to_bytes(4, 'big')

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int) -> CollisionBgCamFuncData:
        record = CollisionBgCamFuncData.decode(file, offset, length)
        return CollisionCamPosData(record)


# 4 byte aligned in vanilla
class CollisionBgCamFuncData(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> None:
        super().__init__(file, RecordType.CamPosData, file.start, offset, length)
        # Data is either a set of 6 Vec3s (crawlspaces/Camera_Subj4 only) or a more
        # complicated struct the same length as 3 Vec3s (0x12). See BgCamFuncData
        # and its comments in z64bgcheck.h in decomp.
        # Assume this is always a list of Vec3s for simplicity.
        self.positions: list[Vec3s] = []

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int) -> CollisionBgCamFuncData:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.CamPosData)
        if existing_record is not None:
            return existing_record
        cam_func_data = CollisionBgCamFuncData(file, offset, length)
        cursor = cam_func_data.start + cam_func_data.offset
        num_vertices = int(length / 0x06)
        # Length may not be aligned with data due to using
        # next record offset to calculate length
        cam_func_data.length = num_vertices * 0x06
        cam_func_data.refresh_rom_data()
        for i in range(0, num_vertices):
            cam_func_data.positions.append(Vec3s.decode(file.rom, cursor + i * 0x06))
        return cam_func_data

    def encode(self) -> bytearray:
        bytes = bytearray()
        for pos in self.positions:
            bytes.extend(pos.encode())
        return bytes

    def merge(self, other_record: CollisionBgCamFuncData) -> None:
        low_record, high_record, lower_overlap = super().merge(other_record)
        lower_overlap_index = int(lower_overlap / 0x06)
        if lower_overlap / 0x06 != lower_overlap_index:
            raise Exception(f'Overlapping {self.type.value} records are not aligned at offset {low_record.offset:0>8x}, length {low_record.length:0>8x} and offset {high_record.offset:0>8x}, length {high_record.length:0>8x}')
        i = lower_overlap_index
        # Check that stored positions haven't changed in case raw bytes were not refreshed after position changes
        while i < len(low_record.positions):
            if low_record.positions[i] != high_record.positions[i - lower_overlap_index]:
                raise Exception(f'Tried to merge mismatching {self.type.value} records at 0x{self.offset:0>8x}, length 0x{self.length:0>8x} and 0x{other_record.offset:0>8x}, length 0x{other_record.length:0>8x}. Mismatch at 0x{low_record.offset + i * 0x06:0>8x} (lower: {low_record.positions[i]}, upper: {high_record.positions[i - lower_overlap_index]})')
            i += 1
        low_record.positions.extend(high_record.positions[i:])

    def _merge_in_file(self, file: FileDataRelocator, other_record: DataRecord, record_offset: int):
        cams: list[CollisionBgCamInfoList] = list(filter(lambda r: r.type == RecordType.Cams, file.data_records))
        for cam in cams:
            i = 0
            while i < len(cam.cams):
                if cam.cams[i].bgCamFuncData.record is other_record:
                    cam.cams[i].bgCamFuncData = CollisionCamPosData(self, record_offset)
                    break
                i += 1


# 4 byte aligned in vanilla
class CollisionWaterBoxList(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> None:
        super().__init__(file, RecordType.Waterboxes, file.start, offset, length)
        self.waterboxes: list[CollisionWaterBox] = []

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int) -> CollisionWaterBoxList:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.Waterboxes)
        if existing_record is not None:
            return existing_record
        waterbox_list = CollisionWaterBoxList(file, offset, length)
        cursor = waterbox_list.start + waterbox_list.offset
        num_waterboxes = int(length / 0x10)
        for i in range(0, num_waterboxes):
            waterbox_list.waterboxes.append(CollisionWaterBox.decode(file.rom, cursor + i * 0x10))
        return waterbox_list

    def encode(self) -> bytearray:
        bytes = bytearray()
        for waterbox in self.waterboxes:
            bytes.extend(waterbox.encode())
        return bytes


# Data only, referenced in waterbox list
class CollisionWaterBox:
    def __init__(self) -> None:
        self.xMin: int = 0
        self.ySurface: int = 0
        self.zMin: int = 0
        self.xLength: int = 0
        self.zLength: int = 0
        self.properties: int = 0

    @staticmethod
    def decode(rom: Rom, cursor: int) -> CollisionWaterBox:
        waterbox = CollisionWaterBox()
        waterbox.xMin = rom.read_s16(cursor)
        waterbox.ySurface = rom.read_s16(cursor + 0x02)
        waterbox.zMin = rom.read_s16(cursor + 0x04)
        waterbox.xLength = rom.read_s16(cursor + 0x06)
        waterbox.zLength = rom.read_s16(cursor + 0x08)
        waterbox.properties = rom.read_int32(cursor + 0x0C)
        return waterbox

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.xMin.to_bytes(2, 'big', signed=True))
        bytes.extend(self.ySurface.to_bytes(2, 'big', signed=True))
        bytes.extend(self.zMin.to_bytes(2, 'big', signed=True))
        bytes.extend(self.xLength.to_bytes(2, 'big', signed=True))
        bytes.extend(self.zLength.to_bytes(2, 'big', signed=True))
        bytes.extend(int.to_bytes(0, 2, 'big'))
        bytes.extend(self.properties.to_bytes(4, 'big'))
        return bytes


# 4 byte aligned in vanilla
class SceneEntranceList(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> None:
        super().__init__(file, RecordType.EntranceList, file.start, offset, length, True)
        self.entrances: list[SceneEntrance] = []

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> SceneEntranceList:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.EntranceList)
        if existing_record is not None:
            return existing_record
        return SceneEntranceList(file, offset, length)

    def decode_late(self) -> None:
        cursor = self.start + self.offset
        self.length = self.file.get_record_length_from_neighbor(self)
        self.refresh_rom_data()
        num_entrances = int(self.length / 0x02)
        for i in range(0, num_entrances):
            self.entrances.append(SceneEntrance.decode(self.file.rom, cursor + i * 0x02))
        self.delay_parsing = False

    def encode(self) -> bytearray:
        bytes = bytearray()
        for entrance in self.entrances:
            bytes.extend(entrance.encode())
        return bytes


# Data only, referenced in entrance list
class SceneEntrance:
    def __init__(self, playerEntryIndex: int, room: int) -> None:
        self.playerEntryIndex: int = playerEntryIndex
        self.room: int = room

    @staticmethod
    def decode(rom: Rom, cursor: int) -> SceneEntrance:
        return SceneEntrance(
            rom.read_byte(cursor),
            rom.read_byte(cursor + 0x01)
        )

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.playerEntryIndex.to_bytes(1, 'big'))
        bytes.extend(self.room.to_bytes(1, 'big'))
        return bytes


# Data only, part of scene headers
class SceneSpecialSettings:
    def __init__(self, naviQuestHintFileId: int, keepObjectId: int) -> None:
        self.naviQuestHintFileId: int = naviQuestHintFileId
        self.keepObjectId: int = keepObjectId

    @staticmethod
    def decode(rom: Rom, cursor: int) -> SceneSpecialSettings:
        return SceneSpecialSettings(
            rom.read_byte(cursor + 0x01),
            rom.read_int16(cursor + 0x06)
        )


# 4 byte aligned in vanilla
class ScenePathList(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> None:
        super().__init__(file, RecordType.PathList, file.start, offset, length, True)
        self.paths: list[ScenePathVtxList] = []

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> ScenePathList:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.PathList)
        if existing_record is not None:
            return existing_record
        path_list = ScenePathList(file, offset, length)
        if length > 0:
            path_list._decode()
        return path_list

    def decode_late(self) -> None:
        # Truncate any padding using path entry size
        self.length = int(self.file.get_record_length_from_neighbor(self) / 0x08) * 0x08
        self.refresh_rom_data()
        self._decode()

    def _decode(self) -> None:
        cursor = self.start + self.offset
        num_paths = int(self.length / 0x08)
        for i in range(0, num_paths):
            num_points = self.file.rom.read_byte(cursor + i * 0x08)
            path_vtx_offset, path_vtx_file = self.file.get_offset(cursor + i * 0x08 + 0x04)
            # There may be some padding after the path list
            if num_points == 0:
                self.length = (cursor + i * 0x08) - self.file.start - self.offset
                self.refresh_rom_data()
                break
            if path_vtx_file is None:
                raise SceneFileAddressException(self.file, self.file.rom.read_byte(cursor + i*0x08 + 0x04), cursor + i*0x08 + 0x04, 'path point list')
            path_vtx_record = ScenePathVtxList.decode(path_vtx_file, path_vtx_offset, num_points * 0x06)
            self.paths.append(path_vtx_record)
            self.file.add_record(path_vtx_file.data_records, path_vtx_record)
        self.delay_parsing = False

    @staticmethod
    def from_json(file: FileDataRelocator, patch_data: list[dict[str, list[list[int]]]]) -> ScenePathList:
        # Don't attempt to replace any existing path records
        # in case MQ has more paths than the vanilla file.
        record_offset = file.end
        path_list = ScenePathList(file, record_offset)
        path_cursor = record_offset + 1
        for path_dict in patch_data:
            path_list.paths.append(ScenePathVtxList.from_json(file, path_cursor, path_dict['Points']))
            path_cursor += 1
        return path_list


    def encode(self) -> bytearray:
        bytes = bytearray()
        for path in self.paths:
            bytes.extend(len(path.vertices).to_bytes(1, 'big'))
            bytes.extend(int.to_bytes(0, 3, 'big'))
            bytes.extend(path.get_segment_address_bytes())
        return bytes


# 4 byte aligned in vanilla
class ScenePathVtxList(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> None:
        super().__init__(file, RecordType.Points, file.start, offset, length)
        self.vertices: list[Vec3s] = []

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int) -> ScenePathVtxList:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.Points)
        if existing_record is not None:
            return existing_record
        num_points = int(length / 0x06)
        path_vtx_list = ScenePathVtxList(file, offset, length)
        cursor = path_vtx_list.start + path_vtx_list.offset
        for i in range(0, num_points):
            path_vtx_list.vertices.append(Vec3s.decode(file.rom, cursor + i * 0x06))
        return path_vtx_list

    @staticmethod
    def from_json(file: FileDataRelocator, offset: int, patch_data: list[list[int]]) -> ScenePathVtxList:
        path_vtx_list = ScenePathVtxList(file, offset)
        for vtx in patch_data:
            path_vtx_list.vertices.append(Vec3s(vtx[0], vtx[1], vtx[2]))
        return path_vtx_list

    def encode(self) -> bytearray:
        bytes = bytearray()
        for entry in self.vertices:
            bytes.extend(entry.encode())
        return bytes


# 4 byte aligned in vanilla
class SceneSpawnPointList(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> None:
        super().__init__(file, RecordType.SpawnList, file.start, offset, length)
        self.spawns: list[ActorEntry] = []

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int) -> SceneSpawnPointList:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.SpawnList)
        if existing_record is not None:
            return existing_record
        num_spawns = int(length / 0x10)
        spawn_list = SceneSpawnPointList(file, offset, length)
        cursor = spawn_list.start + spawn_list.offset
        for i in range(0, num_spawns):
            spawn_list.spawns.append(ActorEntry.decode(file.rom, cursor + i * 0x10))
        return spawn_list

    def encode(self) -> bytearray:
        bytes = bytearray()
        for entry in self.spawns:
            bytes.extend(entry.encode())
        return bytes


# Data only, used in scene spawn lists and room actor lists
class ActorEntry(ActorData):
    def __init__(self, id: int, pos: Vec3s, rot: Vec3s, params: int) -> None:
        self.id: int = id
        self.pos: Vec3s = pos
        self.rot: Vec3s = rot
        self.params: int = params

    def copy(self) -> ActorEntry:
        return ActorEntry(self.id, self.pos.copy(), self.rot.copy(), self.params)

    @staticmethod
    def decode(rom: Rom, cursor: int) -> ActorEntry:
        return ActorEntry(
            rom.read_s16(cursor),
            Vec3s.decode(rom, cursor + 0x02),
            Vec3s.decode(rom, cursor + 0x08),
            rom.read_int16(cursor + 0x0E)
        )

    @staticmethod
    def from_json(patch_data: str) -> ActorEntry:
        raw_bytes = patch_data.replace(' ', '')
        return ActorEntry(
            str_to_s16(raw_bytes[0:4]),
            Vec3s(
                str_to_s16(raw_bytes[4:8]),
                str_to_s16(raw_bytes[8:12]),
                str_to_s16(raw_bytes[12:16])
            ),
            Vec3s(
                str_to_s16(raw_bytes[16:20]),
                str_to_s16(raw_bytes[20:24]),
                str_to_s16(raw_bytes[24:28])
            ),
            int(raw_bytes[28:32], 16)
        )

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.id.to_bytes(2, 'big', signed=True))
        bytes.extend(self.pos.encode())
        bytes.extend(self.rot.encode())
        bytes.extend(self.params.to_bytes(2, 'big'))
        return bytes

    def __eq__(self, value):
        if not isinstance(value, ActorEntry):
            return NotImplemented
        return (
            self.id == value.id and
            self.pos == value.pos and
            self.rot == value.rot and
            self.params == value.params
        )


# Data only, used in scene headers
class SceneSkyboxSettings:
    def __init__(self, skyboxID: int, skyboxConfig: int, envLightMode: int) -> None:
        self.skyboxID: int = skyboxID
        self.skyboxConfig: int = skyboxConfig
        self.envLightMode: int = envLightMode

    @staticmethod
    def decode(rom: Rom, scene_cmd_addr: int) -> SceneSkyboxSettings:
        return SceneSkyboxSettings(
            rom.read_byte(scene_cmd_addr + 4),
            rom.read_byte(scene_cmd_addr + 5),
            rom.read_byte(scene_cmd_addr + 6)
        )


# 4 byte aligned in vanilla
class SceneExitList(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> None:
        super().__init__(file, RecordType.ExitList, file.start, offset, length, True)
        self.exits: list[int] = []

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> SceneExitList:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.ExitList)
        if existing_record is not None:
            return existing_record
        return SceneExitList(file, offset, length)

    def decode_late(self) -> None:
        cursor = self.start + self.offset
        self.length = self.file.get_record_length_from_neighbor(self)
        self.refresh_rom_data()
        num_entrances = int(self.length / 0x02)
        for i in range(0, num_entrances):
            self.exits.append(self.file.rom.read_int16(cursor + i * 0x02))
        self.delay_parsing = False

    def encode(self) -> bytearray:
        bytes = bytearray()
        for exit in self.exits:
            bytes.extend(exit.to_bytes(2, 'big'))
        return bytes


# 4 byte aligned in vanilla
class SceneLightSettingsList(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> None:
        super().__init__(file, RecordType.LightSettings, file.start, offset, length)
        self.lights: list[SceneLightSettings] = []

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int) -> SceneLightSettingsList:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.LightSettings)
        if existing_record is not None:
            return existing_record
        num_lights = int(length / 0x16)
        light_list = SceneLightSettingsList(file, offset, length)
        cursor = light_list.start + light_list.offset
        for i in range(0, num_lights):
            light_list.lights.append(SceneLightSettings.decode(file.rom, cursor + i * 0x16))
        return light_list

    def encode(self) -> bytearray:
        bytes = bytearray()
        for light in self.lights:
            bytes.extend(light.encode())
        return bytes


# Data only, part of light settings list
class SceneLightSettings:
    def __init__(self) -> None:
        self.ambientColor: tuple[int, int, int] = (0, 0, 0)
        self.light1Dir: tuple[int, int, int] = (0, 0, 0)
        self.light1Color: tuple[int, int, int] = (0, 0, 0)
        self.light2Dir: tuple[int, int, int] = (0, 0, 0)
        self.light2Color: tuple[int, int, int] = (0, 0, 0)
        self.fogColor: tuple[int, int, int] = (0, 0, 0)
        self.blendRate: int = 0
        self.zNear: int = 0
        self.zFar: int = 0

    @staticmethod
    def decode(rom: Rom, cursor: int) -> SceneLightSettings:
        light = SceneLightSettings()
        light.ambientColor = (
            rom.read_byte(cursor),
            rom.read_byte(cursor + 1),
            rom.read_byte(cursor + 2),
        )
        light.light1Dir = (
            rom.read_s8(cursor + 3),
            rom.read_s8(cursor + 4),
            rom.read_s8(cursor + 5),
        )
        light.light1Color = (
            rom.read_byte(cursor + 6),
            rom.read_byte(cursor + 7),
            rom.read_byte(cursor + 8),
        )
        light.light2Dir = (
            rom.read_s8(cursor + 9),
            rom.read_s8(cursor + 10),
            rom.read_s8(cursor + 11),
        )
        light.light2Color = (
            rom.read_byte(cursor + 12),
            rom.read_byte(cursor + 13),
            rom.read_byte(cursor + 14),
        )
        light.fogColor = (
            rom.read_byte(cursor + 15),
            rom.read_byte(cursor + 16),
            rom.read_byte(cursor + 17),
        )
        blendRateAndFogNear = rom.read_int16(cursor + 18)
        light.blendRate = (blendRateAndFogNear & 0xFC00) >> 0xA
        light.zNear = blendRateAndFogNear & 0x03FF
        light.zFar = rom.read_int16(cursor + 20)
        return light

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend([int.to_bytes(x, 1, 'big')[0] for x in self.ambientColor])
        bytes.extend([int.to_bytes(x, 1, 'big', signed=True)[0] for x in self.light1Dir])
        bytes.extend([int.to_bytes(x, 1, 'big')[0] for x in self.light1Color])
        bytes.extend([int.to_bytes(x, 1, 'big', signed=True)[0] for x in self.light2Dir])
        bytes.extend([int.to_bytes(x, 1, 'big')[0] for x in self.light2Color])
        bytes.extend([int.to_bytes(x, 1, 'big')[0] for x in self.fogColor])
        bytes.extend(((self.blendRate << 0xA) | self.zNear).to_bytes(2, 'big'))
        bytes.extend(self.zFar.to_bytes(2, 'big'))
        return bytes


# 4 byte aligned in vanilla
class SceneCutsceneData(DataRecord, Cutscene):
    def __init__(self, file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> None:
        DataRecord.__init__(self, file, RecordType.CutsceneData, file.start, offset, length)
        Cutscene.__init__(self, file.start + offset)

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int = -1) -> SceneCutsceneData:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.CutsceneData)
        if existing_record is not None:
            return existing_record
        cutscene = SceneCutsceneData(file, offset, length)
        cutscene.parse(file.rom)
        cutscene.length = cutscene.original_length
        cutscene.refresh_rom_data()
        return cutscene

    def encode(self):
        # Force encode path through parsed data
        return Cutscene.encode(self)


class RoomDataRelocator(FileDataRelocator):
    def __init__(self, rom: Rom, name: str, start: int, end: int, scene: SceneDataRelocator) -> None:
        self.scene = scene
        self.headers: list[Optional[RoomHeader]] = [None]
        super().__init__(rom, name, start, end, FileType.Room)

    def parse_file_header(self, alternate: Optional[int] = None) -> DataRecord:
        self.headers[0] = RoomHeader.decode(self)
        return self.headers[0]

    def get_offset(self, cursor: int) -> tuple[int, Optional[FileDataRelocator]]:
        segment = self.rom.read_byte(cursor)
        offset = self.rom.read_int24(cursor + 1)
        if segment == 0x00 and offset == 0:
            return (0, None)  # null
        if segment == 0x02:
            return (offset, self.scene)  # scene
        if segment == 0x03:
            return (offset, self)  # room
        return (-1, None)  # unknown


# Some duplication from SceneHeader. Separate class
# used to provide distinction in class properties
# for scene- and room-specific commands.
# Always 16 byte aligned in vanilla.
class RoomHeader(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> None:
        super().__init__(file, RecordType.RoomHeader, file.start, offset, length)
        self.alt_header_list: SceneAltHeaderList = None
        self.echo_settings: RoomEchoSettings = None
        self.behavior_settings: RoomBehaviorSettings = None
        self.skybox_settings: RoomSkyboxSettings = None
        self.time_settings: RoomTimeSettings = None
        self.wind_settings: RoomWindSettings = None
        self.mesh_header: RoomMeshHeader = None
        self.object_list: RoomObjectList = None
        self.actor_list: RoomActorList = None
        self.align = 16

    def copy(self) -> RoomHeader:
        new_header = RoomHeader(self.file, self.offset + 1, self.length)
        new_header.alt_header_list = self.alt_header_list
        new_header.echo_settings = self.echo_settings
        new_header.behavior_settings = self.behavior_settings
        new_header.skybox_settings = self.skybox_settings
        new_header.time_settings = self.time_settings
        new_header.wind_settings = self.wind_settings
        new_header.mesh_header = self.mesh_header
        new_header.object_list = self.object_list
        new_header.actor_list = self.actor_list
        return new_header

    @staticmethod
    def decode(file: FileDataRelocator, offset: int = 0, length: Optional[int] = -1) -> RoomHeader:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.RoomHeader)
        if existing_record is not None:
            return existing_record
        setup = RoomHeader(file, offset, length)
        command = 0
        setup_start = setup.start + setup.offset
        cursor = setup_start
        # Process the current setup header.
        # Command byte conditions are listed in the same order as
        # the convention used in the rom.
        while command != 0x14: # header terminator
            command = file.rom.read_byte(cursor)
            if command == 0x18: # Alternate header list
                list_offset, list_file = file.get_offset(cursor + 0x04)
                if list_file is None:
                    raise RoomFileAddressException(file, file.rom.read_byte(cursor + 0x04), cursor + 0x04, 'alternate header list')
                setup.alt_header_list = SceneAltHeaderList.decode(list_file, list_offset)
                file.add_record(list_file.data_records, setup.alt_header_list)
            elif command == 0x16:
                setup.echo_settings = RoomEchoSettings(file.rom.read_byte(cursor + 0x07))
            elif command == 0x08:
                setup.behavior_settings = RoomBehaviorSettings.decode(file.rom, cursor)
            elif command == 0x12:
                setup.skybox_settings = RoomSkyboxSettings.decode(file.rom, cursor)
            elif command == 0x10:
                setup.time_settings = RoomTimeSettings.decode(file.rom, cursor)
            elif command == 0x05:
                setup.wind_settings = RoomWindSettings.decode(file.rom, cursor)
            elif command == 0x0A: # mesh header
                list_offset, list_file = file.get_offset(cursor + 0x04)
                if list_file is None:
                    raise RoomFileAddressException(file, file.rom.read_byte(cursor + 0x04), cursor + 0x04, 'mesh header')
                header_type = list_file.rom.read_byte(list_file.start + list_offset)
                if header_type == 0:
                    setup.mesh_header = RoomMeshHeader.decode(list_file, list_offset, 0x0C)
                elif header_type == 1:
                    header_subtype = list_file.rom.read_byte(list_file.start + list_offset + 0x01)
                    if header_subtype == 0x01:
                        # single image background
                        setup.mesh_header = RoomMeshImageSingleHeader.decode(list_file, list_offset, 0x1E)
                    elif header_subtype == 0x02:
                        # multiple images
                        setup.mesh_header = RoomMeshImageMultiHeader.decode(list_file, list_offset, 0x10)
                    else:
                        # invalid format
                        raise Exception(f'Unsupported room mesh image header subtype of 0x{file.rom.read_byte(cursor + 0x01):0>2x} in {file.name} at offset 0x{cursor:0>2x}')
                elif header_type == 2:
                    setup.mesh_header = RoomMeshCullableHeader.decode(list_file, list_offset, 0x0C)
                else:
                    raise Exception(f'Unsupported room mesh header type 0x{header_type:0>2x} in {list_file.name} at offset {list_offset}')
                file.add_record(list_file.data_records, setup.mesh_header)
            elif command == 0x0B: # object list
                list_offset, list_file = file.get_offset(cursor + 0x04)
                if list_file is None:
                    raise RoomFileAddressException(file, file.rom.read_byte(cursor + 0x04), cursor + 0x04, 'object list')
                num_objects = file.rom.read_byte(cursor + 0x01)
                setup.object_list = RoomObjectList.decode(list_file, list_offset, num_objects * 0x02)
                file.add_record(list_file.data_records, setup.object_list)
            elif command == 0x01: # actor list
                list_offset, list_file = file.get_offset(cursor + 0x04)
                if list_file is None:
                    raise RoomFileAddressException(file, file.rom.read_byte(cursor + 0x04), cursor + 0x04, 'actor list')
                num_actors = file.rom.read_byte(cursor + 0x01)
                setup.actor_list = RoomActorList.decode(list_file, list_offset, num_actors * 0x10)
                file.add_record(list_file.data_records, setup.actor_list)
            elif command == 0x14: # end list
                pass
            else:
                raise Exception(
                    f'Unexpected command 0x{command:02X} at 0x{cursor - setup.start:08X} in {file.name}')
            cursor += 0x08
        setup.length = cursor - setup_start
        setup.refresh_rom_data()
        return setup

    def encode(self) -> bytearray:
        bytes = bytearray()
        if self.alt_header_list is not None:
            bytes.extend(int.to_bytes(0x18 << 0x18, 4, 'big'))
            bytes.extend(self.alt_header_list.get_segment_address_bytes())
        if self.echo_settings is not None:
            bytes.extend(int.to_bytes(0x16 << 0x18, 4, 'big'))
            bytes.extend(int.to_bytes(0, 3, 'big'))
            bytes.extend(self.echo_settings.echo.to_bytes(1, 'big'))
        if self.behavior_settings is not None:
            bytes.extend(int.to_bytes(0x08, 1, 'big'))
            bytes.extend(self.behavior_settings.curRoomUnk3.to_bytes(1, 'big'))
            bytes.extend(int.to_bytes(0, 4, 'big'))
            # Assume individual flags are more current than flag blob
            curRoomUnk2 = ((self.behavior_settings.curRoomUnk2 & 0xFAFF)
                            | (int(self.behavior_settings.showInvisActors) << 8)
                            | (int(self.behavior_settings.disableWarpSongs) << 10))
            bytes.extend(curRoomUnk2.to_bytes(2, 'big'))
        if self.skybox_settings is not None:
            bytes.extend(int.to_bytes(0x12 << 0x18, 4, 'big'))
            bytes.extend(int(self.skybox_settings.disableSky).to_bytes(1, 'big'))
            bytes.extend(int(self.skybox_settings.disableSunMoon).to_bytes(1, 'big'))
            bytes.extend(int.to_bytes(0, 2, 'big'))
        if self.time_settings is not None:
            bytes.extend(int.to_bytes(0x10 << 0x18, 4, 'big'))
            bytes.extend(self.time_settings.hour.to_bytes(1, 'big'))
            bytes.extend(self.time_settings.minute.to_bytes(1, 'big'))
            bytes.extend(self.time_settings.speed.to_bytes(1, 'big'))
            bytes.extend(int.to_bytes(0, 1, 'big'))
        if self.wind_settings is not None:
            bytes.extend(int.to_bytes(0x05 << 0x18, 4, 'big'))
            bytes.extend(self.wind_settings.xDir.to_bytes(1, 'big', signed=True))
            bytes.extend(self.wind_settings.yDir.to_bytes(1, 'big', signed=True))
            bytes.extend(self.wind_settings.zDir.to_bytes(1, 'big', signed=True))
            bytes.extend(self.wind_settings.strength.to_bytes(1, 'big'))
        if self.mesh_header is not None:
            bytes.extend(int.to_bytes(0x0A << 0x18, 4, 'big'))
            bytes.extend(self.mesh_header.get_segment_address_bytes())
        if self.object_list is not None:
            bytes.extend(int.to_bytes(0x0B, 1, 'big'))
            bytes.extend(len(self.object_list.objects).to_bytes(1, 'big'))
            bytes.extend(int.to_bytes(0, 2, 'big'))
            bytes.extend(self.object_list.get_segment_address_bytes())
        if self.actor_list is not None:
            bytes.extend(int.to_bytes(0x01, 1, 'big'))
            bytes.extend(len(self.actor_list.actors).to_bytes(1, 'big'))
            bytes.extend(int.to_bytes(0, 2, 'big'))
            bytes.extend(self.actor_list.get_segment_address_bytes())
        bytes.extend(int.to_bytes(0x14 << 0x18, 4, 'big'))
        bytes.extend(int.to_bytes(0, 4, 'big'))
        return bytes


# Data only, part of room headers
class RoomEchoSettings:
    def __init__(self, echo: int) -> None:
        self.echo: int = echo


# Data only, part of room headers
class RoomBehaviorSettings:
    def __init__(self, curRoomUnk3: int, curRoomUnk2: int, showInvisActors: bool, disableWarpSongs: bool) -> None:
        self.curRoomUnk3: int = curRoomUnk3
        self.curRoomUnk2: int = curRoomUnk2
        self.showInvisActors: bool = showInvisActors
        self.disableWarpSongs: bool = disableWarpSongs

    @staticmethod
    def decode(rom: Rom, cursor: int) -> RoomBehaviorSettings:
        curRoomUnk3 = rom.read_byte(cursor + 0x01)
        curRoomUnk2 = rom.read_int16(cursor + 0x06)
        return RoomBehaviorSettings(
            curRoomUnk3,
            curRoomUnk2,
            (curRoomUnk2 & 0x0100) == 0x0100,
            (curRoomUnk2 & 0x0400) == 0x0400
        )


# Data only, part of room headers
class RoomSkyboxSettings:
    def __init__(self, disableSky: bool, disableSunMoon: bool) -> None:
        self.disableSky: bool = disableSky
        self.disableSunMoon: bool = disableSunMoon

    @staticmethod
    def decode(rom: Rom, cursor: int) -> RoomSkyboxSettings:
        return RoomSkyboxSettings(
            bool(rom.read_byte(cursor + 0x04)),
            bool(rom.read_byte(cursor + 0x05))
        )


# Data only, part of room headers
class RoomTimeSettings:
    def __init__(self, hour: int, minute: int, speed: int) -> None:
        self.hour: int = hour
        self.minute: int = minute
        self.speed: int = speed

    @staticmethod
    def decode(rom: Rom, cursor: int) -> RoomTimeSettings:
        return RoomTimeSettings(
            rom.read_byte(cursor + 0x04),
            rom.read_byte(cursor + 0x05),
            rom.read_byte(cursor + 0x06)
        )


# Data only, part of room headers
class RoomWindSettings:
    def __init__(self, xDir: int, yDir: int, zDir: int, strength: int) -> None:
        self.xDir: int = xDir
        self.yDir: int = yDir
        self.zDir: int = zDir
        self.strength: int = strength

    @staticmethod
    def decode(rom: Rom, cursor: int) -> RoomWindSettings:
        return RoomWindSettings(
            rom.read_s8(cursor + 0x04),
            rom.read_s8(cursor + 0x05),
            rom.read_s8(cursor + 0x06),
            rom.read_byte(cursor + 0x07)
        )


# 16 byte aligned in vanilla
class RoomMeshHeader(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: int) -> None:
        super().__init__(file, RecordType.MeshHeader, file.start, offset, length)
        self.display_list_entries: RoomMeshDLEntries = None
        self.align = 16

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int) -> RoomMeshHeader:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.MeshHeader)
        if existing_record is not None:
            return existing_record
        mesh = RoomMeshHeader(file, offset, length)
        cursor = mesh.start + mesh.offset
        list_offset, list_file = file.get_offset(cursor + 0x04)
        if list_file is None:
            raise RoomFileAddressException(file, file.rom.read_byte(cursor + 0x04), cursor + 0x04, 'display list')
        list_end = segment_address_offset(file.rom.read_int32(cursor + 0x08))
        display_list = RoomMeshDLEntries.decode(list_file, list_offset, list_end - list_offset)
        mesh.display_list_entries = display_list
        file.add_record(list_file.data_records, display_list)
        return mesh

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(int.to_bytes(0x00, 1, 'big'))
        bytes.extend(int(self.display_list_entries.length / 0x08).to_bytes(1, 'big'))
        bytes.extend(int.to_bytes(0, 2, 'big'))
        bytes.extend(self.display_list_entries.get_segment_address_bytes())
        bytes.extend(create_segment_address(self.display_list_entries.file.type.value, self.display_list_entries.offset + self.display_list_entries.length).to_bytes(4, 'big'))
        return bytes


# 16 byte aligned in vanilla
class _RoomMeshImageHeader(DataRecord):
    def __init__(self, file: FileDataRelocator, type: RecordType, offset: int, length: int) -> None:
        super().__init__(file, type, file.start, offset, length)
        self.display_list_entries: RoomMeshDLEntries = None
        self.align = 16

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int) -> RoomMeshImageSingleHeader | RoomMeshImageMultiHeader:
        cursor = file.start + offset
        mesh_type = file.rom.read_byte(cursor + 0x01)
        if mesh_type == 0x01:
            mesh = RoomMeshImageSingleHeader(file, offset, length)
        elif mesh_type == 0x02:
            mesh = RoomMeshImageMultiHeader(file, offset, length)
        else:
            raise Exception(f'Unknown room mesh background type 0x{mesh_type:0>2x} in {file.name} at offset 0x{offset:0>2x}')
        list_offset, list_file = file.get_offset(cursor + 0x04)
        if list_file is None:
            raise RoomFileAddressException(file, file.rom.read_byte(cursor + 0x04), cursor + 0x04, 'display list')
        display_list = RoomMeshDLEntries.decode(list_file, list_offset, 0x08)
        mesh.display_list_entries = display_list
        file.add_record(list_file.data_records, display_list)
        return mesh


# 16 byte aligned in vanilla
class RoomMeshImageSingleHeader(_RoomMeshImageHeader):
    def __init__(self, file: FileDataRelocator, offset: int, length: int) -> None:
        super().__init__(file, RecordType.MeshHeaderImageSingle, offset, length)
        self.background: RoomMeshImage = None
        self.align = 16

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int) -> RoomMeshImageSingleHeader:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.MeshHeaderImageSingle)
        if existing_record is not None:
            return existing_record
        mesh = super(RoomMeshImageSingleHeader, RoomMeshImageSingleHeader).decode(file, offset, length)
        if isinstance(mesh, RoomMeshImageMultiHeader):
            raise Exception(f'Attempted to create single background room mesh with multi background room mesh data in {file.name} at offset 0x{offset:0>2x}')
        cursor = mesh.start + mesh.offset
        mesh.background = RoomMeshImage.decode(file, cursor + 0x08)
        return mesh

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(int.to_bytes(0x01, 1, 'big'))
        bytes.extend(int.to_bytes(0x01, 1, 'big'))
        bytes.extend(int.to_bytes(0, 2, 'big'))
        bytes.extend(self.display_list_entries.get_segment_address_bytes())
        bytes.extend(self.background.encode())
        return bytes


# 16 byte aligned in vanilla
class RoomMeshImageMultiHeader(_RoomMeshImageHeader):
    def __init__(self, file: FileDataRelocator, offset: int, length: int) -> None:
        super().__init__(file, RecordType.MeshHeaderImageMulti, offset, length)
        self.background_list: RoomMeshImageMultiEntries = None
        self.align = 16

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int) -> RoomMeshImageMultiHeader:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.MeshHeaderImageMulti)
        if existing_record is not None:
            return existing_record
        mesh = super(RoomMeshImageMultiHeader, RoomMeshImageMultiHeader).decode(file, offset, length)
        if isinstance(mesh, RoomMeshImageSingleHeader):
            raise Exception(f'Attempted to create multi background room mesh with single background room mesh data in {file.name} at offset 0x{offset:0>2x}')
        cursor = mesh.start + mesh.offset
        num_backgrounds = file.rom.read_byte(cursor + 0x08)
        bg_offset, bg_file = file.get_offset(cursor + 0x0C)
        if bg_file is None:
            raise RoomFileAddressException(file, file.rom.read_byte(cursor + 0x0C), cursor + 0x0C, 'multi background list')
        mesh.background_list = RoomMeshImageMultiEntries.decode(file, bg_offset, num_backgrounds * 0x1C)
        file.add_record(bg_file.data_records, mesh.background_list)
        return mesh

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(int.to_bytes(0x01, 1, 'big'))
        bytes.extend(int.to_bytes(0x02, 1, 'big'))
        bytes.extend(int.to_bytes(0, 2, 'big'))
        bytes.extend(self.display_list_entries.get_segment_address_bytes())
        bytes.extend(len(self.background_list.backgrounds).to_bytes(1, 'big'))
        bytes.extend(int.to_bytes(0, 3, 'big'))
        bytes.extend(self.background_list.get_segment_address_bytes())
        return bytes


# Data only, part of both single and multi background image mesh headers
class RoomMeshImage:
    def __init__(self) -> None:
        self.source: RoomMeshRawImage = None
        self.unk_0C: int = 0
        self.tlut: int = 0 # no vanilla rooms use tluts
        self.width: int = 0
        self.height: int = 0
        self.fmt: int = 0
        self.siz: int = 0
        self.tlutMode: int = 0
        self.tlutCount: int = 0

    @staticmethod
    def decode(file: FileDataRelocator, cursor: int) -> RoomMeshImage:
        image = RoomMeshImage()
        image_offset, image_file = file.get_offset(cursor)
        if image_file is None:
            raise RoomFileAddressException(file, file.rom.read_byte(cursor), cursor, 'background image')
        image.source = RoomMeshRawImage.decode(image_file, image_offset)
        file.add_record(image_file.data_records, image.source)
        # 0x04 == unk_0C (u32), always 0 in vanilla
        # 0x08 == tlut (pointer), not used in vanilla
        image.width = file.rom.read_int16(cursor + 0x0C)
        image.height = file.rom.read_int16(cursor + 0x0E)
        image.fmt = file.rom.read_byte(cursor + 0x10)
        image.siz = file.rom.read_byte(cursor + 0x11)
        # tlutMode and tlutCount never used, always 0 u16s
        return image

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.source.get_segment_address_bytes())
        bytes.extend(int.to_bytes(0, 8, 'big'))
        bytes.extend(self.width.to_bytes(2, 'big'))
        bytes.extend(self.height.to_bytes(2, 'big'))
        bytes.extend(self.fmt.to_bytes(1, 'big'))
        bytes.extend(self.siz.to_bytes(1, 'big'))
        bytes.extend(int.to_bytes(0, 4, 'big'))
        return bytes


# Textures are 16 byte aligned in vanilla
class RoomMeshRawImage(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: int) -> None:
        super().__init__(file, RecordType.BackgroundImage, file.start, offset, length)
        self.align = 16

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int = -1) -> RoomMeshRawImage:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.BackgroundImage)
        if existing_record is not None:
            return existing_record
        # Jpgs use the whole sceen buffer, which is a u16 matrix.
        return RoomMeshRawImage(file, offset, 320 * 240 * 2)


# 16 byte aligned in vanilla
class RoomMeshImageMultiEntries(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: int) -> None:
        super().__init__(file, RecordType.Backgrounds, file.start, offset, length)
        self.backgrounds: list[RoomMeshImageMultiEntry] = []
        self.align = 16

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int = -1) -> RoomMeshImageMultiEntries:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.Backgrounds)
        if existing_record is not None:
            return existing_record
        mesh = RoomMeshImageMultiEntries(file, offset, length)
        num_backgrounds = int(length / 0x1C)
        cursor = mesh.start + mesh.offset
        for i in range(0, num_backgrounds):
            mesh.backgrounds.append(RoomMeshImageMultiEntry.decode(file, cursor + i * 0x1C))
        return mesh

    def encode(self) -> bytearray:
        bytes = bytearray()
        for background in self.backgrounds:
            bytes.extend(background.encode())
        return bytes


# Data only, part of multi-image backround list just above
class RoomMeshImageMultiEntry:
    def __init__(self) -> None:
        self.unk_00: int = 0
        self.bgCamIndex: int = 0
        self.background: RoomMeshImage = None

    @staticmethod
    def decode(file: FileDataRelocator, cursor: int) -> RoomMeshImageMultiEntry:
        entry = RoomMeshImageMultiEntry()
        entry.unk_00 = file.rom.read_int16(cursor)
        entry.bgCamIndex = file.rom.read_byte(cursor + 0x02)
        entry.background = RoomMeshImage.decode(file, cursor + 0x04)
        return entry

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(self.unk_00.to_bytes(2, 'big'))
        bytes.extend(self.bgCamIndex.to_bytes(1, 'big'))
        bytes.extend(int.to_bytes(0, 1, 'big'))
        bytes.extend(self.background.encode())
        bytes.extend(int.to_bytes(0, 2, 'big'))
        return bytes


# 16 byte aligned in vanilla
class RoomMeshCullableHeader(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: int) -> None:
        super().__init__(file, RecordType.MeshHeaderCullable, file.start, offset, length)
        self.display_list_entries: RoomMeshDLCullableEntries = None
        self.align = 16

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int) -> RoomMeshCullableHeader:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.MeshHeaderCullable)
        if existing_record is not None:
            return existing_record
        mesh = RoomMeshCullableHeader(file, offset, length)
        cursor = mesh.start + mesh.offset
        list_offset, list_file = file.get_offset(cursor + 0x04)
        if list_file is None:
            raise RoomFileAddressException(file, file.rom.read_byte(cursor + 0x04), cursor + 0x04, 'display list')
        list_end = segment_address_offset(file.rom.read_int32(cursor + 0x08))
        display_list = RoomMeshDLCullableEntries.decode(list_file, list_offset, list_end - list_offset)
        mesh.display_list_entries = display_list
        file.add_record(list_file.data_records, display_list)
        return mesh

    def encode(self) -> bytearray:
        bytes = bytearray()
        bytes.extend(int.to_bytes(0x02, 1, 'big'))
        bytes.extend(int(self.display_list_entries.length / 0x10).to_bytes(1, 'big'))
        bytes.extend(int.to_bytes(0, 2, 'big'))
        bytes.extend(self.display_list_entries.get_segment_address_bytes())
        bytes.extend(create_segment_address(self.display_list_entries.file.type.value, self.display_list_entries.offset + self.display_list_entries.length).to_bytes(4, 'big'))
        return bytes


# 4 byte aligned in vanilla
class RoomMeshDLEntries(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: int) -> None:
        super().__init__(file, RecordType.DlistEntries, file.start, offset, length)
        self.entries: list[tuple[Optional[RoomMeshDL], Optional[RoomMeshDL]]] = []

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int) -> RoomMeshDLEntries:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.DlistEntries)
        if existing_record is not None:
            return existing_record
        num_entries = int(length / 0x08)
        dl_entries = RoomMeshDLEntries(file, offset, length)
        cursor = dl_entries.start + dl_entries.offset
        for i in range(0, num_entries):
            opa_offset, opa_file = file.get_offset(cursor)
            xlu_offset, xlu_file = file.get_offset(cursor + 0x04)
            if opa_offset == 0 and opa_file is None:
                opa = None
            elif opa_file is None:
                raise RoomFileAddressException(file, file.rom.read_byte(cursor), cursor, 'opaque mesh display list')
            else:
                opa = RoomMeshDL.decode(opa_file, opa_offset)
            if xlu_offset == 0 and xlu_file is None:
                xlu = None
            elif xlu_file is None:
                raise RoomFileAddressException(file, file.rom.read_byte(cursor + 0x04), cursor + 0x04, 'transparent mesh display list')
            else:
                xlu = RoomMeshDL.decode(xlu_file, xlu_offset)
            dl_entries.entries.append((opa, xlu))
            if opa is not None:
                file.add_record(opa_file.data_records, opa)
            if xlu is not None:
                file.add_record(xlu_file.data_records, xlu)
            cursor += 0x08
        return dl_entries

    def encode(self) -> bytearray:
        bytes: bytearray = bytearray()
        for opa, xlu in self.entries:
            if opa is None:
                bytes.extend(int.to_bytes(0, 4, 'big'))
            else:
                bytes.extend(opa.get_segment_address_bytes())
            if xlu is None:
                bytes.extend(int.to_bytes(0, 4, 'big'))
            else:
                bytes.extend(xlu.get_segment_address_bytes())
        return bytes


# 4 byte aligned in vanilla
class RoomMeshDLCullableEntries(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: int) -> None:
        super().__init__(file, RecordType.DlistCullableEntries, file.start, offset, length)
        self.entries: list[RoomMeshDLCullableEntry] = []

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int) -> RoomMeshDLCullableEntries:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.DlistCullableEntries)
        if existing_record is not None:
            return existing_record
        num_entries = int(length / 0x10)
        dl_entries = RoomMeshDLCullableEntries(file, offset, length)
        cursor = dl_entries.start + dl_entries.offset
        for i in range(0, num_entries):
            dl_entries.entries.append(RoomMeshDLCullableEntry.decode(file, cursor + 0x10 * i))
        return dl_entries

    def encode(self) -> bytearray:
        bytes: bytearray = bytearray()
        for entry in self.entries:
            bytes.extend(entry.boundsSphereCenter.encode())
            bytes.extend(entry.boundsSphereRadius.to_bytes(2, 'big', signed=True))
            if entry.opa is None:
                bytes.extend(int.to_bytes(0, 4, 'big'))
            else:
                bytes.extend(entry.opa.get_segment_address_bytes())
            if entry.xlu is None:
                bytes.extend(int.to_bytes(0, 4, 'big'))
            else:
                bytes.extend(entry.xlu.get_segment_address_bytes())
        return bytes


# Data only, used in cullable display list list
class RoomMeshDLCullableEntry:
    def __init__(self, boundsSphereCenter: Vec3s, boundsSphereRadius: int, opa: Optional[RoomMeshDL], xlu: Optional[RoomMeshDL]) -> None:
        self.boundsSphereCenter: Vec3s = boundsSphereCenter
        self.boundsSphereRadius: int = boundsSphereRadius
        self.opa: Optional[RoomMeshDL] = opa
        self.xlu: Optional[RoomMeshDL] = xlu

    @staticmethod
    def decode(file: FileDataRelocator, cursor: int) -> RoomMeshDLCullableEntry:
        opa_offset, opa_file = file.get_offset(cursor + 0x08)
        xlu_offset, xlu_file = file.get_offset(cursor + 0x0C)
        if opa_offset == 0 and opa_file is None:
            opa = None
        elif opa_file is None:
            raise RoomFileAddressException(file, file.rom.read_byte(cursor), cursor, 'opaque mesh display list')
        else:
            opa = RoomMeshDL.decode(opa_file, opa_offset)
        if xlu_offset == 0 and xlu_file is None:
            xlu = None
        elif xlu_file is None:
            raise RoomFileAddressException(file, file.rom.read_byte(cursor + 0x04), cursor + 0x04, 'transparent mesh display list')
        else:
            xlu = RoomMeshDL.decode(xlu_file, xlu_offset)
        if opa is not None:
            file.add_record(opa_file.data_records, opa)
        if xlu is not None:
            file.add_record(xlu_file.data_records, xlu)
        return RoomMeshDLCullableEntry(
            Vec3s.decode(file.rom, cursor),
            file.rom.read_s16(cursor + 0x06),
            opa,
            xlu
        )


# 8 byte aligned in vanilla
class RoomMeshDL(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: int) -> None:
        super().__init__(file, RecordType.Dlist, file.start, offset, length)
        self.external_references: list[DisplayListRecord] = []
        self.align = 8

    def decode(file: FileDataRelocator, offset: int, length: int = -1) -> RoomMeshDL:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.Dlist)
        if existing_record is not None:
            return existing_record
        dlist = RoomMeshDL(file, offset, length)
        dlist_start = dlist.start + dlist.offset
        cursor = dlist_start
        end_dl_code = 0xDF
        branch_code = 0xDE
        while True:
            op_code = file.rom.read_byte(cursor)
            no_push = file.rom.read_byte(cursor + 0x01)
            if op_code == end_dl_code or (op_code == branch_code and no_push == 1):
                cursor += 0x08
                break
            pointer_offset = cursor + 0x04
            op_offset, op_file = file.get_offset(pointer_offset)
            record: Optional[DataRecord] = None
            if op_code == 0x01:  # G_VTX
                if not is_external_resource(file, pointer_offset):
                    vtx_count = file.rom.read_int24(cursor + 0x01) >> 12
                    record = DisplayListVtxList.decode(op_file, op_offset, vtx_count * 0x10)
            elif op_code == 0xDA:  # G_MTX
                if not is_external_resource(file, pointer_offset):
                    record = DataRecord.decode(op_file, RecordType.Mtx, op_offset, 0x40)
            elif op_code == 0xDE:  # G_DL
                if not is_external_resource(file, pointer_offset):
                    record = RoomMeshDL.decode(op_file, op_offset)
            elif op_code == 0xE1:  # G_RDPHALF_1
                if not is_external_resource(file, pointer_offset):
                    lookahead_op = file.rom.read_byte(cursor + 0x08)
                    if lookahead_op == 0x04:  # G_BRANCH_Z
                        record = RoomMeshDL.decode(op_file, op_offset)
                    elif lookahead_op == 0xDD:  # G_LOAD_UCODE
                        raise Exception(
                            f'Unexpected gsSPLoadUcodeEx at 0x{cursor - file.start:08X} in {file.name}')
            elif op_code == 0xFD:  # G_SETTIMG
                if not is_external_resource(file, pointer_offset):
                    record = SceneTexture.decode(op_file, op_offset, -1)
            elif op_code == 0xFE:  # G_SETZIMG
                if not is_external_resource(file, pointer_offset):
                    record = SceneTexture.decode(op_file, op_offset, -1)
            elif op_code == 0xFF:  # G_SETCIMG
                if not is_external_resource(file, pointer_offset):
                    record = SceneTexture.decode(op_file, op_offset, -1)
            if record is not None:
                if record not in op_file.data_records:
                    op_file.data_records.append(record)
                dlist.external_references.append(DisplayListRecord(pointer_offset - dlist_start, record))
            cursor += 0x08
        dlist.length = cursor - dlist_start
        dlist.refresh_rom_data()
        return dlist

    def encode(self) -> bytearray:
        bytes = bytearray(self.data)
        for ref in self.external_references:
            bytes[ref.pointer_offset:ref.pointer_offset + 0x04] = ref.get_segment_address_bytes()
        return bytes


def is_external_resource(file: FileDataRelocator, pointer_offset: int) -> bool:
        segment = file.rom.read_byte(pointer_offset)
        offset = file.rom.read_int24(pointer_offset + 1)
        address = file.rom.read_int32(pointer_offset)
        if address == 0x800fedb0: # gMtxClear
            return True
        if segment == 0x06: # current object file (only in MIZUsin_room_0)
            return True
        if segment in [0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D] and offset == 0: # reference loaded resource
            return True
        if segment not in [0x02, 0x03]: # reference to resource outside scene/room files
            print(f'External resource (segment 0x{segment:0>2x} offset 0x{offset:0>6x}) found in display list in {file.name} at 0x{pointer_offset - file.start:0>8x} (VROM 0x{pointer_offset:0>8x})')
            return True
        return False


# Wrapper class for display list pointer references to permit merging asset objects
class DisplayListRecord:
    def __init__(self, pointer_offset: int, record: DataRecord, record_offset: int = 0) -> None:
        self.pointer_offset: int = pointer_offset
        self.record: DataRecord = record
        self.record_offset: int = record_offset

    def get_segment_address_bytes(self) -> bytes:
        record_address = create_segment_address(self.record.file.type.value, self.record.offset + self.record_offset)
        return record_address.to_bytes(4, 'big')


# 8 byte aligned in vanilla
class DisplayListVtxList(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: int) -> None:
        super().__init__(file, RecordType.Vtx, file.start, offset, length)
        self.align = 8

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int) -> DisplayListVtxList:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.Vtx)
        if existing_record is not None:
            return existing_record
        return DisplayListVtxList(file, offset, length)

    def merge(self, other_record: DataRecord):
        low_record, high_record, lower_overlap = super().merge(other_record)
        parent: SceneDataRelocator | RoomDataRelocator = low_record.file
        if isinstance(parent, SceneDataRelocator):
            for room_file in parent.rooms:
                low_record._merge_in_file(room_file, high_record, lower_overlap)

    def _merge_in_file(self, file: FileDataRelocator, other_record: DataRecord, record_offset: int):
        dlists: list[RoomMeshDL] = list(filter(lambda r: r.type == RecordType.Dlist, file.data_records))
        for dlist in dlists:
            i = 0
            while i < len(dlist.external_references):
                if dlist.external_references[i].record is other_record:
                    ref = dlist.external_references.pop(i)
                    new_ref = DisplayListRecord(ref.pointer_offset, self, record_offset)
                    dlist.external_references.append(new_ref)
                    break
                i += 1


# 4 byte aligned in vanilla
class RoomObjectList(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> None:
        super().__init__(file, RecordType.ObjectList, file.start, offset, length)
        self.objects: list[int] = []

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int = -1) -> RoomObjectList:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.ObjectList)
        if existing_record is not None:
            return existing_record
        num_objects = int(length / 0x02)
        object_list = RoomObjectList(file, offset, length)
        cursor = object_list.start + object_list.offset
        for i in range(0, num_objects):
            object_list.objects.append(file.rom.read_int16(cursor + i * 0x02))
        return object_list

    def apply_patch(self, patch_data: list[str]) -> None:
        self.objects = []
        for object in patch_data:
            self.objects.append(int(object, 16))

    def encode(self) -> bytearray:
        bytes = bytearray()
        for object_id in self.objects:
            bytes.extend(object_id.to_bytes(2, 'big'))
        return bytes


# 4 byte aligned in vanilla
class RoomActorList(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: Optional[int] = -1) -> None:
        super().__init__(file, RecordType.ActorList, file.start, offset, length)
        self.actors: list[ActorEntry] = []

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int) -> RoomActorList:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.ActorList)
        if existing_record is not None:
            return existing_record
        num_actors = int(length / 0x10)
        actor_list = RoomActorList(file, offset, length)
        cursor = actor_list.start + actor_list.offset
        for i in range(0, num_actors):
            actor_list.actors.append(ActorEntry.decode(file.rom, cursor + i * 0x10))
        return actor_list

    def apply_patch(self, patch_data: list[str]) -> None:
        self.actors = []
        for actor in patch_data:
            self.actors.append(ActorEntry.from_json(actor))

    def encode(self) -> bytearray:
        bytes = bytearray()
        for entry in self.actors:
            bytes.extend(entry.encode())
        return bytes


# 8 byte aligned in vanilla
class SceneTexture(DataRecord):
    def __init__(self, file: FileDataRelocator, offset: int, length: int) -> None:
        super().__init__(file, RecordType.Texture, file.start, offset, length)
        if length < 0:
            self.delay_parsing = True
        self.align = 8

    @staticmethod
    def decode(file: FileDataRelocator, offset: int, length: int) -> SceneTexture:
        existing_record = file.get_existing_record_by_offset(offset, RecordType.Texture)
        if existing_record is not None:
            return existing_record
        return SceneTexture(file, offset, length)

    def decode_late(self) -> None:
        self.length = self.file.get_record_length_from_neighbor(self)
        self.refresh_rom_data()
        self.delay_parsing = False


def scene_resource_factory(file: FileDataRelocator, offset: int, type: str, attrib: dict[str, str]) -> None:
    if type == 'Scene':
        if offset == 0:
            file.parse()
        else:
            file.data_records.append(SceneHeader.decode(file, offset))
    elif type == 'Room':
        if offset == 0:
            file.parse()
        else:
            file.data_records.append(RoomHeader.decode(file, offset))
    elif type == 'Texture':
        bytes_per_pixel = 0
        if attrib['Format'] == 'rgba32':
            bytes_per_pixel = 4
        if attrib['Format'] == 'rgba16':
            bytes_per_pixel = 2
        if attrib['Format'] == 'i4':
            bytes_per_pixel = 0.5
        if attrib['Format'] == 'i8':
            bytes_per_pixel = 1
        if attrib['Format'] == 'ia4':
            bytes_per_pixel = 0.5
        if attrib['Format'] == 'ia8':
            bytes_per_pixel = 1
        if attrib['Format'] == 'ia16':
            bytes_per_pixel = 2
        if attrib['Format'] == 'ci4':
            bytes_per_pixel = 0.5
        if attrib['Format'] == 'ci8':
            bytes_per_pixel = 1
        size = int(attrib['Width']) * int(attrib['Height']) * bytes_per_pixel
        if int(size) != size:
            raise Exception(f'Non integer texture size in {file.name} at offset {offset:0>8x}')
        size = int(size)
        file.data_records.append(SceneTexture.decode(file, offset, size))
    elif type == 'Cutscene':
        file.data_records.append(SceneCutsceneData.decode(file, offset))
    elif type == 'Path':
        file.data_records.append(ScenePathList.decode(file, offset, int(attrib['NumPaths']) * 0x08))
    elif type == 'DList':
        file.data_records.append(RoomMeshDL.decode(file, offset))
    elif type == 'Blob':
        file.data_records.append(DataRecord.decode(file, RecordType.Blob, offset, int(attrib['Size'], 16)))
    else:
        raise Exception(f'Unrecognized resource type when parsing scenes: {type}')


# Convenience class to wrap scene parsing, writing, and in-process changes into one object.
class Scenes:
    def __init__(self, rom: Rom) -> None:
        self.scene_list: list[SceneDataRelocator] = parse_scene_data(rom)
        self._index = 0

    def write_to_rom(self, rom: Rom) -> None:
        file_start: int = 0x01F12000 # original start of scene/room files
        files = [scene for scene in self.scene_list]
        files.extend([room for scene in self.scene_list for room in scene.rooms])
        files.sort(key=lambda f: f.start)
        files_end: int = max([file.end for file in files])
        for file in files:
            file_start = file.update_start_and_end(file_start)
        new_files_end: int = max([file.end for file in files])
        for file in files:
            file.write(rom)
        if files_end > new_files_end:
            print(f'Wrote scene files to rom. You saved 0x{files_end - new_files_end:x} bytes! Hooray! 🎉')
        else:
            print(f'Wrote scene files to rom. You used 0x{new_files_end - files_end:x} additional bytes! 🫤')

    def append(self, scene: SceneDataRelocator) -> None:
        self.scene_list.append(scene)

    def __getitem__(self, scene_id: int) -> SceneDataRelocator:
        if scene_id >= len(self.scene_list):
            raise IndexError(f'Scene ID {scene_id} is out of range. Valid values: 0 - {len(self.scene_list) - 1}.')
        return self.scene_list[scene_id]

    def __setitem__(self, scene_id: int, scene: SceneDataRelocator) -> None:
        if scene_id >= len(self.scene_list):
            raise IndexError(f'Scene ID {scene_id} is out of range. Valid values: 0 - {len(self.scene_list)}.')
        self.scene_list[scene_id] = scene

    def __delitem__(self, scene_id: int) -> None:
        if scene_id >= len(self.scene_list):
            raise IndexError(f'Scene ID {scene_id} is out of range. Valid values: 0 - {len(self.scene_list) - 1}.')
        self.scene_list.pop(scene_id)

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index >= len(self.scene_list):
            raise StopIteration
        scene = self.scene_list[self._index]
        self._index += 1
        return scene


# Entry function to parse the vanilla rom using ZAPD xml resources for oot-ntsc-1.0.
def parse_scene_data(rom: Rom) -> list[SceneDataRelocator]:
    logger = logging.getLogger('')
    logger.debug('Reading scene files from ROM')
    xml_dir = data_path('scenes')
    # XML files may not be read in the same order as the scene IDs
    scenes: list[Optional[SceneDataRelocator]] = [None for _ in range(0x00, 0x65)]
    for subdir, _, files in walk(xml_dir):
        for zapd_xml in files:
            scene_id = -1
            tree = ET.parse(path.join(subdir, zapd_xml))
            root = tree.getroot()
            for file in root:
                filename = file.attrib['Name']
                segment = int(file.attrib['Segment'])
                current_file: FileDataRelocator = None
                if segment == 0x02:
                    ids = list(filter(lambda row: row[1] == filename, SCENE_TABLE.values()))
                    if len(ids) == 0:
                        raise Exception(f'Unknown filename from ZAPD XML files: {filename}')
                    if len(ids) > 1:
                        raise Exception(f'Multiple scenes match filename {filename}')
                    scene_id = ids[0][0]
                    scene_start = rom.read_int32(SCENE_TABLE_ADDRESS + (scene_id * 0x14))
                    entry = rom.dma.get_dmadata_record_by_key(scene_start)
                    scene_end = entry.end
                    scene_file = SceneDataRelocator(rom, filename, scene_start, scene_end)
                    current_file = scene_file
                elif segment == 0x03:
                    # rooms always defined after parent scene
                    room_num = int(filename.split('_')[-1])
                    current_file = scene_file.rooms[room_num]
                else:
                    raise Exception(f'Attempted to parse ZAPD XML file {filename} with type (segment {segment}) that is not a scene (segment 0x02) or room (segment 0x03)')
                logger.debug(f'Parsing file {current_file.name}')
                for res in file:
                    offset = int(res.attrib['Offset'], 16)
                    res_type = res.tag
                    scene_resource_factory(current_file, offset, res_type, res.attrib)
                # Don't finalize scene files until all rooms have been parsed
                # in case they have any references to the parent scene file for
                # new records
                if segment == 0x03:
                    current_file.finalize()
            if scene_id < 0 or scene_file is None:
                raise Exception(f'Something went wrong parsing {zapd_xml}. Scene file not found.')
            scene_file.finalize()
            scenes[scene_id] = scene_file
            # Just to be safe in case the XML gets mangled
            scene_file = None
    # Double check that all scenes have been parsed
    for scene_id, scene_file in enumerate(scenes):
        if scene_file is None or not scene_file.parsed:
            raise Exception(f'Scene 0x{scene_id:0>2x} was not parsed')
        for room_id, room_file in enumerate(scene_file.rooms):
            if room_file is None or not room_file.parsed:
                raise Exception(f'Room {room_id} in Scene 0x{scene_id:0>2x} was not parsed')
    logger.debug('Finished parsing scene files')
    return scenes


# Helper test function for check_external_reference_locations
def check_references_for_file(rom: Rom, file: FileDataRelocator) -> int:
    checked_refs = 0
    if file.name in SCENE_EXTERNAL_REFERENCES.keys():
        for record_type, offset, data_references, code_references in SCENE_EXTERNAL_REFERENCES[file.name]:
            record = file.get_existing_record_by_offset(offset, record_type)
            if record is None:
                raise Exception(f'Offset {offset:0>6x} does not match any records in {file.name}')
            address = create_segment_address(file.type.value, offset)
            address_low = address & 0xFFFF
            address_high = (address >> 16) + (1 if address_low > 0x7FFF else 0)
            for data_address in data_references:
                if rom.read_int32(data_address) != address:
                    raise Exception(f'Data reference address {data_address:0>8x} does not match record address {address:0>8x} for {file.name}')
                checked_refs += 1
            for high_ref, low_ref in code_references:
                if rom.read_int16(high_ref) != address_high:
                    raise Exception(f'Data reference address {high_ref:0>8x} does not match record address top half {address_high:0>4x} for {file.name}')
                checked_refs += 1
                if rom.read_int16(low_ref) != address_low:
                    raise Exception(f'Data reference address {low_ref:0>8x} does not match record address bottom half {address_low:0>4x} for {file.name}')
                checked_refs += 1
    return checked_refs


# Test function to verify all external pointer locations are correct.
def check_external_reference_locations(rom: Rom):
    scene_list = parse_scene_data(rom)
    checked_refs = 0
    for scene in scene_list:
        checked_refs += check_references_for_file(rom, scene)
        for room in scene.rooms:
            checked_refs += check_references_for_file(rom, room)
    print (f'Checked {checked_refs} rom addresses. All passed :)')


# Test function to compare scene/room encode function output to the
# vanilla file contents and verify they match.
def compare_parsed_data_to_rom(rom: Rom, save_files: bool = False):
    scene_list = parse_scene_data(rom)
    print('Done parsing')
    for scene in scene_list:
        scene_bytes = scene.encode()
        if save_files:
            with open('scene_out', 'wb') as f:
                f.write(scene_bytes)
        _, vrom_start, vrom_end = SCENE_AND_ROOM_FILES[scene.name]
        rom_scene = rom.read_bytes(vrom_start, vrom_end - vrom_start)
        if len(rom_scene) != len(scene_bytes):
            print(f'Length mismatch for {scene.name}. Vanilla: {len(rom_scene):0>8x} Encode: {len(scene_bytes):0>8x}')
        else:
            print(f'Lengths match for {scene.name}')
        i = 0
        while i < len(rom_scene) and i < len(scene_bytes):
            # spot00_sceneCutsceneData_00E5F0 has only 29 commands, but vanilla lists it as 31.
            # No practical impact as the vanilla cutscene parser will return as soon as it hits
            # CS_END, so special case this cutscene to make sure it's counting commands correctly.
            if scene_bytes[i] != rom_scene[i] and not (i == 0xe5f3 and scene.name == 'spot00_scene' and scene_bytes[i] == 29):
                raise Exception(f'Byte mismatch in {scene.name} at offset 0x{i:0>8x}, address 0x{vrom_start + i:0>8x}. Vanilla: 0x{rom_scene[i]:0>2x} Encode: 0x{scene_bytes[i]:0>2x}')
            i += 1
        print(f'Bytes match for {scene.name}')
        for room in scene.rooms:
            room_bytes = room.encode()
            if save_files:
                with open('room_out', 'wb') as f:
                    f.write(room_bytes)
            _, vrom_start, vrom_end = SCENE_AND_ROOM_FILES[room.name]
            rom_room = rom.read_bytes(vrom_start, vrom_end - vrom_start)
            if len(rom_room) != len(room_bytes):
                print(f'Length mismatch for {room.name}. Vanilla: {len(rom_room):0>8x} Encode: {len(room_bytes):0>8x}')
            else:
                print(f'Lengths match for {room.name}')
            i = 0
            while i < len(rom_room) and i < len(room_bytes):
                if room_bytes[i] != rom_room[i]:
                    raise Exception(f'Byte mismatch in {room.name} at offset 0x{i:0>8x}, address 0x{vrom_start + i:0>8x}. Vanilla: 0x{rom_room[i]:0>2x} Encode: 0x{room_bytes[i]:0>2x}')
                i += 1
            print(f'Bytes match for {room.name}')
    print('Done comparing')


# Proof of concept functions to verify shifting functionality.
# Kakariko gold skulltula initialization parameters are changed
# to allow them to always spawn regardless of time of day, and
# skulltula actor/object entries are added to the day alternate
# scene headers, copied from the night headers.
def copy_skulltulas_to_day(day_header: RoomHeader, night_header: RoomHeader) -> None:
    ACTOR_EN_SW = 149
    OBJECT_ST = 36
    if OBJECT_ST not in day_header.object_list.objects:
        day_header.object_list.objects.append(OBJECT_ST)
    for actor in night_header.actor_list.actors:
        if actor.id == ACTOR_EN_SW:
            new_params = (actor.params & ~0xA000) | 0x8000
            new_actor = ActorEntry(actor.id, actor.pos.copy(), actor.rot.copy(), new_params)
            day_header.actor_list.actors.append(new_actor)


def make_kak_skulltulas_ignore_tod(rom: Rom):
    from Main import compress_rom

    # Modify room files
    scene_list = Scenes(rom)
    kakariko_outside = scene_list[0x52].rooms[0]
    child_day = kakariko_outside.headers[0]
    child_night = kakariko_outside.headers[1]
    adult_day = kakariko_outside.headers[2]
    adult_night = kakariko_outside.headers[3]
    copy_skulltulas_to_day(child_day, child_night)
    copy_skulltulas_to_day(adult_day, adult_night)
    scene_list.write_to_rom(rom)

    # patch Pokey out of the way
    rom.write_bytes(0xE5400A, [0x8C, 0x4C])
    rom.write_bytes(0xE5400E, [0xB4, 0xA4])
    rom.write_bytes(0xE5401C, [0x14, 0x0B])

    output_dir = './Output'
    uncompressed_filename = f"OOT_no_tod_skulls_uncompressed.z64"
    uncompressed_path = path.join(output_dir, uncompressed_filename)
    print(f"Saving Uncompressed ROM: {uncompressed_filename}")
    rom.write_to_file(uncompressed_path)
    print(f"Created uncompressed ROM at: {uncompressed_path}")
    compressed_filename = f"OOT_no_tod_skulls.z64"
    compressed_path = path.join(output_dir, compressed_filename)
    print(f"Compressing ROM: {compressed_filename}")
    compress_rom(uncompressed_path, compressed_path, False)
    print(f"Created compressed ROM at: {compressed_path}")


def extract_bytes_to_file(file: str, start: int, length: int, new_file: str) -> None:
    with open(file, 'rb') as f:
        file_bytes = bytearray(f.read())
    extracted_bytes = file_bytes[start:start + length]
    with open(new_file, 'wb') as f:
        f.write(extracted_bytes)


def compare_file_bytes(original_file: str, new_file: str) -> None:
    with open(original_file, 'rb') as f:
        original_bytes = bytearray(f.read())
    with open(new_file, 'rb') as f:
        new_bytes = bytearray(f.read())
    i = 0
    original_size = len(original_bytes)
    while i < original_size:
        if original_bytes[i] != new_bytes[i]:
            raise Exception(f'Byte mismatch at offset 0x{i:0>8x}. Original: 0x{original_bytes[i]:0>2x} New: 0x{new_bytes[i]:0>2x}')
        i += 1


if __name__ == '__main__':
    #uncompressed_rom = Rom('ZOOTDEC.z64')
    #compare_parsed_data_to_rom(uncompressed_rom, True)
    #check_external_reference_locations(uncompressed_rom)
    #make_kak_skulltulas_ignore_tod(uncompressed_rom)
    extract_bytes_to_file('/home/mracsys/Downloads/OoT-Randomizer-8.1/Output/OoT_B30A4_U3W20VJA0O_uncompressed.z64', 0x253C080, 0x171E0, 'Output/stable_tokinoma_scene.bin')
    extract_bytes_to_file('Output/OoT_D5F29_WKF8ODY7FJ_uncompressed.z64', 0x24F0FF0, 0x171E8, 'Output/new_tokinoma_scene.bin')
    compare_file_bytes('Output/stable_tokinoma_scene.bin', 'Output/new_tokinoma_scene.bin')
