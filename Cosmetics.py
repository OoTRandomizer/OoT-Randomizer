from version import __version__
import random
import Sounds as sfx


tunic_colors = {
    "Custom Color":      [0x00, 0x00, 0x00],
    "Kokiri Green":      [0x1E, 0x69, 0x1B],
    "Goron Red":         [0x64, 0x14, 0x00],
    "Zora Blue":         [0x00, 0x3C, 0x64],
    "Black":             [0x30, 0x30, 0x30],
    "White":             [0xF0, 0xF0, 0xFF],
    "Azure Blue":        [0x13, 0x9E, 0xD8],
    "Vivid Cyan":        [0x13, 0xE9, 0xD8],
    "Light Red":         [0xF8, 0x7C, 0x6D],
    "Fuchsia":           [0xFF, 0x00, 0xFF],
    "Purple":            [0x95, 0x30, 0x80],
    "Majora Purple":     [0x50, 0x52, 0x9A],
    "Twitch Purple":     [0x64, 0x41, 0xA5],
    "Purple Heart":      [0x8A, 0x2B, 0xE2],
    "Persian Rose":      [0xFF, 0x14, 0x93],
    "Dirty Yellow":      [0xE0, 0xD8, 0x60],
    "Blush Pink":        [0xF8, 0x6C, 0xF8],
    "Hot Pink":          [0xFF, 0x69, 0xB4],
    "Rose Pink":         [0xFF, 0x90, 0xB3],
    "Orange":            [0xE0, 0x79, 0x40],
    "Gray":              [0xA0, 0xA0, 0xB0],
    "Gold":              [0xD8, 0xB0, 0x60],
    "Silver":            [0xD0, 0xF0, 0xFF],
    "Beige":             [0xC0, 0xA0, 0xA0],
    "Teal":              [0x30, 0xD0, 0xB0],
    "Blood Red":         [0x83, 0x03, 0x03],
    "Blood Orange":      [0xFE, 0x4B, 0x03],
    "Royal Blue":        [0x40, 0x00, 0x90],
    "Sonic Blue":        [0x50, 0x90, 0xE0],
    "NES Green":         [0x00, 0xD0, 0x00],
    "Dark Green":        [0x00, 0x25, 0x18],
    "Lumen":             [0x50, 0x8C, 0xF0],
}


NaviColors = {
    "Custom Color":      [0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
    "Gold":              [0xFE, 0xCC, 0x3C, 0xFE, 0xC0, 0x07],
    "White":             [0xFF, 0xFF, 0xFF, 0x00, 0x00, 0xFF],
    "Green":             [0x00, 0xFF, 0x00, 0x00, 0xFF, 0x00],
    "Light Blue":        [0x96, 0x96, 0xFF, 0x96, 0x96, 0xFF],
    "Yellow":            [0xFF, 0xFF, 0x00, 0xC8, 0x9B, 0x00],
    "Red":               [0xFF, 0x00, 0x00, 0xFF, 0x00, 0x00],
    "Magenta":           [0xFF, 0x00, 0xFF, 0xC8, 0x00, 0x9B],
    "Black":             [0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
    "Tatl":              [0xFF, 0xFF, 0xFF, 0xC8, 0x98, 0x00],
    "Tael":              [0x49, 0x14, 0x6C, 0xFF, 0x00, 0x00],
    "Fi":                [0x2C, 0x9E, 0xC4, 0x2C, 0x19, 0x83],
    "Ciela":             [0xE6, 0xDE, 0x83, 0xC6, 0xBE, 0x5B],
    "Epona":             [0xD1, 0x49, 0x02, 0x55, 0x1F, 0x08],
    "Ezlo":              [0x62, 0x9C, 0x5F, 0x3F, 0x5D, 0x37],
    "King of Red Lions": [0xA8, 0x33, 0x17, 0xDE, 0xD7, 0xC5],
    "Linebeck":          [0x03, 0x26, 0x60, 0xEF, 0xFF, 0xFF],
    "Loftwing":          [0xD6, 0x2E, 0x31, 0xFD, 0xE6, 0xCC],
    "Midna":             [0x19, 0x24, 0x26, 0xD2, 0x83, 0x30],
    "Phantom Zelda":     [0x97, 0x7A, 0x6C, 0x6F, 0x46, 0x67],
}

sword_colors = {
    "Custom Color":      [0x00, 0x00, 0x00],
    "White":             [0xFF, 0xFF, 0xFF],
    "Red":               [0xFF, 0x00, 0x00],
    "Green":             [0x00, 0xFF, 0x00],
    "Blue":              [0x00, 0x00, 0xFF],
    "Cyan":              [0xFF, 0xFF, 0xFF],
    "Magenta":           [0xFF, 0x00, 0xFF],
    "Orange":            [0xFF, 0xA5, 0x00],
    "Gold":              [0xFF, 0xD7, 0x00],
    "Purple":            [0x80, 0x00, 0x80],
    "Pink":              [0xFF, 0x69, 0xB4],
}

def get_tunic_colors():
    return list(tunic_colors.keys())


def get_tunic_color_options():
    return ["Random Choice", "Completely Random"] + get_tunic_colors()

def get_navi_colors():
    return list(NaviColors.keys())


def get_navi_color_options():
    return ["Random Choice", "Completely Random"] + get_navi_colors()

def get_sword_colors():
    return list(sword_colors.keys())


def get_sword_color_options():
    return ["Random Choice", "Completely Random"] + get_sword_colors()

def patch_cosmetics(settings, rom):
    log = CosmeticsLog(settings)

    # re-seed for aesthetic effects. They shouldn't be affected by the generation seed
    random.seed()

    # Set default targeting option to Hold
    if settings.default_targeting == 'hold':
        rom.write_byte(0xB71E6D, 0x01)
    else:
        rom.write_byte(0xB71E6D, 0x00)

    # patch music
    if settings.background_music == 'random':
        restore_music(rom)
        log.bgm = randomize_music(rom)
    elif settings.background_music == 'off':
        disable_music(rom)
    else:
        restore_music(rom)

    # patch tunic colors
    tunics = [
        ('Kokiri Tunic', settings.kokiri_color, 0x00B6DA38),
        ('Goron Tunic', settings.goron_color,  0x00B6DA3B),
        ('Zora Tunic', settings.zora_color,   0x00B6DA3E),
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
            color = tunic_colors[tunic_option]
        # build color from hex code
        else:
            color = list(int(tunic_option[i:i+2], 16) for i in (0, 2 ,4))
            tunic_option = 'Custom'
        rom.write_bytes(address, color)
        log.tunic_colors[tunic] = dict(option=tunic_option, color=''.join(['{:02X}'.format(c) for c in color]))

    # patch navi colors
    navi = [
        # "Core" Colors, the inner colors for Navi
        ('Navi Idle Core', settings.navi_color_default, [0x00B5E184]), # Default
        ('Navi Targeting Enemy Core', settings.navi_color_enemy,   [0x00B5E19C, 0x00B5E1BC]), # Enemy, Boss
        ('Navi Targeting NPC Core', settings.navi_color_npc,     [0x00B5E194]), # NPC
        ('Navi Targeting Prop Core', settings.navi_color_prop,    [0x00B5E174, 0x00B5E17C, 0x00B5E18C,
                                  0x00B5E1A4, 0x00B5E1AC, 0x00B5E1B4,
                                  0x00B5E1C4, 0x00B5E1CC, 0x00B5E1D4]), # Everything else
        # "Glow" Colors, thne outer colors for Navi
        ('Navi Idle Glow', settings.navi_color_default_outside, [0x00B5E188]), # Default
        ('Navi Targeting Enemy Glow', settings.navi_color_enemy_outside,   [0x00B5E1A0, 0x00B5E1C0]), # Enemy, Boss
        ('Navi Targeting NPC Glow', settings.navi_color_npc_outside,     [0x00B5E198]), # NPC
        ('Navi Targeting Prop Glow', settings.navi_color_prop_outside,    [0x00B5E178, 0x00B5E180, 0x00B5E190,
                                  0x00B5E1A8, 0x00B5E1B0, 0x00B5E1B8,
                                  0x00B5E1C8, 0x00B5E1D0, 0x00B5E1D8]), # Everything else
    ]
    navi_color_list = get_navi_colors()
    for navi_action, navi_option, navi_addresses in navi:
        inner = navi_action in [action[0] for action in navi[0:4]]
        # choose a random choice for the whole group
        if navi_option == 'Random Choice':
            navi_option = random.choice(navi_color_list)
        custom_color = False
        for address in navi_addresses:
            # completely random is random for every subgroup
            if navi_option == 'Completely Random':
                color = [random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)]
            # grab the color from the list
            elif navi_option in NaviColors:
                if inner:
                    color = NaviColors.get(navi_option)[0:3]
                else:
                    color = NaviColors.get(navi_option)[3:6]
            # build color from hex code
            else:
                color = list(int(navi_option[i:i+2], 16) for i in (0, 2 ,4))
                custom_color = True
            if inner:
                color = color + [0xFF]
            else:
                color = color + [0x00]
            rom.write_bytes(address, color)
        if custom_color:
            navi_option = 'Custom'
        if navi_action not in log.navi_colors:
            log.navi_colors[navi_action] = dict(option=navi_option, color=''.join(['{:02X}'.format(c) for c in color[0:3]]))
    
    # patch sword trail colors
    sword_trails = [
        ('Inner Initial Sword Trail', settings.sword_trail_color_inner1, 0x00BEFF7C, 0xB0),
        ('Outer Initial Sword Trail', settings.sword_trail_color_outer1,  0x00BEFF80, 0xB0),
        ('Inner Fade Sword Trail', settings.sword_trail_color_inner2,   0x00BEFF88, 0x20),
        ('Outer Fade Sword Trail', settings.sword_trail_color_outer2, 0x00BEFF84, 0x10)
    ]
    sword_color_list = get_sword_colors()
    
    if not settings.rainbow_sword_trail:
        for index, item in enumerate(sword_trails):
            sword_trail, sword_trail_option, sword_trail_address, transparency = item
            # handle random
            if sword_trail_option == 'Random Choice':
                sword_trail_option = random.choice(sword_color_list)
            # handle completely random
            if sword_trail_option == 'Completely Random':
                color = [random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)]
            elif sword_trail_option in sword_colors:
                color = sword_colors[sword_trail_option]
            # build color from hex code
            else:
                color = list(int(sword_trail_option[i:i+2], 16) for i in (0, 2 ,4))
                sword_trail_option = 'Custom'
            if sword_trail_option == 'White':
                if index < 2:
                    transparency = 0xFF
                if index == 2:
                    transparency = 0x40
                if index == 3:
                    transparency = 0x00
            color = color + [transparency]
            rom.write_bytes(sword_trail_address, color)
            log.sword_colors[sword_trail] = dict(option=sword_trail_option, color=''.join(['{:02X}'.format(c) for c in color]))
    else: 
        rom.write_bytes(0x00BEFF7C, [0x00, 0x00, 0x00, 0xB0,
                                     0x00, 0x00, 0x00, 0xB0,
                                     0x00, 0x00, 0x00, 0x20,
                                     0x00, 0x00, 0x00, 0x10])
        symbol = rom.sym('RAINBOW_SWORD_ENABLED')
        rom.write_int32(symbol, 0x00000001)
    rom.write_byte(0x00BEFF8C, settings.sword_trail_duration)
        
    # Configurable Sound Effects
    sfx_config = [
          (settings.sfx_hover_boots,    sfx.SoundHooks.BOOTS_HOVER),
          (settings.sfx_menu_select,    sfx.SoundHooks.MENU_SELECT),
          (settings.sfx_menu_cursor,    sfx.SoundHooks.MENU_CURSOR),
          (settings.sfx_horse_neigh,    sfx.SoundHooks.HORSE_NEIGH),
          (settings.sfx_navi_overworld, sfx.SoundHooks.NAVI_OVERWORLD),
          (settings.sfx_navi_enemy,     sfx.SoundHooks.NAVI_ENEMY),
          (settings.sfx_low_hp,         sfx.SoundHooks.HP_LOW),
          (settings.sfx_nightfall,      sfx.SoundHooks.NIGHTFALL),
    ]
    sound_dict = sfx.get_patch_dict()

    for selection, hook in sfx_config:
        if selection == 'default':
            for loc in hook.value.locations:
                sound_id = int.from_bytes((rom.original[loc:loc+2]), byteorder='big', signed=False)
                rom.write_int16(loc, sound_id)
        else:
            if selection == 'random-choice':
                selection = random.choice(sfx.get_hook_pool(hook)).value.keyword
            elif selection == 'random-ear-safe':
                selection = random.choice(sfx.no_painful).value.keyword
            elif selection == 'completely-random':
                selection = random.choice(sfx.standard).value.keyword
            sound_id  = sound_dict[selection]
            for loc in hook.value.locations:
                rom.write_int16(loc, sound_id)
        log.sfx[hook.value.name] = selection

    # Player Instrument
    instruments = {
           #'none':            0x00,
            'ocarina':         0x01,
            'malon':           0x02,
            'whistle':         0x03,
            'harp':            0x04,
            'grind_organ':     0x05,
            'flute':           0x06,
           #'another_ocarina': 0x07,
            }
    if settings.sfx_ocarina != 'random':
        choice = settings.sfx_ocarina
    else:
        choice = random.choice(list(instruments.keys()))
    rom.write_byte(0x00B53C7B, instruments[choice])
    log.sfx['Ocarina'] = choice

    return log


# Format: (Title, Sequence ID)
bgm_sequence_ids = [
    ('Hyrule Field', 0x02),
    ('Dodongos Cavern', 0x18),
    ('Kakariko Adult', 0x19),
    ('Battle', 0x1A),
    ('Boss Battle', 0x1B),
    ('Inside Deku Tree', 0x1C),
    ('Market', 0x1D),
    ('Title Theme', 0x1E),
    ('House', 0x1F),
    ('Jabu Jabu', 0x26),
    ('Kakariko Child', 0x27),
    ('Fairy Fountain', 0x28),
    ('Zelda Theme', 0x29),
    ('Fire Temple', 0x2A),
    ('Forest Temple', 0x2C),
    ('Castle Courtyard', 0x2D),
    ('Ganondorf Theme', 0x2E),
    ('Lon Lon Ranch', 0x2F),
    ('Goron City', 0x30),
    ('Miniboss Battle', 0x38),
    ('Temple of Time', 0x3A),
    ('Kokiri Forest', 0x3C),
    ('Lost Woods', 0x3E),
    ('Spirit Temple', 0x3F),
    ('Horse Race', 0x40),
    ('Ingo Theme', 0x42),
    ('Fairy Flying', 0x4A),
    ('Deku Tree', 0x4B),
    ('Windmill Hut', 0x4C),
    ('Shooting Gallery', 0x4E),
    ('Sheik Theme', 0x4F),
    ('Zoras Domain', 0x50),
    ('Shop', 0x55),
    ('Chamber of the Sages', 0x56),
    ('Ice Cavern', 0x58),
    ('Kaepora Gaebora', 0x5A),
    ('Shadow Temple', 0x5B),
    ('Water Temple', 0x5C),
    ('Gerudo Valley', 0x5F),
    ('Potion Shop', 0x60),
    ('Kotake and Koume', 0x61),
    ('Castle Escape', 0x62),
    ('Castle Underground', 0x63),
    ('Ganondorf Battle', 0x64),
    ('Ganon Battle', 0x65),
    ('Fire Boss', 0x6B),
    ('Mini-game', 0x6C)
]


def randomize_music(rom):
    log = {}

    # Read in all the Music data
    bgm_data = []
    for bgm in bgm_sequence_ids:
        bgm_sequence = rom.read_bytes(0xB89AE0 + (bgm[1] * 0x10), 0x10)
        bgm_instrument = rom.read_int16(0xB89910 + 0xDD + (bgm[1] * 2))
        bgm_data.append((bgm[0], bgm_sequence, bgm_instrument))

    # shuffle data
    random.shuffle(bgm_data)

    # Write Music data back in random ordering
    for bgm in bgm_sequence_ids:
        bgm_name, bgm_sequence, bgm_instrument = bgm_data.pop()
        rom.write_bytes(0xB89AE0 + (bgm[1] * 0x10), bgm_sequence)
        rom.write_int16(0xB89910 + 0xDD + (bgm[1] * 2), bgm_instrument)
        log[bgm[0]] = bgm_name

    # Write Fairy Fountain instrument to File Select (uses same track but different instrument set pointer for some reason)
    rom.write_int16(0xB89910 + 0xDD + (0x57 * 2), rom.read_int16(0xB89910 + 0xDD + (0x28 * 2)))
    return log


def disable_music(rom):
    # First track is no music
    blank_track = rom.read_bytes(0xB89AE0 + (0 * 0x10), 0x10)
    for bgm in bgm_sequence_ids:
        rom.write_bytes(0xB89AE0 + (bgm[1] * 0x10), blank_track)


def restore_music(rom):
    # Restore all music from original
    for bgm in bgm_sequence_ids:
        bgm_sequence = rom.original[0xB89AE0 + (bgm[1] * 0x10): 0xB89AE0 + (bgm[1] * 0x10) + 0x10]
        rom.write_bytes(0xB89AE0 + (bgm[1] * 0x10), bgm_sequence)
        bgm_instrument = rom.original[0xB89910 + 0xDD + (bgm[1] * 2): 0xB89910 + 0xDD + (bgm[1] * 2) + 0x02]
        rom.write_bytes(0xB89910 + 0xDD + (bgm[1] * 2), bgm_instrument)

    # restore file select instrument
    bgm_instrument = rom.original[0xB89910 + 0xDD + (0x57 * 2): 0xB89910 + 0xDD + (0x57 * 2) + 0x02]
    rom.write_bytes(0xB89910 + 0xDD + (0x57 * 2), bgm_instrument)


class CosmeticsLog(object):

    def __init__(self, settings):
        self.settings = settings
        self.tunic_colors = {}
        self.navi_colors = {}
        self.sword_colors = {}
        self.sfx = {}
        self.bgm = {}


    def to_file(self, filename):
        with open(filename, 'w') as outfile:
            outfile.write(self.cosmetics_output())


    def cosmetics_output(self):
        output = ''
        output += 'OoT Randomizer Version %s - Cosmetics Log\n' % (__version__)

        format_string = '\n{key:{width}} {value}'
        #keys = list(self.tunic_colors.keys()) + list(self.navi_colors.keys()) + list(self.sfx.keys()) + ['Default Targeting Option', 'Background Music']
        #padding = 1 + len(max(keys, key=len))
        padding = 40

        output += format_string.format(key='Default Targeting Option:', value=self.settings.default_targeting, width=padding)
        output += format_string.format(key='Background Music:', value=self.settings.background_music, width=padding)

        output += '\n\nColors:\n'
        for tunic, options in self.tunic_colors.items():
            color_option_string = '{option} (#{color})'
            output += format_string.format(key=tunic+':', value=color_option_string.format(option=options['option'], color=options['color']), width=padding)
        for navi_action, options in self.navi_colors.items():
            color_option_string = '{option} (#{color})'
            output += format_string.format(key=navi_action+':', value=color_option_string.format(option=options['option'], color=options['color']), width=padding)
        if not self.settings.rainbow_sword_trail:
            for sword_trail, options in self.sword_colors.items():
                color_option_string = '{option} (#{color})'
                output += format_string.format(key=sword_trail+':', value=color_option_string.format(option=options['option'], color=options['color']), width=padding)
        output += format_string.format(key="Rainbow Sword Trails:", value=self.settings.rainbow_sword_trail, width=padding)
        output += format_string.format(key='Sword Trail Duration:', value=self.settings.sword_trail_duration, width=padding)

        output += '\n\nSFX:\n'
        for key, value in self.sfx.items():
            output += format_string.format(key=key+':', value=value, width=padding)

        if self.settings.background_music == 'random':
            #music_padding = 1 + len(max(self.bgm.keys(), key=len))
            music_padding = 40
            output += '\n\nBackground Music:\n'
            for key, value in self.bgm.items():
                output += format_string.format(key=key+':', value=value, width=music_padding)

        return output
