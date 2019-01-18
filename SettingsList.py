import argparse
import re
import math
from Cosmetics import get_tunic_color_options, get_navi_color_options, get_sword_color_options, get_gauntlet_color_options
from LocationList import location_table
import Sounds as sfx

# holds the info for a single setting
class Setting_Info():

    def __init__(self, name, type, bitwidth=0, shared=False, args_params={}, gui_params=None):
        self.name = name # name of the setting, used as a key to retrieve the setting's value everywhere
        self.type = type # type of the setting's value, used to properly convert types in GUI code
        self.bitwidth = bitwidth # number of bits needed to store the setting, used in converting settings to a string
        self.shared = shared # whether or not the setting is one that should be shared, used in converting settings to a string
        self.args_params = args_params # parameters that should be pased to the command line argument parser's add_argument() function
        self.gui_params = gui_params # parameters that the gui uses to build the widget components

        # create the choices parameters from the gui options if applicable
        if gui_params and 'options' in gui_params and 'choices' not in args_params \
                and not ('type' in args_params and callable(args_params['type'])):
            if isinstance(gui_params['options'], list):
                self.args_params['choices'] = list(gui_params['options'])
            elif isinstance(gui_params['options'], dict):
                self.args_params['choices'] = list(gui_params['options'].values())


class Setting_Widget(Setting_Info):

    def __init__(self, name, type, choices, default, args_params={},
            gui_params=None, shared=False):

        assert 'default' not in args_params and 'default' not in gui_params, \
                'Setting {}: default shouldn\'t be defined in '\
                'args_params or in gui_params'.format(name)
        assert 'choices' not in args_params, \
                'Setting {}: choices shouldn\'t be defined in '\
                'args_params'.format(name)
        assert 'options' not in gui_params, \
                'Setting {}: options shouldn\'t be defined in '\
                'gui_params'.format(name)

        if 'type' not in args_params: args_params['type'] = type
        if 'type' not in gui_params:  gui_params['type']  = type

        self.choices = choices
        self.default = default
        args_params['choices'] = list(choices.keys())
        args_params['default'] = default
        gui_params['options']  = {v: k for k, v in choices.items()}
        gui_params['default']  = choices[default]

        super().__init__(name, type, self.calc_bitwidth(choices), shared, args_params, gui_params)


    def calc_bitwidth(self, choices):
        count = len(choices)
        if count > 0:
            return math.ceil(math.log(count, 2))
        return 0


class Checkbutton(Setting_Widget):

    def __init__(self, name, args_help, gui_text, gui_group=None,
            gui_tooltip=None, gui_dependency=None, default=False,
            shared=False):

        choices = {
                True:  'checked',
                False: 'unchecked',
                }
        gui_params = {
                'text':    gui_text,
                'widget': 'Checkbutton',
                }
        if gui_group      is not None: gui_params['group']      = gui_group
        if gui_tooltip    is not None: gui_params['tooltip']    = gui_tooltip
        if gui_dependency is not None: gui_params['dependency'] = gui_dependency
        args_params = {
                'help':    args_help,
                }

        super().__init__(name, bool, choices, default, args_params, gui_params,
                shared)
        self.args_params['type'] = Checkbutton.parse_bool


    def parse_bool(s):
      if s.lower() in ['yes', 'true', 't', 'y', '1']:
          return True
      elif s.lower() in ['no', 'false', 'f', 'n', '0']:
          return False
      else:
          raise argparse.ArgumentTypeError('Boolean value expected.')


class Combobox(Setting_Widget):

    def __init__(self, name, choices, default, args_help, gui_text=None,
            gui_group=None, gui_tooltip=None, gui_dependency=None,
            shared=False):

        type = str
        gui_params = {
                'widget': 'Combobox',
                }
        if gui_text       is not None: gui_params['text']       = gui_text
        if gui_group      is not None: gui_params['group']      = gui_group
        if gui_tooltip    is not None: gui_params['tooltip']    = gui_tooltip
        if gui_dependency is not None: gui_params['dependency'] = gui_dependency
        args_params = {
                'help':    args_help,
                }

        super().__init__(name, type, choices, default, args_params, gui_params,
                shared)


class Scale(Setting_Widget):

    def __init__(self, name, min, max, default, args_help, step=1,
            gui_text=None, gui_group=None, gui_tooltip=None,
            gui_dependency=None, shared=False):

        type = int
        choices = {}
        for i in range(min, max+1, step):
            choices = {**choices, i: str(i)}
        gui_params = {
                'min':     min,
                'max':     max,
                'step':    step,
                'widget': 'Scale',
                }
        if gui_text       is not None: gui_params['text']       = gui_text
        if gui_group      is not None: gui_params['group']      = gui_group
        if gui_tooltip    is not None: gui_params['tooltip']    = gui_tooltip
        if gui_dependency is not None: gui_params['dependency'] = gui_dependency
        args_params = {
                'help':    args_help,
                }

        super().__init__(name, type, choices, default, args_params, gui_params,
                shared)


def parse_custom_tunic_color(s):
    return parse_color(s, get_tunic_color_options())

def parse_custom_navi_color(s):
    return parse_color(s, get_navi_color_options())

def parse_custom_sword_color(s):
    return parse_color(s, get_sword_color_options())

def parse_custom_gauntlet_color(s):
    return parse_color(s, get_gauntlet_color_options())

def parse_color(s, color_choices):
    if s == 'Custom Color':
        raise argparse.ArgumentTypeError('Specify custom color by using \'Custom (#xxxxxx)\'')
    elif re.match(r'^Custom \(#[A-Fa-f0-9]{6}\)$', s):
        return re.findall(r'[A-Fa-f0-9]{6}', s)[0]
    elif s in color_choices:
        return s
    else:
        raise argparse.ArgumentTypeError('Invalid color specified')

def logic_tricks_entry_tooltip(widget, pos):
    val = widget.get()
    if val in logic_tricks:
        text = val + '\n\n' + logic_tricks[val]['tooltip']
        text = '\n'.join([line.strip() for line in text.splitlines()]).strip()
        return text
    else:
        return None

def logic_tricks_list_tooltip(widget, pos):
    index = widget.index("@%s,%s" % (pos))
    val = widget.get(index)
    if val in logic_tricks:
        text = val + '\n\n' + logic_tricks[val]['tooltip']
        text = '\n'.join([line.strip() for line in text.splitlines()]).strip()
        return text
    else:
        return None



logic_tricks = {
    'Morpha with Gold Scale': {
        'name'    : 'logic_morpha_with_scale',
        'tooltip' : '''\
                    Allows entering Water Temple and beating
                    Morpha with Gold Scale instead of Iron Boots.
                    Only applicable for keysanity and keysy due
                    to the logic always seeing every chest in
                    Water Temple that could contain the Boss Key
                    as requiring Iron Boots.
                    '''},
    'Fewer Tunic Requirements': {
        'name'    : 'logic_fewer_tunic_requirements',
        'tooltip' : '''\
                    Allows the following possible without Tunics:
                    - Enter Water Temple. The key below the center
                    pillar still requires Zora Tunic.
                    - Enter Fire Temple. Only the first floor is
                    accessible, and not Volvagia.
                    - Zora's Fountain Bottom Freestanding PoH.
                    Might not have enough health to resurface.
                    - Gerudo Training Grounds Underwater
                    Silver Rupee Chest. May need to make multiple
                    trips.
                    '''},

    'Child Deadhand without Kokiri Sword': {
        'name'    : 'logic_child_deadhand',
        'tooltip' : '''\
                    Requires 9 sticks or 5 jump slashes.
                    '''},
    'Man on Roof without Hookshot': {
        'name'    : 'logic_man_on_roof',
        'tooltip' : '''\
                    Can be reached by side-hopping off
                    the watchtower.
                    '''},
    'Dodongo\'s Cavern Staircase with Bow': {
        'name'    : 'logic_dc_staircase',
        'tooltip' : '''\
                    The Bow can be used to knock down the stairs
                    with two well-timed shots.
                    '''},
    'Dodongo\'s Cavern Spike Trap Room Jump without Hover Boots': {
        'name'    : 'logic_dc_jump',
        'tooltip' : '''\
                    Jump is adult only.
                    '''},
    'Gerudo Fortress "Kitchen" with No Additional Items': {
        'name'    : 'logic_gerudo_kitchen',
        'tooltip' : '''\
                    The logic normally guarantees one of Bow, Hookshot,
                    or Hover Boots.
                    '''},
    'Deku Tree Basement Vines GS with Jump Slash': {
        'name'    : 'logic_deku_basement_gs',
        'tooltip' : '''\
                    Can be defeated by doing a precise jump slash.
                    '''},
    'Hammer Rusted Switches Through Walls': {
        'name'    : 'logic_rusted_switches',
        'tooltip' : '''\
                    Applies to:
                    - Fire Temple Highest Goron Chest.
                    - MQ Fire Temple Lizalfos Maze.
                    - MQ Spirit Trial.
                    '''},
    'Bottom of the Well Basement Chest with Strength & Sticks': {
        'name'    : 'logic_botw_basement',
        'tooltip' : '''\
                    The chest in the basement can be reached with
                    strength by doing a jump slash with a lit
                    stick to access the bomb flowers.
                    '''},
    'Skip Forest Temple MQ Block Puzzle with Bombchu': {
        'name'    : 'logic_forest_mq_block_puzzle',
        'tooltip' : '''\
                    Send the Bombchu straight up the center of the
                    wall directly to the left upon entering the room.
                    '''},
    'Spirit Temple Child Side Bridge with Bombchu': {
        'name'    : 'logic_spirit_child_bombchu',
        'tooltip' : '''\
                    A carefully-timed Bombchu can hit the switch.
                    '''},
    'Windmill PoH as Adult with Nothing': {
        'name'    : 'logic_windmill_poh',
        'tooltip' : '''\
                    Can jump up to the spinning platform from
                    below as adult.
                    '''},
    'Crater\'s Bean PoH with Hover Boots': {
        'name'    : 'logic_crater_bean_poh_with_hovers',
        'tooltip' : '''\
                    Hover from the base of the bridge
                    near Goron City and walk up the
                    very steep slope.
                    '''},
    'Gerudo Training Grounds MQ Left Side Silver Rupees with Hookshot': {
        'name'    : 'logic_gtg_mq_with_hookshot',
        'tooltip' : '''\
                    The highest silver rupee can be obtained by
                    hookshotting the target and then immediately jump
                    slashing toward the rupee.
                    '''},
    'Forest Temple East Courtyard Vines with Hookshot': {
        'name'    : 'logic_forest_vines',
        'tooltip' : '''\
                    The vines in Forest Temple leading to where the well
                    drain switch is in the standard form can be barely
                    reached with just the Hookshot.
                    '''},
    'Swim Through Forest Temple MQ Well with Hookshot': {
        'name'    : 'logic_forest_well_swim',
        'tooltip' : '''\
                    Shoot the vines in the well as low and as far to
                    the right as possible, and then immediately swim
                    under the ceiling to the right. This can only be
                    required if Forest Temple is in its Master Quest
                    form.
                    '''},
    'Death Mountain Trail Bombable Chest with Strength': {
        'name'    : 'logic_dmt_bombable',
        'tooltip' : '''\
                    Child Link can blow up the wall using a nearby bomb
                    flower. You must backwalk with the flower and then
                    quickly throw it toward the wall.
                    '''},
    'Water Temple Boss Key Chest with No Additional Items': {
        'name'    : 'logic_water_bk_chest',
        'tooltip' : '''\
                    After reaching the Boss Key chest's area with Iron Boots
                    and Longshot, the chest can be reached with no additional
                    items aside from Small Keys. Stand on the blue switch
                    with the Iron Boots, wait for the water to rise all the
                    way up, and then swim straight to the exit. You should
                    grab the ledge as you surface. It works best if you don't
                    mash B.
                    '''},
    'Adult Kokiri Forest GS with Hover Boots': {
        'name'    : 'logic_adult_kokiri_gs',
        'tooltip' : '''\
                    Can be obtained without Hookshot by using the Hover
                    Boots off of one of the roots.
                    '''},
    'Spirit Temple MQ Frozen Eye Switch without Fire': {
        'name'    : 'logic_spirit_mq_frozen_eye',
        'tooltip' : '''\
                    You can melt the ice by shooting an arrow through a
                    torch. The only way to find a line of sight for this
                    shot is to first spawn a Song of Time block, and then
                    stand on the very edge of it.
                    '''},
    'Fire Temple MQ Boss Key Chest without Bow': {
        'name'    : 'logic_fire_mq_bk_chest',
        'tooltip' : '''\
                    Din\'s alone can be used to unbar the door to
                    the boss key chest's room thanks to an
                    oversight in the way the game counts how many
                    torches have been lit.
                    '''},
    'Zora\'s Domain Entry with Cucco': {
        'name'    : 'logic_zora_with_cucco',
        'tooltip' : '''\
                    Can fly behind the waterfall with
                    a cucco as child.
                    '''},
    'Zora\'s Domain Entry with Hover Boots': {
        'name'    : 'logic_zora_with_hovers',
        'tooltip' : '''\
                    Can hover behind the waterfall as adult.
                    This is very difficult.
                    '''},
}


# a list of the possible settings
setting_infos = [
    Setting_Info('check_version', bool, 0, False,
    {
        'help': '''\
                Checks if you are on the latest version
                ''',
        'action': 'store_true'
    }),
    Setting_Info('checked_version', str, 0, False, {
            'default': '',
            'help': 'Supress version warnings if checked_version is less than __version__.'}),
    Setting_Info('rom', str, 0, False, {
            'default': '',
            'help': 'Path to an OoT 1.0 rom to use as a base.'}),
    Setting_Info('output_dir', str, 0, False, {
            'default': '',
            'help': 'Path to output directory for rom generation.'}),
    Setting_Info('seed', str, 0, False, {
            'help': 'Define seed number to generate.'}),
    Setting_Info('patch_file', str, 0, False, {
            'default': '',
            'help': 'Path to a patch file.'}),
    Setting_Info('cosmetics_only', bool, 0, False, 
    {
            'help': 'Patched file will only have cosmetics applied.',
            'action': 'store_true',
    }),
    Setting_Info('count', int, 0, False, {
            'help': '''\
                    Use to batch generate multiple seeds with same settings.
                    If --seed is provided, it will be used for the first seed, then
                    used to derive the next seed (i.e. generating 10 seeds with
                    --seed given will produce the same 10 (different) roms each
                    time).
                    ''',
            'type': int}),
    Setting_Info('world_count', int, 5, True, {
            'default': 1,
            'help': '''\
                    Use to create a multi-world generation for co-op seeds.
                    World count is the number of players. Warning: Increasing
                    the world count will drastically increase generation time.
                    ''',
            'type': int}, {}),
    Setting_Info('player_num', int, 0, False, 
        {
            'default': 1,
            'help': '''\
                    Use to select world to generate when there are multiple worlds.
                    ''',
            'type': int
        },
        {
            'dependency': lambda settings: 1 if settings.compress_rom in ['None', 'Patch'] else None,
        }),
    Checkbutton(
            name           = 'create_spoiler',
            args_help      = '''\
                             Output a Spoiler File
                             ''',
            gui_text       = 'Create Spoiler Log',
            gui_group      = 'rom_tab',
            gui_tooltip    = '''\
                             Enabling this will change the seed.
                             ''',
            default        = True,
            shared         = True,
            ),
    Checkbutton(
        name='create_cosmetics_log',
        args_help='''\
                         Output a Cosmetics Log
                         ''',
        gui_text='Create Cosmetics Log',
        gui_group='rom_tab',
        gui_dependency=lambda settings: False if settings.compress_rom in ['None', 'Patch'] else None,
        default=True,
        shared=False,
    ),
    Setting_Widget(
        name='compress_rom',
        type=str,
        default='True',
        choices={
            'True': 'Compressed [Stable]',
            'False': 'Uncompressed [Crashes]',
            'Patch': 'Patch File',
            'None': 'No Output',
        },
        args_params={
            'help': '''\
                    Create a compressed version of the output ROM file.
                    True: Compresses. Improves stability. Will take longer to generate
                    False: Uncompressed. Unstable. Faster generation
                    Patch: Patch file. No ROM, but used to send the patch data
                    None: No ROM Output. Creates spoiler log only
                    ''',
        },
        gui_params={
            'text': 'Output Type',
            'group': 'rom_tab',
            'widget': 'Radiobutton',
            'horizontal': True,
            'tooltip':'''\
                      The first time compressed generation will take a while,
                      but subsequent generations will be quick. It is highly
                      recommended to compress or the game will crash
                      frequently except on real N64 hardware.

                      Patch files are used to send the patched data to other
                      people without sending the ROM file.
                      '''
        },
        shared=False,
    ),
    Checkbutton(
            name           = 'open_forest',
            args_help      = '''\
                             Mido no longer blocks the path to the Deku Tree, and
                             the Kokiri boy no longer blocks the path out of the forest.
                             ''',
            gui_text       = 'Open Forest',
            gui_group      = 'open',
            gui_tooltip    = '''\
                             Mido no longer blocks the path to the Deku Tree,
                             and the Kokiri boy no longer blocks the path out
                             of the forest.

                             When this option is off, the Kokiri Sword and
                             Slingshot are always available somewhere
                             in the forest.
                             ''',
            default        = True,
            shared         = True,
            ),
    Checkbutton(
            name           = 'open_kakariko',
            args_help      = '''\
                             The gate in Kakariko Village to Death Mountain Trail
                             is always open instead of needing Zelda's Letter.
                             ''',
            gui_text       = 'Open Kakariko Gate',
            gui_group      = 'open',
            gui_tooltip    = '''\
                             The gate in Kakariko Village to Death Mountain Trail
                             is always open instead of needing Zelda's Letter.

                             Either way, the gate is always open as an adult.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'open_door_of_time',
            args_help      = '''\
                             The Door of Time is open from the beginning of the game.
                             ''',
            gui_text       = 'Open Door of Time',
            gui_group      = 'open',
            gui_tooltip    = '''\
                             The Door of Time starts opened instead of needing to
                             play the Song of Time. If this is not set, only
                             an Ocarina and Song of Time must be found to open
                             the Door of Time.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'open_fountain',
            args_help      = '''\
                             King Zora is moved from the beginning of the game.
                             ''',
            gui_text       = 'Open Zora\'s Fountain',
            gui_group      = 'open',
            gui_tooltip    = '''\
                             King Zora starts out as moved. This also removes
                             Ruto's Letter from the item pool.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'gerudo_fortress',
            default        = 'normal',
            choices        = {
                'normal': 'Default Behavior',
                'fast':   'Rescue One Carpenter',
                'open':   'Start with Gerudo Card',
                },
            args_help      = '''\
                             Select how much of Gerudo Fortress is required. (default: %(default)s)
                             Normal: Free all four carpenters to get the Gerudo Card.
                             Fast:   Free only the carpenter closest to Link's prison to get the Gerudo Card.
                             Open:   Start with the Gerudo Card and all its benefits.
                             ''',
            gui_text       = 'Gerudo Fortress',
            gui_group      = 'open',
            gui_tooltip    = '''\
                             'Rescue One Carpenter': Only the bottom left
                             carpenter must be rescued.
                             
                             'Start with Gerudo Card': The carpenters are rescued from
                             the start of the game, and the player starts with the Gerudo
                             Card in the inventory allowing access to Gerudo Training Grounds.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'bridge',
            default        = 'medallions',
            choices        = {
                'open':       'Always Open',
                'vanilla':    'Vanilla Requirements',
                'stones':	  'All Spiritual Stones',
                'medallions': 'All Medallions',
                'dungeons':   'All Dungeons',
                'tokens':     '100 Gold Skulltula Tokens'
                },
            args_help      = '''\
                             Select requirement to spawn the Rainbow Bridge to reach Ganon's Castle. (default: %(default)s)
                             open:       The bridge will spawn without an item requirement.
                             vanilla:    Collect only the Shadow and Spirit Medallions and possess the Light Arrows.
                             stones:     Collect all three Spiritual Stones to create the bridge.
                             medallions: Collect all six Medallions to create the bridge.
                             dungeons:   Collect all Spiritual Stones and all Medallions to create the bridge.
                             tokens:     Collect all 100 Gold Skulltula tokens.
                             ''',
            gui_text       = 'Rainbow Bridge Requirement',
            gui_group      = 'open',
            gui_tooltip    = '''\
                             'Always Open': Rainbow Bridge is always present.
                             'Vanilla Requirements': Spirit/Shadow Medallions and Light Arrows.
                             'All Spiritual Stones': All 3 Spiritual Stones.
                             'All Medallions': All 6 Medallions.
                             'All Dungeons': All Medallions and Spiritual Stones.
                             '100 Gold Skulltula Tokens': All 100 Gold Skulltula Tokens.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'logic_rules',
            default        = 'glitchless',
            choices        = {
                'glitchless': 'Glitchless',
                'none':       'No Logic',
                },
            args_help      = '''\
                             Sets the rules the logic uses to determine accessibility:
                             glitchless:  No glitches are required, but may require some minor tricks
                             none:        All locations are considered available. May not be beatable.
                             ''',
            gui_text       = 'Logic Rules',
            gui_group      = 'world',
            gui_tooltip    = '''\
                             Sets the rules the logic uses
                             to determine accessibility.
        
                             'Glitchless': No glitches are
                             required, but may require some
                             minor tricks
        
                             'No Logic': All locations are
                             considered available. May not
                             be beatable.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'all_reachable',
            args_help      = '''\
                             When disabled, only check if the game is beatable with
                             placement. Do not ensure all locations are reachable.
                             ''',
            gui_text       = 'All Locations Reachable',
            gui_group      = 'world',
            gui_tooltip    = '''\
                             When this option is enabled, the randomizer will
                             guarantee that every item is obtainable and every
                             location is reachable.
        
                             When disabled, only required items and locations
                             to beat the game will be guaranteed reachable.
        
                             Even when enabled, some locations may still be able
                             to hold the keys needed to reach them.
                             ''',
            default        = True,
            shared         = True,
            ),
    Checkbutton(
            name           = 'bombchus_in_logic',
            args_help      = '''\
                             Bombchus will be considered in logic. This has a few effects:
                             -Back Alley shop will open once you've found Bombchus.
                             -It will sell an affordable pack (5 for 60) and never sell out.
                             -Bombchus refills cannot be bought until Bombchus have been obtained.
                             ''',
            gui_text       = 'Bombchus Are Considered in Logic',
            gui_group      = 'world',
            gui_tooltip    = '''\
                             Bombchus are properly considered in logic.
        
                             The first Bombchu pack will always be 20.
                             Subsequent packs will be 5 or 10 based on
                             how many you have.
        
                             Bombchus can be purchased for 60/99/180
                             rupees once they have been found.
        
                             Bombchu Bowling opens with Bombchus.
                             Bombchus are available at Kokiri Shop
                             and the Bazaar. Bombchu refills cannot
                             be bought until Bombchus have been
                             obtained.
                             ''',
            default        = True,
            shared         = True,
            ),
    Checkbutton(
            name           = 'one_item_per_dungeon',
            args_help      = '''\
                             Each dungeon will have exactly one major item.
                             Does not include dungeon items or GS Tokens.
                             ''',
            gui_text       = 'Dungeons Have One Major Item',
            gui_group      = 'world',
            gui_tooltip    = '''\
                             Dungeons have exactly one major
                             item. This naturally makes each
                             dungeon similar in value instead
                             of valued based on chest count.
        
                             Spirit Temple Colossus hands count
                             as part of the dungeon. Spirit
                             Temple has TWO items to match
                             vanilla distribution.
        
                             Dungeon items and GS Tokens do
                             not count as major items.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'trials_random',
            args_help      = '''\
                             Sets the number of trials must be cleared to enter
                             Ganon's Tower to a random value.
                             ''',
            gui_text       = 'Random Number of Ganon\'s Trials',
            gui_group      = 'open',
            gui_tooltip    = '''\
                             Sets a random number of trials to
                             enter Ganon's Tower.
                             ''',
            shared         = True,
            ),
    Scale(
            name           = 'trials',
            default        = 6,
            min            = 0,
            max            = 6,
            args_help      = '''\
                             Select how many trials must be cleared to enter Ganon's Tower.
                             The trials you must complete will be selected randomly.
                             ''',
            gui_group      = 'open',
            gui_tooltip    = '''\
                             Trials are randomly selected. If hints are
                             enabled, then there will be hints for which
                             trials need to be completed.
                             ''',
            gui_dependency = lambda settings: 0 if settings.trials_random else None,
            shared         = True,
            ),
    Checkbutton(
            name           = 'no_escape_sequence',
            args_help      = '''\
                             The tower escape sequence between Ganondorf and Ganon will be skipped.
                             ''',
            gui_text       = 'Skip Tower Escape Sequence',
            gui_group      = 'convenience',
            gui_tooltip    = '''\
                             The tower escape sequence between
                             Ganondorf and Ganon will be skipped.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'no_guard_stealth',
            args_help      = '''\
                             The crawlspace into Hyrule Castle will take you straight to Zelda.
                             ''',
            gui_text       = 'Skip Child Stealth',
            gui_group      = 'convenience',
            gui_tooltip    = '''\
                             The crawlspace into Hyrule Castle goes
                             straight to Zelda, skipping the guards.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'no_epona_race',
            args_help      = '''\
                             Having Epona's Song will allow you to summon Epona without racing Ingo.
                             ''',
            gui_text       = 'Skip Epona Race',
            gui_group      = 'convenience',
            gui_tooltip    = '''\
                             Epona can be summoned with Epona's Song
                             without needing to race Ingo.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'fast_chests',
            args_help      = '''\
                             Makes all chests open without the large chest opening cutscene.
                             ''',
            gui_text       = 'Fast Chest Cutscenes',
            gui_group      = 'convenience',
            gui_tooltip    = '''\
                             All chest animations are fast. If disabled,
                             the animation time is slow for major items.
                             ''',
            default        = True,
            shared         = True,
            ),
    Checkbutton(
            name           = 'logic_no_night_tokens_without_suns_song',
            args_help      = '''\
                             You will not be expected to collect nighttime-only skulltulas
                             unless you have Sun's Song
                             ''',
            gui_text       = 'Nighttime Skulltulas Expect Sun\'s Song',
            gui_group      = 'convenience',
            gui_tooltip    = '''\
                             GS Tokens that can only be obtained
                             during the night expect you to have Sun's
                             Song to collect them. This prevents needing
                             to wait until night for some locations.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'free_scarecrow',
            args_help      = '''\
                             Scarecrow's Song is no longer needed to summon Pierre.
                             ''',
            gui_text       = 'Free Scarecrow\'s Song',
            gui_group      = 'convenience',
            gui_tooltip    = '''\
                             Pulling out the Ocarina near a
                             spot at which Pierre can spawn will
                             do so, without needing the song.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'start_with_fast_travel',
            args_help      = '''\
                             Start with two warp songs and Farore's Wind.
                             ''',
            gui_text       = 'Start with Fast Travel',
            gui_group      = 'convenience',
            gui_tooltip    = '''\
                             Start the game with Prelude of Light,
                             Serenade of Water, and Farore's Wind.
                             
                             Two song locations will give items,
                             instead of Prelude and Serenade.
                             ''',
            shared         = True,
            ),            
    Checkbutton(
            name           = 'start_with_rupees',
            args_help      = '''\
                             Start with 99 rupees.
                             ''',
            gui_text       = 'Start with Max Rupees',
            gui_group      = 'convenience',
            gui_tooltip    = '''\
                             Start the game with 99 rupees.
                             ''',
            shared         = True,
            ),         
    Checkbutton(
            name           = 'start_with_wallet',
            args_help      = '''\
                             Start with Tycoon's Wallet.
                             ''',
            gui_text       = 'Start with Tycoon\'s Wallet',
            gui_group      = 'convenience',
            gui_tooltip    = '''\
                             Start the game with the largest wallet (999 max).
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'start_with_deku_equipment',
            args_help      = '''\
                             Start with full Deku sticks, nuts, and a shield.
                             ''',
            gui_text       = 'Start with Deku Equipment',
            gui_group      = 'convenience',
            gui_tooltip    = '''\
                             Start the game with 10 Deku sticks and 20 Deku nuts.
                             Additionally, start the game with a Deku shield equipped,
                             unless playing with the Shopsanity setting.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'big_poe_count_random',
            args_help      = '''\
                             Sets a random number of Big Poes to receive an item from the buyer.
                             ''',
            gui_text       = 'Random Big Poe Target Count',
            gui_group      = 'convenience',
            gui_tooltip    = '''\
                             The Poe buyer will give a reward for turning
                             in a random number of Big Poes.
                             ''',
            shared         = True,
            ),
    Scale(
            name           = 'big_poe_count',
            default        = 10,
            min            = 1,
            max            = 10,
            args_help      = '''\
                             Select the number of Big Poes to receive an item from the buyer.
                             ''',
            gui_group      = 'convenience',
            gui_tooltip    = '''\
                             The Poe buyer will give a reward for turning
                             in the chosen number of Big Poes.
                             ''',
            gui_dependency = lambda settings: 1 if settings.big_poe_count_random else None,
            shared         = True,
            ),
    Checkbutton(
            name           = 'shuffle_kokiri_sword',
            args_help      = '''\
                             Shuffles the Kokiri Sword into the pool.
                             ''',
            gui_text       = 'Shuffle Kokiri Sword',
            gui_group      = 'shuffle',
            gui_tooltip    = '''\
                             Enabling this shuffles the Kokiri Sword into the pool.
                             
                             This will require extensive use of sticks until the
                             sword is found.
                             ''',
            default        = True,
            shared         = True,
            ),
    Checkbutton(
            name           = 'shuffle_ocarinas',
            args_help      = '''\
                             Shuffles the Fairy Ocarina and the Ocarina of Time into the pool.
                             ''',
            gui_text       = 'Shuffle Ocarinas',
            gui_group      = 'shuffle',
            gui_tooltip    = '''\
                             Enabling this shuffles the Fairy Ocarina and the Ocarina
                             of Time into the pool.
                             
                             This will require finding an Ocarina before being able
                             to play songs.
                             ''',
            default        = True,
            shared         = True,
            ),
    Checkbutton(
            name           = 'shuffle_weird_egg',
            args_help      = '''\
                             Shuffles the Weird Egg from Malon into the pool.
                             ''',
            gui_text       = 'Shuffle Weird Egg',
            gui_group      = 'shuffle',
            gui_tooltip    = '''\
                             Enabling this shuffles the Weird Egg from Malon into the pool.
                             
                             This will require finding the Weird Egg to talk to Zelda in 
                             Hyrule Castle, which in turn locks rewards from Impa, Saria,
                             Malon, and Talon, as well as the Happy Mask sidequest.
                             If Open Kakariko Gate is disabled, the Weird Egg will also
                             be required for Zelda's Letter to open the gate as child.
                             ''',
            default        = True,
            shared         = True,
            ),
    Checkbutton(
            name           = 'shuffle_gerudo_card',
            args_help      = '''\
                             Shuffles the Gerudo Card into the pool.
                             ''',
            gui_text       = 'Shuffle Gerudo Card',
            gui_group      = 'shuffle',
            gui_tooltip    = '''\
                             Enabling this shuffles the Gerudo Card into the item pool.
                             
                             The Gerudo Card is required to enter the Gerudo Training Grounds,
                             however it does not prevent the guards throwing you in jail.
                             This has no effect if the option to Start with Gerudo Card is set.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'shuffle_song_items',
            args_help      = '''\
                             Shuffles the songs into the rest of the item pool so that
                             they can appear at other locations and items can appear at
                             the song locations.
                             ''',
            gui_text       = 'Shuffle Songs with Items',
            gui_group      = 'shuffle',
            gui_tooltip    = '''\
                             Enabling this shuffles the songs into the rest of the
                             item pool.
                             
                             This means that song locations can contain other items,
                             and any location can contain a song. Otherwise, songs
                             are only shuffled among themselves.
                             ''',
            default        = True,
            shared         = True,
            ),
    Combobox(
            name           = 'shuffle_scrubs',
            default        = 'off',
            choices        = {
                'off':     'Off',
                'low':     'On (Affordable)',
                'regular': 'On (Expensive)',
                'random':  'On (Random Prices)',
                },
            args_help      = '''\
                             Deku Scrub Salesmen are randomized:
                             off:        Only the 3 Scrubs that give one-time items
                                         in the vanilla game will have random items.
                             low:        All Scrubs will have random items and their
                                         prices will be reduced to 10 rupees each.
                             regular:    All Scrubs will have random items and each
                                         of them will demand their vanilla prices.
                             random:     All Scrubs will have random items and their
                                         price will also be random between 10-99 rupees.
                             ''',
            gui_text       = 'Scrub Shuffle',
            gui_group      = 'shuffle',
            gui_tooltip    = '''\
                             'Off': Only the 3 Scrubs that give one-time
                             items in the vanilla game (PoH, Deku Nut
                             capacity, and Deku Stick capacity) will
                             have random items.
        
                             'Affordable': All Scrub prices will be
                             reduced to 10 rupees each.
        
                             'Expensive': All Scrub prices will be
                             their vanilla prices. This will require
                             spending over 1000 rupees on Scrubs.
        
                             'Random Prices': All Scrub prices will be
                             between 0-99 rupees. This will on average
                             be very, very expensive overall.
        
                             The texts of the Scrubs are not updated.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'shopsanity',
            default        = 'off',
            choices        = {
                'off':    'Off',
                '0':      'Shuffled Shops (0 Items)',
                '1':      'Shuffled Shops (1 Items)',
                '2':      'Shuffled Shops (2 Items)',
                '3':      'Shuffled Shops (3 Items)',
                '4':      'Shuffled Shops (4 Items)',
                'random': 'Shuffled Shops (Random)',
                },
            args_help      = '''\
                             Shop contents are randomized. Non-shop items
                             are one time purchases. This setting also
                             changes the item pool to introduce a new Wallet
                             upgrade and more money.
                             off:        Normal Shops*
                             0-4:        Shop contents are shuffled and N non-shop
                                         items are added to every shop. So more
                                         possible item locations.
                             random:     Shop contents are shuffles and each shop
                                         will have a random number of non-shop items
                             ''',
            gui_text       = 'Shopsanity',
            gui_group      = 'shuffle',
            gui_tooltip    = '''\
                             Shop contents are randomized.
                             (X Items): Shops have X random non-shop (Special
                             Deal!) items. They will always be on the left
                             side, and some of the lower value shop items
                             will be replaced to make room for these.
        
                             (Random): Each shop will have a random number
                             of non-shop items up to a maximum of 4.
        
                             The non-shop items have no requirements except
                             money, while the normal shop items (such as
                             200/300 rupee tunics) have normal vanilla
                             requirements. This means that, for example,
                             as a child you cannot buy 200/300 rupee
                             tunics, but you can buy non-shop tunics.
        
                             Non-shop Bombchus will unlock the chu slot
                             in your inventory, which, if Bombchus are in
                             logic, is needed to buy Bombchu refills.
                             Otherwise, the Bomb Bag is required.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'tokensanity',
            default        = 'off',
            choices        = {
                'off':      'Off',
                'dungeons': 'Dungeons Only',
                'all':      'All Tokens',
                },
            args_help      = '''\
                             Gold Skulltula Tokens will be shuffled into the pool,
                             and Gold Skulltula locations can have any item.
                             off:        Don't use this feature
                             dungeons:   Only dungeon Skulltulas will be shuffled
                             all:        All Gold Skulltulas will be shuffled
                             ''',
            gui_text       = 'Tokensanity',
            gui_group      = 'shuffle',
            gui_tooltip    = '''\
                             Token reward from Gold Skulltulas are
                             shuffled into the pool.
        
                             'Dungeons Only': This only shuffles
                             the GS locations that are within
                             dungeons, increasing the value of
                             most dungeons and making internal
                             dungeon exploration more diverse.
        
                             'All Tokens': Effectively adds 100
                             new locations for items to appear.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'shuffle_mapcompass',
            default        = 'dungeon',
            choices        = {
                'remove':    'Maps/Compasses: Remove',
                'startwith': 'Maps/Compasses: Start With',
                'dungeon':   'Maps/Compasses: Dungeon Only',
                'keysanity': 'Maps/Compasses: Anywhere'
                },
            args_help      = '''\
                             Sets the Map and Compass placement rules
                             remove:      Maps and Compasses are removed from the world.
                             startwith:   Start with all Maps and Compasses.
                             dungeon:     Maps and Compasses are put in their dungeon.
                             keysanity:   Maps and Compasses can appear anywhere.
                             ''',
            gui_text       = 'Shuffle Dungeon Items',
            gui_group      = 'shuffle',
            gui_tooltip    = '''\
                             'Remove': Maps and Compasses are removed.
                             This will add a small amount of money and
                             refill items to the pool.
        
                             'Start With': Maps and Compasses are given to
                             you from the start. This will add a small
                             amount of money and refill items to the pool.
        
                             'Dungeon': Maps and Compasses can only appear
                             in their respective dungeon.
        
                             'Anywhere': Maps and Compasses can appear
                             anywhere in the world.
        
                             Setting 'Remove', 'Start With, or 'Anywhere' will
                             add 2 more possible locations to each Dungeons.
                             This makes dungeons more profitable, especially
                             Ice Cavern, Water Temple, and Jabu Jabu's Belly.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'shuffle_smallkeys',
            default        = 'dungeon',
            choices        = {
                'remove':    'Small Keys: Remove (Keysy)',
                'dungeon':   'Small Keys: Dungeon Only',
                'keysanity': 'Small Keys: Anywhere (Keysanity)'
                },
            args_help      = '''\
                             Sets the Small Keys placement rules
                             remove:      Small Keys are removed from the world.
                             dungeon:     Small Keys are put in their dungeon.
                             keysanity:   Small Keys can appear anywhere.
                             ''',
            gui_group      = 'shuffle',
            gui_tooltip    = '''\
                             'Remove': Small Keys are removed. All locked
                             doors in dungeons will be unlocked. An easier
                             mode.
        
                             'Dungeon': Small Keys can only appear in their
                             respective dungeon. If Fire Temple is not a
                             Master Quest dungeon, the door to the Boss Key
                             chest will be unlocked
        
                             'Anywhere': Small Keys can appear
                             anywhere in the world. A difficult mode since
                             it is more likely to need to enter a dungeon
                             multiple times.
        
                             Try different combination out, such as:
                             'Small Keys: Dungeon' + 'Boss Keys: Anywhere'
                             for a milder Keysanity experience.
                             ''',
            shared=True,
    ),
    Combobox(
            name           = 'shuffle_bosskeys',
            default        = 'dungeon',
            choices        = {
                'remove':    'Boss Keys: Remove (Keysy)',
                'dungeon':   'Boss Keys: Dungeon Only',
                'keysanity': 'Boss Keys: Anywhere (Keysanity)',
                },
            args_help      = '''\
                             Sets the Boss Keys placement rules
                             remove:      Boss Keys are removed from the world.
                             dungeon:     Boss Keys are put in their dungeon.
                             keysanity:   Boss Keys can appear anywhere.
                             ''',
            gui_group      = 'shuffle',
            gui_tooltip    = '''\
                             'Remove': Boss Keys are removed. All locked
                             doors in dungeons will be unlocked. An easier
                             mode.
        
                             'Dungeon': Boss Keys can only appear in their
                             respective dungeon.
        
                             'Anywhere': Boss Keys can appear
                             anywhere in the world. A difficult mode since
                             it is more likely to need to enter a dungeon
                             multiple times.
        
                             Try different combination out, such as:
                             'Small Keys: Dungeon' + 'Boss Keys: Anywhere'
                             for a milder Keysanity experience.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'enhance_map_compass',
            args_help      = '''\
                             Gives the Map and Compass extra functionality.
                             Map will tell if a dungeon is vanilla or Master Quest.
                             Compass will tell what medallion or stone is within.
                             The Temple of Time Altar will no longer provide any
                             information. If the maps and compasses are removed then
                             the information will be unavailable.
                             ''',
            gui_text       = 'Maps and Compasses Give Information',
            gui_group      = 'shuffle',
            gui_tooltip    = '''\
                           Gives the Map and Compass extra functionality.
                           Map will tell if a dungeon is vanilla or Master Quest.
                           Compass will tell what medallion or stone is within.
                           The Temple of Time Altar will no longer provide any
                           information.
        
                           'Maps/Compasses: Remove': The dungeon information is
                           not available anywhere in the game.
        
                           'Maps/Compasses: Start With': The dungeon information
                           is available immediately from the dungeon menu.
                             ''',
            default        = False,
            shared         = True,
            ),
    Checkbutton(
            name           = 'unlocked_ganondorf',
            args_help      = '''\
                             The Boss Key door in Ganon's Tower will start unlocked.
                             ''',
            gui_text       = 'Remove Ganon\'s Boss Door Lock',
            gui_group      = 'shuffle',
            gui_tooltip    = '''\
                             The Boss Key door in Ganon's Tower
                             will start unlocked. This is intended
                             to be used with reduced trial
                             requirements to make it more likely
                             that skipped trials can be avoided.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'mq_dungeons_random',
            args_help      = '''\
                             If set, a uniformly random number of dungeons will have Master Quest designs.
                             ''',
            gui_text       = 'Random Number of MQ Dungeons',
            gui_group      = 'world',
            gui_tooltip    = '''\
                             If set, a random number of dungeons
                             will have Master Quest designs.
                             ''',
            shared         = True,
            ),
    Scale(
            name           = 'mq_dungeons',
            default        = 0,
            min            = 0,
            max            = 12,
            args_help      = '''\
                             Select a number (0-12) of Master Quest dungeons to appear in the game.
                             0:  (default) All dungeon will have their original designs.
                             ...
                             6:  50/50 split; Half of all dungeons will be from Master Quest.
                             ...
                             12: All dungeons will have Master Quest redesigns.
                             ''',
            gui_group      = 'world',
            gui_tooltip    = '''\
                             Select a number of Master Quest
                             dungeons to appear in the game.

                             0: All dungeon will have their
                             original designs. (default)

                             6: Half of all dungeons will
                             be from Master Quest.

                             12: All dungeons will have
                             Master Quest redesigns.
                             ''',
            gui_dependency = lambda settings: 0 if settings.mq_dungeons_random else None,
            shared         = True,
            ),
    Setting_Info('disabled_locations', list, math.ceil(math.log(len(location_table) + 2, 2)), True,
        {
            'default': [],
            'help': '''\
                    Choose a list of locations that will never be required to beat the game.
                    '''
        },
        {
            'text': 'Exclude Locations',
            'widget': 'SearchBox',
            'group': 'logic_tab',
            'options': list(location_table.keys()),
            'tooltip':'''
                    Prevent locations from being required. Major 
                    items can still appear there, however they 
                    will never be required to beat the game.

                    Most dungeon locations have a MQ alternative.
                    If the location does not exist because of MQ
                    then it will be ignored. So make sure to
                    disable both versions if that is the intent.
                '''
        }),
    Setting_Info('allowed_tricks', list, math.ceil(math.log(len(logic_tricks) + 2, 2)), True,
        {
            'default': [],
            'help': '''\
                    Choose a list of allowed logic tricks logic may expect to beat the game.
                    '''
        },
        {
            'text': 'Enable Tricks',
            'widget': 'SearchBox',
            'group': 'logic_tab',
            'options': {gui_text: val['name'] for gui_text, val in logic_tricks.items()},
            'entry_tooltip': logic_tricks_entry_tooltip,
            'list_tooltip': logic_tricks_list_tooltip,
        }),
    Combobox(
            name           = 'logic_earliest_adult_trade',
            default        = 'pocket_egg',
            choices        = {
                'pocket_egg':   'Earliest: Pocket Egg',
                'pocket_cucco': 'Earliest: Pocket Cucco',
                'cojiro':       'Earliest: Cojiro',
                'odd_mushroom': 'Earliest: Odd Mushroom',
                'poachers_saw': "Earliest: Poacher's Saw",
                'broken_sword': 'Earliest: Broken Sword',
                'prescription': 'Earliest: Prescription',
                'eyeball_frog': 'Earliest: Eyeball Frog',
                'eyedrops':     'Earliest: Eyedrops',
                'claim_check':  'Earliest: Claim Check',
                },
            args_help      = '''\
                             Select the earliest item that can appear in the adult trade sequence:
                             'pocket_egg'
                             'pocket_cucco'
                             'cojiro'
                             'odd_mushroom'
                             'poachers_saw'
                             'broken_sword'
                             'prescription'
                             'eyeball_frog'
                             'eyedrops'
                             'claim_check'
                             ''',
            gui_group      = 'checks',
            gui_tooltip    = '''\
                             Select the earliest item that can appear in the adult trade sequence.
                             ''',
            shared         = True,
            ),    
    Combobox(
            name           = 'logic_latest_adult_trade',
            default        = 'claim_check',
            choices        = {
                'pocket_egg':   'Latest: Pocket Egg',
                'pocket_cucco': 'Latest: Pocket Cucco',
                'cojiro':       'Latest: Cojiro',
                'odd_mushroom': 'Latest: Odd Mushroom',
                'poachers_saw': "Latest: Poacher's Saw",
                'broken_sword': 'Latest: Broken Sword',
                'prescription': 'Latest: Prescription',
                'eyeball_frog': 'Latest: Eyeball Frog',
                'eyedrops':     'Latest: Eyedrops',
                'claim_check':  'Latest: Claim Check',
                },
            args_help      = '''\
                             Select the latest item that can appear in the adult trade sequence:
                             'pocket_egg'
                             'pocket_cucco'
                             'cojiro'
                             'odd_mushroom'
                             'poachers_saw'
                             'broken_sword'
                             'prescription'
                             'eyeball_frog'
                             'eyedrops'
                             'claim_check'
                             ''',
            gui_group      = 'checks',
            gui_tooltip    = '''\
                             Select the latest item that can appear in the adult trade sequence.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'logic_lens',
            default        = 'all',
            choices        = {
                'all':             'Required Everywhere',
                'chest-wasteland': 'Wasteland and Chest Minigame',
                'chest':           'Only Chest Minigame',
                },
            args_help      = '''\
                             Choose what expects the Lens of Truth:
                             all:              All lens spots expect the lens (except those that did not in the original game)
                             chest-wasteland:  Only wasteland and chest minigame expect the lens
                             chest:            Only the chest minigame expects the lens
                             ''',
            gui_group      = 'tricks',
            gui_tooltip    = '''\
                             'Required everywhere': every invisible or
                             fake object will expect you to have the
                             Lens of Truth and Magic. The exception is
                             passing through the first wall in Bottom of
                             the Well, since that is required in vanilla.
        
                             'Wasteland': The lens is needed to follow
                             the ghost guide across the Haunted Wasteland.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'ocarina_songs',
            args_help      = '''\
                             Randomizes the notes needed to play each ocarina song.
                             ''',
            gui_text       = 'Randomize Ocarina Song Notes',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             Will need to memorize a new set of songs.
                             Can be silly, but difficult. Songs are
                             generally sensible, and warp songs are
                             typically more difficult.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'correct_chest_sizes',
            args_help      = '''\
                             Updates the chest sizes to match their contents.
                             Small Chest = Non-required Item
                             Big Chest = Progression Item
                             ''',
            gui_text       = 'Chest Size Matches Contents',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             Chests will be large if they contain a major
                             item and small if they don't. Boss keys will
                             be in gold chests. This allows skipping
                             chests if they are small. However, skipping
                             small chests will mean having low health,
                             ammo, and rupees, so doing so is a risk.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'clearer_hints',
            args_help      = '''\
                             The hints provided by Gossip Stones are
                             very direct.
                             ''',
            gui_text       = 'Clearer Hints',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             The hints provided by Gossip Stones will
                             be very direct if this option is enabled.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'hints',
            default        = 'agony',
            choices        = {
                'none':   'No Hints',
                'mask':   'Hints; Need Mask of Truth',
                'agony':  'Hints; Need Stone of Agony',
                'always': 'Hints; Need Nothing',
                },
            args_help      = '''\
                             Choose how Gossip Stones behave
                             none:   Default behavior
                             mask:   Have useful hints that are read with the Mask of Truth.
                             agony:  Have useful hints that are read with Stone of Agony.
                             always: Have useful hints which can always be read.
                             ''',
            gui_text       = 'Gossip Stones',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             Gossip Stones can be made to give hints
                             about where items can be found.
        
                             Different settings can be chosen to
                             decide which item is needed to
                             speak to Gossip Stones. Choosing to
                             stick with the Mask of Truth will
                             make the hints very difficult to
                             obtain.
        
                             Hints for 'on the way of the hero' are
                             locations that contain items that are
                             required to beat the game.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'hint_dist',
            default        = 'balanced',
            choices        = {
                'useless':     'Useless',
                'balanced':    'Balanced',
                'strong':      'Strong',
                'very_strong': 'Very Strong',
                'tournament':  'Tournament',
                },
            args_help      = '''\
                             Choose how Gossip Stones hints are distributed
                             useless: Nothing but junk hints.
                             balanced: Use a balanced distribution of hint types
                             strong: Use a strong distribution of hint types
                             very_strong: Use a very strong distribution of hint types
                             tournament: Similar to strong but has no variation in hint types
                             ''',
            gui_text       = 'Hint Distribution',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             Useless has nothing but junk
                             hints.
                             Strong distribution has some
                             duplicate hints and no junk
                             hints.
                             Very Strong distribution has
                             only very useful hints.
                             Tournament distribution is
                             similar to Strong but with no
                             variation in hint types.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'text_shuffle',
            default        = 'none',
            choices        = {
                'none':         'No Text Shuffled',
                'except_hints': 'Shuffled except Hints and Keys',
                'complete':     'All Text Shuffled',
                },
            args_help      = '''\
                             Choose how to shuffle the game's messages.
                             none:          Default behavior
                             except_hints:  All non-useful text is shuffled.
                             complete:      All text is shuffled.
                             ''',
            gui_text       = 'Text Shuffle',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             Will make things confusing for comedic value.
        
                             'Shuffled except Hints and Keys': Key texts
                             are not shuffled because in keysanity it is
                             inconvenient to figure out which keys are which
                             without the correct text. Similarly, non-shop
                             items sold in shops will also retain standard
                             text for the purpose of accurate price checks.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'junk_ice_traps',
            default        = 'normal',
            choices        = {
                'off':       'No Ice Traps',
                'normal':    'Normal Ice Traps',
                'on':        'Extra Ice Traps',
                'mayhem':    'Ice Trap Mayhem',
                'onslaught': 'Ice Trap Onslaught',
                },
            args_help      = '''\
                             Choose how Ice Traps will be placed in the junk item pool
                             off:       Ice traps are removed.
                             normal:    Default behavior; no ice traps in the junk item pool.
                             on:        Ice Traps will be placed in the junk item pool.
                             mayhem:    All added junk items will be ice traps.
                             onslaught: All junk items will be ice traps, even those in the base item pool.
                             ''',
            gui_text       = 'Ice Traps',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             Off: All Ice Traps are removed.
                             Normal: Only Ice Traps from the base item pool
                             are placed.
                             Extra Ice Traps: Chance to add extra Ice Traps
                             when junk items are added to the itempool.
                             Ice Trap Mayhem: All added junk items will
                             be Ice Traps.
                             Ice Trap Onslaught: All junk items will be
                             replaced by Ice Traps, even those in the
                             base pool.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'item_pool_value',
            default        = 'balanced',
            choices        = {
                'plentiful': 'Plentiful',
                'balanced':  'Balanced',
                'scarce':    'Scarce',
                'minimal':   'Minimal'
                },
            args_help      = '''\
                             Change the item pool for an added challenge.
                             plentiful:      Duplicates most of the major items, making it easier to find progression.
                             balanced:       Default items
                             scarce:         Double defense, double magic, and all 8 heart containers are removed. Ammo
                                             for each type can only be expanded once and you can only find three Bombchu packs.
                             minimal:        Double defense, double magic, Nayru's Love, and all health upgrades are removed.
                                             No ammo expansions are available and you can only find one Bombchu pack.
                             ''',
            gui_text       = 'Item Pool',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             Changes the amount of bonus items that
                             are available in the game.
        
                             'Plentiful': Extra major items are added.
        
                             'Balanced': Original item pool.
        
                             'Scarce': Some excess items are removed,
                             including health upgrades.
        
                             'Minimal': Most excess items are removed.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'damage_multiplier',
            default        = 'normal',
            choices        = {
                'half':      'Half',
                'normal':    'Normal',
                'double':    'Double',
                'quadruple': 'Quadruple',
                'ohko':      'OHKO',
                },
            args_help      = '''\
                             Change the amount of damage taken.
                             half:           Half damage taken.
                             normal:         Normal damage taken.
                             double:         Double damage taken.
                             quadruple:      Quadruple damage taken.
                             ohko:           Link will die in one hit.
                             ''',
            gui_text       = 'Damage Multiplier',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             Changes the amount of damage taken.
        
                             'OHKO': Link dies in one hit.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'starting_tod',
            default        = 'default',
            choices        = {
                'default':       'Default',
                'random':        'Random Choice',
                'early-morning': 'Early Morning',
                'morning':       'Morning',
                'noon':          'Noon',
                'afternoon':     'Afternoon',
                'evening':       'Evening',
                'dusk':          'Dusk',
                'midnight':      'Midnight',
                'witching-hour': 'Witching Hour',
                },
            args_help      = '''\
                             Change up Link's sleep routine.

                             Daytime officially starts at 6:30,
                             nighttime at 18:00 (6:00 PM).

                             Default is 10:00 in the morning.
                             The alternatives are multiples of 3 hours.
                             ''',
            gui_text       = 'Starting Time of Day',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             Change up Link's sleep routine.

                             Daytime officially starts at 6:30,
                             nighttime at 18:00 (6:00 PM).

                             Default is 10:00 in the morning.
                             The alternatives are multiples of 3 hours.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'default_targeting',
            default        = 'hold',
            choices        = {
                'hold':   'Hold',
                'switch': 'Switch',
                },
            args_help      = '''\
                             Choose what the default Z-targeting is.
                             ''',
            gui_text       = 'Default Targeting Option',
            gui_group      = 'cosmetic',
            ),
    Combobox(
            name           = 'background_music',
            default        = 'normal',
            choices        = {
                'normal': 'Normal',
                'off':    'No Music',
                'random': 'Random',
                },
            args_help      = '''\
                             Sets the background music behavior
                             normal:      Areas play their normal background music
                             off:         No background music
                             random:      Areas play random background music
                             ''',
            gui_text       = 'Background Music',
            gui_group      = 'sfx',
            gui_tooltip    = '''\
                              'No Music': No background music.
                              is played.
        
                              'Random': Area background music is
                              randomized.
                             ''',
            ),

    Checkbutton(
            name           = 'display_dpad',
            args_help      = '''\
                             Shows an additional HUD element displaying current available options on the DPAD
                             ''',
            gui_text       = 'Display D-Pad HUD',
            gui_group      = 'cosmetic',
            gui_tooltip    = '''\
                             Shows an additional HUD element displaying
                             current available options on the D-Pad.
                             ''',
            default        = True,
            ),
    Setting_Info('kokiri_color', str, 0, False,
        {
            'default': 'Kokiri Green',
            'type': parse_custom_tunic_color,
            'help': '''\
                    Choose the color for Link's Kokiri Tunic. (default: %(default)s)
                    Color:              Make the Kokiri Tunic this color.
                    Random Choice:      Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Kokiri Tunic',
            'group': 'tunic_colors',
            'widget': 'Combobox',
            'default': 'Kokiri Green',
            'options': get_tunic_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('goron_color', str, 0, False,
        {
            'default': 'Goron Red',
            'type': parse_custom_tunic_color,
            'help': '''\
                    Choose the color for Link's Goron Tunic. (default: %(default)s)
                    Color:              Make the Goron Tunic this color.
                    Random Choice:      Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Goron Tunic',
            'group': 'tunic_colors',
            'widget': 'Combobox',
            'default': 'Goron Red',
            'options': get_tunic_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('zora_color', str, 0, False,
        {
            'default': 'Zora Blue',
            'type': parse_custom_tunic_color,
            'help': '''\
                    Choose the color for Link's Zora Tunic. (default: %(default)s)
                    Color:              Make the Zora Tunic this color.
                    Random Choice:      Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Zora Tunic',
            'group': 'tunic_colors',
            'widget': 'Combobox',
            'default': 'Zora Blue',
            'options': get_tunic_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('navi_color_default', str, 0, False,
        {
            'default': 'White',
            'type': parse_custom_navi_color,
            'help': '''\
                    Choose the color for Navi when she is idle. (default: %(default)s)
                    Color:             Make the Navi this color.
                    Random Choice:     Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Navi Idle',
            'group': 'navi_colors',
            'widget': 'Combobox',
            'default': 'White',
            'options': get_navi_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('navi_color_enemy', str, 0, False,
        {
            'default': 'Yellow',
            'type': parse_custom_navi_color,
            'help': '''\
                    Choose the color for Navi when she is targeting an enemy. (default: %(default)s)
                    Color:             Make the Navi this color.
                    Random Choice:     Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Navi Targeting Enemy',
            'group': 'navi_colors',
            'widget': 'Combobox',
            'default': 'Yellow',
            'options': get_navi_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('navi_color_npc', str, 0, False,
        {
            'default': 'Light Blue',
            'type': parse_custom_navi_color,
            'help': '''\
                    Choose the color for Navi when she is targeting an NPC. (default: %(default)s)
                    Color:             Make the Navi this color.
                    Random Choice:     Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Navi Targeting NPC',
            'group': 'navi_colors',
            'widget': 'Combobox',
            'default': 'Light Blue',
            'options': get_navi_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('navi_color_prop', str, 0, False,
        {
            'default': 'Green',
            'type': parse_custom_navi_color,
            'help': '''\
                    Choose the color for Navi when she is targeting a prop. (default: %(default)s)
                    Color:             Make the Navi this color.
                    Random Choice:     Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Navi Targeting Prop',
            'group': 'navi_colors',
            'widget': 'Combobox',
            'default': 'Green',
            'options': get_navi_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      '''
        }),
    Combobox(
            name           = 'sword_trail_duration',
            default        = 4,
            choices        = {
                    4: 'Default',
                    10: 'Long',
                    15: 'Very Long',
                    20: 'Lightsaber',
                 },
            args_help      = '''\
                             Select the duration of the sword trail
                             ''',
            gui_text       = 'Sword Trail Duration',
            gui_group      = 'sword_trails',
            gui_tooltip    = '''\
                             Select the duration for sword trails.
                             ''',
            ),
    Setting_Info('sword_trail_color_inner', str, 0, False,
        {
            'default': 'White',
            'type': parse_custom_sword_color,
            'help': '''\
                    Choose the color for your sword trail when you swing. This controls the inner color. (default: %(default)s)
                    Color:             Make your sword trail this color.
                    Random Choice:     Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    Rainbow:           Rainbow sword trails.

                    '''
        },
        {
            'text': 'Inner Color',
            'group': 'sword_trails',
            'widget': 'Combobox',
            'default': 'White',
            'options': get_sword_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      'Rainbow': Rainbow sword trails.
                      '''
        }),
    Setting_Info('sword_trail_color_outer', str, 0, False,
        {
            'default': 'White',
            'type': parse_custom_sword_color,
            'help': '''\
                    Choose the color for your sword trail when you swing. This controls the outer color. (default: %(default)s)
                    Color:             Make your sword trail this color.
                    Random Choice:     Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    Rainbow:           Rainbow sword trails.
                    '''
        },
        {
            'text': 'Outer Color',
            'group': 'sword_trails',
            'widget': 'Combobox',
            'default': 'White',
            'options': get_sword_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      'Rainbow': Rainbow sword trails.
                      '''
        }),
    Combobox(
            name           = 'sfx_low_hp',
            default        = 'default',
            choices        = sfx.get_setting_choices(sfx.SoundHooks.HP_LOW),
            args_help      = '''\
                             Select the sound effect that loops at low health. (default: %(default)s)
                             Sound:         Replace the sound effect with the chosen sound.
                             Random Choice: Replace the sound effect with a random sound from this list.
                             None:          Eliminate heart beeps.
                             ''',
            gui_text       = 'Low HP',
            gui_group      = 'sfx',
            gui_tooltip    = '''\
                             'Random Choice': Choose a random
                             sound from this list.
                             'Default': Beep. Beep. Beep.
                             ''',
            ),
    Setting_Info('silver_gauntlets_color', str, 0, False,
        {
            'default': 'Silver',
            'type': parse_custom_gauntlet_color,
            'help': '''\
                    Choose the color for Link's Silver Gauntlets. (default: %(default)s)
                    Color:              Make the Silver Gauntlets this color.
                    Random Choice:      Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Silver Gauntlets',
            'group': 'gauntlet_colors',
            'widget': 'Combobox',
            'default': 'Silver',
            'options': get_gauntlet_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('golden_gauntlets_color', str, 0, False,
        {
            'default': 'Gold',
            'type': parse_custom_gauntlet_color,
            'help': '''\
                    Choose the color for Link's Golden Gauntlets. (default: %(default)s)
                    Color:              Make the Golden Gauntlets this color.
                    Random Choice:      Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Golden Gauntlets',
            'group': 'gauntlet_colors',
            'widget': 'Combobox',
            'default': 'Gold',
            'options': get_gauntlet_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      '''
        }),
    Combobox(
            name           = 'sfx_navi_overworld',
            default        = 'default',
            choices        = sfx.get_setting_choices(sfx.SoundHooks.NAVI_OVERWORLD),
            args_help      = '''\
                             ''',
            gui_text       = 'Navi Overworld',
            gui_group      = 'npc_sfx',
            ),
    Combobox(
            name           = 'sfx_navi_enemy',
            default        = 'default',
            choices        = sfx.get_setting_choices(sfx.SoundHooks.NAVI_ENEMY),
            args_help      = '''\
                             ''',
            gui_text       = 'Navi Enemy',
            gui_group      = 'npc_sfx',
            ),
    Combobox(
            name           = 'sfx_menu_cursor',
            default        = 'default',
            choices        = sfx.get_setting_choices(sfx.SoundHooks.MENU_CURSOR),
            args_help      = '''\
                             ''',
            gui_text       = 'Menu Cursor',
            gui_group      = 'menu_sfx',
            ),
    Combobox(
            name           = 'sfx_menu_select',
            default        = 'default',
            choices        = sfx.get_setting_choices(sfx.SoundHooks.MENU_SELECT),
            args_help      = '''\
                             ''',
            gui_text       = 'Menu Select',
            gui_group      = 'menu_sfx',
            ),
    Combobox(
            name           = 'sfx_horse_neigh',
            default        = 'default',
            choices        = sfx.get_setting_choices(sfx.SoundHooks.HORSE_NEIGH),
            args_help      = '''\
                             ''',
            gui_text       = 'Horse',
            gui_group      = 'sfx',
            ),
    Combobox(
            name           = 'sfx_nightfall',
            default        = 'default',
            choices        = sfx.get_setting_choices(sfx.SoundHooks.NIGHTFALL),
            args_help      = '''\
                             ''',
            gui_text       = 'Nightfall',
            gui_group      = 'sfx',
            ),
    Combobox(
            name           = 'sfx_hover_boots',
            default        = 'default',
            choices        = sfx.get_setting_choices(sfx.SoundHooks.BOOTS_HOVER),
            args_help      = '''\
                             ''',
            gui_text       = 'Hover Boots',
            gui_group      = 'sfx',
            ),
    Combobox(
            name           = 'sfx_ocarina',
            default        = 'ocarina',
            choices        = {
                'ocarina':     'Default',
                'random':      'Random Choice',
                'flute':       'Flute',
                'harp':        'Harp',
                'whistle':     'Whistle',
                'malon':       'Malon',
                'grind-organ': 'Grind Organ',
                },
            args_help      = '''\
                             Change the sound of the ocarina.

                             default: ocarina
                             ''',
            gui_text       = 'Ocarina',
            gui_group      = 'sfx',
            gui_tooltip    = '''\
                             Change the sound of the ocarina.
                             ''',
            ),
]

si_dict = {si.name: si for si in setting_infos}
def get_setting_info(name):
    return si_dict[name]
