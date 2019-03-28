import argparse
import re
import math
from Cosmetics import get_tunic_color_options, get_navi_color_options, get_sword_color_options, get_gauntlet_color_options, get_magic_color_options, get_heart_color_options
from Location import LocationIterator
import Sounds as sfx

# holds the info for a single setting
class Setting_Info():

    def __init__(self, name, type, shared, choices, default=None, dependency=None, gui_params=None):
        self.name = name # name of the setting, used as a key to retrieve the setting's value everywhere
        self.type = type # type of the setting's value, used to properly convert types in GUI code
        self.bitwidth = self.calc_bitwidth(choices) # number of bits needed to store the setting, used in converting settings to a string
        self.shared = shared # whether or not the setting is one that should be shared, used in converting settings to a string
        if gui_params == None:
            gui_params = {}
        self.gui_params = gui_params # additional parameters that the randomizer uses for the gui
        self.dependency = dependency # lambda that determines if the setting is enabled in the gui

        # dictionary of options to their text names
        if isinstance(choices, list):
            self.choices = {k: k for k in choices}
            self.choice_list = list(choices)
        else:
            self.choices = dict(choices)
            self.choice_list = list(choices.keys())
        self.reverse_choices = {v: k for k, v in self.choices.items()}

        if shared:
            self.bitwidth = self.calc_bitwidth(choices)
        else:
            self.bitwidth = 0

        if default != None:
            self.default = default
        elif self.type == bool:
            self.default = False
        elif self.type == str:
            self.default = ""
        elif self.type == int:
            self.default = 0
        elif self.type == list:
            self.default = []

        if 'distribution' not in gui_params:
            self.gui_params['distribution'] = [(choice, 1) for choice in self.choice_list]


    def calc_bitwidth(self, choices):
        count = len(choices)
        if count > 0:
            return math.ceil(math.log(count, 2))
        return 0


class Checkbutton(Setting_Info):

    def __init__(self, name, gui_text=None, gui_group=None,
            gui_tooltip=None, dependency=None, default=False,
            shared=False, gui_params=None):

        choices = {
            True:  'checked',
            False: 'unchecked',
        }
        if gui_params == None:
            gui_params = {}       
        gui_params['widget'] = 'Checkbutton'
        if gui_text       is not None: gui_params['text']       = gui_text
        if gui_group      is not None: gui_params['group']      = gui_group
        if gui_tooltip    is not None: gui_params['tooltip']    = gui_tooltip

        super().__init__(name, bool, shared, choices, default, dependency, gui_params)


class Combobox(Setting_Info):

    def __init__(self, name, choices, default, gui_text=None,
            gui_group=None, gui_tooltip=None, dependency=None,
            shared=False, gui_params=None):

        if gui_params == None:
            gui_params = {}       
        gui_params['widget'] = 'Combobox'
        if gui_text       is not None: gui_params['text']       = gui_text
        if gui_group      is not None: gui_params['group']      = gui_group
        if gui_tooltip    is not None: gui_params['tooltip']    = gui_tooltip

        super().__init__(name, str, shared, choices, default, dependency, gui_params)


class Scale(Setting_Info):

    def __init__(self, name, min, max, default, step=1,
            gui_text=None, gui_group=None, gui_tooltip=None,
            dependency=None, shared=False, gui_params=None):

        choices = {
            i: str(i) for i in range(min, max+1, step)
        }
        if gui_params == None:
            gui_params = {}       
        gui_params['min']    = min
        gui_params['max']    = max
        gui_params['step']   = step
        gui_params['widget'] = 'Scale'
        if gui_text       is not None: gui_params['text']       = gui_text
        if gui_group      is not None: gui_params['group']      = gui_group
        if gui_tooltip    is not None: gui_params['tooltip']    = gui_tooltip

        super().__init__(name, int, shared, choices, default, dependency, gui_params)


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
    'Rolling Goron (Hot Rodder Goron) as Child with Strength': {
        'name'    : 'logic_child_rolling_with_strength',
        'tooltip' : '''\
                    Use the bombflower on the stairs or near Medigoron.
                    Timing is tight, especially without backwalking
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
    'Zora\'s Domain Entry with Cucco': {
        'name'    : 'logic_zora_with_cucco',
        'tooltip' : '''\
                    Can fly behind the waterfall with
                    a cucco as child.
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
    'Spirit Temple Shifting Wall with No Additional Items': {
        'name'    : 'logic_spirit_wall',
        'tooltip' : '''\
                    The logic normally guarantees a way of dealing with both
                    the Beamos and the Walltula before climbing the wall.
                    '''},
    'Spirit Temple Main Room GS with Boomerang': {
        'name'    : 'logic_spirit_lobby_gs',
        'tooltip' : '''\
                    Standing on the highest part of the arm of the statue, a
                    precise Boomerang throw can kill and obtain this Gold
                    Skulltula. You must throw the Boomerang slightly off to
                    the side so that it curves into the Skulltula, as aiming
                    directly at it will clank off of the wall in front.
                    '''},
    'Spirit Temple MQ Sun Block Room GS with Boomerang': {
        'name'    : 'logic_spirit_mq_sun_block_gs',
        'tooltip' : '''\
                    Throw the Boomerang in such a way that it
                    curves through the side of the glass block
                    to hit the Gold Skulltula.
                    '''},
    'Jabu MQ Song of Time Block GS with Boomerang': {
        'name'    : 'logic_jabu_mq_sot_gs',
        'tooltip' : '''\
                    Allow the Boomerang to return to you through
                    the Song of Time block to grab the token.
                    '''},
    'Bottom of the Well MQ Dead Hand Freestanding Key with Boomerang': {
        'name'    : 'logic_botw_mq_dead_hand_key',
        'tooltip' : '''\
                    Boomerang can fish the item out of the rubble without
                    needing explosives to blow it up.
                    '''},
    'Fire Temple Flame Wall Maze Skip': {
        'name'    : 'logic_fire_flame_maze',
        'tooltip' : '''\
                    If you move quickly you can sneak past the edge of
                    a flame wall before it can rise up to block you.
                    To do it without taking damage is more precise.
                    '''},
    'Fire Temple MQ Chest Near Boss without Breaking Crate': {
        'name'    : 'logic_fire_mq_near_boss',
        'tooltip' : '''\
                    The hitbox for the torch extends a bit outside of the crate.
                    Shoot a flaming arrow at the side of the crate to light the
                    torch without needing to get over there and break the crate.
                    '''},
    'Fire Temple MQ Boulder Maze Side Room without Box': {
        'name'    : 'logic_fire_mq_maze_side_room',
        'tooltip' : '''\
                    You can walk from the blue switch to the door and
                    quickly open the door before the bars reclose. This
                    skips needing the Hookshot in order to reach a box
                    to place on the switch.
                    '''},
    'Fire Temple MQ Boss Key Chest without Bow': {
        'name'    : 'logic_fire_mq_bk_chest',
        'tooltip' : '''\
                    Din\'s alone can be used to unbar the door to
                    the boss key chest's room thanks to an
                    oversight in the way the game counts how many
                    torches have been lit.
                    '''},
    'Zora\'s River Lower Freestanding PoH as Adult with Nothing': {
        'name'    : 'logic_zora_river_lower',
        'tooltip' : '''\
                    Adult can reach this PoH with a precise jump,
                    no Hover Boots required.
                    '''},
    'Water Temple Cracked Wall with Hover Boots': {
        'name'    : 'logic_water_cracked_wall_hovers',
        'tooltip' : '''\
                    With a midair side-hop while wearing the Hover
                    Boots, you can reach the cracked wall without
                    needing to raise the water up to the middle level.
                    '''},
    'Shadow Temple Freestanding Key with Bombchu': {
        'name'    : 'logic_shadow_freestanding_key',
        'tooltip' : '''\
                    Release the Bombchu with good timing so that
                    it explodes near the bottom of the pot.
                    '''},
    'Adult Meadow Access without Saria\'s or Minuet': {
        'name'    : 'logic_adult_meadow_access',
        'tooltip' : '''\
                    With a specific position and angle, you can
                    backflip over Mido.
                    '''},
    'Reach Volvagia without Hover Boots or Pillar': {
        'name'    : 'logic_volvagia_jump',
        'tooltip' : '''\
                    The Fire Temple Boss Door can be reached with a precise
                    jump. You must be touching the side wall of the room so
                    so that Link will grab the ledge from farther away than
                    is normally possible.
                    '''},
    'Diving in the Lab without Gold Scale': {
        'name'    : 'logic_lab_diving',
        'tooltip' : '''\
                    Remove the Iron Boots in the midst of
                    Hookshotting the underwater crate.
                    '''},
    'Deliver Eye Drops with Bolero of Fire': {
        'name'    : 'logic_biggoron_bolero',
        'tooltip' : '''\
                    If you do not wear the Goron Tunic, the heat timer
                    inside the crater will override the trade item's timer.
                    When you exit to Death Mountain Trail you will have
                    one second to deliver the Eye Drops before the timer
                    expires. It works best if you play Bolero as quickly as
                    possible upon receiving the Eye Drops. If you have few
                    hearts, there is enough time to dip Goron City to
                    refresh the heat timer as long as you've already
                    pulled the block.
                    '''},
    'Wasteland Crossing without Hover Boots or Longshot': {
        'name'    : 'logic_wasteland_crossing',
        'tooltip' : '''\
                    You can beat the quicksand by backwalking across it
                    in a specific way.
                    '''},
    'Desert Colossus Hill GS with Hookshot': {
        'name'    : 'logic_colossus_gs',
        'tooltip' : '''\
                    Somewhat precise. If you kill enough Leevers
                    you can get enough of a break to take some time
                    to aim more carefully.
                    '''},
    'Dodongo\'s Cavern Scarecrow GS with Armos Statue': {
        'name'    : 'logic_dc_scarecrow_gs',
        'tooltip' : '''\
                    You can jump off an Armos Statue to reach the
                    alcove with the Gold Skulltula. It takes quite
                    a long time to pull the statue the entire way.
                    The jump to the alcove can be a pit picky when
                    done as child.
                    '''},
    'Kakariko Tower GS with Jump Slash': {
        'name'    : 'logic_kakariko_tower_gs',
        'tooltip' : '''\
                    Climb the tower as high as you can without
                    touching the Gold Skulltula, then let go and
                    jump slash immediately. You will take fall
                    damage.
                    '''},
    'Lake Hylia Lab Wall GS with Jump Slash': {
        'name'    : 'logic_lab_wall_gs',
        'tooltip' : '''\
                    The jump slash to actually collect the
                    token is somewhat precise.
                    '''},
    'Spirit Temple MQ Lower Adult without Fire Arrows': {
        'name'    : 'logic_spirit_mq_lower_adult',
        'tooltip' : '''\
                    It can be done with Din\'s Fire and Bow.
                    Whenever an arrow passes through a lit torch, it
                    resets the timer. It's finicky but it's also
                    possible to stand on the pillar next to the center
                    torch, which makes it easier.
                    '''},
    'Spirit Temple Map Chest with Bow': {
        'name'    : 'logic_spirit_map_chest',
        'tooltip' : '''\
                    To get a line of sight from the upper torch to
                    the map chest torches, you must pull an Armos
                    statue all the way up the stairs.
                    '''},
    'Spirit Temple Sun Block Room Chest with Bow': {
        'name'    : 'logic_spirit_sun_chest',
        'tooltip' : '''\
                    Using the blocks in the room as platforms you can
                    get lines of sight to all three torches. The timer
                    on the torches is quite short so you must move
                    quickly in order to light all three.
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
    # Non-GUI Settings
    Checkbutton('cosmetics_only'),
    Checkbutton('check_version'),
    Setting_Info('distribution_file', str, False, {}),
    Setting_Info('checked_version', str, False, {}),
    Setting_Info('rom',             str, False, {}),
    Setting_Info('output_dir',      str, False, {}),
    Setting_Info('output_file',     str, False, {}),
    Setting_Info('seed',            str, False, {}),
    Setting_Info('patch_file',      str, False, {}),
    Setting_Info('count',           int, False, {}, 
        default        = 1,
    ),
    Scale('world_count', 
        min            = 1, 
        max            = 255, 
        default        = 1,
    ),
    Scale('player_num', 
        min            = 1, 
        max            = 255, 
        default        = 1,
        dependency     = lambda settings: 1 if settings.compress_rom in ['None', 'Patch'] else None,
    ),

    # GUI Settings
    Checkbutton(
        name           = 'repatch_cosmetics',
        gui_text       = 'Patch Cosmetics',
        gui_tooltip    = '''\
                         Enabling this will re-patch cosmetics based on current settings.
                         Otherwise, it will utilize the cosmetics that are in the patch file.
                         ''',
        default        = True,
        shared         = False,
    ),
    Checkbutton(
        name           = 'create_spoiler',
        gui_text       = 'Create Spoiler Log',
        gui_group      = 'rom_tab',
        gui_tooltip    = '''\
                         Enabling this will change the seed.
                         ''',
        default        = True,
        shared         = True,
    ),
    Checkbutton(
        name           = 'create_cosmetics_log',
        gui_text       = 'Create Cosmetics Log',
        gui_group      = 'rom_tab',
        default        = True,
        dependency     = lambda settings: False if settings.compress_rom == 'None' else None,
    ),
    Setting_Info(
        name           = 'compress_rom',
        type           = str,
        shared         = False,
        choices        = {
            'True':  'Compressed [Stable]',
            'False': 'Uncompressed [Crashes]',
            'Patch': 'Patch File',
            'None':  'No Output',
        },
        default        = 'True',
        gui_params={
            'text':   'Output Type',
            'group':  'rom_tab',
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
    ),
    Checkbutton(
        name           = 'randomize_settings',
        gui_text       = 'Randomize Main Rule Settings',
        gui_group      = 'rules_tab',
        gui_tooltip    = '''\
                         Randomizes most Main Rules.
                         ''',
        default        = False,
        shared         = True,
    ),
    Checkbutton(
        name           = 'open_forest',
        gui_text       = 'Open Forest',
        gui_group      = 'open',
        gui_tooltip    = '''\
            Mido no longer blocks the path to the Deku Tree,
            and the Kokiri boy no longer blocks the path out
            of the forest.

            When this option is off, the Kokiri Sword and
            Slingshot are always available somewhere
            in the forest.

            This is incompatible with start as adult.
        ''',
        default        = True,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'open_kakariko',
        gui_text       = 'Open Kakariko Gate',
        gui_group      = 'open',
        gui_tooltip    = '''\
            The gate in Kakariko Village to Death Mountain Trail
            is always open instead of needing Zelda's Letter.

            Either way, the gate is always open as an adult.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'open_door_of_time',
        gui_text       = 'Open Door of Time',
        gui_group      = 'open',
        gui_tooltip    = '''\
            The Door of Time starts opened instead of needing to
            play the Song of Time. If this is not set, only
            an Ocarina and Song of Time must be found to open
            the Door of Time.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'open_fountain',
        gui_text       = 'Open Zora\'s Fountain',
        gui_group      = 'open',
        gui_tooltip    = '''\
            King Zora starts out as moved. This also removes
            Ruto's Letter from the item pool.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'child_lake_hylia_control',
        gui_text       = 'Child May Drain Lake Hylia',
        gui_group      = 'open',
        gui_tooltip    = '''\
            The switch to drain Lake Hylia after defeating morpha is
            enabled for child (in addition to adult).

            This option gives another dungeon entrance available to
            child for Entrance Randomizer and adds more items
            potentially accessible from completing Water Temple.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Combobox(
        name           = 'gerudo_fortress',
        default        = 'normal',
        choices        = {
            'normal': 'Default Behavior',
            'fast':   'Rescue One Carpenter',
            'open':   'Open Gerudo Fortress',
        },
        gui_text       = 'Gerudo Fortress',
        gui_group      = 'open',
        gui_tooltip    = '''\
            'Rescue One Carpenter': Only the bottom left
            carpenter must be rescued.

            'Open Gerudo Fortress': The carpenters are rescued from
            the start of the game, and if 'Shuffle Gerudo Card' is disabled,
            the player starts with the Gerudo Card in the inventory 
            allowing access to Gerudo Training Grounds.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
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
            'tokens':     '100 Gold Skulltula Tokens',
            'med-open':   'Medallions + Open',
            'ad-open':    'All Dungeons + Open'
        },
        gui_text       = 'Rainbow Bridge Requirement',
        gui_group      = 'open',
        gui_tooltip    = '''\
            'Always Open': Rainbow Bridge is always present.
            'Vanilla Requirements': Spirit/Shadow Medallions and Light Arrows.
            'All Spiritual Stones': All 3 Spiritual Stones.
            'All Medallions': All 6 Medallions.
            'All Dungeons': All Medallions and Spiritual Stones.
            '100 Gold Skulltula Tokens': All 100 Gold Skulltula Tokens.
            'All Dungeons + Open': Open bridge, Ganon Tower boss key at Light Arrows, Light Arrow cutscene requires Medallions/Stones.
            'Medallions + Open': Open bridge, Ganon Tower Boss Key at Light Arrows, Light Arrow cutscene requires all Medallions.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution':  [
                ('open',       1),
                ('vanilla',    1),
                ('stones',     1),
                ('medallions', 1),
                ('dungeons',   1),
            ],
        },
    ),
    Combobox(
        name           = 'logic_rules',
        default        = 'glitchless',
        choices        = {
            'glitchless': 'Glitchless',
            'none':       'No Logic',
        },
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
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'bombchus_in_logic',
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
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'one_item_per_dungeon',
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
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'trials_random',
        gui_text       = 'Random Number of Ganon\'s Trials',
        gui_group      = 'open',
        gui_tooltip    = '''\
                         Sets a random number of trials to
                         enter Ganon's Tower.
                         ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution':  [
                (True, 1),
            ]
        },
    ),
    Scale(
        name           = 'trials',
        default        = 6,
        min            = 0,
        max            = 6,
        gui_group      = 'open',
        gui_tooltip    = '''\
            Trials are randomly selected. If hints are
            enabled, then there will be hints for which
            trials need to be completed.
        ''',
        shared         = True,
        dependency     = lambda settings: 0 if settings.trials_random else None,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'no_escape_sequence',
        gui_text       = 'Skip Tower Escape Sequence',
        gui_group      = 'convenience',
        gui_tooltip    = '''\
            The tower escape sequence between
            Ganondorf and Ganon will be skipped.
        ''',
        shared         = True,
        dependency     = lambda settings: True if settings.entrance_shuffle == 'indoors' else None,
    ),
    Checkbutton(
        name           = 'no_guard_stealth',
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
        gui_text       = 'Start with Max Rupees',
        gui_group      = 'convenience',
        gui_tooltip    = '''\
            Start the game with 99 rupees.
        ''',
        shared         = True,
    ),
    Checkbutton(
        name           = 'start_with_wallet',
        gui_text       = 'Start with Tycoon\'s Wallet',
        gui_group      = 'convenience',
        gui_tooltip    = '''\
            Start the game with the largest wallet (999 max).
        ''',
        shared         = True,
    ),
    Checkbutton(
        name           = 'start_with_deku_equipment',
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
        name           = 'fast_chickens',
        gui_text       = 'Fast Chickens',
        gui_group      = 'convenience',
        gui_tooltip    = '''\
            Move 3 of the cuccos in child Kakariko into the pen.
        ''',
        shared         = True,
    ),
    Checkbutton(
        name           = 'big_poe_count_random',
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
        gui_group      = 'convenience',
        gui_tooltip    = '''\
            The Poe buyer will give a reward for turning
            in the chosen number of Big Poes.
        ''',
        dependency     = lambda settings: 1 if settings.big_poe_count_random else None,
        shared         = True,
    ),
    Checkbutton(
        name           = 'shuffle_kokiri_sword',
        gui_text       = 'Shuffle Kokiri Sword',
        gui_group      = 'shuffle',
        gui_tooltip    = '''\
            Enabling this shuffles the Kokiri Sword into the pool.

            This will require extensive use of sticks until the
            sword is found.
        ''',
        default        = True,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'shuffle_ocarinas',
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
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'shuffle_weird_egg',
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
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'shuffle_gerudo_card',
        gui_text       = 'Shuffle Gerudo Card',
        gui_group      = 'shuffle',
        gui_tooltip    = '''\
            Enabling this shuffles the Gerudo Card into the item pool.

            The Gerudo Card is required to enter the Gerudo Training Grounds,
            however it does not prevent the guards throwing you in jail.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'shuffle_song_items',
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
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'shuffle_cows',
        gui_text       = 'Shuffle Cows',
        gui_group      = 'shuffle',
        gui_tooltip    = '''\
            Enabling this causes playing Epona's song infront
            of cows to give an item. There are 9 cows, and an
            extra in MQ Jabu
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Combobox(
        name           = 'entrance_shuffle',
        default        = 'off',
        choices        = {
            'off':       'Off',
            'dungeons':  'Dungeons Only',
            'indoors':   'All Indoors',
        },
        gui_text       = 'Entrance Shuffle',
        gui_group      = 'shuffle',
        gui_tooltip    = '''\
            Shuffle entrances bidirectionally within different pools.

            'Dungeons Only':
            Shuffle dungeon entrances with each other, including Bottom 
            of the Well, Ice Cavern, and Gerudo Training Grounds. 
            However, Ganon's Castle is not shuffled.

            Additionally, the entrances of Deku Tree, Fire Temple and 
            Bottom of the Well are opened for both adult and child to 
            improve randomization, and accessing the Fire Temple from 
            Bolero is always in logic for child regardless of Tunic settings.

            Blue warps will return link to the new dungeons entrance. 
            Lake Hylia will be filled for adult after defeating Morpha.

            Master Quest dungeons are not supported yet, coming soon!

            'All Indoors':
            Shuffle dungeon entrances along with grotto and interior 
            entrances as described below. All entrances are still only 
            shuffled within their own pool. This means, for example, 
            that dungeons are only shuffled with other dungeons.

            Grottos: All grottos in the game including small Fairy Fountains 
            and the Lost Woods Stage.

            Interiors: All Houses and Great Fairies in the game.
            For now, this excludes Richard's house, the Windmill, the 
            Kakariko Potion Shop, Link's House and Temple of Time.
            Adult trade quest timers are disabled when shuffling this pool,
            and it forces Skip Tower Escape Sequence to be enabled for now.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution':  [
                ('off', 2),
                ('dungeons', 1),
                ('indoors', 1),
            ],
        },
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
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution':  [
                ('off', 1),
                ('low', 1),
            ],
        },
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
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution':  [
                ('off',    6),
                ('0',      1),
                ('1',      1),
                ('2',      1),
                ('3',      1),
                ('4',      1),
                ('random', 1),
            ],
        },
    ),
    Combobox(
        name           = 'tokensanity',
        default        = 'off',
        choices        = {
            'off':      'Off',
            'dungeons': 'Dungeons Only',
            'all':      'All Tokens',
            },
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
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
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
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Combobox(
        name           = 'shuffle_smallkeys',
        default        = 'dungeon',
        choices        = {
            'remove':    'Small Keys: Remove (Keysy)',
            'dungeon':   'Small Keys: Dungeon Only',
            'keysanity': 'Small Keys: Anywhere (Keysanity)'
        },
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
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Combobox(
        name           = 'shuffle_bosskeys',
        default        = 'dungeon',
        choices        = {
            'remove':    'Boss Keys: Remove (Keysy)',
            'dungeon':   'Boss Keys: Dungeon Only',
            'keysanity': 'Boss Keys: Anywhere (Keysanity)',
        },
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
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'enhance_map_compass',
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
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'unlocked_ganondorf',
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
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'mq_dungeons_random',
        gui_text       = 'Random Number of MQ Dungeons',
        gui_group      = 'world',
        gui_tooltip    = '''\
            If set, a random number of dungeons
            will have Master Quest designs.
        ''',
        dependency     = lambda settings: False if settings.entrance_shuffle != 'off' else None,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution': [
                (True, 1),
            ],
        },
    ),
    Scale(
        name           = 'mq_dungeons',
        default        = 0,
        min            = 0,
        max            = 12,
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
        dependency     = lambda settings: 0 if settings.mq_dungeons_random or settings.entrance_shuffle != 'off' else None,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },    
    ),
    Setting_Info(
        name           = 'disabled_locations', 
        type           = list, 
        shared         = True,
        choices        = [location.name for location in LocationIterator(lambda loc: loc.filter_tags is not None)],
        default        = [],
        gui_params     = {
            'text': 'Exclude Locations',
            'widget': 'FilteredSearchBox',
            'group': 'logic_tab',
            'filterdata': {location.name: location.filter_tags for location in LocationIterator(lambda loc: loc.filter_tags is not None)},
            'tooltip':'''
                Prevent locations from being required. Major
                items can still appear there, however they
                will never be required to beat the game.

                Most dungeon locations have a MQ alternative.
                If the location does not exist because of MQ
                then it will be ignored. So make sure to
                disable both versions if that is the intent.
            '''
        }
    ),
    Setting_Info(
        name           = 'allowed_tricks',
        type           = list,
        shared         = True,
        choices        = {
            val['name']: gui_text for gui_text, val in logic_tricks.items()
        },
        default        = [],
        gui_params     = {
            'text': 'Enable Tricks',
            'widget': 'SearchBox',
            'group': 'logic_tab',
            'entry_tooltip': logic_tricks_entry_tooltip,
            'list_tooltip': logic_tricks_list_tooltip,
        }
    ),
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
        gui_text       = 'Hint Distribution',
        gui_group      = 'other',
        gui_tooltip    = '''\
            Useless has nothing but junk hints.
            Strong distribution has a good
            spread of different hint types.
            Multiworld distribution has only
            a few specific, useful hint types.
            Tournament distribution has a set
            number of hints for each type.
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
        name           = 'starting_age',
        default        = 'child',
        choices        = {
            'child':  'Child',
            'adult':  'Adult',
            'random': 'Random',
        },
        gui_text       = 'Starting Age',
        gui_group      = 'other',
        gui_tooltip    = '''\
            Choose which age Link will start as.

            Starting as adult means you start with
            the master sword in your inventory.

            Only the child option is compatible with
            Closed Forest.
        ''',
        shared         = True,
        dependency     = lambda settings: 'child' if not settings.open_forest else None,
    ),
    Combobox(
        name           = 'default_targeting',
        default        = 'hold',
        choices        = {
            'hold':   'Hold',
            'switch': 'Switch',
        },
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
        gui_text       = 'Display D-Pad HUD',
        gui_group      = 'cosmetic',
        gui_tooltip    = '''\
            Shows an additional HUD element displaying
            current available options on the D-Pad.
        ''',
        default        = True,
    ),

    Setting_Info(
        name           = 'kokiri_color',
        type           = str,
        shared         = False,
        choices        = get_tunic_color_options(),
        default        = 'Kokiri Green',
        gui_params     = {
            'text':   'Kokiri Tunic',
            'group':  'tunic_colors',
            'widget': 'Combobox',
            'tooltip':'''\
                'Random Choice': Choose a random
                color from this list of colors.
                'Completely Random': Choose a random
                color from any color the N64 can draw.
            '''
        },
    ),
    Setting_Info(
        name           = 'goron_color',
        type           = str,
        shared         = False,
        choices        = get_tunic_color_options(),
        default        = 'Goron Red',
        gui_params     = {
            'text':   'Goron Tunic',
            'group':  'tunic_colors',
            'widget': 'Combobox',
            'tooltip':'''\
                'Random Choice': Choose a random
                color from this list of colors.
                'Completely Random': Choose a random
                color from any color the N64 can draw.
            '''
        },
    ),
    Setting_Info(
        name           = 'zora_color',
        type           = str,
        shared         = False,
        choices        = get_tunic_color_options(),
        default        = 'Zora Blue',
        gui_params     = {
            'text':   'Zora Tunic',
            'group':  'tunic_colors',
            'widget': 'Combobox',
            'tooltip':'''\
                'Random Choice': Choose a random
                color from this list of colors.
                'Completely Random': Choose a random
                color from any color the N64 can draw.
            '''
        },
    ),
    Setting_Info(
        name           = 'navi_color_default',
        type           = str,
        shared         = False,
        choices        = get_navi_color_options(),
        default        = 'White',
        gui_params     = {
            'text':   'Navi Idle',
            'group':  'navi_colors',
            'widget': 'Combobox',
            'tooltip':'''\
                'Random Choice': Choose a random
                color from this list of colors.
                'Completely Random': Choose a random
                color from any color the N64 can draw.
            '''
        },
    ),
    Setting_Info(
        name           = 'navi_color_enemy',
        type           = str,
        shared         = False,
        choices        = get_navi_color_options(),
        default        = 'Yellow',
        gui_params     = {
            'text':   'Navi Targeting Enemy',
            'group':  'navi_colors',
            'widget': 'Combobox',
            'tooltip':'''\
                'Random Choice': Choose a random
                color from this list of colors.
                'Completely Random': Choose a random
                color from any color the N64 can draw.
            '''
        },
    ),
    Setting_Info(
        name           = 'navi_color_npc',
        type           = str,
        shared         = False,
        choices        = get_navi_color_options(),
        default        = 'Light Blue',
        gui_params     = {
            'text':   'Navi Targeting NPC',
            'group':  'navi_colors',
            'widget': 'Combobox',
            'tooltip':'''\
                'Random Choice': Choose a random
                color from this list of colors.
                'Completely Random': Choose a random
                color from any color the N64 can draw.
            '''
        },
    ),
    Setting_Info(
        name           = 'navi_color_prop',
        type           = str,
        shared         = False,
        choices        = get_navi_color_options(),
        default        = 'Green',
        gui_params     = {
            'text':   'Navi Targeting Prop',
            'group':  'navi_colors',
            'widget': 'Combobox',
            'tooltip':'''\
                'Random Choice': Choose a random
                color from this list of colors.
                'Completely Random': Choose a random
                color from any color the N64 can draw.
            '''
        },
    ),
    Combobox(
        name           = 'sword_trail_duration',
        choices        = {
            4: 'Default',
            10: 'Long',
            15: 'Very Long',
            20: 'Lightsaber',
        },
        default        = 4,
        gui_text       = 'Sword Trail Duration',
        gui_group      = 'sword_trails',
        gui_tooltip    = '''\
            Select the duration for sword trails.
        ''',
    ),
    Setting_Info(
        name           = 'sword_trail_color_inner',
        type           = str,
        shared         = False,
        choices        = get_sword_color_options(),
        default        = 'White',
        gui_params     = {
            'text':   'Inner Color',
            'group':  'sword_trails',
            'widget': 'Combobox',
            'tooltip':'''\
                'Random Choice': Choose a random
                color from this list of colors.
                'Completely Random': Choose a random
                color from any color the N64 can draw.
                'Rainbow': Rainbow sword trails.
            '''
        },
    ),
    Setting_Info(
        name           = 'sword_trail_color_outer',
        type           = str,
        shared         = False,
        choices        = get_sword_color_options(),
        default        = 'White',
        gui_params     = {
            'text':   'Outer Color',
            'group':  'sword_trails',
            'widget': 'Combobox',
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      'Rainbow': Rainbow sword trails.
            '''
        }
    ),
    Setting_Info(
        name           = 'silver_gauntlets_color',
        type           = str,
        shared         = False,
        choices        = get_gauntlet_color_options(),
        default        = 'Silver',
        gui_params     = {
            'text':   'Silver Gauntlets Color',
            'group':  'gauntlet_colors',
            'widget': 'Combobox',
            'tooltip': '''\
                'Random Choice': Choose a random
                color from this list of colors.
                'Completely Random': Choose a random
                color from any color the N64 can draw.
                'Rainbow': Rainbow sword trails.
            '''
        },
    ),
    Setting_Info(
        name           = 'golden_gauntlets_color',
        type           = str,
        shared         = False,
        choices        = get_gauntlet_color_options(),
        default        = 'Gold',
        gui_params={
            'text':   'Golden Gauntlets Color',
            'group':  'gauntlet_colors',
            'widget': 'Combobox',
            'tooltip': '''\
                'Random Choice': Choose a random
                color from this list of colors.
                'Completely Random': Choose a random
                color from any color the N64 can draw.
                'Rainbow': Rainbow sword trails.
            '''
        },
    ),
    Setting_Info(
        name           = 'heart_color',
        type           = str,
        shared         = False,
        choices        = get_heart_color_options(),
        default        = 'Red',
        gui_params     = {
            'text':   'Heart Color',
            'group':  'ui_colors',
            'widget': 'Combobox',
            'tooltip': '''\
                'Random Choice': Choose a random
                color from this list of colors.
                'Completely Random': Choose a random
                color from any color the N64 can draw.
            '''
        },
    ),
    Setting_Info(
        name           = 'magic_color',
        type           = str,
        shared         = False,
        choices        = get_magic_color_options(),
        default        = 'Green',
        gui_params     = {
            'text':   'Magic Color',
            'group':  'ui_colors',
            'widget': 'Combobox',
            'tooltip': '''\
                'Random Choice': Choose a random
                color from this list of colors.
                'Completely Random': Choose a random
                color from any color the N64 can draw.
            '''
        },
    ),
    Combobox(
        name           = 'sfx_low_hp',
        choices        = sfx.get_setting_choices(sfx.SoundHooks.HP_LOW),
        default        = 'default',
        gui_text       = 'Low HP',
        gui_group      = 'sfx',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            sound from this list.
            'Default': Beep. Beep. Beep.
        ''',
    ),
    Combobox(
        name           = 'sfx_navi_overworld',
        choices        = sfx.get_setting_choices(sfx.SoundHooks.NAVI_OVERWORLD),
        default        = 'default',
        gui_text       = 'Navi Overworld',
        gui_group      = 'npc_sfx',
    ),
    Combobox(
        name           = 'sfx_navi_enemy',
        choices        = sfx.get_setting_choices(sfx.SoundHooks.NAVI_ENEMY),
        default        = 'default',
        gui_text       = 'Navi Enemy',
        gui_group      = 'npc_sfx',
    ),
    Combobox(
        name           = 'sfx_menu_cursor',
        choices        = sfx.get_setting_choices(sfx.SoundHooks.MENU_CURSOR),
        default        = 'default',
        gui_text       = 'Menu Cursor',
        gui_group      = 'menu_sfx',
    ),
    Combobox(
        name           = 'sfx_menu_select',
        choices        = sfx.get_setting_choices(sfx.SoundHooks.MENU_SELECT),
        default        = 'default',
        gui_text       = 'Menu Select',
        gui_group      = 'menu_sfx',
    ),
    Combobox(
        name           = 'sfx_horse_neigh',
        choices        = sfx.get_setting_choices(sfx.SoundHooks.HORSE_NEIGH),
        default        = 'default',
        gui_text       = 'Horse',
        gui_group      = 'sfx',
    ),
    Combobox(
        name           = 'sfx_nightfall',
        choices        = sfx.get_setting_choices(sfx.SoundHooks.NIGHTFALL),
        default        = 'default',
        gui_text       = 'Nightfall',
        gui_group      = 'sfx',
    ),
    Combobox(
        name           = 'sfx_hover_boots',
        choices        = sfx.get_setting_choices(sfx.SoundHooks.BOOTS_HOVER),
        default        = 'default',
        gui_text       = 'Hover Boots',
        gui_group      = 'sfx',
    ),
    Combobox(
        name           = 'sfx_ocarina',
        choices        = {
            'ocarina':       'Default',
            'random-choice': 'Random Choice',
            'flute':         'Flute',
            'harp':          'Harp',
            'whistle':       'Whistle',
            'malon':         'Malon',
            'grind-organ':   'Grind Organ',
        },
        default        = 'ocarina',
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
