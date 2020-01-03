from version import __version__
import random
import Music as music
import Sounds as sfx
import IconManip as icon

from collections import namedtuple
Color = namedtuple('Color', '  R     G     B')

tunic_colors = {
    "Kokiri Green":      Color(0x1E, 0x69, 0x1B),
    "Goron Red":         Color(0x64, 0x14, 0x00),
    "Zora Blue":         Color(0x00, 0x3C, 0x64),
    "Black":             Color(0x30, 0x30, 0x30),
    "White":             Color(0xF0, 0xF0, 0xFF),
    "Azure Blue":        Color(0x13, 0x9E, 0xD8),
    "Vivid Cyan":        Color(0x13, 0xE9, 0xD8),
    "Light Red":         Color(0xF8, 0x7C, 0x6D),
    "Fuchsia":           Color(0xFF, 0x00, 0xFF),
    "Purple":            Color(0x95, 0x30, 0x80),
    "Majora Purple":     Color(0x40, 0x00, 0x40),
    "Twitch Purple":     Color(0x64, 0x41, 0xA5),
    "Purple Heart":      Color(0x8A, 0x2B, 0xE2),
    "Persian Rose":      Color(0xFF, 0x14, 0x93),
    "Dirty Yellow":      Color(0xE0, 0xD8, 0x60),
    "Blush Pink":        Color(0xF8, 0x6C, 0xF8),
    "Hot Pink":          Color(0xFF, 0x69, 0xB4),
    "Rose Pink":         Color(0xFF, 0x90, 0xB3),
    "Orange":            Color(0xE0, 0x79, 0x40),
    "Gray":              Color(0xA0, 0xA0, 0xB0),
    "Gold":              Color(0xD8, 0xB0, 0x60),
    "Silver":            Color(0xD0, 0xF0, 0xFF),
    "Beige":             Color(0xC0, 0xA0, 0xA0),
    "Teal":              Color(0x30, 0xD0, 0xB0),
    "Blood Red":         Color(0x83, 0x03, 0x03),
    "Blood Orange":      Color(0xFE, 0x4B, 0x03),
    "Royal Blue":        Color(0x40, 0x00, 0x90),
    "Sonic Blue":        Color(0x50, 0x90, 0xE0),
    "NES Green":         Color(0x00, 0xD0, 0x00),
    "Dark Green":        Color(0x00, 0x25, 0x18),
    "Lumen":             Color(0x50, 0x8C, 0xF0),
}


NaviColors = {          # Inner Core Color         Outer Glow Color
    "Gold":              (Color(0xFE, 0xCC, 0x3C), Color(0xFE, 0xC0, 0x07)),
    "White":             (Color(0xFF, 0xFF, 0xFF), Color(0x00, 0x00, 0xFF)),
    "Green":             (Color(0x00, 0xFF, 0x00), Color(0x00, 0xFF, 0x00)),
    "Light Blue":        (Color(0x96, 0x96, 0xFF), Color(0x96, 0x96, 0xFF)),
    "Yellow":            (Color(0xFF, 0xFF, 0x00), Color(0xC8, 0x9B, 0x00)),
    "Red":               (Color(0xFF, 0x00, 0x00), Color(0xFF, 0x00, 0x00)),
    "Magenta":           (Color(0xFF, 0x00, 0xFF), Color(0xC8, 0x00, 0x9B)),
    "Black":             (Color(0x00, 0x00, 0x00), Color(0x00, 0x00, 0x00)),
    "Tatl":              (Color(0xFF, 0xFF, 0xFF), Color(0xC8, 0x98, 0x00)),
    "Tael":              (Color(0x49, 0x14, 0x6C), Color(0xFF, 0x00, 0x00)),
    "Fi":                (Color(0x2C, 0x9E, 0xC4), Color(0x2C, 0x19, 0x83)),
    "Ciela":             (Color(0xE6, 0xDE, 0x83), Color(0xC6, 0xBE, 0x5B)),
    "Epona":             (Color(0xD1, 0x49, 0x02), Color(0x55, 0x1F, 0x08)),
    "Ezlo":              (Color(0x62, 0x9C, 0x5F), Color(0x3F, 0x5D, 0x37)),
    "King of Red Lions": (Color(0xA8, 0x33, 0x17), Color(0xDE, 0xD7, 0xC5)),
    "Linebeck":          (Color(0x03, 0x26, 0x60), Color(0xEF, 0xFF, 0xFF)),
    "Loftwing":          (Color(0xD6, 0x2E, 0x31), Color(0xFD, 0xE6, 0xCC)),
    "Midna":             (Color(0x19, 0x24, 0x26), Color(0xD2, 0x83, 0x30)),
    "Phantom Zelda":     (Color(0x97, 0x7A, 0x6C), Color(0x6F, 0x46, 0x67)),
}

sword_colors = {        # Initial Color            Fade Color
    "Rainbow":           (Color(0x00, 0x00, 0x00), Color(0x00, 0x00, 0x00)),
    "White":             (Color(0xFF, 0xFF, 0xFF), Color(0xFF, 0xFF, 0xFF)),
    "Red":               (Color(0xFF, 0x00, 0x00), Color(0xFF, 0x00, 0x00)),
    "Green":             (Color(0x00, 0xFF, 0x00), Color(0x00, 0xFF, 0x00)),
    "Blue":              (Color(0x00, 0x00, 0xFF), Color(0x00, 0x00, 0xFF)),
    "Cyan":              (Color(0x00, 0xFF, 0xFF), Color(0x00, 0xFF, 0xFF)),
    "Magenta":           (Color(0xFF, 0x00, 0xFF), Color(0xFF, 0x00, 0xFF)),
    "Orange":            (Color(0xFF, 0xA5, 0x00), Color(0xFF, 0xA5, 0x00)),
    "Gold":              (Color(0xFF, 0xD7, 0x00), Color(0xFF, 0xD7, 0x00)),
    "Purple":            (Color(0x80, 0x00, 0x80), Color(0x80, 0x00, 0x80)),
    "Pink":              (Color(0xFF, 0x69, 0xB4), Color(0xFF, 0x69, 0xB4)),
}

gauntlet_colors = {
    "Silver":            Color(0xFF, 0xFF, 0xFF),
    "Gold":              Color(0xFE, 0xCF, 0x0F),
    "Black":             Color(0x00, 0x00, 0x06),
    "Green":             Color(0x02, 0x59, 0x18),
    "Blue":              Color(0x06, 0x02, 0x5A),
    "Bronze":            Color(0x60, 0x06, 0x02),
    "Red":               Color(0xFF, 0x00, 0x00),
    "Sky Blue":          Color(0x02, 0x5D, 0xB0),
    "Pink":              Color(0xFA, 0x6A, 0x90),
    "Magenta":           Color(0xFF, 0x00, 0xFF),
    "Orange":            Color(0xDA, 0x38, 0x00),
    "Lime":              Color(0x5B, 0xA8, 0x06),
    "Purple":            Color(0x80, 0x00, 0x80),
}

heart_colors = {
    "Red":          Color(0xFF, 0x46, 0x32),
    "Green":        Color(0x46, 0xC8, 0x32),
    "Blue":         Color(0x32, 0x46, 0xFF),
    "Yellow":       Color(0xFF, 0xE0, 0x00),
}

magic_colors = {
    "Green":             Color(0x00, 0xC8, 0x00),
    "Red":               Color(0xC8, 0x00, 0x00),
    "Blue":              Color(0x00, 0x30, 0xFF),
    "Purple":            Color(0xB0, 0x00, 0xFF),
    "Pink":              Color(0xFF, 0x00, 0xC8),
    "Yellow":            Color(0xFF, 0xFF, 0x00),
    "White":             Color(0xFF, 0xFF, 0xFF),
}


meta_color_choices = ["Random Choice", "Completely Random", "Custom Color"]


def get_tunic_colors():
    return list(tunic_colors.keys())


def get_tunic_color_options():
    return meta_color_choices + get_tunic_colors()


def get_navi_colors():
    return list(NaviColors.keys())


def get_navi_color_options(outer=False):
    if outer:
        return ["[Same as Inner]"] + meta_color_choices + get_navi_colors()
    else:
        return meta_color_choices + get_navi_colors()

    
def get_sword_colors():
    return list(sword_colors.keys())


def get_sword_color_options():
    return meta_color_choices + get_sword_colors()


def get_gauntlet_colors():
    return list(gauntlet_colors.keys())


def get_gauntlet_color_options():
    return meta_color_choices + get_gauntlet_colors()


def get_heart_colors():
    return list(heart_colors.keys())


def get_heart_color_options():
    return meta_color_choices + get_heart_colors()


def get_magic_colors():
    return list(magic_colors.keys())


def get_magic_color_options():
    return meta_color_choices + get_magic_colors()


def patch_targeting(rom, settings, log, symbols):
    # Set default targeting option to Hold
    if settings.default_targeting == 'hold':
        rom.write_byte(0xB71E6D, 0x01)
    else:
        rom.write_byte(0xB71E6D, 0x00)


def patch_dpad(rom, settings, log, symbols):
    # Display D-Pad HUD
    if settings.display_dpad:
        rom.write_byte(symbols['CFG_DISPLAY_DPAD'], 0x01)
    else:
        rom.write_byte(symbols['CFG_DISPLAY_DPAD'], 0x00)
    log.display_dpad = settings.display_dpad



def patch_music(rom, settings, log, symbols):
    # patch music
    if settings.background_music != 'normal' or settings.fanfares != 'normal':
        music.restore_music(rom)
        log.bgm = music.randomize_music(rom, settings)
    else:
        music.restore_music(rom)


def patch_tunic_icon(rom, tunic, color):
    # patch tunic icon colors
    icon_locations = {
        'Kokiri Tunic': 0x007FE000,
        'Goron Tunic': 0x007FF000,
        'Zora Tunic': 0x00800000,
    }

    tunic_icon = icon.generate_tunic_icon(color)

    rom.write_bytes(icon_locations[tunic], tunic_icon)


def patch_tunic_colors(rom, settings, log, symbols):
    # patch tunic colors
    tunics = [
        ('Kokiri Tunic', settings.kokiri_color, 0x00B6DA38),
        ('Goron Tunic',  settings.goron_color,  0x00B6DA3B),
        ('Zora Tunic',   settings.zora_color,   0x00B6DA3E),
    ]
    tunic_color_list = get_tunic_colors()

    for tunic, tunic_option, address in tunics:
        # handle random
        if tunic_option == 'Random Choice':
            tunic_option = random.choice(tunic_color_list)
        # handle completely random
        if tunic_option == 'Completely Random':
            color = [random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)]
        # grab the color from the list
        elif tunic_option in tunic_colors:
            color = list(tunic_colors[tunic_option])
        # build color from hex code
        else:
            color = list(int(tunic_option[i:i+2], 16) for i in (0, 2 ,4))
            tunic_option = 'Custom'
        rom.write_bytes(address, color)

        # patch the tunic icon
        if [tunic, tunic_option] not in [['Kokiri Tunic', 'Kokiri Green'], ['Goron Tunic', 'Goron Red'], ['Zora Tunic', 'Zora Blue']]:
            patch_tunic_icon(rom, tunic, color)

        log.tunic_colors[tunic] = dict(option=tunic_option, color=''.join(['{:02X}'.format(c) for c in color]))


def patch_navi_colors(rom, settings, log, symbols):
    # patch navi colors
    navi = [
        # colors for Navi
        ('Navi Idle',            settings.navi_color_default_inner, settings.navi_color_default_outer,
            [0x00B5E184]), # Default
        ('Navi Targeting Enemy', settings.navi_color_enemy_inner,   settings.navi_color_enemy_outer,
            [0x00B5E19C, 0x00B5E1BC]), # Enemy, Boss
        ('Navi Targeting NPC',   settings.navi_color_npc_inner,     settings.navi_color_npc_outer,
            [0x00B5E194]), # NPC
        ('Navi Targeting Prop',  settings.navi_color_prop_inner,    settings.navi_color_prop_outer,
            [0x00B5E174, 0x00B5E17C, 0x00B5E18C,
            0x00B5E1A4, 0x00B5E1AC, 0x00B5E1B4,
            0x00B5E1C4, 0x00B5E1CC, 0x00B5E1D4]), # Everything else
    ]
    navi_color_list = get_navi_colors()
    for navi_action, navi_option_inner, navi_option_outer, navi_addresses in navi:

        # choose a random choice for the whole group
        if navi_option_inner == 'Random Choice':
            navi_option_inner = random.choice(navi_color_list)
        if navi_option_outer == 'Random Choice':
            navi_option_outer = random.choice(navi_color_list)

        if navi_option_outer == '[Same as Inner]':
            navi_option_outer = navi_option_inner

        inner_color = None
        outer_color = None
        colors = []
        for address in navi_addresses:
            # completely random is random for every subgroup
            if navi_option_inner == 'Completely Random':
                inner_color = [random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)]
            if navi_option_outer == 'Completely Random':
                outer_color = [random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)]

            # grab the color from the list
            if navi_option_inner in NaviColors:
                inner_color = list(NaviColors[navi_option_inner][0])
            if navi_option_outer in NaviColors:
                outer_color = list(NaviColors[navi_option_outer][1])

            # build color from hex code
            if inner_color is None:
                inner_color = list(int(navi_option_inner[i:i+2], 16) for i in (0, 2, 4))
                navi_option_inner = 'Custom'
            if outer_color is None:
                outer_color = list(int(navi_option_outer[i:i+2], 16) for i in (0, 2, 4))
                navi_option_outer = 'Custom'

            # Check color validity
            if inner_color is None:
                raise Exception(f'Invalid inner color {navi_option_inner} for {navi_action}')
            if outer_color is None:
                raise Exception(f'Invalid outer color {navi_option_outer} for {navi_action}')

            # make color set a list for the log if they are completely random (different per address)
            if navi_option_inner == 'Completely Random' or navi_option_outer == 'Completely Random':
                colors.append((inner_color, outer_color))
            else:
                colors = [(inner_color, outer_color)]

            # write color
            color = inner_color + [0xFF] + outer_color + [0xFF]
            rom.write_bytes(address, color)

        log.navi_colors[navi_action] = [dict(
            option1=navi_option_inner, color1=''.join(['{:02X}'.format(c) for c in inner_c]), 
            option2=navi_option_outer, color2=''.join(['{:02X}'.format(c) for c in outer_c]))
            for (inner_c, outer_c) in colors]


def patch_sword_trails(rom, settings, log, symbols):
    # patch sword trail colors
    sword_trails = [
        ('Inner Initial Sword Trail', settings.sword_trail_color_inner, 
            [(0x00BEFF80, 0xB0, 0x40), (0x00BEFF88, 0x20, 0x00)], symbols['CFG_RAINBOW_SWORD_INNER_ENABLED']),
        ('Outer Initial Sword Trail', settings.sword_trail_color_outer, 
            [(0x00BEFF7C, 0xB0, 0xFF), (0x00BEFF84, 0x10, 0x00)], symbols['CFG_RAINBOW_SWORD_OUTER_ENABLED']),
    ]

    sword_color_list = get_sword_colors()

    for index, item in enumerate(sword_trails):
        sword_trail_name, sword_trail_option, sword_trail_addresses, sword_trail_rainbow_symbol = item

        # handle random
        if sword_trail_option == 'Random Choice':
            sword_trail_option = random.choice(sword_color_list)

        custom_color = False
        for index, (address, transparency, white_transparency) in enumerate(sword_trail_addresses):
            # set rainbow option
            if sword_trail_option == 'Rainbow':
                rom.write_byte(sword_trail_rainbow_symbol, 0x01)
                color = [0x00, 0x00, 0x00]
                continue
            else:
                rom.write_byte(sword_trail_rainbow_symbol, 0x00)

            # handle completely random
            if sword_trail_option == 'Completely Random':
                color = [random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)]
                if sword_trail_name not in log.sword_colors:
                    log.sword_colors[sword_trail_name] = list()
                log.sword_colors[sword_trail_name].append(dict(option=sword_trail_option, color=''.join(['{:02X}'.format(c) for c in color[0:3]])))

            elif sword_trail_option in sword_colors:
                color = list(sword_colors[sword_trail_option][index])
            # build color from hex code
            else:
                color = list(int(sword_trail_option[i:i+2], 16) for i in (0, 2, 4))
                custom_color = True

            if sword_trail_option == 'White':
                color = color + [white_transparency]
            else:
                color = color + [transparency]

            rom.write_bytes(address, color)

        if custom_color:
            sword_trail_option = 'Custom'
        if sword_trail_name not in log.sword_colors:
            log.sword_colors[sword_trail_name] = [dict(option=sword_trail_option, color=''.join(['{:02X}'.format(c) for c in color[0:3]]))]
    log.sword_trail_duration = settings.sword_trail_duration
    rom.write_byte(0x00BEFF8C, settings.sword_trail_duration)


def patch_gauntlet_colors(rom, settings, log, symbols):
    # patch gauntlet colors
    gauntlets = [
        ('Silver Gauntlets', settings.silver_gauntlets_color, 0x00B6DA44),
        ('Gold Gauntlets', settings.golden_gauntlets_color,  0x00B6DA47),
    ]
    gauntlet_color_list = get_gauntlet_colors()

    for gauntlet, gauntlet_option, address in gauntlets:
        # handle random
        if gauntlet_option == 'Random Choice':
            gauntlet_option = random.choice(gauntlet_color_list)
        # handle completely random
        if gauntlet_option == 'Completely Random':
            color = [random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)]
        # grab the color from the list
        elif gauntlet_option in gauntlet_colors:
            color = list(gauntlet_colors[gauntlet_option])
        # build color from hex code
        else:
            color = list(int(gauntlet_option[i:i+2], 16) for i in (0, 2 ,4))
            gauntlet_option = 'Custom'
        rom.write_bytes(address, color)
        log.gauntlet_colors[gauntlet] = dict(option=gauntlet_option, color=''.join(['{:02X}'.format(c) for c in color]))


def patch_heart_colors(rom, settings, log, symbols):
    # patch tunic colors
    hearts = [
        ('Heart Colors', settings.heart_color, symbols['CFG_HEART_COLOR'], 0xBB0994),
    ]
    heart_color_list = get_heart_colors()

    for heart, heart_option, symbol, file_select_address in hearts:
        # handle random
        if heart_option == 'Random Choice':
            heart_option = random.choice(heart_color_list)
        # handle completely random
        if heart_option == 'Completely Random':
            color = [random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)]
        # grab the color from the list
        elif heart_option in heart_colors:
            color = list(heart_colors[heart_option])
        # build color from hex code
        else:
            color = list(int(heart_option[i:i+2], 16) for i in (0, 2, 4))
            heart_option = 'Custom'
        rom.write_int16s(symbol, color) # symbol for ingame HUD
        rom.write_int16s(file_select_address, color) # file select normal hearts
        if heart_option != 'Red':
            rom.write_int16s(file_select_address + 6, color) # file select DD hearts
        log.heart_colors[heart] = dict(option=heart_option, color=''.join(['{:02X}'.format(c) for c in color]))


def patch_magic_colors(rom, settings, log, symbols):
    magic = [
        ('Magic Meter Color', settings.magic_color, symbols["CFG_MAGIC_COLOR"]),
    ]
    magic_color_list = get_magic_colors()

    for magic_color, magic_option, symbol in magic:
        if magic_option == 'Random Choice':
           magic_option = random.choice(magic_color_list)

        if magic_option == 'Completely Random':
            color = [random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)]
        elif magic_option in magic_colors:
            color = list(magic_colors[magic_option])
        else:
            color = list(int(magic_option[i:i+2], 16) for i in (0, 2, 4))
            magic_option = 'Custom'
        rom.write_int16s(symbol, color)
        log.magic_colors[magic_color] = dict(option=magic_option, color=''.join(['{:02X}'.format(c) for c in color]))


def patch_sfx(rom, settings, log, symbols):
    # Configurable Sound Effects
    sfx_config = [
          (settings.sfx_navi_overworld, sfx.SoundHooks.NAVI_OVERWORLD),
          (settings.sfx_navi_enemy,     sfx.SoundHooks.NAVI_ENEMY),
          (settings.sfx_low_hp,         sfx.SoundHooks.HP_LOW),
          (settings.sfx_menu_cursor,    sfx.SoundHooks.MENU_CURSOR),
          (settings.sfx_menu_select,    sfx.SoundHooks.MENU_SELECT),
          (settings.sfx_nightfall,      sfx.SoundHooks.NIGHTFALL),
          (settings.sfx_horse_neigh,    sfx.SoundHooks.HORSE_NEIGH),
          (settings.sfx_hover_boots,    sfx.SoundHooks.BOOTS_HOVER),
    ]
    sound_dict = sfx.get_patch_dict()

    for selection, hook in sfx_config:
        if selection == 'default':
            for loc in hook.value.locations:
                sound_id = rom.original.read_int16(loc)
                rom.write_int16(loc, sound_id)
        else:
            if selection == 'random-choice':
                selection = random.choice(sfx.get_hook_pool(hook)).value.keyword
            elif selection == 'random-ear-safe':
                selection = random.choice(sfx.get_hook_pool(hook, "TRUE")).value.keyword
            elif selection == 'completely-random':
                selection = random.choice(sfx.standard).value.keyword
            sound_id  = sound_dict[selection]
            for loc in hook.value.locations:
                rom.write_int16(loc, sound_id)
        log.sfx[hook.value.name] = selection


def patch_instrument(rom, settings, log, symbols):
    # Player Instrument
    instruments = {
           #'none':            0x00,
            'ocarina':         0x01,
            'malon':           0x02,
            'whistle':         0x03,
            'harp':            0x04,
            'grind-organ':     0x05,
            'flute':           0x06,
           #'another_ocarina': 0x07,
            }
    if settings.sfx_ocarina != 'random-choice':
        choice = settings.sfx_ocarina
    else:
        choice = random.choice(list(instruments.keys()))
    rom.write_byte(0x00B53C7B, instruments[choice])
    # For Skull Kids' minigame in Lost Woods
    rom.write_byte(0x00B4BF6F, instruments[choice])
    log.sfx['Ocarina'] = choice


legacy_cosmetic_data_headers = [
    0x03481000,
    0x03480810,
]

global_patch_sets = [
    patch_targeting,
    patch_music,
    patch_tunic_colors,
    patch_navi_colors,
    patch_gauntlet_colors,
    patch_sfx,
    patch_instrument,    
]

patch_sets = {
    0x1F04FA62: {
        "patches": [
            patch_dpad,
            patch_sword_trails,
        ],
        "symbols": {    
            "CFG_DISPLAY_DPAD": 0x0004,
            "CFG_RAINBOW_SWORD_INNER_ENABLED": 0x0005,
            "CFG_RAINBOW_SWORD_OUTER_ENABLED": 0x0006,
        },
    },
    0x1F05D3F9: {
        "patches": [
            patch_dpad,
            patch_sword_trails,
        ],
        "symbols": {    
            "CFG_DISPLAY_DPAD": 0x0004,
            "CFG_RAINBOW_SWORD_INNER_ENABLED": 0x0005,
            "CFG_RAINBOW_SWORD_OUTER_ENABLED": 0x0006,
        },
    },
    0x1F0693FB: {
        "patches": [
            patch_dpad,
            patch_sword_trails,
            patch_heart_colors,
            patch_magic_colors,
        ],
        "symbols": {
            "CFG_MAGIC_COLOR": 0x0004,
            "CFG_HEART_COLOR": 0x000A,
            "CFG_DISPLAY_DPAD": 0x0010,
            "CFG_RAINBOW_SWORD_INNER_ENABLED": 0x0011,
            "CFG_RAINBOW_SWORD_OUTER_ENABLED": 0x0012,
        }
    }
}


def patch_cosmetics(settings, rom):
    log = CosmeticsLog(settings)

    # re-seed for aesthetic effects. They shouldn't be affected by the generation seed
    random.seed()
    settings.resolve_random_settings(cosmetic=True)

    # patch cosmetics that use vanilla oot data, and always compatible
    for patch_func in global_patch_sets:
        patch_func(rom, settings, log, {})

    # try to detect the cosmetic patch data format
    versioned_patch_set = None
    cosmetic_context = rom.read_int32(rom.sym('RANDO_CONTEXT') + 4)
    if cosmetic_context >= 0x80000000:
        cosmetic_context = (cosmetic_context - 0x80400000) + 0x3480000 # convert from RAM to ROM address
        cosmetic_version = rom.read_int32(cosmetic_context)
        versioned_patch_set = patch_sets.get(cosmetic_version)
    else:
        # If cosmetic_context is not a valid pointer, then try to
        # search over all possible legacy header locations.
        for header in legacy_cosmetic_data_headers:
            cosmetic_context = header
            cosmetic_version = rom.read_int32(cosmetic_context)
            if cosmetic_version in patch_sets:
                versioned_patch_set = patch_sets[cosmetic_version]
                break

    # patch version specific patches
    if versioned_patch_set:
        # offset the cosmetic_context struct for absolute addressing
        cosmetic_context_symbols = {
            sym: address + cosmetic_context
            for sym, address in versioned_patch_set['symbols'].items()
        }

        # warn if patching a legacy format
        if cosmetic_version != rom.read_int32(rom.sym('COSMETIC_FORMAT_VERSION')):
            log.error = "ROM uses old cosmetic patch format."

        for patch_func in versioned_patch_set['patches']:
            patch_func(rom, settings, log, cosmetic_context_symbols)
    else:
        # Unknown patch format
        log.error = "Unable to patch some cosmetics. ROM uses unknown cosmetic patch format."

    return log


class CosmeticsLog(object):

    def __init__(self, settings):
        self.settings = settings
        self.tunic_colors = {}
        self.navi_colors = {}
        self.sword_colors = {}
        self.gauntlet_colors = {}
        self.heart_colors = {}
        self.magic_colors = {}
        self.sfx = {}
        self.bgm = {}
        self.error = None


    def to_file(self, filename):
        with open(filename, 'w') as outfile:
            outfile.write(self.cosmetics_output())


    def cosmetics_output(self):
        output = ''
        output += 'OoT Randomizer Version %s - Cosmetics Log\n' % (__version__)

        if self.error:
            output += 'Error: %s\n' % self.error

        format_string = '\n{key:{width}} {value}'
        padding = 40

        output += format_string.format(key='Default Targeting Option:', value=self.settings.default_targeting, width=padding)
        output += format_string.format(key='Background Music:', value=self.settings.background_music, width=padding)
        output += format_string.format(key='Fanfares:', value=self.settings.fanfares, width=padding)
        if self.settings.fanfares == 'random':
            output += format_string.format(key='Ocarina Fanfares:', value=self.settings.ocarina_fanfares, width=padding)

        if 'display_dpad' in self.__dict__:
            output += format_string.format(key='Display D-Pad HUD:', value=self.display_dpad, width=padding)

        output += '\n\nColors:\n'
        for tunic, options in self.tunic_colors.items():
            color_option_string = '{option} (#{color})'
            output += format_string.format(key=tunic+':', value=color_option_string.format(option=options['option'], color=options['color']), width=padding)

        for navi_action, list in self.navi_colors.items():
            for i, options in enumerate(list):
                color_option_string = '{option1}, {option2} (#{color1}, #{color2})'
                output += format_string.format(key=(navi_action+':') if i == 0 else '', value=color_option_string.format(option1=options['option1'], color1=options['color1'], option2=options['option2'], color2=options['color2']), width=padding)

        if 'sword_colors' in self.__dict__:
            for sword_trail, list in self.sword_colors.items():
                for i, options in enumerate(list):
                    if options['option'] == 'Rainbow':
                        color_option_string = '{option}'
                    else:
                        color_option_string = '{option} (#{color})'
                    output += format_string.format(key=(sword_trail+':') if i == 0 else '', value=color_option_string.format(option=options['option'], color=options['color']), width=padding)

        if 'sword_trail_duration' in self.__dict__:
            output += format_string.format(key='Sword Trail Duration:', value=self.sword_trail_duration, width=padding)


        for gauntlet, options in self.gauntlet_colors.items():
            color_option_string = '{option} (#{color})'
            output += format_string.format(key=gauntlet+':', value=color_option_string.format(option=options['option'], color=options['color']), width=padding)
            
        for heart, options in self.heart_colors.items():
            color_option_string = '{option} (#{color})'
            output += format_string.format(key=heart+':', value=color_option_string.format(option=options['option'], color=options['color']), width=padding)

        for magic, options in self.magic_colors.items():
            color_option_string = '{option} (#{color})'
            output += format_string.format(key=magic+':', value=color_option_string.format(option=options['option'], color=options['color']), width=padding)

        output += '\n\nSFX:\n'
        for key, value in self.sfx.items():
            output += format_string.format(key=key+':', value=value, width=padding)

        if self.settings.background_music == 'random' or self.settings.fanfares == 'random':
            #music_padding = 1 + len(max(self.bgm.keys(), key=len))
            music_padding = 40
            output += '\n\nBackground Music:\n'
            for key, value in self.bgm.items():
                output += format_string.format(key=key+':', value=value, width=music_padding)

        return output
