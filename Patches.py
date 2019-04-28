import random
import struct
import itertools
import re

from World import World
from Rom import Rom
from Spoiler import Spoiler
from LocationList import business_scrubs
from Hints import writeGossipStoneHints, buildBossRewardHints, \
        buildGanonText, getSimpleHintNoPrefix
from Utils import data_path
from Messages import read_messages, update_message_by_id, read_shop_items, \
        write_shop_items, remove_unused_messages, make_player_message, \
        add_item_messages, repack_messages, shuffle_messages, \
        get_message_by_id
from OcarinaSongs import replace_songs
from MQ import patch_files, File, update_dmadata, insert_space, add_relocations
from SaveContext import SaveContext
from Navi_Hints import Navi_Hints

def patch_rom(spoiler:Spoiler, world:World, rom:Rom, outfilebase):
    with open(data_path('generated/rom_patch.txt'), 'r') as stream:
        for line in stream:
            address, value = [int(x, 16) for x in line.split(',')]
            rom.write_int32(address, value)
    rom.scan_dmadata_update()

    # Write Randomizer title screen logo
    with open(data_path('title.bin'), 'rb') as stream:
        titleBytes = stream.read()
        rom.write_bytes(0x01795300, titleBytes)

    # Fixes the typo of keatan mask in the item select screen
    with open(data_path('keaton.bin'), 'rb') as stream:
        keatonBytes = stream.read()
        rom.write_bytes(0x8A7C00, keatonBytes)

    # Force language to be English in the event a Japanese rom was submitted
    rom.write_byte(0x3E, 0x45)
    rom.force_patch.append(0x3E)

    # Increase the instance size of Bombchus prevent the heap from becoming corrupt when
    # a Dodongo eats a Bombchu. Does not fix stale pointer issues with the animation
    rom.write_int32(0xD6002C, 0x1F0)

    # Can always return to youth
    rom.write_byte(0xCB6844, 0x35)
    rom.write_byte(0x253C0E2, 0x03) # Moves sheik from pedestal

    # Fix Ice Cavern Alcove Camera
    if not world.dungeon_mq['Ice Cavern']:
        rom.write_byte(0x2BECA25,0x01);
        rom.write_byte(0x2BECA2D,0x01);

    # Fix GS rewards to be static
    rom.write_int32(0xEA3934, 0)
    rom.write_bytes(0xEA3940, [0x10, 0x00])

    # Fix horseback archery rewards to be static
    rom.write_byte(0xE12BA5, 0x00)
    rom.write_byte(0xE12ADD, 0x00)

    # Fix deku theater rewards to be static
    rom.write_bytes(0xEC9A7C, [0x00, 0x00, 0x00, 0x00]) #Sticks
    rom.write_byte(0xEC9CD5, 0x00) #Nuts

    # Fix deku scrub who sells stick upgrade
    rom.write_bytes(0xDF8060, [0x00, 0x00, 0x00, 0x00])

    # Fix deku scrub who sells nut upgrade
    rom.write_bytes(0xDF80D4, [0x00, 0x00, 0x00, 0x00])

    # Fix rolling goron as child reward to be static
    rom.write_bytes(0xED2960, [0x00, 0x00, 0x00, 0x00])

    # Fix proximity text boxes (Navi) (Part 1)
    rom.write_bytes(0xDF8B84, [0x00, 0x00, 0x00, 0x00])

    # Fix final magic bean to cost 99
    rom.write_byte(0xE20A0F, 0x63)
    rom.write_bytes(0x94FCDD, [0x08, 0x39, 0x39])

    # Remove locked door to Boss Key Chest in Fire Temple
    if not world.keysanity and not world.dungeon_mq['Fire Temple']:
        rom.write_byte(0x22D82B7, 0x3F)
    # Remove the unused locked door in water temple
    if not world.dungeon_mq['Water Temple']:
        rom.write_byte(0x25B8197, 0x3F)

    if world.bombchus_in_logic:
        rom.write_int32(rom.sym('BOMBCHUS_IN_LOGIC'), 1)

    # Change graveyard graves to not allow grabbing on to the ledge
    rom.write_byte(0x0202039D, 0x20)
    rom.write_byte(0x0202043C, 0x24)


    # Fix Castle Courtyard to check for meeting Zelda, not Zelda fleeing, to block you
    rom.write_bytes(0xCD5E76, [0x0E, 0xDC])
    rom.write_bytes(0xCD5E12, [0x0E, 0xDC])

    # Cutscene for all medallions never triggers when leaving shadow or spirit temples(hopefully stops warp to colossus on shadow completion with boss reward shuffle)
    rom.write_byte(0xACA409, 0xAD)
    rom.write_byte(0xACA49D, 0xCE)

    # Speed Zelda's Letter scene
    rom.write_bytes(0x290E08E, [0x05, 0xF0])
    rom.write_byte(0xEFCBA7, 0x08)
    rom.write_byte(0xEFE7C7, 0x05)
    #rom.write_byte(0xEFEAF7, 0x08)
    #rom.write_byte(0xEFE7C7, 0x05)
    rom.write_bytes(0xEFE938, [0x00, 0x00, 0x00, 0x00])
    rom.write_bytes(0xEFE948, [0x00, 0x00, 0x00, 0x00])
    rom.write_bytes(0xEFE950, [0x00, 0x00, 0x00, 0x00])

    # Speed Zelda escaping from Hyrule Castle
    Block_code = [0x00, 0x00, 0x00, 0x01, 0x00, 0x21, 0x00, 0x01, 0x00, 0x02, 0x00, 0x02]
    rom.write_bytes(0x1FC0CF8, Block_code)

    # songs as items flag
    songs_as_items = world.shuffle_song_items or world.start_with_fast_travel

    # Speed learning Zelda's Lullaby
    rom.write_int32s(0x02E8E90C, [0x000003E8, 0x00000001]) # Terminator Execution
    if songs_as_items:
        rom.write_int16s(None, [0x0073, 0x001, 0x0002, 0x0002]) # ID, start, end, end
    else:
        rom.write_int16s(None, [0x0073, 0x003B, 0x003C, 0x003C]) # ID, start, end, end


    rom.write_int32s(0x02E8E91C, [0x00000013, 0x0000000C]) # Textbox, Count
    if songs_as_items:
        rom.write_int16s(None, [0xFFFF, 0x0000, 0x0010, 0xFFFF, 0xFFFF, 0xFFFF]) # ID, start, end, type, alt1, alt2
    else:
        rom.write_int16s(None, [0x0017, 0x0000, 0x0010, 0x0002, 0x088B, 0xFFFF]) # ID, start, end, type, alt1, alt2
    rom.write_int16s(None, [0x00D4, 0x0011, 0x0020, 0x0000, 0xFFFF, 0xFFFF]) # ID, start, end, type, alt1, alt2

    # Speed learning Sun's Song
    if songs_as_items:
        rom.write_int32(0x0332A4A4, 0xFFFFFFFF) # Header: frame_count
    else:
        rom.write_int32(0x0332A4A4, 0x0000003C) # Header: frame_count

    rom.write_int32s(0x0332A868, [0x00000013, 0x00000008]) # Textbox, Count
    rom.write_int16s(None, [0x0018, 0x0000, 0x0010, 0x0002, 0x088B, 0xFFFF]) # ID, start, end, type, alt1, alt2
    rom.write_int16s(None, [0x00D3, 0x0011, 0x0020, 0x0000, 0xFFFF, 0xFFFF]) # ID, start, end, type, alt1, alt2

    # Speed learning Saria's Song
    if songs_as_items:
        rom.write_int32(0x020B1734, 0xFFFFFFFF) # Header: frame_count
    else:
        rom.write_int32(0x020B1734, 0x0000003C) # Header: frame_count

    rom.write_int32s(0x20B1DA8, [0x00000013, 0x0000000C]) # Textbox, Count
    rom.write_int16s(None, [0x0015, 0x0000, 0x0010, 0x0002, 0x088B, 0xFFFF]) # ID, start, end, type, alt1, alt2
    rom.write_int16s(None, [0x00D1, 0x0011, 0x0020, 0x0000, 0xFFFF, 0xFFFF]) # ID, start, end, type, alt1, alt2

    rom.write_int32s(0x020B19C0, [0x0000000A, 0x00000006]) # Link, Count
    rom.write_int16s(0x020B19C8, [0x0011, 0x0000, 0x0010, 0x0000]) #action, start, end, ????
    rom.write_int16s(0x020B19F8, [0x003E, 0x0011, 0x0020, 0x0000]) #action, start, end, ????
    rom.write_int32s(None,         [0x80000000,                          # ???
                                     0x00000000, 0x000001D4, 0xFFFFF731,  # start_XYZ
                                     0x00000000, 0x000001D4, 0xFFFFF712]) # end_XYZ

    # Speed learning Epona's Song
    rom.write_int32s(0x029BEF60, [0x000003E8, 0x00000001]) # Terminator Execution
    if songs_as_items:
        rom.write_int16s(None, [0x005E, 0x0001, 0x0002, 0x0002]) # ID, start, end, end
    else:
        rom.write_int16s(None, [0x005E, 0x000A, 0x000B, 0x000B]) # ID, start, end, end

    rom.write_int32s(0x029BECB0, [0x00000013, 0x00000002]) # Textbox, Count
    if songs_as_items:
        rom.write_int16s(None, [0xFFFF, 0x0000, 0x0009, 0xFFFF, 0xFFFF, 0xFFFF]) # ID, start, end, type, alt1, alt2
    else:
        rom.write_int16s(None, [0x00D2, 0x0000, 0x0009, 0x0000, 0xFFFF, 0xFFFF]) # ID, start, end, type, alt1, alt2
    rom.write_int16s(None, [0xFFFF, 0x000A, 0x003C, 0xFFFF, 0xFFFF, 0xFFFF]) # ID, start, end, type, alt1, alt2

    # Speed learning Song of Time
    rom.write_int32s(0x0252FB98, [0x000003E8, 0x00000001]) # Terminator Execution
    if songs_as_items:
        rom.write_int16s(None, [0x0035, 0x0001, 0x0002, 0x0002]) # ID, start, end, end
    else:
        rom.write_int16s(None, [0x0035, 0x003B, 0x003C, 0x003C]) # ID, start, end, end

    rom.write_int32s(0x0252FC80, [0x00000013, 0x0000000C]) # Textbox, Count
    if songs_as_items:
        rom.write_int16s(None, [0xFFFF, 0x0000, 0x0010, 0xFFFF, 0xFFFF, 0xFFFF]) # ID, start, end, type, alt1, alt2
    else:
        rom.write_int16s(None, [0x0019, 0x0000, 0x0010, 0x0002, 0x088B, 0xFFFF]) # ID, start, end, type, alt1, alt2
    rom.write_int16s(None, [0x00D5, 0x0011, 0x0020, 0x0000, 0xFFFF, 0xFFFF]) # ID, start, end, type, alt1, alt2

    rom.write_int32(0x01FC3B84, 0xFFFFFFFF) # Other Header?: frame_count

    # Speed learning Song of Storms
    if songs_as_items:
        rom.write_int32(0x03041084, 0xFFFFFFFF) # Header: frame_count
    else:
        rom.write_int32(0x03041084, 0x0000000A) # Header: frame_count

    rom.write_int32s(0x03041088, [0x00000013, 0x00000002]) # Textbox, Count
    rom.write_int16s(None, [0x00D6, 0x0000, 0x0009, 0x0000, 0xFFFF, 0xFFFF]) # ID, start, end, type, alt1, alt2
    rom.write_int16s(None, [0xFFFF, 0x00BE, 0x00C8, 0xFFFF, 0xFFFF, 0xFFFF]) # ID, start, end, type, alt1, alt2

    # Speed learning Minuet of Forest
    if songs_as_items:
        rom.write_int32(0x020AFF84, 0xFFFFFFFF) # Header: frame_count
    else:
        rom.write_int32(0x020AFF84, 0x0000003C) # Header: frame_count

    rom.write_int32s(0x020B0800, [0x00000013, 0x0000000A]) # Textbox, Count
    rom.write_int16s(None, [0x000F, 0x0000, 0x0010, 0x0002, 0x088B, 0xFFFF]) # ID, start, end, type, alt1, alt2
    rom.write_int16s(None, [0x0073, 0x0011, 0x0020, 0x0000, 0xFFFF, 0xFFFF]) # ID, start, end, type, alt1, alt2

    rom.write_int32s(0x020AFF88, [0x0000000A, 0x00000005]) # Link, Count
    rom.write_int16s(0x020AFF90, [0x0011, 0x0000, 0x0010, 0x0000]) #action, start, end, ????
    rom.write_int16s(0x020AFFC1, [0x003E, 0x0011, 0x0020, 0x0000]) #action, start, end, ????

    rom.write_int32s(0x020B0488, [0x00000056, 0x00000001]) # Music Change, Count
    rom.write_int16s(None, [0x003F, 0x0021, 0x0022, 0x0000]) #action, start, end, ????

    rom.write_int32s(0x020B04C0, [0x0000007C, 0x00000001]) # Music Fade Out, Count
    rom.write_int16s(None, [0x0004, 0x0000, 0x0000, 0x0000]) #action, start, end, ????

    # Speed learning Bolero of Fire
    if songs_as_items:
        rom.write_int32(0x0224B5D4, 0xFFFFFFFF) # Header: frame_count
    else:
        rom.write_int32(0x0224B5D4, 0x0000003C) # Header: frame_count

    rom.write_int32s(0x0224D7E8, [0x00000013, 0x0000000A]) # Textbox, Count
    rom.write_int16s(None, [0x0010, 0x0000, 0x0010, 0x0002, 0x088B, 0xFFFF]) # ID, start, end, type, alt1, alt2
    rom.write_int16s(None, [0x0074, 0x0011, 0x0020, 0x0000, 0xFFFF, 0xFFFF]) # ID, start, end, type, alt1, alt2

    rom.write_int32s(0x0224B5D8, [0x0000000A, 0x0000000B]) # Link, Count
    rom.write_int16s(0x0224B5E0, [0x0011, 0x0000, 0x0010, 0x0000]) #action, start, end, ????
    rom.write_int16s(0x0224B610, [0x003E, 0x0011, 0x0020, 0x0000]) #action, start, end, ????

    rom.write_int32s(0x0224B7F0, [0x0000002F, 0x0000000E]) # Sheik, Count
    rom.write_int16s(0x0224B7F8, [0x0000]) #action
    rom.write_int16s(0x0224B828, [0x0000]) #action
    rom.write_int16s(0x0224B858, [0x0000]) #action
    rom.write_int16s(0x0224B888, [0x0000]) #action

    # Speed learning Serenade of Water
    if songs_as_items:
        rom.write_int32(0x02BEB254, 0xFFFFFFFF) # Header: frame_count
    else:
        rom.write_int32(0x02BEB254, 0x0000003C) # Header: frame_count

    rom.write_int32s(0x02BEC880, [0x00000013, 0x00000010]) # Textbox, Count
    rom.write_int16s(None, [0x0011, 0x0000, 0x0010, 0x0002, 0x088B, 0xFFFF]) # ID, start, end, type, alt1, alt2
    rom.write_int16s(None, [0x0075, 0x0011, 0x0020, 0x0000, 0xFFFF, 0xFFFF]) # ID, start, end, type, alt1, alt2

    rom.write_int32s(0x02BEB258, [0x0000000A, 0x0000000F]) # Link, Count
    rom.write_int16s(0x02BEB260, [0x0011, 0x0000, 0x0010, 0x0000]) #action, start, end, ????
    rom.write_int16s(0x02BEB290, [0x003E, 0x0011, 0x0020, 0x0000]) #action, start, end, ????

    rom.write_int32s(0x02BEB530, [0x0000002F, 0x00000006]) # Sheik, Count
    rom.write_int16s(0x02BEB538, [0x0000, 0x0000, 0x018A, 0x0000]) #action, start, end, ????
    rom.write_int32s(None,         [0x1BBB0000,                          # ???
                                     0xFFFFFB10, 0x8000011A, 0x00000330,  # start_XYZ
                                     0xFFFFFB10, 0x8000011A, 0x00000330]) # end_XYZ

    rom.write_int32s(0x02BEC848, [0x00000056, 0x00000001]) # Music Change, Count
    rom.write_int16s(None, [0x0059, 0x0021, 0x0022, 0x0000]) #action, start, end, ????

    # Speed learning Nocturne of Shadow
    rom.write_int32s(0x01FFE458, [0x000003E8, 0x00000001]) # Other Scene? Terminator Execution
    rom.write_int16s(None, [0x002F, 0x0001, 0x0002, 0x0002]) # ID, start, end, end

    rom.write_int32(0x01FFFDF4, 0x0000003C) # Header: frame_count

    rom.write_int32s(0x02000FD8, [0x00000013, 0x0000000E]) # Textbox, Count
    if songs_as_items:
        rom.write_int16s(None, [0xFFFF, 0x0000, 0x0010, 0xFFFF, 0xFFFF, 0xFFFF]) # ID, start, end, type, alt1, alt2
    else:
        rom.write_int16s(None, [0x0013, 0x0000, 0x0010, 0x0002, 0x088B, 0xFFFF]) # ID, start, end, type, alt1, alt2
    rom.write_int16s(None, [0x0077, 0x0011, 0x0020, 0x0000, 0xFFFF, 0xFFFF]) # ID, start, end, type, alt1, alt2

    rom.write_int32s(0x02000128, [0x000003E8, 0x00000001]) # Terminator Execution
    if songs_as_items:
        rom.write_int16s(None, [0x0032, 0x0001, 0x0002, 0x0002]) # ID, start, end, end
    else:
        rom.write_int16s(None, [0x0032, 0x003A, 0x003B, 0x003B]) # ID, start, end, end

    # Speed learning Requiem of Spirit
    rom.write_int32(0x0218AF14, 0x0000003C) # Header: frame_count

    rom.write_int32s(0x0218C574, [0x00000013, 0x00000008]) # Textbox, Count
    if songs_as_items:
        rom.write_int16s(None, [0xFFFF, 0x0000, 0x0010, 0xFFFF, 0xFFFF, 0xFFFF]) # ID, start, end, type, alt1, alt2
    else:
        rom.write_int16s(None, [0x0012, 0x0000, 0x0010, 0x0002, 0x088B, 0xFFFF]) # ID, start, end, type, alt1, alt2
    rom.write_int16s(None, [0x0076, 0x0011, 0x0020, 0x0000, 0xFFFF, 0xFFFF]) # ID, start, end, type, alt1, alt2

    rom.write_int32s(0x0218B478, [0x000003E8, 0x00000001]) # Terminator Execution
    if songs_as_items:
        rom.write_int16s(None, [0x0030, 0x0001, 0x0002, 0x0002]) # ID, start, end, end
    else:
        rom.write_int16s(None, [0x0030, 0x003A, 0x003B, 0x003B]) # ID, start, end, end

    rom.write_int32s(0x0218AF18, [0x0000000A, 0x0000000B]) # Link, Count
    rom.write_int16s(0x0218AF20, [0x0011, 0x0000, 0x0010, 0x0000]) #action, start, end, ????
    rom.write_int32s(None,         [0x40000000,                          # ???
                                     0xFFFFFAF9, 0x00000008, 0x00000001,  # start_XYZ
                                     0xFFFFFAF9, 0x00000008, 0x00000001,  # end_XYZ
                                     0x0F671408, 0x00000000, 0x00000001]) # normal_XYZ
    rom.write_int16s(0x0218AF50, [0x003E, 0x0011, 0x0020, 0x0000]) #action, start, end, ????

    # Speed learning Prelude of Light
    if songs_as_items:
        rom.write_int32(0x0252FD24, 0xFFFFFFFF) # Header: frame_count
    else:
        rom.write_int32(0x0252FD24, 0x0000003C) # Header: frame_count

    rom.write_int32s(0x02531320, [0x00000013, 0x0000000E]) # Textbox, Count
    rom.write_int16s(None, [0x0014, 0x0000, 0x0010, 0x0002, 0x088B, 0xFFFF]) # ID, start, end, type, alt1, alt2
    rom.write_int16s(None, [0x0078, 0x0011, 0x0020, 0x0000, 0xFFFF, 0xFFFF]) # ID, start, end, type, alt1, alt2

    rom.write_int32s(0x0252FF10, [0x0000002F, 0x00000009]) # Sheik, Count
    rom.write_int16s(0x0252FF18, [0x0006, 0x0000, 0x0000, 0x0000]) #action, start, end, ????

    rom.write_int32s(0x025313D0, [0x00000056, 0x00000001]) # Music Change, Count
    rom.write_int16s(None, [0x003B, 0x0021, 0x0022, 0x0000]) #action, start, end, ????

    # Speed scene after Deku Tree
    rom.write_bytes(0x2077E20, [0x00, 0x07, 0x00, 0x01, 0x00, 0x02, 0x00, 0x02])
    rom.write_bytes(0x2078A10, [0x00, 0x0E, 0x00, 0x1F, 0x00, 0x20, 0x00, 0x20])
    Block_code = [0x00, 0x80, 0x00, 0x00, 0x00, 0x1E, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF,
                  0xFF, 0xFF, 0x00, 0x1E, 0x00, 0x28, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    rom.write_bytes(0x2079570, Block_code)

    # Speed scene after Dodongo's Cavern
    rom.write_bytes(0x2221E88, [0x00, 0x0C, 0x00, 0x3B, 0x00, 0x3C, 0x00, 0x3C])
    rom.write_bytes(0x2223308, [0x00, 0x81, 0x00, 0x00, 0x00, 0x3A, 0x00, 0x00])

    # Speed scene after Jabu Jabu's Belly
    rom.write_bytes(0xCA3530, [0x00, 0x00, 0x00, 0x00])
    rom.write_bytes(0x2113340, [0x00, 0x0D, 0x00, 0x3B, 0x00, 0x3C, 0x00, 0x3C])
    rom.write_bytes(0x2113C18, [0x00, 0x82, 0x00, 0x00, 0x00, 0x3A, 0x00, 0x00])
    rom.write_bytes(0x21131D0, [0x00, 0x01, 0x00, 0x00, 0x00, 0x3C, 0x00, 0x3C])

    # Speed scene after Forest Temple
    rom.write_bytes(0xD4ED68, [0x00, 0x45, 0x00, 0x3B, 0x00, 0x3C, 0x00, 0x3C])
    rom.write_bytes(0xD4ED78, [0x00, 0x3E, 0x00, 0x00, 0x00, 0x3A, 0x00, 0x00])
    rom.write_bytes(0x207B9D4, [0xFF, 0xFF, 0xFF, 0xFF])

    # Speed scene after Fire Temple
    rom.write_bytes(0x2001848, [0x00, 0x1E, 0x00, 0x01, 0x00, 0x02, 0x00, 0x02])
    rom.write_bytes(0xD100B4, [0x00, 0x62, 0x00, 0x3B, 0x00, 0x3C, 0x00, 0x3C])
    rom.write_bytes(0xD10134, [0x00, 0x3C, 0x00, 0x00, 0x00, 0x3A, 0x00, 0x00])

    # Speed scene after Water Temple
    rom.write_bytes(0xD5A458, [0x00, 0x15, 0x00, 0x3B, 0x00, 0x3C, 0x00, 0x3C])
    rom.write_bytes(0xD5A3A8, [0x00, 0x3D, 0x00, 0x00, 0x00, 0x3A, 0x00, 0x00])
    rom.write_bytes(0x20D0D20, [0x00, 0x29, 0x00, 0xC7, 0x00, 0xC8, 0x00, 0xC8])

    # Speed scene after Shadow Temple
    rom.write_bytes(0xD13EC8, [0x00, 0x61, 0x00, 0x3B, 0x00, 0x3C, 0x00, 0x3C])
    rom.write_bytes(0xD13E18, [0x00, 0x41, 0x00, 0x00, 0x00, 0x3A, 0x00, 0x00])

    # Speed scene after Spirit Temple
    rom.write_bytes(0xD3A0A8, [0x00, 0x60, 0x00, 0x3B, 0x00, 0x3C, 0x00, 0x3C])
    rom.write_bytes(0xD39FF0, [0x00, 0x3F, 0x00, 0x00, 0x00, 0x3A, 0x00, 0x00])

    # Speed Nabooru defeat scene
    rom.write_bytes(0x2F5AF84, [0x00, 0x00, 0x00, 0x05])
    rom.write_bytes(0x2F5C7DA, [0x00, 0x01, 0x00, 0x02])
    rom.write_bytes(0x2F5C7A2, [0x00, 0x03, 0x00, 0x04])
    rom.write_byte(0x2F5B369, 0x09)
    rom.write_byte(0x2F5B491, 0x04)
    rom.write_byte(0x2F5B559, 0x04)
    rom.write_byte(0x2F5B621, 0x04)
    rom.write_byte(0x2F5B761, 0x07)

    # Speed scene with all medallions
    rom.write_bytes(0x2512680, [0x00, 0x74, 0x00, 0x01, 0x00, 0x02, 0x00, 0x02])

    # Speed collapse of Ganon's Tower
    rom.write_bytes(0x33FB328, [0x00, 0x76, 0x00, 0x01, 0x00, 0x02, 0x00, 0x02])

    # Speed Phantom Ganon defeat scene
    rom.write_bytes(0xC944D8, [0x00, 0x00, 0x00, 0x00])
    rom.write_bytes(0xC94548, [0x00, 0x00, 0x00, 0x00])
    rom.write_bytes(0xC94730, [0x00, 0x00, 0x00, 0x00])
    rom.write_bytes(0xC945A8, [0x00, 0x00, 0x00, 0x00])
    rom.write_bytes(0xC94594, [0x00, 0x00, 0x00, 0x00])

    # Speed Twinrova defeat scene
    rom.write_bytes(0xD678CC, [0x24, 0x01, 0x03, 0xA2, 0xA6, 0x01, 0x01, 0x42])
    rom.write_bytes(0xD67BA4, [0x10, 0x00])

    # Speed scenes during final battle
    # Ganondorf battle end
    rom.write_byte(0xD82047, 0x09)
    # Zelda descends
    rom.write_byte(0xD82AB3, 0x66)
    rom.write_byte(0xD82FAF, 0x65)
    rom.write_int16s(0xD82D2E, [0x041F])
    rom.write_int16s(0xD83142, [0x006B])
    rom.write_bytes(0xD82DD8, [0x00, 0x00, 0x00, 0x00])
    rom.write_bytes(0xD82ED4, [0x00, 0x00, 0x00, 0x00])
    rom.write_byte(0xD82FDF, 0x33)
    # After tower collapse
    rom.write_byte(0xE82E0F, 0x04)
    # Ganon intro
    rom.write_bytes(0xE83D28, [0x00, 0x00, 0x00, 0x00])
    rom.write_bytes(0xE83B5C, [0x00, 0x00, 0x00, 0x00])
    rom.write_bytes(0xE84C80, [0x10, 0x00])

    # Speed completion of the trials in Ganon's Castle
    rom.write_int16s(0x31A8090, [0x006B, 0x0001, 0x0002, 0x0002]) #Forest
    rom.write_int16s(0x31A9E00, [0x006E, 0x0001, 0x0002, 0x0002]) #Fire
    rom.write_int16s(0x31A8B18, [0x006C, 0x0001, 0x0002, 0x0002]) #Water
    rom.write_int16s(0x31A9430, [0x006D, 0x0001, 0x0002, 0x0002]) #Shadow
    rom.write_int16s(0x31AB200, [0x0070, 0x0001, 0x0002, 0x0002]) #Spirit
    rom.write_int16s(0x31AA830, [0x006F, 0x0001, 0x0002, 0x0002]) #Light

    # Speed obtaining Fairy Ocarina
    rom.write_bytes(0x2151230, [0x00, 0x72, 0x00, 0x3C, 0x00, 0x3D, 0x00, 0x3D])
    Block_code = [0x00, 0x4A, 0x00, 0x00, 0x00, 0x3A, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF,
                  0xFF, 0xFF, 0x00, 0x3C, 0x00, 0x81, 0xFF, 0xFF]
    rom.write_bytes(0x2151240, Block_code)
    rom.write_bytes(0x2150E20, [0xFF, 0xFF, 0xFA, 0x4C])

    if world.shuffle_ocarinas:
        symbol = rom.sym('OCARINAS_SHUFFLED')
        rom.write_byte(symbol,0x01)

    if world.child_lake_hylia_control:
        symbol = rom.sym('CFG_CHILD_CONTROL_LAKE')
        rom.write_byte(symbol,0x01)

    # Speed Zelda Light Arrow cutscene
    rom.write_bytes(0x2531B40, [0x00, 0x28, 0x00, 0x01, 0x00, 0x02, 0x00, 0x02])
    rom.write_bytes(0x2532FBC, [0x00, 0x75])
    rom.write_bytes(0x2532FEA, [0x00, 0x75, 0x00, 0x80])
    rom.write_byte(0x2533115, 0x05)
    rom.write_bytes(0x2533141, [0x06, 0x00, 0x06, 0x00, 0x10])
    rom.write_bytes(0x2533171, [0x0F, 0x00, 0x11, 0x00, 0x40])
    rom.write_bytes(0x25331A1, [0x07, 0x00, 0x41, 0x00, 0x65])
    rom.write_bytes(0x2533642, [0x00, 0x50])
    rom.write_byte(0x253389D, 0x74)
    rom.write_bytes(0x25338A4, [0x00, 0x72, 0x00, 0x75, 0x00, 0x79])
    rom.write_bytes(0x25338BC, [0xFF, 0xFF])
    rom.write_bytes(0x25338C2, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    rom.write_bytes(0x25339C2, [0x00, 0x75, 0x00, 0x76])
    rom.write_bytes(0x2533830, [0x00, 0x31, 0x00, 0x81, 0x00, 0x82, 0x00, 0x82])

    # Speed Bridge of Light cutscene
    rom.write_bytes(0x292D644, [0x00, 0x00, 0x00, 0xA0])
    rom.write_bytes(0x292D680, [0x00, 0x02, 0x00, 0x0A, 0x00, 0x6C, 0x00, 0x00])
    rom.write_bytes(0x292D6E8, [0x00, 0x27])
    rom.write_bytes(0x292D718, [0x00, 0x32])
    rom.write_bytes(0x292D810, [0x00, 0x02, 0x00, 0x3C])
    rom.write_bytes(0x292D924, [0xFF, 0xFF, 0x00, 0x14, 0x00, 0x96, 0xFF, 0xFF])

    #Speed Pushing of All Pushable Objects
    rom.write_bytes(0xDD2B86, [0x40, 0x80])             #block speed
    rom.write_bytes(0xDD2D26, [0x00, 0x01])             #block delay
    rom.write_bytes(0xDD9682, [0x40, 0x80])             #milk crate speed
    rom.write_bytes(0xDD981E, [0x00, 0x01])             #milk crate delay
    rom.write_bytes(0xCE1BD0, [0x40, 0x80, 0x00, 0x00]) #amy puzzle speed
    rom.write_bytes(0xCE0F0E, [0x00, 0x01])             #amy puzzle delay
    rom.write_bytes(0xC77CA8, [0x40, 0x80, 0x00, 0x00]) #fire block speed
    rom.write_bytes(0xC770C2, [0x00, 0x01])             #fire block delay
    rom.write_bytes(0xCC5DBC, [0x29, 0xE1, 0x00, 0x01]) #forest basement puzzle delay
    rom.write_bytes(0xDBCF70, [0x2B, 0x01, 0x00, 0x00]) #spirit cobra mirror startup
    rom.write_bytes(0xDBCF70, [0x2B, 0x01, 0x00, 0x01]) #spirit cobra mirror delay
    rom.write_bytes(0xDBA230, [0x28, 0x41, 0x00, 0x19]) #truth spinner speed
    rom.write_bytes(0xDBA3A4, [0x24, 0x18, 0x00, 0x00]) #truth spinner delay

    #Speed Deku Seed Upgrade Scrub Cutscene
    rom.write_bytes(0xECA900, [0x24, 0x03, 0xC0, 0x00]) #scrub angle
    rom.write_bytes(0xECAE90, [0x27, 0x18, 0xFD, 0x04]) #skip straight to giving item
    rom.write_bytes(0xECB618, [0x25, 0x6B, 0x00, 0xD4]) #skip straight to digging back in
    rom.write_bytes(0xECAE70, [0x00, 0x00, 0x00, 0x00]) #never initialize cs camera
    rom.write_bytes(0xE5972C, [0x24, 0x08, 0x00, 0x01]) #timer set to 1 frame for giving item

    # Remove remaining owls
    rom.write_bytes(0x1FE30CE, [0x01, 0x4B])
    rom.write_bytes(0x1FE30DE, [0x01, 0x4B])
    rom.write_bytes(0x1FE30EE, [0x01, 0x4B])
    rom.write_bytes(0x205909E, [0x00, 0x3F])
    rom.write_byte(0x2059094, 0x80)

    # Darunia won't dance
    rom.write_bytes(0x22769E4, [0xFF, 0xFF, 0xFF, 0xFF])

    # Zora moves quickly
    rom.write_bytes(0xE56924, [0x00, 0x00, 0x00, 0x00])

    # Speed Jabu Jabu swallowing Link
    rom.write_bytes(0xCA0784, [0x00, 0x18, 0x00, 0x01, 0x00, 0x02, 0x00, 0x02])

    # Ruto no longer points to Zora Sapphire
    rom.write_bytes(0xD03BAC, [0xFF, 0xFF, 0xFF, 0xFF])

    # Ruto never disappears from Jabu Jabu's Belly
    rom.write_byte(0xD01EA3, 0x00)

    #Shift octorock in jabu forward
    rom.write_bytes(0x275906E, [0xFF, 0xB3, 0xFB, 0x20, 0xF9, 0x56])

    #Move fire/forest temple switches down 1 unit to make it easier to press
    rom.write_bytes(0x24860A8, [0xFC, 0xF4]) #forest basement 1
    rom.write_bytes(0x24860C8, [0xFC, 0xF4]) #forest basement 2
    rom.write_bytes(0x24860E8, [0xFC, 0xF4]) #forest basement 3
    rom.write_bytes(0x236C148, [0x11, 0x93]) #fire hammer room

    # Speed up Epona race start
    rom.write_bytes(0x29BE984, [0x00, 0x00, 0x00, 0x02])
    rom.write_bytes(0x29BE9CA, [0x00, 0x01, 0x00, 0x02])

    # Speed start of Horseback Archery
    #rom.write_bytes(0x21B2064, [0x00, 0x00, 0x00, 0x02])
    #rom.write_bytes(0x21B20AA, [0x00, 0x01, 0x00, 0x02])

    # Speed up Epona escape
    rom.write_bytes(0x1FC8B36, [0x00, 0x2A])

    # Speed up draining the well
    rom.write_bytes(0xE0A010, [0x00, 0x2A, 0x00, 0x01, 0x00, 0x02, 0x00, 0x02])
    rom.write_bytes(0x2001110, [0x00, 0x2B, 0x00, 0xB7, 0x00, 0xB8, 0x00, 0xB8])

    # Speed up opening the royal tomb for both child and adult
    rom.write_bytes(0x2025026, [0x00, 0x01])
    rom.write_bytes(0x2023C86, [0x00, 0x01])
    rom.write_byte(0x2025159, 0x02)
    rom.write_byte(0x2023E19, 0x02)

    #Speed opening of Door of Time
    rom.write_bytes(0xE0A176, [0x00, 0x02])
    rom.write_bytes(0xE0A35A, [0x00, 0x01, 0x00, 0x02])

    # Poacher's Saw no longer messes up Deku Theater
    rom.write_bytes(0xAE72CC, [0x00, 0x00, 0x00, 0x00])

    # Change Prelude CS to check for medallion
    rom.write_bytes(0x00C805E6, [0x00, 0xA6])
    rom.write_bytes(0x00C805F2, [0x00, 0x01])

    # Change Nocturne CS to check for medallions
    rom.write_bytes(0x00ACCD8E, [0x00, 0xA6])
    rom.write_bytes(0x00ACCD92, [0x00, 0x01])
    rom.write_bytes(0x00ACCD9A, [0x00, 0x02])
    rom.write_bytes(0x00ACCDA2, [0x00, 0x04])

    # Change King Zora to move even if Zora Sapphire is in inventory
    rom.write_bytes(0x00E55BB0, [0x85, 0xCE, 0x8C, 0x3C])
    rom.write_bytes(0x00E55BB4, [0x84, 0x4F, 0x0E, 0xDA])

    # Remove extra Forest Temple medallions
    rom.write_bytes(0x00D4D37C, [0x00, 0x00, 0x00, 0x00])

    # Remove extra Fire Temple medallions
    rom.write_bytes(0x00AC9754, [0x00, 0x00, 0x00, 0x00])
    rom.write_bytes(0x00D0DB8C, [0x00, 0x00, 0x00, 0x00])

    # Remove extra Water Temple medallions
    rom.write_bytes(0x00D57F94, [0x00, 0x00, 0x00, 0x00])

    # Remove extra Spirit Temple medallions
    rom.write_bytes(0x00D370C4, [0x00, 0x00, 0x00, 0x00])
    rom.write_bytes(0x00D379C4, [0x00, 0x00, 0x00, 0x00])

    # Remove extra Shadow Temple medallions
    rom.write_bytes(0x00D116E0, [0x00, 0x00, 0x00, 0x00])

    # Change Mido, Saria, and Kokiri to check for Deku Tree complete flag
    # bitwise pointer for 0x80
    kokiriAddresses = [0xE52836, 0xE53A56, 0xE51D4E, 0xE51F3E, 0xE51D96, 0xE51E1E, 0xE51E7E, 0xE51EDE, 0xE51FC6, 0xE51F96, 0xE293B6, 0xE29B8E, 0xE62EDA, 0xE630D6, 0xE62642, 0xE633AA, 0xE6369E]
    for kokiri in kokiriAddresses:
        rom.write_bytes(kokiri, [0x8C, 0x0C])
    # Kokiri
    rom.write_bytes(0xE52838, [0x94, 0x48, 0x0E, 0xD4])
    rom.write_bytes(0xE53A58, [0x94, 0x49, 0x0E, 0xD4])
    rom.write_bytes(0xE51D50, [0x94, 0x58, 0x0E, 0xD4])
    rom.write_bytes(0xE51F40, [0x94, 0x4B, 0x0E, 0xD4])
    rom.write_bytes(0xE51D98, [0x94, 0x4B, 0x0E, 0xD4])
    rom.write_bytes(0xE51E20, [0x94, 0x4A, 0x0E, 0xD4])
    rom.write_bytes(0xE51E80, [0x94, 0x59, 0x0E, 0xD4])
    rom.write_bytes(0xE51EE0, [0x94, 0x4E, 0x0E, 0xD4])
    rom.write_bytes(0xE51FC8, [0x94, 0x49, 0x0E, 0xD4])
    rom.write_bytes(0xE51F98, [0x94, 0x58, 0x0E, 0xD4])
    # Saria
    rom.write_bytes(0xE293B8, [0x94, 0x78, 0x0E, 0xD4])
    rom.write_bytes(0xE29B90, [0x94, 0x68, 0x0E, 0xD4])
    # Mido
    rom.write_bytes(0xE62EDC, [0x94, 0x6F, 0x0E, 0xD4])
    rom.write_bytes(0xE630D8, [0x94, 0x4F, 0x0E, 0xD4])
    rom.write_bytes(0xE62644, [0x94, 0x6F, 0x0E, 0xD4])
    rom.write_bytes(0xE633AC, [0x94, 0x68, 0x0E, 0xD4])
    rom.write_bytes(0xE636A0, [0x94, 0x48, 0x0E, 0xD4])

    # Change adult Kokiri Forest to check for Forest Temple complete flag
    rom.write_bytes(0xE5369E, [0xB4, 0xAC])
    rom.write_bytes(0xD5A83C, [0x80, 0x49, 0x0E, 0xDC])

    # Change adult Goron City to check for Fire Temple complete flag
    rom.write_bytes(0xED59DC, [0x80, 0xC9, 0x0E, 0xDC])

    # Change Pokey to check DT complete flag
    rom.write_bytes(0xE5400A, [0x8C, 0x4C])
    rom.write_bytes(0xE5400E, [0xB4, 0xA4])
    if world.open_forest:
        rom.write_bytes(0xE5401C, [0x14, 0x0B])

    # Fix Shadow Temple to check for different rewards for scene
    rom.write_bytes(0xCA3F32, [0x00, 0x00, 0x25, 0x4A, 0x00, 0x10])

    # Fix Spirit Temple to check for different rewards for scene
    rom.write_bytes(0xCA3EA2, [0x00, 0x00, 0x25, 0x4A, 0x00, 0x08])

    # Fix Biggoron to check a different flag.
    rom.write_byte(0xED329B, 0x72)
    rom.write_byte(0xED43E7, 0x72)
    rom.write_bytes(0xED3370, [0x3C, 0x0D, 0x80, 0x12])
    rom.write_bytes(0xED3378, [0x91, 0xB8, 0xA6, 0x42, 0xA1, 0xA8, 0xA6, 0x42])
    rom.write_bytes(0xED6574, [0x00, 0x00, 0x00, 0x00])

    # Remove the check on the number of days that passed for claim check.
    rom.write_bytes(0xED4470, [0x00, 0x00, 0x00, 0x00])
    rom.write_bytes(0xED4498, [0x00, 0x00, 0x00, 0x00])

    # Fixed reward order for Bombchu Bowling
    rom.write_bytes(0xE2E698, [0x80, 0xAA, 0xE2, 0x64])
    rom.write_bytes(0xE2E6A0, [0x80, 0xAA, 0xE2, 0x4C])
    rom.write_bytes(0xE2D440, [0x24, 0x19, 0x00, 0x00])

    # Offset kakariko carpenter starting position
    rom.write_bytes(0x1FF93A4, [0x01, 0x8D, 0x00, 0x11, 0x01, 0x6C, 0xFF, 0x92, 0x00, 0x00, 0x01, 0x78, 0xFF, 0x2E, 0x00, 0x00, 0x00, 0x03, 0xFD, 0x2B, 0x00, 0xC8, 0xFF, 0xF9, 0xFD, 0x03, 0x00, 0xC8, 0xFF, 0xA9, 0xFD, 0x5D, 0x00, 0xC8, 0xFE, 0x5F]) # re order the carpenter's path
    rom.write_byte(0x1FF93D0, 0x06) # set the path points to 6
    rom.write_bytes(0x20160B6, [0x01, 0x8D, 0x00, 0x11, 0x01, 0x6C]) # set the carpenter's start position

    # Give hp after first ocarina minigame round
    rom.write_bytes(0xDF2204, [0x24, 0x03, 0x00, 0x02])

    # Allow owl to always carry the kid down Death Mountain
    rom.write_bytes(0xE304F0, [0x24, 0x0E, 0x00, 0x01])

    # Forbid Sun's Song from a bunch of cutscenes
    Suns_scenes = [0x2016FC9, 0x2017219, 0x20173D9, 0x20174C9, 0x2017679, 0x20C1539, 0x20C15D9, 0x21A0719, 0x21A07F9, 0x2E90129, 0x2E901B9, 0x2E90249, 0x225E829, 0x225E939, 0x306D009]
    for address in Suns_scenes:
        rom.write_byte(address,0x01)

    # Remove disruptive text from Gerudo Training Grounds and early Shadow Temple (vanilla)
    Wonder_text = [0x27C00BC, 0x27C00CC, 0x27C00DC, 0x27C00EC, 0x27C00FC, 0x27C010C, 0x27C011C, 0x27C012C, 0x27CE080,
                   0x27CE090, 0x2887070, 0x2887080, 0x2887090, 0x2897070, 0x28C7134, 0x28D91BC, 0x28A60F4, 0x28AE084,
                   0x28B9174, 0x28BF168, 0x28BF178, 0x28BF188, 0x28A1144, 0x28A6104, 0x28D0094]
    for address in Wonder_text:
        rom.write_byte(address, 0xFB)

    # Speed dig text for Dampe
    rom.write_bytes(0x9532F8, [0x08, 0x08, 0x08, 0x59])

    # Make item descriptions into a single box
    Short_item_descriptions = [0x92EC84, 0x92F9E3, 0x92F2B4, 0x92F37A, 0x92F513, 0x92F5C6, 0x92E93B, 0x92EA12]
    for address in Short_item_descriptions:
        rom.write_byte(address,0x02)

    et_original = rom.read_bytes(0xB6FBF0, 4 * 0x0614)

    entrance_updates = []

    def write_entrance(target_index, data_index, length=4):
        ti = target_index * 4
        rom.write_bytes(0xB6FBF0 + data_index * 4, et_original[ti:ti+(4*length)])

    def write_scene_exit(target_index, data_index, scene_start, scene_data):
        start_count = 0
        current = scene_data
        command = 0
        while command != 0x14:
            command = rom.read_byte(current)
            if command == 0x00:
                start_count = rom.read_byte(current + 1)
            current = current + 8
        command = 0
        current = scene_data
        while command != 0x14:
            command = rom.read_byte(current)
            if command == 0x13:
                entrance_list = scene_start + (rom.read_int32(current + 4) & 0x00FFFFFF)
                for _ in range (0, start_count):
                    entrance = rom.read_int16(entrance_list)
                    if (entrance == data_index):
                        entrance_updates.append((entrance_list, target_index))
                    entrance_list = entrance_list + 2
            if command == 0x18: # Alternate header list
                header_list = scene_start + (rom.read_int32(current + 4) & 0x00FFFFFF)
                for alt_id in range(0,3):
                    header_offset = rom.read_int32(header_list) & 0x00FFFFFF
                    if header_offset != 0:
                        write_scene_exit(target_index, data_index, scene_start, scene_start + header_offset)
                    header_list = header_list + 4
            current = current + 8

    def write_scenes_exits(target_index, data_index):
        scene_table = 0x00B71440
        for scene in range(0x00, 0x65):
            #really hacky
            if data_index == 0 and scene != 0x55:
                continue
            scene_start = rom.read_int32(scene_table + (scene * 0x14));
            write_scene_exit(target_index, data_index, scene_start, scene_start)

        #Special case: Jabu with the fish is entered from a cutscene hardcode
        if data_index == 0x0028:
            entrance_updates.append((0xAC95C2, target_index))

    def set_entrance_updates(entrances):
        for entrance in entrances:
            new_entrance = entrance.data
            replaced_entrance = entrance.replaces.data
            write_scenes_exits(replaced_entrance['index'], new_entrance['index'])

            if "dynamic_address" in new_entrance:
                # Dynamic exits are special and have to be set on a specific address
                rom.write_int16(new_entrance["dynamic_address"], replaced_entrance['index'])

            if "blue_warp" in new_entrance:
                if "blue_warp" in replaced_entrance:
                    blue_out_data =  replaced_entrance["blue_warp"]
                else:
                    blue_out_data = replaced_entrance["index"]
                # Blue warps have multiple hardcodes leading to them. The good news is
                # the blue warps (excluding deku sprout and lake fill special cases) each
                # have a nice consistent 4-entry in the table we can just shuffle. So just
                # catch all the hardcode with entrance table rewrite. This covers the
                # Forest temple and Water temple blue warp revisits. Deku sprout remains
                # vanilla as it never took you to the exit and the lake fill is handled
                # above by removing the cutscene completely. Child has problems with Adult
                # blue warps, so always use the return entrance if a child.
                write_entrance(blue_out_data + 2, new_entrance["blue_warp"] + 2, 2)
                write_entrance(replaced_entrance["index"], new_entrance["blue_warp"], 2)

    if world.shuffle_overworld_entrances:
        # Prevent the ocarina cutscene from leading straight to hyrule field
        symbol = rom.sym('OCARINAS_SHUFFLED')
        rom.write_byte(symbol, 1)

        # Patch all LLR exits by leaping over a fence to lead to the main LLR exit
        main_entrance = 0x01F9 # Hyrule Field entrance from Lon Lon Ranch (main land entrance)
        ranch_leap_entrances = [0x028A, 0x028E, 0x0292, 0x0476] # Southern, Western, Eastern, Front Gate
        for entrance_idx in ranch_leap_entrances:
            write_scenes_exits(main_entrance, entrance_idx)

        # Patch the water exits between Hyrule Field and Zora River to lead to the land entrance instead of the water entrance
        write_scenes_exits(0x00EA, 0x01D9) # Hyrule Field -> Zora River
        write_scenes_exits(0x0181, 0x0311) # Zora River -> Hyrule Field

        for entrance, target in entrance_updates:
            rom.write_int16(entrance, target)
        entrance_updates = []

        # Change Impa escort to bring link at the hyrule castle grounds entrance from market, instead of hyrule field
        write_entrance(0x0138, 0x0594) # After Impa escort (overridden to Hyrule Castle entrance from Market)

        # Change Getting caught cutscene as adult without hookshot to keep Link inside the Fortress
        write_entrance(0x0129, 0x01A5 + 2, 2) # Thrown out of fortress as adult (overridden to Gerudo Fortress entrance from Valley)

        # Change Getting caught cutscene as child to always throw Link in the stream
        write_entrance(0x01A5, 0x03B4, 2) # Captured with hookshot 1st time as child (overridden to Thrown out of fortress)
        write_entrance(0x01A5, 0x05F8, 2) # Captured with hookshot 2nd time as child (overridden to Thrown out of fortress)

        # Patch Owl Drop entrances to their new indexes
        for entrance in world.get_shuffled_entrances(type='OwlDrop'):
            write_entrance(entrance.replaces.data['index'], entrance.data['index'])

        set_entrance_updates(world.get_shuffled_entrances(type='Overworld'))

    if world.shuffle_dungeon_entrances:
        symbol = rom.sym('CFG_CHILD_CONTROL_LAKE')
        rom.write_int32(symbol, 1)

        # Connect lake hylia fill exit to revisit exit (Hylia blue will then be rewired below)
        rom.write_int16(0xAC995A, 0x060C)

        # Remove deku sprout and drop player at SFM after forest (SFM blue will then be rewired by ER below)
        rom.write_int16(0xAC9F96, 0x0608)

        #Tell the well water we are always a child.
        rom.write_int32(0xDD5BF4, 0x00000000)

        #Make the Adult well blocking stone dissappear if the well has been drained by
        #checking the well drain event flag instead of links age. This actor doesn't need a
        #code check for links age as the stone is absent for child via the scene alternate
        #lists. So replace the age logic with drain logic.
        rom.write_int32(0xE2887C, rom.read_int32(0xE28870)) #relocate this to nop delay slot
        rom.write_int32(0xE2886C, 0x95CEB4B0) # lhu
        rom.write_int32(0xE28870, 0x31CE0080) # andi

        remove_entrance_blockers(rom)
        #Tell the Deku tree jaw actor we are always a child.
        rom.write_int32(0x0C72C64, 0x240E0000)
        rom.write_int32(0x0C72C74, 0x240F0001)

        set_entrance_updates(world.get_shuffled_entrances(type='Dungeon'))

    if world.shuffle_interior_entrances:
        # Disable trade quest timers
        rom.write_byte(rom.sym('DISABLE_TIMERS'), 0x01)

        set_entrance_updates(world.get_shuffled_entrances(type='Interior'))

    if world.shuffle_special_interior_entrances:
        set_entrance_updates(world.get_shuffled_entrances(type='SpecialInterior'))

    for entrance, target in entrance_updates:
        rom.write_int16(entrance, target)

    # Fix text for Pocket Cucco.
    rom.write_byte(0xBEEF45, 0x0B)
        
    # Fix stupid alcove cameras in Ice Cavern -- thanks to krim and mzx for the help
    rom.write_byte(0x2BECA25,0x01);
    rom.write_byte(0x2BECA2D,0x01); 

    configure_dungeon_info(rom, world)

    hash_icons = 0
    for i,icon in enumerate(spoiler.file_hash):
        hash_icons |= (icon << (5 * i))
    rom.write_int32(rom.sym('cfg_file_select_hash'), hash_icons)

    save_context = SaveContext()

    # Initial Save Data

    save_context.write_bits(0x00D4 + 0x03 * 0x1C + 0x04 + 0x0, 0x08) # Forest Temple switch flag (Poe Sisters cutscene)
    save_context.write_bits(0x00D4 + 0x05 * 0x1C + 0x04 + 0x1, 0x01) # Water temple switch flag (Ruto)
    save_context.write_bits(0x00D4 + 0x51 * 0x1C + 0x04 + 0x2, 0x08) # Hyrule Field switch flag (Owl)
    save_context.write_bits(0x00D4 + 0x55 * 0x1C + 0x04 + 0x0, 0x80) # Kokiri Forest switch flag (Owl)
    save_context.write_bits(0x00D4 + 0x56 * 0x1C + 0x04 + 0x2, 0x40) # Sacred Forest Meadow switch flag (Owl)
    save_context.write_bits(0x00D4 + 0x5B * 0x1C + 0x04 + 0x2, 0x01) # Lost Woods switch flag (Owl)
    save_context.write_bits(0x00D4 + 0x5B * 0x1C + 0x04 + 0x3, 0x80) # Lost Woods switch flag (Owl)
    save_context.write_bits(0x00D4 + 0x5C * 0x1C + 0x04 + 0x0, 0x80) # Desert Colossus switch flag (Owl)
    save_context.write_bits(0x00D4 + 0x5F * 0x1C + 0x04 + 0x3, 0x20) # Hyrule Castle switch flag (Owl)

    save_context.write_bits(0x0ED4, 0x10) # "Met Deku Tree"
    save_context.write_bits(0x0ED5, 0x20) # "Deku Tree Opened Mouth"
    save_context.write_bits(0x0ED6, 0x08) # "Rented Horse From Ingo"
    save_context.write_bits(0x0EDA, 0x08) # "Began Nabooru Battle"
    save_context.write_bits(0x0EDC, 0x80) # "Entered the Master Sword Chamber"
    save_context.write_bits(0x0EDD, 0x20) # "Pulled Master Sword from Pedestal"
    save_context.write_bits(0x0EE0, 0x80) # "Spoke to Kaepora Gaebora by Lost Woods"
    save_context.write_bits(0x0EE7, 0x20) # "Nabooru Captured by Twinrova"
    save_context.write_bits(0x0EE7, 0x10) # "Spoke to Nabooru in Spirit Temple"
    save_context.write_bits(0x0EED, 0x20) # "Sheik, Spawned at Master Sword Pedestal as Adult"
    save_context.write_bits(0x0EED, 0x01) # "Nabooru Ordered to Fight by Twinrova"
    save_context.write_bits(0x0EED, 0x80) # "Watched Ganon's Tower Collapse / Caught by Gerudo"
    save_context.write_bits(0x0EF9, 0x01) # "Greeted by Saria"
    save_context.write_bits(0x0F0A, 0x04) # "Spoke to Ingo Once as Adult"
    save_context.write_bits(0x0F0F, 0x40) # "Met Poe Collector in Ruined Market"
    save_context.write_bits(0x0F1A, 0x04) # "Met Darunia in Fire Temple"

    save_context.write_bits(0x0ED7, 0x01) # "Spoke to Child Malon at Castle or Market"
    save_context.write_bits(0x0ED7, 0x20) # "Spoke to Child Malon at Ranch"
    save_context.write_bits(0x0ED7, 0x40) # "Invited to Sing With Child Malon"
    save_context.write_bits(0x0F09, 0x10) # "Met Child Malon at Castle or Market"
    save_context.write_bits(0x0F09, 0x20) # "Child Malon Said Epona Was Scared of You"

    save_context.write_bits(0x0F21, 0x04) # "Ruto in JJ (M3) Talk First Time"
    save_context.write_bits(0x0F21, 0x02) # "Ruto in JJ (M2) Meet Ruto"

    save_context.write_bits(0x0EE2, 0x01) # "Began Ganondorf Battle"
    save_context.write_bits(0x0EE3, 0x80) # "Began Bongo Bongo Battle"
    save_context.write_bits(0x0EE3, 0x40) # "Began Barinade Battle"
    save_context.write_bits(0x0EE3, 0x20) # "Began Twinrova Battle"
    save_context.write_bits(0x0EE3, 0x10) # "Began Morpha Battle"
    save_context.write_bits(0x0EE3, 0x08) # "Began Volvagia Battle"
    save_context.write_bits(0x0EE3, 0x04) # "Began Phantom Ganon Battle"
    save_context.write_bits(0x0EE3, 0x02) # "Began King Dodongo Battle"
    save_context.write_bits(0x0EE3, 0x01) # "Began Gohma Battle"

    save_context.write_bits(0x0EE8, 0x01) # "Entered Deku Tree"
    save_context.write_bits(0x0EE9, 0x80) # "Entered Temple of Time"
    save_context.write_bits(0x0EE9, 0x40) # "Entered Goron City"
    save_context.write_bits(0x0EE9, 0x20) # "Entered Hyrule Castle"
    save_context.write_bits(0x0EE9, 0x10) # "Entered Zora's Domain"
    save_context.write_bits(0x0EE9, 0x08) # "Entered Kakariko Village"
    save_context.write_bits(0x0EE9, 0x02) # "Entered Death Mountain Trail"
    save_context.write_bits(0x0EE9, 0x01) # "Entered Hyrule Field"
    save_context.write_bits(0x0EEA, 0x04) # "Entered Ganon's Castle (Exterior)"
    save_context.write_bits(0x0EEA, 0x02) # "Entered Death Mountain Crater"
    save_context.write_bits(0x0EEA, 0x01) # "Entered Desert Colossus"
    save_context.write_bits(0x0EEB, 0x80) # "Entered Zora's Fountain"
    save_context.write_bits(0x0EEB, 0x40) # "Entered Graveyard"
    save_context.write_bits(0x0EEB, 0x20) # "Entered Jabu-Jabu's Belly"
    save_context.write_bits(0x0EEB, 0x10) # "Entered Lon Lon Ranch"
    save_context.write_bits(0x0EEB, 0x08) # "Entered Gerudo's Fortress"
    save_context.write_bits(0x0EEB, 0x04) # "Entered Gerudo Valley"
    save_context.write_bits(0x0EEB, 0x02) # "Entered Lake Hylia"
    save_context.write_bits(0x0EEB, 0x01) # "Entered Dodongo's Cavern"
    save_context.write_bits(0x0F08, 0x08) # "Entered Hyrule Castle"

    # Make the Kakariko Gate not open with the MS
    if not world.open_kakariko:
        rom.write_int32(0xDD3538, 0x34190000) # li t9, 0

    if world.open_fountain:
        save_context.write_bits(0x0EDB, 0x08) #Move king zora

    # Make all chest opening animations fast
    rom.write_byte(rom.sym('FAST_CHESTS'), int(world.fast_chests))


    # Set up Rainbow Bridge conditions
    symbol = rom.sym('RAINBOW_BRIDGE_CONDITION')
    if world.bridge == 'open':
        rom.write_int32(symbol, 0)
        save_context.write_bits(0xEDC, 0x20) # "Rainbow Bridge Built by Sages"
    elif world.bridge == 'medallions':
        rom.write_int32(symbol, 1)
    elif world.bridge == 'dungeons':
        rom.write_int32(symbol, 2)
    elif world.bridge == 'stones':
        rom.write_int32(symbol, 3)
    elif world.bridge == 'vanilla':
        rom.write_int32(symbol, 4)
    elif world.bridge == 'tokens':
        rom.write_int32(symbol, 5)

    if world.open_forest:
        save_context.write_bits(0xED5, 0x10) # "Showed Mido Sword & Shield"

    if world.open_door_of_time:
        save_context.write_bits(0xEDC, 0x08) # "Opened the Door of Time"

    # "fast-ganon" stuff
    symbol = rom.sym('NO_ESCAPE_SEQUENCE')
    if world.no_escape_sequence:
        rom.write_bytes(0xD82A12, [0x05, 0x17]) # Sets exit from Ganondorf fight to entrance to Ganon fight
        rom.write_bytes(0xB139A2, [0x05, 0x17]) # Sets Ganon deathwarp back to Ganon
        rom.write_byte(symbol, 0x01)
    else:
        rom.write_byte(symbol, 0x00)
    if world.unlocked_ganondorf:
        save_context.write_bits(0x00D4 + 0x0A * 0x1C + 0x04 + 0x1, 0x10) # Ganon's Tower switch flag (unlock boss key door)
    if world.skipped_trials['Forest']:
        save_context.write_bits(0x0EEA, 0x08) # "Completed Forest Trial"
    if world.skipped_trials['Fire']:
        save_context.write_bits(0x0EEA, 0x40) # "Completed Fire Trial"
    if world.skipped_trials['Water']:
        save_context.write_bits(0x0EEA, 0x10) # "Completed Water Trial"
    if world.skipped_trials['Spirit']:
        save_context.write_bits(0x0EE8, 0x20) # "Completed Spirit Trial"
    if world.skipped_trials['Shadow']:
        save_context.write_bits(0x0EEA, 0x20) # "Completed Shadow Trial"
    if world.skipped_trials['Light']:
        save_context.write_bits(0x0EEA, 0x80) # "Completed Light Trial"
    if world.trials == 0:
        save_context.write_bits(0x0EED, 0x08) # "Dispelled Ganon's Tower Barrier"

    # open gerudo fortress
    if world.gerudo_fortress == 'open':
        if not world.shuffle_gerudo_card:
            save_context.write_bits(0x00A5, 0x40) # Give Gerudo Card
        save_context.write_bits(0x0EE7, 0x0F) # Free all 4 carpenters
        save_context.write_bits(0x00D4 + 0x0C * 0x1C + 0x04 + 0x1, 0x0F) # Thieves' Hideout switch flags (started all fights)
        save_context.write_bits(0x00D4 + 0x0C * 0x1C + 0x04 + 0x2, 0x01) # Thieves' Hideout switch flags (heard yells/unlocked doors)
        save_context.write_bits(0x00D4 + 0x0C * 0x1C + 0x04 + 0x3, 0xFE) # Thieves' Hideout switch flags (heard yells/unlocked doors)
        save_context.write_bits(0x00D4 + 0x0C * 0x1C + 0x0C + 0x2, 0xD4) # Thieves' Hideout collection flags (picked up keys, marks fights finished as well)
    elif world.gerudo_fortress == 'fast':
        save_context.write_bits(0x0EE7, 0x0E) # Free 3 carpenters
        save_context.write_bits(0x00D4 + 0x0C * 0x1C + 0x04 + 0x1, 0x0D) # Thieves' Hideout switch flags (started all fights)
        save_context.write_bits(0x00D4 + 0x0C * 0x1C + 0x04 + 0x2, 0x01) # Thieves' Hideout switch flags (heard yells/unlocked doors)
        save_context.write_bits(0x00D4 + 0x0C * 0x1C + 0x04 + 0x3, 0xDC) # Thieves' Hideout switch flags (heard yells/unlocked doors)
        save_context.write_bits(0x00D4 + 0x0C * 0x1C + 0x0C + 0x2, 0xC4) # Thieves' Hideout collection flags (picked up keys, marks fights finished as well)

    # start with maps/compasses
    if world.shuffle_mapcompass == 'startwith':
        for dungeon in ['deku', 'dodongo', 'jabu', 'forest', 'fire', 'water', 'spirit', 'shadow', 'botw', 'ice']:
            save_context.addresses['dungeon_items'][dungeon]['compass'].value = True
            save_context.addresses['dungeon_items'][dungeon]['map'].value = True

    if world.start_with_wallet:
        world.distribution.give_item('Progressive Wallet', 3)
    if world.start_with_rupees:
        world.distribution.give_item('Rupees', 999)
    if world.start_with_deku_equipment:
        if world.shopsanity == "off":
            world.distribution.give_item('Deku Shield')
        world.distribution.give_item('Deku Sticks', 99)
        world.distribution.give_item('Deku Nuts', 99)
    if world.start_with_fast_travel:
        world.distribution.give_item('Prelude of Light')
        world.distribution.give_item('Serenade of Water')
        world.distribution.give_item('Farores Wind')

    # Set starting time of day
    if world.starting_tod != 'default':
        tod = {
            'midnight':      0x0000,
            'witching-hour': 0x2000,
            'early-morning': 0x4000,
            'morning':       0x6000,
            'noon':          0x8000,
            'afternoon':     0xA000,
            'evening':       0xC000,
            'dusk':          0xE000,
        }
        save_context.addresses['time_of_day'].value = tod[world.starting_tod]

    if world.starting_age == 'adult':
        save_context.addresses['link_age'].value = False                    # Set link's age to adult
        save_context.addresses['scene_index'].value = 0x43                  # Set the scene index to Temple of Time
        save_context.addresses['equip_items']['master_sword'].value = True  # Equip Master Sword by default
        save_context.addresses['equip_items']['kokiri_tunic'].value = True  # Equip Kokiri Tunic & Kokiri Boots by default
        save_context.addresses['equip_items']['kokiri_boots'].value = True  # (to avoid issues when going back child for the first time)

    # Revert change that Skips the Epona Race
    if not world.no_epona_race:
        rom.write_int32(0xA9E838, 0x03E00008)
    else:
        save_context.write_bits(0xF0E, 0x01) # Set talked to Malon flag

    # skip castle guard stealth sequence
    if world.no_guard_stealth:
        # change the exit at child/day crawlspace to the end of zelda's goddess cutscene
        rom.write_bytes(0x21F60DE, [0x05, 0xF0])

    # patch mq scenes
    mq_scenes = []
    if world.dungeon_mq['Deku Tree']:
        mq_scenes.append(0)
    if world.dungeon_mq['Dodongos Cavern']:
        mq_scenes.append(1)
    if world.dungeon_mq['Jabu Jabus Belly']:
        mq_scenes.append(2)
    if world.dungeon_mq['Forest Temple']:
        mq_scenes.append(3)
    if world.dungeon_mq['Fire Temple']:
        mq_scenes.append(4)
    if world.dungeon_mq['Water Temple']:
        mq_scenes.append(5)
    if world.dungeon_mq['Spirit Temple']:
        mq_scenes.append(6)
    if world.dungeon_mq['Shadow Temple']:
        mq_scenes.append(7)
    if world.dungeon_mq['Bottom of the Well']:
        mq_scenes.append(8)
    if world.dungeon_mq['Ice Cavern']:
        mq_scenes.append(9)
    # Scene 10 has no layout changes, so it doesn't need to be patched
    if world.dungeon_mq['Gerudo Training Grounds']:
        mq_scenes.append(11)
    if world.dungeon_mq['Ganons Castle']:
        mq_scenes.append(13)

    patch_files(rom, mq_scenes)

    ### Load Shop File
    # Move shop actor file to free space
    shop_item_file = File({
            'Name':'En_GirlA',
            'Start':'00C004E0',
            'End':'00C02E00',
        })
    shop_item_file.relocate(rom)

    # Increase the shop item table size
    shop_item_vram_start = rom.read_int32(0x00B5E490 + (0x20 * 4) + 0x08)
    insert_space(rom, shop_item_file, shop_item_vram_start, 1, 0x3C + (0x20 * 50), 0x20 * 50)

    # Add relocation entries for shop item table
    new_relocations = []
    for i in range(50, 100):
        new_relocations.append(shop_item_file.start + 0x1DEC + (i * 0x20) + 0x04)
        new_relocations.append(shop_item_file.start + 0x1DEC + (i * 0x20) + 0x14)
        new_relocations.append(shop_item_file.start + 0x1DEC + (i * 0x20) + 0x1C)
    add_relocations(rom, shop_item_file, new_relocations)

    # update actor table
    rom.write_int32s(0x00B5E490 + (0x20 * 4),
        [shop_item_file.start,
        shop_item_file.end,
        shop_item_vram_start,
        shop_item_vram_start + (shop_item_file.end - shop_item_file.start)])

    # Update DMA Table
    update_dmadata(rom, shop_item_file)

    # Create 2nd Bazaar Room
    bazaar_room_file = File({
            'Name':'shop1_room_1',
            'Start':'028E4000',
            'End':'0290D7B0',
        })
    bazaar_room_file.copy(rom)

    # Add new Bazaar Room to Bazaar Scene
    rom.write_int32s(0x28E3030, [0x00010000, 0x02000058]) #reduce position list size
    rom.write_int32s(0x28E3008, [0x04020000, 0x02000070]) #expand room list size

    rom.write_int32s(0x28E3070, [0x028E4000, 0x0290D7B0,
                     bazaar_room_file.start, bazaar_room_file.end]) #room list
    rom.write_int16s(0x28E3080, [0x0000, 0x0001]) # entrance list
    rom.write_int16(0x28E4076, 0x0005) # Change shop to Kakariko Bazaar
    #rom.write_int16(0x3489076, 0x0005) # Change shop to Kakariko Bazaar

    # Load Message and Shop Data
    messages = read_messages(rom)
    shop_items = read_shop_items(rom, shop_item_file.start + 0x1DEC)
    remove_unused_messages(messages)

    # Set Big Poe count to get reward from buyer
    poe_points = world.big_poe_count * 100
    rom.write_int16(0xEE69CE, poe_points)
    # update dialogue
    new_message = "\x08Hey, young man. What's happening \x01today? If you have a \x05\x41Poe\x05\x40, I will \x01buy it.\x04\x1AIf you earn \x05\x41%d points\x05\x40, you'll\x01be a happy man! Heh heh.\x04\x08Your card now has \x05\x45\x1E\x01 \x05\x40points.\x01Come back again!\x01Heh heh heh!\x02" % poe_points
    update_message_by_id(messages, 0x70F5, new_message)
    if world.big_poe_count != 10:      
        new_message = "\x1AOh, you brought a Poe today!\x04\x1AHmmmm!\x04\x1AVery interesting!\x01This is a \x05\x41Big Poe\x05\x40!\x04\x1AI'll buy it for \x05\x4150 Rupees\x05\x40.\x04On top of that, I'll put \x05\x41100\x01points \x05\x40on your card.\x04\x1AIf you earn \x05\x41%d points\x05\x40, you'll\x01be a happy man! Heh heh." % poe_points
        update_message_by_id(messages, 0x70f7, new_message)
        new_message = "\x1AWait a minute! WOW!\x04\x1AYou have earned \x05\x41%d points\x05\x40!\x04\x1AYoung man, you are a genuine\x01\x05\x41Ghost Hunter\x05\x40!\x04\x1AIs that what you expected me to\x01say? Heh heh heh!\x04\x1ABecause of you, I have extra\x01inventory of \x05\x41Big Poes\x05\x40, so this will\x01be the last time I can buy a \x01ghost.\x04\x1AYou're thinking about what I \x01promised would happen when you\x01earned %d points. Heh heh.\x04\x1ADon't worry, I didn't forget.\x01Just take this." % (poe_points, poe_points)
        update_message_by_id(messages, 0x70f8, new_message)


    # use faster jabu elevator
    if not world.dungeon_mq['Jabu Jabus Belly'] and world.shuffle_scrubs == 'off':
        symbol = rom.sym('JABU_ELEVATOR_ENABLE')
        rom.write_byte(symbol, 0x01)

    # Sets hooks for gossip stone changes

    symbol = rom.sym("GOSSIP_HINT_CONDITION");

    if world.hints == 'none':
        rom.write_int32(symbol, 0)
    else:
        writeGossipStoneHints(spoiler, world, messages)

        if world.hints == 'mask':
            rom.write_int32(symbol, 0)
        elif world.hints == 'always':
            rom.write_int32(symbol, 2)
        else:
            rom.write_int32(symbol, 1)


    # build silly ganon lines
    buildGanonText(world, messages)

    # Write item overrides
    override_table = get_override_table(world)
    rom.write_bytes(rom.sym('cfg_item_overrides'), get_override_table_bytes(override_table))
    rom.write_byte(rom.sym('PLAYER_ID'), world.id + 1) # Write player ID

    # Revert Song Get Override Injection
    if not songs_as_items:
        # general get song
        rom.write_int32(0xAE5DF8, 0x240200FF)
        rom.write_int32(0xAE5E04, 0xAD0F00A4)
        # requiem of spirit
        rom.write_int32s(0xAC9ABC, [0x3C010001, 0x00300821])
        # sun song
        rom.write_int32(0xE09F68, 0x8C6F00A4)
        rom.write_int32(0xE09F74, 0x01CFC024)
        rom.write_int32(0xE09FB0, 0x240F0001)
        # epona's song
        rom.write_int32s(0xD7E140, [0x8DCE8C24, 0x8C6F00A4])
        rom.write_int32( 0xD7E77C, 0x8C4900A4)
        rom.write_int32( 0xD7E784, 0x8D088C24)
        rom.write_int32s(0xD7E8D4, [0x8DCE8C24, 0x8C4F00A4])
        rom.write_int32( 0xD7EBBC, 0x14410008)
        rom.write_int32( 0xD7EC1C, 0x17010010)
        # song of time
        rom.write_int32(0xDB532C, 0x24050003)


    # Set damage multiplier
    if world.damage_multiplier == 'half':
        rom.write_byte(rom.sym('CFG_DAMAGE_MULTIPLYER'), -1)
    if world.damage_multiplier == 'normal':
        rom.write_byte(rom.sym('CFG_DAMAGE_MULTIPLYER'), 0)
    if world.damage_multiplier == 'double':
        rom.write_byte(rom.sym('CFG_DAMAGE_MULTIPLYER'), 1)
    if world.damage_multiplier == 'quadruple':
        rom.write_byte(rom.sym('CFG_DAMAGE_MULTIPLYER'), 2)
    if world.damage_multiplier == 'ohko':
        rom.write_byte(rom.sym('CFG_DAMAGE_MULTIPLYER'), 3)

    # Patch songs and boss rewards
    for location in world.get_filled_locations():
        item = location.item
        special = item.special
        locationaddress = location.address
        secondaryaddress = location.address2

        if location.type == 'Song' and not songs_as_items:
            bit_mask_pointer = 0x8C34 + ((special['item_id'] - 0x65) * 4)
            rom.write_byte(locationaddress, special['song_id'])
            next_song_id = special['song_id'] + 0x0D
            rom.write_byte(secondaryaddress, next_song_id)
            if location.name == 'Impa at Castle':
                rom.write_byte(0x0D12ECB, special['item_id'])
                rom.write_byte(0x2E8E931, special['text_id']) #Fix text box
            elif location.name == 'Song from Malon':
                rom.write_int16(0xD7E142, bit_mask_pointer)
                rom.write_int16(0xD7E8D6, bit_mask_pointer)
                rom.write_int16(0xD7E786, bit_mask_pointer)
                rom.write_byte(0x29BECB9, special['text_id']) #Fix text box
            elif location.name == 'Song from Composer Grave':
                rom.write_int16(0xE09F66, bit_mask_pointer)
                rom.write_byte(0x332A87D, special['text_id']) #Fix text box
            elif location.name == 'Song from Saria':
                rom.write_byte(0x0E2A02B, special['item_id'])
                rom.write_byte(0x20B1DBD, special['text_id']) #Fix text box
            elif location.name == 'Song from Ocarina of Time':
                rom.write_byte(0x252FC95, special['text_id']) #Fix text box
            elif location.name == 'Song at Windmill':
                rom.write_byte(0x0E42ABF, special['item_id'])
                rom.write_byte(0x3041091, special['text_id']) #Fix text box
            elif location.name == 'Sheik Forest Song':
                rom.write_byte(0x0C7BAA3, special['item_id'])
                rom.write_byte(0x20B0815, special['text_id']) #Fix text box
            elif location.name == 'Sheik at Temple':
                rom.write_byte(0x0C805EF, special['item_id'])
                rom.write_byte(0x2531335, special['text_id']) #Fix text box
            elif location.name == 'Sheik in Crater':
                rom.write_byte(0x0C7BC57, special['item_id'])
                rom.write_byte(0x224D7FD, special['text_id']) #Fix text box
            elif location.name == 'Sheik in Ice Cavern':
                rom.write_byte(0x0C7BD77, special['item_id'])
                rom.write_byte(0x2BEC895, special['text_id']) #Fix text box
            elif location.name == 'Sheik in Kakariko':
                rom.write_byte(0x0AC9A5B, special['item_id'])
                rom.write_byte(0x2000FED, special['text_id']) #Fix text box
            elif location.name == 'Sheik at Colossus':
                rom.write_byte(0x218C589, special['text_id']) #Fix text box
        elif location.type == 'Boss':
            if location.name == 'Links Pocket':
                save_context.give_item(item.name)
            else:
                rom.write_byte(locationaddress, special['item_id'])
                rom.write_byte(secondaryaddress, special['addr2_data'])
                bit_mask_hi = special['bit_mask'] >> 16
                bit_mask_lo = special['bit_mask'] & 0xFFFF
                if location.name == 'Bongo Bongo':
                    rom.write_int16(0xCA3F32, bit_mask_hi)
                    rom.write_int16(0xCA3F36, bit_mask_lo)
                elif location.name == 'Twinrova':
                    rom.write_int16(0xCA3EA2, bit_mask_hi)
                    rom.write_int16(0xCA3EA6, bit_mask_lo)

    # add a cheaper bombchu pack to the bombchu shop
    # describe
    update_message_by_id(messages, 0x80FE, '\x08\x05\x41Bombchu   (5 pieces)   60 Rupees\x01\x05\x40This looks like a toy mouse, but\x01it\'s actually a self-propelled time\x01bomb!\x09\x0A', 0x03)
    # purchase
    update_message_by_id(messages, 0x80FF, '\x08Bombchu    5 Pieces    60 Rupees\x01\x01\x1B\x05\x42Buy\x01Don\'t buy\x05\x40\x09', 0x03)
    rbl_bombchu = shop_items[0x0018]
    rbl_bombchu.price = 60
    rbl_bombchu.pieces = 5
    rbl_bombchu.get_item_id = 0x006A
    rbl_bombchu.description_message = 0x80FE
    rbl_bombchu.purchase_message = 0x80FF

    # Reduce 10 Pack Bombchus from 100 to 99 Rupees
    shop_items[0x0015].price = 99
    shop_items[0x0019].price = 99
    shop_items[0x001C].price = 99
    update_message_by_id(messages, shop_items[0x001C].description_message, "\x08\x05\x41Bombchu  (10 pieces)  99 Rupees\x01\x05\x40This looks like a toy mouse, but\x01it's actually a self-propelled time\x01bomb!\x09\x0A")
    update_message_by_id(messages, shop_items[0x001C].purchase_message, "\x08Bombchu  10 pieces   99 Rupees\x09\x01\x01\x1B\x05\x42Buy\x01Don't buy\x05\x40")

    shuffle_messages.shop_item_messages = []

    # kokiri shop
    shop_objs = place_shop_items(rom, world, shop_items, messages,
        world.get_region('Kokiri Shop').locations, True)
    shop_objs |= {0x00FC, 0x00B2, 0x0101, 0x0102, 0x00FD, 0x00C5} # Shop objects
    rom.write_byte(0x2587029, len(shop_objs))
    rom.write_int32(0x258702C, 0x0300F600)
    rom.write_int16s(0x2596600, list(shop_objs))

    # kakariko bazaar
    shop_objs = place_shop_items(rom, world, shop_items, messages,
        world.get_region('Kakariko Bazaar').locations)
    shop_objs |= {0x005B, 0x00B2, 0x00C5, 0x0107, 0x00C9, 0x016B} # Shop objects
    rom.write_byte(0x28E4029, len(shop_objs))
    rom.write_int32(0x28E402C, 0x03007A40)
    rom.write_int16s(0x28EBA40, list(shop_objs))

    # castle town bazaar
    shop_objs = place_shop_items(rom, world, shop_items, messages,
        world.get_region('Castle Town Bazaar').locations)
    shop_objs |= {0x005B, 0x00B2, 0x00C5, 0x0107, 0x00C9, 0x016B} # Shop objects
    rom.write_byte(bazaar_room_file.start + 0x29, len(shop_objs))
    rom.write_int32(bazaar_room_file.start + 0x2C, 0x03007A40)
    rom.write_int16s(bazaar_room_file.start + 0x7A40, list(shop_objs))

    # goron shop
    shop_objs = place_shop_items(rom, world, shop_items, messages,
        world.get_region('Goron Shop').locations)
    shop_objs |= {0x00C9, 0x00B2, 0x0103, 0x00AF} # Shop objects
    rom.write_byte(0x2D33029, len(shop_objs))
    rom.write_int32(0x2D3302C, 0x03004340)
    rom.write_int16s(0x2D37340, list(shop_objs))

    # zora shop
    shop_objs = place_shop_items(rom, world, shop_items, messages,
        world.get_region('Zora Shop').locations)
    shop_objs |= {0x005B, 0x00B2, 0x0104, 0x00FE} # Shop objects
    rom.write_byte(0x2D5B029, len(shop_objs))
    rom.write_int32(0x2D5B02C, 0x03004B40)
    rom.write_int16s(0x2D5FB40, list(shop_objs))

    # kakariko potion shop
    shop_objs = place_shop_items(rom, world, shop_items, messages,
        world.get_region('Kakariko Potion Shop Front').locations)
    shop_objs |= {0x0159, 0x00B2, 0x0175, 0x0122} # Shop objects
    rom.write_byte(0x2D83029, len(shop_objs))
    rom.write_int32(0x2D8302C, 0x0300A500)
    rom.write_int16s(0x2D8D500, list(shop_objs))

    # market potion shop
    shop_objs = place_shop_items(rom, world, shop_items, messages,
        world.get_region('Castle Town Potion Shop').locations)
    shop_objs |= {0x0159, 0x00B2, 0x0175, 0x00C5, 0x010C, 0x016B} # Shop objects
    rom.write_byte(0x2DB0029, len(shop_objs))
    rom.write_int32(0x2DB002C, 0x03004E40)
    rom.write_int16s(0x2DB4E40, list(shop_objs))

    # bombchu shop
    shop_objs = place_shop_items(rom, world, shop_items, messages,
        world.get_region('Castle Town Bombchu Shop').locations)
    shop_objs |= {0x0165, 0x00B2} # Shop objects
    rom.write_byte(0x2DD8029, len(shop_objs))
    rom.write_int32(0x2DD802C, 0x03006A40)
    rom.write_int16s(0x2DDEA40, list(shop_objs))

    # Scrub text stuff.
    def update_scrub_text(message, text_replacement, default_price, price, item_name=None):
        scrub_strip_text = ["some ", "1 piece   ", "5 pieces   ", "30 pieces   "]
        for text in scrub_strip_text:
            message = message.replace(text.encode(), b'')
        message = message.replace(text_replacement[0].encode(), text_replacement[1].encode())
        message = message.replace(b'they are', b'it is')
        if default_price != price:
            message = message.replace(('%d Rupees' % default_price).encode(), ('%d Rupees' % price).encode())
        if item_name is not None:
            message = message.replace(b'mysterious item', item_name.encode())
        return message

    single_item_scrubs = {
        0x3E: world.get_location("HF Grotto Deku Scrub Piece of Heart"),
        0x77: world.get_location("LW Deku Scrub Deku Stick Upgrade"),
        0x79: world.get_location("LW Grotto Deku Scrub Deku Nut Upgrade"),
    }

    scrub_message_dict = {}
    if world.shuffle_scrubs == 'off':
        # Revert Deku Scrubs changes
        rom.write_int32s(0xEBB85C, [
            0x24010002, # addiu at, zero, 2
            0x3C038012, # lui v1, 0x8012
            0x14410004, # bne v0, at, 0xd8
            0x2463A5D0, # addiu v1, v1, -0x5a30
            0x94790EF0])# lhu t9, 0xef0(v1)
        rom.write_int32(0xDF7CB0,
            0xA44F0EF0)  # sh t7, 0xef0(v0)

        # Replace scrub text for 3 default shuffled scrubs.
        for (scrub_item, default_price, text_id, text_replacement) in business_scrubs:
            if scrub_item not in single_item_scrubs.keys():
                continue
            scrub_message_dict[text_id] = update_scrub_text(get_message_by_id(messages, text_id).raw_text, text_replacement, default_price, default_price)
    else:
        # Rebuild Business Scrub Item Table
        rom.seek_address(0xDF8684)
        for (scrub_item, default_price, text_id, text_replacement) in business_scrubs:
            price = world.scrub_prices[scrub_item]
            rom.write_int16(None, price)       # Price
            rom.write_int16(None, 1)           # Count
            rom.write_int32(None, scrub_item)  # Item
            rom.write_int32(None, 0x80A74FF8)  # Can_Buy_Func
            rom.write_int32(None, 0x80A75354)  # Buy_Func

            scrub_message_dict[text_id] = update_scrub_text(get_message_by_id(messages, text_id).raw_text, text_replacement, default_price, price)

        # update actor IDs
        set_deku_salesman_data(rom)

    # Update scrub messages.
    for text_id, message in scrub_message_dict.items():
        update_message_by_id(messages, text_id, message)

    if world.shuffle_grotto_entrances:
        # Update grotto actors based on their new entrance
        set_grotto_shuffle_data(rom, world)

    if world.shuffle_cows:
        rom.write_byte(rom.sym('SHUFFLE_COWS'), 0x01)
        #Moves the cow in LLR Tower, as the two cows are too close in vanilla
        rom.write_bytes(0x33650CA, [0xFE, 0xD3, 0x00, 0x00, 0x00, 0x6E, 0x00, 0x00, 0x4A, 0x34])
        set_cow_id_data(rom, world)

    if world.shuffle_smallkeys == 'remove' or world.shuffle_bosskeys == 'remove':
        locked_doors = get_locked_doors(rom, world)
        for _,[door_byte, door_bits] in locked_doors.items():
            save_context.write_bits(door_byte, door_bits)

    # Fix chest animations
    if world.bombchus_in_logic:
        bombchu_ids = [0x6A, 0x03, 0x6B]
        for i in bombchu_ids:
            item = read_rom_item(rom, i)
            item['chest_type'] = 0
            write_rom_item(rom, i, item)
    if world.bridge == 'tokens':
        item = read_rom_item(rom, 0x5B)
        item['chest_type'] = 0
        write_rom_item(rom, 0x5B, item)       

    # Update chest type sizes
    if world.correct_chest_sizes:
        symbol = rom.sym('CHEST_SIZE_MATCH_CONTENTS')
        rom.write_int32(symbol, 0x00000001)
        # Move Ganon's Castle's Zelda's Lullaby Chest back so is reachable if large
        if not world.dungeon_mq['Ganons Castle']:
            rom.write_int16(0x321B176, 0xFC40) # original 0xFC48

        # Move Spirit Temple Compass Chest if it is a small chest so it is reachable with hookshot 
        if not world.dungeon_mq['Spirit Temple']:
            chest_name = 'Spirit Temple Compass Chest'
            chest_address = 0x2B6B07C
            location = world.get_location(chest_name)
            item = read_rom_item(rom, location.item.index)
            if item['chest_type'] in (1, 3):
                rom.write_int16(chest_address + 2, 0x0190) # X pos
                rom.write_int16(chest_address + 6, 0xFABC) # Z pos

    # give dungeon items the correct messages
    add_item_messages(messages, shop_items, world)
    if world.enhance_map_compass:
        reward_list = {'Kokiri Emerald':   "\x05\x42Kokiri Emerald\x05\x40",
                       'Goron Ruby':       "\x05\x41Goron Ruby\x05\x40",
                       'Zora Sapphire':    "\x05\x43Zora Sapphire\x05\x40",
                       'Forest Medallion': "\x05\x42Forest Medallion\x05\x40",
                       'Fire Medallion':   "\x05\x41Fire Medallion\x05\x40",
                       'Water Medallion':  "\x05\x43Water Medallion\x05\x40",
                       'Spirit Medallion': "\x05\x46Spirit Medallion\x05\x40",
                       'Shadow Medallion': "\x05\x45Shadow Medallion\x05\x40",
                       'Light Medallion':  "\x05\x44Light Medallion\x05\x40"
        }
        dungeon_list = {'Deku Tree':          ("the \x05\x42Deku Tree", 'Queen Gohma', 0x62, 0x88),
                        'Dodongos Cavern':    ("\x05\x41Dodongo\'s Cavern", 'King Dodongo', 0x63, 0x89),
                        'Jabu Jabus Belly':   ("\x05\x43Jabu Jabu\'s Belly", 'Barinade', 0x64, 0x8a),
                        'Forest Temple':      ("the \x05\x42Forest Temple", 'Phantom Ganon', 0x65, 0x8b),
                        'Fire Temple':        ("the \x05\x41Fire Temple", 'Volvagia', 0x7c, 0x8c),
                        'Water Temple':       ("the \x05\x43Water Temple", 'Morpha', 0x7d, 0x8e),
                        'Spirit Temple':      ("the \x05\x46Spirit Temple", 'Twinrova', 0x7e, 0x8f),
                        'Ice Cavern':         ("the \x05\x44Ice Cavern", None, 0x87, 0x92),
                        'Bottom of the Well': ("the \x05\x45Bottom of the Well", None, 0xa2, 0xa5),
                        'Shadow Temple':      ("the \x05\x45Shadow Temple", 'Bongo Bongo', 0x7f, 0xa3),
        }
        for dungeon in world.dungeon_mq:
            if dungeon in ['Gerudo Training Grounds', 'Ganons Castle']:
                pass
            elif dungeon in ['Bottom of the Well', 'Ice Cavern']:
                dungeon_name, boss_name, compass_id, map_id = dungeon_list[dungeon]
                if world.world_count > 1:
                    map_message = "\x13\x76\x08\x05\x42\x0F\x05\x40 found the \x05\x41Dungeon Map\x05\x40\x01for %s\x05\x40!\x09" % (dungeon_name)
                else:
                    map_message = "\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for %s\x05\x40!\x01It\'s %s!\x09" % (dungeon_name, "masterful" if world.dungeon_mq[dungeon] else "ordinary")

                if world.mq_dungeons_random or world.mq_dungeons != 0 and world.mq_dungeons != 12:
                    update_message_by_id(messages, map_id, map_message)
            else:
                dungeon_name, boss_name, compass_id, map_id = dungeon_list[dungeon]
                dungeon_reward = reward_list[world.get_location(boss_name).item.name]
                if world.world_count > 1:
                    compass_message = "\x13\x75\x08\x05\x42\x0F\x05\x40 found the \x05\x41Compass\x05\x40\x01for %s\x05\x40!\x09" % (dungeon_name)
                else:
                    compass_message = "\x13\x75\x08You found the \x05\x41Compass\x05\x40\x01for %s\x05\x40!\x01It holds the %s!\x09" % (dungeon_name, dungeon_reward)
                update_message_by_id(messages, compass_id, compass_message)
                if world.mq_dungeons_random or world.mq_dungeons != 0 and world.mq_dungeons != 12:
                    if world.world_count > 1:
                        map_message = "\x13\x76\x08\x05\x42\x0F\x05\x40 found the \x05\x41Dungeon Map\x05\x40\x01for %s\x05\x40!\x09" % (dungeon_name)
                    else:
                        map_message = "\x13\x76\x08You found the \x05\x41Dungeon Map\x05\x40\x01for %s\x05\x40!\x01It\'s %s!\x09" % (dungeon_name, "masterful" if world.dungeon_mq[dungeon] else "ordinary")
                    update_message_by_id(messages, map_id, map_message)

    else:
        # Set hints for boss reward shuffle
        rom.write_bytes(0xE2ADB2, [0x70, 0x7A])
        rom.write_bytes(0xE2ADB6, [0x70, 0x57])
        buildBossRewardHints(world, messages)

    # update happy mask shop to use new SOLD OUT text id
    rom.write_int16(shop_item_file.start + 0x1726, shop_items[0x26].description_message)

    # Add 3rd Wallet Upgrade
    rom.write_int16(0xB6D57E, 0x0003)
    rom.write_int16(0xB6EC52, 999)
    tycoon_message = "\x08\x13\x57You got a \x05\x43Tycoon's Wallet\x05\x40!\x01Now you can hold\x01up to \x05\x46999\x05\x40 \x05\x46Rupees\x05\x40."
    if world.world_count > 1:
       tycoon_message = make_player_message(tycoon_message)
    update_message_by_id(messages, 0x00F8, tycoon_message, 0x23)
    
    #write/shuffle messages was moved down
    

    if world.free_scarecrow:
        # Played song as adult
        save_context.write_bits(0x0EE6, 0x10)
        # Direct scarecrow behavior
        symbol = rom.sym('FREE_SCARECROW_ENABLED')
        rom.write_byte(symbol, 0x01)

    if world.ocarina_songs:
        replace_songs(rom)

    # actually write the save table to rom
    world.distribution.give_items(save_context)
    if world.starting_age == 'adult':
        # When starting as adult, the pedestal doesn't handle child default equips when going back child the first time, so we have to equip them ourselves
        save_context.equip_default_items('child')
    save_context.equip_current_items(world.starting_age)
    save_context.write_save_table(rom)


    symbol = rom.sym('NAVI_HINTSs_CONDITION')
    if world.settings.Navi_Hints:
        rom.write_int32(symbol, 1)
        wNavi = Navi_Hints(rom)
        wNavi.Navi_Hints_patch(rom, world, spoiler, save_context, outfilebase, messages)

    else:
        rom.write_int32(symbol, 0)


    repack_messages(rom, messages)

    # text shuffle
    if world.text_shuffle == 'except_hints':
        shuffle_messages(rom, except_hints=True)
    elif world.text_shuffle == 'complete':
        shuffle_messages(rom, except_hints=False)
        
    write_shop_items(rom, shop_item_file.start + 0x1DEC, shop_items)


    # output a text dump, for testing...
    #with open('keysanity_' + str(world.seed) + '_dump.txt', 'w', encoding='utf-16') as f:
    #     messages = read_messages(rom)
    #     f.write('item_message_strings = {\n')
    #     for m in messages:
    #        f.write("\t0x%04X: \"%s\",\n" % (m.id, m.get_python_string()))
    #     f.write('}\n')

        
    symbol = rom.sym('SARIA_HINTS_CONDITION')
    if world.settings.saria_repeats_hints:
        rom.write_int32(symbol, 1)
        
        #Generate gossip stone TextID table
        index = 0
        SARIA_GOSSIP_TEXTID_TABLE_SYM = rom.sym('SARIA_GOSSIP_TEXTID_TABLE_SYM')
        
        for message in messages:
            if (message.id <= 0x04FF) and (message.id >= 0x0401):
                byteArray = message.id.to_bytes(2, 'big')
                rom.write_bytes(int(SARIA_GOSSIP_TEXTID_TABLE_SYM)+2*index, byteArray) #is a J, was a jr before, cyclic hack jumps back to previous ret address
                
                index += 1
                
                if(index>42):
                    raise ValueError('ERROR - Saria gossip TextID overflow')
        
    else:
        rom.write_int32(symbol, 0)


    
    return rom


item_row_struct = struct.Struct('>BBHHBBIIhh') # Match item_row_t in item_table.h
item_row_fields = [
    'base_item_id', 'action_id', 'text_id', 'object_id', 'graphic_id', 'chest_type',
    'upgrade_fn', 'effect_fn', 'effect_arg1', 'effect_arg2',
]


def read_rom_item(rom, item_id):
    addr = rom.sym('item_table') + (item_id * item_row_struct.size)
    row_bytes = rom.read_bytes(addr, item_row_struct.size)
    row = item_row_struct.unpack(row_bytes)
    return { item_row_fields[i]: row[i] for i in range(len(item_row_fields)) }


def write_rom_item(rom, item_id, item):
    addr = rom.sym('item_table') + (item_id * item_row_struct.size)
    row = [item[f] for f in item_row_fields]
    row_bytes = item_row_struct.pack(*row)
    rom.write_bytes(addr, row_bytes)



def get_override_table(world):
    return list(filter(lambda val: val != None, map(get_override_entry, world.get_filled_locations())))


override_struct = struct.Struct('>xBBBHBB') # match override_t in get_items.c
def get_override_table_bytes(override_table):
    return b''.join(sorted(itertools.starmap(override_struct.pack, override_table)))


def get_override_entry(location):
    scene = location.scene
    default = location.default
    item_id = location.item.index
    if None in [scene, default, item_id]:
        return None

    player_id = location.item.world.id + 1
    if location.item.looks_like_item is not None:
        looks_like_item_id = location.item.looks_like_item.index
    else:
        looks_like_item_id = 0

    if location.type in ['NPC', 'BossHeart']:
        type = 0
    elif location.type == 'Chest':
        type = 1
        default &= 0x1F
    elif location.type == 'Collectable':
        type = 2
    elif location.type == 'GS Token':
        type = 3
    elif location.type == 'Shop' and location.item.type != 'Shop':
        type = 0
    elif location.type == 'GrottoNPC' and location.item.type != 'Shop':
        type = 4
    elif location.type in ['Song', 'Cutscene']:
        type = 5
    else:
        return None

    return (scene, type, default, item_id, player_id, looks_like_item_id)


chestTypeMap = {
        #    small   big     boss
    0x0000: [0x5000, 0x0000, 0x2000], #Large
    0x1000: [0x7000, 0x1000, 0x1000], #Large, Appears, Clear Flag
    0x2000: [0x5000, 0x0000, 0x2000], #Boss Key’s Chest
    0x3000: [0x8000, 0x3000, 0x3000], #Large, Falling, Switch Flag
    0x4000: [0x6000, 0x4000, 0x4000], #Large, Invisible
    0x5000: [0x5000, 0x0000, 0x2000], #Small
    0x6000: [0x6000, 0x4000, 0x4000], #Small, Invisible
    0x7000: [0x7000, 0x1000, 0x1000], #Small, Appears, Clear Flag
    0x8000: [0x8000, 0x3000, 0x3000], #Small, Falling, Switch Flag
    0x9000: [0x9000, 0x9000, 0x9000], #Large, Appears, Zelda's Lullaby
    0xA000: [0xA000, 0xA000, 0xA000], #Large, Appears, Sun's Song Triggered
    0xB000: [0xB000, 0xB000, 0xB000], #Large, Appears, Switch Flag
    0xC000: [0x5000, 0x0000, 0x2000], #Large
    0xD000: [0x5000, 0x0000, 0x2000], #Large
    0xE000: [0x5000, 0x0000, 0x2000], #Large
    0xF000: [0x5000, 0x0000, 0x2000], #Large
}


def room_get_actors(rom, actor_func, room_data, scene, alternate=None):
    actors = {}
    room_start = alternate if alternate else room_data
    command = 0
    while command != 0x14: # 0x14 = end header
        command = rom.read_byte(room_data)
        if command == 0x01: # actor list
            actor_count = rom.read_byte(room_data + 1)
            actor_list = room_start + (rom.read_int32(room_data + 4) & 0x00FFFFFF)
            for _ in range(0, actor_count):
                actor_id = rom.read_int16(actor_list)
                entry = actor_func(rom, actor_id, actor_list, scene)
                if entry:
                    actors[actor_list] = entry
                actor_list = actor_list + 16
        if command == 0x18: # Alternate header list
            header_list = room_start + (rom.read_int32(room_data + 4) & 0x00FFFFFF)
            for alt_id in range(0,3):
                header_data = room_start + (rom.read_int32(header_list) & 0x00FFFFFF)
                if header_data != 0 and not alternate:
                    actors.update(room_get_actors(rom, actor_func, header_data, scene, room_start))
                header_list = header_list + 4
        room_data = room_data + 8
    return actors


def scene_get_actors(rom, actor_func, scene_data, scene, alternate=None, processed_rooms=None):
    if processed_rooms == None:
        processed_rooms = []
    actors = {}
    scene_start = alternate if alternate else scene_data
    command = 0
    while command != 0x14: # 0x14 = end header
        command = rom.read_byte(scene_data)
        if command == 0x04: #room list
            room_count = rom.read_byte(scene_data + 1)
            room_list = scene_start + (rom.read_int32(scene_data + 4) & 0x00FFFFFF)
            for _ in range(0, room_count):
                room_data = rom.read_int32(room_list);

                if not room_data in processed_rooms:
                    actors.update(room_get_actors(rom, actor_func, room_data, scene))
                    processed_rooms.append(room_data)
                room_list = room_list + 8
        if command == 0x0E: #transition actor list
            actor_count = rom.read_byte(scene_data + 1)
            actor_list = scene_start + (rom.read_int32(scene_data + 4) & 0x00FFFFFF)
            for _ in range(0, actor_count):
                actor_id = rom.read_int16(actor_list + 4)
                entry = actor_func(rom, actor_id, actor_list, scene)
                if entry:
                    actors[actor_list] = entry
                actor_list = actor_list + 16
        if command == 0x18: # Alternate header list
            header_list = scene_start + (rom.read_int32(scene_data + 4) & 0x00FFFFFF)
            for alt_id in range(0,3):
                header_data = scene_start + (rom.read_int32(header_list) & 0x00FFFFFF)
                if header_data != 0 and not alternate:
                    actors.update(scene_get_actors(rom, actor_func, header_data, scene, scene_start, processed_rooms))
                header_list = header_list + 4

        scene_data = scene_data + 8
    return actors


def get_actor_list(rom, actor_func):
    actors = {}
    scene_table = 0x00B71440
    for scene in range(0x00, 0x65):
        scene_data = rom.read_int32(scene_table + (scene * 0x14));
        actors.update(scene_get_actors(rom, actor_func, scene_data, scene))
    return actors


def get_override_itemid(override_table, scene, type, flags):
    for entry in override_table:
        if entry[0] == scene and (entry[1] & 0x07) == type and entry[2] == flags:
            return entry[4]
    return None

def remove_entrance_blockers(rom):
    def remove_entrance_blockers_do(rom, actor_id, actor, scene):
        if actor_id == 0x014E and scene == 97:
            actor_var = rom.read_int16(actor + 14);
            if actor_var == 0xFF01:
                rom.write_int16(actor + 14, 0x0700)
    get_actor_list(rom, remove_entrance_blockers_do)

def set_cow_id_data(rom, world):
    def set_cow_id(rom, actor_id, actor, scene):
        nonlocal last_scene
        nonlocal cow_count
        nonlocal last_actor

        if actor_id == 0x01C6: #Cow
            if scene == last_scene and last_actor != actor:
                cow_count += 1
            else:
                cow_count = 1

            last_scene = scene
            last_actor = actor
            if world.dungeon_mq['Jabu Jabus Belly'] and scene == 2: #If its an MQ jabu cow
                rom.write_int16(actor + 0x8, 1 if cow_count == 17 else 0) #Give all wall cows ID 0, and set cow 11's ID to 1
            else:
                rom.write_int16(actor + 0x8, cow_count)

    last_actor = -1
    last_scene = -1
    cow_count = 1

    get_actor_list(rom, set_cow_id)


def set_grotto_shuffle_data(rom, world):
    def get_grotto_data(rom, actor_id, actor, scene):
        if actor_id == 0x009B: #Grotto
            actor_zrot = rom.read_int16(actor + 12)
            actor_var = rom.read_int16(actor + 14)

            grotto_table[actor] = {
                'id': (scene << 16) + actor_var,
                'scene': (actor_var >> 8) & 0xF0,
                'entrance': actor_zrot & 0x00FF,
                'content': actor_var & 0x00FF,
            }

    def override_grotto_data(rom, actor_id, actor, scene):
        if actor_id == 0x009B: #Grotto
            actor_zrot = rom.read_int16(actor + 12)
            actor_var = rom.read_int16(actor + 14)
            grotto_type = (actor_var >> 8) & 0x0F

            grotto_data = grotto_override_table[actor]
            rom.write_byte(actor + 14, grotto_type + grotto_data['scene'])
            rom.write_byte(actor + 13, grotto_data['entrance'])
            rom.write_byte(actor + 15, grotto_data['content'])

    # Retrieve the original grotto data
    grotto_table = {}
    get_actor_list(rom, get_grotto_data)

    # Build the override table based on shuffled grotto entrances
    shuffled_grotto_table = {}
    for entrance in world.get_shuffled_entrances(type='Grotto'):
        grotto_id = (entrance.data['scene'] << 16) + entrance.data['grotto_var']
        grotto_override_id = (entrance.replaces.data['scene'] << 16) + entrance.replaces.data['grotto_var']
        shuffled_grotto_table[grotto_id] = grotto_override_id

    grotto_override_table = {}
    for actor in grotto_table:
        grotto_id = grotto_table[actor]['id']
        grotto_override_table[actor] = next(filter(lambda grotto_data: grotto_data['id'] == shuffled_grotto_table[grotto_id], grotto_table.values()))

    # Override grotto actors data with the new table
    get_actor_list(rom, override_grotto_data)


def set_deku_salesman_data(rom):
    def set_deku_salesman(rom, actor_id, actor, scene):
        if actor_id == 0x0195: #Salesman
            actor_var = rom.read_int16(actor + 14)
            if actor_var == 6:
                rom.write_int16(actor + 14, 0x0003)

    get_actor_list(rom, set_deku_salesman)


def get_locked_doors(rom, world):
    def locked_door(rom, actor_id, actor, scene):
        actor_var = rom.read_int16(actor + 14)
        actor_type = actor_var >> 6
        actor_flag = actor_var & 0x003F

        flag_id = (1 << actor_flag)
        flag_byte = 3 - (actor_flag >> 3)
        flag_bits = 1 << (actor_flag & 0x07)

        # If locked door, set the door's unlock flag
        if world.shuffle_smallkeys == 'remove':
            if actor_id == 0x0009 and actor_type == 0x02:
                return [0x00D4 + scene * 0x1C + 0x04 + flag_byte, flag_bits]
            if actor_id == 0x002E and actor_type == 0x0B:
                return [0x00D4 + scene * 0x1C + 0x04 + flag_byte, flag_bits]

        # If boss door, set the door's unlock flag
        if world.shuffle_bosskeys == 'remove':
            if actor_id == 0x002E and actor_type == 0x05:
                return [0x00D4 + scene * 0x1C + 0x04 + flag_byte, flag_bits]

    return get_actor_list(rom, locked_door)


def create_fake_name(name):
    vowels = 'aeiou'
    list_name = list(name)
    vowel_indexes = [i for i,c in enumerate(list_name) if c in vowels]
    for i in random.sample(vowel_indexes, min(2, len(vowel_indexes))):
        c = list_name[i]
        list_name[i] = random.choice([v for v in vowels if v != c])
    
    # keeping the game E...
    new_name = ''.join(list_name)
    censor = ['cum', 'cunt', 'dike', 'penis', 'puss', 'shit']
    new_name_az = re.sub(r'[^a-zA-Z]', '', new_name.lower(), re.UNICODE)
    for cuss in censor:
        if cuss in new_name_az:
            return create_fake_name(name)
    return new_name


def place_shop_items(rom, world, shop_items, messages, locations, init_shop_id=False):
    if init_shop_id:
        place_shop_items.shop_id = 0x32

    shop_objs = { 0x0148 } # "Sold Out" object
    for location in locations:
        if location.item.type == 'Shop':
            shop_objs.add(location.item.special['object'])
            rom.write_int16(location.address, location.item.index)
        else:
            if location.item.looks_like_item is not None:
                item_display = location.item.looks_like_item
            else:
                item_display = location.item

            # bottles in shops should look like empty bottles
            # so that that are different than normal shop refils
            if 'shop_object' in item_display.special:
                rom_item = read_rom_item(rom, item_display.special['shop_object'])
            else:
                rom_item = read_rom_item(rom, item_display.index)

            shop_objs.add(rom_item['object_id'])
            shop_id = place_shop_items.shop_id
            rom.write_int16(location.address, shop_id)
            shop_item = shop_items[shop_id]

            shop_item.object = rom_item['object_id']
            shop_item.model = rom_item['graphic_id'] - 1
            shop_item.price = location.price
            shop_item.pieces = 1
            shop_item.get_item_id = location.default
            shop_item.func1 = 0x808648CC
            shop_item.func2 = 0x808636B8
            shop_item.func3 = 0x00000000
            shop_item.func4 = 0x80863FB4

            message_id = (shop_id - 0x32) * 2
            shop_item.description_message = 0x8100 + message_id
            shop_item.purchase_message = 0x8100 + message_id + 1

            shuffle_messages.shop_item_messages.extend(
                [shop_item.description_message, shop_item.purchase_message])

            if item_display.dungeonitem:
                split_item_name = item_display.name.split('(')
                split_item_name[1] = '(' + split_item_name[1]

                if location.item.name == 'Ice Trap':
                    split_item_name[0] = create_fake_name(split_item_name[0])

                if world.world_count > 1:
                    description_text = '\x08\x05\x41%s  %d Rupees\x01%s\x01\x05\x42Player %d\x05\x40\x01Special deal! ONE LEFT!\x09\x0A\x02' % (split_item_name[0], location.price, split_item_name[1], location.item.world.id + 1)
                else:
                    description_text = '\x08\x05\x41%s  %d Rupees\x01%s\x01\x05\x40Special deal! ONE LEFT!\x01Get it while it lasts!\x09\x0A\x02' % (split_item_name[0], location.price, split_item_name[1])
                purchase_text = '\x08%s  %d Rupees\x09\x01%s\x01\x1B\x05\x42Buy\x01Don\'t buy\x05\x40\x02' % (split_item_name[0], location.price, split_item_name[1])
            else:
                shop_item_name = getSimpleHintNoPrefix(item_display)
                if location.item.name == 'Ice Trap':
                    shop_item_name = create_fake_name(shop_item_name)

                if world.world_count > 1:
                    description_text = '\x08\x05\x41%s  %d Rupees\x01\x05\x42Player %d\x05\x40\x01Special deal! ONE LEFT!\x09\x0A\x02' % (shop_item_name, location.price, location.item.world.id + 1)
                else:
                    description_text = '\x08\x05\x41%s  %d Rupees\x01\x05\x40Special deal! ONE LEFT!\x01Get it while it lasts!\x09\x0A\x02' % (shop_item_name, location.price)
                purchase_text = '\x08%s  %d Rupees\x09\x01\x01\x1B\x05\x42Buy\x01Don\'t buy\x05\x40\x02' % (shop_item_name, location.price)

            update_message_by_id(messages, shop_item.description_message, description_text, 0x03)
            update_message_by_id(messages, shop_item.purchase_message, purchase_text, 0x03)

            place_shop_items.shop_id += 1

    return shop_objs


def boss_reward_index(world, boss_name):
    code = world.get_location(boss_name).item.special['item_id']
    if code >= 0x6C:
        return code - 0x6C
    else:
        return 3 + code - 0x66


def configure_dungeon_info(rom, world):
    mq_enable = (world.mq_dungeons_random or world.mq_dungeons != 0 and world.mq_dungeons != 12)
    mapcompass_keysanity = world.settings.enhance_map_compass

    bosses = ['Queen Gohma', 'King Dodongo', 'Barinade', 'Phantom Ganon',
            'Volvagia', 'Morpha', 'Twinrova', 'Bongo Bongo']
    dungeon_rewards = [boss_reward_index(world, boss) for boss in bosses]

    codes = ['Deku Tree', 'Dodongos Cavern', 'Jabu Jabus Belly', 'Forest Temple',
             'Fire Temple', 'Water Temple', 'Spirit Temple', 'Shadow Temple',
             'Bottom of the Well', 'Ice Cavern', 'Tower (N/A)',
             'Gerudo Training Grounds', 'Hideout (N/A)', 'Ganons Castle']
    dungeon_is_mq = [1 if world.dungeon_mq.get(c) else 0 for c in codes]

    rom.write_int32(rom.sym('cfg_dungeon_info_enable'), 1)
    rom.write_int32(rom.sym('cfg_dungeon_info_mq_enable'), int(mq_enable))
    rom.write_int32(rom.sym('cfg_dungeon_info_mq_need_map'), int(mapcompass_keysanity))
    rom.write_int32(rom.sym('cfg_dungeon_info_reward_need_compass'), int(mapcompass_keysanity))
    rom.write_int32(rom.sym('cfg_dungeon_info_reward_need_altar'), int(not mapcompass_keysanity))
    rom.write_bytes(rom.sym('cfg_dungeon_rewards'), dungeon_rewards)
    rom.write_bytes(rom.sym('cfg_dungeon_is_mq'), dungeon_is_mq)
