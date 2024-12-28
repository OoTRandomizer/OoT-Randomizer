#include "enemy_spawn_shuffle.h"
#include "z64.h"
#include "save.h"
#include "util.h"

uint8_t CFG_ENEMY_SPAWN_SHUFFLE = 0;
bool curr_room_enemies_inhibited = false; //When loading a room, set to keep track if any enemies were prevented from spawning due to enemy spawn shuffle. Used when checking for room clear to prevent clear if enemies are inhibited.

soul_menu_info SOUL_MENU_NAMES[] = {
    {SOUL_ID_ANUBIS, "Anubis"},
    {SOUL_ID_ARMOS, "Armos"},
    {SOUL_ID_BABY_DODONGO, "Baby Dodongo"},
    {SOUL_ID_BEAMOS, "Beamos"},
    {SOUL_ID_BIRI_AND_BARI, "Biri and Bari"},
    {SOUL_ID_BUBBLE, "Bubble"},
    {SOUL_ID_DARK_LINK, "Dark Link"},
    {SOUL_ID_DEAD_HAND, "Dead hand"},
    {SOUL_ID_DEKU_BABA, "Deku Baba"},
    {SOUL_ID_DEKU_SCRUB, "Deku Scrub"},
    {SOUL_ID_DODONGO, "Dodongo"},
    {SOUL_ID_FLARE_DANCER, "Flare Dancer"},
    {SOUL_ID_FLOORMASTER, "Floormaster"},
    {SOUL_ID_FLYING_POT, "Flying Pot"},
    {SOUL_ID_FREEZARD, "Freezard"},
    {SOUL_ID_GOHMA_LARVAE, "Gohma Larvae"},
    {SOUL_ID_GUAY, "Guay"},
    {SOUL_ID_IRON_KNUCKLE, "Iron Knuckle"},
    {SOUL_ID_JABU_JABU_TENTACLE, "Jabu Jabu Tentacle"},
    {SOUL_ID_KEESE, "Keese"},
    {SOUL_ID_LIKE_LIKE, "Like-like"},
    {SOUL_ID_LIZALFOS_AND_DINALFOS, "Lizalfos and Dinalfos"},
    {SOUL_ID_MOBLIN, "Moblin"},
    {SOUL_ID_OCTOROK, "Octorok"},
    {SOUL_ID_PEAHAT, "Peahat"},
    {SOUL_ID_REDEAD_AND_GIBDO, "Redead and Gibdo"},
    {SOUL_ID_SHABOM, "Shabom"},
    {SOUL_ID_SHELL_BLADE, "Shell blade"},
    {SOUL_ID_SKULL_KID, "Skull Kid"},
    {SOUL_ID_SKULLTULA, "Skulltula"},
    {SOUL_ID_SKULLWALLTULA, "Skullwalltula"},
    {SOUL_ID_SPIKE_ENEMY, "Spike Enemy"},
    {SOUL_ID_STALFOS, "Stalfos"},
    {SOUL_ID_STINGER, "Stinger"},
    {SOUL_ID_TAILPASARAN, "Tailpasaran"},
    {SOUL_ID_TEKTITE, "Tektite"},
    {SOUL_ID_TORCH_SLUG, "Torch Slug"},
    {SOUL_ID_WALLMASTER, "Wallmaster"},
    {SOUL_ID_WOLFOS, "Wolfos"},
    {SOUL_ID_QUEEN_GOHMA, "Queen Gohma"},
    {SOUL_ID_KING_DODONGO, "King Dodongo"},
    {SOUL_ID_BARINADE, "Barinade"},
    {SOUL_ID_PHANTOM_GANON, "Phantom Ganon"},
    {SOUL_ID_VOLVAGIA, "Volvagia"},
    {SOUL_ID_MORPHA, "Morpha"},
    {SOUL_ID_BONGO_BONGO, "Bongo Bongo"},
    {SOUL_ID_TWINROVA, "Twinrova"},
};

regional_soul_menu_info REGIONAL_SOUL_MENU_NAMES[] = {
    {SOUL_ID_REGIONAL_DEKU_TREE, "Deku Tree"},
    {SOUL_ID_REGIONAL_DODONGOS_CAVERN, "Dodongos Cavern"},
    {SOUL_ID_REGIONAL_JABU, "Jabu Jabu's Belly"},
    {SOUL_ID_REGIONAL_FOREST_TEMPLE, "Forest Temple"},
    {SOUL_ID_REGIONAL_FIRE_TEMPLE, "Fire Temple"},
    {SOUL_ID_REGIONAL_WATER_TEMPLE, "Water Temple"},
    {SOUL_ID_REGIONAL_SPIRIT_TEMPLE, "Spirit Temple"},
    {SOUL_ID_REGIONAL_SHADOW_TEMPLE, "Shadow Temple"},
    {SOUL_ID_REGIONAL_BOTW, "Bottom of the Well"},
    {SOUL_ID_REGIONAL_ICE_CAVERN, "Ice Cavern"},
    {SOUL_ID_REGIONAL_GTG, "Gerudo Training Ground"},
    {SOUL_ID_REGIONAL_GANONS_CASTLE, "Ganons Castle"},
    {SOUL_ID_REGIONAL_FOREST_AREA, "Forest Region"},
    {SOUL_ID_REGIONAL_HYRULE_FIELD, "Hyrule Field"},
    {SOUL_ID_REGIONAL_LAKE_HYLIA, "Lake Hylia"},
    {SOUL_ID_REGIONAL_GERUDO_AREA, "Gerudo Region"},
    {SOUL_ID_REGIONAL_MARKET_AREA, "Market Region"},
    {SOUL_ID_REGIONAL_KAKARIKO_AREA, "Kakariko Region"},
    {SOUL_ID_REGIONAL_GORON_AREA, "Goron Region"},
    {SOUL_ID_REGIONAL_ZORA_AREA, "Zora Region"},
    {SOUL_ID_REGIONAL_LLR, "Lon Lon Ranch"},
    {SOUL_ID_REGIONAL_GROTTOS, "Grottos"},
};


uint8_t SCENE_GROUP_DEKU_TREE[]           = {0, 17};
uint8_t SCENE_GROUP_DODONGOS_CAVERN[]     = {1,18};
uint8_t SCENE_GROUP_JABU[]                = {2,19};
uint8_t SCENE_GROUP_FOREST_TEMPLE[]       = {3,20};
uint8_t SCENE_GROUP_FIRE_TEMPLE[]         = {4,21};
uint8_t SCENE_GROUP_WATER_TEMPLE[]        = {5,22};
uint8_t SCENE_GROUP_SPIRIT_TEMPLE[]       = {6,23};
uint8_t SCENE_GROUP_SHADOW_TEMPLE[]       = {7,24};
uint8_t SCENE_GROUP_BOTW[]                = {8};
uint8_t SCENE_GROUP_ICE_CAVERN[]          = {9};
uint8_t SCENE_GROUP_GTG[]                 = {11};
uint8_t SCENE_GROUP_GANONS_CASTLE[]       = {10,13,14,15,25,26,79};
uint8_t SCENE_GROUP_FOREST_AREA[]         = {38,39,40,41,45,52,85,86,91};
uint8_t SCENE_GROUP_HYRULE_FIELD[]        = {81};
uint8_t SCENE_GROUP_LAKE_HYLIA[]          = {56,87,73};
uint8_t SCENE_GROUP_GERUDO_AREA[]         = {57,90,92,93,94};
uint8_t SCENE_GROUP_MARKET_AREA[]         = {16,27,28,29,30,31,32,33,34,35,36,37,43,49,50,51,53,77,75,67,68,69,70,74,95,100};
uint8_t SCENE_GROUP_KAKARIKO_AREA[]       = {42,48,58,63,65,72,78,80,82,83};
uint8_t SCENE_GROUP_GORON_AREA[]          = {46,98,96,97};
uint8_t SCENE_GROUP_ZORA_AREA[]           = {47,84,88,89};
uint8_t SCENE_GROUP_LLR[]                 = {54,55,76,99};
uint8_t SCENE_GROUP_GROTTOS[]             = {62,64};

regional_enemy_spawn_table_entry regional_enemy_spawn_table[] = {
    REGIONAL_ENEMY_SPAWN_TABLE_ENTRY(SCENE_GROUP_DEKU_TREE),
    REGIONAL_ENEMY_SPAWN_TABLE_ENTRY(SCENE_GROUP_DODONGOS_CAVERN),
    REGIONAL_ENEMY_SPAWN_TABLE_ENTRY(SCENE_GROUP_JABU),
    REGIONAL_ENEMY_SPAWN_TABLE_ENTRY(SCENE_GROUP_FOREST_TEMPLE),
    REGIONAL_ENEMY_SPAWN_TABLE_ENTRY(SCENE_GROUP_FIRE_TEMPLE),
    REGIONAL_ENEMY_SPAWN_TABLE_ENTRY(SCENE_GROUP_WATER_TEMPLE),
    REGIONAL_ENEMY_SPAWN_TABLE_ENTRY(SCENE_GROUP_SHADOW_TEMPLE),
    REGIONAL_ENEMY_SPAWN_TABLE_ENTRY(SCENE_GROUP_SPIRIT_TEMPLE),
    REGIONAL_ENEMY_SPAWN_TABLE_ENTRY(SCENE_GROUP_BOTW),
    REGIONAL_ENEMY_SPAWN_TABLE_ENTRY(SCENE_GROUP_ICE_CAVERN),
    REGIONAL_ENEMY_SPAWN_TABLE_ENTRY(SCENE_GROUP_GTG),
    REGIONAL_ENEMY_SPAWN_TABLE_ENTRY(SCENE_GROUP_GANONS_CASTLE),
    REGIONAL_ENEMY_SPAWN_TABLE_ENTRY(SCENE_GROUP_FOREST_AREA),
    REGIONAL_ENEMY_SPAWN_TABLE_ENTRY(SCENE_GROUP_HYRULE_FIELD),
    REGIONAL_ENEMY_SPAWN_TABLE_ENTRY(SCENE_GROUP_LAKE_HYLIA),
    REGIONAL_ENEMY_SPAWN_TABLE_ENTRY(SCENE_GROUP_GERUDO_AREA),
    REGIONAL_ENEMY_SPAWN_TABLE_ENTRY(SCENE_GROUP_MARKET_AREA),
    REGIONAL_ENEMY_SPAWN_TABLE_ENTRY(SCENE_GROUP_KAKARIKO_AREA),
    REGIONAL_ENEMY_SPAWN_TABLE_ENTRY(SCENE_GROUP_GORON_AREA),
    REGIONAL_ENEMY_SPAWN_TABLE_ENTRY(SCENE_GROUP_ZORA_AREA),
    REGIONAL_ENEMY_SPAWN_TABLE_ENTRY(SCENE_GROUP_LLR),
    REGIONAL_ENEMY_SPAWN_TABLE_ENTRY(SCENE_GROUP_GROTTOS),
};

enemy_spawn_table_entry enemy_spawn_table[] = {
    ENEMY_SPAWN_TABLE_ENTRY(0x0002, 0,   SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Test (Stalfos)
    ENEMY_SPAWN_TABLE_ENTRY(0x000E, 1,   SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Okuta (Octorok (and big octo))
    ENEMY_SPAWN_TABLE_ENTRY(0x00C8, 1,   SPAWN_FLAGS_SPAWNENTRY, spawn_check_big_octo), //Jabu objects Big Octo Platform
    ENEMY_SPAWN_TABLE_ENTRY(0x0011, 2,   SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Wallmas (Wallmaster)
    ENEMY_SPAWN_TABLE_ENTRY(0x0012, 3,   SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Dodongo (Dodongo)
    ENEMY_SPAWN_TABLE_ENTRY(0x0013, 4,   SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Firefly (Keese (fire, ice, regular))
    ENEMY_SPAWN_TABLE_ENTRY(0x001B, 5,   SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Tite (Tektite)
    ENEMY_SPAWN_TABLE_ENTRY(0x001D, 6,   SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Peehat (Peahat)
    ENEMY_SPAWN_TABLE_ENTRY(0x0025, 7,   SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Zf (Lizalfos/Dinalfos)
    ENEMY_SPAWN_TABLE_ENTRY(0x002B, 8,   SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Goma (Gohma Larva)
    ENEMY_SPAWN_TABLE_ENTRY(0x002D, 9,   SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Bubble (Shabom)
    ENEMY_SPAWN_TABLE_ENTRY(0x002F, 10,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Dodojr (Baby Dodongo)
    ENEMY_SPAWN_TABLE_ENTRY(0x0034, 11,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Bili (Biri/Bari)
    ENEMY_SPAWN_TABLE_ENTRY(0x0063, 11,  SPAWN_FLAGS_SPAWNENTRY, NULL), //Bari
    ENEMY_SPAWN_TABLE_ENTRY(0x0035, 12,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Tp (Tailpasarn)
    ENEMY_SPAWN_TABLE_ENTRY(0x0037, 13,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_St (Skulltula)
    ENEMY_SPAWN_TABLE_ENTRY(0x0038, 14,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Bw (Torch Slug)
    ENEMY_SPAWN_TABLE_ENTRY(0x004B, 15,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Mb (Moblin)
    ENEMY_SPAWN_TABLE_ENTRY(0x0054, 16,  SPAWN_FLAGS_SPAWNENTRY, spawn_check_armos), //En_Am (Armos)
    ENEMY_SPAWN_TABLE_ENTRY(0x0055, 17,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Dekubaba (Deku Baba)
    ENEMY_SPAWN_TABLE_ENTRY(0x00C7, 17,  SPAWN_FLAGS_SPAWNENTRY, NULL), //Withered Deku Baba
    ENEMY_SPAWN_TABLE_ENTRY(0x0060, 18,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Dekunuts, En_Hintnuts (Deku Scrub)
    ENEMY_SPAWN_TABLE_ENTRY(0x0192, 18,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Hintnuts (Hint Scrub from Deku Tree)
    ENEMY_SPAWN_TABLE_ENTRY(0x0069, 19,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Bb (Bubble (fire, blue, white))
    ENEMY_SPAWN_TABLE_ENTRY(0x008A, 20,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Vm (Beamos)
    ENEMY_SPAWN_TABLE_ENTRY(0x008E, 21,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Floormas (Floormaster (maybe combine))
    ENEMY_SPAWN_TABLE_ENTRY(0x0090, 22,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Rd (Redead/Gibdo)
    ENEMY_SPAWN_TABLE_ENTRY(0x0095, 23,  SPAWN_FLAGS_SPAWNENTRY, spawn_check_gs), //En_Sw (Skullwalltula (but not gold skulltula))
    ENEMY_SPAWN_TABLE_ENTRY(0x0099, 24,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Fd (Flare Dancer)
    ENEMY_SPAWN_TABLE_ENTRY(0x00A4, 25,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Dh (Dead hand)
    ENEMY_SPAWN_TABLE_ENTRY(0x00C5, 26,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Sb (Shell blade)
    ENEMY_SPAWN_TABLE_ENTRY(0x00DD, 27,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Rr (Like-like)
    ENEMY_SPAWN_TABLE_ENTRY(0x00EC, 28,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Ny (spike)
    ENEMY_SPAWN_TABLE_ENTRY(0x00F6, 29,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Anubice_Tag, En_Anubice (Anubis (spawner))
    ENEMY_SPAWN_TABLE_ENTRY(0x0113, 30,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Ik (Iron Knuckle)
    ENEMY_SPAWN_TABLE_ENTRY(0x0115, 31,  SPAWN_FLAGS_SPAWNENTRY, spawn_check_skullkid), //En_Skj (Skull Kid)
    ENEMY_SPAWN_TABLE_ENTRY(0x011D, 32,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Tubo_Trap (Flying Pot)
    ENEMY_SPAWN_TABLE_ENTRY(0x0121, 33,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Fz (Freezard (Frezzard))
    ENEMY_SPAWN_TABLE_ENTRY(0x018C, 34,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Weiyer, En_Eiyer (Stinger and Water Stinger)
    ENEMY_SPAWN_TABLE_ENTRY(0x003A, 34,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Eiyer (Stinger)
    ENEMY_SPAWN_TABLE_ENTRY(0x01AF, 35,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Wf (Wolfos)
    ENEMY_SPAWN_TABLE_ENTRY(0x01C0, 36,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Crow (Guay)
    ENEMY_SPAWN_TABLE_ENTRY(0x0028, 37,  SPAWN_FLAGS_SPAWNENTRY, NULL), //Boss_Goma (Queen Gohma)
    ENEMY_SPAWN_TABLE_ENTRY(0x0027, 38,  SPAWN_FLAGS_SPAWNENTRY, NULL), //Boss_Dodongo (King Dodongo)
    ENEMY_SPAWN_TABLE_ENTRY(0x00BA, 39,  SPAWN_FLAGS_SPAWNENTRY, NULL), //Boss_Va (Barinade)
    ENEMY_SPAWN_TABLE_ENTRY(0x0052, 40,  SPAWN_FLAGS_SPAWNENTRY, NULL), //Boss_Ganondrof (Phantom Ganon)
    ENEMY_SPAWN_TABLE_ENTRY(0x0096, 41,  SPAWN_FLAGS_SPAWNENTRY, NULL), //Boss_Fd (Volvagia)
    ENEMY_SPAWN_TABLE_ENTRY(0x00C4, 42,  SPAWN_FLAGS_SPAWNENTRY, NULL), //Boss_Mo (Morpha)
    ENEMY_SPAWN_TABLE_ENTRY(0x00E9, 43,  SPAWN_FLAGS_SPAWNENTRY, NULL), //Boss_Sst (Bongo Bongo)
    ENEMY_SPAWN_TABLE_ENTRY(0x00DC, 44,  SPAWN_FLAGS_SPAWNENTRY, NULL), //Boss_Tw (Twinrova)
    ENEMY_SPAWN_TABLE_ENTRY(0x00DE, 45,  SPAWN_FLAGS_SPAWNENTRY, NULL), //En_Ba (Jabu Jabu Tentacles),
    ENEMY_SPAWN_TABLE_ENTRY(0x0033, 46,  SPAWN_FLAGS_ACTORSPAWN, NULL)  //En_Torch2 (Dark Link)
};


// Return false if this is a gold skulltula
bool spawn_check_gs(ActorEntry *actorEntry, z64_game_t *globalCtx) {
    uint16_t type = (actorEntry->params & 0xE000) >> 13;
    if (type == 4 || type == 5) // Check if it's a gold skulltula
        return false;
    return true;
}

bool spawn_check_armos(ActorEntry *actorEntry, z64_game_t *globalCtx) {
    if (actorEntry->params == 0) // Pushable armos statue, don't treat like an enemy
        return false;
    return true;
}

bool spawn_check_big_octo(ActorEntry *actorEntry, z64_game_t *globalCtx) {
    if ((actorEntry->params & 0x00FF) == 0)
        return true;
    return false;
}

bool spawn_check_skullkid(ActorEntry *actorEntry, z64_game_t *globalCtx) {
    uint16_t type = (actorEntry->params >> 0x0A) & 0x3F;
    if (type <= 6) // Ocarina game/sarias song skull kids
        return false;
    return true;
}

bool flags_getsoul(int table_index) {
    return (extended_savectx.enemy_spawn_flags[table_index/8] & (1 << (table_index % 8))) > 0;
}

bool flags_setsoul(int table_index) {
    extended_savectx.enemy_spawn_flags[table_index/8] |= 1 << (table_index % 8);
    extended_savectx.soul_enable_flags[table_index/8] |= 1 << (table_index % 8);
}

bool get_soul_enabled(int table_index) {
    return (extended_savectx.soul_enable_flags[table_index/8] & (1 << (table_index % 8))) > 0;
}

bool toggle_soul_enabled(int table_index) {
    uint8_t flags = extended_savectx.soul_enable_flags[table_index/8];
    uint8_t mask = (1 << (table_index % 8));
    extended_savectx.soul_enable_flags[table_index/8] = flags ^ mask;
}

// Spawn override function for enemy spawn shuffle.
// Check if the actor id is in the enemy_spawn_table, and if it is check if the enemy spawn flag is set in extended save context
bool spawn_override_enemy_spawn_shuffle(ActorEntry *actorEntry, z64_game_t *globalCtx, SPAWN_FLAGS flag)
{
    if ( CFG_ENEMY_SPAWN_SHUFFLE ) { // Only if the setting is enabled
        for (int i = 0; i < array_size(enemy_spawn_table); i++) { //Loop through the enemy_spawn_table
            if ((actorEntry->id == enemy_spawn_table[i].actor_id) && (enemy_spawn_table[i].flags & flag)) {
                if (enemy_spawn_table[i].override_func) {
                    if (!enemy_spawn_table[i].override_func(actorEntry, globalCtx))
                        return true;
                }
                // For standard enemy spawn shuffle, check if we collected the soul for that enemy
                if (CFG_ENEMY_SPAWN_SHUFFLE == CFG_ENEMY_SPAWN_SHUFFLE_STANDARD) {
                    enemy_spawn_table_entry *table_entry = &(enemy_spawn_table[i]);
                    bool continue_spawn = true;
                    
                    continue_spawn &= flags_getsoul(table_entry->index) & get_soul_enabled(table_entry->index);
                    curr_room_enemies_inhibited |= !continue_spawn;
                    return continue_spawn;
                }
                // For regional enemy spawn shuffle, check if we collected the soul for that region
                else if (CFG_ENEMY_SPAWN_SHUFFLE == CFG_ENEMY_SPAWN_SHUFFLE_REGIONAL) {
                    // Loop through the regional spawn table and check for the current scene
                    for(int j = 0; j < array_size(regional_enemy_spawn_table); j++) {
                        // Loop throught the scene group
                        for(int k = 0; k < regional_enemy_spawn_table[j].scene_group_length; k++) {
                            if(regional_enemy_spawn_table[j].scene_group[k] == globalCtx->scene_index) {
                                // found a scene group matching the current scene
                                // Check if we have that flag
                                bool continue_spawn = flags_getsoul(j) && get_soul_enabled(j);
                                curr_room_enemies_inhibited |= !continue_spawn;
                                return continue_spawn;
                            }
                        }
                    }
                    // If we got here, we didn't find a scene group for this enemy. This should probably never happen
                    // But just spawn the enemy if it does
                    return true;
                }
            }
        }
    }

    return true;
}

void Actor_RemoveFromCategory_SetTempClear_Hack(z64_game_t *globalCtx, int32_t flag)
{
    if(curr_room_enemies_inhibited) {
        return;
    }
    z64_Flags_SetTempClear(globalCtx, flag);
}
