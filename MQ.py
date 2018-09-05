# mzxrules 2018
#
# In order to patch MQ to the existing data...
# 
# Ice Cavern (Scene 9) needs to have it's header altered to support MQ's path list. This 
# expansion will delete the otherwise unused alternate headers command
# 
# Scenes:
# 
# Transition actors will be patched over the old data, as the number of records is the same
# Path data will be appended to the end of the scene file. 
# 
# The size of a single path on file is NUM_POINTS * 6, rounded up to the nearest 4 byte boundary
# The total size consumed by the path data is NUM_PATHS * 8, plus the sum of all path file sizes
# padded to the nearest 0x10 bytes
# 
# Rooms:
# 
# Object file initialization data will be appended to the end of the room file.
# The total size consumed by the object file data is NUM_OBJECTS * 0x02, aligned to
# the nearest 0x04 bytes
# 
# Actor spawn data will be appended to the end of the room file, after the objects.
# The total size consumed by the actor spawn data is NUM_ACTORS * 0x10
# 
# Finally:
# 
# Scene and room files will be padded to the nearest 0x10 bytes

from Utils import local_path
from Rom import LocalRom
import json

SCENE_DMADATA = 0xB320 # address where scene files begin to appear in dmadata
SCENE_TABLE = 0xB71440



class File(object):
    def __init__(self, file):
        self.name = file['Name']
        self.start = int(file['Start'], 16)
        self.end = int(file['End'], 16)
        self.remap = file['RemapStart']

        # used to update the file's associated dmadata record
        self.dma_key = self.start

        if self.remap is not None:
            self.remap = int(self.remap, 16)

    def __repr__(self):
        remap = "None"
        if self.remap is not None:
            remap = "{0:x}".format(self.remap)
        return "{0}: {1:x} {2:x}, remap {3}".format(self.name, self.start, self.end, remap)

    def relocate(self, rom:LocalRom):
        if self.remap is None:
            return

        new_start = self.remap
       
        offset = new_start - self.start
        new_end = self.end + offset

        rom.buffer[new_start:new_end] = rom.buffer[self.start:self.end]
        self.start = new_start
        self.end = new_end


class Scene(object):
    def __init__(self, scene):
        self.file = File(scene['File'])
        self.id = scene['Id']
        self.transition_actors = [convert_actor_data(x) for x in scene['TActors']]
        self.rooms = [Room(x) for x in scene['Rooms']]
        self.paths = []
        temp_paths = scene['Paths']
        for item in temp_paths:
            self.paths.append(item['Points'])


    def write_data(self, rom:LocalRom):
        
        # move file to remap address
        self.file.relocate(rom)

        start = self.file.start
        headcur = self.file.start

        room_list_offset = 0

        code = rom.read_byte(headcur)
        loop = 0x20
        while loop > 0 and code != 0x14: #terminator
            loop -= 1

            if code == 0x04: #rooms
                room_list_offset = rom.read_int24(headcur + 5)

            elif code == 0x0D: #paths
                path_offset = self.append_path_data(rom)
                rom.write_int32(headcur + 4, path_offset)

            elif code == 0x0E: #transition actors
                t_offset = rom.read_int24(headcur + 5)
                addr = self.file.start + t_offset
                write_actor_data(rom, addr, self.transition_actors)

            headcur += 8
            code = rom.read_byte(headcur)

        # update file references
        self.file.end = align16(self.file.end)
        update_dmadata(rom, self.file)
        update_scene_table(rom, self.id, self.file.start, self.file.end)
        
        # write room file data
        for room in self.rooms:
            room.write_data(rom)

        cur = self.file.start + room_list_offset
        for room in self.rooms:
            rom.write_int32s(cur, [room.file.start, room.file.end])
            cur += 0x08


    # appends path data to the end of the rom
    # returns segment address to path data
    def append_path_data(self, rom:LocalRom):
        start = self.file.start
        cur = self.file.end
        records = []
        records_offset = 0

        for path in self.paths:
            nodes = len(path)
            offset = get_segment_address(2, cur - start)
            records.append((nodes, offset))

            #flatten
            points = [x for points in path for x in points]
            rom.write_int16s(cur, points)
            path_size = align4(len(path) * 6)
            cur += path_size

        records_offset = get_segment_address(2, cur - start) 
        for node, offset in records:
            rom.write_byte(cur, node)
            rom.write_int32(cur + 4, offset)
            cur += 8

        self.file.end = cur
        return records_offset


class Room(object):
    def __init__(self, room):
        self.file = File(room['File'])
        self.id = room['Id']
        self.objects = [int(x, 16) for x in room['Objects']]
        self.actors = [convert_actor_data(x) for x in room['Actors']]

    def write_data(self, rom:LocalRom):

        # move file to remap address
        self.file.relocate(rom)

        headcur = self.file.start

        code = rom.read_byte(headcur)
        loop = 0x20
        while loop != 0 and code != 0x14: #terminator
            loop -= 1

            if code == 0x01: # actors
                offset = self.file.end - self.file.start
                write_actor_data(rom, self.file.end, self.actors)
                self.file.end += len(self.actors) * 0x10

                rom.write_byte(headcur + 1, len(self.actors))
                rom.write_int32(headcur + 4, get_segment_address(3, offset))

            elif code == 0x0B: # objects
                offset = self.append_object_data(rom, self.objects)

                rom.write_byte(headcur + 1, len(self.objects))
                rom.write_int32(headcur + 4, get_segment_address(3, offset))

            headcur += 8
            code = rom.read_byte(headcur)

        # update file reference
        self.file.end = align16(self.file.end)
        update_dmadata(rom, self.file)
        

    def append_object_data(self, rom:LocalRom, objects):
        offset = self.file.end - self.file.start
        cur = self.file.end
        rom.write_int16s(cur, objects)

        objects_size = align4(len(objects) * 2)
        self.file.end += objects_size
        return offset


def patch_files(world, rom:LocalRom):
    #patch_ice_cavern_scene_header(rom)

    data = get_json()
    scenes = [Scene(x) for x in data]

    if world.dungeon_mq['DT']:
        scenes[0].write_data(rom)
    if world.dungeon_mq['DC']:
        scenes[1].write_data(rom)

    verify_dma(rom)


def get_json():
    with open(local_path('data/mqu.json'), 'r') as stream:
        data = json.load(stream)
    return data


def convert_actor_data(str):
    spawn_args = str.split(" ")
    return [ int(x,16) for x in spawn_args ]


def get_segment_address(base, offset):
    offset &= 0xFFFFFF
    base *= 0x01000000
    return base + offset


def patch_ice_cavern_scene_header(rom):
    rom.buffer[0x2BEB000:0x2BEB038] = rom.buffer[0x2BEB008:0x2BEB040]
    rom.write_int32s(0x2BEB038, [0x0D000000, 0x02000000])


def get_dma_record(rom:LocalRom, cur):
    start = rom.read_int32(cur)
    end = rom.read_int32(cur+0x04)
    size = end-start
    return start, end, size


def verify_remap(scenes):
    def test_remap(file:File):
        if file.remap is not None:
            if file.start < file.remap:
                return False
        return True
    print("test code: verify remap won't corrupt data")

    for scene in scenes:
        file = scene.file
        result = test_remap(file)
        print("{0} - {1}".format(result, file))

        for room in scene.rooms:
            file = room.file
            result = test_remap(file)
            print("{0} - {1}".format(result, file))


def verify_dma(rom:LocalRom):
    cur = SCENE_DMADATA

    next_start = -1
    errors = []
    
    while True:
        this_start, this_end, this_size = get_dma_record(rom, cur)
        next_start, next_end, next_size = get_dma_record(rom, cur + 0x10)

        if next_start == 0:
            break

        if this_end > next_start:
            errors.append('dmadata info')
            st, e, si = get_dma_record(rom, cur-0x10)
            errors.append("{0:x} {1:x} {2:x}".format(st, e, si))
            st, e, si = get_dma_record(rom, cur)
            errors.append("{0:x} {1:x} {2:x} <-- overlapping record".format(st, e, si))
            st, e, si = get_dma_record(rom, cur+0x10)
            errors.append("{0:x} {1:x} {2:x}".format(st, e, si))
        next_start = this_start
        cur += 0x10

    if len(errors) > 0:
        for e in errors:
            print(e)
        Exception("overlapping dmadata records!")


def update_dmadata(rom:LocalRom, file:File):
    cur = SCENE_DMADATA

    key, start, end = file.dma_key, file.start, file.end

    record_key = rom.read_int32(cur)
    while record_key != 0 and record_key != key:
        cur += 0x10
        record_key = rom.read_int32(cur)

    if record_key == 0:
        raise Exception('dmadata update failed: key {0:x} not found in dmadata'.format(key))

    else:
        rom.write_int32s(cur, [start, end, start, 0])


def update_scene_table(rom:LocalRom, sceneId, start, end):
    cur = sceneId * 0x14 + SCENE_TABLE
    rom.write_int32s(cur, [start, end])


def write_actor_data(rom:LocalRom, cur, actors):
    for actor in actors:
        rom.write_int16s(cur, actor)
        cur += 0x10

def align4(value):
    return ((value + 3) // 4) * 4

def align16(value):
    return ((value + 0xF) // 0x10) * 0x10