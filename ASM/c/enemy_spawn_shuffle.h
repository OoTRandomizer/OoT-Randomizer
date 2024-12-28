#ifndef ENEMY_SPAWN_SHUFFLE_H
#define ENEMY_SPAWN_SHUFFLE_H

#include <stdbool.h>
#include "z64.h"

typedef enum {
    SOUL_ID_STALFOS,
    SOUL_ID_OCTOROK,
    SOUL_ID_WALLMASTER,
    SOUL_ID_DODONGO,
    SOUL_ID_KEESE,
    SOUL_ID_TEKTITE,
    SOUL_ID_PEAHAT,
    SOUL_ID_LIZALFOS_AND_DINALFOS,
    SOUL_ID_GOHMA_LARVAE,
    SOUL_ID_SHABOM,
    SOUL_ID_BABY_DODONGO,
    SOUL_ID_BIRI_AND_BARI,
    SOUL_ID_TAILPASARAN,
    SOUL_ID_SKULLTULA,
    SOUL_ID_TORCH_SLUG,
    SOUL_ID_MOBLIN,
    SOUL_ID_ARMOS,
    SOUL_ID_DEKU_BABA,
    SOUL_ID_DEKU_SCRUB,
    SOUL_ID_BUBBLE,
    SOUL_ID_BEAMOS,
    SOUL_ID_FLOORMASTER,
    SOUL_ID_REDEAD_AND_GIBDO,
    SOUL_ID_SKULLWALLTULA,
    SOUL_ID_FLARE_DANCER,
    SOUL_ID_DEAD_HAND,
    SOUL_ID_SHELL_BLADE,
    SOUL_ID_LIKE_LIKE,
    SOUL_ID_SPIKE_ENEMY,
    SOUL_ID_ANUBIS,
    SOUL_ID_IRON_KNUCKLE,
    SOUL_ID_SKULL_KID,
    SOUL_ID_FLYING_POT,
    SOUL_ID_FREEZARD,
    SOUL_ID_STINGER,
    SOUL_ID_WOLFOS,
    SOUL_ID_GUAY,
    SOUL_ID_QUEEN_GOHMA,
    SOUL_ID_KING_DODONGO,
    SOUL_ID_BARINADE,
    SOUL_ID_PHANTOM_GANON,
    SOUL_ID_VOLVAGIA,
    SOUL_ID_MORPHA,
    SOUL_ID_BONGO_BONGO,
    SOUL_ID_TWINROVA,
    SOUL_ID_JABU_JABU_TENTACLE,
    SOUL_ID_DARK_LINK,
    NUM_ENEMY_SOULS,
} SOUL_ID;

typedef enum {
    SOUL_ID_REGIONAL_DEKU_TREE,
    SOUL_ID_REGIONAL_DODONGOS_CAVERN,
    SOUL_ID_REGIONAL_JABU,
    SOUL_ID_REGIONAL_FOREST_TEMPLE,
    SOUL_ID_REGIONAL_FIRE_TEMPLE,
    SOUL_ID_REGIONAL_WATER_TEMPLE,
    SOUL_ID_REGIONAL_SHADOW_TEMPLE,
    SOUL_ID_REGIONAL_SPIRIT_TEMPLE,
    SOUL_ID_REGIONAL_BOTW,
    SOUL_ID_REGIONAL_ICE_CAVERN,
    SOUL_ID_REGIONAL_GTG,
    SOUL_ID_REGIONAL_GANONS_CASTLE,
    SOUL_ID_REGIONAL_FOREST_AREA,
    SOUL_ID_REGIONAL_HYRULE_FIELD,
    SOUL_ID_REGIONAL_LAKE_HYLIA,
    SOUL_ID_REGIONAL_GERUDO_AREA,
    SOUL_ID_REGIONAL_MARKET_AREA,
    SOUL_ID_REGIONAL_KAKARIKO_AREA,
    SOUL_ID_REGIONAL_GORON_AREA,
    SOUL_ID_REGIONAL_ZORA_AREA,
    SOUL_ID_REGIONAL_LLR,
    SOUL_ID_REGIONAL_GROTTOS,
    NUM_REGIONAL_ENEMY_SOULS
} SOUL_ID_REGIONAL;

// Enemy spawn shuffle spawn check override function.
// Return true if the actor entry should be handled by enemy spawn shuffle
typedef bool (*alt_spawn_override_fn)(ActorEntry *actorEntry, z64_game_t *globalCtx);

bool spawn_check_gs(ActorEntry *actorEntry, z64_game_t *globalCtx);
bool spawn_check_big_octo(ActorEntry *actorEntry, z64_game_t *globalCtx);
bool spawn_check_armos(ActorEntry *actorEntry, z64_game_t *globalCtx);
bool spawn_check_skullkid(ActorEntry *actorEntry, z64_game_t *globalCtx);
bool flags_getsoul(int table_index);
bool flags_setsoul(int table_index);
bool get_soul_enabled(int table_index);
bool toggle_soul_enabled(int table_index);

typedef enum SPAWN_FLAGS {
    SPAWN_FLAGS_SPAWNENTRY =  1,
    SPAWN_FLAGS_ACTORSPAWN = 2
} SPAWN_FLAGS;

typedef struct enemy_spawn_table_entry {
    uint16_t actor_id;
    uint8_t index;
    SPAWN_FLAGS flags;
    alt_spawn_override_fn override_func;
} enemy_spawn_table_entry;

typedef struct regional_enemy_spawn_table_entry{
    uint8_t* scene_group;
    uint8_t scene_group_length; 
} regional_enemy_spawn_table_entry;

typedef struct soul_menu_info {
    SOUL_ID soul_id;
    char* name;
} soul_menu_info;

typedef struct regional_soul_menu_info {
    SOUL_ID_REGIONAL soul_id;
    char* name;
} regional_soul_menu_info;

#define CFG_ENEMY_SPAWN_SHUFFLE_NONE 0
#define CFG_ENEMY_SPAWN_SHUFFLE_STANDARD 1
#define CFG_ENEMY_SPAWN_SHUFFLE_REGIONAL 2

extern uint8_t CFG_ENEMY_SPAWN_SHUFFLE;
extern soul_menu_info SOUL_MENU_NAMES[];
extern regional_soul_menu_info REGIONAL_SOUL_MENU_NAMES[];

#define ENEMY_SPAWN_TABLE_ENTRY(actor_id_,index_,flags_,override_func_) {.actor_id = actor_id_, .index = index_, .flags = flags_, .override_func = override_func_}
#define REGIONAL_ENEMY_SPAWN_TABLE_ENTRY(scene_group_) {.scene_group = scene_group_, .scene_group_length = array_size(scene_group_)}

bool spawn_override_enemy_spawn_shuffle(ActorEntry *actorEntry, z64_game_t *globalCtx, SPAWN_FLAGS flag);

#endif
