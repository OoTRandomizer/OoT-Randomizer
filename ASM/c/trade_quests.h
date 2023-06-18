#ifndef TRADE_QUESTS_H
#define TRADE_QUESTS_H

#include "util.h"
#include "z64.h"
#include "shop_actors.h"

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

#endif
