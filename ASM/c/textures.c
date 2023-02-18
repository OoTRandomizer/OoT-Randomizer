#include "textures.h"


#define LEN_TEXTURE_TABLE 20

typedef struct {
    uint16_t textureID;
    file_t file;
} texture_t;

texture_t texture_table[LEN_TEXTURE_TABLE] = {
    [TEXTURE_ID_POT_GOLD] = { .textureID = TEXTURE_ID_POT_GOLD },
    [TEXTURE_ID_POT_KEY] = { .textureID = TEXTURE_ID_POT_KEY },
    [TEXTURE_ID_POT_BOSSKEY] = { .textureID = TEXTURE_ID_POT_BOSSKEY },
    [TEXTURE_ID_POT_SKULL] = { .textureID = TEXTURE_ID_POT_SKULL },
    [TEXTURE_ID_CRATE_DEFAULT] = { .textureID = TEXTURE_ID_CRATE_DEFAULT },
    [TEXTURE_ID_CRATE_GOLD] = { .textureID = TEXTURE_ID_CRATE_GOLD },
    [TEXTURE_ID_CRATE_KEY] = { .textureID = TEXTURE_ID_CRATE_KEY },
    [TEXTURE_ID_CRATE_BOSSKEY] = { .textureID = TEXTURE_ID_CRATE_BOSSKEY },
    [TEXTURE_ID_CRATE_SKULL] = { .textureID = TEXTURE_ID_CRATE_SKULL },
    [TEXTURE_ID_SMALLCRATE_GOLD] = { .textureID = TEXTURE_ID_SMALLCRATE_GOLD },
    [TEXTURE_ID_SMALLCRATE_KEY] = { .textureID = TEXTURE_ID_SMALLCRATE_KEY },
    [TEXTURE_ID_SMALLCRATE_SKULL] = { .textureID = TEXTURE_ID_SMALLCRATE_SKULL },
    [TEXTURE_ID_SMALLCRATE_BOSSKEY] = { .textureID = TEXTURE_ID_SMALLCRATE_BOSSKEY },
};

uint8_t *get_texture(uint16_t textureID) {
    return texture_table[textureID].file.buf;
}

void init_textures() {
    for (int i = 0; i < LEN_TEXTURE_TABLE; i++) {
        if (texture_table[i].file.vrom_start != 0x00000000) {
            file_init(&texture_table[i].file);
        }
    }
}
