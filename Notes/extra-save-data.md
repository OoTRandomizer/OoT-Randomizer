This file documents parts of the OoT save data that go unused in vanilla but are used by the randomizer. **It may be incomplete.**

# Ammo counts

The ammunition count fields for fire arrows (save context + 0x90) and Din's Fire (save context + 0x91) are repurposed as a single unsigned 16-bit integer field representing the number of items received from the network in a multiworld seed.

# Scene flags

## Unused field

The unused field (offset 0x10) of the permanent scene flags (save context + 0xd4 + 0x1c * scene ID) is used for the following purposes:

* Total small key count: Scenes 0x00–0x10
    * Each dungeon uses the upper halfword of its own unused field.
    * 0x00-0x0F Dungeons
    * 0x10 Treasure Box Shop
* Scrub Shuffle: Scenes 0x00–0x27, 0x5B, 0x61
    * Scrubs in grottos store their “sold out” flag in the scene corresponding to the grotto content ID minus 0xD6, and other scrubs store it in their own scene.
    * Each scrub uses [the item it sells in vanilla](https://wiki.cloudmodding.com/oot/Actor_List_(Variables)#En_Shopnuts) as a bit mask. These are all in the lower halfword, so there is no collision with total small key count.
    * 0x00 Deku Tree
    * 0x01 Dodongo's Cavern
    * 0x02 Jabu Jabu's Belly
    * 0x0D Ganon's Castle
    * 0x10 Treasure Box Shop, Hyrule Field Grotto ID 0x12, Content ID 0xE6
    * 0x15 Volvagia Boss Room, Zora River Grotto ID 0x02, Content ID 0xEB
    * 0x18 Bongo Bongo Boss Room, Sacred Forest Meadow Grotto ID 0x17, Content ID 0xEE
    * 0x19 Ganondorf Boss Room, Lake Hylia Grotto ID 0x01, Content ID 0xEF
    * 0x1A Tower Collapse Exterior, Gerudo Valley Grotto ID 0x1E, Content ID 0xF0
    * 0x1F Back Alley (Night), Lost Woods Grotto ID 0x19, Content ID 0xF5
    * 0x23 Temple of Time Exterior (Child, Day), Death Mountain Crater Grotto ID 0x05, Content ID 0xF9
    * 0x25 Temple of Time Exterior (Adult), Goron City Grotto ID 0x07, Content ID 0xFB
    * 0x26 Know-It-All Brothers' House, Lon Lon Ranch Grotto ID 0x15, Content ID 0xFC
    * 0x27 House of Twins, Desert Colossus Grotto ID 0x00, Content ID 0xFD
    * 0x5B Lost Woods
    * 0x61 Death Mountain Crater
* Shopsanity: Scene 0x2C
    * 0x2C Bazaar
* Pending item queue: Scenes 0x30–0x35
    * Even-numbered scenes are used for override keys and odd-numbered scenes for their values.
    * 0x30 Kakariko Potion Shop
    * 0x31 Market Potion Shop
    * 0x32 Bombchu Shop
    * 0x33 Happy Mask Shop
    * 0x34 Link's House
    * 0x35 Dog Lady's House
* FW in both ages: Scenes 0x3E–0x47
    * 0x3E Grottos
    * 0x3F Redead Grave
    * 0x40 Shield Grave
    * 0x41 Royal Family's Tomb
    * 0x42 Shooting Gallery
    * 0x43 Temple of Time
    * 0x44 Chamber of the Sages
    * 0x45 Castle Hedge Maze (Day)
    * 0x46 Castle Hedge Maze (Night)
    * 0x47 Cutscene Map
* Triforce Hunt: Scene 0x48
    * 0x48 Dampe's Grave and Windmill
* Pending ice traps: Scene 0x49
    * 0x49 Fishing Pond
* Expensive Merchants (Granny's Potion Shop only): Scene 0x4E
    * 0x4E Granny's Potion Shop
* Unlocked ocarina notes: Scene 0x50
    * 0x50 House of Skulltula
* Full Trade Quest Shuffle: Scenes 0x60 and 0x62
    * Items Owned are stored in Death Mountain Trail flags, used with the d-pad in the inventory screen to cycle owned items
    * Items Traded are stored in Goron City Flags, used to prevent duping trades with the same NPC
    * Child trade items use bits 0-10, Adult trade items use bits 11-21. See trade_quest_items in ASM/c/trade_quests.c
    * Owned and Traded flags use the same bit position for the same item (e.g. Weird Egg uses bit 0 for both Owned and Traded flags)
    * 0x60 Death Mountain Trail
    * 0x62 Goron City

## Collectibles field

With `shuffle_cows`, the flags representing which cows have been talked to are stored in the collectibles field (offset 0x0c) of the permanent scene flags of the cow's respective scene:

* Jabu Jabus Belly MQ Cow: scene 0x02, bit 0100_0000
* KF Links House Cow: scene 0x34, bit 0100_0000
* LLR Stables Right Cow: scene 0x36, bit 0200_0000
* LLR Stables Left Cow: scene 0x36, bit 0100_0000
* Kak Impas House Cow: scene 0x37, bit 0100_0000
* HF Cow Grotto Cow: scene 0x37, bit 0200_0000
* DMT Cow Grotto Cow: scene 0x3e, bit 0100_0000
* LLR Tower Left Cow: scene 0x4c, bit 0200_0000
* LLR Tower Right Cow: scene 0x4c, bit 0100_0000
* GV Cow: scene 0x5a, bit 0100_0000

With `shuffle_beans`, `shuffle_expensive_merchants`, or `shuffle_tcgkeys`, flags for the bean salesman or Medigoron and the carpet salesman, respectively, are similarly stored in collectibles fields:

* Chest Mini Game: scene 0x10, bit 0000_0002
* ZR Magic Bean Salesman: scene 0x54, bit 0000_0002
* Wasteland Bombchu Salesman: scene 0x5e, bit 0000_0002
* GC Medigoron: scene 0x62, bit 0000_0002

Bombchu Bowling uses collectible flags 0 - 5 for each of the possible prizes in its scene flags (0x4B).

# inf_table

Additional flags stored in `inf_table` (an array of 16-bit integers at save context + 0x0ef8):

* Entry 0x1b, bit 0002 is set when the Temple of Time altar is read as child. This allows the pause menu dungeon info to display stone locations depending on settings.
* Entry 0x1b, bit 0001 is set when the Temple of Time altar is read as adult. This allows the pause menu dungeon info to display medallion locations depending on settings.

# event_chk_inf

Additional flags stored in 'event_chk_inf' (an array of 16-bit integers at save context + 0x0ED4)

* Entry 0xDF, bit 0001 is set when collection the 100 Gold Skulltula Reward

# Misc data

Current mask: 1 byte at save context + 0x3B. Written on `Player_Destroy`. Read on `Player_Init` except when moving through time.
