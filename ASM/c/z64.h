#ifndef Z64_H
#define Z64_H
#include <stdint.h>
#include <n64.h>
#include "color.h"

#define Z64_OOT10             0x00
#define Z64_OOT11             0x01
#define Z64_OOT12             0x02

#define Z64_SCREEN_WIDTH      320
#define Z64_SCREEN_HEIGHT     240

#define Z64_SEG_PHYS          0x00
#define Z64_SEG_TITLE         0x01
#define Z64_SEG_SCENE         0x02
#define Z64_SEG_ROOM          0x03
#define Z64_SEG_KEEP          0x04
#define Z64_SEG_SKEEP         0x05
#define Z64_SEG_OBJ           0x06
#define Z64_SEG_ZIMG          0x0E
#define Z64_SEG_CIMG          0x0F

#define Z64_ETAB_LENGTH       0x0614

typedef struct
{
  int16_t x;
  int16_t y;
  int16_t z;
} z64_xyz_t;

typedef struct
{
  float x;
  float y;
  float z;
} z64_xyzf_t;

typedef uint16_t z64_angle_t;
typedef struct
{
  z64_angle_t x;
  z64_angle_t y;
  z64_angle_t z;
} z64_rot_t;

typedef struct
{
  /* index of z64_col_type in scene file */
  uint16_t    type;
  /* vertex indices, a and b are bitmasked for some reason */
  struct
  {
    uint16_t  unk_00_ : 3;
    uint16_t  va      : 13;
  };
  struct
  {
    uint16_t  unk_01_ : 3;
    uint16_t  vb      : 13;
  };
  uint16_t    vc;
  /* normal vector */
  z64_xyz_t   norm;
  /* plane distance from origin */
  int16_t     dist;
} z64_col_poly_t;

typedef struct
{
  struct
  {
    uint32_t  unk_00_     : 1;
    uint32_t  drop        : 1; /* link drops one unit into the floor */
    uint32_t  special     : 4;
    uint32_t  interaction : 5;
    uint32_t  unk_01_     : 3;
    uint32_t  behavior    : 5;
    uint32_t  exit        : 5;
    uint32_t  camera      : 8;
  } flags_1;                    /* 0x0000 */
  struct
  {
    uint32_t  pad_00_     : 4;
    uint32_t  wall_damage : 1;
    uint32_t  unk_00_     : 6;
    uint32_t  unk_01_     : 3;
    uint32_t  hookshot    : 1;
    uint32_t  echo        : 6;
    uint32_t  unk_02_     : 5;
    uint32_t  terrain     : 2;
    uint32_t  material    : 4;
  } flags_2;                    /* 0x0004 */
} z64_col_type_t;

typedef struct
{
  z64_xyz_t pos;
  z64_xyz_t rot;
  int16_t   fov;
  int16_t   unk_00_;
} z64_camera_params_t;

typedef struct
{
  uint16_t mode;
  uint16_t unk_01_;
  uint32_t seg_params; /* segment address of z64_camera_params_t */
} z64_camera_t;

typedef struct
{
  z64_xyz_t     pos;
  int16_t       width;
  int16_t       depth;
  struct
  {
    uint32_t    unk_00_ : 12;
    uint32_t    active  : 1;
    uint32_t    group   : 6; /* ? */
    uint32_t    unk_01_ : 5;
    uint32_t    camera  : 8;
  } flags;
} z64_col_water_t;

typedef struct
{
  z64_xyz_t         min;
  z64_xyz_t         max;
  uint16_t          n_vtx;
  z64_xyz_t        *vtx;
  uint16_t          n_poly;
  z64_col_poly_t   *poly;
  z64_col_type_t   *type;
  z64_camera_t     *camera;
  uint16_t          n_water;
  z64_col_water_t  *water;
} z64_col_hdr_t;

typedef enum
{
  Z64_ITEM_NULL = -1,
  Z64_ITEM_STICK,
  Z64_ITEM_NUT,
  Z64_ITEM_BOMB,
  Z64_ITEM_BOW,
  Z64_ITEM_FIRE_ARROW,
  Z64_ITEM_DINS_FIRE,
  Z64_ITEM_SLINGSHOT,
  Z64_ITEM_FAIRY_OCARINA,
  Z64_ITEM_OCARINA_OF_TIME,
  Z64_ITEM_BOMBCHU,
  Z64_ITEM_HOOKSHOT,
  Z64_ITEM_LONGSHOT,
  Z64_ITEM_ICE_ARROW,
  Z64_ITEM_FARORES_WIND,
  Z64_ITEM_BOOMERANG,
  Z64_ITEM_LENS,
  Z64_ITEM_BEANS,
  Z64_ITEM_HAMMER,
  Z64_ITEM_LIGHT_ARROW,
  Z64_ITEM_NAYRUS_LOVE,
  Z64_ITEM_BOTTLE,
  Z64_ITEM_RED_POTION,
  Z64_ITEM_GREEN_POTION,
  Z64_ITEM_BLUE_POTION,
  Z64_ITEM_FAIRY,
  Z64_ITEM_FISH,
  Z64_ITEM_MILK,
  Z64_ITEM_LETTER,
  Z64_ITEM_BLUE_FIRE,
  Z64_ITEM_BUG,
  Z64_ITEM_BIG_POE,
  Z64_ITEM_HALF_MILK,
  Z64_ITEM_POE,
  Z64_ITEM_WEIRD_EGG,
  Z64_ITEM_CHICKEN,
  Z64_ITEM_ZELDAS_LETTER,
  Z64_ITEM_KEATON_MASK,
  Z64_ITEM_SKULL_MASK,
  Z64_ITEM_SPOOKY_MASK,
  Z64_ITEM_BUNNY_HOOD,
  Z64_ITEM_GORON_MASK,
  Z64_ITEM_ZORA_MASK,
  Z64_ITEM_GERUDO_MASK,
  Z64_ITEM_MASK_OF_TRUTH,
  Z64_ITEM_SOLD_OUT,
  Z64_ITEM_POCKET_EGG,
  Z64_ITEM_POCKET_CUCCO,
  Z64_ITEM_COJIRO,
  Z64_ITEM_ODD_MUSHROOM,
  Z64_ITEM_ODD_POTION,
  Z64_ITEM_POACHERS_SAW,
  Z64_ITEM_BROKEN_GORONS_SWORD,
  Z64_ITEM_PRESCRIPTION,
  Z64_ITEM_EYEBALL_FROG,
  Z64_ITEM_EYE_DROPS,
  Z64_ITEM_CLAIM_CHECK,
  Z64_ITEM_BOW_FIRE_ARROW,
  Z64_ITEM_BOW_ICE_ARROW,
  Z64_ITEM_BOW_LIGHT_ARROW,
  Z64_ITEM_KOKIRI_SWORD,
  Z64_ITEM_MASTER_SWORD,
  Z64_ITEM_BIGGORON_SWORD,
  Z64_ITEM_DEKU_SHIELD,
  Z64_ITEM_HYLIAN_SHIELD,
  Z64_ITEM_MIRROR_SHIELD,
  Z64_ITEM_KOKIRI_TUNIC,
  Z64_ITEM_GORON_TUNIC,
  Z64_ITEM_ZORA_TUNIC,
  Z64_ITEM_KOKIRI_BOOTS,
  Z64_ITEM_IRON_BOOTS,
  Z64_ITEM_HOVER_BOOTS,
  Z64_ITEM_BULLET_BAG_30,
  Z64_ITEM_BULLET_BAG_40,
  Z64_ITEM_BULLET_BAG_50,
  Z64_ITEM_QUIVER_30,
  Z64_ITEM_QUIVER_40,
  Z64_ITEM_QUIVER_50,
  Z64_ITEM_BOMB_BAG_20,
  Z64_ITEM_BOMB_BAG_30,
  Z64_ITEM_BOMB_BAG_40,
  Z64_ITEM_GORONS_BRACELET,
  Z64_ITEM_SILVER_GAUNTLETS,
  Z64_ITEM_GOLDEN_GAUNTLETS,
  Z64_ITEM_SILVER_SCALE,
  Z64_ITEM_GOLDEN_SCALE,
  Z64_ITEM_BROKEN_GIANTS_KNIFE,
  Z64_ITEM_ADULTS_WALLET,
  Z64_ITEM_GIANTS_WALLET,
  Z64_ITEM_DEKU_SEEDS,
  Z64_ITEM_FISHING_POLE,
  Z64_ITEM_MINUET,
  Z64_ITEM_BOLERO,
  Z64_ITEM_SERENADE,
  Z64_ITEM_REQUIEM,
  Z64_ITEM_NOCTURNE,
  Z64_ITEM_PRELUDE,
  Z64_ITEM_ZELDAS_LULLABY,
  Z64_ITEM_EPONAS_SONG,
  Z64_ITEM_SARIAS_SONG,
  Z64_ITEM_SUNS_SONG,
  Z64_ITEM_SONG_OF_TIME,
  Z64_ITEM_SONG_OF_STORMS,
  Z64_ITEM_FOREST_MEDALLION,
  Z64_ITEM_FIRE_MEDALLION,
  Z64_ITEM_WATER_MEDALLION,
  Z64_ITEM_SPIRIT_MEDALLION,
  Z64_ITEM_SHADOW_MEDALLION,
  Z64_ITEM_LIGHT_MEDALLION,
  Z64_ITEM_KOKIRIS_EMERALD,
  Z64_ITEM_GORONS_RUBY,
  Z64_ITEM_ZORAS_SAPPHIRE,
  Z64_ITEM_STONE_OF_AGONY,
  Z64_ITEM_GERUDOS_CARD,
  Z64_ITEM_GOLD_SKULLTULA,
  Z64_ITEM_HEART_CONTAINER,
  Z64_ITEM_PIECE_OF_HEART,
  Z64_ITEM_BOSS_KEY,
  Z64_ITEM_COMPASS,
  Z64_ITEM_DUNGEON_MAP,
  Z64_ITEM_SMALL_KEY,
  Z64_ITEM_MAGIC_SMALL,
  Z64_ITEM_MAGIC_LARGE,
} z64_item_t;

typedef enum
{
  Z64_SLOT_STICK,
  Z64_SLOT_NUT,
  Z64_SLOT_BOMB,
  Z64_SLOT_BOW,
  Z64_SLOT_FIRE_ARROW,
  Z64_SLOT_DINS_FIRE,
  Z64_SLOT_SLINGSHOT,
  Z64_SLOT_OCARINA,
  Z64_SLOT_BOMBCHU,
  Z64_SLOT_HOOKSHOT,
  Z64_SLOT_ICE_ARROW,
  Z64_SLOT_FARORES_WIND,
  Z64_SLOT_BOOMERANG,
  Z64_SLOT_LENS,
  Z64_SLOT_BEANS,
  Z64_SLOT_HAMMER,
  Z64_SLOT_LIGHT_ARROW,
  Z64_SLOT_NAYRUS_LOVE,
  Z64_SLOT_BOTTLE_1,
  Z64_SLOT_BOTTLE_2,
  Z64_SLOT_BOTTLE_3,
  Z64_SLOT_BOTTLE_4,
  Z64_SLOT_ADULT_TRADE,
  Z64_SLOT_CHILD_TRADE,
} z64_slot_t;

typedef enum
{
  Z64_ITEMBTN_B,
  Z64_ITEMBTN_CL,
  Z64_ITEMBTN_CD,
  Z64_ITEMBTN_CR,
} z64_itembtn_t;

typedef struct
{
  char      unk_00_[0x006E];        /* 0x0000 */
  int16_t   run_speed_limit;        /* 0x006E */
  char      unk_01_[0x0004];        /* 0x0070 */
  int16_t   run_speed_max_anim;     /* 0x0074 */
  char      unk_02_[0x0026];        /* 0x0076 */
  int16_t   gravity;                /* 0x009C */
  char      unk_03_[0x0072];        /* 0x009E */
  uint16_t  update_rate;            /* 0x0110 */
  char      unk_04_[0x0022];        /* 0x0112 */
  int16_t   override_aspect;        /* 0x0134 */
  uint16_t  aspect_width;           /* 0x0136 */
  uint16_t  aspect_height;          /* 0x0138 */
  char      unk_05_[0x0050];        /* 0x013A */
  int16_t   game_playing;           /* 0x018A */
  char      unk_06_[0x03B8];        /* 0x018C */
  uint16_t  c_up_icon_x;            /* 0x0544 */
  uint16_t  c_up_icon_y;            /* 0x0546 */
  char      unk_07_[0x021C];        /* 0x0548 */
  uint16_t  game_freeze;            /* 0x0764 */
  char      unk_08_[0x002E];        /* 0x0766 */
  uint16_t  magic_fill_r;           /* 0x0794 */
  uint16_t  magic_fill_g;           /* 0x0796 */
  uint16_t  magic_fill_b;           /* 0x0798 */
  char      unk_09_[0x004A];        /* 0x079A */
  uint16_t  c_button_r;             /* 0x07E4 */
  uint16_t  c_button_g;             /* 0x07E6 */
  uint16_t  c_button_b;             /* 0x07E8 */
  uint16_t  b_button_r;             /* 0x07EA */
  uint16_t  b_button_g;             /* 0x07EC */
  uint16_t  b_button_b;             /* 0x07EE */
  char      unk_0A_[0x0004];        /* 0x07F0 */
  qs510_t   start_icon_dd;          /* 0x07F4 */
  int16_t   start_icon_scale;       /* 0x07F6 */
  char      unk_0B_[0x0006];        /* 0x07F8 */
  uint16_t  start_icon_y;           /* 0x07FE */
  char      unk_0C_[0x0002];        /* 0x0800 */
  uint16_t  start_icon_x;           /* 0x0802 */
  char      unk_0D_[0x000C];        /* 0x0804 */
  uint16_t  c_up_button_x;          /* 0x0810 */
  uint16_t  c_up_button_y;          /* 0x0812 */
  char      unk_0E_[0x0008];        /* 0x0814 */
  uint16_t  start_button_x;         /* 0x081C */
  uint16_t  start_button_y;         /* 0x081E */
  uint16_t  item_button_x[4];       /* 0x0820 */
  uint16_t  item_button_y[4];       /* 0x0828 */
  qs510_t   item_button_dd[4];      /* 0x0830 */
  uint16_t  item_icon_x[4];         /* 0x0838 */
  uint16_t  item_icon_y[4];         /* 0x0840 */
  qs510_t   item_icon_dd[4];        /* 0x0848 */
  char      unk_0F_[0x0264];        /* 0x0850 */
  uint16_t  a_button_y;             /* 0x0AB4 */
  uint16_t  a_button_x;             /* 0x0AB6 */
  char      unk_10_[0x0002];        /* 0x0AB8 */
  uint16_t  a_button_icon_y;        /* 0x0ABA */
  uint16_t  a_button_icon_x;        /* 0x0ABC */
  char      unk_11_[0x0002];        /* 0x0ABE */
  uint16_t  a_button_r;             /* 0x0AC0 */
  uint16_t  a_button_g;             /* 0x0AC2 */
  uint16_t  a_button_b;             /* 0x0AC4 */
  char      unk_12_[0x0030];        /* 0x0AC6 */
  uint16_t  magic_bar_x;            /* 0x0AF6 */
  uint16_t  magic_bar_y;            /* 0x0AF8 */
  uint16_t  magic_fill_x;           /* 0x0AFA */
  char      unk_13_[0x02D6];        /* 0x0AFC */
  int16_t   minimap_disabled;       /* 0x0DD2 */
  char      unk_14_[0x01C0];        /* 0x0DD4 */
  uint16_t  item_ammo_x[4];         /* 0x0F94 */
  uint16_t  item_ammo_y[4];         /* 0x0F9C */
  char      unk_15_[0x0008];        /* 0x0FA4 */
  uint16_t  item_icon_space[4];     /* 0x0FAC */
  uint16_t  item_button_space[4];   /* 0x0FB4 */
                                    /* 0x0FBC */
} z64_gameinfo_t;

typedef struct
{
  int32_t         entrance_index;           /* 0x0000 */
  int32_t         link_age;                 /* 0x0004 */
  char            unk_00_[0x0002];          /* 0x0008 */
  uint16_t        cutscene_index;           /* 0x000A */
  uint16_t        day_time;                 /* 0x000C */
  char            unk_01_[0x0002];          /* 0x000E */
  int32_t         night_flag;               /* 0x0010 */
  char            unk_02_[0x0008];          /* 0x0014 */
  char            id[6];                    /* 0x001C */
  int16_t         deaths;                   /* 0x0022 */
  char            file_name[0x08];          /* 0x0024 */
  int16_t         n64dd_flag;               /* 0x002C */
  int16_t         energy_capacity;          /* 0x002E */
  int16_t         energy;                   /* 0x0030 */
  uint8_t         magic_capacity_set;       /* 0x0032 */
  uint8_t         magic;                    /* 0x0033 */
  uint16_t        rupees;                   /* 0x0034 */
  uint16_t        bgs_hits_left;            /* 0x0036 */
  uint16_t        navi_timer;               /* 0x0038 */
  uint8_t         magic_acquired;           /* 0x003A */
  char            unk_03_;                  /* 0x003B */
  uint8_t         magic_capacity;           /* 0x003C */
  int8_t          double_defense;           /* 0x003D */
  int8_t          bgs_flag;                 /* 0x003E */
  char            unk_05_;                  /* 0x003F */
  int8_t          child_button_items[4];    /* 0x0040 */
  int8_t          child_c_button_slots[3];  /* 0x0044 */
  union
  {
    uint16_t      child_equips;             /* 0x0048 */
    struct
    {
      uint16_t    child_equip_boots   : 4;
      uint16_t    child_equip_tunic   : 4;
      uint16_t    child_equip_shield  : 4;
      uint16_t    child_equip_sword   : 4;
    };
  };
  int8_t          adult_button_items[4];    /* 0x004A */
  int8_t          adult_c_button_slots[3];  /* 0x004E */
  union
  {
    uint16_t      adult_equips;             /* 0x0052 */
    struct
    {
      uint16_t    adult_equip_boots   : 4;
      uint16_t    adult_equip_tunic   : 4;
      uint16_t    adult_equip_shield  : 4;
      uint16_t    adult_equip_sword   : 4;
    };
  };
  char            unk_06_[0x0012];          /* 0x0054 */
  int16_t         scene_index;              /* 0x0066 */
  int8_t          button_items[4];          /* 0x0068 */
  int8_t          c_button_slots[3];        /* 0x006C */
  union
  {
    uint16_t      equips;                   /* 0x0070 */
    struct
    {
      uint16_t    equip_boots         : 4;
      uint16_t    equip_tunic         : 4;
      uint16_t    equip_shield        : 4;
      uint16_t    equip_sword         : 4;
    };
  };
  char            unk_07_[0x0002];          /* 0x0072 */
  int8_t          items[24];                /* 0x0074 */
  int8_t          ammo[15];                 /* 0x008C */
  uint8_t         magic_beans_sold;         /* 0x009B */
  union
  {
    uint16_t      equipment;                /* 0x009C */
    struct
    {
      uint16_t                        : 1;
      uint16_t    hover_boots         : 1;
      uint16_t    iron_boots          : 1;
      uint16_t    kokiri_boots        : 1;
      uint16_t                        : 1;
      uint16_t    zora_tunic          : 1;
      uint16_t    goron_tunic         : 1;
      uint16_t    kokiri_tunic        : 1;
      uint16_t                        : 1;
      uint16_t    mirror_shield       : 1;
      uint16_t    hylian_shield       : 1;
      uint16_t    deku_shield         : 1;
      uint16_t    broken_giants_knife : 1;
      uint16_t    giants_knife        : 1;
      uint16_t    master_sword        : 1;
      uint16_t    kokiri_sword        : 1;
    };
  };
  char            unk_08_[0x0002];          /* 0x009E */
  union
  {
    uint32_t      equipment_items;          /* 0x00A0 */
    struct
    {
      uint32_t                        : 9;
      uint32_t    nut_upgrade         : 3;
      uint32_t    stick_upgrade       : 3;
      uint32_t    bullet_bag          : 3;
      uint32_t    wallet              : 2;
      uint32_t    diving_upgrade      : 3;
      uint32_t    strength_upgrade    : 3;
      uint32_t    bomb_bag            : 3;
      uint32_t    quiver              : 3;
    };
  };
  union
  {
    uint32_t      quest_items;              /* 0x00A4 */
    struct
    {
      uint32_t    heart_pieces        : 8;
      uint32_t    gold_skulltula      : 1;
      uint32_t    gerudos_card        : 1;
      uint32_t    stone_of_agony      : 1;
      uint32_t    zoras_sapphire      : 1;
      uint32_t    gorons_ruby         : 1;
      uint32_t    kokiris_emerald     : 1;
      uint32_t    song_of_storms      : 1;
      uint32_t    song_of_time        : 1;
      uint32_t    suns_song           : 1;
      uint32_t    sarias_song         : 1;
      uint32_t    eponas_song         : 1;
      uint32_t    zeldas_lullaby      : 1;
      uint32_t    prelude_of_light    : 1;
      uint32_t    nocturne_of_shadow  : 1;
      uint32_t    requiem_of_spirit   : 1;
      uint32_t    serenade_of_water   : 1;
      uint32_t    bolero_of_fire      : 1;
      uint32_t    minuet_of_forest    : 1;
      uint32_t    light_medallion     : 1;
      uint32_t    shadow_medallion    : 1;
      uint32_t    spirit_medallion    : 1;
      uint32_t    water_medallion     : 1;
      uint32_t    fire_medallion      : 1;
      uint32_t    forest_medallion    : 1;
    };
  };
  union
  {
    uint8_t       items;
    struct
    {
      uint8_t                         : 5;
      uint8_t     map                 : 1;
      uint8_t     compass             : 1;
      uint8_t     boss_key            : 1;
    };
  }               dungeon_items[20];        /* 0x00A8 */
  int8_t          dungeon_keys[19];         /* 0x00BC */
  uint8_t         defense_hearts;           /* 0x00CF */
  int16_t         gs_tokens;                /* 0x00D0 */
  char            unk_09_[0x0002];          /* 0x00D2 */
  struct
  {
    uint32_t      chest;
    uint32_t      swch;
    uint32_t      clear;
    uint32_t      collect;
    uint32_t      unk_00_;
    uint32_t      rooms_1;
    uint32_t      rooms_2;
  }               scene_flags[101];         /* 0x00D4 */
  char            unk_0A_[0x0284];          /* 0x0BE0 */
  z64_xyzf_t      fw_pos;                   /* 0x0E64 */
  z64_angle_t     fw_yaw;                   /* 0x0E70 */
  char            unk_0B_[0x0008];          /* 0x0E72 */
  uint16_t        fw_scene_index;           /* 0x0E7A */
  uint32_t        fw_room_index;            /* 0x0E7C */
  int32_t         fw_set;                   /* 0x0E80 */
  char            unk_0C_[0x0018];          /* 0x0E84 */
  uint8_t         gs_flags[56];             /* 0x0E9C */
  uint16_t        event_chk_inf[14];        /* 0x0ED4 */
  uint16_t        item_get_inf[4];          /* 0x0EF0 */
  uint16_t        inf_table[30];            /* 0x0EF8 */
  char            unk_0D_[0x041E];          /* 0x0F34 */
  uint16_t        checksum;                 /* 0x1352 */
  char            unk_0E_[0x0003];          /* 0x1354 */
  int8_t          file_index;               /* 0x1357 */
  char            unk_0F_[0x0004];          /* 0x1358 */
  int32_t         game_mode;                /* 0x135C */
  uint32_t        scene_setup_index;        /* 0x1360 */
  int32_t         void_flag;                /* 0x1364 */
  z64_xyzf_t      void_pos;                 /* 0x1368 */
  z64_angle_t     void_yaw;                 /* 0x1374 */
  int16_t         void_var;                 /* 0x1376 */
  int16_t         void_entrance;            /* 0x1378 */
  int8_t          void_room_index;          /* 0x137A */
  int8_t          unk_10_;                  /* 0x137B */
  uint32_t        temp_swch_flags;          /* 0x137C */
  uint32_t        temp_collect_flags;       /* 0x1380 */
  char            unk_11_[0x0013];          /* 0x1384 */
  uint8_t         grotto_id;                /* 0x1397 */
  char            unk_12_[0x0030];          /* 0x1398 */
  uint16_t        nayrus_love_timer;        /* 0x13C8 */
  char            unk_13_[0x0004];          /* 0x13CA */
  int16_t         timer_1_state;            /* 0x13CE */
  int16_t         timer_1_value;            /* 0x13D0 */
  int16_t         timer_2_state;            /* 0x13D2 */
  int16_t         timer_2_value;            /* 0x13D4 */
  char            unk_14_[0x000A];          /* 0x13D6 */
  int8_t          seq_index;                /* 0x13E0 */
  int8_t          night_sfx;                /* 0x13E1 */
  char            unk_15_[0x0012];          /* 0x13E2 */
  uint16_t        magic_meter_size;         /* 0x13F4 */
  char            unk_16_[0x0004];          /* 0x13F6 */
  uint16_t        event_inf[4];             /* 0x13FA */
  char            unk_17_[0x0001];          /* 0x1402 */
  uint8_t         minimap_index;            /* 0x1403 */
  int16_t         minigame_state;           /* 0x1404 */
  char            unk_18_[0x0003];          /* 0x1406 */
  uint8_t         language;                 /* 0x1409 */
  char            unk_19_[0x0002];          /* 0x140A */
  uint8_t         z_targeting;              /* 0x140C */
  char            unk_1A_[0x0001];          /* 0x140D */
  uint16_t        disable_music_flag;       /* 0x140E */
  char            unk_1B_[0x0002];          /* 0x1410 */
  uint16_t        cutscene_next;            /* 0x1412 */
  char            unk_1C_[0x0010];          /* 0x1414 */
  uint16_t        refill_hearts;            /* 0x1424 */
  char            unk_1D_[0x000A];          /* 0x1426 */
  z64_gameinfo_t *gameinfo;                 /* 0x1430 */
  char            unk_1E_[0x001C];          /* 0x1434 */
                                            /* 0x1450 */
} z64_file_t;

typedef struct
{
    uint8_t       sound_options;            /* 0x0000 */
    uint8_t       z_target_options;         /* 0x0001 */
    uint8_t       language_options;         /* 0x0002 */
    char          verification_string[9];   /* 0x0003 */
    char          unk_00_[0x0014];          /* 0x000C */
    z64_file_t    primary_saves[3];         /* 0x0020 */
    z64_file_t    backup_saves[3];          /* 0x3D10 */
                                            /* 0x7A00 */
} z64_sram_data_t;

typedef struct
{
  uint32_t seg[16];
} z64_stab_t;

typedef struct
{
  uint8_t       scene_index;
  uint8_t       entrance_index;
  union
  {
    uint16_t    variable;
    struct
    {
      uint16_t  transition_out  : 7;
      uint16_t  transition_in   : 7;
      uint16_t  unk_00_         : 1;
      uint16_t  continue_music  : 1;
    };
  };
} z64_entrance_table_t;

typedef struct
{
  uint32_t scene_vrom_start;
  uint32_t scene_vrom_end;
  uint32_t title_vrom_start;
  uint32_t title_vrom_end;
  char     unk_00_;
  uint8_t  scene_config;
  char     unk_01_;
  char     padding_00_;
} z64_scene_table_t;

typedef struct
{
  uint32_t        size;                 /* 0x0000 */
  Gfx            *buf;                  /* 0x0004 */
  Gfx            *p;                    /* 0x0008 */
  Gfx            *d;                    /* 0x000C */
} z64_disp_buf_t;

typedef struct
{
  Gfx            *poly_opa_w;           /* 0x0000 */
  Gfx            *poly_xlu_w;           /* 0x0004 */
  char            unk_00_[0x0008];      /* 0x0008 */
  Gfx            *overlay_w;            /* 0x0010 */
  char            unk_01_[0x00A4];      /* 0x0014 */
  Gfx            *work_c;               /* 0x00B8 */
  uint32_t        work_c_size;          /* 0x00BC */
  char            unk_02_[0x00F0];      /* 0x00C0 */
  Gfx            *work_w;               /* 0x01B0 */
  z64_disp_buf_t  work;                 /* 0x01B4 */
  char            unk_03_[0x00E4];      /* 0x01C4 */
  z64_disp_buf_t  overlay;              /* 0x02A8 */
  z64_disp_buf_t  poly_opa;             /* 0x02B8 */
  z64_disp_buf_t  poly_xlu;             /* 0x02C8 */
  uint32_t        frame_count_1;        /* 0x02D8 */
  void           *frame_buffer;         /* 0x02DC */
  char            unk_04_[0x0008];      /* 0x02E0 */
  uint32_t        frame_count_2;        /* 0x02E8 */
                                        /* 0x02EC */
} z64_gfx_t;

typedef union
{
  struct
  {
    uint16_t  a  : 1;
    uint16_t  b  : 1;
    uint16_t  z  : 1;
    uint16_t  s  : 1;
    uint16_t  du : 1;
    uint16_t  dd : 1;
    uint16_t  dl : 1;
    uint16_t  dr : 1;
    uint16_t     : 2;
    uint16_t  l  : 1;
    uint16_t  r  : 1;
    uint16_t  cu : 1;
    uint16_t  cd : 1;
    uint16_t  cl : 1;
    uint16_t  cr : 1;
  };
  uint16_t    pad;
} pad_t;

typedef struct
{
  pad_t         pad;
  int8_t        x;
  int8_t        y;
} z64_controller_t;

typedef enum {
    ACTORTYPE_SWITCH,
    ACTORTYPE_BG,
    ACTORTYPE_PLAYER,
    ACTORTYPE_EXPLOSIVES,
    ACTORTYPE_NPC,
    ACTORTYPE_ENEMY,
    ACTORTYPE_PROP,
    ACTORTYPE_ITEMACTION,
    ACTORTYPE_MISC,
    ACTORTYPE_BOSS,
    ACTORTYPE_DOOR,
    ACTORTYPE_CHEST
} actor_type_t;

typedef struct z64_actor_s z64_actor_t;
struct z64_actor_s
{
  int16_t         actor_id;         /* 0x0000 */
  uint8_t         actor_type;       /* 0x0002 */
  int8_t          room_index;       /* 0x0003 */
  uint32_t        flags;            /* 0x0004 */
  z64_xyzf_t      pos_1;            /* 0x0008 */
  z64_rot_t       rot_init;         /* 0x0014 */
  char            unk_01_[0x0002];  /* 0x001A */
  uint16_t        variable;         /* 0x001C */
  uint8_t         alloc_index;      /* 0x001E */
  char            navi_tgt_dist;    /* 0x001F */
  uint16_t        sound_effect;     /* 0x0020 */
  char            unk_03_[0x0002];  /* 0x0022 */
  z64_xyzf_t      pos_2;            /* 0x0024 */
  char            unk_04_[0x0002];  /* 0x0030 */
  uint16_t        xz_dir;           /* 0x0032 */
  char            unk_05_[0x0004];  /* 0x0034 */
  z64_xyzf_t      pos_3;            /* 0x0038 */
  z64_rot_t       rot_1;            /* 0x0044 */
  char            unk_06_[0x0002];  /* 0x004A */
  float           unk_07_;          /* 0x004C */
  z64_xyzf_t      scale;            /* 0x0050 */
  z64_xyzf_t      vel_1;            /* 0x005C */
  float           xz_speed;         /* 0x0068 */
  float           gravity;          /* 0x006C */
  float           min_vel_y;        /* 0x0070 */
  void           *unk_08_;          /* 0x0074 */
  z64_col_poly_t *floor_poly;       /* 0x0078 */
  char            unk_09_[0x000C];  /* 0x007C */
  uint16_t        unk_flags_00;     /* 0x0088 */
  int16_t         unk_roty;         /* 0x008A */
  float           distsq_from_link; /* 0x008C */
  float           xzdist_from_link; /* 0x0090 */
  float           ydist_from_link;  /* 0x0094 */
  void           *damage_table;     /* 0x0098 */
  z64_xyzf_t      vel_2;            /* 0x009C */
  char            unk_0C_[0x0006];  /* 0x00A8 */
  int16_t         health;           /* 0x00AE */
  char            unk_0D_;          /* 0x00B0 */
  uint8_t         damage_effect;    /* 0x00B1 */
  char            unk_0E_[0x0002];  /* 0x00B2 */
  z64_rot_t       rot_2;            /* 0x00B4 */
  char            unk_0F_[0x0046];  /* 0x00BA */
  z64_xyzf_t      pos_4;            /* 0x0100 */
  uint16_t        unk_10_;          /* 0x010C */
  uint16_t        text_id;          /* 0x010E */
  int16_t         frozen;           /* 0x0110 */
  char            unk_11_[0x0003];  /* 0x0112 */
  uint8_t         active;           /* 0x0115 */
  char            unk_12_[0x0002];  /* 0x0116 */
  z64_actor_t    *parent;           /* 0x0118 */
  z64_actor_t    *child;            /* 0x011C */
  z64_actor_t    *prev;             /* 0x0120 */
  z64_actor_t    *next;             /* 0x0124 */
  void           *ctor;             /* 0x0128 */
  void           *dtor;             /* 0x012C */
  void           *main_proc;        /* 0x0130 */
  void           *draw_proc;        /* 0x0134 */
  void           *code_entry;       /* 0x0138 */
                                    /* 0x013C */
};

typedef struct
{
  z64_actor_t  common;               /* 0x0000 */
  char         unk_00_[0x02E8];      /* 0x013C */
  int8_t       incoming_item_id;     /* 0x0424 */
  char         unk_01_[0x0003];      /* 0x0425 */
  z64_actor_t *incoming_item_actor;  /* 0x0428 */
  char         unk_02_[0x0008];      /* 0x042C */
  uint8_t      action;               /* 0x0434 */
  char         unk_03_[0x0237];      /* 0x0435 */
  uint32_t     state_flags_1;        /* 0x066C */
  uint32_t     state_flags_2;        /* 0x0670 */
  char         unk_04_[0x0004];      /* 0x0674 */
  z64_actor_t *boomerang_actor;      /* 0x0678 */
  z64_actor_t *navi_actor;           /* 0x067C */
  char         unk_05_[0x01A8];      /* 0x0680 */
  float        linear_vel;           /* 0x0828 */
  char         unk_06_[0x0002];      /* 0x082C */
  uint16_t     target_yaw;           /* 0x082E */
  char         unk_07_[0x0003];      /* 0x0830 */
  int8_t       sword_state;          /* 0x0833 */
  char         unk_08_[0x0050];      /* 0x0834 */
  int16_t      drop_y;               /* 0x0884 */
  int16_t      drop_distance;        /* 0x0886 */
                                     /* 0x0888 */
} z64_link_t;

typedef struct
{
  z64_controller_t  raw;
  uint16_t          unk_00_;
  z64_controller_t  raw_prev;
  uint16_t          unk_01_;
  pad_t             pad_pressed;
  int8_t            x_diff;
  int8_t            y_diff;
  char              unk_02_[0x0002];
  pad_t             pad_released;
  int8_t            adjusted_x;
  int8_t            adjusted_y;
  char              unk_03_[0x0002];
} z64_input_t;

/* context base */
typedef struct
{
  z64_gfx_t      *gfx;                    /* 0x0000 */
  void           *state_main;             /* 0x0004 */
  void           *state_dtor;             /* 0x0008 */
  void           *next_ctor;              /* 0x000C */
  uint32_t        next_size;              /* 0x0010 */
  z64_input_t     input[4];               /* 0x0014 */
  uint32_t        state_heap_size;        /* 0x0074 */
  void           *state_heap;             /* 0x0078 */
  void           *heap_start;             /* 0x007C */
  void           *heap_end;               /* 0x0080 */
  void           *state_heap_node;        /* 0x0084 */
  char            unk_00_[0x0010];        /* 0x0088 */
  int32_t         state_continue;         /* 0x0098 */
  int32_t         state_frames;           /* 0x009C */
  uint32_t        unk_01_;                /* 0x00A0 */
                                          /* 0x00A4 */
} z64_ctxt_t;

typedef struct
{
  /* file loading params */
  uint32_t      vrom_addr;
  void         *dram_addr;
  uint32_t      size;
  /* unknown, seem to be unused */
  void         *unk_00_;
  uint32_t      unk_01_;
  uint32_t      unk_02_;
  /* completion notification params */
  OSMesgQueue  *notify_queue;
  OSMesg        notify_message;
} z64_getfile_t;

/* object structs */
typedef struct
{
  int16_t       id;
  void         *data;
  z64_getfile_t getfile;
  OSMesgQueue   load_mq;
  OSMesg        load_m;
} z64_mem_obj_t;

typedef struct
{
  void         *obj_space_start;
  void         *obj_space_end;
  uint8_t       n_objects;
  uint8_t       n_spawned_objects;
  uint8_t       keep_index;
  uint8_t       skeep_index;
  z64_mem_obj_t objects[19];
} z64_obj_ctxt_t;

typedef struct
{
    char              unk_00_[0x0128];          /* 0x0000 */
    void             *icon_item;                /* 0x0128 */
    void             *icon_item_24;             /* 0x012C */
    void             *icon_item_s;              /* 0x0130 */
    void             *icon_item_lang;           /* 0x0134 */
    void             *name_texture;             /* 0x0138 */
    void             *p13C;                     /* 0x013C */
    char              unk_01_[0x0094];          /* 0x0140 */
    uint16_t          state;                    /* 0x01D4 */
    char              unk_02_[0x000E];          /* 0x01D6 */
    uint16_t          changing;                 /* 0x01E4 */
    uint16_t          screen_prev_idx;          /* 0x01E6 */
    uint16_t          screen_idx;               /* 0x01E8 */
    char              unk_03_[0x002E];          /* 0x01EA */
    int16_t           item_cursor;              /* 0x0218 */
    char              unk_04_[0x0002];          /* 0x021A */
    int16_t           quest_cursor;             /* 0x021C */
    int16_t           equip_cursor;             /* 0x021E */
    int16_t           map_cursor;               /* 0x0220 */
    int16_t           item_x;                   /* 0x0222 */
    char              unk_05_[0x0004];          /* 0x0224 */
    int16_t           equipment_x;              /* 0x0228 */
    char              unk_06_[0x0002];          /* 0x022A */
    int16_t           item_y;                   /* 0x022C */
    char              unk_07_[0x0004];          /* 0x022E */
    int16_t           equipment_y;              /* 0x0232 */
    char              unk_08_[0x0004];          /* 0x0234 */
    int16_t           cursor_pos;               /* 0x0238 */
    char              unk_09_[0x0002];          /* 0x023A */
    int16_t           item_id;                  /* 0x023C */
    int16_t           item_item;                /* 0x023E */
    int16_t           map_item;                 /* 0x0240 */
    int16_t           quest_item;               /* 0x0242 */
    int16_t           equip_item;               /* 0x0244 */
    char              unk_0A_[0x0004];          /* 0x0246 */
    int16_t           quest_hilite;             /* 0x024A */
    char              unk_0B_[0x0018];          /* 0x024C */
    int16_t           quest_song;               /* 0x0264 */
    char              unk_0C_[0x0016];          /* 0x0266 */
                                                /* unknown structure */
    char              s27C[0x0038];             /* 0x027C */
                                                /* 0x02B4 */
} z64_pause_ctxt_t;

typedef struct
{
  uint32_t vrom_start;
  uint32_t vrom_end;
} z64_object_table_t;

/* lighting structs */
typedef struct
{
  int8_t  dir[3];
  uint8_t col[3];
} z64_light1_t;

typedef struct
{
  int16_t x;
  int16_t y;
  int16_t z;
  uint8_t col[3];
  int16_t intensity;
} z64_light2_t;

typedef union
{
  z64_light1_t  light1;
  z64_light2_t  light2;
} z64_lightn_t;

typedef struct
{
  uint8_t       type;
  z64_lightn_t  lightn;
} z64_light_t;

typedef struct z64_light_node_s z64_light_node_t;
struct z64_light_node_s
{
  z64_light_t      *light;
  z64_light_node_t *prev;
  z64_light_node_t *next;
};

typedef struct
{
  z64_light_node_t *light_list;
  uint8_t           ambient[3];
  uint8_t           fog[3];
  int16_t           fog_position;
  int16_t           draw_distance;
} z64_lighting_t;

typedef struct
{
  int8_t  numlights;
  Lightsn lites;
} z64_gbi_lights_t;

typedef void (*z64_light_handler_t)(z64_gbi_lights_t*, z64_lightn_t*,
                                    z64_actor_t*);

/* game context */
typedef struct
{
  z64_ctxt_t       common;                 /* 0x00000 */
  uint16_t         scene_index;            /* 0x000A4 */
  char             unk_00_[0x001A];        /* 0x000A6 */
  uint32_t         screen_top;             /* 0x000C0 */
  uint32_t         screen_bottom;          /* 0x000C4 */
  uint32_t         screen_left;            /* 0x000C8 */
  uint32_t         screen_right;           /* 0x000CC */
  float            camera_distance;        /* 0x000D0 */
  float            fog_distance;           /* 0x000D4 */
  float            z_distance;             /* 0x000D8 */
  float            unk_01_;                /* 0x000DC */
  char             unk_02_[0x0190];        /* 0x000E0 */
  z64_actor_t     *camera_focus;           /* 0x00270 */
  char             unk_03_[0x00AE];        /* 0x00274 */
  uint16_t         camera_mode;            /* 0x00322 */
  char             unk_04_[0x001A];        /* 0x00324 */
  uint16_t         camera_flag_1;          /* 0x0033E */
  char             unk_05_[0x016C];        /* 0x00340 */
  int16_t          event_flag;             /* 0x004AC */
  char             unk_06_[0x02E6];        /* 0x004AE */
  uint32_t         camera_2;               /* 0x00794 */
  char             unk_07_[0x0010];        /* 0x00798 */
  z64_lighting_t   lighting;               /* 0x007A8 */
  char             unk_08_[0x0008];        /* 0x007B8 */
  z64_col_hdr_t   *col_hdr;                /* 0x007C0 */
  char             unk_09_[0x1460];        /* 0x007C4 */
  char             actor_ctxt[0x0008];     /* 0x01C24 */
  uint8_t          n_actors_loaded;        /* 0x01C2C */
  char             unk_0A_[0x0003];        /* 0x01C2D */
  struct
  {
    uint32_t       length;
    z64_actor_t   *first;
  }                actor_list[12];         /* 0x01C30 */
  char             unk_0B_[0x0038];        /* 0x01C90 */
  z64_actor_t     *arrow_actor;            /* 0x01CC8 */
  z64_actor_t     *target_actor;           /* 0x01CCC */
  char             unk_0C_1_[0x000A];      /* 0x01CD0 */
  uint8_t          target_actor_type;      /* 0x01CDA */
  char             unk_0C_2_[0x0005];      /* 0x01CDB */
  struct
  {
    z64_xyzf_t     pos;
    float          unk;
    colorRGB8_t    color;
  }                target_arr[3];          /* 0x01CE0 */
  char             unk_0C_3_[0x000C];      /* 0x01D1C */
  uint32_t         swch_flags;             /* 0x01D28 */
  uint32_t         temp_swch_flags;        /* 0x01D2C */
  uint32_t         unk_flags_0;            /* 0x01D30 */
  uint32_t         unk_flags_1;            /* 0x01D34 */
  uint32_t         chest_flags;            /* 0x01D38 */
  uint32_t         clear_flags;            /* 0x01D3C */
  uint32_t         temp_clear_flags;       /* 0x01D40 */
  uint32_t         collect_flags;          /* 0x01D44 */
  uint32_t         temp_collect_flags;     /* 0x01D48 */
  void            *title_card_texture;     /* 0x01D4C */
  char             unk_0D_[0x0007];        /* 0x01D50 */
  uint8_t          title_card_delay;       /* 0x01D57 */
  char             unk_0E_[0x0010];        /* 0x01D58 */
  void            *cutscene_ptr;           /* 0x01D68 */
  int8_t           cutscene_state;         /* 0x01D6C */
  char             unk_0F_[0xE66F];        /* 0x01D6D */
  uint8_t          textbox_state_1;        /* 0x103DC */
  char             unk_10_[0x00DF];        /* 0x103DD */
  uint8_t          textbox_state_2;        /* 0x104BC */
  char             unk_11_[0x0002];        /* 0x104BD */
  uint8_t          textbox_state_3;        /* 0x104BF */
  char             unk_12_[0x0272];        /* 0x104C0 */
  struct {
    uint16_t       unk_00_;
    uint16_t       fadeout;
    uint16_t       a_button_carots;
    uint16_t       b_button;
    uint16_t       cl_button;
    uint16_t       cd_button;
    uint16_t       cr_button;
    uint16_t       hearts_navi;
    uint16_t       rupees_keys_magic;
    uint16_t       minimap;
  }                hud_alpha_channels;    /* 0x10732 */
  char             unk_13_[0x000C];       /* 0x10746 */
  struct
  {
    uint8_t        unk_00_;
    uint8_t        b_button;
    uint8_t        unk_01_;
    uint8_t        bottles;
    uint8_t        trade_items;
    uint8_t        hookshot;
    uint8_t        ocarina;
    uint8_t        warp_songs;
    uint8_t        suns_song;
    uint8_t        farores_wind;
    uint8_t        dfnl;
    uint8_t        all;
  }                restriction_flags;      /* 0x10752 */
  char             unk_14_[0x0002];        /* 0x1075E */
  z64_pause_ctxt_t pause_ctxt;             /* 0x10760 */
  char             unk_15_[0x0D90];        /* 0x10A14 */
  z64_obj_ctxt_t   obj_ctxt;               /* 0x117A4 */
  int8_t           room_index;             /* 0x11CBC */
  char             unk_16_[0x000B];        /* 0x11CBD */
  void            *room_ptr;               /* 0x11CC8 */
  char             unk_17_[0x0118];        /* 0x11CCC */
  uint32_t         gameplay_frames;        /* 0x11DE4 */
  uint8_t          link_age;               /* 0x11DE8 */
  char             unk_18_;                /* 0x11DE9 */
  uint8_t          spawn_index;            /* 0x11DEA */
  uint8_t          n_map_actors;           /* 0x11DEB */
  uint8_t          n_rooms;                /* 0x11DEC */
  char             unk_19_[0x000B];        /* 0x11DED */
  void            *map_actor_list;         /* 0x11DF8 */
  char             unk_20_[0x0008];        /* 0x11DFC */
  void            *scene_exit_list;        /* 0x11E04 */
  char             unk_21_[0x000C];        /* 0x11E08 */
  uint8_t          skybox_type;            /* 0x11E14 */
  int8_t           scene_load_flag;        /* 0x11E15 */
  char             unk_22_[0x0004];        /* 0x11E16 */
  int16_t          entrance_index;         /* 0x11E1A */
  char             unk_23_[0x0042];        /* 0x11E1C */
  uint8_t          fadeout_transition;     /* 0x11E5E */
                                           /* 0x11E5F */
} z64_game_t;

typedef struct
{
  char              unk_00_[0x01D8];          /* 0x00000 */
  z64_sram_data_t  *sram_buffer;              /* 0x001D8 */
  char              unk_01_[0x1C812];         /* 0x001DC */
  uint16_t          deaths[3];                /* 0x1C9EE */
  uint8_t           name[3][8];               /* 0x1C9F4 */
  uint16_t          hearts[3];                /* 0x1CA0C */
  uint32_t          quest_items[3];           /* 0x1CA14 */
  uint16_t          disk_drive[3];            /* 0x1CA20 */
  uint8_t           double_defense[3];        /* 0x1CA26 */
  char              unk_02_[0x0001];          /* 0x1CA29 */
  uint16_t          selected_item;            /* 0x1CA2A */
  uint16_t          selected_sub_item;        /* 0x1CA2C */
  uint16_t          menu_depth;               /* 0x1CA2E */
  uint16_t          alt_transition;           /* 0x1CA30 */
  char              unk_03_[0x0004];          /* 0x1CA32 */
  uint16_t          menu_transition;          /* 0x1CA36 */
  uint16_t          selected_file;            /* 0x1CA38 */
  char              unk_04_[0x0008];          /* 0x1CA3A */
  uint16_t          transition_frame;         /* 0x1CA42 */
  struct {
    int16_t         file[3];                  /* 0x1CA44 */
    int16_t         yes;                      /* 0x1CA4A */
    int16_t         quit;                     /* 0x1CA4C */
    int16_t         options;                  /* 0x1CA4E */
  }                 button_offsets;
  int16_t           unk_05_;                  /* 0x1CA50 */
  int16_t           file_message;             /* 0x1CA52 */
  int16_t           unk_06_;                  /* 0x1CA54 */
  int16_t           message_id[2];            /* 0x1CA56 */
  colorRGB16_t      panel_color;              /* 0x1CA5A */
  struct {
    uint16_t        message[2];               /* 0x1CA60 */
    uint16_t        panel;                    /* 0x1CA64 */
    uint16_t        file[3];                  /* 0x1CA66 */
    uint16_t        tag[3];                   /* 0x1CA6C */
    uint16_t        name_text[3];             /* 0x1CA72 */
    uint16_t        link[3];                  /* 0x1CA78 */
    uint16_t        file_details[3];          /* 0x1CA7E */
    uint16_t        copy_button;              /* 0x1CA84 */
    uint16_t        erase_button;             /* 0x1CA86 */
    uint16_t        yes_button;               /* 0x1CA88 */
    uint16_t        quit_button;              /* 0x1CA8A */
    uint16_t        options_button;           /* 0x1CA8C */
    uint16_t        unk_00_;                  /* 0x1CA8E */
    uint16_t        input_button_text;        /* 0x1CA90 */
    uint16_t        unk_01_;                  /* 0x1CA92 */
  } alpha_levels;
  colorRGB16_t      cursor_color;             /* 0x1CA94 */
} z64_menudata_t;

typedef struct
{
  void             *ptr;                      /* 0x0000 */
  uint32_t          vrom_start;               /* 0x0004 */
  uint32_t          vrom_end;                 /* 0x0008 */
  uint32_t          vram_start;               /* 0x000C */
  uint32_t          vram_end;                 /* 0x0010 */
  char              unk_00_[0x0004];          /* 0x0014 */
  uint32_t          vram_ctor;                /* 0x0018 */
  uint32_t          vram_dtor;                /* 0x001C */
  char              unk_01_[0x000C];          /* 0x0020 */
  char              ctxt_size;                /* 0x002C */
                                              /* 0x0030 */
} z64_state_ovl_t;

typedef struct
{
  /* state ? */
  int32_t           state;                    /* 0x0000 */
  /* elapsed time */
  int32_t           time;                     /* 0x0004 */
  /* point 1 */
  int16_t           p1x;                      /* 0x0008 */
  int16_t           p1y;                      /* 0x000A */
  int16_t           p1z;                      /* 0x000C */
  /* point 2 */
  int16_t           p2x;                      /* 0x000E */
  int16_t           p2y;                      /* 0x0010 */
  int16_t           p2z;                      /* 0x0012 */
  /* flags ? */
  uint16_t          flags;                    /* 0x0014 */
  char              pad_00_[0x0002];          /* 0x0016 */
                                              /* 0x0018 */
} z64_trail_cp_t;

typedef struct
{
  /* control points */
  z64_trail_cp_t    cp[16];                   /* 0x0000 */
  /* interpolation mode ? */
  uint32_t          ipn_mode;                 /* 0x0180 */
  /* parameter for interpolation mode 4 */
  float             f184;                     /* 0x0184 */
  /* flags ? */
  uint16_t          h188;                     /* 0x0188 */
  /* counter increment, counter, what for ? */
  int16_t           h18A;                     /* 0x018A */
  int16_t           h18C;                     /* 0x018C */
  /* point 1 starting color */
  colorRGBA8_t      p1_start;                 /* 0x018E */
  /* point 2 starting color */
  colorRGBA8_t      p2_start;                 /* 0x0192 */
  /* point 1 ending color */
 colorRGBA8_t       p1_end;                   /* 0x0196 */
  /* point 2 ending color */
  colorRGBA8_t      p2_end;                   /* 0x019A */
  /* number of active control points */
  uint8_t           n_cp;                     /* 0x019E */
  /* control point duration */
  uint8_t           duration;                 /* 0x019F */
  /* unknown */
  uint8_t           b1A0;                     /* 0x01A0 */
  /* render mode */
  /* 0:   simple */
  /* 1:   simple with alternate colors */
  /* 2+:  smooth */
  uint8_t           mode;                     /* 0x01A1 */
  /* alternate colors */
  /* inner color */
  uint8_t           m1r1;                     /* 0x01A2 */
  uint8_t           m1g1;                     /* 0x01A3 */
  uint8_t           m1b1;                     /* 0x01A4 */
  uint8_t           m1a1;                     /* 0x01A5 */
  /* outer color */
  uint8_t           m1r2;                     /* 0x01A6 */
  uint8_t           m1g2;                     /* 0x01A7 */
  uint8_t           m1b2;                     /* 0x01A8 */
  uint8_t           m1a2;                     /* 0x01A9 */
                                              /* 0x01AC */
} z64_trail_fx_t;

typedef struct
{
  uint8_t           active;                   /* 0x0000 */
  char              pad_00_[0x0003];          /* 0x0001 */
  z64_trail_fx_t    fx;                       /* 0x0004 */
                                              /* 0x01B0 */
} z64_trail_t;

struct EnItem00;

typedef void(*EnItem00ActionFunc)(struct EnItem00*, z64_game_t*);

typedef struct EnItem00 {
	z64_actor_t actor;
	EnItem00ActionFunc actionFunc;
	uint16_t collectibleFlag;
	uint16_t getItemId;
	uint16_t unk_154;
	uint16_t unk_156;
	uint16_t unk_158;
	uint16_t timeToLive; //0x15A
	float scale;
} EnItem00;

/* dram addresses */
#define z64_osSendMesg_addr                     0x80001E20
#define z64_osRecvMesg_addr                     0x80002030
#define z64_osCreateMesgQueue_addr              0x80004220
#define z64_file_mq_addr                        0x80007D40
#define z64_vi_counter_addr                     0x80009E8C
#define z64_DrawActors_addr                     0x80024AB4
#define z64_DeleteActor_addr                    0x80024FE0
#define z64_SpawnActor_addr                     0x80025110
#define z64_minimap_disable_1_addr              0x8006CD50
#define z64_minimap_disable_2_addr              0x8006D4E4
#define z64_SwitchAgeEquips_addr                0x8006F804
#define z64_UpdateItemButton_addr               0x8006FB50
#define z64_GiveItem_addr                       0x8006FDCC
#define z64_UpdateEquipment_addr                0x80079764
#define z64_LoadRoom_addr                       0x80080A3C
#define z64_UnloadRoom_addr                     0x80080C98
#define z64_Io_addr                             0x80091474
#define z64_entrance_offset_hook_addr           0x8009AA44
#define z64_frame_update_func_addr              0x8009AF1C
#define z64_frame_update_call_addr              0x8009CAE8
#define z64_disp_swap_1_addr                    0x800A1198
#define z64_disp_swap_2_addr                    0x800A11B0
#define z64_disp_swap_3_addr                    0x800A11C8
#define z64_disp_swap_4_addr                    0x800A11E4
#define z64_frame_input_func_addr               0x800A0BA0
#define z64_main_hook_addr                      0x800A0C3C
#define z64_frame_input_call_addr               0x800A16AC
#define z64_GetMatrixStackTop_addr              0x800AA78C
#define z64_DisplayTextbox_addr                 0x800DCE14
#define gspF3DEX2_NoN_fifoTextStart             0x800E3F70
#define z64_fog_state_addr                      0x800F1640
#define z64_day_speed_addr                      0x800F1650
#define z64_light_handlers_addr                 0x800F1B40
#define z64_object_table_addr                   0x800F8FF8
#define z64_entrance_table_addr                 0x800F9C90
#define z64_scene_table_addr                    0x800FB4E0
#define z64_scene_config_table_addr             0x800FBD18
#define z64_seq_pos_addr                        0x801043B0
#define gspF3DEX2_NoN_fifoDataStart             0x801145C0
#define z64_file_addr                           0x8011A5D0
#define z64_input_direct_addr                   0x8011D730
#define z64_stab_addr                           0x80120C38
#define z64_seq_buf_addr                        0x80124800
#define z64_ctxt_addr                           0x801C84A0
#define z64_link_addr                           0x801DAA30
#define z64_state_ovl_tab_addr                  0x800F1340
#define z64_event_state_1_addr                  0x800EF1B0
#define z64_LinkInvincibility_addr              0x8038E578
#define z64_LinkDamage_addr                     0x8038E6A8
#define z64_ObjectSpawn_addr                    0x800812F0
#define z64_ObjectIndex_addr                    0x80081628
#define z64_ActorSetLinkIncomingItemId_addr     0x80022CF4

/* rom addresses */
#define z64_icon_item_static_vaddr              0x007BD000
#define z64_icon_item_static_vsize              0x000888A0
#define z64_icon_item_24_static_vaddr           0x00846000
#define z64_icon_item_24_static_vsize           0x0000B400
#define z64_nes_font_static_vaddr               0x00928000
#define z64_nes_font_static_vsize               0x00004580
#define z64_file_select_static_vaddr            0x01A02000
#define z64_file_select_static_vsize            0x000395C0
#define z64_parameter_static_vaddr              0x01A3C000
#define z64_parameter_static_vsize              0x00003B00
#define z64_icon_item_dungeon_static_vaddr      0x0085E000
#define z64_icon_item_dungeon_static_vsize      0x00001D80


/* context info */
#define z64_ctxt_filemenu_ctor                  0x80812394
#define z64_ctxt_filemenu_size                  0x0001CAD0
#define z64_ctxt_game_ctor                      0x8009A750
#define z64_ctxt_game_size                      0x00012518

/* function prototypes */
typedef void (*z64_DrawActors_proc)       (z64_game_t *game, void *actor_ctxt);
typedef void (*z64_DeleteActor_proc)      (z64_game_t *game, void *actor_ctxt,
                                           z64_actor_t *actor);
typedef void (*z64_SpawnActor_proc)       (void *actor_ctxt, z64_game_t *game,
                                           int actor_id, float x, float y,
                                           float z, uint16_t rx, uint16_t ry,
                                           uint16_t rz, uint16_t variable);
typedef void (*z64_SwitchAgeEquips_proc)  (void);
typedef void (*z64_UpdateItemButton_proc) (z64_game_t *game, int button_index);
typedef void (*z64_UpdateEquipment_proc)  (z64_game_t *game, z64_link_t *link);
typedef void (*z64_LoadRoom_proc)         (z64_game_t *game,
                                           void *p_ctxt_room_index,
                                           uint8_t room_index);
typedef void (*z64_UnloadRoom_proc)       (z64_game_t *game,
                                           void *p_ctxt_room_index);
typedef void (*z64_Io_proc)               (uint32_t dev_addr, void *dram_addr,
                                           uint32_t size, int32_t direction);
typedef void (*z64_SceneConfig_proc)      (z64_game_t *game);
typedef void (*z64_DisplayTextbox_proc)   (z64_game_t *game, uint16_t text_id,
                                           int unknown_);
typedef void (*z64_GiveItem_proc)         (z64_game_t *game, uint8_t item);

typedef void(*z64_LinkDamage_proc)        (z64_game_t *ctxt, z64_link_t *link,
                                           uint8_t damage_type, float unk_00, uint32_t unk_01,
                                           uint16_t unk_02);
typedef void(*z64_LinkInvincibility_proc) (z64_link_t *link, uint8_t frames);
typedef float *(*z64_GetMatrixStackTop_proc)();

typedef int32_t(*z64_ObjectSpawn_proc)    (z64_obj_ctxt_t *object_ctx, int16_t object_id);
typedef int32_t(*z64_ObjectIndex_proc)    (z64_obj_ctxt_t *object_ctx, int16_t object_id);

typedef int32_t(*z64_ActorSetLinkIncomingItemId_proc) (z64_actor_t *actor, z64_game_t *game,
                                                       int32_t get_item_id, float xz_range, float y_range);

/* data */
#define z64_file_mq             (*(OSMesgQueue*)      z64_file_mq_addr)
#define z64_vi_counter          (*(uint32_t*)         z64_vi_counter_addr)
#define z64_stab                (*(z64_stab_t*)       z64_stab_addr)
#define z64_scene_table         ( (z64_scene_table_t*)z64_scene_table_addr)
#define z64_fog_state           (*(uint8_t*)          z64_fog_state_addr)
#define z64_day_speed           (*(uint16_t*)         z64_day_speed_addr)
#define z64_light_handlers      ( (z64_light_handler_t*)                      \
                                                      z64_light_handlers_addr)
#define z64_object_table        ( (z64_object_table_t*)                      \
                                                      z64_object_table_addr)
#define z64_entrance_table      ( (z64_entrance_table_t*)                     \
                                   z64_entrance_table_addr)
#define z64_scene_config_table  ( (z64_SceneConfig_proc*)                     \
                                   z64_scene_config_table_addr)
#define z64_file                (*(z64_file_t*)       z64_file_addr)
#define z64_input_direct        (*(z64_input_t*)      z64_input_direct_addr)
#define z64_gameinfo            (*                    z64_file.gameinfo)
#define z64_ctxt                (*(z64_ctxt_t*)       z64_ctxt_addr)
#define z64_game                (*(z64_game_t*)      &z64_ctxt)
#define z64_link                (*(z64_link_t*)       z64_link_addr)
#define z64_state_ovl_tab       (*(z64_state_ovl_t(*)[6])                     \
                                                      z64_state_ovl_tab_addr)
#define z64_event_state_1       (*(uint32_t*)         z64_event_state_1_addr)


/* functions */
#define z64_osSendMesg          ((osSendMesg_t)       z64_osSendMesg_addr)
#define z64_osRecvMesg          ((osRecvMesg_t)       z64_osRecvMesg_addr)
#define z64_osCreateMesgQueue   ((osCreateMesgQueue_t)                        \
                                 z64_osCreateMesgQueue_addr)
#define z64_DrawActors          ((z64_DrawActors_proc)z64_DrawActors_addr)
#define z64_DeleteActor         ((z64_DeleteActor_proc)                       \
                                 z64_DeleteActor_addr)
#define z64_SpawnActor          ((z64_SpawnActor_proc)z64_SpawnActor_addr)
#define z64_SwitchAgeEquips     ((z64_SwitchAgeEquips_proc)                   \
                                                      z64_SwitchAgeEquips_addr)
#define z64_UpdateItemButton    ((z64_UpdateItemButton_proc)                  \
                                                      z64_UpdateItemButton_addr)
#define z64_UpdateEquipment     ((z64_UpdateEquipment_proc)                   \
                                                      z64_UpdateEquipment_addr)
#define z64_LoadRoom            ((z64_LoadRoom_proc)  z64_LoadRoom_addr)
#define z64_UnloadRoom          ((z64_UnloadRoom_proc)                        \
                                                      z64_UnloadRoom_addr)
#define z64_Io                  ((z64_Io_proc)        z64_Io_addr)
#define z64_DisplayTextbox      ((z64_DisplayTextbox_proc)                    \
                                                      z64_DisplayTextbox_addr)
#define z64_GiveItem            ((z64_GiveItem_proc)  z64_GiveItem_addr)

#define z64_LinkDamage          ((z64_LinkDamage_proc)z64_LinkDamage_addr)
#define z64_LinkInvincibility   ((z64_LinkInvincibility_proc)                 \
                                                      z64_LinkInvincibility_addr)
#define z64_GetMatrixStackTop   ((z64_GetMatrixStackTop_proc) \
                                                      z64_GetMatrixStackTop_addr)

#define z64_ObjectSpawn         ((z64_ObjectSpawn_proc)z64_ObjectSpawn_addr)
#define z64_ObjectIndex         ((z64_ObjectIndex_proc)z64_ObjectIndex_addr)

#define z64_ActorSetLinkIncomingItemId ((z64_ActorSetLinkIncomingItemId_proc)z64_ActorSetLinkIncomingItemId_addr)

#endif
