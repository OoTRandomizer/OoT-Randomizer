#include "message.h"
#include "stdbool.h"
#include "save.h"
#include "dungeon_info.h"

// no support for kana since they're not part of the message charset
char FILENAME_ENCODING[256] = {
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '?', '?', '?', '?', '?', '?',
    '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?',
    '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?',
    '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?',
    '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?',
    '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?',
    '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?',
    '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?',
    '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?',
    '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?',
    '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', 'A', 'B', 'C', 'D', 'E',
    'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
    'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
    'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', ' ',
    '?', '?', '!', ':', '-', '(', ')', '?', '?', ',', '.', '/', '?', '?', '?', '?',
    '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?',
};

extern uint8_t PLAYER_NAMES[256][8];
extern uint8_t PLAYER_NAME_ID;

// Helper function for adding characters to the decoded message buffer
void Message_AddCharacter(MessageContext* msgCtx, void* pFont, uint32_t* pDecodedBufPos, uint32_t* pCharTexIdx, uint8_t charToAdd) {
    uint32_t decodedBufPosVal = *pDecodedBufPos;
    uint32_t charTexIdx = *pCharTexIdx;
    msgCtx->msgBufDecoded[decodedBufPosVal++] = charToAdd; // Add the character to the output buffer, increment the output position
    if (charToAdd != ' ') { // Only load the character texture if it's not a space.
        Font_LoadChar(pFont, charToAdd - ' ', charTexIdx); // Load the character texture
        charTexIdx += 0x80; // Increment the texture pointer
    }

    // Copy our locals back to their pointers
    *pDecodedBufPos = decodedBufPosVal;
    *pCharTexIdx = charTexIdx;
}

// Helper function for adding integer numbers to the decoded message buffer
void Message_AddInteger(MessageContext* msgCtx, void* pFont, uint32_t* pDecodedBufPos, uint32_t* pCharTexIdx, uint32_t numToAdd) {
    uint8_t digits[10];
    uint8_t i = 0;
    // Extract each digit. They are added, in reverse order, to digits[]
    do {
        digits[i] = numToAdd % 10;
        numToAdd = numToAdd / 10;
        i++;
    }
    // Loop through each digit in digits[] and add the character to the decoded buffer.
    while (numToAdd > 0);

    for (uint8_t c = i; c > 0; c--) {
        Message_AddCharacter(msgCtx, pFont, pDecodedBufPos, pCharTexIdx, '0' + digits[c - 1]);
    }
}

// Helper function for adding simple strings to the decoded message buffer. Does not support additional control codes.
void Message_AddString(MessageContext* msgCtx, void* pFont, uint32_t* pDecodedBufPos, uint32_t* pCharTexIdx, char* stringToAdd) {
    while (*stringToAdd != 0) {
        Message_AddCharacter(msgCtx, pFont, pDecodedBufPos, pCharTexIdx, *stringToAdd);
        stringToAdd++;
    }
}

// Helper function for adding a filename to the decoded message buffer. Filenames use a different character set from other text.
void Message_AddFileName(MessageContext* msgCtx, void* pFont, uint32_t* pDecodedBufPos, uint32_t* pCharTexIdx, uint8_t* filenameToAdd) {
    int end = 8;
    while (filenameToAdd[end - 1] == 0xDF) {
        // trim trailing space
        end--;
    }
    for (int i = 0; i < end; i++) {
        Message_AddCharacter(msgCtx, pFont, pDecodedBufPos, pCharTexIdx, FILENAME_ENCODING[filenameToAdd[i]]);
    }
}

// Hack to add additional text control codes.
// If additional codes need to be read after the primary code, increment msgCtx->msgBufPos and index msgRaw
// To add a new control code:
//      Compare currChar to the control code.
//          Add text to the output buffer by performing the following:
//          Call one of the above functions to add the text.
//          Subtract 1 from* pDecodedBufPos
//          Return true
bool Message_Decode_Additional_Control_Codes(uint8_t currChar, uint32_t* pDecodedBufPos, uint32_t* pCharTexIdx) {
    MessageContext* msgCtx = &(z64_game.msgContext);
    Font* pFont = &(msgCtx->font); // Get a reference to the font.
    char* msgRaw = (char*) &(pFont->msgBuf); // Get a reference to the start of the raw message. Index using msgCtx->msgBufPos.

    switch (currChar) {
        case 0xF0: {
            // Silver rupee puzzle control code
            // Get the next character which tells us which puzzle it's for
            uint8_t puzzle = msgRaw[++(msgCtx->msgBufPos)];
            uint8_t count = extended_savectx.silver_rupee_counts[puzzle];
            Message_AddInteger(msgCtx, pFont, pDecodedBufPos, pCharTexIdx, count);
            (*pDecodedBufPos)--;
            return true;
        }
        case 0xF1: {
            // Small key count
            // Get the next character which tells us which dungeon it's for
            uint8_t dungeon = msgRaw[++(msgCtx->msgBufPos)];
            uint8_t count = z64_file.scene_flags[dungeon].unk_00_ >> 0x10;
            Message_AddInteger(msgCtx, pFont, pDecodedBufPos, pCharTexIdx, count);
            (*pDecodedBufPos)--;
            return true;
        }
        case 0xF2: {
            // Outgoing item filename
            Message_AddFileName(msgCtx, pFont, pDecodedBufPos, pCharTexIdx, PLAYER_NAMES[PLAYER_NAME_ID]);
            (*pDecodedBufPos)--;
            return true;
        }
        case 0xF3: {
            // Farore's Wind destination
            switch (z64_file.respawn[RESPAWN_MODE_TOP].entranceIndex) {
                case 0x000:
                case 0x252: {
                    // Deku Tree
                    Message_AddString(msgCtx, pFont, pDecodedBufPos, pCharTexIdx, dungeons[0].name);
                    break;
                }
                case 0x004:
                case 0x0C5: {
                    // DC
                    Message_AddString(msgCtx, pFont, pDecodedBufPos, pCharTexIdx, dungeons[1].name);
                    break;
                }
                case 0x028:
                case 0x407: {
                    // Jabu
                    Message_AddString(msgCtx, pFont, pDecodedBufPos, pCharTexIdx, dungeons[2].name);
                    break;
                }
                case 0x169:
                case 0x24E: {
                    // Forest Temple
                    Message_AddString(msgCtx, pFont, pDecodedBufPos, pCharTexIdx, dungeons[3].name);
                    break;
                }
                case 0x165:
                case 0x175: {
                    // Fire Temple
                    Message_AddString(msgCtx, pFont, pDecodedBufPos, pCharTexIdx, dungeons[4].name);
                    break;
                }
                case 0x010:
                case 0x423: {
                    // Water Temple
                    Message_AddString(msgCtx, pFont, pDecodedBufPos, pCharTexIdx, dungeons[5].name);
                    break;
                }
                case 0x037:
                case 0x2B2: {
                    // Shadow Temple
                    Message_AddString(msgCtx, pFont, pDecodedBufPos, pCharTexIdx, dungeons[6].name);
                    break;
                }
                case 0x082:
                case 0x2F5:
                case 0x3F0:
                case 0x3F4: {
                    // Spirit Temple
                    Message_AddString(msgCtx, pFont, pDecodedBufPos, pCharTexIdx, dungeons[7].name);
                    break;
                }
                case 0x098: {
                    // BotW
                    Message_AddString(msgCtx, pFont, pDecodedBufPos, pCharTexIdx, dungeons[8].name);
                    break;
                }
                case 0x088: {
                    // Ice
                    Message_AddString(msgCtx, pFont, pDecodedBufPos, pCharTexIdx, dungeons[9].name);
                    break;
                }
                case 0x008: {
                    // GTG
                    Message_AddString(msgCtx, pFont, pDecodedBufPos, pCharTexIdx, dungeons[11].name);
                    break;
                }
                case 0x41B:
                case 0x467:
                case 0x534:
                case 0x538:
                case 0x53C:
                case 0x540:
                case 0x544:
                case 0x548:
                case 0x54C: {
                    // Ganon
                    Message_AddString(msgCtx, pFont, pDecodedBufPos, pCharTexIdx, dungeons[12].name);
                    break;
                }
                default: {
                    // Vanilla text
                    Message_AddString(msgCtx, pFont, pDecodedBufPos, pCharTexIdx, "the Warp Point");
                    break;
                }
            }
            (*pDecodedBufPos)--;
            return true;
        }
        default: {
            return false;
        }
    }
}

uint8_t shooting_gallery_show_message = 0;
// Displays a warning message if player did adult shooting gallery without bow.
void shooting_gallery_message() {
    // Child/Adult shooting galleries actor is the same, so the asm hook will work for both.
    // We only want the message for Adult.
    if (!LINK_IS_ADULT) {
        return;
    }
    // Check if we have a bow.
    if (z64_file.items[ITEM_BOW] != ITEM_NONE) {
        return;
    }
    // Check if the message was already displayed once.
    if (shooting_gallery_show_message != 0) {
        return;
    }
    shooting_gallery_show_message = 1;
}

uint8_t treasure_chest_game_show_message = 0;
// Displays a warning message if the player attempted the Treasure Chest Game without
// Lens of Truth when settings require it.
void treasure_chest_game_message() {
    if (z64_file.items[Z64_SLOT_LENS] != Z64_ITEM_LENS || !z64_file.magic_acquired) {
        treasure_chest_game_show_message = 1;
    }
}

extern uint8_t EQUIPMENT_TEXTBOX;
uint8_t kokiri_sword_message = 0;
uint8_t biggoron_sword_message = 0;
uint8_t deku_shield_message = 0;
uint8_t hylian_shield_message = 0;
uint8_t mirror_shield_message = 0;
uint8_t goron_tunic_message = 0;
uint8_t zora_tunic_message = 0;
void manage_kokiri_sword_message() {
    if (kokiri_sword_message == 1 &&
        z64_MessageGetState(((uint8_t *)(&z64_game)) + 0x20D8) == 0) {
        z64_DisplayTextbox(&z64_game, 0x045E, 0);
        kokiri_sword_message = 2;
    }
    if (kokiri_sword_message == 2) {
        MessageContext *msgCtx = &(z64_game.msgContext);
        z64_link.common.frozen = 10;
        if (Message_ShouldAdvance(&z64_game)) {
            if (msgCtx->choiceIndex == 0) {
                z64_file.button_items[0] = Z64_ITEM_KOKIRI_SWORD;
                Interface_LoadItemIcon1(&z64_game, 0);
                Inventory_ChangeEquipment(EQUIP_TYPE_SWORD, EQUIP_VALUE_SWORD_KOKIRI);
            }
            kokiri_sword_message = 0;
        }
    }
}

void manage_biggoron_sword_message() {
    if (biggoron_sword_message == 1 &&
        z64_MessageGetState(((uint8_t *)(&z64_game)) + 0x20D8) == 0) {
        z64_DisplayTextbox(&z64_game, 0x045E, 0);
        biggoron_sword_message = 2;
    }
    if (biggoron_sword_message == 2) {
        MessageContext *msgCtx = &(z64_game.msgContext);
        z64_link.common.frozen = 10;
        if (Message_ShouldAdvance(&z64_game)) {
            if (msgCtx->choiceIndex == 0) {
                z64_file.button_items[0] = Z64_ITEM_BIGGORON_SWORD;
                Interface_LoadItemIcon1(&z64_game, 0);
                Inventory_ChangeEquipment(EQUIP_TYPE_SWORD, EQUIP_VALUE_SWORD_BIGGORON);
            }
            biggoron_sword_message = 0;
        }
    }
}

void manage_deku_shield_message() {
    if (deku_shield_message == 1 &&
        z64_MessageGetState(((uint8_t *)(&z64_game)) + 0x20D8) == 0) {
        z64_DisplayTextbox(&z64_game, 0x045E, 0);
        deku_shield_message = 2;
    }
    if (deku_shield_message == 2) {
        MessageContext *msgCtx = &(z64_game.msgContext);
        z64_link.common.frozen = 10;
        if (Message_ShouldAdvance(&z64_game)) {
            if (msgCtx->choiceIndex == 0) {
                Inventory_ChangeEquipment(EQUIP_TYPE_SHIELD, EQUIP_VALUE_SHIELD_DEKU);
            }
            deku_shield_message = 0;
        }
    }
}

void manage_hylian_shield_message() {
    if (hylian_shield_message == 1 &&
        z64_MessageGetState(((uint8_t *)(&z64_game)) + 0x20D8) == 0) {
        z64_DisplayTextbox(&z64_game, 0x045E, 0);
        hylian_shield_message = 2;
    }
    if (hylian_shield_message == 2) {
        MessageContext *msgCtx = &(z64_game.msgContext);
        z64_link.common.frozen = 10;
        if (Message_ShouldAdvance(&z64_game)) {
            if (msgCtx->choiceIndex == 0) {
                Inventory_ChangeEquipment(EQUIP_TYPE_SHIELD, EQUIP_VALUE_SHIELD_HYLIAN);
            }
            hylian_shield_message = 0;
        }
    }
}

void manage_mirror_shield_message() {
    if (mirror_shield_message == 1 &&
        z64_MessageGetState(((uint8_t *)(&z64_game)) + 0x20D8) == 0) {
        z64_DisplayTextbox(&z64_game, 0x045E, 0);
        mirror_shield_message = 2;
    }
    if (mirror_shield_message == 2) {
        MessageContext *msgCtx = &(z64_game.msgContext);
        z64_link.common.frozen = 10;
        if (Message_ShouldAdvance(&z64_game)) {
            if (msgCtx->choiceIndex == 0) {
                Inventory_ChangeEquipment(EQUIP_TYPE_SHIELD, EQUIP_VALUE_SHIELD_MIRROR);
            }
            mirror_shield_message = 0;
        }
    }
}

void manage_goron_tunic_message() {
    if (goron_tunic_message == 1 &&
        z64_MessageGetState(((uint8_t *)(&z64_game)) + 0x20D8) == 0) {
        z64_DisplayTextbox(&z64_game, 0x045E, 0);
        goron_tunic_message = 2;
    }
    if (goron_tunic_message == 2) {
        MessageContext *msgCtx = &(z64_game.msgContext);
        z64_link.common.frozen = 10;
        if (Message_ShouldAdvance(&z64_game)) {
            if (msgCtx->choiceIndex == 0) {
                Inventory_ChangeEquipment(EQUIP_TYPE_TUNIC, EQUIP_VALUE_TUNIC_GORON);
            }
            goron_tunic_message = 0;
        }
    }
}

void manage_zora_tunic_message() {
    if (zora_tunic_message == 1 &&
        z64_MessageGetState(((uint8_t *)(&z64_game)) + 0x20D8) == 0) {
        z64_DisplayTextbox(&z64_game, 0x045E, 0);
        zora_tunic_message = 2;
    }
    if (zora_tunic_message == 2) {
        MessageContext *msgCtx = &(z64_game.msgContext);
        z64_link.common.frozen = 10;
        if (Message_ShouldAdvance(&z64_game)) {
            if (msgCtx->choiceIndex == 0) {
                Inventory_ChangeEquipment(EQUIP_TYPE_TUNIC, EQUIP_VALUE_TUNIC_ZORA);
            }
            zora_tunic_message = 0;
        }
    }
}

// Function to display custom textboxes ingame.
void display_misc_messages() {
    if (z64_MessageGetState(((uint8_t *)(&z64_game)) + 0x20D8) == 0) {
        // Each minigame warning message can only be triggered in their respective
        // scenes. Order doesn't matter.
        if (shooting_gallery_show_message == 1) {
            z64_DisplayTextbox(&z64_game, 0x045C, 0);
            // To avoid displaying the message several times if the player just wants to farm the 50 rupees.
            shooting_gallery_show_message = -1;
        } else if (treasure_chest_game_show_message) {
            z64_DisplayTextbox(&z64_game, 0x045D, 0);
            // No reason not to repeat the message on a reattempt in case the player forgot.
            treasure_chest_game_show_message = 0;
        }
    }
    if (EQUIPMENT_TEXTBOX & 1 << 0) {
        manage_deku_shield_message();
        manage_hylian_shield_message();
        manage_mirror_shield_message();
    }
    if (EQUIPMENT_TEXTBOX & 1 << 1) {
        manage_kokiri_sword_message();
        manage_biggoron_sword_message();
    }
    if (EQUIPMENT_TEXTBOX & 1 << 2) {
        manage_goron_tunic_message();
        manage_zora_tunic_message();
    }
}

void equip_kokiri_sword_message(z64_file_t* save, int16_t arg1, int16_t arg2) {
    if (LINK_IS_ADULT) {
        return;
    }
    // If kokiri sword is already equipped.
    if (z64_file.equip_sword == 1) {
        return;
    }
    kokiri_sword_message = 1;
}

void equip_biggoron_sword_message(z64_file_t* save, int16_t arg1, int16_t arg2) {
    if (!LINK_IS_ADULT) {
        return;
    }
    // If biggoron sword is already equipped.
    if (z64_file.equip_sword == 3) {
        return;
    }
    biggoron_sword_message = 1;
}

void equip_deku_shield_message(z64_file_t* save, int16_t arg1, int16_t arg2) {
    if (LINK_IS_ADULT) {
        return;
    }
    // If a deku shield is already equipped.
    if (z64_file.equip_shield == 1) {
        return;
    }
    deku_shield_message = 1;
}

void equip_hylian_shield_message(z64_file_t* save, int16_t arg1, int16_t arg2) {
    // Only ask for child if he has no shield equipped at all.
    if (!LINK_IS_ADULT) {
        if (z64_file.equip_shield == 1) {
            return;
        }
    }
    // If a hylian shield or mirror shield is already equipped.
    if (z64_file.equip_shield > 1) {
        return;
    }
    hylian_shield_message = 1;
}

void equip_mirror_shield_message(z64_file_t* save, int16_t arg1, int16_t arg2) {
    if (!LINK_IS_ADULT) {
        return;
    }
    // If mirror shield is already equipped.
    if (z64_file.equip_shield == 3) {
        return;
    }
    mirror_shield_message = 1;
}

void equip_goron_tunic_message(z64_file_t* save, int16_t arg1, int16_t arg2) {
    if (!LINK_IS_ADULT) {
        return;
    }
    // If a goron tunic is already equipped.
    if (z64_file.equip_tunic == 2) {
        return;
    }
    goron_tunic_message = 1;
}

void equip_zora_tunic_message(z64_file_t* save, int16_t arg1, int16_t arg2) {
    if (!LINK_IS_ADULT) {
        return;
    }
    // If a zora tunic is already equipped.
    if (z64_file.equip_shield == 3) {
        return;
    }
    zora_tunic_message = 1;
}
