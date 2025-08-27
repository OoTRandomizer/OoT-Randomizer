#include "trade_quests.h"

extern uint8_t CFG_ADULT_TRADE_SHUFFLE;

const exchange_item_t trade_quest_items[] = {
    {  0, Z64_ITEM_WEIRD_EGG,           Z64_EXCH_ITEM_WEIRD_EGG,    PLAYER_AP_WEIRD_EGG    , 0 }, // "Weird Egg"
    {  1, Z64_ITEM_CHICKEN,             Z64_EXCH_ITEM_CHICKEN,      PLAYER_AP_CHICKEN      , 0 }, // "Chicken"
    {  2, Z64_ITEM_ZELDAS_LETTER,       Z64_EXCH_ITEM_LETTER_ZELDA, PLAYER_AP_LETTER_ZELDA , 0 }, // "Zelda's Letter"
    {  3, Z64_ITEM_KEATON_MASK,         Z64_EXCH_ITEM_MASK_KEATON,  PLAYER_AP_MASK_KEATON  , 0 }, // "Keaton Mask"
    {  4, Z64_ITEM_SKULL_MASK,          Z64_EXCH_ITEM_MASK_SKULL,   PLAYER_AP_MASK_SKULL   , 0 }, // "Skull Mask"
    {  5, Z64_ITEM_SPOOKY_MASK,         Z64_EXCH_ITEM_MASK_SPOOKY,  PLAYER_AP_MASK_SPOOKY  , 0 }, // "Spooky Mask"
    {  6, Z64_ITEM_BUNNY_HOOD,          Z64_EXCH_ITEM_MASK_BUNNY,   PLAYER_AP_MASK_BUNNY   , 0 }, // "Bunny Hood"
    {  7, Z64_ITEM_GORON_MASK,          Z64_EXCH_ITEM_MASK_GORON,   PLAYER_AP_MASK_GORON   , 0 }, // "Goron Mask"
    {  8, Z64_ITEM_ZORA_MASK,           Z64_EXCH_ITEM_MASK_ZORA,    PLAYER_AP_MASK_ZORA    , 0 }, // "Zora Mask"
    {  9, Z64_ITEM_GERUDO_MASK,         Z64_EXCH_ITEM_MASK_GERUDO,  PLAYER_AP_MASK_GERUDO  , 0 }, // "Gerudo Mask"
    { 10, Z64_ITEM_MASK_OF_TRUTH,       Z64_EXCH_ITEM_MASK_TRUTH,   PLAYER_AP_MASK_TRUTH   , 0 }, // "Mask of Truth"
    { 11, Z64_ITEM_POCKET_EGG,          Z64_EXCH_ITEM_POCKET_EGG,   PLAYER_AP_POCKET_EGG   , 0 }, // "Pocket Egg"
    { 12, Z64_ITEM_POCKET_CUCCO,        Z64_EXCH_ITEM_POCKET_CUCCO, PLAYER_AP_POCKET_CUCCO , 0 }, // "Pocket Cucco"
    { 13, Z64_ITEM_COJIRO,              Z64_EXCH_ITEM_COJIRO,       PLAYER_AP_COJIRO       , 0 }, // "Cojiro"
    { 14, Z64_ITEM_ODD_MUSHROOM,        Z64_EXCH_ITEM_ODD_MUSHROOM, PLAYER_AP_ODD_MUSHROOM , 0 }, // "Odd Mushroom"
    { 15, Z64_ITEM_ODD_POTION,          Z64_EXCH_ITEM_ODD_POTION,   PLAYER_AP_ODD_POTION   , 0 }, // "Odd Potion"
    { 16, Z64_ITEM_POACHERS_SAW,        Z64_EXCH_ITEM_SAW,          PLAYER_AP_SAW          , 0 }, // "Poacher's Saw"
    { 17, Z64_ITEM_BROKEN_GORONS_SWORD, Z64_EXCH_ITEM_SWORD_BROKEN, PLAYER_AP_SWORD_BROKEN , 0 }, // "Broken Goron Sword"
    { 18, Z64_ITEM_PRESCRIPTION,        Z64_EXCH_ITEM_PRESCRIPTION, PLAYER_AP_PRESCRIPTION , 0 }, // "Prescription"
    { 19, Z64_ITEM_EYEBALL_FROG,        Z64_EXCH_ITEM_FROG,         PLAYER_AP_FROG         , 0 }, // "Eyeball Frog"
    { 20, Z64_ITEM_EYE_DROPS,           Z64_EXCH_ITEM_EYEDROPS,     PLAYER_AP_EYEDROPS     , 0 }, // "Eye Drops"
    { 21, Z64_ITEM_CLAIM_CHECK,         Z64_EXCH_ITEM_CLAIM_CHECK,  PLAYER_AP_CLAIM_CHECK  , 0 }  // "Claim Check"
};

// Rupees to pay back to Happy Mask Shop
static int16_t sMaskPaymentPrice[] = { 10, 30, 20, 50 };

uint16_t GetTradeItemIndex(uint16_t itemId) {
    if (itemId <= Z64_ITEM_MASK_OF_TRUTH) {
        return itemId - Z64_ITEM_WEIRD_EGG;
    } else {
        // Offset adult trade list for Sold Out item
        return itemId - (Z64_ITEM_WEIRD_EGG + 1);
    }
}

uint16_t GetTradeItemByAP(int16_t actionParam) {
    for (int i = 0; i < 22; i++) {
        exchange_item_t entry = trade_quest_items[i];
        if (actionParam == entry.action_parameter) {
            return entry.item_id;
        }
    }
    // Shouldn't ever get here, calling function filters for trade item APs
    return 0;
}

int16_t GetTradeSlot(uint16_t itemId) {
    if (itemId >= Z64_ITEM_WEIRD_EGG && itemId <= Z64_ITEM_MASK_OF_TRUTH) {
        return Z64_SLOT_CHILD_TRADE;
    } else if (itemId >= Z64_ITEM_POCKET_EGG && itemId <= Z64_ITEM_CLAIM_CHECK) {
        return Z64_SLOT_ADULT_TRADE;
    } else {
        return 0;
    }
}

uint16_t GetTradeItemMin(uint16_t itemId) {
    if (itemId <= Z64_ITEM_MASK_OF_TRUTH) {
        return Z64_ITEM_WEIRD_EGG;
    } else {
        return Z64_ITEM_POCKET_EGG;
    }
}

uint16_t GetTradeItemMax(uint16_t itemId) {
    if (itemId <= Z64_ITEM_MASK_OF_TRUTH) {
        return Z64_ITEM_MASK_OF_TRUTH;
    } else {
        return Z64_ITEM_CLAIM_CHECK;
    }
}

uint16_t IsTradeItem(uint16_t itemId) {
    if ((itemId >= Z64_ITEM_WEIRD_EGG && itemId <= Z64_ITEM_MASK_OF_TRUTH) || \
        (itemId >= Z64_ITEM_POCKET_EGG && itemId <= Z64_ITEM_CLAIM_CHECK)) {
        return 1;
    }
    return 0;
}

uint16_t IsAdultTradeItem(uint16_t itemId) {
    if ((itemId > Z64_ITEM_POCKET_EGG && itemId <= Z64_ITEM_CLAIM_CHECK) || \
         itemId == Z64_ITEM_BIGGORON_SWORD) {
        return 1;
    }
    return 0;
}

// Use the "unk" flags in DMT to represent trade item ownership
void SaveFile_SetTradeItemAsOwned(uint16_t itemId) {
    uint16_t tradeItemNum = GetTradeItemIndex(itemId);
    z64_file.scene_flags[0x60].unk_00_ |= (0x1 << tradeItemNum);
}

void SaveFile_UnsetTradeItemAsOwned(uint16_t itemId) {
    uint16_t tradeItemNum = GetTradeItemIndex(itemId);
    z64_file.scene_flags[0x60].unk_00_ &= ~(0x1 << tradeItemNum);
}

uint32_t SaveFile_TradeItemIsOwned(uint16_t itemId) {
    uint16_t tradeItemNum = GetTradeItemIndex(itemId);
    return (z64_file.scene_flags[0x60].unk_00_ & (0x1 << tradeItemNum)) != 0;
}

// Update trade item owned flags if the game updates the item.
// Works "forwards" for hatching eggs as both child and adult,
// and "backwards" for reverting adult trade items due to timers
// or savewarps. Note that the disabled timers hack works by
// setting the new and old item IDs to the same value, not disabling
// the function itself, so this needs to be checked before unsetting
// flags.
int32_t SaveFile_UpdateShiftableItem(uint16_t oldItemId, uint16_t newItemId) {
    if (IsTradeItem(newItemId)) {
        switch(newItemId) {
            // Eggs hatching
            case Z64_ITEM_CHICKEN:
            case Z64_ITEM_POCKET_CUCCO:
            // Timer reverts
            case Z64_ITEM_COJIRO:
            case Z64_ITEM_PRESCRIPTION:
                if (SaveFile_TradeItemIsOwned(oldItemId) && oldItemId != newItemId) {
                    SaveFile_SetTradeItemAsOwned(newItemId);
                    SaveFile_UnsetTradeItemAsOwned(oldItemId);
                    return 1;
                }
                break;
            default:
                return 0;
                break;
        }
    }
    return 0;
}

// Use the "unk" flags in DMC to represent trade item trade-in status
void SaveFile_SetTradeItemAsTraded(uint16_t itemId) {
    uint16_t tradeItemNum = GetTradeItemIndex(itemId);
    z64_file.scene_flags[0x62].unk_00_ |= (0x1 << tradeItemNum);
}

void SaveFile_UnsetTradeItemAsTraded(uint16_t itemId) {
    uint16_t tradeItemNum = GetTradeItemIndex(itemId);
    z64_file.scene_flags[0x62].unk_00_ &= ~(0x1 << tradeItemNum);
}

uint32_t SaveFile_TradeItemIsTraded(uint16_t itemId) {
    // Adult trade shuffle without full shuffle does not set traded flags
    // because of timers. Some hacks still need to know if the item was
    // traded independent of story flags. Child trade quest does not have
    // this limitation because duping by re-trading isn't possible there.
    uint16_t tradeItemNum = GetTradeItemIndex(itemId);
    uint32_t traded = (z64_file.scene_flags[0x62].unk_00_ & (0x1 << tradeItemNum)) != 0;
    if (itemId >= Z64_ITEM_POCKET_EGG && itemId <= Z64_ITEM_CLAIM_CHECK && !CFG_ADULT_TRADE_SHUFFLE) {
        return itemId < z64_file.items[Z64_SLOT_ADULT_TRADE] || traded;
    }
    return traded;
}

// Goron, Zora, Gerudo, and Mask of Truth masks have no need for Traded flags.
// Use them as paid flags for the left-side masks. In vanilla the mask
// salesman can only handle paying one mask at a time but would give access
// to everything after each payment.
void SaveFile_SetMaskAsPaid(uint16_t itemId) {
    uint16_t tradeItemNum = GetTradeItemIndex(itemId) + 4;
    z64_file.scene_flags[0x62].unk_00_ |= (0x1 << tradeItemNum);
}

uint32_t SaveFile_MaskIsPaid(uint16_t itemId) {
    uint16_t tradeItemNum = GetTradeItemIndex(itemId) + 4;
    return (z64_file.scene_flags[0x62].unk_00_ & (0x1 << tradeItemNum)) != 0;
}

uint16_t SaveFile_NextOwnedTradeItem(uint16_t itemId) {
    if (IsTradeItem(itemId)) {
        uint16_t minItem = GetTradeItemMin(itemId);
        uint16_t maxItem = GetTradeItemMax(itemId);
        uint16_t potentialItem = (itemId + 1) > maxItem ? minItem : itemId + 1;
        while ((potentialItem != itemId) && !SaveFile_TradeItemIsOwned(potentialItem)) {
            potentialItem++;
            if (potentialItem > maxItem) {
                potentialItem = minItem;
            }
        }
        return potentialItem;
    } else {
        return itemId;
    }
}

uint16_t SaveFile_PrevOwnedTradeItem(uint16_t itemId) {
    if (IsTradeItem(itemId)) {
        uint16_t minItem = GetTradeItemMin(itemId);
        uint16_t maxItem = GetTradeItemMax(itemId);
        uint16_t potentialItem = (itemId - 1) < minItem ? maxItem : itemId - 1;
        while ((potentialItem != itemId) && !SaveFile_TradeItemIsOwned(potentialItem)) {
            potentialItem--;
            if (potentialItem < minItem) {
                potentialItem = maxItem;
            }
        }
        return potentialItem;
    } else {
        return itemId;
    }
}

void UpdateTradeEquips(uint16_t itemId, int16_t tradeSlot) {
    // Update inventory slot
    z64_file.items[tradeSlot] = itemId;
    // Update player trade progression for other actors
    //z64_link.exchange_item_id = trade_quest_items[GetTradeItemIndex(itemId)].exchange_item_id;
    for (int i = 0; i < 3; i++) {
        // Handle current age C button equips, if any
        if (z64_file.c_button_slots[i] == tradeSlot) {
            z64_file.button_items[i + 1] = itemId;
            Interface_LoadItemIcon1(&z64_game, i + 1);
        }
        // Handle alternate age C button equips, if any
        if (z64_file.child_c_button_slots[i] == tradeSlot)
            z64_file.child_button_items[i + 1] = itemId;
        if (z64_file.adult_c_button_slots[i] == tradeSlot)
            z64_file.adult_button_items[i + 1] = itemId;
    }
}

void TurnInTradeItem(uint16_t itemId) {
    if (SaveFile_TradeItemIsOwned(itemId) && !SaveFile_TradeItemIsTraded(itemId)) {
        SaveFile_SetTradeItemAsTraded(itemId);
    }
}

uint32_t IsClaimCheckTraded() {
    return SaveFile_TradeItemIsTraded(Z64_ITEM_CLAIM_CHECK);
}

z64_actor_t* IsTradeItemTraded(int16_t itemActionParam, z64_actor_t* targetActor) {
    if ((itemActionParam >= PLAYER_AP_LETTER_ZELDA && itemActionParam <= PLAYER_AP_CHICKEN) ||
        (itemActionParam >= PLAYER_AP_POCKET_EGG && itemActionParam < PLAYER_AP_CLAIM_CHECK)) {
        uint16_t itemId = GetTradeItemByAP(itemActionParam);
        if (itemId != 0) {
            if (SaveFile_TradeItemIsTraded(itemId)) {
                return NULL;
            }
        }
    }
    return targetActor;
}

int32_t Inventory_ReplaceItem_Override(z64_game_t* play, uint16_t oldItem, uint16_t newItem) {
    int16_t i;
    int32_t result = 0;

    for (i = 0; i < 24; i++) {
        if (z64_file.items[i] == oldItem) {
            z64_file.items[i] = newItem;
            for (i = 1; i < 4; i++) {
                if (z64_file.button_items[i] == oldItem) {
                    z64_file.button_items[i] = newItem;
                    Interface_LoadItemIcon1(play, i);
                    break;
                }
            }
            result = 1;
        }
    }

    // Can't be a one liner or the function gets skipped if the regular
    // inventory was updated.
    int32_t update_trade = SaveFile_UpdateShiftableItem(oldItem, newItem);

    return result || update_trade;;
}

// Overrides the adult trade item slot to make Biggoron use
// his pre-Eyedrops animation until Eyedrops are turned in,
// regardless of current trade item. The ASM hook skips this
// if adult trade quest shuffle is off.
int32_t SetBiggoronAnimationState() {
    if (SaveFile_TradeItemIsOwned(Z64_ITEM_BROKEN_GORONS_SWORD) ||
        SaveFile_TradeItemIsOwned(Z64_ITEM_PRESCRIPTION) ||
        SaveFile_TradeItemIsOwned(Z64_ITEM_EYEBALL_FROG) ||
        SaveFile_TradeItemIsOwned(Z64_ITEM_EYE_DROPS)) {
        if (SaveFile_TradeItemIsTraded(Z64_ITEM_EYE_DROPS)) {
            return Z64_ITEM_CLAIM_CHECK;
        }
        return Z64_ITEM_EYE_DROPS;
    }
    return Z64_ITEM_CLAIM_CHECK;
}

// Skull kid should spawn if both Fado and Grog are
// not present. In vanilla he can spawn at the same
// time as Grog if you don't have an adult trade item,
// but Grog is changed to only show up if you find the
// Cojiro. This maintains skull kids as a viable
// rupee farming spot without getting locked out by an
// unrelated trade item.
// Because entrance rando can also lock you out of the
// trade sequence, this change is always active regardless
// of adult trade shuffle status
int32_t ShouldSkullKidSpawn() {
    if (SaveFile_TradeItemIsOwned(Z64_ITEM_COJIRO)) {
        if (!SaveFile_TradeItemIsTraded(Z64_ITEM_COJIRO)) {
            return Z64_ITEM_POCKET_EGG;
        }
    }
    if (SaveFile_TradeItemIsOwned(Z64_ITEM_ODD_POTION)) {
        if (!SaveFile_TradeItemIsTraded(Z64_ITEM_ODD_POTION)) {
            return Z64_ITEM_POCKET_EGG;
        }
    }
    return Z64_ITEM_CLAIM_CHECK;
}

int32_t IsCuccoGivenToCuccoLady() {
    return z64_link.exchange_item_id == Z64_EXCH_ITEM_POCKET_CUCCO;
}

uint16_t SetupMaskShopHelloDialogOverride(EnOssan* maskShop) {
    uint16_t traded = (z64_file.scene_flags[0x62].unk_00_ >> 0x03) & 0xF;
    uint16_t paid = (z64_file.scene_flags[0x62].unk_00_ >> 0x07) & 0xF;
    if (traded != paid) {
        if (GET_ITEMGETINF(ITEMGETINF_38)) {
            if (!GET_EVENTCHKINF(EVENTCHKINF_8C)) {
                // Pay back Keaton Mask
                maskShop->happyMaskShopState = OSSAN_HAPPY_STATE_REQUEST_PAYMENT_KEATON_MASK;
                return 0x70A5;
            }
        }
        if (GET_ITEMGETINF(ITEMGETINF_39)) {
            if (!GET_EVENTCHKINF(EVENTCHKINF_8D)) {
                // Pay back Skull Mask
                maskShop->happyMaskShopState = OSSAN_HAPPY_STATE_REQUEST_PAYMENT_SKULL_MASK;
                return 0x70C4;
            }
        }
        if (GET_ITEMGETINF(ITEMGETINF_3A)) {
            if (!GET_EVENTCHKINF(EVENTCHKINF_8E)) {
                // Pay back Spooky Mask
                maskShop->happyMaskShopState = OSSAN_HAPPY_STATE_REQUEST_PAYMENT_SPOOKY_MASK;
                return 0x70C5;
            }
        }
        if (GET_ITEMGETINF(ITEMGETINF_3B)) {
            if (!GET_EVENTCHKINF(EVENTCHKINF_8F)) {
                // Pay back Bunny Hood
                maskShop->happyMaskShopState = OSSAN_HAPPY_STATE_REQUEST_PAYMENT_BUNNY_HOOD;
                return 0x70C6;
            }
        }
        return 0x70AC;
    } else {
        if (GET_ITEMGETINF(ITEMGETINF_3B)) {
            return 0x70AC;
        } else if (!GET_ITEMGETINF(ITEMGETINF_3A) && !GET_ITEMGETINF(ITEMGETINF_24) &&
                    !GET_ITEMGETINF(ITEMGETINF_38)) {
            // Haven't borrowed the Keaton Mask
            if (!GET_ITEMGETINF(ITEMGETINF_23)) {
                return 0x70A1;
            } else {
                // Haven't sold the Keaton Mask
                // Commented line is from decomp, removed to prevent softlock taking
                // the Keaton Mask item without being able to turn the mask in.
                //maskShop->happyMaskShopState = OSSAN_HAPPY_STATE_BORROWED_FIRST_MASK;
                return 0x70A6;
            }
        } else {
            return 0x70C7;
        }
    }
}

void TryPaybackMaskOverride(EnOssan* maskShop, z64_game_t* play) {
    // The hello dialog starts with the least expensive mask.
    // This function then loops to the next cheaper traded mask.
    int16_t price = sMaskPaymentPrice[maskShop->happyMaskShopState];

    if (z64_file.rupees < price) {
        Message_ContinueTextbox(play, 0x70A8);
        maskShop->happyMaskShopkeeperEyeIdx = 1;
        maskShop->happyMaskShopState = OSSAN_HAPPY_STATE_ANGRY;
    } else {
        Rupees_ChangeBy(-price);

        if (maskShop->happyMaskShopState == OSSAN_HAPPY_STATE_REQUEST_PAYMENT_KEATON_MASK) {
            SET_EVENTCHKINF(EVENTCHKINF_8C);
            SaveFile_SetMaskAsPaid(Z64_ITEM_KEATON_MASK);
        }
        if (maskShop->happyMaskShopState == OSSAN_HAPPY_STATE_REQUEST_PAYMENT_SKULL_MASK) {
            SET_EVENTCHKINF(EVENTCHKINF_8D);
            SaveFile_SetMaskAsPaid(Z64_ITEM_SKULL_MASK);
        }
        if (maskShop->happyMaskShopState == OSSAN_HAPPY_STATE_REQUEST_PAYMENT_SPOOKY_MASK) {
            SET_EVENTCHKINF(EVENTCHKINF_8E);
            SaveFile_SetMaskAsPaid(Z64_ITEM_SPOOKY_MASK);
        }
        if (maskShop->happyMaskShopState == OSSAN_HAPPY_STATE_REQUEST_PAYMENT_BUNNY_HOOD) {
            SET_EVENTCHKINF(EVENTCHKINF_8F);
            SaveFile_SetMaskAsPaid(Z64_ITEM_BUNNY_HOOD);
        }

        uint16_t paid = (z64_file.scene_flags[0x62].unk_00_ >> 0x07) & 0xF;
        uint16_t traded = (z64_file.scene_flags[0x62].unk_00_ >> 0x03) & 0xF;

        if (traded != paid) {
            if (SaveFile_TradeItemIsTraded(Z64_ITEM_SKULL_MASK) && !SaveFile_MaskIsPaid(Z64_ITEM_SKULL_MASK)) {
                Message_ContinueTextbox(play, 0x70C4);
                maskShop->happyMaskShopState = OSSAN_HAPPY_STATE_REQUEST_PAYMENT_SKULL_MASK;
                return;
            }
            if (SaveFile_TradeItemIsTraded(Z64_ITEM_SPOOKY_MASK) && !SaveFile_MaskIsPaid(Z64_ITEM_SPOOKY_MASK)) {
                Message_ContinueTextbox(play, 0x70C5);
                maskShop->happyMaskShopState = OSSAN_HAPPY_STATE_REQUEST_PAYMENT_SPOOKY_MASK;
                return;
            }
            if (SaveFile_TradeItemIsTraded(Z64_ITEM_BUNNY_HOOD) && !SaveFile_MaskIsPaid(Z64_ITEM_BUNNY_HOOD)) {
                Message_ContinueTextbox(play, 0x70C6);
                maskShop->happyMaskShopState = OSSAN_HAPPY_STATE_REQUEST_PAYMENT_BUNNY_HOOD;
                return;
            }
        }

        if (paid == 0xF) {
            // All masks paid, give Mask of Truth slot
            Message_ContinueTextbox(play, 0x70A9);
            maskShop->happyMaskShopState = OSSAN_HAPPY_STATE_ALL_MASKS_SOLD;
        } else {
            // Traded masks so far paid in full, start shopping
            Message_ContinueTextbox(play, 0x70A7);
            maskShop->happyMaskShopState = OSSAN_HAPPY_STATE_NONE;
        }
    }
    maskShop->stateFlag = OSSAN_STATE_START_CONVERSATION;
}

int32_t CanBuy_RightSideMask() {
    uint16_t paid = (z64_file.scene_flags[0x62].unk_00_ >> 0x07) & 0xF;
    if (GET_ITEMGETINF(ITEMGETINF_3F) && paid == 0xF) {
        return CANBUY_RESULT_SUCCESS_FANFARE;
    } else {
        return CANBUY_RESULT_CANT_GET_NOW;
    }
}
