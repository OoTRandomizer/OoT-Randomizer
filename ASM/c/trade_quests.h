#ifndef TRADE_QUESTS_H
#define TRADE_QUESTS_H

#include "util.h"
#include "z64.h"

uint16_t SaveFile_NextOwnedTradeItem(uint16_t itemId);
uint16_t SaveFile_PrevOwnedTradeItem(uint16_t itemId);

void SaveFile_SetTradeItemAsOwned(uint16_t itemId);
void SaveFile_UnsetTradeItemAsOwned(uint16_t itemId);

uint16_t IsTradeItem(uint16_t itemId);
uint16_t IsAdultTradeItem(uint16_t itemId);
uint16_t GetTradeItemIndex(uint16_t itemId);

int16_t GetTradeSlot(uint16_t itemId);
void UpdateTradeEquips(uint16_t itemId, int16_t trade_slot);
void TurnInTradeItem(uint16_t itemId);

typedef struct {
    uint16_t index;
    uint16_t item_id;
    uint16_t exchange_item_id;
    int16_t action_parameter;
    char name[20];
} exchange_item_t;

extern const exchange_item_t trade_quest_items[22];

typedef struct
{
    z64_actor_t  actor;                     /* 0x0000 */
    char         unk_00_[0x009F];           /* 0x013C */
    uint8_t      happyMaskShopState;        /* 0x01DB */
    uint8_t      happyMaskShopkeeperEyeIdx; /* 0x01DC */
    char         unk_01_[0x000F];           /* 0x01DD */
    int16_t      stateFlag;                 /* 0x01EC */
    char         unk_02_[0x00DA];           /* 0x01EE */
                                            /* 0x02C8 */
} EnOssan;

typedef enum {
    /* 00 */ OSSAN_STATE_IDLE,
    /* 01 */ OSSAN_STATE_START_CONVERSATION,
    /* 02 */ OSSAN_STATE_FACING_SHOPKEEPER,
    /* 03 */ OSSAN_STATE_TALKING_TO_SHOPKEEPER,
    /* 04 */ OSSAN_STATE_LOOK_SHELF_LEFT,
    /* 05 */ OSSAN_STATE_LOOK_SHELF_RIGHT,
    /* 06 */ OSSAN_STATE_BROWSE_LEFT_SHELF,
    /* 07 */ OSSAN_STATE_BROWSE_RIGHT_SHELF,
    /* 08 */ OSSAN_STATE_LOOK_SHOPKEEPER, // From looking at shelf
    /* 09 */ OSSAN_STATE_SELECT_ITEM,     // Select most items
    /* 10 */ OSSAN_STATE_SELECT_ITEM_MILK_BOTTLE,
    /* 11 */ OSSAN_STATE_SELECT_ITEM_WEIRD_EGG,
    /* 12 */ OSSAN_STATE_SELECT_ITEM_UNIMPLEMENTED, // Handles two unfinished shop items
    /* 13 */ OSSAN_STATE_SELECT_ITEM_BOMBS,
    /* 14 */ OSSAN_STATE_CANT_GET_ITEM,
    /* 15 */ OSSAN_STATE_GIVE_ITEM_FANFARE, // Give Item, hold it up with fanfare
    /* 16 */ OSSAN_STATE_ITEM_PURCHASED,
    /* 17 */ OSSAN_STATE_CONTINUE_SHOPPING_PROMPT,
    /* 18 */ OSSAN_STATE_GIVE_LON_LON_MILK,
    /* 19 */ OSSAN_STATE_DISPLAY_ONLY_BOMB_DIALOG,          // Turn to shopkeeper, talk about fake bombs
    /* 20 */ OSSAN_STATE_WAIT_FOR_DISPLAY_ONLY_BOMB_DIALOG, // Can't Get Goron City Bombs
    /* 21 */ OSSAN_STATE_21,                                // Unused
    /* 22 */ OSSAN_STATE_22,                                // Follows OSSAN_STATE_21
    /* 23 */ OSSAN_STATE_QUICK_BUY,
    /* 24 */ OSSAN_STATE_SELECT_ITEM_MASK,
    /* 25 */ OSSAN_STATE_LEND_MASK_OF_TRUTH, // First time all masks are sold
    /* 26 */ OSSAN_STATE_DISCOUNT_DIALOG     // Hylian Shield Discount
} EnOssanState;

typedef enum {
    OSSAN_HAPPY_STATE_REQUEST_PAYMENT_KEATON_MASK,
    OSSAN_HAPPY_STATE_REQUEST_PAYMENT_SPOOKY_MASK,
    OSSAN_HAPPY_STATE_REQUEST_PAYMENT_SKULL_MASK,
    OSSAN_HAPPY_STATE_REQUEST_PAYMENT_BUNNY_HOOD,
    OSSAN_HAPPY_STATE_BORROWED_FIRST_MASK,
    OSSAN_HAPPY_STATE_ANGRY,          // Give me my money man!
    OSSAN_HAPPY_STATE_ALL_MASKS_SOLD, // All masks have been sold
    OSSAN_HAPPY_STATE_NONE = 8        // No Action / Payment received!
} EnOssanHappyMaskState;

typedef enum {
    /* 0 */ CANBUY_RESULT_SUCCESS_FANFARE,
    /* 1 */ CANBUY_RESULT_SUCCESS,
    /* 2 */ CANBUY_RESULT_CANT_GET_NOW,
    /* 3 */ CANBUY_RESULT_NEED_BOTTLE,
    /* 4 */ CANBUY_RESULT_NEED_RUPEES,
    /* 5 */ CANBUY_RESULT_CANT_GET_NOW_5
} EnGirlACanBuyResult;

#endif
