#ifndef ENTRANCE_TABLE_H
#define ENTRANCE_TABLE_H

#include "z64.h"
#include "scene_table.h"

#define ENTRANCE_INFO_CONTINUE_BGM_FLAG (1 << 15)
#define ENTRANCE_INFO_DISPLAY_TITLE_CARD_FLAG (1 << 14)
#define ENTRANCE_INFO_END_TRANS_TYPE_MASK 0x3F80
#define ENTRANCE_INFO_END_TRANS_TYPE_SHIFT 7
#define ENTRANCE_INFO_END_TRANS_TYPE(field)          \
    (((field) >> ENTRANCE_INFO_END_TRANS_TYPE_SHIFT) \
     & (ENTRANCE_INFO_END_TRANS_TYPE_MASK >> ENTRANCE_INFO_END_TRANS_TYPE_SHIFT))
#define ENTRANCE_INFO_START_TRANS_TYPE_MASK 0x7F
#define ENTRANCE_INFO_START_TRANS_TYPE_SHIFT 0
#define ENTRANCE_INFO_START_TRANS_TYPE(field)          \
    (((field) >> ENTRANCE_INFO_START_TRANS_TYPE_SHIFT) \
     & (ENTRANCE_INFO_START_TRANS_TYPE_MASK >> ENTRANCE_INFO_START_TRANS_TYPE_SHIFT))

// DEFINE_ENTRANCE should be used for new entrances
//    - Argument 1: Scene this entrance belongs to
//    - Argument 2: Spawn number for this entrance
//    - Argument 3: Toggle if bgm should continue during the transition using this entrance (true or false)
//                  NOTE: For non-cutscene layers, this field is only read from the `SCENE_LAYER_CHILD_DAY` layer.
//                  Meaning, the setting only matters for the first entry within a group of layers and that
//                  setting will apply to the other 3 non-cutscene layers.
//    - Argument 4: Toggle if a title card should display when using this entrance (true or false)
//    - Argument 5: Transition type when entering using this entrance (second half of a scene transition)
//    - Argument 6: Transition type when exiting using this entrance (first half of a scene transition)
//
// WARNING: Due to how the entrance system is implemented, entries within the same group of scene layers are NOT shiftable.
//          Groups of scene layers are indicated by line breaks.
//
//          Only the first entrance within a group of layers is expected to be referenced in code.
//          The entrance system will apply the offset on its own to access the correct entrance for a given layer.
#define DEFINE_ENTRANCE(sceneId, spawn, continueBgm, displayTitleCard, endTransType, startTransType) \
    { sceneId, spawn,                                                                                    \
      (((continueBgm) ? ENTRANCE_INFO_CONTINUE_BGM_FLAG : 0) |                                           \
       ((displayTitleCard) ? ENTRANCE_INFO_DISPLAY_TITLE_CARD_FLAG : 0) |                                \
       (((endTransType) << ENTRANCE_INFO_END_TRANS_TYPE_SHIFT) & ENTRANCE_INFO_END_TRANS_TYPE_MASK) |    \
       (((startTransType) << ENTRANCE_INFO_START_TRANS_TYPE_SHIFT) & ENTRANCE_INFO_START_TRANS_TYPE_MASK)) },

#define SCENE_LAYERS_PER_ENTRANCE 4 // default for new entries, not always true for vanilla!
#define VANILLA_ENTRIES 0x614
#define BYTES_PER_ENTRANCE_ENTRY sizeof(EntranceInfo)

// 33 grottos, both entrances and exits, minus unique grotto entrances such as Deku Theater
#define EXTENDED_ENTRIES 33 * 2 - 11
#define EXTENDED_TABLE_SIZE VANILLA_ENTRIES * BYTES_PER_ENTRANCE_ENTRY + EXTENDED_ENTRIES * BYTES_PER_ENTRANCE_ENTRY * SCENE_LAYERS_PER_ENTRANCE

typedef struct EntranceInfo {
    /* 0x00 */ int8_t   sceneId;
    /* 0x01 */ int8_t   spawn;
    /* 0x02 */ uint16_t field;
} EntranceInfo; // size = 0x4

typedef enum TransitionType {
    /*  0 */ TRANS_TYPE_WIPE,
    /*  1 */ TRANS_TYPE_TRIFORCE,
    /*  2 */ TRANS_TYPE_FADE_BLACK,
    /*  3 */ TRANS_TYPE_FADE_WHITE,
    /*  4 */ TRANS_TYPE_FADE_BLACK_FAST,
    /*  5 */ TRANS_TYPE_FADE_WHITE_FAST,
    /*  6 */ TRANS_TYPE_FADE_BLACK_SLOW,
    /*  7 */ TRANS_TYPE_FADE_WHITE_SLOW,
    /*  8 */ TRANS_TYPE_WIPE_FAST,
    /*  9 */ TRANS_TYPE_FILL_WHITE2,
    /* 10 */ TRANS_TYPE_FILL_WHITE,
    /* 11 */ TRANS_TYPE_INSTANT,
    /* 12 */ TRANS_TYPE_FILL_BROWN,
    /* 13 */ TRANS_TYPE_FADE_WHITE_CS_DELAYED,
    /* 14 */ TRANS_TYPE_SANDSTORM_PERSIST,
    /* 15 */ TRANS_TYPE_SANDSTORM_END,
    /* 16 */ TRANS_TYPE_CS_BLACK_FILL,
    /* 17 */ TRANS_TYPE_FADE_WHITE_INSTANT,
    /* 18 */ TRANS_TYPE_FADE_GREEN,
    /* 19 */ TRANS_TYPE_FADE_BLUE,
    // transition types 20 - 31 are unused
    // transition types 32 - 55 are constructed using the TRANS_TYPE_CIRCLE macro
    /* 56 */ TRANS_TYPE_MAX = 56
} TransitionType;

extern EntranceInfo gExtendedEntranceTable[];

#endif