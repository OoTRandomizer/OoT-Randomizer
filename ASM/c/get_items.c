#include "get_items.h"

#include "icetrap.h"
#include "item_table.h"
#include "stdbool.h"
#include "util.h"
#include "z64.h"

extern uint8_t FAST_CHESTS;
extern uint8_t OCARINAS_SHUFFLED;
extern uint8_t NO_COLLECTIBLE_HEARTS;
override_t cfg_item_overrides[1536] = { 0 };
int item_overrides_count = 0;

z64_actor_t *dummy_actor = NULL;

// Co-op state
extern uint8_t PLAYER_ID;
extern uint8_t PLAYER_NAME_ID;
extern uint16_t INCOMING_PLAYER;
extern uint16_t INCOMING_ITEM;
extern uint8_t MW_SEND_OWN_ITEMS;
extern override_key_t OUTGOING_KEY;
extern uint16_t OUTGOING_ITEM;
extern uint16_t OUTGOING_PLAYER;
uint16_t drop_collectible_override_flag = 0; // Flag used by hacks in Item_DropCollectible to override the item being dropped. Set it to the flag for the overridden item.

override_t active_override = { 0 };
int active_override_is_outgoing = 0;
item_row_t *active_item_row = NULL;
// Split active_item_row into variables for convenience in ASM
uint32_t active_item_action_id = 0;
uint32_t active_item_text_id = 0;
uint32_t active_item_object_id = 0;
uint32_t active_item_graphic_id = 0;
uint32_t active_item_fast_chest = 0;

uint8_t satisified_pending_frames = 0;

// This table contains the offset (in bytes) of the start of a particular scene/room/setup flag space in collectible_override_flags.
// Call get_collectible_flag_offset to retrieve the desired offset.
uint8_t collectible_scene_flags_table[600];
alt_override_t alt_overrides[64];

extern int8_t curr_scene_setup;

// Total amount of memory required for each flag table (in bytes).
uint16_t num_override_flags;

// Pointer to a variable length array that will contain the collectible flags for each scene. 
uint8_t *collectible_override_flags;

// Initialize the override flag tables on the heap.
void override_flags_init() {
    collectible_override_flags = heap_alloc(num_override_flags + 100);
}

void item_overrides_init() {
    while (cfg_item_overrides[item_overrides_count].key.all != 0) {
        item_overrides_count++;
    }

    // Create an actor satisfying the minimum requirements to give the player an item
    dummy_actor = heap_alloc(sizeof(z64_actor_t));
    dummy_actor->main_proc = (void *)1;
}

override_key_t get_override_search_key(z64_actor_t *actor, uint8_t scene, uint8_t item_id) {
    if (actor->actor_id == 0x0A) {
        // Don't override WINNER purple rupee in the chest minigame scene
        if (scene == 0x10) {
            int chest_item_id = (actor->variable >> 5) & 0x7F;
            if (chest_item_id == 0x75) {
                return (override_key_t){ .all = 0 };
            }
        }

        return (override_key_t){
            .scene = scene,
            .type = OVR_CHEST,
            .flag = actor->variable & 0x1F,
        };
    } else if (actor->actor_id == 0x15) {
        // Override En_Item00 collectibles
        int collectible_type = actor->variable & 0xFF;
        if (collectible_type == 0x12) { // don't override fairies. Honestly don't think this is even necessary
            return (override_key_t){ .all = 0 };
        }
        EnItem00 *item = (EnItem00 *)actor;
        
        if(collectible_type == 0x06 || collectible_type == 0x11) //heart pieces and keys
        {
            return (override_key_t) {
                .scene = scene,
                .type = OVR_COLLECTABLE,
                .flag = item->collectibleFlag,
            };
        }

        // Get the collectible flag stored in the actor's initial y rotation field.
        uint16_t flag = item->actor.rot_init.y;
        if(flag > 0) 
        {
            flag |= curr_scene_setup << 14;
            if (scene == 0x19) {
                scene = 0x0A;
            }
            override_key_t key = {
            .scene = scene,
            .type = OVR_NEWFLAGCOLLECTIBLE,
            .flag = flag,
            };
            return resolve_alternative_override(key);
        }
        
    } else if (actor->actor_id == 0x19C) {
        return (override_key_t){
            .scene = (actor->variable >> 8) & 0x1F,
            .type = OVR_SKULL,
            .flag = actor->variable & 0xFF,
        };
    } else if (scene == 0x3E && actor->actor_id == 0x011A) {
        return (override_key_t){
            .scene = z64_file.grotto_id,
            .type = OVR_GROTTO_SCRUB,
            .flag = item_id,
        };
    } else {
        return (override_key_t) {
            .scene = scene,
            .type = OVR_BASE_ITEM,
            .flag = item_id,
        };
    }
}

override_t lookup_override_by_key(override_key_t key) {
    int start = 0;
    int end = item_overrides_count - 1;
    while (start <= end) {
        int mid_index = (start + end) / 2;
        override_t mid_entry = cfg_item_overrides[mid_index];
        if (key.all < mid_entry.key.all) {
            end = mid_index - 1;
        } else if (key.all > mid_entry.key.all) {
            start = mid_index + 1;
        } else {
            return mid_entry;
        }
    }
    return (override_t){ 0 };
}

override_t lookup_override(z64_actor_t *actor, uint8_t scene, uint8_t item_id) {
    override_key_t search_key = get_override_search_key(actor, scene, item_id);
    if (search_key.all == 0) {
        return (override_t){ 0 };
    }

    return lookup_override_by_key(search_key);
}


//Checks for the existence of override_key within the alternative override table and returns it
// override_key: The key to search for in the alternative override table
// Returns: The primary key to use if an alternative override is found in the table. Otherwise returns override_key
override_key_t resolve_alternative_override(override_key_t override_key)
{
    alt_override_t* alt = &alt_overrides[0];
    while(alt->alt.all != 0)
    {
        if(alt->alt.all == override_key.all)
        {
            return alt->primary;
        }
        alt++;
    }
    return override_key;
}

void activate_override(override_t override) {
    uint16_t resolved_item_id = resolve_upgrades(override.value.item_id);
    item_row_t *item_row = get_item_row(resolved_item_id);

    active_override = override;
    if (resolved_item_id == 0xCA)
        active_override_is_outgoing = 2; // Send to everyone
    else
        active_override_is_outgoing = override.value.player != PLAYER_ID;
    active_item_row = item_row;
    active_item_action_id = item_row->action_id;
    active_item_text_id = item_row->text_id;
    active_item_object_id = item_row->object_id;
    active_item_graphic_id = item_row->graphic_id;
    if (override.value.looks_like_item_id) {
        item_row = get_item_row(override.value.looks_like_item_id);
    }
    active_item_fast_chest = item_row->chest_type == BROWN_CHEST || item_row->chest_type == SILVER_CHEST || item_row->chest_type == SKULL_CHEST_SMALL;
    PLAYER_NAME_ID = override.value.player;
}

void clear_override() {
    active_override = (override_t){ 0 };
    active_override_is_outgoing = 0;
    active_item_row = NULL;
    active_item_action_id = 0;
    active_item_text_id = 0;
    active_item_object_id = 0;
    active_item_graphic_id = 0;
    active_item_fast_chest = 0;
}

void set_outgoing_override(override_t *override) {
    if (override->key.type != OVR_DELAYED || override->key.flag != 0xFF) { // don't send items received from incoming back to outgoing
        OUTGOING_KEY = override->key;
        OUTGOING_ITEM = override->value.item_id;
        OUTGOING_PLAYER = override->value.player;
    }
}

void push_pending_item(override_t override) {
    for (int key_scene = 0x30; key_scene < 0x36; key_scene += 2) {
        if (z64_file.scene_flags[key_scene].unk_00_ == 0) {
            z64_file.scene_flags[key_scene].unk_00_ = override.key.all;
            z64_file.scene_flags[key_scene + 1].unk_00_ = override.value.all;
            break;
        }
        if (z64_file.scene_flags[key_scene].unk_00_ == override.key.all) {
            // Prevent duplicate entries
            break;
        }
    }
}

void push_coop_item() {
    if (INCOMING_ITEM != 0) {
        override_t override = { 0 };
        override.key.scene = 0xFF;
        override.key.type = OVR_DELAYED;
        override.key.flag = 0xFF;
        override.value.player = INCOMING_PLAYER;
        override.value.item_id = INCOMING_ITEM;
        push_pending_item(override);
    }
}

void push_delayed_item(uint8_t flag) {
    override_key_t search_key = { .all = 0 };
    search_key.scene = 0xFF;
    search_key.type = OVR_DELAYED;
    search_key.flag = flag;
    override_t override = lookup_override_by_key(search_key);
    if (override.key.all != 0) {
        push_pending_item(override);
    }
}

void pop_pending_item() {
    for (int scene = 0x30; scene < 0x34; scene++) {
        z64_file.scene_flags[scene].unk_00_ = z64_file.scene_flags[scene + 2].unk_00_;
    }
    z64_file.scene_flags[0x34].unk_00_ = 0;
    z64_file.scene_flags[0x35].unk_00_ = 0;
}

void after_key_received(override_key_t key) {
    if (key.type == OVR_DELAYED && key.flag == 0xFF) {
        INCOMING_ITEM = 0;
        INCOMING_PLAYER = 0;
        uint16_t *received_item_counter = (uint16_t *)(z64_file_addr + 0x90);
        (*received_item_counter)++;
        return;
    }

    override_key_t fire_arrow_key = {
        .scene = 0x57, // Lake hylia
        .type = OVR_BASE_ITEM,
        .flag = 0x58, // Fire arrows item ID
    };
    if (key.all == fire_arrow_key.all) {
        // Mark fire arrow location as obtained
        z64_game.chest_flags |= 0x1;
    }
}

void pop_ice_trap() {
    override_key_t key = { .all = z64_file.scene_flags[0x30].unk_00_ };
    override_value_t value = { .all = z64_file.scene_flags[0x31].unk_00_ };
    if (value.item_id == 0x7C && value.player == PLAYER_ID) {
        push_pending_ice_trap();
        pop_pending_item();
        after_key_received(key);
    }
}

void after_item_received() {
    override_key_t key = active_override.key;
    if (key.all == 0) {
        return;
    }

    if (MW_SEND_OWN_ITEMS || active_override_is_outgoing) {
        set_outgoing_override(&active_override);
    }

    if (key.all == z64_file.scene_flags[0x30].unk_00_) {
        pop_pending_item();
    }
    after_key_received(key);
    clear_override();
}

inline uint32_t link_is_ready() {
    if ((z64_link.state_flags_1 & 0xFCAC2485) == 0 &&
        (z64_link.common.unk_flags_00 & 0x0001) &&
        (z64_link.state_flags_2 & 0x000C0000) == 0 &&
        (z64_event_state_1 & 0x20) == 0 &&
        (z64_game.camera_2 == 0)) {
        satisified_pending_frames++;
    }
    else {
        satisified_pending_frames = 0;
    }
    if (satisified_pending_frames >= 2) {
        satisified_pending_frames = 0;
        return 1;
    }
    return 0;
}

void try_pending_item() {
    override_t override = {
        .key.all = z64_file.scene_flags[0x30].unk_00_,
        .value.all = z64_file.scene_flags[0x31].unk_00_,
    };

    if(override.key.all == 0) {
        return;
    }

    if (override.value.item_id == 0xCA && override.value.player != PLAYER_ID) {
        uint16_t resolved_item_id = resolve_upgrades(override.value.item_id);
        item_row_t *item_row = get_item_row(resolved_item_id);
        call_effect_function(item_row);
        pop_pending_item();
        after_key_received(override.key);
        clear_override();
        return;
    }

    activate_override(override);

    z64_link.incoming_item_actor = dummy_actor;
    z64_link.incoming_item_id = active_item_row->base_item_id;
}

void handle_pending_items() {
    push_coop_item();
    if (link_is_ready()) {
        pop_ice_trap();
        // don't apply ice traps while playing the treasure chest game, since that would allow cheesing it
        // (dying there lets you buy another key but doesn't lock already unlocked doors)
        if (ice_trap_is_pending() && (z64_game.scene_index != 0x0010 || z64_game.chest_flags & 0x00000400)) {
            give_ice_trap();
        } else {
            try_pending_item();
        }
    }
}

void get_item(z64_actor_t *from_actor, z64_link_t *link, int8_t incoming_item_id) {
    override_t override = { 0 };
    int incoming_negative = incoming_item_id < 0;

    if (from_actor && incoming_item_id != 0) {
        int8_t item_id = incoming_negative ? -incoming_item_id : incoming_item_id;
        override = lookup_override(from_actor, z64_game.scene_index, item_id);
    }

    if (override.key.all == 0) {
        // No override, use base game's item code
        clear_override();
        link->incoming_item_id = incoming_item_id;
        return;
    }

    activate_override(override);
    int8_t base_item_id = active_item_row->base_item_id;

    if (from_actor->actor_id == 0x0A) {
        // Update chest contents
        if (override.value.item_id == 0x7C && override.value.player == PLAYER_ID && (FAST_CHESTS || active_item_fast_chest)) {
            // Use ice trap base item ID to freeze Link as the chest opens rather than playing the full item get animation
            base_item_id = 0x7C;
        }
        from_actor->variable = (from_actor->variable & 0xF01F) | (base_item_id << 5);
    }

    link->incoming_item_id = incoming_negative ? -base_item_id : base_item_id;
}

#define GIVEITEM_RUPEE_GREEN 0x84
#define GIVEITEM_RUPEE_BLUE 0x85
#define GIVEITEM_RUPEE_RED 0x86
#define GIVEITEM_HEART 0x83
#define GIVEITEM_STICK 0x00
#define GIVEITEM_NUT_5 140
#define GIVEITEM_BOMBS_5 142
#define GIVEITEM_ARROWS_SINGLE 3
#define GIVEITEM_ARROWS_SMALL 146
#define GIVEITEM_ARROWS_MEDIUM 147
#define GIVEITEM_ARROWS_LARGE 148
#define GIVEITEM_SEEDS 88
#define GIVEITEM_MAGIC_SMALL 120
#define GIVEITEM_MAGIC_LARGE 121
#define GIVEITEM_RUPEE_PURPLE 135

#define LEN_ITEMS 21
uint8_t items[] = {
    GIVEITEM_RUPEE_GREEN,
    GIVEITEM_RUPEE_BLUE,
    GIVEITEM_RUPEE_RED,
    GIVEITEM_HEART,
    GIVEITEM_BOMBS_5,
    GIVEITEM_ARROWS_SINGLE,
    0,
    0,
    GIVEITEM_ARROWS_SMALL,
    GIVEITEM_ARROWS_MEDIUM,
    GIVEITEM_ARROWS_LARGE,
    GIVEITEM_BOMBS_5,
    GIVEITEM_NUT_5,
    GIVEITEM_STICK,
    GIVEITEM_MAGIC_LARGE,
    GIVEITEM_MAGIC_SMALL,
    GIVEITEM_SEEDS,
    0,
    0,
    0,
    GIVEITEM_RUPEE_PURPLE,
};

EnItem00 *collectible_mutex = 0;

override_t collectible_override;

void reset_collectible_mutex() {
    collectible_mutex = NULL;
}

// New EnItem00 function that freezes Link until the messagebox is closed. Similar to how skulls work.
void Collectible_WaitForMessageBox(EnItem00 *this, z64_game_t *game) {
    // Check message state:
    if (z64_MessageGetState(((uint8_t *)(&z64_game)) + 0x20D8) == 0) {
        // Make sure link was frozen for the minimum amount of time
        if (this->timeToLive == 0) {
            reset_collectible_mutex(); // release the mutex
            // Kill the actor
            z64_ActorKill(&(this->actor));
        }
    } else {
        z64_link.common.frozen = 10;
    }
}

// Determine the offset into the new flag table to store the flags for the current scene/setup/room.
// TODO: Optimize this by remembering the current scene's offset.
uint16_t get_collectible_flag_offset(uint8_t scene, uint8_t room, uint8_t setup_id)
{
    uint8_t num_scenes = collectible_scene_flags_table[0];
    uint16_t index = 1;
    uint8_t i = 0;
    uint8_t scene_id = 0;
    uint8_t room_id = 0;
    uint8_t setup_id_temp;
    uint8_t room_setup_count = 0;
    uint16_t room_byte_offset = 0;
    // Loop through collectible_scene_flags_table until we find the right scene
    while(num_scenes > 0)
    {
        scene_id = collectible_scene_flags_table[index++];
        room_setup_count = collectible_scene_flags_table[index++];
        if(scene_id == scene) // Found the scene
        {
            // Loop through each room/setup combination in the scene until we find the right one.
            for(i = 0; i < room_setup_count; i++)
            {
                room_id = collectible_scene_flags_table[index] & 0x3F;
                setup_id_temp = (collectible_scene_flags_table[index++] & 0xC0) >> 6;
                room_byte_offset = (collectible_scene_flags_table[index] << 8) + collectible_scene_flags_table[index+1];
                index += 2;
                if((room_id == room) && (setup_id_temp == setup_id)) // Found the right room/setup
                {
                    return room_byte_offset;
                }
            }
        }
        else // Not the right scene so skip to the next one.
        {
            index += 3 * room_setup_count;
        }
        num_scenes--;
        
    }
    return 0xFFFF;
}

// Check if the new collectible flag for an EnItem00 is set.
bool Get_CollectibleOverrideFlag(EnItem00 *item00) {
    uint16_t scene = z64_game.scene_index;

    if (item00->actor.variable == ITEM00_HEART_PIECE || item00->actor.variable == ITEM00_SMALL_KEY || item00->actor.variable == ITEM00_HEART_CONTAINER) {
        return z64_Flags_GetCollectible(&z64_game, item00->collectibleFlag) > 0;
    }
    override_key_t key = get_override_search_key(&item00->actor, scene, 0);
    scene = key.scene;
    uint16_t collectible_flag = key.flag & 0xFF;
    uint8_t room = (key.flag & 0x3F00) >> 8;
    uint8_t setup = (key.flag & 0xC000) >> 14;
    if (collectible_flag > 0) //Check if this is one of our collectibles
    {
        uint16_t table_offset = get_collectible_flag_offset(scene, room, setup); //Get the offset into the flag table for the current scene/room/setup
        if(table_offset != 0xFFFF) //get_collectible_flag_offset will return 0xFF is the flag is not found in the table
        {
            return collectible_override_flags[table_offset + collectible_flag / 8] & (1 << (collectible_flag % 8));
        }
    }
    return false;
}

// Set a collectible flag in the new flag table for a given EnItem00.
void Set_CollectibleOverrideFlag(EnItem00 *item00) {
    uint16_t scene = z64_game.scene_index;
    override_key_t key = get_override_search_key(&item00->actor, scene, 0);
    scene = key.scene;
    uint8_t room = (key.flag & 0x3F00) >> 8;
    uint16_t collectible_flag = key.flag & 0xFF;
    uint8_t setup = (key.flag & 0xC000) >> 14;
    if(collectible_flag > 0) {
        uint16_t table_offset = get_collectible_flag_offset(scene, room, setup);
        if(table_offset != 0xFFFF)
        {
            collectible_override_flags[table_offset + collectible_flag / 8] |= (1 << (collectible_flag % 8));
        }
    }
}

// Returns true if the EnItem00 should be overridden. Checks if an entry exists in the override table, and if the collectible flag is set.
bool should_override_collectible(EnItem00 *item00) {
    override_t override = lookup_override(&(item00->actor), z64_game.scene_index, 0);
    if (override.key.all == 0 || Get_CollectibleOverrideFlag(item00)) {
        return 0;
    }
    return 1;
}

// Hack at the end of Item_DropCollectible to not set the time to live, or clear the "room_index" if the collectible is being overridden.
// This allows the the item to not despawn after a few seconds like normal dropped collectibles.
// Not clearing room_index to -1 causes collectible items to despawn upon switching rooms. 
void Item_DropCollectible_Room_Hack(EnItem00 *spawnedActor)
{
    if(should_override_collectible(spawnedActor)) // Check if we should override the collectible
    {
        return; // Overriding the collectible so just return.
    }
    // Not overriding the collectible, set the time to live.
    spawnedActor->timeToLive = 220;
    if((spawnedActor->actor.variable != ITEM00_SMALL_KEY) &&
       (spawnedActor->actor.variable != ITEM00_HEART_PIECE) &&
       (spawnedActor->actor.variable != ITEM00_HEART_CONTAINER))
       {
        spawnedActor->actor.room_index = -1;
       }
}

bool Item00_KillActorIfFlagIsSet(z64_actor_t *actor) {
    EnItem00 *this = (EnItem00 *)actor;
    if (should_override_collectible(this)) {
        return 0;
    }

    if (z64_Flags_GetCollectible(&z64_game, this->collectibleFlag)) {
        z64_ActorKill(actor);
        return 1;
    }
}

// Override the drop ID (what item to spawn) in the call to Item_DropCollectible/Item_DropCollectible2.
// Drops all overridden items as green rupees for consistency (so they don't float like hearts do).
// The rest of the code is just the rewrite of the vanilla code for converting drops based on age/health.
int16_t get_override_drop_id(int16_t dropId) {
    // make our a dummy enitem00 with enough info to get the override
    EnItem00 dummy;
    dummy.actor.actor_id = 0x15;
    dummy.actor.rot_init.y = drop_collectible_override_flag;
    dummy.actor.variable = dropId;
    if (should_override_collectible(&dummy) &&
        dropId != ITEM00_HEART_PIECE &&
        dropId != ITEM00_SMALL_KEY &&
        dropId != ITEM00_HEART_CONTAINER &&
        dropId != ITEM00_SHIELD_DEKU &&
        dropId != ITEM00_SHIELD_HYLIAN &&
        dropId != ITEM00_TUNIC_ZORA &&
        dropId != ITEM00_TUNIC_GORON)
    {
        dropId = ITEM00_RUPEE_GREEN;
        return dropId;
    }

    if (LINK_IS_ADULT) {
        if (dropId == ITEM00_SEEDS) {
            dropId = ITEM00_ARROWS_SMALL;
        } else if (dropId == ITEM00_STICK) {
            dropId = ITEM00_RUPEE_GREEN;
        }
    } else {
        if (dropId == ITEM00_ARROWS_SMALL || dropId == ITEM00_ARROWS_MEDIUM || dropId == ITEM00_ARROWS_LARGE) {
            dropId = ITEM00_SEEDS;
        }
    }

    // This is convoluted but it seems like it must be a single condition to match
    if ((dropId == ITEM00_BOMBS_A || dropId == ITEM00_BOMBS_SPECIAL || dropId == ITEM00_BOMBS_B) && z64_file.items[ITEM_BOMB] == -1) {
        return -1;
    }
    if ((dropId == ITEM00_ARROWS_SMALL || dropId == ITEM00_ARROWS_MEDIUM || dropId == ITEM00_ARROWS_LARGE) && z64_file.items[ITEM_BOW] == -1) {
        return -1;
    }
    if ((dropId == ITEM00_MAGIC_LARGE || dropId == ITEM00_MAGIC_SMALL) && z64_file.magic_capacity_set == 0) {
        return -1;
    }
    if ((dropId == ITEM00_SEEDS) && z64_file.items[ITEM_SLINGSHOT] == -1) {
        return -1;
    }

    if (dropId == ITEM00_HEART && (z64_file.energy_capacity == z64_file.energy || NO_COLLECTIBLE_HEARTS)) {
        return ITEM00_RUPEE_GREEN;
    }

    return dropId;
}

// Override hack for freestanding collectibles (rupees, recovery hearts, sticks, nuts, seeds, bombs, arrows, magic jars. Pieces of heart, heart containers, small keys handled by the regular get_item function)
uint8_t item_give_collectible(uint8_t item, z64_link_t *link, z64_actor_t *from_actor) {
    EnItem00 *pItem = (EnItem00 *)from_actor;

    override_t override = lookup_override(from_actor, z64_game.scene_index, 0);

    // Check if we should override the item. We have logic in the randomizer to not include excluded items in the override table.
    if (override.key.all == 0 || Get_CollectibleOverrideFlag(pItem)) {
        z64_GiveItem(&z64_game, items[item]); // Give the regular item (this is what is normally called by the non-hacked function)
        //if (get_extended_flag(pItem) > 0x3F) { // If our extended collectible flag is outside the range of normal collectibles, set the flag to 0 so it doesn't write something wrong. We should only ever be using this for things that normally are 0 anyway
        //    pItem->collectibleFlag = 0;
        //    pItem->actor.dropFlag &= 0x01;
        //}
        return 0;
    }

    if (!collectible_mutex && pItem->actor.main_proc != NULL) { // Check our mutex so that only one collectible can run at a time (if 2 run on the same frame you lose the message). Also make sure that this actor hasn't already been killed.
        collectible_mutex = (EnItem00 *)from_actor;
        collectible_override = override;
        // resolve upgrades and figure out what item to give.
        uint16_t item_id = collectible_override.value.item_id;
        uint16_t resolved_item_id = resolve_upgrades(item_id);
        item_row_t *item_row = get_item_row(resolved_item_id);

        // Set the collectible flag
        Set_CollectibleOverrideFlag(pItem);
        //if (item == ITEM00_HEART_PIECE || item == ITEM00_SMALL_KEY) { // Don't allow heart pieces or small keys to be collected a second time. This is really just for the "Drop" types.
        //    z64_SetCollectibleFlags(&z64_game, pItem->collectibleFlag);
        //}
        item_id = collectible_override.value.item_id;
        uint8_t player = collectible_override.value.player;

        PLAYER_NAME_ID = player;

        // If it's a collectible item don't do the fanfare music/message box. 
        if (item_row->collectible >= 0) { // Item is one of our base collectibles
            collectible_mutex = NULL;
            pItem->actor.health = 1;
            z64_GiveItem(&z64_game, item_row->action_id);
            // Pick the correct sound effect for rupees or other items.
            uint16_t sfxId = NA_SE_SY_GET_ITEM;
            if (item_row->collectible <= ITEM00_RUPEE_RED || item_row->collectible == ITEM00_RUPEE_PURPLE || item_row->collectible == ITEM00_RUPEE_ORANGE) {
                sfxId = NA_SE_SY_GET_RUPY;
            }
            z64_Audio_PlaySoundGeneral(sfxId, (void *)0x80104394, 4, (float *)0x801043A0, (float *)0x801043A0, (uint8_t *)0x801043A8);
            return 3; // Return to the original function so it can draw the collectible above our head.
        }

        // draw message box and play get item sound (like when a skull is picked up)
        z64_Audio_PlayFanFare(NA_BGM_SMALL_ITEM_GET);

        z64_DisplayTextbox(&z64_game, item_row->text_id, 0);

        // Set up
        pItem->timeToLive = 15;  // unk_15A is a frame timer that is decremented each frame by the main actor code.
        pItem->unk_154 = 35;     // not quite sure but this is what the vanilla game does.
        pItem->getItemId = 0;
        z64_link.common.frozen = 10;                        // freeze Link (like when picking up a skull)
        pItem->actionFunc = Collectible_WaitForMessageBox;  // Set up the EnItem00 action function to wait for the message box to close.

        // Give the item to the right place
        if (resolved_item_id == 0xCA) {
            // Send triforce to everyone
            set_outgoing_override(&collectible_override);
            z64_GiveItem(&z64_game, item_row->action_id);
            call_effect_function(item_row);
        } else if (player != PLAYER_ID) {
            // Item is for another world. Set outgoing item.
            set_outgoing_override(&collectible_override);
        } else {
            // Item is for this player
            if (MW_SEND_OWN_ITEMS) {
                set_outgoing_override(&collectible_override);
            }
            z64_GiveItem(&z64_game, item_row->action_id);
            call_effect_function(item_row);
        }

        return 1;
    }
    return 2;  //
}

void get_skulltula_token(z64_actor_t *token_actor) {
    override_t override = lookup_override(token_actor, 0, 0);
    uint16_t item_id;
    uint8_t player;
    if (override.key.all == 0) {
        // Give a skulltula token if there is no override
        item_id = 0x5B;
        player = PLAYER_ID;
    } else {
        item_id = override.value.item_id;
        player = override.value.player;
    }

    uint16_t resolved_item_id = resolve_upgrades(item_id);
    item_row_t *item_row = get_item_row(resolved_item_id);

    token_actor->draw_proc = NULL;

    PLAYER_NAME_ID = player;
    z64_DisplayTextbox(&z64_game, item_row->text_id, 0);

    if (resolved_item_id == 0xCA) {
        // Send triforce to everyone
        set_outgoing_override(&override);
        z64_GiveItem(&z64_game, item_row->action_id);
        call_effect_function(item_row);
    } else if (player != PLAYER_ID) {
        set_outgoing_override(&override);
    } else {
        if (MW_SEND_OWN_ITEMS) {
            set_outgoing_override(&override);
        }
        z64_GiveItem(&z64_game, item_row->action_id);
        call_effect_function(item_row);
    }
}

int give_sarias_gift() {
    uint16_t received_sarias_gift = (z64_file.event_chk_inf[0x0C] & 0x0002);
    if (received_sarias_gift == 0) {
        if (OCARINAS_SHUFFLED)
            push_delayed_item(0x02);
        z64_file.event_chk_inf[0x0C] |= 0x0002;
    }

    // return 1 to skip the cutscene
    return OCARINAS_SHUFFLED || received_sarias_gift;
}
