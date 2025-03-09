# Parser

FileDataRelocator is the main class for shifting and extending scene and room files. Scene file entries are read from the rom's scene table connected with the DMA table. Room files are read as they are discovered in scene headers, also referencing the DMA table. FileDataRelocator is subclassed for both scenes and rooms in order to implement custom header parsers for each.

File data is stored using two concepts:

1. DataRecord - Raw byte data.
2. PointerRecord - Address of a pointer (NOT the pointer value) with its associated DataRecord. PointerRecords can be located in different files than the DataRecord they reference.

Parsing starts with creating a DataRecord for the current scene header. Everytime a pointer is encountered in a scene/room header, a PointerRecord is created linking the pointer location relative to the start of the file with the DataRecord the pointer is referencing. The PointerRecord is also added as a reference to the DataRecord according to the type of DataRecord in order to keep track of it when writing to back to the rom. PointerRecords are created recursively as needed, such as scene headers referencing alternate headers referencing scene collision headers referencing vertex/polygon/surface/camera/waterbox lists.

Unreferenced data in any file is added as an Unknown record type of fixed length after all other records have been identified and parsed. Unknown records should not be modified, moved, or removed.

DataRecords with a known type are deduplicated after parsing in order to save space. This may affect glitches.

DataRecords are subclassed into classes specific to a given scene command, such as SceneTransitionActorList. Class properties without a "_" prefix can be freely modified. When writing back to the rom during patching, attritbutes are automatically converted to whatever byte format they use. Record offsets are shifted as needed along with any related pointers. Finally, the scene table is rewritten to use the new file start and end addresses.

Note that MQ dungeon support changes the following record types:

- Scene Transition Actors
- Scene Paths
- Scene Collision polygons, surfaces, and camera info
- Room Objects
- Room Actors

Make sure to perform scene/room changes after MQ patching to avoid conflicts.

# References

Formatting info: https://wiki.cloudmodding.com/oot/Scenes_and_Rooms
As of 2024, scenes and rooms are not included in the decomp repo, but they can be extracted to human-readable C code and PNG texture files by building one of the supported versions. Scene and room files get placed in `extracted/<VERSION>/assets/scenes`, sorted in subfolders by area type and scene name. Rooms are placed in the same subfolder as their parent scene. See https://wiki.cloudmodding.com/oot/File_List/NTSC_1.0#File_1007_to_1495_.28Scenes_.26_Rooms.29 for a list of all the scene and room files relevant to rando.

# Scenes

- (0x18) Read scene setups/alternate headers
    - Read all headers starting with main header (setup 0)
    - Command may not exist (dungeons). Always process at least setup 0.
    - 18000000 xxyyyyyy
    - x = segment ID (should always be 2)
    - y = segment offset (ID 2 means offset from start of scene file)
    - always 8 byte aligned in vanilla

## Scene Setups

- (0x15) Read sound settings
    - Data only
        - 15xx0000 0000yyzz
        - x = settings config, max 0x11
        - y = night sfx to play (0x13 = use day music)
        - z = day music sequence (0x7F = use night sfx)
mr (0x04) Read room list
    - Contains number of rooms and points to segment address of room list
    - 04xx0000 yyzzzzzz
    - x = number of rooms (max 32)
    - y = segment ID (should always be 2)
    - z = segment offset (ID 2 means offset from start of scene file)
    - Room file list format
        - ssssssss eeeeeeee
        - s = start vrom address
        - e = end vrom address
    - Read each room file (see [Rooms](#Rooms))
mr (0x0E) Read transition actors
    - Contains number of transition actors and points to segment address of transition actor list
    - 0Exx0000 yyzzzzzz
    - x = number of transition actors (max 64)
    - y = segment ID (should always be 2)
    - z = segment offset (ID 2 means offset from start of scene file)
    - Transition actor list format
        - ffmmbbnn aaaaxxxx yyyyzzzz wwwwvvvv
        - f = Room to switch to when triggered from the front of the object (for doors, the front has the knob on the right)
        - m = How the camera reacts during the front transition
        - b = Room to switch to when triggered from the back of the object
        - n = How the camera reacts during the back transition
        - a = Actor Number (always en_door 0009, en_holl 0023, or en_door_shutter 002E)
        - x = Position along x-axis
        - y = Position along y-axis
        - z = Position along z-axis
        - w = Y rotation
        - v = Initialization variable
- (0x19) Read misc settings (camera and world map)
    - Data only
        - 19xx0000 000000yy
        - x = camera type
        - y = world map location
m (0x03) Read collision header
    - Points to collision header
    - 03000000 xxyyyyyy
    - x = segment ID (should always be 2)
    - y = segment offset (ID 2 means offset from start of scene file)
    - Collision header format
        - 0x00 - Vec3s - minimum vertex of bounding box
        - 0x06 - Vec3s - maximum vertex of bounding box
        - 0x0C - u16 - vertex count
        - 0x10 - Segment offset to vertex array (`Vec3s[]`)
            - 0x00 - s16 - x
            - 0x02 - s16 - y
            - 0x04 - s16 - z
        - 0x14 - u16 - polygon count
        - 0x18 - Segment offset to polygon array (`CollisionPoly[]`)
            - 0x00 - u16 - type
            - 0x02 - u16 - `vtxData[3]` (union with flags, see decomp)
            - 0x08 - Vec3s - normal
            - 0x0E - s16 - distance from origin along normal
        - 0x1C - Segment offset to surface type array (`SurfaceType[]`)
            - u32 - `data[2]`
        - 0x20 - Segment offset to camera data (`BgCamInfo[]`)
            - 0x00 - u16 - setting (see CameraSettingType enum)
            - 0x02 - s16 - count
            - 0x04 - Vec3s* - segment offset to specific camera position or list of positions
        - 0x24 - u16 - waterbox count
        - 0x28 - Segment offset to waterbox array (`WaterBox[]`)
            - 0x00 - s16 - xMin
            - 0x02 - s16 - ySurface
            - 0x04 - s16 - zMin
            - 0x06 - s16 - xLength
            - 0x08 - s16 - zLength
            - 0x0C - u32 - properties
- (0x06) Read entrance list
    - Points to entrance list
    - 06000000 xxyyyyyy
    - x = segment ID (should always be 2)
    - y = segment offset (ID 2 means offset from start of scene file)
    - Entrance list format
        - xxyy
        - x = u8 - spawn point number (see 0x00 command)
        - y = u8 - room number to load
r (0x07) Read special objects
    - Data only
        - 07xx0000 0000yyyy
        - x = Navi hint type
        - y = Keep object type
m (0x0D) Read paths
    - Points to path list
    - 0D000000 xxyyyyyy
    - x = segment ID (should always be 2)
    - y = segment offset (ID 2 means offset from start of scene file)
    - Path list format (`Path[]`)
        - 0x00 - s32 - vertex count
        - 0x04 - Segment offset to vertex array (`Vec3s[]`)
            - 0x00 - s16 - x
            - 0x02 - s16 - y
            - 0x04 - s16 - z
- (0x00) Read spawn points
    - Contains number of spawn points and points to segment address of list
    - 00xx0000 yyzzzzzz
    - x = number of spawn points
    - y = segment ID (should always be 2)
    - z = segment offset (ID 2 means offset from start of scene file)
    - Spawn point list format (`ActorEntry[]`)
        - aaaaxxxx yyyyzzzz ppppwwww rrrrvvvv
        - a = Actor number
        - x = Position on x-axis
        - y = Position on y-axis
        - z = Position on z-axis
        - p = Rotation around x-axis
        - w = Rotation around y-axis
        - r = Rotation around z-axis
        - v = initialization variable sent to actor
- (0x11) Read skybox settings
    - Data only
        - 11000000 xx0y0z00
        - x = skybox ID
        - y = sunny/cloudy flag
        - z = lighting setting control (time-controlled vs indoors)
- (0x13) Read exit list
    - Points to exit list
    - 13000000 xxyyyyyy
    - x = segment ID (should always be 2)
    - y = segment offset (ID 2 means offset from start of scene file)
    - Exit list format
        - xxxx - entrance table exit index
- (0x0F) Read lighting settings
    - Contains number of lighting settings and points to segment address of  list
    - 0Fxx0000 yyzzzzzz
    - x = number of lighting settings
    - y = segment ID (should always be 2)
    - z = segment offset (ID 2 means offset from start of scene file)
    - Lighting setting list format (`EnvLightSettings[]`)
        - 0x00 - u8 - `ambientColor[3]`
        - 0x03 - s8 - `light1Dir[3]`
        - 0x06 - u8 - `light1Color[3]`
        - 0x09 - s8 - `light2Dir[3]`
        - 0x0C - u8 - `light2Color[3]`
        - 0x0F - u8 - `fogColor[3]`
        - 0x12 - s16 - `blendRateAndFogNear`
        - 0x14 - s16 - `zFar`
- (0x17) Read cutscenes
    - Command applies to cutscenes on scene load?
    - Other cutscenes may be contained in scene file but NOT referenced in scene header, such as owl cutscenes in DMT and LH
    - Points to segment address of cutscene data
    - 17000000 xxyyyyyy
    - x = segment ID (should always be 2)
    - y = segment offset (ID 2 means offset from start of scene file)
    - Read each cutscene command (see [Cutscenes](#Cutscenes))
- Padding/unaccounted data
    - Decomp has some unknown unreferenced data in some of the extracted scene files.
    - Track bytes read from each scene file, then store remaining unread bytes to separate bytearrays so they can be preserved in relocated files.
    - If any data shifts, padding will need to change to maintain alignment, so tracking unreferenced data is likely overkill, but who knows with this game.

# Rooms

r (0x18) Read room setups/alternate headers
    - Read all headers starting with main header (setup 0)
    - Command may not exist (dungeons). Always process at least setup 0.
    - 18000000 xxyyyyyy
    - x = segment ID (should always be 3)
    - y = segment offset (ID 3 means offset from start of room file)
    - always 8 byte aligned in vanilla
- (0x16) Read sound settings
    - Data only
        - 16000000 000000xx
        - x = echo
- (0x08) Read room behavior
    - Data only
        - 08xx0000 0000yyzz
        - x = Sun Song toggle and others
        - y = Warp song toggle, invisible actor behavior
        - z = Link's idle animation/heat timer toggle
        - yyzz
            - 0100 = showInvisActors
            - 0400 = disableWarp
- (0x12) Read skybox settings
    - Data only
        - 12000000 xxyy0000
        - x = disable sky
        - y = disable sun/moon
- (0x10) Read time settings
    - Data only
        - 10000000 xxxxyy00
        - x = set time to specific value
        - y = time speed (default 0xA)
- (0x05) Read wind settings
    - Data only
        - 05000000 wwzzssff
        - w = wind direction west (xDir)
        - z = wind direction vertical (yDir)
        - s = wind direction south (zDir)
        - f = wind strength
- (0x0A) Read room mesh
    - Points to room mesh
    - 0A000000 xxyyyyyy
    - x = segment ID (should always be 3)
    - y = segment offset (ID 3 means offset from start of room file)
    - Room shape format
        - 3 types of meshes (00, 01, 02)
        - 16 byte aligned in vanilla for all variants (Normal, Cullable, ImageSingle, ImageMulti)
        - 00cc0000 ssssssss eeeeeeee
            - c = number of display list sets in list
            - s = segment offset to start of display lists
            - e - segment offset to end of display lists
            - xxxxxxxx yyyyyyyy - List format
                - x = if set, segment offset to DL for opaque geometry
                - y = if set, segment offset to DL for transparent geometry
                - DLs chain together. Always end with gsSPEndDisplayList / DF000000 00000000
                - Don't attempt to parse DLs completely. Only check for segment addresses to potentially shift / read and scan referenced bytes.
                - Op codes that have segment address arguments to shift (d):
                    - gsSPDisplayList / gsSPBranchList
                      0xDE / DEpp0000 dddddddd
                        - p = j vs jal
                    - gsSPVertex
                      0x01 / 010nn0aa dddddddd
                        - n = num vertices
                        - a = index to store vertices to
                    - gsSPBranchLessZraw
                      0xE1 / 0x04 / E1000000 dddddddd 04aaabbb zzzzzzzz
                        - a = vertex buffer index of vertex to test
                        - b = vertex buffer index of vertex to test
                        - z = Z value to test against
                    - gsSPMatrix
                      0xDA / DA3800pp dddddddd
                        - p = matrix control parameters
                    - gsDPSetTextureImage
                      0xFD / FD__0www dddddddd __ -> fffs s000
                        - f = texture format
                        - s = texture size in bits
                        - w = texture width
                    - gsDPSetDepthImage
                      0xFE / FE000000 dddddddd
                        - f = texture format
                        - s = texture size in bits
                        - w = texture width
                    - gsDPSetColorImage
                      0xFF / FF__0www dddddddd __ -> fffs s000
                        - f = texture format
                        - s = texture size in bits
                        - w = texture width
mr (0x0B) Read object list
    - Points to object list
    - 0Bxx0000 yyzzzzzz (max 15)
    - x = number of objects in list
    - y = segment ID (should always be 3)
    - z = segment offset (ID 3 means offset from start of room file)
    - Object list format
        - oooo = object ID
    - 4 byte aligned in vanilla
mr (0x01) Read actor list
    - Points to actor list
    - 01xx0000 yyzzzzzz
    - x = number of actors in list
    - y = segment ID (should always be 3)
    - z = segment offset (ID 3 means offset from start of room file)
    - Actor list format (`ActorEntry[]`)
        - aaaaxxxx yyyyzzzz ppppwwww rrrrvvvv
        - a = Actor number
        - x = Position on x-axis
        - y = Position on y-axis
        - z = Position on z-axis
        - p = Rotation around x-axis
        - w = Rotation around y-axis
        - r = Rotation around z-axis
        - v = initialization variable sent to actor
    - 4 byte aligned in vanilla

# Gold Skulltulas

Param `0xA000` makes them spawn at night, `0x8000` will always spawn.
Always set for overworld scenes with changing time.
Night-only room setups may also have this set for en_sw instances.

01F12000
03470F20

# Cutscenes

Safe to use CS_END_OF_SCRIPT() as terminator and just read in all the raw bytes if we're feeling lazy. Decomp doesn't show any commands past it for any cutscene despite cloudmodding suggesting that there may be commands past it. Command bytes are 0xFFFFFFFF. Note that this assumption is an artifact of how ZAPD parses the cutscenes and may not be accurate!!

Store these in a way that Cutscenes.py can index them for its changes.

Cutscene commands have variable lengths. Below is how to determine command length by command ID, sourced from ZAPD's `ZCutscene.cpp` and `CutsceneOoT_Commands.cpp` files.

CS_HEADER always at start of cutscene commands. No explicit ID.
    numCommands: s32
    endFrame: s32
    total size = 0x08

CS_END always at end of cutscene commands. 0xFFFFFFFF ID plus 0x04 bytes padding.
    total size = 0x08

CutsceneOoTCommand_ActorCue
    CS_CMD_PLAYER_CUE
    CS_CMD_ACTOR_CUE_1_0
    CS_CMD_ACTOR_CUE_0_0
    CS_CMD_ACTOR_CUE_1_1
    CS_CMD_ACTOR_CUE_0_1
    CS_CMD_ACTOR_CUE_0_2
    CS_CMD_ACTOR_CUE_0_3
    CS_CMD_ACTOR_CUE_1_2
    CS_CMD_ACTOR_CUE_2_0
    CS_CMD_ACTOR_CUE_3_0
    CS_CMD_ACTOR_CUE_4_0
    CS_CMD_ACTOR_CUE_6_0
    CS_CMD_ACTOR_CUE_0_4
    CS_CMD_ACTOR_CUE_1_3
    CS_CMD_ACTOR_CUE_2_1
    CS_CMD_ACTOR_CUE_3_1
    CS_CMD_ACTOR_CUE_4_1
    CS_CMD_ACTOR_CUE_0_5
    CS_CMD_ACTOR_CUE_1_4
    CS_CMD_ACTOR_CUE_2_2
    CS_CMD_ACTOR_CUE_3_2
    CS_CMD_ACTOR_CUE_4_2
    CS_CMD_ACTOR_CUE_5_0
    CS_CMD_ACTOR_CUE_0_6
    CS_CMD_ACTOR_CUE_4_3
    CS_CMD_ACTOR_CUE_1_5
    CS_CMD_ACTOR_CUE_7_0
    CS_CMD_ACTOR_CUE_2_3
    CS_CMD_ACTOR_CUE_3_3
    CS_CMD_ACTOR_CUE_6_1
    CS_CMD_ACTOR_CUE_3_4
    CS_CMD_ACTOR_CUE_4_4
    CS_CMD_ACTOR_CUE_5_1
    CS_CMD_ACTOR_CUE_6_2
    CS_CMD_ACTOR_CUE_6_3
    CS_CMD_ACTOR_CUE_7_1
    CS_CMD_ACTOR_CUE_8_0
    CS_CMD_ACTOR_CUE_3_5
    CS_CMD_ACTOR_CUE_1_6
    CS_CMD_ACTOR_CUE_3_6
    CS_CMD_ACTOR_CUE_3_7
    CS_CMD_ACTOR_CUE_2_4
    CS_CMD_ACTOR_CUE_1_7
    CS_CMD_ACTOR_CUE_2_5
    CS_CMD_ACTOR_CUE_1_8
    CS_CMD_ACTOR_CUE_2_6
    CS_CMD_ACTOR_CUE_2_7
    CS_CMD_ACTOR_CUE_3_8
    CS_CMD_ACTOR_CUE_0_7
    CS_CMD_ACTOR_CUE_5_2
    CS_CMD_ACTOR_CUE_1_9
    CS_CMD_ACTOR_CUE_4_5
    CS_CMD_ACTOR_CUE_1_10
    CS_CMD_ACTOR_CUE_2_8
    CS_CMD_ACTOR_CUE_3_9
    CS_CMD_ACTOR_CUE_4_6
    CS_CMD_ACTOR_CUE_5_3
    CS_CMD_ACTOR_CUE_0_8
    CS_CMD_ACTOR_CUE_6_4
    CS_CMD_ACTOR_CUE_7_2
    CS_CMD_ACTOR_CUE_5_4
    CS_CMD_ACTOR_CUE_0_9
    CS_CMD_ACTOR_CUE_1_11
    CS_CMD_ACTOR_CUE_0_10
    CS_CMD_ACTOR_CUE_2_9
    CS_CMD_ACTOR_CUE_0_11
    CS_CMD_ACTOR_CUE_3_10
    CS_CMD_ACTOR_CUE_0_12
    CS_CMD_ACTOR_CUE_7_3
    CS_CMD_ACTOR_CUE_7_4
    CS_CMD_ACTOR_CUE_6_5
    CS_CMD_ACTOR_CUE_1_12
    CS_CMD_ACTOR_CUE_2_10
    CS_CMD_ACTOR_CUE_1_13
    CS_CMD_ACTOR_CUE_0_13
    CS_CMD_ACTOR_CUE_1_14
    CS_CMD_ACTOR_CUE_2_11
    CS_CMD_ACTOR_CUE_0_14
    CS_CMD_ACTOR_CUE_1_15
    CS_CMD_ACTOR_CUE_2_12
    CS_CMD_ACTOR_CUE_3_11
    CS_CMD_ACTOR_CUE_4_7
    CS_CMD_ACTOR_CUE_5_5
    CS_CMD_ACTOR_CUE_6_6
    CS_CMD_ACTOR_CUE_1_16
    CS_CMD_ACTOR_CUE_2_13
    CS_CMD_ACTOR_CUE_3_12
    CS_CMD_ACTOR_CUE_7_5
    CS_CMD_ACTOR_CUE_4_8
    CS_CMD_ACTOR_CUE_5_6
    CS_CMD_ACTOR_CUE_6_7
    CS_CMD_ACTOR_CUE_0_15
    CS_CMD_ACTOR_CUE_0_16
    CS_CMD_ACTOR_CUE_1_17
    CS_CMD_ACTOR_CUE_7_6
    CS_CMD_ACTOR_CUE_9_0
    CS_CMD_ACTOR_CUE_0_17
    Size calculations:
        numEntries: u32
        list of CutsceneOoTSubCommandEntry_ActorCue
            0x06 padding
            rot: Vec3s(u16)
            startPos: Vec3s(s32)
            endPos: Vec3s(s32)
            normal: Vec3s(f32)
            total size = 0x30
        total size = 0x08 + 0x30 * entries
CutsceneOoTCommand_GenericCmd
    CS_CMD_MISC
    CS_CMD_LIGHT_SETTING
    CS_CMD_START_SEQ
    CS_CMD_STOP_SEQ
    CS_CMD_FADE_OUT_SEQ
        numEntries: u32
        list of CutsceneOoTSubCommandEntry_GenericCmd
            word0: u32
            word1: u32
            unused1: u32
            unused2: u32
            unused3: u32
            unused4: u32
            unused5: u32
            unused6: u32
            unused7: u32
            unused8: u32
            unused9: u32
            unused10: u32
            total size = 0x30
        total size = 0x08 + 0x30 * entries
CutsceneOoTCommand_GenericCameraCmd
    CS_CMD_CAM_EYE_SPLINE
    CS_CMD_CAM_AT_SPLINE
    CS_CMD_CAM_EYE_SPLINE_REL_TO_PLAYER
    CS_CMD_CAM_AT_SPLINE_REL_TO_PLAYER
    Invalid command ID not matching anything else
    Size calculations:
        base: u16
        startFrame: u16
        endFrame: u16
        unused: u16
        list of CutsceneOoTCommand_CameraPoint
            continueFlag: s8
            cameraRoll: s8
            nextPointFrame: s16
            viewAngle: f32
            pos: Vec3s
            unused: s16
            total size = 0x10
            continueFlag == -1 indicates end of list
        total size = 0x0C + 0x10 * camera points
CutsceneOoTCommand_Rumble
    CS_CMD_RUMBLE_CONTROLLER
    Size calculations:
        numEntries: u32
        list of CutsceneOoTSubCommandEntry_Rumble
            0x06 padding
            sourceStrength: u8
            duration: u8
            decreaseRate: u8
            unk_09: u8
            0x01 padding
            unk_0A: u8
            0x01 padding
            total size = 0x0C
        total size = 0x08 + 0x0C * entries
CutsceneOoTCommand_Text
    CS_CMD_TEXT
    Size calculations:
        numEntries: u32
        list of CutsceneOoTSubCommandEntry_Text
            0x06 padding
            type: u16
            textId1: u16
            textId2: u16
        total size = 0x08 + 0x0C * entries
CutsceneOoTCommand_Transition
    CS_CMD_TRANSITION
    Size calculations:
        0x04 padding
        base: u16
        startFrame: u16
        endFrame: u16
        0x02 padding
        total size = 0x10
CutsceneCommand_Time
    CS_CMD_TIME
    Size calculations:
        numEntries: u32
        list of CutsceneSubCommandEntry_SetTime
            0x06 padding
            hour: u8
            minute: u8
            0x04 padding
        total size = 0x08 + 0x0C * entries
CutsceneOoTCommand_Destination
    CS_CMD_DESTINATION
    Size calculations:
        0x04 padding
        base: u16
        startFrame: u16
        endFrame: u16
        unknown: u16
        total size = 0x10
Null pointers
    CS_CMD_CAM_EYE
    CS_CMD_CAM_AT
    Size calculations:
        numEntries: u32
        list of CutsceneSubCommandEntry
            base: u16
            startFrame: u16
            endFrame: u16
            pad: u16
            unprocessed/not implemented
            does not appear to be in any 1.0 assets, MM only?
            total size = 0x08
        total size = 0x08 + 0x08 * entries

Externally referenced cutscenes:
    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/dungeons/bdan.xml
      3,10:         <Cutscene Name="gJabuJabuIntroCs" Offset="0x155E0"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/dungeons/ddan.xml
      16,10:         <Cutscene Name="gDcOpeningCs" Offset="0x14F80"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/dungeons/ganontika.xml
      3,10:         <Cutscene Name="gForestTrialSageCs" Offset="0x19ED0"/>
      4,10:         <Cutscene Name="gWaterTrialSageCs" Offset="0x1A8D0"/>
      5,10:         <Cutscene Name="gShadowTrialSageCs" Offset="0x1B2A0"/>
      6,10:         <Cutscene Name="gFireTrialSageCs" Offset="0x1BC70"/>
      7,10:         <Cutscene Name="gLightTrialSageCs" Offset="0x1C6A0"/>
      8,10:         <Cutscene Name="gSpiritTrialSageCs" Offset="0x1D070"/>
      10,10:         <Cutscene Name="gTowerBarrierCs" Offset="0x1DA40"/>
      12,10:         <Cutscene Name="gLightBarrierCs" Offset="0x1DF80"/>
      13,10:         <Cutscene Name="gFireBarrierCs" Offset="0x1E3D0"/>
      14,10:         <Cutscene Name="gForestBarrierCs" Offset="0x1E780"/>
      15,10:         <Cutscene Name="gSpiritBarrierCs" Offset="0x1EB30"/>
      16,10:         <Cutscene Name="gWaterBarrierCs" Offset="0x1EF60"/>
      17,10:         <Cutscene Name="gShadowBarrierCs" Offset="0x21370"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/dungeons/ice_doukutu.xml
      3,10:         <Cutscene Name="gIceCavernSerenadeCs" Offset="0x250"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/dungeons/jyasinboss.xml
      3,10:         <Cutscene Name="gSpiritBossNabooruKnuckleIntroCs" Offset="0x2BB0"/>
      4,10:         <Cutscene Name="gSpiritBossNabooruKnuckleDefeatCs" Offset="0x3F80"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/dungeons/ydan.xml
      3,10:         <Cutscene Name="gDekuTreeIntroCs" Offset="0xB640"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/indoors/daiyousei_izumi.xml
      3,10:         <Cutscene Name="gGreatFairyMagicCs" Offset="0x0130"/>
      4,10:         <Cutscene Name="gGreatFairyDoubleMagicCs" Offset="0x13E0"/>
      5,10:         <Cutscene Name="gGreatFairyDoubleDefenseCs" Offset="0x25D0"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/indoors/hakasitarelay.xml
      4,10:         <Cutscene Name="gSongOfStormsCs" Offset="0xE080"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/indoors/nakaniwa.xml
      3,10:         <Cutscene Name="gZeldasCourtyardGanonCs" Offset="0x104"/>
      4,10:         <Cutscene Name="gZeldasCourtyardWindowCs" Offset="0x444"/>
      5,10:         <Cutscene Name="gZeldasCourtyardMeetCs" Offset="0x3994"/>
      6,10:         <Cutscene Name="gZeldasCourtyardLullabyCs" Offset="0x2524"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/indoors/tokinoma.xml
      3,10:         <Cutscene  Name="gTempleOfTimeFirstAdultCs" Offset="0x46F0"/>
      4,10:         <Cutscene  Name="gTempleOfTimePreludeCs" Offset="0x6D20"/>
      5,10:         <Cutscene Name="gTempleOfTimeIntroCs" Offset="0xCE00"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/indoors/yousei_izumi_yoko.xml
      3,10:         <Cutscene Name="gGreatFairyFaroresWindCs" Offset="0x0160"/>
      4,10:         <Cutscene Name="gGreatFairyDinsFireCs" Offset="0x1020"/>
      5,10:         <Cutscene Name="gGreatFairyNayrusLoveCs" Offset="0x1F40"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/misc/hakaana_ouke.xml
      3,10:         <Cutscene Name="gSunSongGraveSunSongTeachCs" Offset="0x24A0"/>
      4,10:         <Cutscene Name="gSunSongGraveSunSongTeachPart2Cs" Offset="0x28E0"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/overworld/ganon_tou.xml
      3,10:         <Cutscene Name="gRainbowBridgeCs" Offset="0x2640"/>
      4,10:         <Cutscene Name="gGanonsCastleIntroCs" Offset="0x4280"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/overworld/spot00.xml
      3,10:         <Cutscene Name="gHyruleFieldGetOoTCs" Offset="0xBB80"/>
      4,10:         <Cutscene Name="gHyruleFieldZeldaSongOfTimeCs" Offset="0xF870"/>
      5,10:         <Cutscene Name="gHyruleFieldEastEponaJumpCs" Offset="0xFF00"/>
      6,10:         <Cutscene Name="gHyruleFieldIntroCs" Offset="0x13AA0"/>
      7,10:         <Cutscene Name="gHyruleFieldSouthEponaJumpCs" Offset="0xF9E0"/>
      8,10:         <Cutscene Name="gHyruleFieldWestEponaJumpCs" Offset="0x10550"/>
      9,10:         <Cutscene Name="gHyruleFieldGateEponaJumpCs" Offset="0x10B30"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/overworld/spot01.xml
      4,10:         <Cutscene Name="gKakarikoVillageIntroCs" Offset="0xA540"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/overworld/spot02.xml
      5,10:         <Cutscene Name="spot02_scene_Cs_003C80" Offset="0x3C80"/>
      7,10:         <Cutscene Name="spot02_scene_Cs_005020" Offset="0x5020"/>
      8,10:         <Cutscene Name="gGraveyardIntroCs" Offset="0x70C0"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/overworld/spot04.xml
      5,10:         <Cutscene Name="gKokiriForestDekuSproutCs" Offset="0xC9D0"/>
      6,10:         <Cutscene Name="gSpot04Cs_10E20" Offset="0x10E20"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/overworld/spot05.xml
      3,10:         <Cutscene Name="gMinuetCs" Offset="0x3F80"/>
      5,10:         <Cutscene Name="spot05_scene_Cs_005730" Offset="0x5730"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/overworld/spot06.xml
      3,10:         <Cutscene Name="gLakeHyliaFireArrowsCS" Offset="0x7020"/>
      4,10:         <Cutscene Name="gLakeHyliaOwlCs" Offset="0x1B0C0"/>
      6,10:         <Cutscene Name="gLakeHyliaIntroCs" Offset="0x7A30"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/overworld/spot07.xml
      4,10:         <Cutscene Name="gZorasDomainIntroCs" Offset="0x3D70"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/overworld/spot08.xml
      3,10:         <Cutscene Name="gZorasFountainIntroCs" Offset="0x4A80"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/overworld/spot09.xml
      3,10:         <Cutscene Name="gGerudoValleyBridgeJumpFieldFortressCs" Offset="0x2AC0"/>
      4,10:         <Cutscene Name="gGerudoValleyBridgeJumpFortressToFieldCs" Offset="0x230"/>
      5,10:         <Cutscene Name="gGerudoValleyIntroCs" Offset="0x31E0"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/overworld/spot11.xml
      3,10:         <Cutscene Name="gDesertColossusIntroCs" Offset="0x7990"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/overworld/spot12.xml
      3,10:         <Cutscene Name="gGerudoFortressFirstCaptureCs" Offset="0x55C0"/>
      4,10:         <Cutscene Name="gGerudoFortressIntroCs" Offset="0x6490"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/overworld/spot15.xml
      3,10:         <Cutscene Name="gHyruleCastleIntroCs" Offset="0x3F40"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/overworld/spot16.xml
      3,10:         <Cutscene Name="gDMTOwlCs" Offset="0x1E6A0"/>
      4,10:         <Cutscene Name="gDMTIntroCs" Offset="0x7EA0"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/overworld/spot17.xml
      3,10:         <Cutscene Name="gDeathMountainCraterBoleroCs" Offset="0x45D0"/>
      4,10:         <Cutscene Name="gDeathMountainCraterIntroCs" Offset="0x76D0"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/overworld/spot18.xml
      3,10:         <Cutscene Name="gGoronCityDaruniaCorrectCs" Offset="0x59E0"/>
      4,10:         <Cutscene Name="gGoronCityDarunia01Cs" Offset="0x6930"/>
      5,10:         <Cutscene Name="gGoronCityDaruniaWrongCs" Offset="0x7DE0"/>
      6,10:         <Cutscene Name="gGoronCityIntroCs" Offset="0x8400"/>

    /Users/mracsys/git/OoT-Randomizer-Fork/data/scenes/overworld/spot20.xml
      3,10:         <Cutscene Name="gLonLonRanchIntroCs" Offset="0x5B70"/>


Addresses:
```python
# z_demo tables
ENTRANCE_CUTSCENE_TABLE_ADDRESS = 0xB65C64
UNKNOWN_LIST_CUTSCENES = 0xB65D74 # does not include NULL first entry

# z_demo_kekkai list
SAGE_CUTSCENES = 0xECF8EC

external_cutscene_pointer_locations = {
    # z_demo
    'bdan': [
        (1, [ # gJabuJabuIntroCs
            ENTRANCE_CUTSCENE_TABLE_ADDRESS + (17 * 0x8) + 0x4,
            UNKNOWN_LIST_CUTSCENES + 1 * 0x4,
        ], [], []),
    ],
    # z_demo, z_bg_breakwall
    'ddan': [
        (0, [ # gDcOpeningCs
            UNKNOWN_LIST_CUTSCENES + 2 * 0x4,
        ], [
            0xC9EDAE # lui     a1, 0x0201
        ], [
            0xC9EDB2 # addiu   a1, a1, 0x4F80
        ]),
    ],
    # z_demo, z_demo_kekkai
    'ganontika': [
        (0, [SAGE_CUTSCENES + 6 * 0x4], [], []), # gForestTrialSageCs
        (1, [SAGE_CUTSCENES + 1 * 0x4], [], []), # gWaterTrialSageCs
        (2, [SAGE_CUTSCENES + 4 * 0x4], [], []), # gShadowTrialSageCs
        (3, [SAGE_CUTSCENES + 3 * 0x4], [], []), # gFireTrialSageCs
        (4, [SAGE_CUTSCENES + 2 * 0x4], [], []), # gLightTrialSageCs
        (5, [SAGE_CUTSCENES + 5 * 0x4], [], []), # gSpiritTrialSageCs
        (6, [ # gTowerBarrierCs
            UNKNOWN_LIST_CUTSCENES + 5 * 0x4,
        ], [
            0xACA97E # lui     v0, 0x0202
        ], [
            0xACA982 # addiu   v0, v0, 0xDA40
        ]),
        (7, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (28 * 0x8) + 0x4], [], []), # gLightBarrierCs
        (8, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (27 * 0x8) + 0x4], [], []), # gFireBarrierCs
        (9, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (24 * 0x8) + 0x4], [], []), # gForestBarrierCs
        (10, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (29 * 0x8) + 0x4], [], []), # gSpiritBarrierCs
        (11, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (25 * 0x8) + 0x4], [], []), # gWaterBarrierCs
        (12, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (26 * 0x8) + 0x4], [], []), # gShadowBarrierCs
    ],
    # z_demo, z_en_xc
    'ice_doukutu': [
        (0, [ # gIceCavernSerenadeCs
            UNKNOWN_LIST_CUTSCENES + 4 * 0x4,
        ], [
            0xC7BD46 # lui     a1, 0x0200
        ], [
            0xC7BD4E # addiu   a1, a1, 0x0250
        ]),
    ],
    # z_demo, z_en_ik
    'jyasinboss': [
        (0, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (30 * 0x8) + 0x4], [], []), # gSpiritBossNabooruKnuckleIntroCs
        (1, [ # gSpiritBossNabooruKnuckleDefeatCs
            UNKNOWN_LIST_CUTSCENES + 3 * 0x4,
        ], [
            0xDED5C2 # lui     a1, 0x0200
        ], [
            0xDED5D6 # addiu   a1, a1, 0x3F80
        ]),
    ],
    # z_demo, z_bg_breakwall
    'ydan': [
        (1, [ # gDekuTreeIntroCs
            ENTRANCE_CUTSCENE_TABLE_ADDRESS + (7 * 0x8) + 0x4,
            UNKNOWN_LIST_CUTSCENES + 0 * 0x4,
        ], [], []),
    ],
    # z_bg_dy_yoseizo
    'daiyousei_izumi': [
        (0, [], [ # gGreatFairyMagicCs
            0xC89A0A # lui     v0, 0x0200
        ], [
            0xC89A0E # addiu   v0, v0, 0x0130
        ]),
        (1, [], [ # gGreatFairyDoubleMagicCs
            0xC89A4E # lui     v0, 0x0200
        ], [
            0xC89A52 # addiu   v0, v0, 0x13E0
        ]),
        (2, [], [ # gGreatFairyDoubleDefenseCs
            0xC89A92 # lui     v0, 0x0200
        ], [
            0xC89A96 # addiu   v0, v0, 0x25D0
        ]),
    ],
    # z_en_fu
    'hakasitarelay': [
        (0, [], [ # gSongOfStormsCs
            0xE42A4E # lui     v0, 0x0201
        ], [
            0xE42A5A # addiu   v0, v0, 0xE080
        ]),
    ],
    # z_en_zl4, z_demo_im
    'nakaniwa': [
        (0, [], [ # gZeldasCourtyardGanonCs
            0xEFE0FA # lui     v0, 0x0200
        ], [
            0xEFE0FE # addiu   v0, v0, 0x0104
        ]),
        (1, [], [ # gZeldasCourtyardWindowCs
            0xEFE09A # lui     v0, 0x0200
        ], [
            0xEFE09E # addiu   v0, v0, 0x0444
        ]),
        (3, [], [ # gZeldasCourtyardLullabyCs
            0xD12E72 # lui     v0, 0x0200
        ], [
            0xD12E76 # addiu   v0, v0, 0x2524
        ]),
        (5, [], [ # gZeldasCourtyardMeetCs
            0xEFCEF2 # lui     v0, 0x0200
        ], [
            0xEFCEF6 # addiu   v0, v0, 0x3994
        ]),
    ],
    # z_demo, z_en_xc
    'tokinoma': [
        (4, [], [ # gTempleOfTimeFirstAdultCs
            0xC8056E # lui     v0, 0x0200
        ], [
            0xC80572 # addiu   v0, v0, 0x46F0
        ]),
        (6, [], [ # gTempleOfTimePreludeCs
            0xC8060E # lui     v0, 0x0200
        ], [
            0xC80612 # addiu   v0, v0, 0x13E0
        ]),
        (11, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (6 * 0x8) + 0x4], [], []), # gTempleOfTimeIntroCs
    ],
    # z_bg_dy_yoseizo
    'yousei_izumi_yoko': [
        (0, [], [ # gGreatFairyFaroresWindCs
            0xC8991A # lui     v0, 0x0200
        ], [
            0xC8991E # addiu   v0, v0, 0x0160
        ]),
        (1, [], [ # gGreatFairyDinsFireCs
            0xC8995E # lui     v0, 0x0200
        ], [
            0xC89962 # addiu   v0, v0, 0x1020
        ]),
        (2, [], [ # gGreatFairyNayrusLoveCs
            0xC899A2 # lui     v0, 0x0200
        ], [
            0xC899A6 # addiu   v0, v0, 0x1F40
        ]),
    ],
    # z_demo, z_en_okarina_tag
    'hakaana_ouke': [
        (0, [], [ # gSunSongGraveSunSongTeachCs
            0xE09F6E # lui     v0, 0x0200
        ], [
            0xE09F72 # addiu   v0, v0, 0x24A0
        ]),
        (1, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (23 * 0x8) + 0x4], [], []), # gSunSongGraveSunSongTeachPart2Cs
    ],
    # z_demo, z_bg_giyo_bridge
    'ganon_tou': [
        (0, [], [ # gRainbowBridgeCs
            0xE2B502 # lui     v0, 0x0200
        ], [
            0xE2B506 # addiu   v0, v0, 0x2640
        ]),
        (1, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (22 * 0x8) + 0x4], [], []), # gGanonsCastleIntroCs
    ],
    # z_demo, z_item_ocarina
    'spot00': [
        (3, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (12 * 0x8) + 0x4], [], []), # gHyruleFieldGetOoTCs
        (9, [], [ # gHyruleFieldZeldaSongOfTimeCs
            0xDB529A # lui     v0, 0x0201
        ], [
            0xDB529E # addiu   v0, v0, 0xF870
        ]),
        (11, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (9 * 0x8) + 0x4], [], []), # gHyruleFieldEastEponaJumpCs
        (15, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (0 * 0x8) + 0x4], [], []), # gHyruleFieldIntroCs
        (10, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (8 * 0x8) + 0x4], [], []), # gHyruleFieldSouthEponaJumpCs
        (12, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (10 * 0x8) + 0x4], [], []), # gHyruleFieldWestEponaJumpCs
        (13, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (11 * 0x8) + 0x4], [], []), # gHyruleFieldGateEponaJumpCs
    ],
    # z_demo
    'spot01': [
        (5, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (2 * 0x8) + 0x4], [], []), # gKakarikoVillageIntroCs
    ],
    # z_demo, z_en_okarina_tag
    'spot02': [
        (0, [], [ # spot02_scene_Cs_003C80
            0xE09D42 # lui     v0, 0x0200
        ], [
            0xE09D46 # addiu   v0, v0, 0x3C80
        ]),
        (2, [], [ # spot02_scene_Cs_005020
            0xE09D32 # lui     v0, 0x0200
        ], [
            0xE09D36 # addiu   v0, v0, 0x5020
        ]),
        (3, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (18 * 0x8) + 0x4], [], []), # gGraveyardIntroCs
    ],
    # z_demo, z_en_sa
    'spot04': [
        (9, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (33 * 0x8) + 0x4], [], []), # gKokiriForestDekuSproutCs
        (10, [], [ # gSpot04Cs_10E20
            0xE297AE # lui     v0, 0x0201
        ], [
            0xE297B6 # addiu   v0, v0, 0x0E20
        ]),
    ],
    # z_en_xc, z_en_sa
    'spot05': [
        (0, [], [ # gMinuetCs
            0xC7BA4A # lui     v0, 0x0200
        ], [
            0xC7BA4E # addiu   v0, v0, 0x3F80
        ]),
        (1, [], [ # spot05_scene_Cs_005730
            0xE29D5E # lui     v0, 0x0200
        ], [
            0xE29D62 # addiu   v0, v0, 0x5730
        ]),
    ],
    # z_demo, z_shot_sun, z_en_owl
    'spot06': [
        (2, [], [ # gLakeHyliaFireArrowsCS
            0xE9E222 # lui     v1, 0x0200
        ], [
            0xE9E226 # addiu   v1, v1, 0x7020
        ]),
        (3, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (13 * 0x8) + 0x4], [], []), # gLakeHyliaIntroCs
        (4, [], [ # gLakeHyliaOwlCs
            0xE31302 # lui     v0, 0x0202
        ], [
            0xE31306 # addiu   v0, v0, 0xB0C0
        ]),
    ],
    # z_demo
    'spot07': [
        (1, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (3 * 0x8) + 0x4], [], []), # gZorasDomainIntroCs
    ],
    # z_demo
    'spot08': [
        (3, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (19 * 0x8) + 0x4], [], []), # gZorasFountainIntroCs
    ],
    # z_demo, z_en_horse
    'spot09': [
        (4, [], [ # gGerudoValleyBridgeJumpFieldFortressCs
            0xC1CCC6 # lui     v0, 0x0200
        ], [
            0xC1CCCA # addiu   v0, v0, 0x2AC0
        ]),
        (0, [], [ # gGerudoValleyBridgeJumpFortressToFieldCs
            0xC1CD12 # lui     v0, 0x0200
        ], [
            0xC1CD16 # addiu   v0, v0, 0x0230
        ]),
        (5, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (14 * 0x8) + 0x4], [], []), # gGerudoValleyIntroCs
    ],
    # z_demo
    'spot11': [
        (2, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (20 * 0x8) + 0x4], [], []), # gDesertColossusIntroCs
    ],
    # z_demo
    'spot12': [
        (2, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (31 * 0x8) + 0x4], [], []), # gGerudoFortressFirstCaptureCs
        (3, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (15 * 0x8) + 0x4], [], []), # gGerudoFortressIntroCs
    ],
    # z_demo
    'spot15': [
        (0, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (4 * 0x8) + 0x4], [], []), # gHyruleCastleIntroCs
    ],
    # z_demo, z_en_owl
    'spot16': [
        (6, [], [ # gDMTOwlCs
            0xE31342 # lui     v0, 0x0202
        ], [
            0xE31346 # addiu   v0, v0, 0xE6A0
        ]),
        (5, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (1 * 0x8) + 0x4], [], []), # gDMTIntroCs
    ],
    # z_demo, z_en_xc
    'spot17': [
        (0, [], [ # gDeathMountainCraterBoleroCs
            0xC7BBFE # lui     v0, 0x0200
        ], [
            0xC7BC02 # addiu   v0, v0, 0x45D0
        ]),
        (2, [ # gDeathMountainCraterIntroCs
            ENTRANCE_CUTSCENE_TABLE_ADDRESS + (21 * 0x8) + 0x4,
            ENTRANCE_CUTSCENE_TABLE_ADDRESS + (32 * 0x8) + 0x4,
        ], [], []),
    ],
    # z_demo, z_en_du
    'spot18': [
        (0, [], [ # gGoronCityDaruniaCorrectCs
            0xCF14DA # lui     v0, 0x0200
        ], [
            0xCF14DE # addiu   v0, v0, 0x59E0
        ]),
        (1, [], [ # gGoronCityDarunia01Cs
            0xCF11C6 # lui     v0, 0x0200
        ], [
            0xCF11D6 # addiu   v0, v0, 0x6930
        ]),
        (3, [], [ # gGoronCityDaruniaWrongCs
            0xCF1436 # lui     v0, 0x0200
        ], [
            0xCF143A # addiu   v0, v0, 0x7DE0
        ]),
        (4, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (21 * 0x8) + 0x4,], [], []), # gGoronCityIntroCs
    ],
    # z_demo
    'spot20': [
        (8, [ENTRANCE_CUTSCENE_TABLE_ADDRESS + (16 * 0x8) + 0x4], [], []), # gLonLonRanchIntroCs
    ],
}
```

# Rando Patches to Test with New System

- [?] Cutscene Patching
    - [?] Cutscenes
    - [?] wondertalk2 actor moves
- [?] Other Patches
    - [X] Duplicate Bazaar room for Kakariko
    - [X] Move Sheik from pedastal in ToT
    - [?] Ice Cavern alcove camera (duplicated in two spots in Patches.py)
    - [X] Fire Temple boss loop unlocked door without keysanity
    - [X] Non-MQ Water Temple door always unlocked
    - [X] Graveyard ledge grabs
    - [X] Owl removals
    - [X] Jabu octorok position
    - [X] Forest/Fire Temple switch heights
    - [X] Kakariko carpenter starting position
    - [X] Vanilla DC gossip stone fairy flag
    - [X] Colossus Fairy entrance "...???" text
    - [X] Forbid Sun's song in a bunch of cutscenes
    - [X] Move Fado for adult trade shuffle
    - [X] Spirit Shortcut actor tweaks
    - [X] Gerudo Fortress gate guard reposition
    - [X] Skip child stealth crawlspace exit
    - [?] Silver rupee shuffle MQ DC/Spirit temp->permanent flags
    - [X] Well ladder rupee reposition
    - [X] Shadow Temple redead shared flags for silver rupee shuffle
    - [X] Song shuffle cutscene text boxes
    - [X] Song shuffle location addresses
    - [X] Shopsanity shop item objects in room headers
    - [?] Cow shuffle repositions
        - [X] Stable
        - [X] Tower
        - [?] Shuffled item actor params in set_cow_id_data
    - [X] CSMC repositions
        - [X] Vanilla Ganons Castle Light Trial
        - [X] Vanilla Spirit Temple compass chest
        - [X] Silver Gauntlet chest in glitched logic
    - [X] Dead Hand spawns in vanilla Shadow/Well
    - [X] Broken drops vanilla Spirit deku shield in anubis room
    - [X] TCG shuffle temp flags to permanent/keysy
    - [X] Remove "entrance blockers"
    - [?] Scrub shuffle actor params in set_deku_salesman_data
    - [X] Jabu stone actor
    - [X] Keysy dungeon/boss doors
    - [?] Ganons Tower first BK door unlock for pot shuffle
- [?] Entrance Shuffle
    - [?] Generate/write exit list for each scene
    - [?] Jabu boss exit coordinates
    - [?] Water Temple boss exit room number
    - [?] Redirect LLR exits to main exit for OW shuffle
    - [?] Redirect ZR<->Field exits to land from water
    - [?] Spirit temp flag purge on entry through front door
    - [?] Grotto actor data changes in set_grotto_shuffle_data
- [ ] MQ Patching
    - [ ] All rooms can be entered from all entrances
    - [ ] Ice Cavern scene header patch from old system
    - [ ] MQ Spirit Temple room 6 new alternate header
- [?] ASM/C patches
    - [?] 0x26c10e3 - generic grotto ACTOR_EN_GS actor params 0x3818 -> 0x38FF
