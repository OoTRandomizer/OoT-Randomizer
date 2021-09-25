#include "chests.h"

extern uint32_t CHEST_SIZE_MATCH_CONTENTS;

void get_chest_override(z64_actor_t *actor) {
	uint8_t size  = ((uint8_t*)actor)[0x01E9];
	uint8_t color = size;

	if (CHEST_SIZE_MATCH_CONTENTS) {
		uint8_t scene = z64_game.scene_index;
		uint8_t item_id = (actor->variable & 0x0FE0) >> 5;

		override_t override = lookup_override(actor, scene, item_id);
		if (override.value.item_id != 0) {
			item_row_t *item_row = get_item_row(override.value.looks_like_item_id);
			if (item_row == NULL) {
			    item_row = get_item_row(override.value.item_id);
		    }

			if (item_row->chest_type & 0x01) {
				// Small chest
				size = 5;
			}
			else {
				// Big chest
				size = 0;
			}

		    if (item_row->chest_type & 0x02) {
				// Gold chest
				color = 2;
			}
			else {
				// Wood chest
				color = 0;
			}
		}
	}

	((uint8_t*)actor)[0x01EC] = size;
	((uint8_t*)actor)[0x01ED] = color;
}
