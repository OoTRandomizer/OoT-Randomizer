#include "message.h"
#include "stdbool.h"
#include "save.h"
#include "dungeon_info.h"

#define MSG_BUF_WIDE (font->msgBufWide)

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

uint16_t FILENAME_ENCODING_WIDE[256] = {
    0x824F, 0x8250, 0x8251, 0x8252, 0x8253, 0x8254, 0x8255, 0x8256, 0x8257, 0x8258, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148,
    0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148,
    0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148,
    0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148,
    0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148,
    0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148,
    0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148,
    0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148,
    0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148,
    0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148,
    0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8260, 0x8261, 0x8262, 0x8263, 0x8264,
    0x8265, 0x8266, 0x8267, 0x8268, 0x8269, 0x826A, 0x826B, 0x826C, 0x826D, 0x826E, 0x826F, 0x8270, 0x8271, 0x8272, 0x8273, 0x8274,
    0x8275, 0x8276, 0x8277, 0x8278, 0x8279, 0x8281, 0x8282, 0x8283, 0x8284, 0x8285, 0x8286, 0x8287, 0x8288, 0x8289, 0x828A, 0x828B,
    0x828C, 0x828D, 0x828E, 0x828F, 0x8290, 0x8291, 0x8292, 0x8293, 0x8294, 0x8295, 0x8296, 0x8297, 0x8298, 0x8299, 0x829A, 0x8140,
    0x8148, 0x8148, 0x8149, 0x8146, 0x817C, 0x8169, 0x816A, 0x8148, 0x8148, 0x8143, 0x8144, 0x815E, 0x8148, 0x8148, 0x8148, 0x8148,
    0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148, 0x8148,
};

extern uint8_t PLAYER_NAMES[256][8];
extern uint8_t PLAYER_NAME_ID;
uint16_t current_textbox_id;

#define MESSAGE_WIDE_END 0x8170
#define MESSAGE_WIDE_QUICKTEXT_ENABLE 0x8189

// Japanese QuickText does not stop scanning at TEXTID. Prime the unused tail of
// the decoded buffer with END so an instant message that ends in TEXTID has a
// deterministic boundary immediately after its destination ID. Valid decoded
// words overwrite the sentinel normally, so this does not alter visible text or
// require inserting QUICKTEXT_DISABLE.
static void Message_PrimeWideQuickTextBoundary(MessageContext* msgCtx, uint32_t decodedBufPos) {
    uint32_t i;
    uint32_t capacity;

    if (msgCtx == NULL) {
        return;
    }

    capacity = (uint32_t)(sizeof(msgCtx->msgBufDecodedWide) / sizeof(msgCtx->msgBufDecodedWide[0]));
    if ((capacity == 0) || (decodedBufPos >= capacity - 1)) {
        return;
    }

    for (i = decodedBufPos + 1; i < capacity; i++) {
        msgCtx->msgBufDecodedWide[i] = MESSAGE_WIDE_END;
    }
}
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

void Message_AddCharacterWide(MessageContext* msgCtx, Font* font, uint32_t* pDecodedBufPos, uint32_t* pCharTexIdx, uint16_t charToAdd) {
    uint32_t decodedBufPosVal = *pDecodedBufPos;
    uint32_t charTexIdx = *pCharTexIdx;
    msgCtx->msgBufDecodedWide[decodedBufPosVal++] = charToAdd; // Add the character to the output buffer, increment the output position
    if (charToAdd != 0x8140) { // Only load the character texture if it's not a space.
        Font_LoadCharWide(font, charToAdd, charTexIdx); // Load the character texture
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

void Message_AddIntegerWide(MessageContext* msgCtx, Font* font,
    uint32_t* pDecodedBufPos, uint32_t* pCharTexIdx,
    uint32_t numToAdd){
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
        Message_AddCharacterWide(msgCtx, font, pDecodedBufPos, pCharTexIdx, MESSAGE_WIDE_CHAR_ZERO + digits[c - 1]);
    }
}

// Helper function for adding simple strings to the decoded message buffer. Does not support additional control codes.
void Message_AddString(MessageContext* msgCtx, void* pFont, uint32_t* pDecodedBufPos, uint32_t* pCharTexIdx, char* stringToAdd) {
    while (*stringToAdd != 0) {
        Message_AddCharacter(msgCtx, pFont, pDecodedBufPos, pCharTexIdx, *stringToAdd);
        stringToAdd++;
    }
}

void Message_AddStringWide(MessageContext* msgCtx, Font* font, uint32_t* pDecodedBufPos, uint32_t* pCharTexIdx, char* stringToAdd) {
    while (*stringToAdd != 0) {
        char     src = *stringToAdd++;
        uint16_t ch  = 0x8140;
        if (src >= '0' && src <= '9') {
            ch = (uint16_t)((0x82 << 8) | (0x4F + (ch - '0')));
        }
        else if (src >= 'A' && src <= 'Z') {
            ch = (uint16_t)((0x82 << 8) | (0x60 + (ch - 'A')));
        }
        else if (src >= 'a' && src <= 'z') {
            ch = (uint16_t)((0x82 << 8) | (0x81 + (ch - 'a')));
        }
        Message_AddCharacterWide(msgCtx, font, pDecodedBufPos, pCharTexIdx, ch);
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

void Message_AddFileNameWide(MessageContext* msgCtx, Font* font, uint32_t* pDecodedBufPos, uint32_t* pCharTexIdx, uint8_t* filenameToAdd) {
    int end = 8;
    while (filenameToAdd[end - 1] == 0xDF) {
        // trim trailing space
        end--;
    }
    for (int i = 0; i < end; i++) {
        Message_AddCharacterWide(msgCtx, font, pDecodedBufPos, pCharTexIdx, FILENAME_ENCODING_WIDE[filenameToAdd[i]]);
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
                case 0x427: {
                    // Ganon's Tower
                    Message_AddString(msgCtx, pFont, pDecodedBufPos, pCharTexIdx, dungeons[12].name);
                    break;
                }
                case 0x467:
                case 0x534:
                case 0x538:
                case 0x53C:
                case 0x540:
                case 0x544:
                case 0x548:
                case 0x54C: {
                    // Ganon's Castle
                    Message_AddString(msgCtx, pFont, pDecodedBufPos, pCharTexIdx, dungeons[13].name);
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

// The ASM trampoline stores s5/s4 as full 32-bit values before passing their
// stack addresses here. Keep the pointer types aligned with that ABI.
bool Message_Decode_Additional_Control_Codes_JP(
    uint16_t      currCharWide,
    int16_t*      pDecodedBufPos,
    int32_t*      pCharTexIdx
) {
    MessageContext* msgCtx = &z64_game.msgContext;
    Font*           font   = &msgCtx->font;

    if (currCharWide == MESSAGE_WIDE_QUICKTEXT_ENABLE) {
        Message_PrimeWideQuickTextBoundary(msgCtx, *((uint32_t*)pDecodedBufPos));
    }

    if (currCharWide == 0x87F0) {
        // Silver rupee puzzle control code
        msgCtx->msgBufPos++;
        uint8_t puzzle = MSG_BUF_WIDE[msgCtx->msgBufPos] & 0xFF;
        uint8_t count  = extended_savectx.silver_rupee_counts[puzzle];

        Message_AddIntegerWide(msgCtx, font, (uint32_t*)pDecodedBufPos, (uint32_t*)pCharTexIdx, count);
        (*pDecodedBufPos)--;
        return true;

    }

    if (currCharWide == 0x87F1) {
        // Small key count
        msgCtx->msgBufPos++;
        uint8_t dungeon = MSG_BUF_WIDE[msgCtx->msgBufPos] & 0xFF;
        uint8_t count   = (z64_file.scene_flags[dungeon].unk_00_ >> 16) & 0xFF;

        Message_AddIntegerWide(msgCtx, font, (uint32_t*)pDecodedBufPos, (uint32_t*)pCharTexIdx, count);
        (*pDecodedBufPos)--;
        return true;

    }

    if (currCharWide == 0x87F2) {
        // Outgoing item filename
        Message_AddFileNameWide(
            msgCtx, font, (uint32_t*)pDecodedBufPos, (uint32_t*)pCharTexIdx,
            PLAYER_NAMES[PLAYER_NAME_ID]
        );
        (*pDecodedBufPos)--;
        return true;

    }

    if (currCharWide == 0x87F3) {
        // Farore's Wind destination
        uint16_t entrance = z64_file.respawn[RESPAWN_MODE_TOP].entranceIndex;
        char* name;

        if      (entrance ==   0x000 || entrance == 0x252) name = dungeons[0].name;
        else if (entrance ==   0x004 || entrance == 0x0C5) name = dungeons[1].name;
        else if (entrance ==   0x028 || entrance == 0x407) name = dungeons[2].name;
        else if (entrance ==   0x169 || entrance == 0x24E) name = dungeons[3].name;
        else if (entrance ==   0x165 || entrance == 0x175) name = dungeons[4].name;
        else if (entrance ==   0x010 || entrance == 0x423) name = dungeons[5].name;
        else if (entrance ==   0x037 || entrance == 0x2B2) name = dungeons[6].name;
        else if (entrance ==   0x082 || entrance == 0x2F5 ||
                 entrance ==   0x3F0 || entrance == 0x3F4) name = dungeons[7].name;
        else if (entrance ==   0x098)                      name = dungeons[8].name;
        else if (entrance ==   0x088)                      name = dungeons[9].name;
        else if (entrance ==   0x008)                      name = dungeons[11].name;
        else if ((entrance >= 0x41B && entrance <= 0x41B) ||
                 (entrance ==   0x467) ||
                 (entrance ==   0x534) ||
                 (entrance ==   0x538) ||
                 (entrance ==   0x53C) ||
                 (entrance ==   0x540) ||
                 (entrance ==   0x544) ||
                 (entrance ==   0x548) ||
                 (entrance ==   0x54C)            )    name = dungeons[12].name;
        else                                               name = "WARP";

        Message_AddStringWide(msgCtx, font, (uint32_t*)pDecodedBufPos, (uint32_t*)pCharTexIdx, name);
        (*pDecodedBufPos)--;
        return true;
    }

    return false;
}

void grab_textbox_id(z64_game_t* play, uint16_t textId)
{
    // Displaced code
    Message_OpenText(play, textId);

    current_textbox_id = textId;
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
}
