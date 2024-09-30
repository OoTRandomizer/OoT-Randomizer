#include "item_draw_functions.h"

#include "z64.h"
#include "item_draw_table.h"
#include "sys_matrix.h"

typedef Gfx* (*append_setup_dl_fn)(Gfx* gfx, uint32_t dl_index);
typedef void (*append_setup_dl_26_to_opa_fn)(z64_gfx_t* gfx);
typedef void (*append_setup_dl_25_to_opa_fn)(z64_gfx_t* gfx);
typedef void (*append_setup_dl_25_to_xlu_fn)(z64_gfx_t* gfx);
typedef Gfx* (*gen_double_tile_fn)(z64_gfx_t* gfx, int32_t tile1, uint32_t x1, uint32_t y1, int32_t width1, int32_t height1,
                                int32_t tile2, uint32_t x2, uint32_t y2, int32_t width2, int32_t height2);

#define append_setup_dl ((append_setup_dl_fn)0x8007DFBC)
#define append_setup_dl_26_to_opa ((append_setup_dl_26_to_opa_fn)0x8007E1DC)
#define append_setup_dl_25_to_opa ((append_setup_dl_25_to_opa_fn)0x8007E298)
#define append_setup_dl_25_to_xlu ((append_setup_dl_25_to_xlu_fn)0x8007E2C0)
#define gen_double_tile ((gen_double_tile_fn)0x8007EB84)

void draw_gi_bombchu_and_masks(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_26_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);
}

void draw_gi_eggs_and_medallions(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_26_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[1].dlist);
}

void draw_gi_sold_out(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    gfx->poly_xlu.p = append_setup_dl(gfx->poly_xlu.p, 5);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[0].dlist);
}

void draw_gi_compass(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);

    gfx->poly_xlu.p = append_setup_dl(gfx->poly_xlu.p, 5);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[1].dlist);
}

void draw_gi_various_opa0(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);
}

void draw_gi_various_opa1023(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[1].dlist);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[2].dlist);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[3].dlist);
}

void draw_gi_wallets(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[1].dlist);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[2].dlist);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[3].dlist);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[4].dlist);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[5].dlist);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[6].dlist);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[7].dlist);
}

void draw_gi_silver_rupee_pouch(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);

    // Set the wallet color silver by reimplementing the gGiAdultWalletColorDL calls:
    // E7 00 00 00 00 00 00 00 gSPRDPPipeSync
    // FA 00 00 00 A0 82 64 FF gSPSetPrimColor
    // FB 00 00 00 46 3C 32 FF gSPSetEnvColor
    // DF 00 00 00 00 00 00 00

    //gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[1].dlist);  // gGiAdultWalletColorDL
    gDPPipeSync(gfx->poly_opa.p++);
    gDPSetPrimColor(gfx->poly_opa.p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);
    gDPSetEnvColor(gfx->poly_opa.p++, 0x32, 0x3C, 0x3C, 0xFF);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);  // gGiWalletDL
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[2].dlist);  // gGiAdultWalletRupeeOuterColorDL
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[3].dlist);  // gGiWalletRupeeOuterDL
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[4].dlist);  // gGiAdultWalletStringColorDL
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[5].dlist);  // gGiWalletStringDL
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[6].dlist);  // gGiAdultWalletRupeeInnerColorDL
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[7].dlist);  // gGiWalletRupeeInnerDL
}

void draw_gi_various_xlu01(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_xlu(gfx);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[0].dlist);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[1].dlist);
}

void draw_gi_various_opa0_xlu1(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);

    append_setup_dl_25_to_xlu(gfx);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[1].dlist);
}

void draw_rutos_letter(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    // Turn the model sideways
    rotate_Z_sys_matrix(1.57f, 1);

    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);

    append_setup_dl_25_to_xlu(gfx);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[1].dlist);
}

void draw_gi_coins_and_cuccos(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[1].dlist);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);

    append_setup_dl_25_to_xlu(gfx);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[2].dlist);
}

void draw_gi_magic_arrows(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);

    append_setup_dl_25_to_xlu(gfx);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[1].dlist);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[2].dlist);
}

void draw_gi_various_opa10_xlu32(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[1].dlist);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);

    append_setup_dl_25_to_xlu(gfx);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[3].dlist);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[2].dlist);
}

void draw_gi_bullet_bags(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[1].dlist);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);

    append_setup_dl_25_to_xlu(gfx);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[2].dlist);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[3].dlist);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[4].dlist);
}

void draw_gi_small_rupees(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    scale_sys_matrix(0.7f, 0.7f, 0.7f, 1);

    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[1].dlist);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);

    append_setup_dl_25_to_xlu(gfx);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[3].dlist);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[2].dlist);
}

void draw_gi_goron_swords(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_opa(gfx);
    gSPSegment(gfx->poly_opa.p++, 0x08,
               gen_double_tile(gfx,
                               0, game->common.state_frames, 0, 32, 32,
                               1, 0, 0, 32, 32));
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);
}

void draw_gi_deku_nut(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_opa(gfx);
    gSPSegment(gfx->poly_opa.p++, 0x08,
               gen_double_tile(gfx,
                               0, game->common.state_frames * 6, game->common.state_frames * 6, 32, 32,
                               1, game->common.state_frames * 6, game->common.state_frames * 6, 32, 32));
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);
}

void draw_gi_recovery_heart(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_xlu(gfx);
    gSPSegment(gfx->poly_xlu.p++, 0x08,
               gen_double_tile(gfx,
                               0, 0, -(game->common.state_frames * 3), 32, 32,
                               1, 0, -(game->common.state_frames * 2), 32, 32));
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[0].dlist);
}

void draw_gi_fish_bottle(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_xlu(gfx);
    gSPSegment(gfx->poly_xlu.p++, 0x08,
               gen_double_tile(gfx,
                               0, 0, game->common.state_frames, 32, 32,
                               1, 0, game->common.state_frames, 32, 32));
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[0].dlist);
}

void draw_gi_magic_spells(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_xlu(gfx);
    gSPSegment(gfx->poly_xlu.p++, 0x08,
               gen_double_tile(gfx,
                               0, game->common.state_frames * 2, -(game->common.state_frames * 6), 32, 32,
                               1, game->common.state_frames, -(game->common.state_frames * 2), 32, 32));
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[0].dlist);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[1].dlist);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[2].dlist);
}

void draw_gi_scales(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_xlu(gfx);
    gSPSegment(gfx->poly_xlu.p++, 0x08,
               gen_double_tile(gfx,
                               0, game->common.state_frames * 2, -(game->common.state_frames * 2), 64, 64,
                               1, game->common.state_frames * 4, -(game->common.state_frames * 4), 32, 32));
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[2].dlist);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[3].dlist);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[1].dlist);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[0].dlist);
}

void draw_gi_potions(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_opa(gfx);
    gSPSegment(gfx->poly_opa.p++, 0x08,
               gen_double_tile(gfx,
                               0, -game->common.state_frames, game->common.state_frames, 32, 32,
                               1, -game->common.state_frames, game->common.state_frames, 32, 32));
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[1].dlist);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[2].dlist);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[3].dlist);

    append_setup_dl_25_to_xlu(gfx);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[4].dlist);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[5].dlist);
}

void draw_gi_mirror_shield(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_opa(gfx);
    gSPSegment(gfx->poly_opa.p++, 0x08,
               gen_double_tile(gfx,
                               0, 0, (game->common.state_frames * 2) % 256, 64, 64,
                               1, 0, game->common.state_frames % 128, 32, 32));
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);

    append_setup_dl_25_to_xlu(gfx);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[1].dlist);
}

void draw_gi_gs_token(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);

    append_setup_dl_25_to_xlu(gfx);
    gSPSegment(gfx->poly_xlu.p++, 0x08,
               gen_double_tile(gfx,
                               0, 0, -(game->common.state_frames * 5), 32, 32,
                               1, 0, 0, 32, 64));
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[1].dlist);
}

void draw_gi_blue_fire_candle(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);

    append_setup_dl_25_to_xlu(gfx);
    gSPSegment(gfx->poly_xlu.p++, 0x08,
               gen_double_tile(gfx,
                               0, 0, 0, 16, 32,
                               1, game->common.state_frames * 1, -(game->common.state_frames * 8), 16, 32));
    duplicate_sys_matrix();
    translate_sys_matrix(-8.0f, -2.0f, 0.0f, 1);
    update_sys_matrix(game->mf_11DA0);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[1].dlist);
    pop_sys_matrix();
}

void draw_gi_fairy_lantern(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);

    append_setup_dl_25_to_xlu(gfx);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[1].dlist);
    gSPSegment(gfx->poly_xlu.p++, 0x08,
               gen_double_tile(gfx,
                               0, 0, 0, 32, 32,
                               1, game->common.state_frames, -(game->common.state_frames * 6), 32, 32));
    duplicate_sys_matrix();
    update_sys_matrix(game->mf_11DA0);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[2].dlist);
    pop_sys_matrix();
}

void draw_gi_fairy(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_xlu(gfx);
    gSPSegment(gfx->poly_xlu.p++, 0x08,
               gen_double_tile(gfx,
                               0, 0, 0, 32, 32,
                               1, game->common.state_frames, -(game->common.state_frames * 6), 32, 32));
    duplicate_sys_matrix();
    update_sys_matrix(game->mf_11DA0);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    // Not sure how much of this is required but these are called from the bottle DL. Not including them causes it to draw weird
    gDPSetRenderMode(gfx->poly_xlu.p++, G_RM_PASS, G_RM_AA_ZB_XLU_SURF2);
    gDPSetTextureLUT(gfx->poly_xlu.p++, G_TT_NONE);
    gSPLoadGeometryMode(gfx->poly_xlu.p++, G_ZBUFFER | G_SHADE | G_CULL_BACK | G_FOG | G_LIGHTING | G_SHADING_SMOOTH);
    gSPClearGeometryMode(gfx->poly_xlu.p++,G_CULL_BACK | G_FOG);
    gSPSetGeometryMode(gfx->poly_xlu.p++,G_LIGHTING | G_TEXTURE_GEN | G_TEXTURE_GEN_LINEAR);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[0].dlist);
    pop_sys_matrix();
}

void draw_gi_poe_bottles(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);

    append_setup_dl_25_to_xlu(gfx);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[1].dlist);
    gSPSegment(gfx->poly_xlu.p++, 0x08,
               gen_double_tile(gfx,
                               0, 0, 0, 16, 32,
                               1, game->common.state_frames * 1, -(game->common.state_frames * 6), 16, 32));
    duplicate_sys_matrix();
    update_sys_matrix(game->mf_11DA0);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[3].dlist);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[2].dlist);
    pop_sys_matrix();
}

void draw_gi_song_notes(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;
    colorRGBA8_t env_color = item_draw_table[draw_id].args[1].color;

    if (item_draw_table[draw_id].args[2].dlist) {
        scale_sys_matrix(1.5f, 1.5f, 1.5f, 1);
    }

    append_setup_dl_25_to_xlu(gfx);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gDPSetEnvColor(gfx->poly_xlu.p++, env_color.r, env_color.g, env_color.b, env_color.a);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[0].dlist);
}

void draw_gi_small_keys(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;
    colorRGBA8_t prim_color = item_draw_table[draw_id].args[1].color;
    colorRGBA8_t env_color = item_draw_table[draw_id].args[2].color;

    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gDPSetCombineMode(gfx->poly_opa.p++, G_CC_MODULATEI_PRIM, G_CC_MODULATEI_PRIM);
    gDPSetPrimColor(gfx->poly_opa.p++, 0, 0x80, prim_color.r, prim_color.g, prim_color.b, prim_color.a);
    gDPSetEnvColor(gfx->poly_opa.p++, env_color.r, env_color.g, env_color.b, env_color.a);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);
}

void draw_gi_shrink_keys(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;
    colorRGBA8_t prim_color = item_draw_table[draw_id].args[1].color;
    colorRGBA8_t env_color = item_draw_table[draw_id].args[2].color;

    translate_sys_matrix(0, 5, 0, 1);
    scale_sys_matrix(0.8f, 0.8f, 0.8f, 1);

    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gDPSetCombineMode(gfx->poly_opa.p++, G_CC_MODULATEI_PRIM, G_CC_MODULATEI_PRIM);
    gDPSetPrimColor(gfx->poly_opa.p++, 0, 0x80, prim_color.r, prim_color.g, prim_color.b, prim_color.a);
    gDPSetEnvColor(gfx->poly_opa.p++, env_color.r, env_color.g, env_color.b, env_color.a);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);
}

void draw_gi_boss_keys(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    colorRGBA8_t prim_color = item_draw_table[draw_id].args[2].color;
    colorRGBA8_t env_color = item_draw_table[draw_id].args[3].color;

    colorRGBA8_t prim_color_key = item_draw_table[draw_id].args[4].color;
    colorRGBA8_t env_color_key = item_draw_table[draw_id].args[5].color;

    translate_sys_matrix(0, 15, 0, 1);
    scale_sys_matrix(1.25f, 1.25f, 1.25f, 1);

    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gDPSetPrimColor(gfx->poly_opa.p++, 0, 0x80, prim_color_key.r, prim_color_key.g, prim_color_key.b, prim_color_key.a);
    gDPSetEnvColor(gfx->poly_opa.p++, env_color_key.r, env_color_key.g, env_color_key.b, env_color_key.a);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);

    append_setup_dl_25_to_xlu(gfx);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gDPSetPrimColor(gfx->poly_xlu.p++, 0, 0x80, prim_color.r, prim_color.g, prim_color.b, prim_color.a);
    gDPSetEnvColor(gfx->poly_xlu.p++, env_color.r, env_color.g, env_color.b, env_color.a);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[1].dlist);

}

// Gem DL First
void draw_gi_boss_altered(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;
    // extract gem colors
    colorRGBA8_t prim_color = item_draw_table[draw_id].args[2].color;
    colorRGBA8_t env_color = item_draw_table[draw_id].args[3].color;
    // extract key colors
    colorRGBA8_t prim_color_key = item_draw_table[draw_id].args[4].color;
    colorRGBA8_t env_color_key = item_draw_table[draw_id].args[5].color;
    // Move and Resize
    translate_sys_matrix(0, 5, 0, 1);
    scale_sys_matrix(0.8f, 0.8f, 0.8f, 1);
    // draw key
    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gDPSetPrimColor(gfx->poly_opa.p++, 0, 0x80, prim_color_key.r, prim_color_key.g, prim_color_key.b, prim_color_key.a);
    gDPSetEnvColor(gfx->poly_opa.p++, env_color_key.r, env_color_key.g, env_color_key.b, env_color_key.a);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[1].dlist);
    // draw gem
    append_setup_dl_25_to_xlu(gfx);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gDPSetPrimColor(gfx->poly_xlu.p++, 0, 0x80, prim_color.r, prim_color.g, prim_color.b, prim_color.a);
    gDPSetEnvColor(gfx->poly_xlu.p++, env_color.r, env_color.g, env_color.b, env_color.a);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[0].dlist);
}

// Key DL First
void draw_gi_boss_altflip(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;
    // extract gem colors
    colorRGBA8_t prim_color = item_draw_table[draw_id].args[2].color;
    colorRGBA8_t env_color = item_draw_table[draw_id].args[3].color;
    // extract key colors
    colorRGBA8_t prim_color_key = item_draw_table[draw_id].args[4].color;
    colorRGBA8_t env_color_key = item_draw_table[draw_id].args[5].color;
    // Move and Resize
    translate_sys_matrix(0, 5, 0, 1);
    scale_sys_matrix(0.8f, 0.8f, 0.8f, 1);
    // draw key
    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gDPSetPrimColor(gfx->poly_opa.p++, 0, 0x80, prim_color_key.r, prim_color_key.g, prim_color_key.b, prim_color_key.a);
    gDPSetEnvColor(gfx->poly_opa.p++, env_color_key.r, env_color_key.g, env_color_key.b, env_color_key.a);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);
    // draw gem
    append_setup_dl_25_to_xlu(gfx);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gDPSetPrimColor(gfx->poly_xlu.p++, 0, 0x80, prim_color.r, prim_color.g, prim_color.b, prim_color.a);
    gDPSetEnvColor(gfx->poly_xlu.p++, env_color.r, env_color.g, env_color.b, env_color.a);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[1].dlist);
}

void draw_gi_chubag(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;
    // Band
    colorRGBA8_t prim_color_band = item_draw_table[draw_id].args[5].color;
    colorRGBA8_t env_color_band = item_draw_table[draw_id].args[6].color;
    // Front
    colorRGBA8_t prim_color = item_draw_table[draw_id].args[3].color;
    colorRGBA8_t env_color = item_draw_table[draw_id].args[4].color;
    // Band
    append_setup_dl_25_to_xlu(gfx);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gDPSetPrimColor(gfx->poly_xlu.p++, 0, 0x80, prim_color_band.r, prim_color_band.g, prim_color_band.b, prim_color_band.a);
    gDPSetEnvColor(gfx->poly_xlu.p++, env_color_band.r, env_color_band.g, env_color_band.b, env_color_band.a);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[0].dlist);
    // Front
    append_setup_dl_25_to_xlu(gfx);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gDPSetPrimColor(gfx->poly_xlu.p++, 0, 0x80, prim_color.r, prim_color.g, prim_color.b, prim_color.a);
    gDPSetEnvColor(gfx->poly_xlu.p++, env_color.r, env_color.g, env_color.b, env_color.a);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[1].dlist);
    // Bag
    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[2].dlist);
}

void draw_gi_a_button(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;
    colorRGBA8_t prim_color = item_draw_table[draw_id].args[1].color;
    if (CFG_CORRECT_MODEL_COLORS) {
        prim_color.r = CFG_A_BUTTON_COLOR.r;
        prim_color.g = CFG_A_BUTTON_COLOR.g;
        prim_color.b = CFG_A_BUTTON_COLOR.b;
    }

    append_setup_dl_25_to_xlu(gfx);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gDPSetPrimColor(gfx->poly_xlu.p++, 0, 0x80, prim_color.r, prim_color.g, prim_color.b, prim_color.a);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[0].dlist);
}

void draw_gi_c_button_vertical(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;
    colorRGBA8_t prim_color = item_draw_table[draw_id].args[1].color;
    if (CFG_CORRECT_MODEL_COLORS) {
        prim_color.r = CFG_C_BUTTON_COLOR.r;
        prim_color.g = CFG_C_BUTTON_COLOR.g;
        prim_color.b = CFG_C_BUTTON_COLOR.b;
    }

    rotate_Z_sys_matrix(item_draw_table[draw_id].args[2].dlist*3.14f, 1);

    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gDPSetPrimColor(gfx->poly_opa.p++, 0, 0x80, prim_color.r, prim_color.g, prim_color.b, prim_color.a);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);
}

void draw_gi_c_button_horizontal(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;
    colorRGBA8_t prim_color = item_draw_table[draw_id].args[1].color;
    if (CFG_CORRECT_MODEL_COLORS) {
        prim_color.r = CFG_C_BUTTON_COLOR.r;
        prim_color.g = CFG_C_BUTTON_COLOR.g;
        prim_color.b = CFG_C_BUTTON_COLOR.b;
    }

    rotate_Z_sys_matrix(item_draw_table[draw_id].args[2].dlist*3.14f, 1);

    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gDPSetPrimColor(gfx->poly_opa.p++, 0, 0x80, prim_color.r, prim_color.g, prim_color.b, prim_color.a);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);
}

void draw_gi_nothing(z64_game_t* game, uint32_t draw_id) {
}

static const uint64_t kInitListMedallion[] = {
    0xe700000000000000, 0xd7000002ffffffff,
    0xfc11fe23fffff7fb, 0xef082c1000552078,
    0xd900000000220405, 0xdf00000000000000,
};

void draw_gi_medallions(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;

    append_setup_dl_25_to_opa(gfx);
    gSPDisplayList(gfx->poly_opa.p++, (uint32_t)(&kInitListMedallion));
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_PUSH | G_MTX_LOAD | G_MTX_MODELVIEW);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[0].dlist);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[1].dlist);
}

static void* pushOpaMatrix(z64_gfx_t* gfx, const float* mat) {
    void* end = gfx->poly_opa.d;
    end = (char*)end - 0x40;
    gfx->poly_opa.d = end;

    convert_matrix(mat, end);

    return end;
}

static void* pushXluMatrix(z64_gfx_t* gfx, const float* mat) {
    void* end = gfx->poly_xlu.d;
    end = (char*)end - 0x40;
    gfx->poly_xlu.d = end;

    convert_matrix(mat, end);

    return end;
}

static void* dummyOpaSegment(z64_gfx_t* gfx) {
    Gfx* end = gfx->poly_opa.d - 1;
    gfx->poly_opa.d = end;
    gSPEndDisplayList(end);
    return end;
}

static void* dummyXluSegment(z64_gfx_t* gfx) {
    Gfx* end = gfx->poly_xlu.d - 1;
    gfx->poly_xlu.d = end;
    gSPEndDisplayList(end);
    return end;
}

void draw_gi_stones(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t* gfx = game->common.gfx;
    colorRGBA8_t prim_color = item_draw_table[draw_id].args[2].color;
    colorRGBA8_t env_color = item_draw_table[draw_id].args[3].color;

    static const float kMatrixRot[] = {
        1.f, 0.f, 0.f, 0.f,
        0.f, 0.f, 1.f, 0.f,
        0.f, -1.f, 0.f, 0.f,
        0.f, 0.f, 0.f, 1.f,
    };

    /* Matrix setup */
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_PUSH | G_MTX_LOAD | G_MTX_MODELVIEW);
    gSPMatrix(gfx->poly_xlu.p++, pushXluMatrix(gfx, kMatrixRot), G_MTX_NOPUSH | G_MTX_MUL | G_MTX_MODELVIEW);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_PUSH | G_MTX_LOAD | G_MTX_MODELVIEW);
    gSPMatrix(gfx->poly_opa.p++, pushOpaMatrix(gfx, kMatrixRot), G_MTX_NOPUSH | G_MTX_MUL | G_MTX_MODELVIEW);

    /* Segment setup */
    gSPSegment(gfx->poly_xlu.p++, 9, dummyXluSegment(gfx));
    gSPSegment(gfx->poly_opa.p++, 8, dummyOpaSegment(gfx));

    append_setup_dl_25_to_xlu(gfx);
    gDPSetPrimColor(gfx->poly_xlu.p++, 0x00, 0x80, prim_color.r, prim_color.g, prim_color.b, prim_color.a);
    gDPSetEnvColor(gfx->poly_xlu.p++, env_color.r, env_color.g, env_color.b, env_color.a);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[0].dlist);

    append_setup_dl_25_to_opa(gfx);
    gDPSetPrimColor(gfx->poly_opa.p++, 0x00, 0x80, 0xff, 0xff, 0xaa, 0xff);
    gDPSetEnvColor(gfx->poly_opa.p++, 0x96, 0x78, 0x00, 0xFF);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[1].dlist);
}

void draw_gi_magic_meter(z64_game_t* game, uint32_t draw_id) {
    z64_gfx_t *gfx = game->common.gfx;

    // InnerOutline
    colorRGBA8_t prim_outline = item_draw_table[draw_id].args[5].color;
    // Container
    colorRGBA8_t prim_container = item_draw_table[draw_id].args[4].color;
    colorRGBA8_t env_color = item_draw_table[draw_id].args[4].color;
    // Magic
    colorRGBA8_t prim_color = item_draw_table[draw_id].args[3].color;
    if (CFG_CORRECT_MODEL_COLORS) {
        prim_color.r = CFG_MAGIC_COLOR .r;
        prim_color.g = CFG_MAGIC_COLOR .g;
        prim_color.b = CFG_MAGIC_COLOR .b;
    }

   // Magic
    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gDPSetPrimColor(gfx->poly_opa.p++, 0, 0x80, prim_color.r, prim_color.g, prim_color.b, prim_color.a);
    gDPSetEnvColor(gfx->poly_xlu.p++, env_color.r, env_color.g, env_color.b, env_color.a);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[1].dlist);
    // Container
    append_setup_dl_25_to_xlu(gfx);
    gSPMatrix(gfx->poly_xlu.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gDPSetPrimColor(gfx->poly_xlu.p++, 0, 0x80, prim_container.r, prim_container.g, prim_container.b, prim_container.a);
    gDPSetEnvColor(gfx->poly_xlu.p++, env_color.r, env_color.g, env_color.b, env_color.a);
    gSPDisplayList(gfx->poly_xlu.p++, item_draw_table[draw_id].args[0].dlist);
    // InnerOutline
    append_setup_dl_25_to_opa(gfx);
    gSPMatrix(gfx->poly_opa.p++, append_sys_matrix(gfx), G_MTX_MODELVIEW | G_MTX_LOAD | G_MTX_NOPUSH);
    gDPSetPrimColor(gfx->poly_opa.p++, 0, 0x80, prim_outline.r, prim_outline.g, prim_outline.b, prim_outline.a);
    gSPDisplayList(gfx->poly_opa.p++, item_draw_table[draw_id].args[2].dlist);

}
