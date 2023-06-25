This file documents parts of the OoT save data that go unused in vanilla but are used by the randomizer. **It may be incomplete.**

# Ammo counts

The ammunition count fields for fire arrows (save context + 0x90) and Din's Fire (save context + 0x91) are repurposed as a single unsigned 16-bit integer field representing the number of items received from the network in a multiworld seed.

# Scene flags

## Unused field

The unused field (offset 0x10) of the permanent scene flags (save context + 0xd4 + 0x1c * scene ID) is used for the following purposes:

* Total small key count: Scenes 0x00–0x10 (Each dungeon uses the upper halfword of its own unused field.)
* Scrub Shuffle: Scenes 0x00–0x27 and 0x5B (Scrubs in grottos store their “sold out” flag in the scene corresponding to the grotto ID minus 0xD6, and other scrubs store it in their own scene. Each scrub uses [the item it sells in vanilla](https://wiki.cloudmodding.com/oot/Actor_List_(Variables)#En_Shopnuts) as a bit mask. These are all in the lower halfword, so there is no collision with total small key count.)
* Shopsanity: Scene 0x2C
* Pending item queue: Scenes 0x30–0x35 (Even-numbered scenes are used for override keys and odd-numbered scenes for their values.)
* FW in both ages: Scenes 0x3E–0x47
* Triforce Hunt: Scene 0x48
* Pending ice traps: Scene 0x49
* Trade Quest Items Owned: Scene 0x60
* Trade Quest Items Traded: Scene 0x62
* Expensive Merchants (Granny's Potion Shop only): Scene 4E
* Unlocked ocarina notes: Scene 0x50

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

# Misc data

Current mask: 1 byte at save context + 0x3B. Written on `Player_Destroy` Read on `Player_Init` except when moving through time.
