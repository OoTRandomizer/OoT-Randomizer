#ifndef SHOP_ACTORS_H
#define SHOP_ACTORS_H

#include "z64.h"

struct EnGirlA;

typedef void (*EnGirlAActionFunc)(struct EnGirlA*, z64_game_t*);
typedef void (*EnGirlA2Func)(z64_game_t*, struct EnGirlA*);
typedef void (*EnGirlA3Func)(z64_actor_t*, z64_game_t*, int32_t);
typedef int32_t (*EnGirlA4Func)(z64_game_t*, struct EnGirlA*);

typedef struct {
    z64_actor_t       actor;                     /* 0x0000 */
    char              unk_00_[0x0048];           /* 0x013C */
    int8_t            objBankIndex;              /* 0x0184 */
    EnGirlAActionFunc actionFunc2;               /* 0x0188 */
    int32_t           isInitialized;             /* 0x018C */
    int16_t           itemBuyPromptTextId;       /* 0x0190 */
    int32_t           getItemId;                 /* 0x0194 */
    int16_t           isInvisible;               /* 0x0198 */
    EnGirlA2Func      setOutOfStockFunc;         /* 0x019C */
    EnGirlA2Func      updateStockedItemFunc;     /* 0x01A0 */
    int16_t           isSelected;                /* 0x01A4 */
    int16_t           yRotationInit;             /* 0x01A6 */
    int16_t           yRotation;                 /* 0x01A8 */
    EnGirlA4Func      canBuyFunc;                /* 0x01AC */
    EnGirlA2Func      itemGiveFunc;              /* 0x01B0 */
    EnGirlA2Func      buyEventFunc;              /* 0x01B4 */
    int16_t           basePrice;                 /* 0x01B8 */
    int16_t           itemCount;                 /* 0x01BA */
    int16_t           giDrawId;                  /* 0x01BC */
    EnGirlA3Func      hiliteFunc;                /* 0x01C0 */
                                                 /* 0x01C4 */
} EnGirlA;

typedef struct {
    int16_t objID;                                              /* 0x00 */
    int16_t giDrawId;                                           /* 0x02 */
    void (*hiliteFunc)(z64_actor_t*, z64_game_t*, int32_t);     /* 0x04 */
    int16_t price;                                              /* 0x08 */
    int16_t count;                                              /* 0x0A */
    uint16_t itemDescTextId;                                    /* 0x0C */
    uint16_t itemBuyPromptTextId;                               /* 0x0E */
    int32_t getItemId;                                          /* 0x10 */
    int32_t (*canBuyFunc)(z64_game_t*, EnGirlA*);               /* 0x14 */
    void (*itemGiveFunc)(z64_game_t*, EnGirlA*);                /* 0x18 */
    void (*buyEventFunc)(z64_game_t*, EnGirlA*);                /* 0x1C */
                                                                /* 0x20 */
} ShopItemEntry;

typedef struct
{
    z64_actor_t  actor;                     /* 0x0000 */
    char         unk_00_[0x009F];           /* 0x013C */
    uint8_t      happyMaskShopState;        /* 0x01DB */
    uint8_t      happyMaskShopkeeperEyeIdx; /* 0x01DC */
    char         unk_01_[0x000F];           /* 0x01DD */
    int16_t      stateFlag;                 /* 0x01EC */
    int16_t      tempStateFlag;             /* 0x01EE */
    EnGirlA*     shelfSlots[8];             /* 0x01F0 */
    // Shelves are indexed as such:
    /* 7 5  3 1 */
    /* 6 4  2 0 */
    char         unk_02_[0x0032];           /* 0x0210 */
    uint8_t      cursorIndex;               /* 0x0242 */
    char         unk_03_[0x0084];           /* 0x0244 */
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
