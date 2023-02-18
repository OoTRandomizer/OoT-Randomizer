The **co-op context** is a region of memory where a portion of the randomizer's configuration variables are stored in a versioned layout defined below. It is the interface used by emulator plugins to implement [Multiworld](https://wiki.ootrandomizer.com/index.php?title=Multiworld).

The starting address of the auto-tracker context is listed at address `0x8040_0000` (at the start of the randomizer context). On versions of the randomizer before this feature was added, the starting address is given as zero. At that address, a 4-byte integer can be found. This is the version number of the co-op context and defines the layout of the remainder of the context according to the sections below. The current version is 4.

# Version 1

|Offset|Name|Min version|Size|Description|
|--:|---|--:|--:|---|
|`0x04`|`PLAYER_ID`|1|`0x0001`|The world number of this world, 1-indexed.|
|`0x05`|`PLAYER_NAME_ID`|1|`0x0001`|The world number of the player whose item is being picked up, used as an index into `PLAYER_NAME_ID` to render that player's name in the text box. `0` if no item is being picked up. This should usually not be read or modified by the multiworld plugin; use `OUTGOING_PLAYER` instead.|
|`0x06`|`INCOMING_ITEM`|1|`0x0002`|The ID (as in `Item.index`) of the next item to receive from the network, or `0` if there is none.|
|`0x08`|`OUTGOING_KEY`|1|`0x0004`|A unique ID (see `get_override_entry` in Patches.py for details) for the source location of the outgoing item, or `0` if no item is being sent. The multiworld plugin should set this to `0` after handling an outgoing item.|
|`0x0c`|`OUTGOING_ITEM`|1|`0x0002`|The ID (as in `Item.index`) of the outgoing item, or `0` if no item is being sent. The multiworld plugin should set this to `0` after handling an outgoing item.|
|`0x0e`|`OUTGOING_PLAYER`|1|`0x0002`|The world number of the outgoing item's recipient, or `0` if no item is being sent. The multiworld plugin should set this to `0` after handling an outgoing item.|
|`0x10`|`PLAYER_NAMES`|1|`0x0800`|An array of 256 player names, each 8 bytes long, that must be populated by the multiworld plugin. `PLAYER_NAME_ID` is used as an index into this array.|

# Versions 2–4

|Offset|Name|Min version|Size|Description|
|--:|---|--:|--:|---|
|`0x0004`|`PLAYER_ID`|1|`0x0001`|The world number of this world, 1-indexed.|
|`0x0005`|`PLAYER_NAME_ID`|1|`0x0001`|The world number of the player whose item is being picked up, used as an index into `PLAYER_NAME_ID` to render that player's name in the text box. `0` if no item is being picked up. This should usually not be read or modified by the multiworld plugin; use `OUTGOING_PLAYER` instead.|
|`0x0006`|`INCOMING_PLAYER`|2|`0x0002`|The world number from which the `INCOMING_ITEM` came, or `0` if there is no incoming item.|
|`0x0008`|`INCOMING_ITEM`|2|`0x0002`|The ID (as in `Item.index`) of the next item to receive from the network, or `0` if there is none.|
|`0x000a`|`MW_SEND_OWN_ITEMS`|3|`0x0001`|The multiworld plugin can set this to `1` to make the game set `OUTGOING_KEY`, `OUTGOING_ITEM`, and `OUTGOING_PLAYER` even when finding an item for its own world. Defaults to `0`, meaning these fields are only set for Triforce pieces (which affect all worlds) and other players' items.|
|`0x000c`|`OUTGOING_KEY`|2|`0x0004`|A unique ID (see `get_override_entry` in Patches.py for details) for the source location of the outgoing item, or `0` if no item is being sent. The multiworld plugin should set this to `0` after handling an outgoing item.|
|`0x0010`|`OUTGOING_ITEM`|2|`0x0002`|The ID (as in `Item.index`) of the outgoing item, or `0` if no item is being sent. The multiworld plugin should set this to `0` after handling an outgoing item.|
|`0x0012`|`OUTGOING_PLAYER`|2|`0x0002`|The world number of the outgoing item's recipient, or `0` if no item is being sent. The multiworld plugin should set this to `0` after handling an outgoing item.|
|`0x0014`|`PLAYER_NAMES`|2|`0x0800`|An array of 256 player names, each 8 bytes long, that must be populated by the multiworld plugin. `PLAYER_NAME_ID` is used as an index into this array.|
|`0x0814`|`CFG_FILE_SELECT_HASH`|4|`0x0005`|The 5 icons displayed at the top of the file select screen, represented as indices into the `HASH_ICONS` list in Spoiler.py.|
