The **auto-tracker context** is a region of memory where a portion of the randomizer's configuration variables are stored in a versioned layout defined below. Its intent is to give some symbols added by the randomizer well-defined addresses so that auto-trackers can read them reliably without needing the symbols.json for the specific randomizer version that was used to generate the seed.

The starting address of the auto-tracker context is listed at address `0x8040_000c` (randomizer context + `0xc`). On versions of the randomizer before this feature was added, the starting address is given as zero. At that address, a 4-byte integer can be found. This is the version number of the auto-tracker context and defines the layout of the remainder of the context according to the sections below. The current version is 4.

# Versions 1–2

|Offset|Name|Min version|Size|Description|
|--:|---|--:|--:|---|
|`0x04`|`CFG_DUNGEON_INFO_ENABLE`|1|`0x04`|Defines how information about dungeons will be displayed on the inventory screen on the pause menu. `0` = disabled, `1` = a single menu shown when holding A, `2` = separate menus shown when holding D-pad buttons.|
|`0x08`|`CFG_DUNGEON_INFO_MQ_ENABLE`|1|`0x04`|`1` if the dungeon info in the pause menu should include info about which dungeons are in Master Quest mode.|
|`0x0c`|`CFG_DUNGEON_INFO_MQ_NEED_MAP`|1|`0x04`|`1` if the Master Quest info should only be displayed for dungeons whose maps have been obtained or which don't have maps.|
|`0x10`|`CFG_DUNGEON_INFO_REWARD_ENABLE`|1|`0x04`|`1` if the dungeon info in the pause menu should include info about which medallions and stones are in which dungeon.|
|`0x14`|`CFG_DUNGEON_INFO_REWARD_NEED_COMPASS`|1|`0x04`|Defines which item is required to display the location of a dungeon reward in the pause menu. `0` = no item required, `1` = the compass of the dungeon in which the reward is found, `2` = the compass of the reward's vanilla dungeon. For example, if the Kokiri Emerald is in the Fire Temple, `1` means the Fire Temple compass is required and `2` means the Deku Tree compass is required.|
|`0x18`|`CFG_DUNGEON_INFO_REWARD_NEED_ALTAR`|1|`0x04`|`1` if the reward info should only be displayed for rewards whose Temple of Time altar text boxes have been read.|
|`0x1c`|`CFG_DUNGEON_REWARDS`|1|`0x0e`|A byte representing the medallion or stone for each dungeon. Dungeons without rewards are listed as `0xff`, and one reward is chosen arbitrarily if the dungeon has multiple rewards. For more complete data, use `CFG_DUNGEON_REWARD_AREAS` instead.|
|`0x2a`|`CFG_DUNGEON_IS_MQ`|1|`0x0e`|A byte set to `1` for each dungeon in Master Quest mode.|
|`0x38`|`RAINBOW_BRIDGE_CONDITION`|2|`0x04`|The condition for spawning the rainbow bridge. `0` = open, `1` = medallions, `2` = dungeon rewards, `3` = stones, `4` = vanilla, `5` = tokens, `6` = hearts.|
|`0x3c`|`LACS_CONDITION`|2|`0x04`|The condition for triggering the light arrow cutscene. `0` = vanilla, `1` = medallions, `2` = dungeons, `3` = stones, `4` = tokens, `5` = hearts.|
|`0x40`|`RAINBOW_BRIDGE_COUNT`|2|`0x02`|The number of items (of the kind defined in `RAINBOW_BRIDGE_CONDITION`) required to spawn the rainbow bridge.|
|`0x42`|`LACS_CONDITION_COUNT`|2|`0x02`|The number of items (of the kind defined in `LACS_CONDITION`) required to trigger the light arrow cutscene.|
|`0x44`|`TRIFORCE_HUNT_ENABLED`|2|`0x02`|`1` if Triforce hunt is enabled.|
|`0x46`|`TRIFORCE_PIECES_REQUIRED`|2|`0x02`|In Triforce hunt, the total number of Triforce pieces (across all worlds) required to win the game.|
|`0x48`|`SPECIAL_DEAL_COUNTS`|2|`0x08`|A byte representing the number of special deal slots in each shop, in the following order: KF Shop, Market Bazaar, Market Potion Shop, Market Bombchu Shop, Kak Bazaar, Kak Potion Shop, GC Shop, ZD Shop.|
|`0x50`|`CFG_DUNGEON_REWARD_AREAS`|3|`0xcf`|For each dungeon reward in the order of Emerald, Ruby, Sapphire, Light, Forest, Fire, Water, Shadow, and Spirit, a null-terminated `0x16`-byte (`0x17` including the null terminator) ASCII string containing the hint area of that reward, padded with spaces on the right.|

# Version 3

Special care needs to be taken when working with version 3 of the auto-tracker context, since a breaking change was made in version 6.2.181 of the randomizer without an accompanying change to the auto-tracker context version. Versions 6.2.180 of the randomizer and earlier use the same layout as version 2 described above (with the addition of the `CFG_DUNGEON_REWARD_AREAS` field), while versions 6.2.181 and later use the same layout as version 4 described below. The version number at addresses 0x35–0x37 of the ROM header may be used to check for the randomizer version, but this may not be accurate for forks of the randomizer if they merged the change early.

# Version 4

|Offset|Name|Min version|Size|Description|
|--:|---|--:|--:|---|
|`0x04`|`CFG_DUNGEON_INFO_ENABLE`|4|`0x04`|Defines how information about dungeons will be displayed on the inventory screen on the pause menu. `0` = disabled, `1` = a single menu shown when holding A, `2` = separate menus shown when holding D-pad buttons in addition to the summary menu on A.|
|`0x08`|`CFG_DUNGEON_INFO_MQ_ENABLE`|1|`0x04`|`1` if the dungeon info in the pause menu should include info about which dungeons are in Master Quest mode.|
|`0x0c`|`CFG_DUNGEON_INFO_MQ_NEED_MAP`|1|`0x04`|`1` if the Master Quest info should only be displayed for dungeons whose maps have been obtained or which don't have maps.|
|`0x10`|`CFG_DUNGEON_INFO_REWARD_ENABLE`|1|`0x04`|`1` if the dungeon info in the pause menu should include info about which medallions and stones are in which dungeon.|
|`0x14`|`CFG_DUNGEON_INFO_REWARD_NEED_COMPASS`|1|`0x04`|Defines which item is required to display the location of a dungeon reward in the pause menu. `0` = no item required, `1` = the compass of the dungeon in which the reward is found, `2` = the compass of the reward's vanilla dungeon. For example, if the Kokiri Emerald is in the Fire Temple, `1` means the Fire Temple compass is required and `2` means the Deku Tree compass is required.|
|`0x18`|`CFG_DUNGEON_INFO_REWARD_NEED_ALTAR`|1|`0x04`|`1` if the reward info should only be displayed for rewards whose Temple of Time altar text boxes have been read.|
|`0x1c`|`CFG_DUNGEON_INFO_REWARD_SUMMARY_ENABLE`|4|`0x04`|`1` if the summary menu shown when holding A should display dungeon reward locations.|
|`0x20`|`CFG_DUNGEON_REWARDS`|4|`0x0e`|A byte representing the medallion or stone for each dungeon. Dungeons without rewards are listed as `0xff`, and one reward is chosen arbitrarily if the dungeon has multiple rewards. For more complete data, use `CFG_DUNGEON_REWARD_AREAS` instead.|
|`0x2e`|`CFG_DUNGEON_IS_MQ`|4|`0x0e`|A byte set to `1` for each dungeon in Master Quest mode.|
|`0x3c`|`RAINBOW_BRIDGE_CONDITION`|4|`0x04`|The condition for spawning the rainbow bridge. `0` = open, `1` = medallions, `2` = dungeon rewards, `3` = stones, `4` = vanilla, `5` = tokens, `6` = hearts.|
|`0x40`|`LACS_CONDITION`|4|`0x04`|The condition for triggering the light arrow cutscene. `0` = vanilla, `1` = medallions, `2` = dungeons, `3` = stones, `4` = tokens, `5` = hearts.|
|`0x44`|`RAINBOW_BRIDGE_COUNT`|4|`0x02`|The number of items (of the kind defined in `RAINBOW_BRIDGE_CONDITION`) required to spawn the rainbow bridge.|
|`0x46`|`LACS_CONDITION_COUNT`|4|`0x02`|The number of items (of the kind defined in `LACS_CONDITION`) required to trigger the light arrow cutscene.|
|`0x48`|`TRIFORCE_HUNT_ENABLED`|4|`0x02`|`1` if Triforce hunt is enabled.|
|`0x4a`|`TRIFORCE_PIECES_REQUIRED`|4|`0x02`|In Triforce hunt, the total number of Triforce pieces (across all worlds) required to win the game.|
|`0x4c`|`SPECIAL_DEAL_COUNTS`|4|`0x08`|A byte representing the number of special deal slots in each shop, in the following order: KF Shop, Market Bazaar, Market Potion Shop, Market Bombchu Shop, Kak Bazaar, Kak Potion Shop, GC Shop, ZD Shop.|
|`0x54`|`CFG_DUNGEON_REWARD_AREAS`|4|`0xcf`|For each dungeon reward in the order of Emerald, Ruby, Sapphire, Light, Forest, Fire, Water, Shadow, and Spirit, a null-terminated `0x16`-byte (`0x17` including the null terminator) ASCII string containing the hint area of that reward, padded with spaces on the right.|
