#include "get_items.h"

#include "trade_quests.h"
#include "icetrap.h"
#include "item_table.h"
#include "stdbool.h"
#include "util.h"
#include "en_item00.h"
#include "z64.h"
#include "scene.h"
#include "actor.h"
#include "save.h"
#include "models.h"

extern uint8_t SHUFFLE_CHEST_GAME;
extern uint8_t FAST_CHESTS;
extern uint8_t OCARINAS_SHUFFLED;
extern uint8_t NO_COLLECTIBLE_HEARTS;
extern uint32_t FREE_BOMBCHU_DROPS;
override_t cfg_item_overrides[2200] = { 0 };
int item_overrides_count = 0;

z64_actor_t* dummy_actor = NULL;

// Co-op state
extern uint8_t PLAYER_ID;
extern uint8_t PLAYER_NAME_ID;
extern uint16_t INCOMING_PLAYER;
extern uint16_t INCOMING_ITEM;
extern uint8_t MW_SEND_OWN_ITEMS;
extern override_key_t OUTGOING_KEY;
extern uint16_t OUTGOING_ITEM;
extern uint16_t OUTGOING_PLAYER;
extern uint16_t GET_ITEM_SEQ_ID;
xflag_t drop_collectible_override_flag; // Flag used by hacks in Item_DropCollectible to override the item being dropped. Set it to the flag for the overridden item.
xflag_t* spawn_actor_with_flag = NULL;

override_t active_override = { 0 };
int active_override_is_outgoing = 0;
item_row_t* active_item_row = NULL;
// Split active_item_row into variables for convenience in ASM
uint32_t active_item_action_id = 0;
uint32_t active_item_text_id = 0;
uint32_t active_item_object_id = 0;
uint32_t active_item_graphic_id = 0;
uint32_t active_item_fast_chest = 0;
uint16_t incoming_junk = 0;

uint8_t satisfied_pending_frames = 0;
// Minimum number that prevents Sheik at Temple and ToT Reward from Rauru from overlapping, see https://github.com/OoTRandomizer/OoT-Randomizer/issues/2247
const uint8_t REQUIRED_PENDING_FRAMES = 6;

// These tables contain the flag bit offset for a particular scene/room/setup. These tables also index into xflag_room_blob to obtain the bit assignment for each actor in that room
// xlflag_room_blob contains a compressed table of actor bit assignments for each scene/room/setup.
// Call get_xflag_bit_offset to retrieve the desired offset for a flag.
uint16_t xflag_scene_table[101];
uint8_t xflag_room_table[700];
uint8_t xflag_room_blob[3000];
alt_override_t alt_overrides[200];

extern uint16_t CURR_ACTOR_SPAWN_INDEX;

// Total amount of memory required for each flag table (in bytes).
uint16_t num_override_flags;

// Pointer to a variable length array that will contain the collectible flags for each scene.
uint8_t* collectible_override_flags;

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
    dummy_actor->main_proc = (void*)1;
}

override_key_t get_override_search_key_by_newflag(xflag_t* flag) {
    if (flag > 0) {
        override_key_t key = {
            .scene = flag->scene,
            .type = OVR_NEWFLAGCOLLECTIBLE,
            .pad = 0,
            .flag = flag->all,
        };
        return resolve_alternative_override(key);
    }
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
            .pad = 0,
            .flag = actor->variable & 0x1F,
        };
    } else if (actor->actor_id == 0x15) {
        // Override En_Item00 collectibles
        int collectible_type = actor->variable & 0xFF;
        if (collectible_type == 0x12) { // don't override fairies. Honestly don't think this is even necessary
            return (override_key_t){ .all = 0 };
        }
        EnItem00* item = (EnItem00*)actor;

        if (collectible_type == 0x06 || collectible_type == 0x11) { // heart pieces and keys
            return (override_key_t) {
                .scene = scene,
                .type = OVR_COLLECTABLE,
                .pad = 0,
                .flag = item->collectibleFlag,
            };
        }
    } else if (actor->actor_id == 0x19C) {
        return (override_key_t){
            .scene = (actor->variable >> 8) & 0x1F,
            .type = OVR_SKULL,
            .pad = 0,
            .flag = actor->variable & 0xFF,
        };
    } else if (scene == 0x3E && actor->actor_id == 0x011A) {
        return (override_key_t){
            .scene = z64_file.respawn[RESPAWN_MODE_RETURN].data,
            .type = OVR_GROTTO_SCRUB,
            .pad = 0,
            .flag = item_id,
        };
    } else if (actor->actor_id == 0x132) {
        // Turning in Poacher's Saw to Carpenter Boss in Kakariko as child
        // using equip swap instead of Gerudo Valley as adult. Override is
        // keyed on Gerudo Valley.
        return (override_key_t) {
            .scene = 0x5A,
            .type = OVR_BASE_ITEM,
            .pad = 0,
            .flag = item_id,
        };
    } else {
        return (override_key_t) {
            .scene = scene,
            .type = OVR_BASE_ITEM,
            .pad = 0,
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

override_t lookup_override(z64_actor_t* actor, uint8_t scene, uint8_t item_id) {
    override_key_t search_key = get_override_search_key(actor, scene, item_id);
    if (search_key.all == 0) {
        return (override_t){ 0 };
    }

    return lookup_override_by_key(search_key);
}

override_t lookup_override_by_newflag(xflag_t* flag) {
    override_key_t search_key = get_override_search_key_by_newflag(flag);
    if (search_key.all == 0) {
        return (override_t){ 0 };
    }
    return lookup_override_by_key(search_key);
}

// Checks for the existence of override_key within the alternative override table and returns it
// override_key: The key to search for in the alternative override table
// Returns: The primary key to use if an alternative override is found in the table. Otherwise returns override_key
override_key_t resolve_alternative_override(override_key_t override_key) {
    alt_override_t* alt = &alt_overrides[0];
    while (alt->alt.all != 0) {
        if (alt->alt.all == override_key.all) {
            return alt->primary;
        }
        alt++;
    }
    return override_key;
}

xflag_t resolve_alternative_flag(xflag_t* flag) {
    override_key_t key;
    key.scene = flag->scene;
    key.type = 0x06;
    key.flag = flag->all;
    override_key_t alt = resolve_alternative_override(key);
    xflag_t alt_flag = {
        .all = alt.flag,
        .scene = alt.scene,
    };
    return alt_flag;
}

void activate_override(override_t override) {
    uint16_t resolved_item_id = resolve_upgrades(override);
    item_row_t* item_row = get_item_row(resolved_item_id);

    active_override = override;
    if (resolved_item_id == GI_TRIFORCE_PIECE) {
        active_override_is_outgoing = 2; // Send to everyone
    } else {
        active_override_is_outgoing = override.value.base.player != PLAYER_ID;
    }
    active_item_row = item_row;
    active_item_action_id = item_row->action_id;
    active_item_text_id = resolve_item_text_id(item_row, active_override_is_outgoing);
    active_item_object_id = item_row->object_id;
    active_item_graphic_id = item_row->graphic_id;
    if (override.value.looks_like_item_id) {
        item_row = get_item_row(override.value.looks_like_item_id);
    }
    active_item_fast_chest = item_row->chest_type == BROWN_CHEST || item_row->chest_type == SILVER_CHEST || item_row->chest_type == SKULL_CHEST_SMALL || item_row->chest_type == HEART_CHEST_SMALL;
    PLAYER_NAME_ID = override.value.base.player;
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

override_t outgoing_queue[8] = { 0 };

void push_outgoing_override(override_t* override) {
    if (override->key.type != OVR_DELAYED || override->key.flag != 0xFF) { // don't send items received from incoming back to outgoing
        if (OUTGOING_KEY.all == 0) {
            OUTGOING_ITEM = override->value.base.item_id;
            OUTGOING_PLAYER = override->value.base.player;
            // Set the value first and then the key, so a plugin checking whether the key is present is guaranteed to see the value as well
            OUTGOING_KEY = override->key;
        } else {
            for (int i = 0; i < 8; i++) {
                if (outgoing_queue[i].key.all == 0) {
                    outgoing_queue[i] = *override;
                    break;
                }
            }
        }
    }
}

void move_outgoing_queue() {
    if (OUTGOING_KEY.all == 0) {
        OUTGOING_ITEM = outgoing_queue[0].value.base.item_id;
        OUTGOING_PLAYER = outgoing_queue[0].value.base.player;
        // Set the value first and then the key, so a plugin checking whether the key is present is guaranteed to see the value as well
        OUTGOING_KEY = outgoing_queue[0].key;
        for (int i = 0; i < 7; i++) {
            outgoing_queue[i] = outgoing_queue[i + 1];
        }
        outgoing_queue[7] = (override_t){ 0 };
    }
}

void push_pending_item(override_t override) {
    for (int i = 0; i < 3; i++) {
        if (extended_savectx.incoming_queue[i].key.all == 0) {
            extended_savectx.incoming_queue[i] = override;
            break;
        }
        if (extended_savectx.incoming_queue[i].key.all == override.key.all) {
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
        override.value.base.player = INCOMING_PLAYER;
        override.value.base.item_id = INCOMING_ITEM;
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
    for (int i = 0; i < 2; i++) {
        extended_savectx.incoming_queue[i] = extended_savectx.incoming_queue[i+1];
    }
    extended_savectx.incoming_queue[2] = (override_t){ 0 };
}

void after_key_received(override_key_t key) {
    if (key.type == OVR_DELAYED && key.flag == 0xFF) {
        INCOMING_ITEM = 0;
        INCOMING_PLAYER = 0;
        uint16_t* received_item_counter = (uint16_t*)(z64_file_addr + 0x90);
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
    override_t override = extended_savectx.incoming_queue[0];
    override_key_t key = { .all = override.key.all };
    override_value_base_t value = { .all = override.value.base.all };
    if (value.item_id == GI_ICE_TRAP && value.player == PLAYER_ID) {
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
        push_outgoing_override(&active_override);
    }

    if (key.all == extended_savectx.incoming_queue[0].key.all) {
        pop_pending_item();
    }
    after_key_received(key);
    clear_override();
}

inline uint32_t link_is_ready() {
    if ((z64_logo_state != 0x802C5880) &&
        (z64_logo_state != 0) &&
        (z64_file.game_mode == PAUSE_STATE_OFF) &&
        (z64_game.pause_ctxt.state == 0) &&
        // don't receive items in shops to avoid a softlock when buying an item at the same time as receiving one
        ((z64_game.scene_index < 0x002C || z64_game.scene_index > 0x0033) && z64_game.scene_index != 0x0042 && z64_game.scene_index != 0x004B) &&
        (z64_link.state_flags_1 & 0xFCAC2485) == 0 &&
        (z64_link.common.unk_flags_00 & 0x0001) &&
        (z64_link.state_flags_2 & 0x000C0000) == 0 &&
        (z64_event_state_1 & 0x20) == 0 &&
        (z64_game.camera_2 == 0)) {
        satisfied_pending_frames++;
    } else {
        satisfied_pending_frames = 0;
    }
    if (satisfied_pending_frames >= REQUIRED_PENDING_FRAMES) {
        satisfied_pending_frames = 0;
        return 1;
    }
    return 0;
}

void try_pending_item() {
    override_t override = extended_savectx.incoming_queue[0];

    if (override.key.all == 0) {
        return;
    }

    uint16_t resolved_item_id = resolve_upgrades(override);
    item_row_t* item_row = get_item_row(resolved_item_id);
    if (override.value.base.item_id == GI_TRIFORCE_PIECE && override.value.base.player != PLAYER_ID) {
        call_effect_function(item_row);
        pop_pending_item();
        after_key_received(override.key);
        clear_override();
        return;
    }

    if (item_row->collectible >= 0 && override.key.flag == 0xFF) {
        // This is an incoming collectible junk item so speed it up by spawning a give immediate collectible
        EnItem00* collectible = (EnItem00*)z64_SpawnActor(&z64_game.actor_ctxt, &z64_game, 0x0015, z64_link.common.pos_world.x, z64_link.common.pos_world.y, z64_link.common.pos_world.z, 0, 0, 0, 0x8000 | item_row->collectible);
        collectible->override = override;
        collectible->scale = collectible->actor.scale.x = collectible->actor.scale.y = collectible->actor.scale.z = 0.015f;
        collectible->actor.yOffset = 750.0f;
        lookup_model_by_override(&collectible->model, collectible->override);
        pop_pending_item();
        after_key_received(override.key);
    } else {
        activate_override(override);
        z64_link.incoming_item_actor = dummy_actor;
        z64_link.incoming_item_id = active_item_row->base_item_id;
    }
}

void handle_pending_items() {
    move_outgoing_queue();
    push_coop_item();
    if (link_is_ready()) {
        pop_ice_trap();
        // don't apply ice traps while playing the treasure chest game, since that would allow cheesing it
        // (dying there lets you buy another key but doesn't lock already unlocked doors)
        if (ice_trap_is_pending() && (z64_game.scene_index != 0x0010 || (!SHUFFLE_CHEST_GAME && z64_game.chest_flags & 0x00000400))) {
            give_ice_trap();
        } else {
            try_pending_item();
        }
    }
}

void get_item(z64_actor_t* from_actor, z64_link_t* link, int8_t incoming_item_id) {
    override_t override = { 0 };
    int incoming_negative = incoming_item_id < 0;
    int8_t item_id = 0;
    item_row_t* row;

    if (from_actor && incoming_item_id != 0) {
        item_id = incoming_negative ? -incoming_item_id : incoming_item_id;
        // Set trade items as traded, but keep in inventory. The incoming item
        // ID will be the next sequential trade item, so use that as a reference.
        row = get_item_row(item_id);
        if (row) {
            int16_t action_id = row->action_id;
            // Set adult trade item "traded" flags to prevent duping.
            // Only necessary for full adult trade shuffle, except for Biggoron who always sets his flag.
            if ((CFG_ADULT_TRADE_SHUFFLE || action_id == Z64_ITEM_BIGGORON_SWORD) // full adult trade shuffle on, or vanilla incoming item is Biggoron Sword
                && action_id > 0 // filter invalid items
                && from_actor->actor_id != 0x000A && from_actor->actor_id != 0x013D // filter chests (0x000A) and Medigoron (0x013D) as they aren't trading actors
                // Fun fact, Medigoron's incoming item GI_GIANTS_KNIFE (0x0028) has the same action ID as Biggoron Sword, which could prevent trading to Biggoron
                // if you talked to Medigoron first without this filter. Same thing happens without full adult trade shuffle and the Biggoron dupe fix above
                && IsAdultTradeItem(action_id)) { // Only set traded flags for adult trade items. Child is handled separately.
                if (action_id == Z64_ITEM_BIGGORON_SWORD) { // special case for biggoron sword as its ID isn't contiguous with the other trade items
                    TurnInTradeItem(Z64_ITEM_CLAIM_CHECK);
                } else {
                    TurnInTradeItem(action_id - 1);
                }
            }
        }
        override = lookup_override(from_actor, z64_game.scene_index, item_id);
    }

    if (override.key.all == 0) {
        // No override, use base game's item code
        clear_override();
        link->incoming_item_id = incoming_item_id;

        // If this is an unshuffled mask shop item, set the mask owned flag
        // for partial trade shuffle. The rest of the trade items have entries
        // in the override table when unshuffled. Mask Shop unshuffled items
        // do not to avoid tripping the shop hack to only allow purchasing
        // a shop item once.
        if (row) {
            if (row->action_id >= Z64_ITEM_KEATON_MASK && row->action_id <= Z64_ITEM_MASK_OF_TRUTH && CFG_CHILD_TRADE_SHUFFLE) {
                call_effect_function(row);
            }
        }

        return;
    }

    activate_override(override);
    int8_t base_item_id = active_item_row->base_item_id;

    if (from_actor->actor_id == 0x0A) {
        // Update chest contents
        if (override.value.base.item_id == GI_ICE_TRAP && override.value.base.player == PLAYER_ID && (FAST_CHESTS || active_item_fast_chest) && z64_game.scene_index != 0x0010) {
            // Use ice trap base item ID to freeze Link as the chest opens rather than playing the full item get animation
            //HACK: Not used in treasure box shop since it causes crashes that seem to be related to a timer being shared between ice traps and something in the minigame
            base_item_id = GI_ICE_TRAP;
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
#define GIVEITEM_BOMBCHUS_5 0x96

#define LEN_ITEMS 21
uint8_t items[] = {
    GIVEITEM_RUPEE_GREEN,
    GIVEITEM_RUPEE_BLUE,
    GIVEITEM_RUPEE_RED,
    GIVEITEM_HEART,
    GIVEITEM_BOMBS_5,
    GIVEITEM_BOMBCHUS_5,
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

EnItem00* collectible_mutex = 0;

override_t collectible_override;

void reset_collectible_mutex() {
    collectible_mutex = NULL;
}

// New EnItem00 function that freezes Link until the messagebox is closed. Similar to how skulls work.
void Collectible_WaitForMessageBox(EnItem00* this, z64_game_t* game) {
    // Put the item above Link's head and keep it spinning like the normal action function
    this->actor.rot_2.y += 960;
    this->actor.pos_world = z64_link.common.pos_world;
    this->actor.pos_world.y += 40.0f;
    if (z64_file.link_age == 0) { // Link is adult so move it up another 20.0f
        this->actor.pos_world.y += 20.0f;
    }

    // Check message state:
    if (z64_MessageGetState(((uint8_t*)(&z64_game)) + 0x20D8) == 0) {
        // Make sure Link was frozen for the minimum amount of time
        if (this->timeToLive == 0) {
            reset_collectible_mutex(); // release the mutex
            // Kill the actor
            z64_ActorKill(&(this->actor));
        }
    } else {
        z64_link.common.frozen = 10;
    }
}


uint32_t loaded_scene_room_setup = -1; // Stores the currently cached scene/room/setup
uint16_t loaded_room_bit_offset = -1; // Stores the bit offset of the cached scene/room/setup
uint8_t room_flags[256]; // Stores the bit offset for each actor in the currently cached scene/room/setup

// Determine the bit offset into the collectible_override_flags for a flag
// Caches the bit offets for every actor in the current scene/room/setup into room_flags so that we don't have to search the table over and over.
uint16_t get_xflag_bit_offset(xflag_t* flag) {
    uint8_t i = 0;
    uint8_t room_id_temp = 0;
    uint8_t room_id = 0;
    uint8_t setup_id_temp;
    uint8_t setup_id = 0;
    uint8_t room_setup_count = 0;
    uint16_t room_byte_offset = 0xFFFF;
    bool is_grotto = flag->scene == 0x3E;
    //Index xflag_scene_table to get the offset into the room table for the current scene
    uint32_t test_scene_room_setup;

    // Check if we're in a grotto because we calculate grotto scene/room/setup differently because grottos are dumb
    if (is_grotto) {
        test_scene_room_setup = (flag->scene << 24) + (flag->grotto.grotto_id << 8) + (flag->grotto.room);
    } else {
        test_scene_room_setup = (flag->scene << 24) + (flag->setup << 6) + (flag->room);
    }

    // Check if we have this scene/room/setup cached already
    if (test_scene_room_setup != loaded_scene_room_setup) {
        // Not cached so load it using the xflag tables
        loaded_room_bit_offset = -1;
        loaded_scene_room_setup = -1;

        // Get the offset into xflag_room_table for the current scene.
        uint16_t room_table_index = xflag_scene_table[flag->scene];
        if (room_table_index == 0xffff) {
            return 0xffff;
        }

        // First byte in the xflag_room_table block for this scene is the number of rooms/setups
        room_setup_count = xflag_room_table[room_table_index++];

        // Loop through all of the rooms/setups to find the one for this flag
        for (i = 0; i < room_setup_count; i++) {
            // Get the setup/room from the entry
            if (flag->scene == 0x3E) {
                // If we're in a the room/setup entries are stored differently because we need 2 bytes to represent them
                setup_id_temp = (xflag_room_table[room_table_index++]);
                room_id_temp = xflag_room_table[room_table_index++];
                room_id = flag->grotto.room;
                setup_id = flag->grotto.grotto_id;
            } else {
                setup_id_temp = (xflag_room_table[room_table_index] & 0xC0) >> 6;
                room_id_temp = xflag_room_table[room_table_index++] & 0x3F;
                room_id = flag->room;
                setup_id = flag->setup;
            }

            // Test if the setup/room matches the flag
            if ((room_id_temp == room_id) && setup_id_temp == setup_id) {
                // Match. Read the next 2 bytes which contains the byte offset into the xflag_room_blob table
                room_byte_offset = (xflag_room_table[room_table_index] << 8) + xflag_room_table[room_table_index+1];
                break;
            }
            // Doesn't match so skip to the next entry
            room_table_index += 2;
        }
        // If we get here and room_byte_offset is still 0xFFFF then the room/setup combination for this flag wasn't found in the table. Just return 0xFFFF
        if (room_byte_offset == 0xFFFF) {
            return 0xFFFF;
        }

        // Now load the actor flags from the compressed data starting at room_byte_offset in xflag_room_blob

        // Read the bit offset for the current room/setup. First uint16_t in the blob
        loaded_room_bit_offset = (xflag_room_blob[room_byte_offset] << 8) + (xflag_room_blob[room_byte_offset+1]);
        room_byte_offset += 2;

        // Read the next byte from the blob. This contains the size, in bytes, of the run-length coded data to follow
        uint8_t rlc_size = xflag_room_blob[room_byte_offset++] / 2;
        uint8_t token;
        uint8_t tok_len;
        int j = 0;
        int index = 0;
        room_flags[0] = 0;
        loaded_scene_room_setup = test_scene_room_setup;
        uint8_t sum = 0;

        // Zeroize the room_flags
        z64_bzero(room_flags, 256);

        // Read and decode the RLC, data and store it into room_flags
        for (i = 0; i < rlc_size; i++) {
            token = xflag_room_blob[room_byte_offset++];
            tok_len = xflag_room_blob[room_byte_offset++];
            for (j = 0; j < tok_len; j++) {
                sum += token;
                if (token != 0) {
                    room_flags[index] = sum;
                }
                index++;
            }
        }

    }

    // Finally, return the bit offset for this flag
    // Substract 1 from the value in room_flags because we use 0 to indicate that there is no flag for that actor.
    if (loaded_room_bit_offset != -1) {
        if (is_grotto) {
            if (room_flags[flag->grotto.flag]) return loaded_room_bit_offset + room_flags[flag->grotto.flag] - 1 + flag->grotto.subflag;
        } else if(room_flags[flag->flag]) {
            return loaded_room_bit_offset + room_flags[flag->flag] - 1 + flag->subflag;
        }
    }
    return 0xFFFF;
}

// Check if the new collectible flag for an actor is set.
bool Get_NewFlag(xflag_t* flag) {
    if (flag->all) { // Check if this is one of our collectibles
        uint16_t flag_bit_offset = get_xflag_bit_offset(flag);
        if (flag_bit_offset != 0xFFFF) { // get_xflag_bit_offset will return 0xFF is the flag is not found in the tables
            return collectible_override_flags[flag_bit_offset / 8] & (0x80 >> (flag_bit_offset % 8));
        }
    }
    return true;
}

// Set a collectible flag in the new flag table for a given EnItem00.
void Set_NewFlag(xflag_t* flag) {
    uint16_t flag_bit_offset = get_xflag_bit_offset(flag);
    if (flag_bit_offset != 0xFFFF) { // get_xflag_bit_offset will return 0xFF is the flag is not found in the tables
        collectible_override_flags[flag_bit_offset / 8] |= (0x80 >> (flag_bit_offset % 8));
    }
}

// Hack at the end of Item_DropCollectible to not set the time to live, or clear the "room_index" if the collectible is being overridden.
// This allows the the item to not despawn after a few seconds like normal dropped collectibles.
// Not clearing room_index to -1 causes collectible items to despawn upon switching rooms.
void Item_DropCollectible_Room_Hack(EnItem00* spawnedActor) {
    if (spawnedActor->override.key.all && !Get_NewFlag(&(Actor_GetAdditionalData(&(spawnedActor->actor))->flag))) { // Check if we should override the collectible
        return; // Overriding the collectible so just return.
    }
    // Not overriding the collectible, set the time to live.
    spawnedActor->timeToLive = 220;
    if (
        (spawnedActor->actor.variable != ITEM00_SMALL_KEY) &&
        (spawnedActor->actor.variable != ITEM00_HEART_PIECE) &&
        (spawnedActor->actor.variable != ITEM00_HEART_CONTAINER)
    ) {
        spawnedActor->actor.room_index = -1;
    }
}

// Prevent overridden collectible items from despawning when changing to a room where
// they are still being drawn.
void Room_Change_Actor_Kill_Hack(z64_actor_t *actor) {
    if (actor->actor_id == 0x15) {
        EnItem00* this = (EnItem00*)actor;
        if (this->dropped && this->override.key.all > 0) return;
    }
    z64_ActorKill(actor);
}

// Hack in EnItem00_Init where it checks whether or not to kill the actor based on the collectible flag.
// We use this point to determine if this is an overriden collectible and store that information in the actor.
bool Item00_KillActorIfFlagIsSet(z64_actor_t* actor) {
    EnItem00* this = (EnItem00*)actor;
    this->is_silver_rupee = false;
    xflag_t flag = (xflag_t) { 0 };
    if (drop_collectible_override_flag.all) {
        flag = drop_collectible_override_flag;
    } else if (CURR_ACTOR_SPAWN_INDEX) {
        flag.scene = z64_game.scene_index;
        if (z64_game.scene_index == 0x3E) {
            flag.grotto.room = actor->room_index;
            flag.grotto.grotto_id = z64_file.respawn[RESPAWN_MODE_RETURN].data & 0x1F;
            flag.grotto.flag = CURR_ACTOR_SPAWN_INDEX;
            flag.grotto.subflag = 0;
        } else {
            flag.room = actor->room_index;
            flag.setup = curr_scene_setup;
            flag.flag = CURR_ACTOR_SPAWN_INDEX;
            flag.subflag = 0;
        }

    };
    ActorAdditionalData* extra = Actor_GetAdditionalData(actor);
    // Check if an override exists

    flag = resolve_alternative_flag(&flag);
    this->override = lookup_override_by_newflag(&flag);
    lookup_model_by_override(&this->model, this->override);
    // Check if the overridden item has already been collected
    if (Get_NewFlag(&flag)) {
        this->override = (override_t) { 0 };
        extra->flag = (xflag_t) { 0 };
    }

    if (this->override.key.all) { // If an override exists and we haven't already collected it
        extra->flag = flag;
        return 0; // Return 0 to continue spawning the actor
    }

    // If we get here than we either don't have an override, or the override has already been collected. Perform normal collectible flag check.
    if (z64_Flags_GetCollectible(&z64_game, this->collectibleFlag)) {
        z64_ActorKill(actor);
        return 1;
    }
}

// Check ammo counts for bombs/chus and drop correspondingly.
// This function returns the provided drop ID if bombs should be dropped, or ITEM00_ARROWS_SINGLE for chu drops.
int16_t drop_bombs_or_chus(int16_t dropId) {
    int8_t bomb_count = z64_file.ammo[Z64_SLOT_BOMB];
    int8_t chu_count = z64_file.ammo[Z64_SLOT_BOMBCHU];

    if (bomb_count > 15 && chu_count > 15) {
        // We have more than 15 of both so randomly drop one (50/50)
        if (z64_Rand_ZeroOne() < 0.5f) {
            return dropId;
        } else {
            return ITEM00_ARROWS_SINGLE;
        }
    }

    if (bomb_count <= chu_count) {
        return dropId; // drop bombs
    } else {
        return ITEM00_ARROWS_SINGLE; // drop chus
    }
}

// Override the drop ID (what item to spawn) in the call to Item_DropCollectible/Item_DropCollectible2.
// Drops all overridden items as green rupees for consistency (so they don't float like hearts do).
// The rest of the code is just the rewrite of the vanilla code for converting drops based on age/health.
int16_t get_override_drop_id(int16_t dropId) {
    // make our a dummy enitem00 with enough info to get the override
    if (!Get_NewFlag(&drop_collectible_override_flag) &&
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

    // Chu bag drops, convert bomb drop to bombchu drop under certain circumstances
    if (FREE_BOMBCHU_DROPS && (dropId == ITEM00_BOMBS_A || dropId == ITEM00_BOMBS_SPECIAL || dropId == ITEM00_BOMBS_B)) {
        if (z64_file.items[Z64_SLOT_BOMB] != ITEM_NONE && z64_file.items[Z64_SLOT_BOMBCHU] != ITEM_NONE) { // we have bombs and chus
            return drop_bombs_or_chus(dropId);
        } else if (z64_file.items[Z64_SLOT_BOMB] != ITEM_NONE) { // only have bombs
            return dropId; // don't do anything because this is already the right drop ID
        } else if (z64_file.items[Z64_SLOT_BOMBCHU] != ITEM_NONE) { // only have chus
            return ITEM00_ARROWS_SINGLE; // override drop ID to use the one for chus
        } else {
            return -1;
        }
    }

    // This is convoluted but it seems like it must be a single condition to match
    if ((dropId == ITEM00_BOMBS_A || dropId == ITEM00_BOMBS_SPECIAL || dropId == ITEM00_BOMBS_B) && z64_file.items[ITEM_BOMB] == ITEM_NONE) {
        return -1;
    }
    if ((dropId == ITEM00_ARROWS_SMALL || dropId == ITEM00_ARROWS_MEDIUM || dropId == ITEM00_ARROWS_LARGE) && z64_file.items[ITEM_BOW] == ITEM_NONE) {
        return -1;
    }
    if ((dropId == ITEM00_MAGIC_LARGE || dropId == ITEM00_MAGIC_SMALL) && z64_file.magic_capacity_set == 0) {
        return -1;
    }
    if ((dropId == ITEM00_SEEDS) && z64_file.items[ITEM_SLINGSHOT] == ITEM_NONE) {
        return -1;
    }

    if (dropId == ITEM00_HEART && (z64_file.energy_capacity == z64_file.energy || NO_COLLECTIBLE_HEARTS)) {
        return ITEM00_RUPEE_GREEN;
    }

    return dropId;
}

void dispatch_item(uint16_t resolved_item_id, uint8_t player, override_t* override, item_row_t* item_row) {
    // Give the item to the right place
    if (resolved_item_id == GI_TRIFORCE_PIECE) {
        // Send triforce to everyone
        push_outgoing_override(override);
        call_effect_function(item_row);
        z64_GiveItem(&z64_game, item_row->action_id);
    } else if (player != PLAYER_ID) {
        // Item is for another world. Set outgoing item.
        push_outgoing_override(override);
    } else {
        // Item is for this player
        if (MW_SEND_OWN_ITEMS) {
            // Also send to multiworld plugin for informational purposes if requested
            push_outgoing_override(override);
        }
        call_effect_function(item_row);
        z64_GiveItem(&z64_game, item_row->action_id);
    }
}

// Override hack for freestanding collectibles (rupees, recovery hearts, sticks, nuts, seeds, bombs, arrows, magic jars. Pieces of heart, heart containers, small keys handled by the regular get_item function)
uint8_t item_give_collectible(uint8_t item, z64_link_t* link, z64_actor_t* from_actor) {
    EnItem00* pItem = (EnItem00*)from_actor;

    override_t override = pItem->override;
    xflag_t flag = Actor_GetAdditionalData(from_actor)->flag;

    // Check if we should override the item. We have logic in the randomizer to not include excluded items in the override table.
    if (override.key.all == 0 || Get_NewFlag(&flag)) {
        z64_GiveItem(&z64_game, items[item]); // Give the regular item (this is what is normally called by the non-hacked function)
        return 0;
    }

    if (!collectible_mutex && pItem->actor.main_proc != NULL) { // Check our mutex so that only one collectible can run at a time (if 2 run on the same frame you lose the message). Also make sure that this actor hasn't already been killed.
        collectible_mutex = (EnItem00*)from_actor;
        collectible_override = override;
        // resolve upgrades and figure out what item to give.
        uint16_t item_id = collectible_override.value.base.item_id;
        uint16_t resolved_item_id = resolve_upgrades(collectible_override);
        item_row_t* item_row = get_item_row(resolved_item_id);

        // Set the collectible flag
        Set_NewFlag(&flag);
        //if (item == ITEM00_HEART_PIECE || item == ITEM00_SMALL_KEY) { // Don't allow heart pieces or small keys to be collected a second time. This is really just for the "Drop" types.
        //    z64_SetCollectibleFlags(&z64_game, pItem->collectibleFlag);
        //}
        item_id = collectible_override.value.base.item_id;
        uint8_t player = collectible_override.value.base.player;

        PLAYER_NAME_ID = player;

        // If it's a collectible item don't do the fanfare music/message box.
        if (item_row->collectible >= 0) { // Item is one of our base collectibles
            collectible_mutex = NULL;
            pItem->actor.dropFlag = 1; // Store this so the draw function knows to keep drawing the override.
            dispatch_item(resolved_item_id, player, &collectible_override, item_row);
            // Pick the correct sound effect for rupees or other items.
            uint16_t sfxId = GET_ITEM_SEQ_ID;
            if (item_row->collectible <= ITEM00_RUPEE_RED || item_row->collectible == ITEM00_RUPEE_PURPLE || item_row->collectible == ITEM00_RUPEE_ORANGE) {
                sfxId = NA_SE_SY_GET_RUPY;
            }

            // If the item is for another player, use a custom action to make the item fly off the screen
            if (player != PLAYER_ID) {
                pItem->timeToLive = 15; // same time to live as regular bounce effect.
                pItem->unk_154 = 35;     // not quite sure but this is what the vanilla game does.
                pItem->actor.rot_2.z = 0;
                pItem->actor.xz_speed = 0;
                pItem->actor.vel_1.y = 0;
                pItem->actor.gravity = 0;
                pItem->actionFunc = EnItem00_OutgoingAction; // Set our action function
                sfxId = NA_SE_SY_FSEL_DECIDE_L; // Play a different sound effect for outgoing items. This is one from the file select screen.
                z64_Audio_PlaySoundGeneral(sfxId, (void*)0x80104394, 4, (float*)0x801043A0, (float*)0x801043A0, (uint8_t*)0x801043A8);
                return 1;  // Return to the end of the Update function
            }
            z64_Audio_PlaySoundGeneral(sfxId, (void*)0x80104394, 4, (float*)0x801043A0, (float*)0x801043A0, (uint8_t*)0x801043A8);
            return 3; // Return to the original function so it can draw the collectible above our head.
        }

        // draw message box and play get item sound (like when a skull is picked up)
        z64_Audio_PlayFanFare(NA_BGM_SMALL_ITEM_GET);

        z64_DisplayTextbox(&z64_game, resolve_item_text_id(item_row, player != PLAYER_ID), 0);

        // Set up
        pItem->timeToLive = 15;  // unk_15A is a frame timer that is decremented each frame by the main actor code.
        pItem->unk_154 = 35;     // not quite sure but this is what the vanilla game does.
        pItem->getItemId = 0;
        pItem->actor.rot_2.z = 0;
        pItem->actor.xz_speed = 0;
        pItem->actor.vel_1.y = 0;
        pItem->actor.gravity = 0;
        z64_link.common.frozen = 10;                        // freeze Link (like when picking up a skull)
        pItem->actionFunc = Collectible_WaitForMessageBox;  // Set up the EnItem00 action function to wait for the message box to close.

        dispatch_item(resolved_item_id, player, &collectible_override, item_row);
        return 1;
    }
    return 2;
}

void get_skulltula_token(z64_actor_t* token_actor) {
    override_t override = lookup_override(token_actor, 0, 0);
    uint16_t item_id;
    uint8_t player;
    if (override.key.all == 0) {
        // Give a skulltula token if there is no override
        item_id = GI_SKULL_TOKEN;
        player = PLAYER_ID;
    } else {
        item_id = override.value.base.item_id;
        player = override.value.base.player;
    }

    uint16_t resolved_item_id = resolve_upgrades(override);
    item_row_t* item_row = get_item_row(resolved_item_id);

    token_actor->draw_proc = NULL;

    PLAYER_NAME_ID = player;
    z64_DisplayTextbox(&z64_game, resolve_item_text_id(item_row, player != PLAYER_ID), 0);
    dispatch_item(resolved_item_id, player, &override, item_row);
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

// called as part of the cutscene
void fairy_ocarina_getitem() {
    override_key_t lw_gift_from_saria = { .scene = 0xFF, .type = OVR_DELAYED, .flag = 0x02 };
    override_t override = lookup_override_by_key(lw_gift_from_saria);
    uint16_t resolved_item_id = resolve_upgrades(override);
    switch (resolved_item_id) {
        case GI_OCARINA_FAIRY: { // Fairy Ocarina
            z64_file.items[Z64_SLOT_OCARINA] = 0x07;
            break;
        }
        case GI_OCARINA_OF_TIME: { // Ocarina of Time
            z64_file.items[Z64_SLOT_OCARINA] = 0x08;
            break;
        }
    }
    item_row_t* item_row = get_item_row(resolved_item_id);
    PLAYER_NAME_ID = override.value.base.player;
    z64_DisplayTextbox(&z64_game, resolve_item_text_id(item_row, PLAYER_NAME_ID != PLAYER_ID), 0);
}
