# mzxrules 2018
# updated by mracsys 2025
# In order to patch MQ to the existing data...
#
# Scenes:
#
# Ice Cavern (Scene 9) needs to have its header altered to support MQ's path list. This
# expansion will delete the otherwise unused alternate headers command
#
# Transition actors will be patched over the old data
# Path data will be appended to the end of the scene file.
#
# The size of a single path on file is NUM_POINTS * 6, rounded up to the nearest 4 byte boundary
# The total size consumed by the path data is NUM_PATHS * 8, plus the sum of all path file sizes
# padded to the nearest 0x10 bytes. Sizing is handled automatically by the ScenePathVtxList class.
#
# Collision:
# OoT's collision data consists of these elements: vertices, surface types, water boxes,
# camera behavior data, and polys. MQ's vertice and polygon geometry data is identical.
# However, the surface types and the collision exclusion flags bound to the polys have changed
# for some polygons, as well as the number of surface type records and camera type records.
#
# Collision patching no longer uses the 'IsLarger' flag. The SceneDataRelocator class shifts
# each record within the scene file to fit any expansions in collision data.
#
# Rooms:
#
# Object file initialization data overwrites the existing list.
# The total size consumed by the object file data is NUM_OBJECTS * 0x02, aligned to
# the nearest 0x04 bytes
#
# Actor spawn data also overwrites the existing list.
# The total size consumed by the actor spawn data is NUM_ACTORS * 0x10
#
# Finally:
#
# Scene and room files will be padded to the nearest 0x10 bytes
#
# Maps:
# Jabu Jabu's B1 map contains no chests in the vanilla layout. Because of this,
# the floor map data is missing a vertex pointer that would point within kaleido_scope.
# As such, if the kaleido_scope file moves, the patch will break.
# Map data is not contained within scene or room files.
# It is written directly to the rom in write_map_data.

from __future__ import annotations
import json
from struct import pack, unpack
from typing import Optional, Any, TYPE_CHECKING

from Rom import Rom
from Utils import data_path

if TYPE_CHECKING:
    from Scene import Scenes


class File:
    def __init__(self, name: str, start: int = 0, end: Optional[int] = None, remap: Optional[int] = None) -> None:
        self.name: str = name
        self.start: int = start
        self.end: int = end if end is not None else self.start
        self.remap: Optional[int] = remap
        self.from_file: int = self.start

        # used to update the file's associated dmadata record
        self.dma_key: int = self.start

    @classmethod
    def from_json(cls, file: dict[str, Optional[str]]) -> File:
        return cls(
            file['Name'],
            int(file['Start'], 16) if file.get('Start', None) is not None else 0,
            int(file['End'], 16) if file.get('End', None) is not None else None,
            int(file['RemapStart'], 16) if file.get('RemapStart', None) is not None else None
        )

    def __repr__(self) -> str:
        remap = "None"
        if self.remap is not None:
            remap = "{0:x}".format(self.remap)
        return "{0}: {1:x} {2:x}, remap {3}".format(self.name, self.start, self.end, remap)

    def relocate(self, rom: Rom) -> None:
        if self.remap is None:
            self.remap = rom.dma.free_space()

        new_start = self.remap

        offset = new_start - self.start
        new_end = self.end + offset

        rom.buffer[new_start:new_end] = rom.buffer[self.start:self.end]
        self.start = new_start
        self.end = new_end
        update_dmadata(rom, self)

    # The file will now refer to the new copy of the file
    def copy(self, rom: Rom) -> None:
        self.dma_key = None
        self.relocate(rom)


class Icon:
    def __init__(self, data: dict[str, int | list[dict[str, int]]]) -> None:
        self.icon: int = data["Icon"]
        self.count: int = data["Count"]
        self.points: list[IconPoint] = [IconPoint(x) for x in data["IconPoints"]]

    def write_to_minimap(self, rom: Rom, addr: int) -> None:
        rom.write_sbyte(addr, self.icon)
        rom.write_byte(addr + 1,  self.count)
        cur = 2
        for p in self.points:
            p.write_to_minimap(rom, addr + cur)
            cur += 0x03

    def write_to_floormap(self, rom: Rom, addr: int) -> None:
        rom.write_int16(addr, self.icon)
        rom.write_int32(addr + 0x10, self.count)

        cur = 0x14
        for p in self.points:
            p.write_to_floormap(rom, addr + cur)
            cur += 0x0C


class IconPoint:
    def __init__(self, point: dict[str, int]) -> None:
        self.flag = point["Flag"]
        self.x = point["x"]
        self.y = point["y"]

    def write_to_minimap(self, rom: Rom, addr: int) -> None:
        rom.write_sbyte(addr, self.flag)
        rom.write_byte(addr+1, self.x)
        rom.write_byte(addr+2, self.y)

    def write_to_floormap(self, rom: Rom, addr: int) -> None:
        rom.write_int16(addr, self.flag)
        rom.write_f32(addr + 4, float(self.x))
        rom.write_f32(addr + 8, float(self.y))


def write_map_data(rom: Rom, scene_id: int, minimap_data, floormap_data) -> None:
    if scene_id >= 10:
        return

    minimaps: list[list[Icon]] = [[Icon(icon) for icon in minimap['Icons']] for minimap in minimap_data]
    floormaps: list[list[Icon]] = [[Icon(icon) for icon in floormap['Icons']] for floormap in floormap_data]

    # write floormap
    floormap_indices = 0xB6C934
    floormap_vrom = 0xBC7E00
    floormap_index = rom.read_int16(floormap_indices + (scene_id * 2))
    floormap_index //= 2  # game uses texture index, where two textures are used per floor

    cur = floormap_vrom + (floormap_index * 0x1EC)
    for floormap in floormaps:
        for icon in floormap:
            Icon.write_to_floormap(icon, rom, cur)
            cur += 0xA4

    # fixes jabu jabu floor B1 having no chest data
    if scene_id == 2:
        cur = floormap_vrom + (0x08 * 0x1EC + 4)
        kaleido_scope_chest_verts = 0x803A3DA0  # hax, should be vram 0x8082EA00
        rom.write_int32s(cur, [0x17, kaleido_scope_chest_verts, 0x04])

    # write minimaps
    map_mark_vrom = 0xBF40D0
    map_mark_vram = 0x808567F0
    map_mark_array_vram = 0x8085D2DC  # ptr array in map_mark_data to minimap "marks"

    array_vrom = map_mark_array_vram - map_mark_vram + map_mark_vrom
    map_mark_scene_vram = rom.read_int32(scene_id * 4 + array_vrom)
    mark_vrom = map_mark_scene_vram - map_mark_vram + map_mark_vrom

    cur = mark_vrom
    for minimap in minimaps:
        for icon in minimap:
            Icon.write_to_minimap(icon, rom, cur)
            cur += 0x26


def patch_files(scenes: Scenes, mq_scenes: list[int]) -> None:
    patch_data = get_json()
    for scene in patch_data:
        if scene['Id'] in mq_scenes:
            scenes[scene['Id']].apply_mq_patch(scene)


def get_json() -> Any:
    with open(data_path('mqu.json'), 'r') as stream:
        data = json.load(stream)
    return data


def update_dmadata(rom: Rom, file: File) -> None:
    key, start, end, from_file = file.dma_key, file.start, file.end, file.from_file
    rom.update_dmadata_record_by_key(key, start, end, from_file)
    file.dma_key = file.start


def align4(value: int) -> int:
    return ((value + 3) // 4) * 4


def align8(value: int) -> int:
    return ((value + 7) // 8) * 8


def align16(value: int) -> int:
    return ((value + 0xF) // 0x10) * 0x10


def align_file(value: int) -> int:
    return align16(value)

# This function inserts space in a ovl section at the section's offset
# The section size is expanded
# Every relocation entry in the section after the offset is moved accordingly
# Every relocation value that is after the inserted space is increased accordingly
def insert_space(rom: Rom, file: File, vram_start: int, insert_section: int, insert_offset: int, insert_size: int) -> None:
    sections = []
    val_hi = {}
    adr_hi = {}

    # get the ovl header
    cur = file.end - rom.read_int32(file.end - 4)
    section_total = 0
    for i in range(0, 4):
        # build the section offsets
        section_size = rom.read_int32(cur)
        sections.append(section_total)
        section_total += section_size

        # increase the section to be expanded
        if insert_section == i:
            rom.write_int32(cur, section_size + insert_size)

        cur += 4

    # calculate the insert address in vram
    insert_vram = sections[insert_section] + insert_offset + vram_start
    insert_rom = sections[insert_section] + insert_offset + file.start

    # iterate over the relocation table
    relocate_count = rom.read_int32(cur)
    cur += 4
    for i in range(0, relocate_count):
        entry = rom.read_int32(cur)

        # parse relocation entry
        section = ((entry & 0xC0000000) >> 30) - 1
        type = (entry & 0x3F000000) >> 24
        offset = entry & 0x00FFFFFF

        # calculate relocation address in rom
        address = file.start + sections[section] + offset

        # move relocation if section is increased and it's after the insert
        if insert_section == section and offset >= insert_offset:
            # rebuild new relocation entry
            rom.write_int32(cur,
                ((section + 1) << 30) |
                (type << 24) |
                (offset + insert_size))

        # value contains the vram address
        value = rom.read_int32(address)
        reg = None
        if type == 2:
            # Data entry: value is the raw vram address
            pass
        elif type == 4:
            # Jump OP: Get the address from a Jump instruction
            value = 0x80000000 | (value & 0x03FFFFFF) << 2
        elif type == 5:
            # Load High: Upper half of an address load
            reg = (value >> 16) & 0x1F
            val_hi[reg] = (value & 0x0000FFFF) << 16
            adr_hi[reg] = address
            # Do not process, wait until the lower half is read
            value = None
        elif type == 6:
            # Load Low: Lower half of the address load
            reg = (value >> 21) & 0x1F
            val_low = value & 0x0000FFFF
            val_low = unpack('h', pack('H', val_low))[0]
            # combine with previous load high
            value = val_hi[reg] + val_low
        else:
            # unknown. OoT does not use any other types
            value = None

        # update the vram values if it's been moved
        if value is not None and value >= insert_vram:
            # value = new vram address
            new_value = value + insert_size

            if type == 2:
                # Data entry: value is the raw vram address
                rom.write_int32(address, new_value)
            elif type == 4:
                # Jump OP: Set the address in the Jump instruction
                op = rom.read_int32(address) & 0xFC000000
                new_value = (new_value & 0x0FFFFFFC) >> 2
                new_value = op | new_value
                rom.write_int32(address, new_value)
            elif type == 6:
                # Load Low: Lower half of the address load
                op = rom.read_int32(address) & 0xFFFF0000
                new_val_low = new_value & 0x0000FFFF
                rom.write_int32(address, op | new_val_low)

                # Load High: Upper half of an address load
                op = rom.read_int32(adr_hi[reg]) & 0xFFFF0000
                new_val_hi = (new_value & 0xFFFF0000) >> 16
                if new_val_low >= 0x8000:
                    # add 1 if the lower part is negative for borrow
                    new_val_hi += 1
                rom.write_int32(adr_hi[reg], op | new_val_hi)

        cur += 4

    # Move rom bytes
    rom.buffer[(insert_rom + insert_size):(file.end + insert_size)] = rom.buffer[insert_rom:file.end]
    rom.buffer[insert_rom:(insert_rom + insert_size)] = [0] * insert_size
    file.end += insert_size


def add_relocations(rom: Rom, file: File, addresses: list[int | tuple[int, int]]) -> None:
    relocations = []
    sections = []
    header_size = rom.read_int32(file.end - 4)
    header = file.end - header_size
    cur = header

    # read section sizes and build offsets
    section_total = 0
    for i in range(0, 4):
        section_size = rom.read_int32(cur)
        sections.append(section_total)
        section_total += section_size
        cur += 4

    # get all entries in relocation table
    relocate_count = rom.read_int32(cur)
    cur += 4
    for i in range(0, relocate_count):
        relocations.append(rom.read_int32(cur))
        cur += 4

    # create new enties
    for address in addresses:
        if isinstance(address, tuple):
            # if type provided use it
            type, address = address
        else:
            # Otherwise, try to infer type from value
            value = rom.read_int32(address)
            op = value >> 26
            type = 2 # default: data
            if op == 0x02 or op == 0x03: # j or jal
                type = 4
            elif op == 0x0F: # lui
                type = 5
            elif op == 0x08: # addi
                type = 6

        # Calculate section and offset
        address = address - file.start
        section = 0
        for section_start in sections:
            if address >= section_start:
                section += 1
            else:
                break
        offset = address - sections[section - 1]

        # generate relocation entry
        relocations.append((section << 30)
                        | (type << 24)
                        | (offset & 0x00FFFFFF))

    # Rebuild Relocation Table
    cur = header + 0x10
    relocations.sort(key = lambda val: val & 0xC0FFFFFF)
    rom.write_int32(cur, len(relocations))
    cur += 4
    for relocation in relocations:
        rom.write_int32(cur, relocation)
        cur += 4

    # Add padded 0?
    rom.write_int32(cur, 0)
    cur += 4

    # Update Header and File size
    new_header_size = (cur + 4) - header
    rom.write_int32(cur, new_header_size)
    file.end += (new_header_size - header_size)
