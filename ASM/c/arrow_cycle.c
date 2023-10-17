#include "arrow_cycle.h"

typedef void(*playsfx_t)(uint16_t sfx, z64_xyzf_t *unk_00_, int8_t unk_01_ , float *unk_02_, float *unk_03_, float *unk_04_);

struct arrow_cycle_state {
	uint16_t     frameDelay;
	int8_t       magicCost;
	z64_actor_t* arrow;
};

static struct arrow_cycle_state g_arrow_cycle_state = {
	.frameDelay = 0,
	.magicCost  = 0,
	.arrow      = NULL,
};

struct arrow_info {
	uint8_t  item;
	uint8_t  slot;
	uint8_t  icon;
	uint8_t  action;
	uint16_t var;
};

static struct arrow_info g_arrows[4] = {
	{ Z64_ITEM_BOW,         Z64_SLOT_BOW,         Z64_ITEM_BOW,             0x8, 0x2, },
	{ Z64_ITEM_FIRE_ARROW,  Z64_SLOT_FIRE_ARROW,  Z64_ITEM_BOW_FIRE_ARROW,  0x9, 0x3, },
	{ Z64_ITEM_ICE_ARROW,   Z64_SLOT_ICE_ARROW,   Z64_ITEM_BOW_ICE_ARROW,   0xA, 0x4, },
	{ Z64_ITEM_LIGHT_ARROW, Z64_SLOT_LIGHT_ARROW, Z64_ITEM_BOW_LIGHT_ARROW, 0xB, 0x5, },
};

static const struct arrow_info* get_info(uint16_t variable) {
	for (int i=0; i<4; i++) {
		if (g_arrows[i].var == variable)
			return (const struct arrow_info*)&g_arrows[i];
	}
	return NULL;
}

static uint16_t get_next_arrow_variable(uint16_t variable) {
	switch (variable) {
		case 2:  return 3; // Normal -> Fire
		case 3:  return 4; // Fire   -> Ice
		case 4:  return 5; // Ice    -> Light
		case 5:  return 2; // Light  -> Normal
		default: return variable;
	}
}

static int8_t get_magic_cost_by_info(const struct arrow_info *info) {
	switch (info->item) {
		case Z64_ITEM_FIRE_ARROW:  return arrow_cycle_get_magic_cost(0);
		case Z64_ITEM_ICE_ARROW:   return arrow_cycle_get_magic_cost(1);
		case Z64_ITEM_LIGHT_ARROW: return arrow_cycle_get_magic_cost(2);
		default:                   return 0;
	}
}

static const struct arrow_info* get_next_info(uint16_t variable) {
	// Get magic cost of current arrow type.
	int8_t       magicCost = get_magic_cost_by_info(get_info(variable));
	uint16_t     current   = variable;
	const struct arrow_info* info;
	for (int i=0; i<4; i++) {
		current = get_next_arrow_variable(current);
		info    = get_info(current);
		// Calculate difference in magic cost and ensure that the player has enough magic to switch.
		if (info != NULL && info->item == z64_file.items[info->slot] && z64_file.magic >= (magicCost - get_magic_cost_by_info(info)))
			return info;
	}
	return NULL;
}

/**
 * Call the En_Arrow actor constructor on an existing En_Arrow instance.
 *
 * This will re-copy the data used to draw the arrow trail color, and thus it will appear as it should.
 **/
static uint8_t call_arrow_actor_ctor(z64_actor_t* arrow, z64_game_t* ctxt) {
	z64_actor_ovl_t*  ovl  = &z64_actor_ovl_table[ACTOR_EN_ARROW];
	z64_actor_init_t* init = reloc_resolve_actor_init(ovl);
	if (init != NULL && init->init != NULL) {
		init->destroy(arrow, ctxt);
		init->init(arrow, ctxt);
		return 1;
	}
	return 0;
}

static uint8_t is_arrow_item(uint8_t item) {
	switch (item) {
		case Z64_ITEM_BOW:
		case Z64_ITEM_BOW_FIRE_ARROW:
		case Z64_ITEM_BOW_ICE_ARROW:
		case Z64_ITEM_BOW_LIGHT_ARROW:
			return 1;
		default:
			return 0;
	}
}

/**
 * Helper function used to update the arrow type on the current C button.
 **/
static void update_c_button(z64_link_t* player, z64_game_t* ctxt, const struct arrow_info* info) {
	// Update the C button value & texture.
	z64_file.button_items[player->item_button] = info->icon;
	z64_UpdateItemButton(ctxt, player->item_button);
	// Update player fields for new action type.
	player->item_action_param      = info->action;
	player->held_item_action_param = info->action;
}

uint8_t actor_helper_does_actor_exist(const z64_actor_t* target, const z64_game_t* ctxt, uint8_t actorCategory) {
	const z64_actor_t* actor = ctxt->actor_list[actorCategory].first;
	// Iterate actor linked list for each entry.
	while (actor != NULL) {
		if (actor == target)
			return 1;
		actor = actor->next;
	}
	return 0;
}

/**
 * Function called on delayed frame to finish processing the arrow cycle.
 **/
static void handle_frame_delay(z64_link_t* player, z64_game_t* ctxt, z64_actor_t* arrow) {
	// Sanity check: Ensure arrow is still an allocated actor after delay frame.
	if (!actor_helper_does_actor_exist(arrow, ctxt, ACTORTYPE_ITEMACTION))
		return;

	const struct arrow_info* curInfo = get_info(arrow->variable);
	if (arrow != NULL && curInfo != NULL) {
		z64_actor_t* special = arrow->child;
		// Deconstruct and remove special arrow actor.
		if (special != NULL) {
			z64_DeleteActor(ctxt, &ctxt->actor_ctxt, special);
			arrow->child = NULL;
		}
		
		// Handle magic consume state.
		
		// Make sure the game is aware that a special arrow effect is happening when switching
		// from normal arrow -> elemental arrow. Uses value 2 to make sure the magic cost is
		// consumed this frame.
		if (curInfo->item != Z64_ITEM_BOW)
			z64_file.magic_consume_state = 3;
		else z64_file.magic_consume_state = 0;
		
		// Refund magic cost of previous arrow type.
		z64_file.magic += g_arrow_cycle_state.magicCost;
		
		// Set magic cost value to be subtracted.
		z64_file.magic -= get_magic_cost_by_info(curInfo);
	}
}

/**
 * Helper function used to find the En_Arrow actor if attached to player.
 **/
z64_actor_t* arrow_cycle_find_arrow(z64_link_t* player, z64_game_t* ctxt) {
	z64_actor_t* attached = player->common.child;
	if (attached != NULL && attached->actor_id == ACTOR_EN_ARROW && attached->parent == &player->common)
		return attached;
	else return NULL;
}

/**
 * Get the magic cost by index from the array in player_actor.
 **/
int8_t arrow_cycle_get_magic_cost(uint8_t index) {
	if (index < 3) {
		// TODO: Vanilla MM RDRAM: 0x8077A448, find for OoT
		// 4-byte array for each cost: [Fire Arrow, Ice Arrow, Light Arrow]
		const int8_t costArray[3] = { 4, 4, 8 }; // TODO: const int8_t* costArray = (const int8_t*)reloc_resolve_player_overlay(&s801D0B70.playerActor, 0x8085CFB8);
		return costArray[index];
	}
	else return 0;
}

/**
 * Handle arrow cycling.
 *
 * Note: A "delay frame" is necessary because we cannot free the special arrow actor immediately.
 * This is due to the double-buffer nature of the game's DLists, where each one is processed every
 * other frame, and if we free the actor immediately the next DList will still contain pointers to
 * data which requires the special arrow actor file to be loaded.
 *
 * Thus, we must set the draw pointer to NULL and let one frame process before freeing the actor.
 **/
void handle_arrow_cycle(z64_link_t* player, z64_game_t* ctxt) {
	// Check if processing arrow cycling on delay frame.
	if (g_arrow_cycle_state.frameDelay >= 1) {
		handle_frame_delay(player, ctxt, g_arrow_cycle_state.arrow);
		g_arrow_cycle_state.arrow      = NULL;
		g_arrow_cycle_state.frameDelay = 0;
		g_arrow_cycle_state.magicCost  = 0;
		return;
	}
	
	// Check if buttons state is normal, otherwise we are possibly in a minigame or on Epona.
	if (z64_file.hud_visibility_mode != HUD_VISIBILITY_ALL)
		return;
	
	// Find the arrow currently attached to the player.
	z64_actor_t* arrow = arrow_cycle_find_arrow(player, ctxt);
	if (arrow == NULL)
		return;
	
	// Ensure arrow has an appropriate variable (cannot be a slingshot deku seed).
	if (!(2 <= arrow->variable && arrow->variable < 6))
		return;
	
	// Check if current button pressed corresponds to an arrow item.
	if (!is_arrow_item(z64_file.button_items[player->item_button]))
		return;
	
	// Check if R is pressed.
	if (!z64_game.common.input[0].pad_pressed.r)
		return;
	z64_game.common.input[0].raw.pad.r = z64_game.common.input[0].pad_pressed.r = 0;
	
	// Get info for arrow types.
	const struct arrow_info *curInfo, *nextInfo;
	curInfo  = get_info(arrow->variable);
	nextInfo = get_next_info(arrow->variable);
	
	// Check if there is nothing to cycle to and return early.
	if (curInfo == NULL || nextInfo == NULL || curInfo->var == nextInfo->var) {
		if (curInfo->var == 2 && z64_file.button_items[player->item_button] != Z64_ITEM_BOW && z64_file.items[Z64_SLOT_BOW] == Z64_ITEM_BOW)
			update_c_button(player, ctxt, &g_arrows[0]);
		z64_playsfx(0x4806, (z64_xyzf_t*)0x80104394, 0x04, (float*)0x801043A0, (float*)0x801043A0, (float*)0x801043A8);
		return;
	}
	
	// Check if we are switching from normal arrow -> elemental arrow, and if so verify that an
    // existing effect is not active. Otherwise the game may crash by attempting to load the actor
    // code file for one effect while an existing effect is still processing.
    // This also prevents from switching when Lens of Truth is activated.
	if (curInfo->item == Z64_ITEM_BOW && z64_file.magic < get_magic_cost_by_info(nextInfo)) {
		z64_playsfx(0x4806, (z64_xyzf_t*)0x80104394, 0x04, (float*)0x801043A0, (float*)0x801043A0, (float*)0x801043A8);
		return;
	}
	
	// Update the existing actor variable.
	arrow->variable = nextInfo->var;
	
	// Call arrow actor constructor so that the arrow trail color data is re-copied.
	call_arrow_actor_ctor(arrow, ctxt);
	
	// If found, NULL out special arrow actor's draw function to prevent it from writing to DList.
	z64_actor_t* special = arrow->child;
	if (special != NULL)
		special->draw_proc = NULL;
	
	// Update C button.
	update_c_button(player, ctxt, nextInfo);
	
	// Prepare for finishing cycle next frame.
	g_arrow_cycle_state.arrow = arrow;
	g_arrow_cycle_state.frameDelay++;
	g_arrow_cycle_state.magicCost = get_magic_cost_by_info(curInfo);
	
	// If cycling from normal arrow -> elemental arrow, reserve magic consume state.
    // This prevents using Lens between now and processing the delay frame, and thus prevents
    // mutating the magic consume state while Lens is active.
    //if (curInfo->item == Z64_ITEM_BOW)
    //    z64_file.magic_consume_state = 3;
}

struct resolve_info {
	void* ram;
    uint32_t virtStart;
    uint32_t virtEnd;
};

#define create_info(Ram, Start, End) { .ram = (Ram), .virtStart = (uint32_t)(Start), .virtEnd = (uint32_t)(End), }

static void* resolve(struct resolve_info info, uint32_t vram) {
    if (info.ram && info.virtStart <= vram && vram < info.virtEnd) {
        uint32_t offset = vram - info.virtStart;
        return (void*)((char*)info.ram + offset);
    } else {
        return NULL;
    }
}

void* reloc_resolve_actor_overlay(z64_actor_ovl_t* ovl, uint32_t vram) {
    struct resolve_info info = create_info(ovl->loaded_ram_addr, ovl->vram_start, ovl->vram_end);
    return resolve(info, vram);
}

z64_actor_init_t* reloc_resolve_actor_init(z64_actor_ovl_t* ovl) {
    return reloc_resolve_actor_overlay(ovl, (uint32_t)ovl->init_info);
}