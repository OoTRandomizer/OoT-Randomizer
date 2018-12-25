#include "chests.h"

extern uint32_t CHEST_SIZE_MATCH_CONTENTS;

uint8_t get_chest_override_size(z64_actor_t *actor) {
	if (!CHEST_SIZE_MATCH_CONTENTS) {
		// if option is off, always use default
		return ((uint8_t*)actor)[0x01E9]; // Chest type
	}

	uint8_t scene = z64_game.scene_index;
	uint8_t item_id = (actor->variable & 0x0FE0) >> 5;

	override_t override = lookup_override(actor, scene, item_id);
	if (override.value.item_id == 0) {
		// If no override, return normal type
		return ((uint8_t*)actor)[0x01E9]; // Chest type
	}

	item_row_t *item_row = get_item_row(override.value.item_id);
	if (item_row->chest_type & 0x01) {
		// Small chest
		return 5;
	}
	else {
		// Big chest
		return 0;
	}
}


uint8_t get_chest_override_color(z64_actor_t *actor) {
	if (!CHEST_SIZE_MATCH_CONTENTS) {
		// if option is off, always use default
		return ((uint8_t*)actor)[0x01E9]; // Chest type
	}

	uint8_t scene = z64_game.scene_index;
	uint8_t item_id = (actor->variable & 0x0FE0) >> 5;

	override_t override = lookup_override(actor, scene, item_id);
	if (override.value.item_id == 0) {
		// If no override, return normal type
		return ((uint8_t*)actor)[0x01E9]; // Chest type
	}

	item_row_t *item_row = get_item_row(override.value.item_id);
	if (item_row->chest_type & 0x02) {
		// Gold chest
		return 2;
	}
	else {
		// Wood chest
		return 0;
	}
}
