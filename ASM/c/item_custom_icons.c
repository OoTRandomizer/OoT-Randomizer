#include "z64.h"
#include "player.h"
#include "gfx.h"

// An "item icon" (gItemIcon*Tex) is 32x32 rgba32
#define ITEM_ICON_WIDTH 32
#define ITEM_ICON_HEIGHT 32
#define ITEM_ICON_SIZE (ITEM_ICON_WIDTH * ITEM_ICON_HEIGHT * 4) // The size in bytes of an item icon
#define GET_ITEM_ICON_VROM(itemId) (uintptr_t)(_icon_item_staticSegmentRomStart + (itemId*ITEM_ICON_SIZE))

// Note that z_kaleido_scope.c assumes that the dimensions and texture format here also matches the dimensions and
// texture format for MAP_NAME_TEX1_*
#define ITEM_NAME_TEX_WIDTH 128
#define ITEM_NAME_TEX_HEIGHT 16
#define ITEM_NAME_TEX_SIZE ((ITEM_NAME_TEX_WIDTH * ITEM_NAME_TEX_HEIGHT) / 2) // 128x16 IA4 texture

extern uint8_t _icon_item_staticSegmentRomStart[];
extern uint8_t _item_name_staticSegmentRomStart[];

// Get icon id from C button item
uint16_t Interface_GetCustomIconId(uint8_t button) {
    switch (z64_file.button_items[button]) {
        case ITEM_NAVI_BELL:
            return ITEM_SOLD_OUT;
        default:
            return z64_file.button_items[button];
    }
}

// Texture for transferring item from kaleidoscope to C button
void* Interface_GetCustomEquipIcon(uint16_t equipTargetItem) {
    if (equipTargetItem == ITEM_NAVI_BELL) {
        return z64_ItemIcons[ITEM_SOLD_OUT];
    } else {
        return z64_ItemIcons[equipTargetItem];
    }
}

// z_construct Interface_Init
// Replaces all button icon loads
void Interface_LoadInitCustomItemIcon(z64_game_t* play) {
    uint8_t button;
    for (button = 0; button < 4; button++) {
        if (z64_file.button_items[button] < 0xF0 || (button == 0 && z64_file.button_items[0] != 0xFF)) {
            uint16_t itemIconId = Interface_GetCustomIconId(button);
            DmaMgr_RequestSync(play->iconItemSegment + (button * ITEM_ICON_SIZE),
                                GET_ITEM_ICON_VROM(itemIconId), ITEM_ICON_SIZE);
        }
    }
}

// z_parameter Interface_LoadItemIcon1
void Interface_LoadCustomItemIcon1(z64_game_t* play, uint16_t button) {
    uint16_t itemIconId = Interface_GetCustomIconId(button);
    DmaMgr_RequestAsync(&play->dmaRequest_160, play->iconItemSegment + (button * ITEM_ICON_SIZE),
                        GET_ITEM_ICON_VROM(itemIconId), ITEM_ICON_SIZE, 0, &play->loadQueue, NULL);
}

// Interface_LoadItemIcon2
void Interface_LoadCustomItemIcon2(z64_game_t* play, uint16_t button) {
    uint16_t itemIconId = Interface_GetCustomIconId(button);
    DmaMgr_RequestAsync(&play->dmaRequest_180, play->iconItemSegment + (button * ITEM_ICON_SIZE),
                        GET_ITEM_ICON_VROM(itemIconId), ITEM_ICON_SIZE, 0, &play->loadQueue, NULL);
}

// KaleidoScope_UpdateNamePanel
void KaleidoScope_LoadCustomName(z64_game_t* play) {
    uint16_t texIndex;

    if (play->pause_ctxt.item_id == ITEM_NAVI_BELL) {
        texIndex = (ITEM_SOLD_OUT + (z64_file.language * 123));
    } else {
        texIndex = (play->pause_ctxt.item_id + (z64_file.language * 123));
    }

    DmaMgr_RequestSync(play->pause_ctxt.name_texture,
                                 (uintptr_t)_item_name_staticSegmentRomStart + (texIndex * ITEM_NAME_TEX_SIZE),
                                 ITEM_NAME_TEX_SIZE);
}
