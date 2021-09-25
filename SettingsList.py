import argparse
import difflib
from itertools import chain
import re
import math
import json
import operator

from Colors import get_tunic_color_options, get_navi_color_options, get_sword_trail_color_options, \
    get_bombchu_trail_color_options, get_boomerang_trail_color_options, get_gauntlet_color_options, \
    get_magic_color_options, get_heart_color_options, get_shield_frame_color_options, get_a_button_color_options,\
    get_b_button_color_options, get_c_button_color_options, get_start_button_color_options
from Hints import HintDistList, HintDistTips
from Location import LocationIterator
import Sounds as sfx
import StartingItems
from Utils import data_path

# holds the info for a single setting
class Setting_Info():

    def __init__(self, name, type, gui_text, gui_type, shared, choices, default=None, disabled_default=None, disable=None, gui_tooltip=None, gui_params=None, cosmetic=False):
        self.name = name # name of the setting, used as a key to retrieve the setting's value everywhere
        self.type = type # type of the setting's value, used to properly convert types to setting strings
        self.shared = shared # whether or not the setting is one that should be shared, used in converting settings to a string
        self.cosmetic = cosmetic # whether or not the setting should be included in the cosmetic log
        self.gui_text = gui_text
        self.gui_type = gui_type
        if gui_tooltip is None:
            self.gui_tooltip = ""
        else:
            self.gui_tooltip = gui_tooltip

        if gui_params == None:
            gui_params = {}
        self.gui_params = gui_params # additional parameters that the randomizer uses for the gui
        self.disable = disable # dictionary of settings this this setting disabled
        self.dependency = None # lambda the determines if this is disabled. Generated later

        # dictionary of options to their text names
        if isinstance(choices, list):
            self.choices = {k: k for k in choices}
            self.choice_list = list(choices)
        else:
            self.choices = dict(choices)
            self.choice_list = list(choices.keys())
        self.reverse_choices = {v: k for k, v in self.choices.items()}

        # number of bits needed to store the setting, used in converting settings to a string
        if shared:
            if self.gui_params.get('min') and self.gui_params.get('max') and not choices:
                self.bitwidth = math.ceil(math.log(self.gui_params.get('max') - self.gui_params.get('min') + 1, 2))
            else:
                self.bitwidth = self.calc_bitwidth(choices)
        else:
            self.bitwidth = 0

        # default value if undefined/unset
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
        elif self.type == dict:
            self.default = {}

        # default value if disabled
        if disabled_default == None:
            self.disabled_default = self.default
        else:
            self.disabled_default = disabled_default

        # used to when random options are set for this setting
        if 'distribution' not in gui_params:
            self.gui_params['distribution'] = [(choice, 1) for choice in self.choice_list]


    def calc_bitwidth(self, choices):
        count = len(choices)
        if count > 0:
            if self.type == list:
                # Need two special values for terminating additive and subtractive lists
                count = count + 2
            return math.ceil(math.log(count, 2))
        return 0


class Checkbutton(Setting_Info):

    def __init__(self, name, gui_text, gui_tooltip=None, disable=None,
            disabled_default=None, default=False, shared=False, gui_params=None, cosmetic=False):

        choices = {
            True:  'checked',
            False: 'unchecked',
        }

        super().__init__(name, bool, gui_text, 'Checkbutton', shared, choices, default, disabled_default, disable, gui_tooltip, gui_params, cosmetic)


class Combobox(Setting_Info):

    def __init__(self, name, gui_text, choices, default, gui_tooltip=None,
            disable=None, disabled_default=None, shared=False, gui_params=None, cosmetic=False):

        super().__init__(name, str, gui_text, 'Combobox', shared, choices, default, disabled_default, disable, gui_tooltip, gui_params, cosmetic)


class Scale(Setting_Info):

    def __init__(self, name, gui_text, min, max, default, step=1,
            gui_tooltip=None, disable=None, disabled_default=None,
            shared=False, gui_params=None, cosmetic=False):

        choices = {
            i: str(i) for i in range(min, max+1, step)
        }
        if gui_params == None:
            gui_params = {}
        gui_params['min']    = min
        gui_params['max']    = max
        gui_params['step']   = step

        super().__init__(name, int, gui_text, 'Scale', shared, choices, default, disabled_default, disable, gui_tooltip, gui_params, cosmetic)


logic_tricks = {
    'Fewer Tunic Requirements': {
        'name'    : 'logic_fewer_tunic_requirements',
        'tags'    : ("General", "Fire Temple", "Water Temple", "Gerudo Training Ground", "Zora's Fountain",),
        'tooltip' : '''\
                    Allows the following possible without Tunics:
                    - Enter Water Temple. The key below the center
                    pillar still requires Zora Tunic.
                    - Enter Fire Temple. Only the first floor is
                    accessible, and not Volvagia.
                    - Zora's Fountain Bottom Freestanding PoH.
                    Might not have enough health to resurface.
                    - Gerudo Training Ground Underwater
                    Silver Rupee Chest. May need to make multiple
                    trips.
                    '''},
    'Hidden Grottos without Stone of Agony': {
        'name'    : 'logic_grottos_without_agony',
        'tags'    : ("General", "Entrance",),
        'tooltip' : '''\
                    Allows entering hidden grottos without the
                    Stone of Agony.
                    '''},
    'Pass Through Visible One-Way Collisions': {
        'name'    : 'logic_visible_collisions',
        'tags'    : ("Entrance", "Kakariko Village",),
        'tooltip' : '''\
                    Allows climbing through the platform to reach 
                    Impa's House Back as adult with no items and 
                    going through the Kakariko Village Gate as child
                    when coming from the Mountain Trail side.
                    '''},
    'Child Deadhand without Kokiri Sword': {
        'name'    : 'logic_child_deadhand',
        'tags'    : ("Bottom of the Well",),
        'tooltip' : '''\
                    Requires 9 sticks or 5 jump slashes.
                    '''},
    'Second Dampe Race as Child': {
        'name'    : 'logic_child_dampe_race_poh',
        'tags'    : ("the Graveyard", "Entrance",),
        'tooltip' : '''\
                    It is possible to complete the second dampe
                    race as child in under a minute, but it is
                    a strict time limit.
                    '''},
    'Man on Roof without Hookshot': {
        'name'    : 'logic_man_on_roof',
        'tags'    : ("Kakariko Village",),
        'tooltip' : '''\
                    Can be reached by side-hopping off
                    the watchtower.
                    '''},
    'Dodongo\'s Cavern Staircase with Bow': {
        'name'    : 'logic_dc_staircase',
        'tags'    : ("Dodongo's Cavern",),
        'tooltip' : '''\
                    The Bow can be used to knock down the stairs
                    with two well-timed shots.
                    '''},
    'Dodongo\'s Cavern Spike Trap Room Jump without Hover Boots': {
        'name'    : 'logic_dc_jump',
        'tags'    : ("Dodongo's Cavern",),
        'tooltip' : '''\
                    Jump is adult only.
                    '''},
    'Dodongo\'s Cavern Vines GS from Below with Longshot': {
        'name'    : 'logic_dc_vines_gs',
        'tags'    : ("Dodongo's Cavern", "Skulltulas",),
        'tooltip' : '''\
                    The vines upon which this Skulltula rests are one-
                    sided collision. You can use the Longshot to get it
                    from below, by shooting it through the vines,
                    bypassing the need to lower the staircase.
                    '''},
    'Thieves\' Hideout "Kitchen" with No Additional Items': {
        'name'    : 'logic_gerudo_kitchen',
        'tags'    : ("Thieves' Hideout", "Gerudo's Fortress",),
        'tooltip' : '''\
                    The logic normally guarantees one of Bow, Hookshot,
                    or Hover Boots.
                    '''},
    'Deku Tree Basement Vines GS with Jump Slash': {
        'name'    : 'logic_deku_basement_gs',
        'tags'    : ("Deku Tree", "Skulltulas",),
        'tooltip' : '''\
                    Can be defeated by doing a precise jump slash.
                    '''},
    'Deku Tree Basement Web to Gohma with Bow': {
        'name'    : 'logic_deku_b1_webs_with_bow',
        'tags'    : ("Deku Tree", "Entrance",),
        'tooltip' : '''\
                    All spider web walls in the Deku Tree basement can be burnt
                    as adult with just a bow by shooting through torches. This
                    trick only applies to the circular web leading to Gohma;
                    the two vertical webs are always in logic.

                    Backflip onto the chest near the torch at the bottom of
                    the vine wall. With precise positioning you can shoot
                    through the torch to the right edge of the circular web.

                    This allows completion of adult Deku Tree with no fire source.
                    '''},
    'Deku Tree MQ Roll Under the Spiked Log': {
        'name'    : 'logic_deku_mq_log',
        'tags'    : ("Deku Tree",),
        'tooltip' : '''\
                    You can get past the spiked log by rolling
                    to briefly shrink your hitbox. As adult,
                    the timing is a bit more precise.
                    '''},
    'Hammer Rusted Switches Through Walls': {
        'name'    : 'logic_rusted_switches',
        'tags'    : ("Fire Temple", "Ganon's Castle",),
        'tooltip' : '''\
                    Applies to:
                    - Fire Temple Highest Goron Chest.
                    - MQ Fire Temple Lizalfos Maze.
                    - MQ Spirit Trial.
                    '''},
    'Bottom of the Well Map Chest with Strength & Sticks': {
        'name'    : 'logic_botw_basement',
        'tags'    : ("Bottom of the Well",),
        'tooltip' : '''\
                    The chest in the basement can be reached with
                    strength by doing a jump slash with a lit
                    stick to access the bomb flowers.
                    '''},
    'Bottom of the Well MQ Jump Over the Pits': {
        'name'    : 'logic_botw_mq_pits',
        'tags'    : ("Bottom of the Well",),
        'tooltip' : '''\
                    While the pits in Bottom of the Well don't allow you to
                    jump just by running straight at them, you can still get
                    over them by side-hopping or backflipping across. With
                    explosives, this allows you to access the central areas
                    without Zelda's Lullaby. With Zelda's Lullaby, it allows
                    you to access the west inner room without explosives.
                    '''},
    'Skip Forest Temple MQ Block Puzzle with Bombchu': {
        'name'    : 'logic_forest_mq_block_puzzle',
        'tags'    : ("Forest Temple",),
        'tooltip' : '''\
                    Send the Bombchu straight up the center of the
                    wall directly to the left upon entering the room.
                    '''},
    'Spirit Temple Child Side Bridge with Bombchu': {
        'name'    : 'logic_spirit_child_bombchu',
        'tags'    : ("Spirit Temple",),
        'tooltip' : '''\
                    A carefully-timed Bombchu can hit the switch.
                    '''},
    'Windmill PoH as Adult with Nothing': {
        'name'    : 'logic_windmill_poh',
        'tags'    : ("Kakariko Village",),
        'tooltip' : '''\
                    Can jump up to the spinning platform from
                    below as adult.
                    '''},
    'Crater\'s Bean PoH with Hover Boots': {
        'name'    : 'logic_crater_bean_poh_with_hovers',
        'tags'    : ("Death Mountain Crater",),
        'tooltip' : '''\
                    Hover from the base of the bridge
                    near Goron City and walk up the
                    very steep slope.
                    '''},
    'Zora\'s Domain Entry with Cucco': {
        'name'    : 'logic_zora_with_cucco',
        'tags'    : ("Zora's River",),
        'tooltip' : '''\
                    Can fly behind the waterfall with
                    a cucco as child.
                    '''},
    'Water Temple MQ Central Pillar with Fire Arrows': {
        'name'    : 'logic_water_mq_central_pillar',
        'tags'    : ("Water Temple",),
        'tooltip' : '''\
                    Slanted torches have misleading hitboxes. Whenever
                    you see a slanted torch jutting out of the wall,
                    you can expect most or all of its hitbox is actually
                    on the other side that wall. This can make slanted
                    torches very finicky to light when using arrows. The
                    torches in the central pillar of MQ Water Temple are
                    a particularly egregious example. Logic normally
                    expects Din's Fire and Song of Time.
                    '''},
    'Gerudo Training Ground MQ Left Side Silver Rupees with Hookshot': {
        'name'    : 'logic_gtg_mq_with_hookshot',
        'tags'    : ("Gerudo Training Ground",),
        'tooltip' : '''\
                    The highest silver rupee can be obtained by
                    hookshotting the target and then immediately jump
                    slashing toward the rupee.
                    '''},
    'Forest Temple East Courtyard Vines with Hookshot': {
        'name'    : 'logic_forest_vines',
        'tags'    : ("Forest Temple",),
        'tooltip' : '''\
                    The vines in Forest Temple leading to where the well
                    drain switch is in the standard form can be barely
                    reached with just the Hookshot.
                    '''},
    'Forest Temple East Courtyard GS with Boomerang': {
        'name'    : 'logic_forest_outdoor_east_gs',
        'tags'    : ("Forest Temple", "Entrance", "Skulltulas",),
        'tooltip' : '''\
                    Precise Boomerang throws can allow child to
                    kill the Skulltula and collect the token.
                    '''},
    'Forest Temple First Room GS with Difficult-to-Use Weapons': {
        'name'    : 'logic_forest_first_gs',
        'tags'    : ("Forest Temple", "Entrance", "Skulltulas",),
        'tooltip' : '''\
                    Allows killing this Skulltula with Sword or Sticks by
                    jump slashing it as you let go from the vines. You will
                    take fall damage.
                    Also allows killing it as Child with a Bomb throw. It's
                    much more difficult to use a Bomb as child due to
                    Child Link's shorter height.
                    '''},
    'Swim Through Forest Temple MQ Well with Hookshot': {
        'name'    : 'logic_forest_well_swim',
        'tags'    : ("Forest Temple",),
        'tooltip' : '''\
                    Shoot the vines in the well as low and as far to
                    the right as possible, and then immediately swim
                    under the ceiling to the right. This can only be
                    required if Forest Temple is in its Master Quest
                    form.
                    '''},
    'Forest Temple MQ Twisted Hallway Switch with Jump Slash': {
        'name'    : 'logic_forest_mq_hallway_switch_jumpslash',
        'tags'    : ("Forest Temple",),
        'tooltip' : '''\
                    The switch to twist the hallway can be hit with
                    a jump slash through the glass block. To get in
                    front of the switch, either use the Hover Boots
                    or hit the shortcut switch at the top of the
                    room and jump from the glass blocks that spawn.
                    '''},
    #'Forest Temple MQ Twisted Hallway Switch with Hookshot': {
    #    'name'    : 'logic_forest_mq_hallway_switch_hookshot',
    #    'tags'    : ("Forest Temple",),
    #    'tooltip' : '''\
    #                There's a very small gap between the glass block
    #                and the wall. Through that gap you can hookshot
    #                the target on the ceiling.
    #                '''},
    'Death Mountain Trail Chest with Strength': {
        'name'    : 'logic_dmt_bombable',
        'tags'    : ("Death Mountain Trail",),
        'tooltip' : '''\
                    Child Link can blow up the wall using a nearby bomb
                    flower. You must backwalk with the flower and then
                    quickly throw it toward the wall.
                    '''},
    'Goron City Spinning Pot PoH with Strength': {
        'name'    : 'logic_goron_city_pot_with_strength',
        'tags'    : ("Goron City",),
        'tooltip' : '''\
                    Allows for stopping the Goron City Spinning
                    Pot using a bomb flower alone, requiring 
                    strength in lieu of inventory explosives.
                    '''},
    'Adult Kokiri Forest GS with Hover Boots': {
        'name'    : 'logic_adult_kokiri_gs',
        'tags'    : ("Kokiri Forest", "Skulltulas",),
        'tooltip' : '''\
                    Can be obtained without Hookshot by using the Hover
                    Boots off of one of the roots.
                    '''},
    'Spirit Temple MQ Frozen Eye Switch without Fire': {
        'name'    : 'logic_spirit_mq_frozen_eye',
        'tags'    : ("Spirit Temple",),
        'tooltip' : '''\
                    You can melt the ice by shooting an arrow through a
                    torch. The only way to find a line of sight for this
                    shot is to first spawn a Song of Time block, and then
                    stand on the very edge of it.
                    '''},
    'Spirit Temple Shifting Wall with No Additional Items': {
        'name'    : 'logic_spirit_wall',
        'tags'    : ("Spirit Temple",),
        'tooltip' : '''\
                    The logic normally guarantees a way of dealing with both
                    the Beamos and the Walltula before climbing the wall.
                    '''},
    'Spirit Temple Main Room GS with Boomerang': {
        'name'    : 'logic_spirit_lobby_gs',
        'tags'    : ("Spirit Temple", "Skulltulas",),
        'tooltip' : '''\
                    Standing on the highest part of the arm of the statue, a
                    precise Boomerang throw can kill and obtain this Gold
                    Skulltula. You must throw the Boomerang slightly off to
                    the side so that it curves into the Skulltula, as aiming
                    directly at it will clank off of the wall in front.
                    '''},
    'Spirit Temple Main Room Jump from Hands to Upper Ledges': {
        'name'    : 'logic_spirit_lobby_jump',
        'tags'    : ("Spirit Temple", "Skulltulas",),
        'tooltip' : '''\
                    A precise jump to obtain the following as adult
                    without needing one of Hookshot or Hover Boots:
                    - Spirit Temple Statue Room Northeast Chest
                    - Spirit Temple GS Lobby
                    '''},
    'Spirit Temple MQ Sun Block Room GS with Boomerang': {
        'name'    : 'logic_spirit_mq_sun_block_gs',
        'tags'    : ("Spirit Temple", "Skulltulas",),
        'tooltip' : '''\
                    Throw the Boomerang in such a way that it
                    curves through the side of the glass block
                    to hit the Gold Skulltula.
                    '''},
    'Jabu Scrub as Adult with Jump Dive': {
        'name'    : 'logic_jabu_scrub_jump_dive',
        'tags'    : ("Jabu Jabu's Belly", "Entrance",),
        'tooltip' : '''\
                    Standing above the underwater tunnel leading to the scrub,
                    jump down and swim through the tunnel. This allows adult to
                    access the scrub with no Scale or Iron Boots.
                    '''},
    'Jabu MQ Song of Time Block GS with Boomerang': {
        'name'    : 'logic_jabu_mq_sot_gs',
        'tags'    : ("Jabu Jabu's Belly", "Skulltulas",),
        'tooltip' : '''\
                    Allow the Boomerang to return to you through
                    the Song of Time block to grab the token.
                    '''},
    'Bottom of the Well MQ Dead Hand Freestanding Key with Boomerang': {
        'name'    : 'logic_botw_mq_dead_hand_key',
        'tags'    : ("Bottom of the Well",),
        'tooltip' : '''\
                    Boomerang can fish the item out of the rubble without
                    needing explosives to blow it up.
                    '''},
    'Fire Temple Flame Wall Maze Skip': {
        'name'    : 'logic_fire_flame_maze',
        'tags'    : ("Fire Temple",),
        'tooltip' : '''\
                    If you move quickly you can sneak past the edge of
                    a flame wall before it can rise up to block you.
                    To do it without taking damage is more precise.
                    Allows you to progress without needing either a
                    Small Key or Hover Boots.
                    '''},
    'Fire Temple MQ Flame Wall Maze Skip': {
        'name'    : 'logic_fire_mq_flame_maze',
        'tags'    : ("Fire Temple", "Skulltulas",),
        'tooltip' : '''\
                    If you move quickly you can sneak past the edge of
                    a flame wall before it can rise up to block you.
                    To do it without taking damage is more precise.
                    Allows you to reach the side room GS without needing
                    Song of Time or Hover Boots. If either of "Fire Temple
                    MQ Lower to Upper Lizalfos Maze with Hover Boots" or
                    "with Precise Jump" are enabled, this also allows you
                    to progress deeper into the dungeon without Hookshot.
                    '''},
    'Fire Temple MQ Climb without Fire Source': {
        'name'    : 'logic_fire_mq_climb',
        'tags'    : ("Fire Temple",),
        'tooltip' : '''\
                    You can use the Hover Boots to hover around to
                    the climbable wall, skipping the need to use a
                    fire source and spawn a Hookshot target.
                    '''},
    'Fire Temple MQ Lower to Upper Lizalfos Maze with Hover Boots': {
        'name'    : 'logic_fire_mq_maze_hovers',
        'tags'    : ("Fire Temple",),
        'tooltip' : '''\
                    Use the Hover Boots off of a crate to
                    climb to the upper maze without needing
                    to spawn and use the Hookshot targets.
                    '''},
    'Fire Temple MQ Chest Near Boss without Breaking Crate': {
        'name'    : 'logic_fire_mq_near_boss',
        'tags'    : ("Fire Temple",),
        'tooltip' : '''\
                    The hitbox for the torch extends a bit outside of the crate.
                    Shoot a flaming arrow at the side of the crate to light the
                    torch without needing to get over there and break the crate.
                    '''},
    'Fire Temple MQ Lizalfos Maze Side Room without Box': {
        'name'    : 'logic_fire_mq_maze_side_room',
        'tags'    : ("Fire Temple",),
        'tooltip' : '''\
                    You can walk from the blue switch to the door and
                    quickly open the door before the bars reclose. This
                    skips needing to reach the upper sections of the
                    maze to get a box to place on the switch.
                    '''},
    'Fire Temple MQ Boss Key Chest without Bow': {
        'name'    : 'logic_fire_mq_bk_chest',
        'tags'    : ("Fire Temple",),
        'tooltip' : '''\
                    It is possible to light both of the timed torches
                    to unbar the door to the boss key chest's room
                    with just Din's Fire if you move very quickly
                    between the two torches. It is also possible to
                    unbar the door with just Din's by abusing an
                    oversight in the way the game counts how many
                    torches have been lit.
                    '''},
    'Fire Temple MQ Above Flame Wall Maze GS from Below with Longshot': {
        'name'    : 'logic_fire_mq_above_maze_gs',
        'tags'    : ("Fire Temple", "Skulltulas",),
        'tooltip' : '''\
                    The floor of the room that contains this Skulltula
                    is only solid from above. From the maze below, the
                    Longshot can be shot through the ceiling to obtain 
                    the token with two fewer small keys than normal.
                    '''},
    'Zora\'s River Lower Freestanding PoH as Adult with Nothing': {
        'name'    : 'logic_zora_river_lower',
        'tags'    : ("Zora's River",),
        'tooltip' : '''\
                    Adult can reach this PoH with a precise jump,
                    no Hover Boots required.
                    '''},
    'Water Temple Cracked Wall with Hover Boots': {
        'name'    : 'logic_water_cracked_wall_hovers',
        'tags'    : ("Water Temple",),
        'tooltip' : '''\
                    With a midair side-hop while wearing the Hover
                    Boots, you can reach the cracked wall without
                    needing to raise the water up to the middle level.
                    '''},
    'Shadow Temple Freestanding Key with Bombchu': {
        'name'    : 'logic_shadow_freestanding_key',
        'tags'    : ("Shadow Temple",),
        'tooltip' : '''\
                    Release the Bombchu with good timing so that
                    it explodes near the bottom of the pot.
                    '''},
    'Shadow Temple MQ Invisible Blades Silver Rupees without Song of Time': {
        'name'    : 'logic_shadow_mq_invisible_blades',
        'tags'    : ("Shadow Temple",),
        'tooltip' : '''\
                    The Like Like can be used to boost you into the
                    silver rupee that normally requires Song of Time.
                    This cannot be performed on OHKO since the Like
                    Like does not boost you high enough if you die.
                    '''},
    'Shadow Temple MQ Lower Huge Pit without Fire Source': {
        'name'    : 'logic_shadow_mq_huge_pit',
        'tags'    : ("Shadow Temple",),
        'tooltip' : '''\
                    Normally a frozen eye switch spawns some platforms
                    that you can use to climb down, but there's actually
                    a small piece of ground that you can stand on that
                    you can just jump down to.
                    '''},
    'Backflip over Mido as Adult': {
        'name'    : 'logic_mido_backflip',
        'tags'    : ("the Lost Woods",),
        'tooltip' : '''\
                    With a specific position and angle, you can
                    backflip over Mido.
                    '''},
    'Fire Temple Boss Door without Hover Boots or Pillar': {
        'name'    : 'logic_fire_boss_door_jump',
        'tags'    : ("Fire Temple",),
        'tooltip' : '''\
                    The Fire Temple Boss Door can be reached with a precise
                    jump. You must be touching the side wall of the room so
                    that Link will grab the ledge from farther away than
                    is normally possible.
                    '''},
    'Lake Hylia Lab Dive without Gold Scale': {
        'name'    : 'logic_lab_diving',
        'tags'    : ("Lake Hylia",),
        'tooltip' : '''\
                    Remove the Iron Boots in the midst of
                    Hookshotting the underwater crate.
                    '''},
    'Deliver Eye Drops with Bolero of Fire': {
        'name'    : 'logic_biggoron_bolero',
        'tags'    : ("Death Mountain Trail",),
        'tooltip' : '''\
                    Playing a warp song normally causes a trade item to
                    spoil immediately, however, it is possible use Bolero
                    to reach Biggoron and still deliver the Eye Drops
                    before they spoil. If you do not wear the Goron Tunic,
                    the heat timer inside the crater will override the trade
                    item's timer. When you exit to Death Mountain Trail you
                    will have one second to show the Eye Drops before they
                    expire. You can get extra time to show the Eye Drops if
                    you warp immediately upon receiving them. If you don't
                    have many hearts, you may have to reset the heat timer
                    by quickly dipping in and out of Darunia's chamber.
                    This trick does not apply if "Randomize Warp Song
                    Destinations" is enabled, or if the settings are such
                    that trade items do not need to be delivered within a
                    time limit.
                    '''},
    'Wasteland Crossing without Hover Boots or Longshot': {
        'name'    : 'logic_wasteland_crossing',
        'tags'    : ("Haunted Wasteland",),
        'tooltip' : '''\
                    You can beat the quicksand by backwalking across it
                    in a specific way.
                    '''},
    'Colossus Hill GS with Hookshot': {
        'name'    : 'logic_colossus_gs',
        'tags'    : ("Desert Colossus", "Skulltulas",),
        'tooltip' : '''\
                    Somewhat precise. If you kill enough Leevers
                    you can get enough of a break to take some time
                    to aim more carefully.
                    '''},
    'Dodongo\'s Cavern Scarecrow GS with Armos Statue': {
        'name'    : 'logic_dc_scarecrow_gs',
        'tags'    : ("Dodongo's Cavern", "Skulltulas",),
        'tooltip' : '''\
                    You can jump off an Armos Statue to reach the
                    alcove with the Gold Skulltula. It takes quite
                    a long time to pull the statue the entire way.
                    The jump to the alcove can be a bit picky when
                    done as child.
                    '''},
    'Kakariko Tower GS with Jump Slash': {
        'name'    : 'logic_kakariko_tower_gs',
        'tags'    : ("Kakariko Village", "Skulltulas",),
        'tooltip' : '''\
                    Climb the tower as high as you can without
                    touching the Gold Skulltula, then let go and
                    jump slash immediately. You will take fall
                    damage.
                    '''},
    'Deku Tree MQ Compass Room GS Boulders with Just Hammer': {
        'name'    : 'logic_deku_mq_compass_gs',
        'tags'    : ("Deku Tree", "Skulltulas",),
        'tooltip' : '''\
                    Climb to the top of the vines, then let go
                    and jump slash immediately to destroy the
                    boulders using the Hammer, without needing
                    to spawn a Song of Time block.
                    '''},
    'Lake Hylia Lab Wall GS with Jump Slash': {
        'name'    : 'logic_lab_wall_gs',
        'tags'    : ("Lake Hylia", "Skulltulas",),
        'tooltip' : '''\
                    The jump slash to actually collect the
                    token is somewhat precise.
                    '''},
    'Spirit Temple MQ Lower Adult without Fire Arrows': {
        'name'    : 'logic_spirit_mq_lower_adult',
        'tags'    : ("Spirit Temple",),
        'tooltip' : '''\
                    It can be done with Din\'s Fire and Bow.
                    Whenever an arrow passes through a lit torch, it
                    resets the timer. It's finicky but it's also
                    possible to stand on the pillar next to the center
                    torch, which makes it easier.
                    '''},
    'Spirit Temple Map Chest with Bow': {
        'name'    : 'logic_spirit_map_chest',
        'tags'    : ("Spirit Temple",),
        'tooltip' : '''\
                    To get a line of sight from the upper torch to
                    the map chest torches, you must pull an Armos
                    statue all the way up the stairs.
                    '''},
    'Spirit Temple Sun Block Room Chest with Bow': {
        'name'    : 'logic_spirit_sun_chest',
        'tags'    : ("Spirit Temple",),
        'tooltip' : '''\
                    Using the blocks in the room as platforms you can
                    get lines of sight to all three torches. The timer
                    on the torches is quite short so you must move
                    quickly in order to light all three.
                    '''},
    'Spirit Temple MQ Sun Block Room as Child without Song of Time': {
        'name'    : 'logic_spirit_mq_sun_block_sot',
        'tags'    : ("Spirit Temple",),
        'tooltip' : '''\
                    While adult can easily jump directly to the switch that
                    unbars the door to the sun block room, child Link cannot
                    make the jump without spawning a Song of Time block to
                    jump from. You can skip this by throwing the crate down
                    onto the switch from above, which does unbar the door,
                    however the crate immediately breaks, so you must move
                    quickly to get through the door before it closes back up.
                    '''},
    'Shadow Trial MQ Torch with Bow': {
        'name'    : 'logic_shadow_trial_mq',
        'tags'    : ("Ganon's Castle",),
        'tooltip' : '''\
                    You can light the torch in this room without a fire
                    source by shooting an arrow through the lit torch
                    at the beginning of the room. Because the room is
                    so dark and the unlit torch is so far away, it can
                    be difficult to aim the shot correctly.
                    '''},
    'Forest Temple NE Outdoors Ledge with Hover Boots': {
        'name'    : 'logic_forest_outdoors_ledge',
        'tags'    : ("Forest Temple", "Entrance",),
        'tooltip' : '''\
                    With precise Hover Boots movement you can fall down
                    to this ledge from upper balconies. If done precisely
                    enough, it is not necessary to take fall damage.
                    In MQ, this skips a Longshot requirement.
                    In Vanilla, this can skip a Hookshot requirement in
                    entrance randomizer.
                    '''},
    'Water Temple Boss Key Region with Hover Boots': {
        'name'    : 'logic_water_boss_key_region',
        'tags'    : ("Water Temple",),
        'tooltip' : '''\
                    With precise Hover Boots movement it is possible
                    to reach the boss key chest's region without
                    needing the Longshot. It is not necessary to take
                    damage from the spikes. The Gold Skulltula Token
                    in the following room can also be obtained with
                    just the Hover Boots.
                    '''},
    'Water Temple MQ North Basement GS without Small Key': {
        'name'    : 'logic_water_mq_locked_gs',
        'tags'    : ("Water Temple", "Skulltulas",),
        'tooltip' : '''\
                    There is an invisible Hookshot target that can be used
                    to get over the gate that blocks you from going to this
                    Skulltula early. This avoids going through some rooms
                    that normally require a Small Key to access. If "Water
                    Temple North Basement Ledge with Precise Jump" is not
                    enabled, this also skips needing Hover Boots or
                    Scarecrow's Song to reach the locked door.
                    '''},
    'Water Temple Falling Platform Room GS with Hookshot': {
        'name'    : 'logic_water_falling_platform_gs_hookshot',
        'tags'    : ("Water Temple", "Skulltulas",),
        'tooltip' : '''\
                    If you stand on the very edge of the platform, this
                    Gold Skulltula can be obtained with only the Hookshot.
                    '''},
    'Water Temple Falling Platform Room GS with Boomerang': {
        'name'    : 'logic_water_falling_platform_gs_boomerang',
        'tags'    : ("Water Temple", "Skulltulas", "Entrance",),
        'tooltip' : '''\
                    If you stand on the very edge of the platform, this
                    Gold Skulltula can be obtained with only the Boomerang.
                    '''},
    'Water Temple River GS without Iron Boots': {
        'name'    : 'logic_water_river_gs',
        'tags'    : ("Water Temple", "Skulltulas",),
        'tooltip' : '''\
                    Standing on the exposed ground toward the end of
                    the river, a precise Longshot use can obtain the
                    token. The Longshot cannot normally reach far
                    enough to kill the Skulltula, however. You'll
                    first have to find some other way of killing it.
                    '''},
    'Water Temple Entry without Iron Boots using Hookshot': {
        'name'    : 'logic_water_hookshot_entry',
        'tags'    : ("Lake Hylia",),
        'tooltip' : '''\
                    When entering Water Temple using Gold Scale instead
                    of Iron Boots, the Longshot is usually used to be
                    able to hit the switch and open the gate. But, by
                    standing in a particular spot, the switch can be hit
                    with only the reach of the Hookshot.
                    '''},
    'Death Mountain Trail Climb with Hover Boots': {
        'name'    : 'logic_dmt_climb_hovers',
        'tags'    : ("Death Mountain Trail",),
        'tooltip' : '''\
                    It is possible to use the Hover Boots to bypass
                    needing to destroy the boulders blocking the path
                    to the top of Death Mountain.
                    '''},
    'Death Mountain Trail Upper Red Rock GS without Hammer': {
        'name'    : 'logic_trail_gs_upper',
        'tags'    : ("Death Mountain Trail", "Skulltulas",),
        'tooltip' : '''\
                    After killing the Skulltula, the token can be collected
                    by backflipping into the rock at the correct angle.
                    '''},
    'Death Mountain Trail Lower Red Rock GS with Hookshot': {
        'name'    : 'logic_trail_gs_lower_hookshot',
        'tags'    : ("Death Mountain Trail", "Skulltulas",),
        'tooltip' : '''\
                    After killing the Skulltula, the token can be fished
                    out of the rock without needing to destroy it, by
                    using the Hookshot in the correct way.
                    '''},
    'Death Mountain Trail Lower Red Rock GS with Hover Boots': {
        'name'    : 'logic_trail_gs_lower_hovers',
        'tags'    : ("Death Mountain Trail", "Skulltulas",),
        'tooltip' : '''\
                    After killing the Skulltula, the token can be
                    collected without needing to destroy the rock by
                    backflipping down onto it with the Hover Boots.
                    First use the Hover Boots to stand on a nearby
                    fence, and go for the Skulltula Token from there.
                    '''},
    'Death Mountain Trail Lower Red Rock GS with Magic Bean': {
        'name'    : 'logic_trail_gs_lower_bean',
        'tags'    : ("Death Mountain Trail", "Skulltulas",),
        'tooltip' : '''\
                    After killing the Skulltula, the token can be
                    collected without needing to destroy the rock by
                    jumping down onto it from the bean plant,
                    midflight, with precise timing and positioning.
                    '''},
    'Death Mountain Crater Upper to Lower with Hammer': {
        'name'    : 'logic_crater_upper_to_lower',
        'tags'    : ("Death Mountain Crater",),
        'tooltip' : '''\
                    With the Hammer, you can jump slash the rock twice
                    in the same jump in order to destroy it before you
                    fall into the lava.
                    '''},
    'Zora\'s Domain Entry with Hover Boots': {
        'name'    : 'logic_zora_with_hovers',
        'tags'    : ("Zora's River",),
        'tooltip' : '''\
                    Can hover behind the waterfall as adult.
                    '''},
    'Zora\'s Domain GS with No Additional Items': {
        'name'    : 'logic_domain_gs',
        'tags'    : ("Zora's Domain", "Skulltulas",),
        'tooltip' : '''\
                    A precise jump slash can kill the Skulltula and
                    recoil back onto the top of the frozen waterfall.
                    To kill it, the logic normally guarantees one of
                    Hookshot, Bow, or Magic.
                    '''},
    'Skip King Zora as Adult with Nothing': {
        'name'    : 'logic_king_zora_skip',
        'tags'    : ("Zora's Domain",),
        'tooltip' : '''\
                    With a precise jump as adult, it is possible to
                    get on the fence next to King Zora from the front
                    to access Zora's Fountain.
                    '''},
    'Shadow Temple River Statue with Bombchu': {
        'name'    : 'logic_shadow_statue',
        'tags'    : ("Shadow Temple",),
        'tooltip' : '''\
                    By sending a Bombchu around the edge of the
                    gorge, you can knock down the statue without
                    needing a Bow.
                    Applies in both vanilla and MQ Shadow.
                    '''},
    'Stop Link the Goron with Din\'s Fire': {
        'name'    : 'logic_link_goron_dins',
        'tags'    : ("Goron City",),
        'tooltip' : '''\
                    The timing is quite awkward.
                    '''},
    'Fire Temple Song of Time Room GS without Song of Time': {
        'name'    : 'logic_fire_song_of_time',
        'tags'    : ("Fire Temple", "Skulltulas",),
        'tooltip' : '''\
                    A precise jump can be used to reach this room.
                    '''},
    'Fire Temple Climb without Strength': {
        'name'    : 'logic_fire_strength',
        'tags'    : ("Fire Temple",),
        'tooltip' : '''\
                    A precise jump can be used to skip
                    pushing the block.
                    '''},
    'Fire Temple MQ Big Lava Room Blocked Door without Hookshot': {
        'name'    : 'logic_fire_mq_blocked_chest',
        'tags'    : ("Fire Temple",),
        'tooltip' : '''\
                    There is a gap between the hitboxes of the flame
                    wall in the big lava room. If you know where this
                    gap is located, you can jump through it and skip
                    needing to use the Hookshot. To do this without
                    taking damage is more precise.
                    '''},
    'Fire Temple MQ Lower to Upper Lizalfos Maze with Precise Jump': {
        'name'    : 'logic_fire_mq_maze_jump',
        'tags'    : ("Fire Temple",),
        'tooltip' : '''\
                    A precise jump off of a crate can be used to
                    climb to the upper maze without needing to spawn
                    and use the Hookshot targets. This trick
                    supersedes both "Fire Temple MQ Lower to Upper
                    Lizalfos Maze with Hover Boots" and "Fire Temple
                    MQ Lizalfos Maze Side Room without Box".
                    '''},
    'Light Trial MQ without Hookshot': {
        'name'    : 'logic_light_trial_mq',
        'tags'    : ("Ganon's Castle",),
        'tooltip' : '''\
                    If you move quickly you can sneak past the edge of
                    a flame wall before it can rise up to block you.
                    In this case to do it without taking damage is
                    especially precise.
                    '''},
    'Ice Cavern MQ Scarecrow GS with No Additional Items': {
        'name'    : 'logic_ice_mq_scarecrow',
        'tags'    : ("Ice Cavern", "Skulltulas",),
        'tooltip' : '''\
                    A precise jump can be used to reach this alcove.
                    '''},
    'Ice Cavern MQ Red Ice GS without Song of Time': {
        'name'    : 'logic_ice_mq_red_ice_gs',
        'tags'    : ("Ice Cavern", "Skulltulas",),
        'tooltip' : '''\
                    If you side-hop into the perfect position, you
                    can briefly stand on the platform with the red
                    ice just long enough to dump some blue fire.
                    '''},
    'Ice Cavern Block Room GS with Hover Boots': {
        'name'    : 'logic_ice_block_gs',
        'tags'    : ("Ice Cavern", "Skulltulas",),
        'tooltip' : '''\
                    The Hover Boots can be used to get in front of the
                    Skulltula to kill it with a jump slash. Then, the
                    Hover Boots can again be used to obtain the Token,
                    all without Hookshot or Boomerang.
                    '''},
    'Reverse Wasteland': {
        'name'    : 'logic_reverse_wasteland',
        'tags'    : ("Haunted Wasteland",),
        'tooltip' : '''\
                    By memorizing the path, you can travel through the
                    Wasteland in reverse.
                    Note that jumping to the carpet merchant as child
                    typically requires a fairly precise jump slash.
                    The equivalent trick for going forward through the
                    Wasteland is "Lensless Wasteland".
                    To cross the river of sand with no additional items,
                    be sure to also enable "Wasteland Crossing without
                    Hover Boots or Longshot".
                    Unless all overworld entrances are randomized, child
                    Link will not be expected to do anything at Gerudo's
                    Fortress.
                    '''},
    'Zora\'s River Upper Freestanding PoH as Adult with Nothing': {
        'name'    : 'logic_zora_river_upper',
        'tags'    : ("Zora's River",),
        'tooltip' : '''\
                    Adult can reach this PoH with a precise jump,
                    no Hover Boots required.
                    '''},
    'Shadow Temple MQ Truth Spinner Gap with Longshot': {
        'name'    : 'logic_shadow_mq_gap',
        'tags'    : ("Shadow Temple",),
        'tooltip' : '''\
                    You can Longshot a torch and jump-slash recoil onto
                    the tongue. It works best if you Longshot the right
                    torch from the left side of the room.
                    '''},
    'Lost Woods Adult GS without Bean': {
        'name'    : 'logic_lost_woods_gs_bean',
        'tags'    : ("the Lost Woods", "Skulltulas",),
        'tooltip' : '''\
                    You can collect the token with a precise
                    Hookshot use, as long as you can kill the
                    Skulltula somehow first. It can be killed
                    using Longshot, Bow, Bombchus or Din's Fire.
                    '''},
    'Jabu Near Boss GS without Boomerang as Adult': {
        'name'    : 'logic_jabu_boss_gs_adult',
        'tags'    : ("Jabu Jabu's Belly", "Skulltulas", "Entrance",),
        'tooltip' : '''\
                    You can easily get over to the door to the
                    near boss area early with Hover Boots. The
                    tricky part is getting through the door
                    without being able to use a box to keep the
                    switch pressed. One way is to quickly roll
                    from the switch and open the door before it
                    closes.
                    '''},
    'Kakariko Rooftop GS with Hover Boots': {
        'name'    : 'logic_kakariko_rooftop_gs',
        'tags'    : ("Kakariko Village", "Skulltulas",),
        'tooltip' : '''\
                    Take the Hover Boots from the entrance to Impa's
                    House over to the rooftop of Skulltula House. From
                    there, a precise Hover Boots backwalk with backflip
                    can be used to get onto a hill above the side of
                    the village. And then from there you can Hover onto
                    Impa's rooftop to kill the Skulltula and backflip
                    into the token.
                    '''},
    'Graveyard Freestanding PoH with Boomerang': {
        'name'    : 'logic_graveyard_poh',
        'tags'    : ("the Graveyard",),
        'tooltip' : '''\
                    Using a precise moving setup you can obtain
                    the Piece of Heart by having the Boomerang
                    interact with it along the return path.
                    '''},
    'Hyrule Castle Storms Grotto GS with Just Boomerang': {
        'name'    : 'logic_castle_storms_gs',
        'tags'    : ("Hyrule Castle", "Skulltulas",),
        'tooltip' : '''\
                    With precise throws, the Boomerang alone can
                    kill the Skulltula and collect the token,
                    without first needing to blow up the wall.
                    '''},
    'Death Mountain Trail Soil GS without Destroying Boulder': {
        'name'    : 'logic_dmt_soil_gs',
        'tags'    : ("Death Mountain Trail", "Skulltulas",),
        'tooltip' : '''\
                    Bugs will go into the soft soil even while the boulder is
                    still blocking the entrance.
                    Then, using a precise moving setup you can kill the Gold
                    Skulltula and obtain the token by having the Boomerang
                    interact with it along the return path.
                    '''},
    'Gerudo Training Ground Left Side Silver Rupees without Hookshot': {
        'name'    : 'logic_gtg_without_hookshot',
        'tags'    : ("Gerudo Training Ground",),
        'tooltip' : '''\
                    After collecting the rest of the silver rupees in the room,
                    you can reach the final silver rupee on the ceiling by being
                    pulled up into it after getting grabbed by the Wallmaster.
                    Then, you must also reach the exit of the room without the
                    use of the Hookshot. If you move quickly you can sneak past
                    the edge of a flame wall before it can rise up to block you.
                    To do so without taking damage is more precise.
                    '''},
    'Gerudo Training Ground MQ Left Side Silver Rupees without Hookshot': {
        'name'    : 'logic_gtg_mq_without_hookshot',
        'tags'    : ("Gerudo Training Ground",),
        'tooltip' : '''\
                    After collecting the rest of the silver rupees in the room,
                    you can reach the final silver rupee on the ceiling by being
                    pulled up into it after getting grabbed by the Wallmaster.
                    The Wallmaster will not track you to directly underneath the
                    rupee. You should take the last step to be under the rupee
                    after the Wallmaster has begun its attempt to grab you.
                    Also included with this trick is that fact that the switch
                    that unbars the door to the final chest of GTG can be hit
                    without a projectile, using a precise jump slash.
                    This trick supersedes "Gerudo Training Ground MQ Left Side
                    Silver Rupees with Hookshot".
                    '''},
    'Reach Gerudo Training Ground Fake Wall Ledge with Hover Boots': {
        'name'    : 'logic_gtg_fake_wall',
        'tags'    : ("Gerudo Training Ground",),
        'tooltip' : '''\
                    A precise Hover Boots use from the top of the chest can allow
                    you to grab the ledge without needing the usual requirements.
                    In Master Quest, this always skips a Song of Time requirement.
                    In Vanilla, this skips a Hookshot requirement, but is only
                    relevant if "Gerudo Training Ground Left Side Silver Rupees
                    without Hookshot" is enabled.
                    '''},
    'Water Temple Cracked Wall with No Additional Items': {
        'name'    : 'logic_water_cracked_wall_nothing',
        'tags'    : ("Water Temple",),
        'tooltip' : '''\
                    A precise jump slash (among other methods) will
                    get you to the cracked wall without needing the
                    Hover Boots or to raise the water to the middle
                    level. This trick supersedes "Water Temple
                    Cracked Wall with Hover Boots".
                    '''},
    'Water Temple North Basement Ledge with Precise Jump': {
        'name'    : 'logic_water_north_basement_ledge_jump',
        'tags'    : ("Water Temple",),
        'tooltip' : '''\
                    In the northern basement there's a ledge from where, in
                    vanilla Water Temple, boulders roll out into the room.
                    Normally to jump directly to this ledge logically
                    requires the Hover Boots, but with precise jump, it can
                    be done without them. This trick applies to both
                    Vanilla and Master Quest.
                    '''},
    'Water Temple Torch Longshot': {
        'name'    : 'logic_water_temple_torch_longshot',
        'tags'    : ("Water Temple",),
        'tooltip' : '''\
                    Stand on the eastern side of the central pillar and longshot
                    the torches on the bottom level. Swim through the corridor
                    and float up to the top level. This allows access to this
                    area and lower water levels without Iron Boots.
                    The majority of the tricks that allow you to skip Iron Boots
                    in the Water Temple are not going to be relevant unless this
                    trick is first enabled.
                    '''},
    'Water Temple Central Pillar GS with Farore\'s Wind': {
        'name'    : 'logic_water_central_gs_fw',
        'tags'    : ("Water Temple", "Skulltulas",),
        'tooltip' : '''\
                    If you set Farore's Wind inside the central pillar
                    and then return to that warp point after raising
                    the water to the highest level, you can obtain this
                    Skulltula Token with Hookshot or Boomerang.
                    '''},
    'Water Temple Central Pillar GS with Iron Boots': {
        'name'    : 'logic_water_central_gs_irons',
        'tags'    : ("Water Temple", "Skulltulas",),
        'tooltip' : '''\
                    After opening the middle water level door into the
                    central pillar, the door will stay unbarred so long
                    as you do not leave the room -- even if you were to
                    raise the water up to the highest level. With the
                    Iron Boots to go through the door after the water has
                    been raised, you can obtain the Skulltula Token with
                    the Hookshot.
                    '''},
    'Water Temple Boss Key Jump Dive': {
        'name'    : 'logic_water_bk_jump_dive',
        'tags'    : ("Water Temple",),
        'tooltip' : '''\
                    Stand on the very edge of the raised corridor leading from the
                    push block room to the rolling boulder corridor. Face the
                    gold skulltula on the waterfall and jump over the boulder
                    corridor floor into the pool of water, swimming right once
                    underwater. This allows access to the boss key room without
                    Iron boots.
                    '''},
    'Water Temple Dragon Statue Jump Dive': {
        'name'    : 'logic_water_dragon_jump_dive',
        'tags'    : ("Water Temple",),
        'tooltip' : '''\
                    If you come into the dragon statue room from the
                    serpent river, you can jump down from above and get
                    into the tunnel without needing either Iron Boots
                    or a Scale. This trick applies to both Vanilla and
                    Master Quest. In Vanilla, you must shoot the switch
                    from above with the Bow, and then quickly get
                    through the tunnel before the gate closes.
                    '''},
    'Water Temple Dragon Statue Switch from Above the Water as Adult': {
        'name'    : 'logic_water_dragon_adult',
        'tags'    : ("Water Temple",),
        'tooltip' : '''\
                    Normally you need both Hookshot and Iron Boots to hit the
                    switch and swim through the tunnel to get to the chest. But
                    by hitting the switch from dry land, using one of Bombchus,
                    Hookshot, or Bow, it is possible to skip one or both of
                    those requirements. After the gate has been opened, besides 
                    just using the Iron Boots, a well-timed dive with at least
                    the Silver Scale could be used to swim through the tunnel. If
                    coming from the serpent river, a jump dive can also be used
                    to get into the tunnel.
                    '''},
    'Water Temple Dragon Statue Switch from Above the Water as Child': {
        'name'    : 'logic_water_dragon_child',
        'tags'    : ("Water Temple", "Entrance",),
        'tooltip' : '''\
                    It is possible for child to hit the switch from dry land
                    using one of Bombchus, Slingshot or Boomerang. Then, to
                    get to the chest, child can dive through the tunnel using
                    at least the Silver Scale. The timing and positioning of
                    this dive needs to be perfect to actually make it under the
                    gate, and it all needs to be done very quickly to be able to
                    get through before the gate closes. Be sure to enable "Water
                    Temple Dragon Statue Switch from Above the Water as Adult"
                    for adult's variant of this trick.
                    '''},
    'Goron City Maze Left Chest with Hover Boots': {
        'name'    : 'logic_goron_city_leftmost',
        'tags'    : ("Goron City",),
        'tooltip' : '''\
                    A precise backwalk starting from on top of the
                    crate and ending with a precisely-timed backflip
                    can reach this chest without needing either
                    the Hammer or Silver Gauntlets.
                    '''},
    'Goron City Grotto with Hookshot While Taking Damage': {
        'name'    : 'logic_goron_grotto',
        'tags'    : ("Goron City",),
        'tooltip' : '''\
                    It is possible to reach the Goron City Grotto by
                    quickly using the Hookshot while in the midst of
                    taking damage from the lava floor. This trick will
                    not be expected on OHKO or quadruple damage.
                    '''},
    'Deku Tree Basement without Slingshot': {
        'name'    : 'logic_deku_b1_skip',
        'tags'    : ("Deku Tree",),
        'tooltip' : '''\
                    A precise jump can be used to skip
                    needing to use the Slingshot to go
                    around B1 of the Deku Tree. If used
                    with the "Closed Forest" setting, a
                    Slingshot will not be guaranteed to
                    exist somewhere inside the Forest.
                    This trick applies to both Vanilla
                    and Master Quest.
                    '''},
    'Spirit Temple Lower Adult Switch with Bombs': {
        'name'    : 'logic_spirit_lower_adult_switch',
        'tags'    : ("Spirit Temple",),
        'tooltip' : '''\
                    A bomb can be used to hit the switch on the ceiling,
                    but it must be thrown from a particular distance
                    away and with precise timing.
                    '''},
    'Forest Temple Outside Backdoor with Jump Slash': {
        'name'    : 'logic_forest_outside_backdoor',
        'tags'    : ("Forest Temple",),
        'tooltip' : '''\
                    With a precise jump slash from above,
                    you can reach the backdoor to the west
                    courtyard without Hover Boots. Applies
                    to both Vanilla and Master Quest.
                    '''},
    'Forest Temple East Courtyard Door Frame with Hover Boots': {
        'name'    : 'logic_forest_door_frame',
        'tags'    : ("Forest Temple",),
        'tooltip' : '''\
                    A precise Hover Boots movement from the upper
                    balconies in this courtyard can be used to get on
                    top of the door frame. Applies to both Vanilla and
                    Master Quest. In Vanilla, from on top the door
                    frame you can summon Pierre, allowing you to access
                    the falling ceiling room early. In Master Quest,
                    this allows you to obtain the GS on the door frame
                    as adult without Hookshot or Song of Time.
                    '''},
    'Dodongo\'s Cavern MQ Early Bomb Bag Area as Child': {
        'name'    : 'logic_dc_mq_child_bombs',
        'tags'    : ("Dodongo's Cavern",),
        'tooltip' : '''\
                    With a precise jump slash from above, you
                    can reach the Bomb Bag area as only child
                    without needing a Slingshot. You will
                    take fall damage.
                    '''},
    'Dodongo\'s Cavern Two Scrub Room with Strength': {
        'name'    : 'logic_dc_scrub_room',
        'tags'    : ("Dodongo's Cavern",),
        'tooltip' : '''\
                    With help from a conveniently-positioned block,
                    Adult can quickly carry a bomb flower over to
                    destroy the mud wall blocking the room with two
                    Deku Scrubs.
                    '''},
    'Dodongo\'s Cavern Child Slingshot Skips': {
        'name'    : 'logic_dc_slingshot_skip',
        'tags'    : ("Dodongo's Cavern",),
        'tooltip' : '''\
                    With precise platforming, child can cross the
                    platforms while the flame circles are there.
                    When enabling this trick, it's recommended that
                    you also enable the Adult variant: "Dodongo's
                    Cavern Spike Trap Room Jump without Hover Boots".
                    '''},
    'Dodongo\'s Cavern MQ Light the Eyes with Strength': {
        'name'    : 'logic_dc_mq_eyes',
        'tags'    : ("Dodongo's Cavern",),
        'tooltip' : '''\
                    If you move very quickly, it is possible to use
                    the bomb flower at the top of the room to light
                    the eyes. To perform this trick as child is
                    significantly more difficult, but child will never
                    be expected to do so unless "Dodongo's Cavern MQ
                    Back Areas as Child without Explosives" is enabled.
                    Also, the bombable floor before King Dodongo can be
                    destroyed with Hammer if hit in the very center.
                    '''},
    'Dodongo\'s Cavern MQ Back Areas as Child without Explosives': {
        'name'    : 'logic_dc_mq_child_back',
        'tags'    : ("Dodongo's Cavern",),
        'tooltip' : '''\
                    Child can progress through the back areas without
                    explosives by throwing a pot at a switch to lower a
                    fire wall, and by defeating Armos to detonate bomb
                    flowers (among other methods). While these techniques
                    themselves are relatively simple, they're not
                    relevant unless "Dodongo's Cavern MQ Light the Eyes
                    with Strength" is enabled, which is a trick that
                    is particularly difficult for child to perform.
                    '''},
    'Rolling Goron (Hot Rodder Goron) as Child with Strength': {
        'name'    : 'logic_child_rolling_with_strength',
        'tags'    : ("Goron City",),
        'tooltip' : '''\
                    Use the bombflower on the stairs or near Medigoron.
                    Timing is tight, especially without backwalking.
                    '''},
    'Goron City Spinning Pot PoH with Bombchu': {
        'name'    : 'logic_goron_city_pot',
        'tags'    : ("Goron City",),
        'tooltip' : '''\
                    A Bombchu can be used to stop the spinning
                    pot, but it can be quite finicky to get it
                    to work.
                    '''},
    'Gerudo Valley Crate PoH as Adult with Hover Boots': {
        'name'    : 'logic_valley_crate_hovers',
        'tags'    : ("Gerudo Valley",),
        'tooltip' : '''\
                    From the far side of Gerudo Valley, a precise
                    Hover Boots movement and jump-slash recoil can
                    allow adult to reach the ledge with the crate
                    PoH without needing Longshot. You will take 
                    fall damage.
                    '''},
    'Jump onto the Lost Woods Bridge as Adult with Nothing': {
        'name'    : 'logic_lost_woods_bridge',
        'tags'    : ("the Lost Woods", "Entrance",),
        'tooltip' : '''\
                    With very precise movement it's possible for
                    adult to jump onto the bridge without needing
                    Longshot, Hover Boots, or Bean.
                    '''},
    'Spirit Trial without Hookshot': {
        'name'    : 'logic_spirit_trial_hookshot',
        'tags'    : ("Ganon's Castle",),
        'tooltip' : '''\
                    A precise jump off of an Armos can
                    collect the highest rupee.
                    '''},
    'Shadow Temple Stone Umbrella Skip': {
        'name'    : 'logic_shadow_umbrella',
        'tags'    : ("Shadow Temple",),
        'tooltip' : '''\
                    A very precise Hover Boots movement
                    from off of the lower chest can get you
                    on top of the crushing spikes without
                    needing to pull the block. Applies to
                    both Vanilla and Master Quest.
                    '''},
    'Shadow Temple Falling Spikes GS with Hover Boots': {
        'name'    : 'logic_shadow_umbrella_gs',
        'tags'    : ("Shadow Temple", "Skulltulas",),
        'tooltip' : '''\
                    After killing the Skulltula, a very precise Hover Boots
                    movement from off of the lower chest can get you on top
                    of the crushing spikes without needing to pull the block.
                    From there, another very precise Hover Boots movement can
                    be used to obtain the token without needing the Hookshot.
                    Applies to both Vanilla and Master Quest. For obtaining
                    the chests in this room with just Hover Boots, be sure to
                    enable "Shadow Temple Stone Umbrella Skip".
                    '''},
    'Water Temple Central Bow Target without Longshot or Hover Boots': {
        'name'    : 'logic_water_central_bow',
        'tags'    : ("Water Temple",),
        'tooltip' : '''\
                    A very precise Bow shot can hit the eye
                    switch from the floor above. Then, you
                    can jump down into the hallway and make
                    through it before the gate closes.
                    It can also be done as child, using the
                    Slingshot instead of the Bow.
                    '''},
    'Fire Temple East Tower without Scarecrow\'s Song': {
        'name'    : 'logic_fire_scarecrow',
        'tags'    : ("Fire Temple",),
        'tooltip' : '''\
                    Also known as "Pixelshot".
                    The Longshot can reach the target on the elevator
                    itself, allowing you to skip needing to spawn the
                    scarecrow.
                    '''},
    'Fire Trial MQ with Hookshot': {
        'name'    : 'logic_fire_trial_mq',
        'tags'    : ("Ganon's Castle",),
        'tooltip' : '''\
                    It's possible to hook the target at the end of
                    fire trial with just Hookshot, but it requires
                    precise aim and perfect positioning. The main
                    difficulty comes from getting on the very corner
                    of the obelisk without falling into the lava.
                    '''},
    'Shadow Temple Entry with Fire Arrows': {
        'name'    : 'logic_shadow_fire_arrow_entry',
        'tags'    : ("Shadow Temple",),
        'tooltip' : '''\
                    It is possible to light all of the torches to
                    open the Shadow Temple entrance with just Fire
                    Arrows, but you must be very quick, precise,
                    and strategic with how you take your shots.
                    '''},
    'Lensless Wasteland': {
        'name'    : 'logic_lens_wasteland',
        'tags'    : ("Lens of Truth","Haunted Wasteland",),
        'tooltip' : '''\
                    By memorizing the path, you can travel through the
                    Wasteland without using the Lens of Truth to see
                    the Poe.
                    The equivalent trick for going in reverse through
                    the Wasteland is "Reverse Wasteland".
                    '''},
    'Bottom of the Well without Lens of Truth': {
        'name'    : 'logic_lens_botw',
        'tags'    : ("Lens of Truth","Bottom of the Well",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Bottom of the Well.
                    '''},
    'Ganon\'s Castle MQ without Lens of Truth': {
        'name'    : 'logic_lens_castle_mq',
        'tags'    : ("Lens of Truth","Ganon's Castle",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Ganon's Castle MQ.
                    '''},
    'Ganon\'s Castle without Lens of Truth': {
        'name'    : 'logic_lens_castle',
        'tags'    : ("Lens of Truth","Ganon's Castle",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Ganon's Castle.
                    '''},
    'Gerudo Training Ground MQ without Lens of Truth': {
        'name'    : 'logic_lens_gtg_mq',
        'tags'    : ("Lens of Truth","Gerudo Training Ground",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Gerudo Training Ground MQ.
                    '''},
    'Gerudo Training Ground without Lens of Truth': {
        'name'    : 'logic_lens_gtg',
        'tags'    : ("Lens of Truth","Gerudo Training Ground",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Gerudo Training Ground.
                    '''},
    'Jabu MQ without Lens of Truth': {
        'name'    : 'logic_lens_jabu_mq',
        'tags'    : ("Lens of Truth","Jabu Jabu's Belly",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Jabu MQ.
                    '''},
    'Shadow Temple MQ before Invisible Moving Platform without Lens of Truth': {
        'name'    : 'logic_lens_shadow_mq',
        'tags'    : ("Lens of Truth","Shadow Temple",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Shadow Temple MQ before the invisible moving platform.
                    '''},
    'Shadow Temple MQ beyond Invisible Moving Platform without Lens of Truth': {
        'name'    : 'logic_lens_shadow_mq_back',
        'tags'    : ("Lens of Truth","Shadow Temple",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Shadow Temple MQ beyond the invisible moving platform.
                    '''},
    'Shadow Temple before Invisible Moving Platform without Lens of Truth': {
        'name'    : 'logic_lens_shadow',
        'tags'    : ("Lens of Truth","Shadow Temple",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Shadow Temple before the invisible moving platform.
                    '''},
    'Shadow Temple beyond Invisible Moving Platform without Lens of Truth': {
        'name'    : 'logic_lens_shadow_back',
        'tags'    : ("Lens of Truth","Shadow Temple",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Shadow Temple beyond the invisible moving platform.
                    '''},
    'Spirit Temple MQ without Lens of Truth': {
        'name'    : 'logic_lens_spirit_mq',
        'tags'    : ("Lens of Truth","Spirit Temple",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Spirit Temple MQ.
                    '''},
    'Spirit Temple without Lens of Truth': {
        'name'    : 'logic_lens_spirit',
        'tags'    : ("Lens of Truth","Spirit Temple",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Spirit Temple.
                    '''},
}


# a list of the possible settings
setting_infos = [
    # Web Only Settings
    Setting_Info(
        name        = 'web_wad_file',
        type        = str,
        gui_text    = "WAD File",
        gui_type    = "Fileinput",
        shared      = False,
        choices     = {},
        gui_tooltip = "Your original OoT 1.2 NTSC-U / NTSC-J WAD file (.wad)",
        gui_params  = {
            "file_types": [
                {
                  "name": "WAD Files",
                  "extensions": [ "wad" ]
                },
                {
                  "name": "All Files",
                  "extensions": [ "*" ]
                }
            ],
            "hide_when_disabled": True,
        }
    ),
    Setting_Info(
        name        = 'web_common_key_file',
        type        = str,
        gui_text    = "Wii Common Key File",
        gui_type    = "Fileinput",
        shared      = False,
        choices     = {},
        gui_tooltip = """\
            The Wii Common Key is a copyrighted 32 character string needed for WAD encryption.
            Google to find it! Do not ask on Discord!
        """,
        gui_params  = {
            "file_types": [
                {
                  "name": "BIN Files",
                  "extensions": [ "bin" ]
                },
                {
                  "name": "All Files",
                  "extensions": [ "*" ]
                }
            ],
            "hide_when_disabled": True,
        }
    ),
    Setting_Info(
        name        = 'web_common_key_string',
        type        = str,
        gui_text    = "Alternatively Enter Wii Common Key",
        gui_type    = "Textinput",
        shared      = False,
        choices     = {},
        gui_tooltip = """\
            The Wii Common Key is a copyrighted 32 character string needed for WAD encryption.
            Google to find it! Do not ask on Discord!
        """,
        gui_params  = {
            "size"               : "full",
            "max_length"         : 32,
            "hide_when_disabled" : True,
        }
    ),
    Setting_Info(
        name        = 'web_wad_channel_id',
        type        = str,
        gui_text    = "WAD Channel ID",
        gui_type    = "Textinput",
        shared      = False,
        choices     = {},
        default     = "NICE",
        gui_tooltip = """\
            4 characters, should end with E to ensure Dolphin compatibility.
            Note: If you have multiple OoTR WAD files with different Channel IDs installed, the game can crash on a soft reset. Use a Title Deleter to remove old WADs.
        """,
        gui_params  = {
            "size"               : "small",
            "max_length"         : 4,
            "no_line_break"      : True,
            "hide_when_disabled" : True,
        }
    ),
    Setting_Info(
        name        = 'web_wad_channel_title',
        type        = str,
        gui_text    = "WAD Channel Title",
        gui_type    = "Textinput",
        shared      = False,
        choices     = {},
        default     = "OoTRandomizer",
        gui_tooltip = "20 characters max",
        gui_params  = {
            "size"               : "medium",
            "max_length"         : 20,
            "hide_when_disabled" : True,
        }
    ),
    Setting_Info(
        name       = 'web_output_type',
        type       = str,
        gui_text   = "Output Type",
        gui_type   = "Radiobutton",
        shared     = False,
        choices    = {
            'z64' : ".z64 (N64/Emulator)",
            'wad' : ".wad (WiiVC)"
        },
        gui_params  = {
            "hide_when_disabled" : True,
        },
        default    = "z64",
        disable    = {
            'z64' : {'settings' : [
                'web_wad_file',
                'web_common_key_file',
                'web_common_key_string',
                'web_wad_channel_id',
                'web_wad_channel_title']
            }
        }
    ),
    Checkbutton(
        name           = 'web_persist_in_cache',
        gui_text       = 'Persist Files in Cache',
        default        = True,
        shared         = False,
    ),

    # Non-GUI Settings
    Checkbutton('cosmetics_only', None),
    Checkbutton('check_version', None),
    Checkbutton('output_settings', None),
    Checkbutton(
        name           = 'generate_from_file',
        gui_text       = 'Generate From Patch File',
        default        = False,
        disable        = {
            True : {
                'tabs' : ['main_tab', 'detailed_tab', 'starting_tab', 'other_tab'],
                'sections' : ['preset_section'],
                'settings' : ['count', 'create_spoiler', 'world_count', 'enable_distribution_file', 'distribution_file'],
            },
            False : {
                'settings' : ['repatch_cosmetics'],
            },
        },
        gui_params     = {
            'web:disable' : {
                False : {
                    'settings' : [
                        'rom','web_output_type','player_num',
                        'web_wad_file', 'web_common_key_file', 'web_common_key_string',
                        'web_wad_channel_id','web_wad_channel_title'
                    ],
                },
            }
        },
        shared         = False,
    ),
    Checkbutton(
        name           = 'enable_distribution_file',
        gui_text       = 'Enable Plandomizer (Advanced)',
        gui_tooltip    = '''\
            Optional. Use a plandomizer JSON file to get 
            total control over the item placement.
        ''',
        gui_params     = {
            'no_line_break': True,
        },
        default        = False,
        disable        = {
            False  : {'settings' : ['distribution_file']},
        },
        shared         = False,
    ),
    Checkbutton(
        name           = 'enable_cosmetic_file',
        gui_text       = 'Enable Cosmetic Plandomizer (Advanced)',
        gui_tooltip    = '''\
            Optional. Use a cosmetic plandomizer JSON file to get 
            more control over your cosmetic and sound settings.
        ''',
        default        = False,
        disable        = {
            False  : {'settings' : ['cosmetic_file']},
        },
        shared         = False,
    ),
    Setting_Info('distribution_file', str, "Plandomizer File", "Fileinput", False, {},
        gui_tooltip = """\
            Optional. Place a plandomizer JSON file here 
            to get total control over the item placement.
        """,
        gui_params = {
            "file_types": [
                {
                  "name": "JSON Files",
                  "extensions": [ "json" ]
                },
                {
                  "name": "All Files",
                  "extensions": [ "*" ]
                }
            ],
            "hide_when_disabled" : True,
        }),
    Setting_Info('cosmetic_file', str, "Cosmetic Plandomizer File", "Fileinput", False, {},
        gui_tooltip = """\
            Optional. Use a cosmetic plandomizer JSON file to get 
            more control over your cosmetic and sound settings.
        """,
        gui_params = {
            "file_types": [
                {
                  "name": "JSON Files",
                  "extensions": [ "json" ]
                },
                {
                  "name": "All Files",
                  "extensions": [ "*" ]
                }
            ],
            "hide_when_disabled" : True,
        }),
    Setting_Info('checked_version',   str, None, None, False, {}),
    Setting_Info('rom',               str, "Base ROM", "Fileinput", False, {},
        gui_params = {
            "file_types": [
                {
                  "name": "ROM Files",
                  "extensions": [ "z64", "n64" ]
                },
                {
                  "name": "All Files",
                  "extensions": [ "*" ]
                }
            ],
            "web:hide_when_disabled" : True,
        }),
    Setting_Info('output_dir',        str, "Output Directory", "Directoryinput", False, {}),
    Setting_Info('output_file',       str, None, None, False, {}),
    Setting_Info('seed',              str, None, None, False, {}),
    Setting_Info('patch_file',        str, "Patch File", "Fileinput", False, {},
        gui_params = {
            "file_types": [
                {
                  "name": "Patch File Archive",
                  "extensions": [ "zpfz", "zpf" ]
                },
                {
                  "name": "All Files",
                  "extensions": [ "*" ]
                }
            ],
        }),
    Setting_Info('count',             int, "Generation Count", "Numberinput", False, {},
        default        = 1,
        gui_params = {
            'min' : 1,
        }
    ),
    Setting_Info('world_count',       int, "Player Count", "Numberinput", True, {},
        default        = 1,
        gui_params = {
            'min' : 1,
            'max' : 255,
            'no_line_break'     : True,
            'web:max'           : 15,
            'web:no_line_break' : True,
        }
    ),
    Setting_Info('player_num',        int, "Player ID", "Numberinput", False, {},
        default        = 1,
        gui_params = {
            'min' : 1,
            'max' : 255,
        }
    ),

    # GUI Settings
    Setting_Info('presets',           str, "", "Presetinput", False, {},
        default        = "[New Preset]",
        gui_tooltip    = 'Select a setting preset to apply.',
    ),
    Setting_Info('open_output_dir',   str, "Open Output Directory", "Button", False, {},
        gui_params = {
            'function' : "openOutputDir",
            'no_line_break' : True,
        }
    ),
    Setting_Info('open_python_dir',   str, "Open App Directory", "Button", False, {},
        gui_params = {
            'function' : "openPythonDir",
        }
    ),
    Checkbutton(
        name           = 'repatch_cosmetics',
        gui_text       = 'Override Original Cosmetics',
        default        = True,
        disable        = {
            False : {
                'tabs': ['cosmetics_tab','sfx_tab'],
                'settings' : ['create_cosmetics_log', 'enable_cosmetic_file', 'cosmetic_file'],
            },
        },
        shared         = False,
    ),
    Checkbutton(
        name           = 'create_spoiler',
        gui_text       = 'Create Spoiler Log',
        gui_tooltip    = '''\
                         Enabling this will change the seed.
                         Warning: Only disable this if you don't want any help in solving this seed!
                         ''',
        default        = True,
        gui_params     = {
            'no_line_break' : True,
            'web:no_line_break' : False,
        },
        shared         = True,
    ),
    Checkbutton(
        name           = 'create_cosmetics_log',
        gui_text       = 'Create Cosmetics Log',
        default        = True,
        disabled_default = False,
    ),
    Setting_Info(
        name           = 'compress_rom',
        type           = str,
        gui_text       = "Output Type",
        gui_type       = "Radiobutton",
        shared         = False,
        choices        = {
            'True':  'Compressed [Stable]',
            'False': 'Uncompressed [Crashes]',
            'Patch': 'Patch File',
            'None':  'No Output',
        },
        default        = 'True',
        disable        = {
            'None'  : {'settings' : ['player_num', 'create_cosmetics_log', 'enable_cosmetic_file', 'cosmetic_file', 'rom']},
            'Patch' : {'settings' : ['player_num']}
        },
        gui_tooltip = '''\
            The first time compressed generation will take a while,
            but subsequent generations will be quick. It is highly
            recommended to compress or the game will crash
            frequently except on real N64 hardware.

            Patch files are used to send the patched data to other
            people without sending the ROM file.
        ''',
        gui_params={
            'horizontal': True
        },
    ),
    Checkbutton(
        name           = 'randomize_settings',
        gui_text       = 'Randomize Main Rule Settings',
        gui_tooltip    = '''\
                         Randomizes all settings on the 'Main Rules' tab, except:

                         - Logic Rules
                         - (Random) Number of MQ Dungeons
                         - Rainbow Bridge/LACS Requirements: Gold Skulltula Tokens
                         - Variable numbers of Spiritual Stones, Medallions, or Dungeons
                         for Rainbow Bridge and Ganon's Boss Key on LACS 
                         (you will always be required to obtain all the relevant rewards)
                         - Scrub Shuffle will either be "Off" or "On (Affordable)"
                         ''',
        default        = False,
        disable        = {
            True : {
                'sections' : ['open_section', 'shuffle_section', 'shuffle_dungeon_section'],
                'settings': ['starting_age', 'shuffle_interior_entrances', 'shuffle_grotto_entrances', 'shuffle_dungeon_entrances',
                             'shuffle_overworld_entrances', 'owl_drops', 'warp_songs', 'spawn_positions',
                             'triforce_hunt', 'triforce_goal_per_world', 'bombchus_in_logic', 'one_item_per_dungeon'],
            }
        },
        shared         = True,
    ),
    Combobox(
        name           = 'open_forest',
        gui_text       = 'Forest',
        default        = 'closed',
        choices        = {
            'open':        'Open Forest',
            'closed_deku': 'Closed Deku',
            'closed':      'Closed Forest',
            },
        gui_tooltip    = '''\
            'Open Forest': Mido no longer blocks the path to the
            Deku Tree, and the Kokiri boy no longer blocks the path
            out of the forest.
            
            'Closed Deku': The Kokiri boy no longer blocks the path
            out of the forest, but Mido still blocks the path to the
            Deku Tree, requiring Kokiri Sword and Deku Shield to access
            the Deku Tree.

            'Closed Forest': Beating Deku Tree is logically required
            to leave the forest area (Kokiri Forest/Lost Woods/Sacred Forest
            Meadow/Deku Tree), while the Kokiri Sword and a Deku Shield are
            required to access the Deku Tree. Items needed for this will be
            guaranteed inside the forest area. This setting is incompatible
            with starting as adult, and so Starting Age will be locked to Child.
            With either "Shuffle Interior Entrances" set to "All", "Shuffle 
            Overworld Entrances" on, "Randomize Warp Song Destinations" on 
            or "Randomize Overworld Spawns" on, Closed Forest will instead 
            be treated as Closed Deku with starting age Child and WILL NOT 
            guarantee that these items are available in the forest area.
        ''',
        shared         = True,
        disable        = {
            'closed' : {'settings' : ['starting_age']}
        },
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution': [
                ('open', 1),
                ('closed_deku', 1),
                ('closed', 1),
            ],
        },
    ),
    Combobox(
        name           = 'open_kakariko',
        gui_text       = 'Kakariko Gate',
        default        = 'closed',
        choices        = {
            'open':   'Open Gate',
            'zelda':  "Zelda's Letter Opens Gate",
            'closed': 'Closed Gate',
            },
        gui_tooltip    = '''\
            This changes the behavior of the Kakariko Gate to
            Death Mountain Trail as child. The gate is always
            open as adult.
            
            "Open Gate": The gate is always open instead of
            needing Zelda's Letter. The Happy Mask Shop opens
            upon obtaining Zelda's Letter without needing to
            show it to the guard.
            
            "Zelda's Letter Opens Gate": The gate is closed at
            the start, but opens automatically along with the
            Happy Mask Shop upon obtaining Zelda's Letter.
            
            "Closed": The gate and the Happy Mask Shop both remain closed
            until showing Zelda's Letter to the guard in Kakariko.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'open_door_of_time',
        gui_text       = 'Open Door of Time',
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
    Combobox(
        name           = 'zora_fountain',
        gui_text       = 'Zora\'s Fountain',
        default        = 'closed',
        choices        = {
            'closed': 'Default Behavior (Closed)',
            'adult':  'Open For Adult',
            'open':   'Always Open',
        },
        gui_tooltip    = '''\
            'Default Behavior': King Zora obstructs the way to
            Zora's Fountain. Ruto's Letter must be shown as
            child in order to move him for both eras.

            'Open For Adult': King Zora is always moved in 
            the adult era. This means Ruto's Letter is only
            required to access Zora's Fountain as child.

            'Always Open': King Zora starts as moved in
            both the child and adult eras. This also removes 
            Ruto's Letter from the pool since it can't be used.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Combobox(
        name           = 'gerudo_fortress',
        gui_text       = 'Gerudo\'s Fortress',
        default        = 'normal',
        choices        = {
            'normal': 'Default Behavior',
            'fast':   'Rescue One Carpenter',
            'open':   'Open Gerudo\'s Fortress',
        },
        gui_tooltip    = '''\
            'Rescue One Carpenter': Only the bottom left carpenter,
            in the cell with a single torch, must be rescued.
            This cell can be savewarped to from any room in the hideout.
            All but one of the Thieves' Hideout Keys are removed.

            'Open Gerudo's Fortress': The carpenters are rescued from
            the start of the game, and if 'Shuffle Gerudo Card' is disabled,
            the player starts with the Gerudo Card in the inventory 
            allowing access to Gerudo Training Ground.
        ''',
        shared         = True,
        disable        = {
            'open' : {'settings' : ['shuffle_hideoutkeys']}
        },
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Combobox(
        name           = 'bridge',
        gui_text       = 'Rainbow Bridge Requirement',
        default        = 'medallions',
        choices        = {
            'open':       'Always Open',
            'vanilla':    'Vanilla Requirements',
            'stones':	  'Spiritual Stones',
            'medallions': 'Medallions',
            'dungeons':   'Dungeons',
            'tokens':     'Gold Skulltula Tokens',
            'random':     'Random'
        },
        gui_tooltip    = '''\
            'Always Open': Rainbow Bridge is always present.
            'Vanilla Requirements': Spirit/Shadow Medallions and Light Arrows.
            'Spiritual Stones': A configurable amount of Spiritual Stones.
            'Medallions': A configurable amount of Medallions.
            'Dungeons': A configurable amount of Dungeon Rewards.
            'Gold Skulltula Tokens': A configurable amount of Gold Skulltula Tokens.
            'Random': A random Rainbow Bridge requirement excluding Gold Skulltula Tokens.
        ''',
        shared         = True,
        disable={
            'open':       {'settings': ['bridge_medallions', 'bridge_stones', 'bridge_rewards', 'bridge_tokens']},
            'vanilla':    {'settings': ['bridge_medallions', 'bridge_stones', 'bridge_rewards', 'bridge_tokens']},
            'stones':     {'settings': ['bridge_medallions', 'bridge_rewards', 'bridge_tokens']},
            'medallions': {'settings': ['bridge_stones', 'bridge_rewards', 'bridge_tokens']},
            'dungeons':   {'settings': ['bridge_medallions', 'bridge_stones', 'bridge_tokens']},
            'tokens':     {'settings': ['bridge_medallions', 'bridge_stones', 'bridge_rewards']},
            'random':     {'settings': ['bridge_medallions', 'bridge_stones', 'bridge_rewards', 'bridge_tokens']}
        },
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
    Scale(
        name           = 'bridge_medallions',
        gui_text       = "Medallions Required for Bridge",
        default        = 6,
        min            = 1,
        max            = 6,
        gui_tooltip    = '''\
            Select the amount of Medallions required to spawn the rainbow bridge.
        ''',
        shared         = True,
        disabled_default = 0,
        gui_params     = {
            "randomize_key": "randomize_settings",
            "hide_when_disabled": True,
            'distribution': [(6, 1)],
        },
    ),
    Scale(
        name           = 'bridge_stones',
        gui_text       = "Spiritual Stones Required for Bridge",
        default        = 3,
        min            = 1,
        max            = 3,
        gui_tooltip    = '''\
            Select the amount of Spiritual Stones required to spawn the rainbow bridge.
        ''',
        shared         = True,
        disabled_default = 0,
        gui_params     = {
            "randomize_key": "randomize_settings",
            "hide_when_disabled": True,
            'distribution': [(3, 1)],
        },
    ),
    Scale(
        name           = 'bridge_rewards',
        gui_text       = "Dungeon Rewards Required for Bridge",
        default        = 9,
        min            = 1,
        max            = 9,
        gui_tooltip    = '''\
            Select the amount of Dungeon Rewards (Medallions and Spiritual Stones)
            required to spawn the rainbow bridge.
        ''',
        shared         = True,
        disabled_default = 0,
        gui_params     = {
            "randomize_key": "randomize_settings",
            "hide_when_disabled": True,
            'distribution': [(9, 1)],
        },
    ),
    Scale(
        name           = 'bridge_tokens',
        gui_text       = "Skulltulas Required for Bridge",
        default        = 100,
        min            = 1,
        max            = 100,
        gui_tooltip    = '''\
            Select the amount of Gold Skulltula Tokens required to spawn the rainbow bridge.
        ''',
        shared         = True,
        disabled_default = 0,
        gui_params     = {
            "hide_when_disabled": True,
        },
    ),
    Checkbutton(
        name           = 'triforce_hunt',
        gui_text       = 'Triforce Hunt',
        gui_tooltip    = '''\
            Pieces of the Triforce have been scattered around the world. 
            Find some of them to beat the game.

            Game is saved on completion, and Ganon's Castle key is given
            if beating the game again is desired.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
        disable        = {
            True  : {'settings' : ['shuffle_ganon_bosskey', 'ganon_bosskey_stones', 'ganon_bosskey_medallions', 'ganon_bosskey_rewards', 'ganon_bosskey_tokens']},
            False : {'settings' : ['triforce_goal_per_world']}
        },
    ),
    Scale(
        name           = 'triforce_goal_per_world',
        gui_text       = 'Required Triforces Per World',
        default        = 20,
        min            = 1,
        max            = 100,
        shared         = True,
        gui_tooltip    = '''\
            Select the amount of Triforce Pieces required to beat the game.

            In multiworld, each world will have the same number of triforces 
            in them. The required amount will be per world collectively. 
            For example, if this is set to 20 in a 2 player multiworld, players 
            need 40 total, but one player could obtain 30 and the other 10. 

            Extra pieces are determined by the the Item Pool setting:
            'Plentiful': 100% Extra
            'Balanced': 50% Extra
            'Scarce': 25% Extra
            'Minimal: No Extra
        ''',
        gui_params     = {
            "hide_when_disabled": True,
        },
    ),
    Combobox(
        name           = 'logic_rules',
        gui_text       = 'Logic Rules',
        default        = 'glitchless',
        choices        = {
            'glitchless': 'Glitchless',
            'glitched':   'Glitched',
            'none':       'No Logic',
        },
        gui_tooltip    = '''\
            Logic provides guiding sets of rules for world generation
            which the Randomizer uses to ensure the generated seeds 
            are beatable.

            'Glitchless': No glitches are required, but may require 
            some minor tricks. Add minor tricks to consider for logic
            in the 'Detailed Logic' tab.

            'Glitched': Movement-oriented glitches are likely required.
            No locations excluded.

            'No Logic': Maximize randomization, All locations are 
            considered available. MAY BE IMPOSSIBLE TO BEAT.
        ''',
        disable        = {
            'glitchless': {'settings' : ['tricks_list_msg']},
            'glitched'  : {'settings' : ['allowed_tricks', 'shuffle_interior_entrances', 'shuffle_grotto_entrances',
                                         'shuffle_dungeon_entrances', 'shuffle_overworld_entrances', 'owl_drops',
                                         'warp_songs', 'spawn_positions', 'mq_dungeons_random', 'mq_dungeons', ]},
            'none'      : {'settings' : ['allowed_tricks', 'logic_no_night_tokens_without_suns_song', 'reachable_locations']},
        },
        shared         = True,
    ),
    Combobox(
        name           = 'reachable_locations',
        gui_text       = 'Guarantee Reachable Locations',
        default        = 'all',
        choices        = {
            'all':      'All',
            'goals':    'All Goals',
            'beatable': 'Required Only',
        },
        gui_tooltip    = '''\
            This determines which items and locations are guaranteed to be reachable.

            'All': The randomizer will guarantee that every item is obtainable and every location is reachable.

            'All Goals': The randomizer will guarantee that every goal item is obtainable, not just the amount required
            to beat the game, but otherwise behaves like 'Required Only'.
            Goal items are the items required for the rainbow bridge and/or Ganon's Boss Key, so for example if the bridge is
            set to 1 Medallion and Ganon's Boss Key to 1 Gold Skulltula Token, all 6 Medallions and all 100 Tokens will
            be obtainable. In Triforce Hunt, this will also guarantee that all Triforce Pieces can be obtained.

            'Required Only': Only items and locations required to beat the game will be guaranteed reachable.
        ''',
        gui_params={
            "hide_when_disabled": True,
        },
        shared         = True
    ),
    Checkbutton(
        name           = 'bombchus_in_logic',
        gui_text       = 'Bombchus Are Considered in Logic',
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
            be bought until Bombchus have been obtained.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'one_item_per_dungeon',
        gui_text       = 'Dungeons Have One Major Item',
        gui_tooltip    = '''\
            Dungeons have exactly one major item. 
            This naturally makes each dungeon similar in value
            rather than vary based on shuffled locations.

            Spirit Temple Colossus hands count as part 
            of the dungeon. Spirit Temple has TWO items 
            to match vanilla distribution.

            Boss Keys and Fortress Keys only count as 
            major items if they are shuffled Anywhere 
            (Keysanity) or in Any Dungeon, and Small 
            Keys only count as major items if they are 
            shuffled Anywhere (Keysanity). This setting 
            is disabled if Small Keys are shuffled in 
            Any Dungeon.

            GS Tokens only count as major items if the 
            bridge or LACS requirements are set to 
            "GS Tokens".

            Bombchus only count as major items if they
            are considered in logic.

            This setting has potential to conflict with
            other randomizer settings. Should seeds continuously
            fail to generate, consider turning this option off.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'trials_random',
        gui_text       = 'Random Number of Ganon\'s Trials',
        gui_tooltip    = '''\
            Sets a random number of trials to enter Ganon's Tower.
        ''',
        shared         = True,
        disable        = {
            True : {'settings' : ['trials']}
        },
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution':  [
                (True, 1),
            ]
        },
    ),
    Scale(
        name           = 'trials',
        gui_text       = "Ganon's Trials Count",
        default        = 6,
        min            = 0,
        max            = 6,
        gui_tooltip    = '''\
            Trials are randomly selected. If hints are
            enabled, then there will be hints for which
            trials need to be completed.
        ''',
        shared         = True,
        disabled_default = 0,
    ),
    Checkbutton(
        name           = 'skip_child_zelda',
        gui_text       = 'Skip Child Zelda',
        gui_tooltip    = '''\
            Start having already met Zelda and obtained
            Zelda's Letter along with the item from Impa.
            Supersedes "Skip Child Stealth" since the whole
            sequence is skipped. Similarly, this is
            incompatible with Shuffle Weird Egg.
        ''',
        shared         = True,
        disable = {
            True: {'settings': ['shuffle_weird_egg']},
        },
    ),
    Checkbutton(
        name           = 'no_escape_sequence',
        gui_text       = 'Skip Tower Escape Sequence',
        gui_tooltip    = '''\
            The tower escape sequence between
            Ganondorf and Ganon will be skipped.
        ''',
        shared         = True,
    ),
    Checkbutton(
        name           = 'no_guard_stealth',
        gui_text       = 'Skip Child Stealth',
        gui_tooltip    = '''\
            The crawlspace into Hyrule Castle goes
            straight to Zelda, skipping the guards.
        ''',
        shared         = True,
    ),
    Checkbutton(
        name           = 'no_epona_race',
        gui_text       = 'Skip Epona Race',
        gui_tooltip    = '''\
            Epona can be summoned with Epona's Song
            without needing to race Ingo.
        ''',
        shared         = True,
    ),
    Checkbutton(
        name           = 'skip_some_minigame_phases',
        gui_text       = 'Skip Some Minigame Phases',
        gui_tooltip    = '''\
            Awards all eligible prizes after the first attempt for
            Dampe Race and Gerudo Horseback Archery.

            Dampe will start with the second race so you can finish 
            the race in under a minute and get both rewards at once. 
            You still get the first reward from the chest even if you 
            don't complete the race in under a minute.

            Both rewards at the Gerudo Horseback Archery will be 
            available from the first time you play the minigame. 
            This means you can get both rewards at once if you get 
            1500 points in a single attempt.
        ''',
        shared         = True,
    ),
    Checkbutton(
        name           = 'useful_cutscenes',
        gui_text       = 'Enable Useful Cutscenes',
        gui_tooltip    = '''\
            The cutscenes of the Poes in Forest Temple,
            Darunia in Fire Temple, and the introduction
            to Twinrova will not be skipped.
        ''',
        shared         = True,
    ),
    Checkbutton(
        name           = 'complete_mask_quest',
        gui_text       = 'Complete Mask Quest',
        gui_tooltip    = '''\
            Once the Happy Mask Shop is opened,
            all masks will be available to be borrowed.
        ''',
        shared         = True,
    ),
    Checkbutton(
        name           = 'fast_chests',
        gui_text       = 'Fast Chest Cutscenes',
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
        gui_tooltip    = '''\
            GS Tokens that can only be obtained
            during the night expect you to have Sun's
            Song to collect them. This prevents needing
            to wait until night for some locations.
        ''',
        gui_params={
            "hide_when_disabled": True,
        },
        shared         = True,
    ),
    Checkbutton(
        name           = 'free_scarecrow',
        gui_text       = 'Free Scarecrow\'s Song',
        gui_tooltip    = '''\
            Pulling out the Ocarina near a
            spot at which Pierre can spawn will
            do so, without needing the song.
        ''',
        shared         = True,
    ),
    Checkbutton(
        name           = 'fast_bunny_hood',
        gui_text       = 'Fast Bunny Hood',
        gui_tooltip    = '''\
            The Bunny Hood mask behaves like it does
            in Majora's Mask and makes you go 1.5× faster.
        ''',
        shared         = True,
    ),
    Checkbutton(
        name           = 'start_with_rupees',
        gui_text       = 'Start with Max Rupees',
        gui_tooltip    = '''\
            Start the game with a full wallet.
            Wallet upgrades will also fill the wallet.
        ''',
        shared         = True,
    ),
    Checkbutton(
        name           = 'start_with_consumables',
        gui_text       = 'Start with Consumables',
        gui_tooltip    = '''\
            Start the game with maxed out Deku Sticks and Deku Nuts.
        ''',
        shared         = True,
    ),
    Scale(
        name           = 'starting_hearts',
        gui_text       = "Starting Hearts",
        default        = 3,
        min            = 3,
        max            = 20,
        gui_tooltip    = '''\
            Start the game with the selected number of hearts.
            Heart Containers and Pieces of Heart are removed
            from the item pool in equal proportion.
        ''',
        disabled_default = 1,
        shared         = True,
    ),
    Checkbutton(
        name           = 'chicken_count_random',
        gui_text       = 'Random Cucco Count',
        gui_tooltip    = '''\
            Anju will give a reward for collecting a random
            number of Cuccos.
        ''',
        disable        = {
            True : {'settings' : ['chicken_count']}
        },
        shared         = True,
    ),
    Scale(
        name           = 'chicken_count',
        gui_text       = 'Cucco Count',
        default        = 7,
        min            = 0,
        max            = 7,
        gui_tooltip    = '''\
            Anju will give a reward for turning
            in the chosen number of Cuccos.
        ''',
        shared         = True,
        gui_params     = {
            'no_line_break': True,
        },
    ),
    Checkbutton(
        name           = 'big_poe_count_random',
        gui_text       = 'Random Big Poe Target Count',
        gui_tooltip    = '''\
            The Poe buyer will give a reward for turning
            in a random number of Big Poes.
        ''',
        disable        = {
            True : {'settings' : ['big_poe_count']}
        },
        shared         = True,
    ),
    Scale(
        name           = 'big_poe_count',
        gui_text       = "Big Poe Target Count",
        default        = 10,
        min            = 1,
        max            = 10,
        gui_tooltip    = '''\
            The Poe buyer will give a reward for turning
            in the chosen number of Big Poes.
        ''',
        disabled_default = 1,
        shared         = True,
    ),
    Checkbutton(
        name           = 'shuffle_kokiri_sword',
        gui_text       = 'Shuffle Kokiri Sword',
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
        gui_tooltip    = '''\
            Enabling this shuffles the Fairy Ocarina and the Ocarina
            of Time into the pool.

            This will require finding an Ocarina before being able
            to play songs.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'shuffle_weird_egg',
        gui_text       = 'Shuffle Weird Egg',
        gui_tooltip    = '''\
            Enabling this shuffles the Weird Egg from Malon into the pool.

            This will require finding the Weird Egg to talk to Zelda in
            Hyrule Castle, which in turn locks rewards from Impa, Saria,
            Malon, and Talon, as well as the Happy Mask sidequest.
            The Weird Egg is also required for Zelda's Letter to open 
            the Kakariko Gate as child which can lock some progression.
        ''',
        disable        = {
            True : {'settings' : ['skip_child_zelda']}
        },
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'shuffle_gerudo_card',
        gui_text       = "Shuffle Gerudo Card",
        gui_tooltip    = '''\
            Enabling this shuffles the Gerudo Card into the item pool.

            The Gerudo Card is required to enter the Gerudo Training Ground
            and prevents the guards from throwing you in jail.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Combobox(
        name           = 'shuffle_song_items',
        gui_text       = 'Shuffle Songs',
        default        = 'song',
        choices        = {
            'song':    'Song Locations',
            'dungeon': 'Dungeon Rewards',
            'any':     'Anywhere',
            },
        gui_tooltip    = '''\
            This restricts where song items can appear.

            'Song Locations': Song will only appear at locations that
            normally teach songs. In Multiworld, songs will only 
            appear in their own world.

            'Dungeon Rewards': Songs appear at the end of dungeons.
            For major dungeons, they will be at the boss heart
            container location. The remaining 4 songs are placed at:

            - Zelda's Lullaby Location
            - Ice Cavern's Serenade of Water Location
            - Bottom of the Well's Lens of Truth Location
            - Gerudo Training Ground's Ice Arrow Location

            'Anywhere': Songs can appear in any location.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution':  [
                ('song', 2),
                ('dungeon', 1),
                ('any', 1),
            ],
        },
        shared         = True,
    ),
    Checkbutton(
        name           = 'shuffle_cows',
        gui_text       = 'Shuffle Cows',
        gui_tooltip    = '''\
            Enabling this will let cows give you items
            upon performing Epona's song in front of them.
            There are 9 cows, and an extra in MQ Jabu.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'shuffle_beans',
        gui_text       = 'Shuffle Magic Beans',
        gui_tooltip    = '''\
            Enabling this adds a pack of 10 beans to the item pool
            and changes the Magic Bean Salesman to sell a random
            item once at the price of 60 Rupees.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'shuffle_medigoron_carpet_salesman',
        gui_text       = 'Shuffle Medigoron & Carpet Salesman',
        gui_tooltip    = '''\
            Enabling this adds a Giant's Knife and a pack of Bombchus 
            to the item pool and changes both Medigoron and the 
            Haunted Wasteland Carpet Salesman to sell a random item 
            once at the price of 200 Rupees.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Combobox(
        name           = 'shuffle_interior_entrances',
        gui_text       = 'Shuffle Interior Entrances',
        default        = 'off',
        choices        = {
            'off':       'Off',
            'simple':    'Simple Interiors',
            'all':       'All Interiors',
        },
        gui_tooltip    = '''\
            'Simple Interiors': 
            Shuffle the pool of interior entrances which contains most Houses 
            and all Great Fairies.
    
            'All Interiors':
            Extended version of 'Simple Interiors' with some extra places:
            Windmill, Link's House, Temple of Time and Kakariko Potion Shop.

            When shuffling any interior entrances, trade quest timers are disabled 
            and items never revert, even when dying or loading a save.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution':  [
                ('off', 2),
                ('simple', 1),
                ('all', 1),
            ],
        },
    ),
    Checkbutton(
        name           = 'shuffle_grotto_entrances',
        gui_text       = 'Shuffle Grotto Entrances',
        gui_tooltip    = '''\
            Shuffle the pool of grotto entrances, including all graves, 
            small Fairy Fountains and the Lost Woods Stage.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'shuffle_dungeon_entrances',
        gui_text       = 'Shuffle Dungeon Entrances',
        gui_tooltip    = '''\
            Shuffle the pool of dungeon entrances, including Bottom 
            of the Well, Ice Cavern, and Gerudo Training Ground.
            However, Ganon's Castle and Thieves' Hideout are not shuffled.

            Additionally, the entrances of Deku Tree, Fire Temple and 
            Bottom of the Well are opened for both adult and child.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'shuffle_overworld_entrances',
        gui_text       = 'Shuffle Overworld Entrances',
        gui_tooltip    = '''\
            Shuffle the pool of Overworld entrances, which corresponds
            to almost all loading zones between Overworld areas.

            Some entrances are kept unshuffled to avoid issues:
            - Hyrule Castle Courtyard and Garden entrances
            - Both Market Back Alley entrances
            - Gerudo Valley to Lake Hylia

            Just like when shuffling interior entrances, shuffling overworld 
            entrances disables trade timers and trade items never revert, 
            even when dying or loading a save.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'owl_drops',
        gui_text       = 'Randomize Owl Drops',
        gui_tooltip    = '''\
            Randomize where Kaepora Gaebora (the Owl) drops you at 
            when you talk to him at Lake Hylia or at the top of 
            Death Mountain Trail.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'warp_songs',
        gui_text       = 'Randomize Warp Song Destinations',
        gui_tooltip    = '''\
            Randomize where each of the 6 warp songs leads to.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Checkbutton(
        name           = 'spawn_positions',
        gui_text       = 'Randomize Overworld Spawns',
        gui_tooltip    = '''\
            Randomize where you start as Child or Adult when loading
            a save in the Overworld. This means you may not necessarily
            spawn inside Link's House or Temple of Time.

            This stays consistent after saving and loading the game again.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Combobox(
        name           = 'shuffle_scrubs',
        gui_text       = 'Scrub Shuffle',
        default        = 'off',
        choices        = {
            'off':     'Off',
            'low':     'On (Affordable)',
            'regular': 'On (Expensive)',
            'random':  'On (Random Prices)',
        },
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
        gui_text       = 'Shopsanity',
        default        = 'off',
        choices        = {
            'off':    'Off',
            '0':      '0 Items Per Shop',
            '1':      '1 Item Per Shop',
            '2':      '2 Items Per Shop',
            '3':      '3 Items Per Shop',
            '4':      '4 Items Per Shop',
            'random': 'Random # of Items Per Shop',
        },
        gui_tooltip    = '''\
            Randomizes Shop contents.
            
            'X Items Per Shop': Each shop will have the
            specified number of items randomized and they
            will always appear on the left side
            (identified by the Special Deal! text).
            Remaining items will be shuffled between shops.
            
            'Random # of Items Per Shop': Each shop will
            have 0 to 4 Special Deals.
            
            The randomized items have no requirements
            except money, while the remaining items retain
            normal requirements. Tunics that aren't a
            Special Deal! will still require you to be an
            adult to purchase for example.
            
            Bombchu Special Deals will unlock the Bombchu
            slot in your inventory and allow purchase of
            Bombchu Refills if "Bombchus are considered in
            logic" is enabled. Otherwise, the Bomb Bag is
            required to purchase Bombchu Refills.
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
        gui_text       = 'Tokensanity',
        default        = 'off',
        choices        = {
            'off':       'Off',
            'dungeons':  'Dungeons Only',
            'overworld': 'Overworld Only',
            'all':       'All Tokens',
            },
        gui_tooltip    = '''\
            Token reward from Gold Skulltulas are
            shuffled into the pool.

            'Dungeons Only': This only shuffles
            the GS locations that are within
            dungeons, increasing the value of
            most dungeons and making internal
            dungeon exploration more diverse.

            'Overworld Only': This only shuffles
            the GS locations that are outside
            of dungeons.

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
        gui_text       = 'Maps & Compasses',
        default        = 'dungeon',
        choices        = {
            'remove':      'Remove',
            'startwith':   'Start With',
            'vanilla':     'Vanilla Locations',
            'dungeon':     'Own Dungeon',
            'overworld':   'Overworld Only',
            'any_dungeon': 'Any Dungeon',
            'keysanity':   'Anywhere',
        },
        gui_tooltip    = '''\
            'Remove': Maps and Compasses are removed.
            This will add a small amount of money and
            refill items to the pool.

            'Start With': Maps and Compasses are given to
            you from the start. This will add a small
            amount of money and refill items to the pool.

            'Vanilla': Maps and Compasses will appear in
            their vanilla locations.

            'Own Dungeon': Maps and Compasses can only appear
            in their respective dungeon.
            
            'Overworld Only': Maps and Compasses can only appear
            outside of dungeons.

            'Any Dungeon': Maps and Compasses can only appear in a
            dungeon, but not necessarily the dungeon they are for.            

            'Anywhere': Maps and Compasses can appear
            anywhere in the world.

            Setting 'Remove', 'Start With, 'Overworld', or 'Anywhere'
            will add 2 more possible locations to each Dungeons.
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
        gui_text       = 'Small Keys',
        default        = 'dungeon',
        choices        = {
            'remove':      'Remove (Keysy)',
            'vanilla':     'Vanilla Locations',
            'dungeon':     'Own Dungeon',
            'overworld':   'Overworld Only',
            'any_dungeon': 'Any Dungeon',
            'keysanity':   'Anywhere (Keysanity)',
        },
        gui_tooltip    = '''\
            'Remove': Small Keys are removed. All locked
            doors in dungeons will be unlocked. An easier
            mode.

            'Vanilla': Small Keys will appear in their 
            vanilla locations. You start with 3 keys in 
            Spirit Temple MQ because the vanilla key 
            layout is not beatable in logic.

            'Own Dungeon': Small Keys can only appear in their
            respective dungeon. If Fire Temple is not a
            Master Quest dungeon, the door to the Boss Key
            chest will be unlocked.
            
            'Overworld Only': Small Keys can only appear outside
            of dungeons. You may need to enter a dungeon multiple
            times to gain items to access the overworld locations
            with the keys required to finish a dungeon.
            
            'Any Dungeon': Small Keys can only appear inside
            of any dungeon, but won't necessarily be in the
            dungeon that the key is for. A difficult mode since
            it is more likely to need to enter a dungeon
            multiple times.

            'Anywhere': Small Keys can appear
            anywhere in the world. A difficult mode since
            it is more likely to need to enter a dungeon
            multiple times.

            Try different combination out, such as:
            'Small Keys: Dungeon' + 'Boss Keys: Anywhere'
            for a milder Keysanity experience.
        ''',
        disable        = {
            'any_dungeon': {'settings': ['one_item_per_dungeon']},
        },
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Combobox(
        name           = 'shuffle_hideoutkeys',
        gui_text       = 'Thieves\' Hideout Keys',
        default        = 'vanilla',
        disabled_default = 'remove',
        choices        = {
            'vanilla':     'Vanilla Locations',
            'overworld':   'Overworld Only',
            'any_dungeon': 'Any Dungeon',
            'keysanity':   'Anywhere (Keysanity)',
        },
        gui_tooltip    = '''\
            'Vanilla': Thieves' Hideout Keys will appear in their
            vanilla location, dropping from fighting Gerudo guards
            that attack when trying to free the jailed carpenters.
            
            'Overworld Only': Thieves' Hideout Keys can only appear
            outside of dungeons.
            
            'Any Dungeon': Thieves' Hideout Keys can only appear
            inside of dungeons.

            'Anywhere': Thieves' Hideout Keys can appear anywhere
            in the world.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Combobox(
        name           = 'shuffle_bosskeys',
        gui_text       = 'Boss Keys',
        default        = 'dungeon',
        choices        = {
            'remove':      'Remove (Keysy)',
            'vanilla':     'Vanilla Locations',
            'dungeon':     'Own Dungeon',
            'overworld':   'Overworld Only',
            'any_dungeon': 'Any Dungeon',
            'keysanity':   'Anywhere (Keysanity)',
        },
        gui_tooltip    = '''\
            'Remove': Boss Keys are removed. All locked
            doors in dungeons will be unlocked. An easier
            mode.

            'Vanilla': Boss Keys will appear in their 
            vanilla locations.

            'Own Dungeon': Boss Keys can only appear in their
            respective dungeon.
            
            'Overworld Only': Boss Keys can only appear outside
            of dungeons. You may need to enter a dungeon without
            the boss key to get items required to find the key
            in the overworld.
            
            'Any Dungeon': Boss Keys can only appear inside
            of any dungeon, but won't necessarily be in the
            dungeon that the key is for. A difficult mode since
            it is more likely to need to enter a dungeon
            multiple times.

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
    Combobox(
        name           = 'shuffle_ganon_bosskey',
        gui_text       = 'Ganon\'s Boss Key',
        default        = 'dungeon',
        disabled_default = 'triforce',
        choices        = {
            'remove':          "Remove (Keysy)",
            'vanilla':         "Vanilla Location",
            'dungeon':         "Own Dungeon",
            'overworld':       "Overworld Only",
            'any_dungeon':     "Any Dungeon",
            'keysanity':       "Anywhere (Keysanity)",
            'on_lacs':         "Light Arrow Cutscene",
            'stones':          "Stones",
            'medallions':      "Medallions",
            'dungeons':        "Dungeons",
            'tokens':          "Tokens",
        },
        gui_tooltip    = '''\
            'Remove': Ganon's Castle Boss Key is removed
            and the boss door in Ganon's Tower starts unlocked.

            'Own Dungeon': Ganon's Castle Boss Key can only appear
            inside Ganon's Castle.

            'Vanilla': Ganon's Castle Boss Key will appear in 
            the vanilla location.
            
            'Overworld Only': Ganon's Castle Boss Key can only appear
            outside of dungeons.
            
            'Any Dungeon': Ganon's Castle Boss Key can only appear
            inside of a dungeon, but not necessarily Ganon's Castle.

            'Anywhere': Ganon's Castle Boss Key can appear
            anywhere in the world.

            'Light Arrow Cutscene': Ganon's Castle Boss Key will
            appear on the Light Arrow Cutscene.
            
            'Stones': Ganon's Castle Boss Key will be awarded
            when reaching the target number of Spiritual Stones.
            
            'Medallions': Ganon's Castle Boss Key will be awarded
            when reaching the target number of Medallions.
                        
            'Dungeons': Ganon's Castle Boss Key will be awarded
            when reaching the target number of Dungeon Rewards.
            
            'Tokens': Ganon's Castle Boss Key will be awarded
            when reaching the target number of Gold Skulltula Tokens.
        ''',
        shared         = True,
        disable        = {
            '!stones':  {'settings': ['ganon_bosskey_stones']},
            '!medallions':  {'settings': ['ganon_bosskey_medallions']},
            '!dungeons':  {'settings': ['ganon_bosskey_rewards']},
            '!tokens':  {'settings': ['ganon_bosskey_tokens']},
        },
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution': [
                ('remove',          4),
                ('dungeon',         2),
                ('vanilla',         2),
                ('keysanity',       4),
                ('on_lacs',         1)
            ],
        },
    ),
    Scale(
        name           = 'ganon_bosskey_medallions',
        gui_text       = "Medallions Required for Ganon's BK",
        default        = 6,
        min            = 1,
        max            = 6,
        gui_tooltip    = '''\
            Select the amount of Medallions required to receive Ganon's Castle Boss Key.
        ''',
        shared         = True,
        disabled_default = 0,
        gui_params     = {
            "randomize_key": "randomize_settings",
            "hide_when_disabled": True,
            'distribution': [(6, 1)],
        },
    ),
    Scale(
        name           = 'ganon_bosskey_stones',
        gui_text       = "Spiritual Stones Required for Ganon's BK",
        default        = 3,
        min            = 1,
        max            = 3,
        gui_tooltip    = '''\
            Select the amount of Spiritual Stones required to receive Ganon's Castle Boss Key.
        ''',
        shared         = True,
        disabled_default = 0,
        gui_params     = {
            "randomize_key": "randomize_settings",
            "hide_when_disabled": True,
            'distribution': [(3, 1)],
        },
    ),
    Scale(
        name           = 'ganon_bosskey_rewards',
        gui_text       = "Dungeon Rewards Required for Ganon's BK",
        default        = 9,
        min            = 1,
        max            = 9,
        gui_tooltip    = '''\
            Select the amount of Dungeon Rewards (Medallions and Spiritual Stones)
            required to receive Ganon's Castle Boss Key.
        ''',
        shared         = True,
        disabled_default = 0,
        gui_params     = {
            "randomize_key": "randomize_settings",
            "hide_when_disabled": True,
            'distribution': [(9, 1)],
        },
    ),
    Scale(
        name           = 'ganon_bosskey_tokens',
        gui_text       = "Gold Skulltula Tokens Required for Ganon's BK",
        default        = 100,
        min            = 1,
        max            = 100,
        gui_tooltip    = '''\
            Select the amount of Gold Skulltula Tokens
            required to receive Ganon's Castle Boss Key.
        ''',
        shared         = True,
        disabled_default = 0,
        gui_params     = {
            "hide_when_disabled": True,
        },
    ),
    Combobox(
        name           = 'lacs_condition',
        gui_text       = 'LACS Condition',
        default        = 'vanilla',
        choices        = {
            'vanilla':    "Vanilla",
            'stones':     "Stones",
            'medallions': "Medallions",
            'dungeons':   "Dungeons",
            'tokens':     "Tokens",
        },
        gui_tooltip    = '''\
            Sets the condition for the Light Arrow Cutscene
            check to give you the item from Zelda.
            
            'Vanilla': Shadow and Spirit Medallions.
            'Stones': A configurable amount of Spiritual Stones.
            'Medallions': A configurable amount of Medallions.
            'Dungeons': A configurable amount of Dungeon Rewards.
            'Tokens': A configurable amount of Gold Skulltula Tokens.
        ''',
        shared         = True,
        disable        = {
            '!stones':  {'settings': ['lacs_stones']},
            '!medallions':  {'settings': ['lacs_medallions']},
            '!dungeons':  {'settings': ['lacs_rewards']},
            '!tokens':  {'settings': ['lacs_tokens']},
        },
        gui_params     = {
            'optional': True,
            'distribution': [
                ('vanilla',    1),
                ('medallions', 1),
                ('stones',     1),
                ('dungeons',   1),
            ],
        },
    ),
    Scale(
        name           = 'lacs_medallions',
        gui_text       = "Medallions Required for LACS",
        default        = 6,
        min            = 1,
        max            = 6,
        gui_tooltip    = '''\
            Select the amount of Medallions required to trigger the Light Arrow Cutscene.
        ''',
        shared         = True,
        disabled_default = 0,
        gui_params     = {
            'optional': True,
            "hide_when_disabled": True,
            'distribution': [(6, 1)],
        },
    ),
    Scale(
        name           = 'lacs_stones',
        gui_text       = "Spiritual Stones Required for LACS",
        default        = 3,
        min            = 1,
        max            = 3,
        gui_tooltip    = '''\
            Select the amount of Spiritual Stones required to trigger the Light Arrow Cutscene.
        ''',
        shared         = True,
        disabled_default = 0,
        gui_params     = {
            'optional': True,
            "hide_when_disabled": True,
            'distribution': [(3, 1)],
        },
    ),
    Scale(
        name           = 'lacs_rewards',
        gui_text       = "Dungeon Rewards Required for LACS",
        default        = 9,
        min            = 1,
        max            = 9,
        gui_tooltip    = '''\
            Select the amount of Dungeon Rewards (Medallions and Spiritual Stones)
            required to trigger the Light Arrow Cutscene.
        ''',
        shared         = True,
        disabled_default = 0,
        gui_params     = {
            'optional': True,
            "hide_when_disabled": True,
            'distribution': [(9, 1)],
        },
    ),
    Scale(
        name           = 'lacs_tokens',
        gui_text       = "Gold Skulltula Tokens Required for LACS",
        default        = 100,
        min            = 1,
        max            = 100,
        gui_tooltip    = '''\
            Select the amount of Gold Skulltula Tokens
            required to trigger the Light Arrow Cutscene.
        ''',
        shared         = True,
        disabled_default = 0,
        gui_params     = {
            'optional': True,
            "hide_when_disabled": True,
        },
    ),
    Checkbutton(
        name           = 'enhance_map_compass',
        gui_text       = 'Maps and Compasses Give Information',
        gui_tooltip    = '''\
            Gives the Map and Compass extra functionality.
            Map will tell if a dungeon is vanilla or Master Quest.
            Compass will tell what medallion or stone is within.
            The Temple of Time Altar will no longer provide
            information on the location of medallions and stones.

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
        name           = 'mq_dungeons_random',
        gui_text       = 'Random Number of MQ Dungeons',
        gui_tooltip    = '''\
            If set, a random number of dungeons
            will have Master Quest designs.
        ''',
        shared         = True,
        disable        = {
            True : {'settings' : ['mq_dungeons']}
        },
    ),
    Scale(
        name           = 'mq_dungeons',
        gui_text       = "MQ Dungeon Count",
        default        = 0,
        min            = 0,
        max            = 12,
        gui_tooltip    = '''\
            Specify the number of Master Quest
            dungeons to appear in the game.

            0: All dungeon will have their
            original designs. (default)

            6: Half of all dungeons will
            be from Master Quest.

            12: All dungeons will have
            Master Quest redesigns.
        ''',
        shared         = True,
    ),
    Setting_Info(
        name           = 'disabled_locations',
        type           = list,
        gui_text       = "Exclude Locations",
        gui_type       = "SearchBox",
        shared         = True,
        choices        = [location.name for location in LocationIterator(lambda loc: loc.filter_tags is not None)],
        default        = [],
        gui_tooltip    = '''
            Locations in the left column may contain items
            required to complete the game. 
            
            Locations in the right column will never have 
            items that are required to complete the game, 
            and will only contain junk.

            Most dungeon locations have a MQ alternative.
            If the location does not exist because of MQ
            then it will be ignored. So make sure to
            disable both versions if that is the intent.
        ''',
        gui_params     = {
            'filterdata': {location.name: location.filter_tags for location in LocationIterator(lambda loc: loc.filter_tags is not None)},
        }
    ),
    Setting_Info(
        name           = 'allowed_tricks',
        type           = list,
        gui_text       = "Enable Tricks",
        gui_type       = "SearchBox",
        shared         = True,
        choices        = {
            val['name']: gui_text for gui_text, val in logic_tricks.items()
        },
        default        = [],
        gui_params     = {
            'choice_tooltip': {choice['name']: choice['tooltip'] for choice in logic_tricks.values()},
            'filterdata': {val['name']: val['tags'] for _, val in logic_tricks.items()},
            "hide_when_disabled": True,
        },
        gui_tooltip='''
            Tricks moved to the right column are in-logic
            and MAY be required to complete the game.
            
            Tricks in the left column are NEVER required.
            
            Tricks are only relevant for Glitchless logic.
        '''
    ),
    Setting_Info(
        name           = 'tricks_list_msg',
        type           = str,
        gui_text       = "Your current logic setting does not support the enabling of tricks.",
        gui_type       = "Textbox",
        shared         = False,
        gui_params     = {
            "hide_when_disabled": True
        },
        choices        = {},
    ),
    Combobox(
        name           = 'logic_earliest_adult_trade',
        gui_text       = 'Adult Trade Sequence Earliest Item',
        default        = 'pocket_egg',
        choices        = {
            'pocket_egg':   'Pocket Egg',
            'pocket_cucco': 'Pocket Cucco',
            'cojiro':       'Cojiro',
            'odd_mushroom': 'Odd Mushroom',
            'poachers_saw': "Poacher's Saw",
            'broken_sword': 'Broken Sword',
            'prescription': 'Prescription',
            'eyeball_frog': 'Eyeball Frog',
            'eyedrops':     'Eyedrops',
            'claim_check':  'Claim Check',
        },
        gui_tooltip    = '''\
            Select the earliest item that can appear in the adult trade sequence.
        ''',
        shared         = True,
    ),
    Combobox(
        name           = 'logic_latest_adult_trade',
        gui_text       = 'Adult Trade Sequence Latest Item',
        default        = 'claim_check',
        choices        = {
            'pocket_egg':   'Pocket Egg',
            'pocket_cucco': 'Pocket Cucco',
            'cojiro':       'Cojiro',
            'odd_mushroom': 'Odd Mushroom',
            'poachers_saw': "Poacher's Saw",
            'broken_sword': 'Broken Sword',
            'prescription': 'Prescription',
            'eyeball_frog': 'Eyeball Frog',
            'eyedrops':     'Eyedrops',
            'claim_check':  'Claim Check',
        },
        gui_tooltip    = '''\
            Select the latest item that can appear in the adult trade sequence.
        ''',
        shared         = True,
    ),
    Setting_Info(
        name           = 'starting_equipment',
        type           = list,
        gui_text       = "Starting Equipment",
        gui_type       = "SearchBox",
        shared         = True,
        choices        = {
            key: value.guitext for key, value in StartingItems.equipment.items()
        },
        default        = [],
        gui_tooltip    = '''\
            Begin the game with the selected equipment.
        ''',
    ),
    Setting_Info(
        name           = 'starting_items',
        type           = list,
        gui_text       = "Starting Items",
        gui_type       = "SearchBox",
        shared         = True,
        choices        = {
            key: value.guitext for key, value in StartingItems.inventory.items()
        },
        default        = [],
        gui_tooltip    = '''\
            Begin the game with the selected inventory items.
            Selecting multiple progressive items will give
            the appropriate number of upgrades.
            
            If playing with Open Zora's Fountain, the Ruto's Letter
            is converted to a regular Bottle.
        ''',
    ),
    Setting_Info(
        name           = 'starting_songs',
        type           = list,
        gui_text       = "Starting Songs",
        gui_type       = "SearchBox",
        shared         = True,
        choices        = {
            key: value.guitext for key, value in StartingItems.songs.items()
        },
        default        = [],
        gui_tooltip    = '''\
            Begin the game with the selected songs already learnt.
        ''',
    ),
    Checkbutton(
        name           = 'ocarina_songs',
        gui_text       = 'Randomize Ocarina Song Notes',
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
        gui_tooltip    = '''\
            The hints provided by Gossip Stones will
            be very direct if this option is enabled.
        ''',
        shared         = True,
        default        = True,
    ),
    Checkbutton(
        name           = 'no_collectible_hearts',
        gui_text       = 'Hero Mode',
        gui_tooltip    = '''\
            No recovery hearts will drop from 
            enemies or objects.
            (You might still find some freestanding
            or in chests depending on other settings.)
        ''',
        default        = False,
        shared         = True,
    ),
    Combobox(
        name           = 'hints',
        gui_text       = 'Gossip Stones',
        default        = 'always',
        choices        = {
            'none':   'No Hints',
            'mask':   'Hints; Need Mask of Truth',
            'agony':  'Hints; Need Stone of Agony',
            'always': 'Hints; Need Nothing',
        },
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
        gui_text       = 'Hint Distribution',
        default        = 'balanced',
        choices        = HintDistList(),
        gui_tooltip    = HintDistTips(),
        shared         = True,
        disable        = {
            '!bingo' : {'settings' : ['bingosync_url']},
        },
    ),
    Setting_Info(
        name           = "bingosync_url",
        type           = str,
        choices        = {},
        gui_type       = "Textinput",
        gui_text       = "Bingosync URL",
        shared         = False,
        gui_tooltip    = '''\
            Enter a URL to a Bingosync bingo board in
            order to have hints specific to items needed
            to beat the board. Goals which are completed simply
            by finding a specific item are not hinted
            (e.g. "Boomerang"). 
            In addition, overworld tokensanity will always
            hint the location of Sun's Song, and shopsanity
            will always hint the location of a wallet.

            Leaving this entry blank or providing an
            invalid URL will generate generic item hints
            designed to allow completion of most bingo goals.
            Non Bingosync bingo boards are not directly
            supported, and will also generate generic item hints.
        ''',
        disabled_default = None,
        gui_params       = {
            "size"               : "full",
            "hide_when_disabled" : True,
        },
    ),
    Setting_Info('item_hints',    list, None, None, True, {}),
    Setting_Info('hint_dist_user',    dict, None, None, True, {}),
    Combobox(
        name           = 'text_shuffle',
        gui_text       = 'Text Shuffle',
        default        = 'none',
        choices        = {
            'none':         'No Text Shuffled',
            'except_hints': 'Shuffled except Important Text',
            'complete':     'All Text Shuffled',
        },
        gui_tooltip    = '''\
            Will make things confusing for comedic value.

            'Shuffled except Important Text': For when
            you want comedy but don't want to impact
            gameplay. Text that has an impact on gameplay
            is not shuffled. This includes all hint text,
            key text, Good Deal! items sold in shops, random
            price scrubs, chicken count and poe count.
        ''',
        shared         = True,
    ),
    Checkbutton(
        name           = 'misc_hints',
        gui_text       = 'Misc. Hints',
        gui_tooltip    = '''\
            This setting adds some hints at locations
            other than Gossip Stones:

            Reading the Temple of Time altar as child
            will tell you the locations of the
            Spiritual Stones (unless Maps and Compasses
            Give Information is enabled).

            Reading the Temple of Time altar as adult
            will tell you the locations of the Medallions
            (unless Maps and Compasses Give Information
            is enabled), as well as the conditions for
            building the Rainbow Bridge and getting the
            Boss Key for Ganon's Castle.

            Talking to Ganondorf in his boss room will
            tell you the location of the Light Arrows.

            If this setting is enabled and Ganondorf
            is reachable without Light Arrows, Gossip
            Stones will never hint the Light Arrows.
        ''',
        shared         = True,
        default        = True,
    ),
    Combobox(
        name           = 'ice_trap_appearance',
        gui_text       = 'Ice Trap Appearance',
        default        = 'major_only',
        choices        = {
            'major_only': 'Major Items Only',
            'junk_only':  'Junk Items Only',
            'anything':   'Anything',
        },
        gui_tooltip    = '''\
            Changes the categories of items Ice Traps may
            appear as, both when freestanding and when in
            chests with Chest Size Matches Contents enabled. 

            'Major Items Only': Ice Traps appear as Major
            Items (and in large chests if CSMC enabled).

            'Junk Items Only': Ice Traps appear as Junk
            Items (and in small chests if CSMC enabled).

            'Anything': Ice Traps may appear as anything.
        ''',
        shared         = True,
    ),
    Combobox(
        name           = 'junk_ice_traps',
        gui_text       = 'Ice Traps',
        default        = 'normal',
        choices        = {
            'off':       'No Ice Traps',
            'normal':    'Normal Ice Traps',
            'on':        'Extra Ice Traps',
            'mayhem':    'Ice Trap Mayhem',
            'onslaught': 'Ice Trap Onslaught',
        },
        gui_tooltip    = '''\
            'Off': All Ice Traps are removed.

            'Normal': Only Ice Traps from the base item pool
            are placed.

            'Extra Ice Traps': Chance to add extra Ice Traps
            when junk items are added to the itempool.

            'Ice Trap Mayhem': All added junk items will
            be Ice Traps.

            'Ice Trap Onslaught': All junk items will be
            replaced by Ice Traps, even those in the
            base pool.
        ''',
        shared         = True,
    ),
    Combobox(
        name           = 'item_pool_value',
        gui_text       = 'Item Pool',
        default        = 'balanced',
        choices        = {
            'plentiful': 'Plentiful',
            'balanced':  'Balanced',
            'scarce':    'Scarce',
            'minimal':   'Minimal'
        },
        gui_tooltip    = '''\
            Changes the amount of major items that are 
            available in the game.

            'Plentiful': One additional copy of each major 
            item is added.

            'Balanced': Original item pool.

            'Scarce': An extra copy of major item upgrades 
            that are not required to open location checks 
            is removed (e.g. Bow upgrade, Magic upgrade). 
            Heart Containers are removed as well. Number
            of Bombchu items is reduced.

            'Minimal': All major item upgrades not used to 
            open location checks are removed. All health 
            upgrades are removed. Only one Bombchu item is 
            available.
        ''',
        shared         = True,
    ),
    Combobox(
        name           = 'damage_multiplier',
        gui_text       = 'Damage Multiplier',
        default        = 'normal',
        choices        = {
            'half':      'Half',
            'normal':    'Normal',
            'double':    'Double',
            'quadruple': 'Quadruple',
            'ohko':      'OHKO',
        },
        gui_tooltip    = '''\
            Changes the amount of damage taken.

            'OHKO': Link dies in one hit.
        ''',
        shared         = True,
    ),
    Combobox(
        name           = 'starting_tod',
        gui_text       = 'Starting Time of Day',
        default        = 'default',
        choices        = {
            'default':       'Default (10:00)',
            'random':        'Random Choice',
            'sunrise':       'Sunrise (6:30)',
            'morning':       'Morning (9:00)',
            'noon':          'Noon (12:00)',
            'afternoon':     'Afternoon (15:00)',
            'sunset':        'Sunset (18:00)',
            'evening':       'Evening (21:00)',
            'midnight':      'Midnight (00:00)',
            'witching-hour': 'Witching Hour (03:00)',
        },
        gui_tooltip    = '''\
            Change up Link's sleep routine.

            Daytime officially starts at 6:30,
            nighttime at 18:00 (6:00 PM).
        ''',
        shared         = True,
    ),
    Combobox(
        name           = 'starting_age',
        gui_text       = 'Starting Age',
        default        = 'child',
        choices        = {
            'child':  'Child',
            'adult':  'Adult',
            'random': 'Random',
        },
        gui_tooltip    = '''\
            Choose which age Link will start as.

            Starting as adult means you start with
            the master sword in your inventory.

            Only the child option is compatible with
            Closed Forest.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution': [
                ('random', 1),
            ],
        }
    ),
    Combobox(
        name           = 'default_targeting',
        gui_text       = 'Default Targeting Option',
        shared         = False,
        cosmetic       = True,
        default        = 'hold',
        choices        = {
            'hold':   'Hold',
            'switch': 'Switch',
        },
    ),
    Combobox(
        name           = 'background_music',
        gui_text       = 'Background Music',
        shared         = False,
        cosmetic       = True,
        default        = 'normal',
        choices        = {
            'normal':               'Normal',
            'off':                  'No Music',
            'random':               'Random',
            'random_custom_only':   'Random (Custom Only)',
        },
        gui_tooltip    = '''\
            'No Music': No background music is played.

            'Random': Area background music is randomized. 
            Additional music can be loaded from data/Music/
        ''',
        gui_params  = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random', 1),
            ],
            'web:option_remove': ['random_custom_only'],
        },
    ),
    Combobox(
        name           = 'fanfares',
        gui_text       = 'Fanfares',
        shared         = False,
        cosmetic       = True,
        default        = 'normal',
        choices        = {
            'normal':               'Normal',
            'off':                  'No Fanfares',
            'random':               'Random',
            'random_custom_only':   'Random (Custom Only)',
        },
        disable        = {
            'normal' : {'settings' : ['ocarina_fanfares']},
        },
        gui_tooltip    = '''\
            'No Fanfares': No fanfares (short non-looping tracks) are played.

            'Random': Fanfares are randomized.
            Additional fanfares can be loaded from data/Music/
        ''',
        gui_params  = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random', 1),
            ],
            'web:option_remove': ['random_custom_only'],
        },
    ),
    Checkbutton(
        name           = 'ocarina_fanfares',
        gui_text       = 'Ocarina Songs as Fanfares',
        shared         = False,
        cosmetic       = True,
        gui_tooltip    = '''\
            Include the songs that play when an ocarina song
            is played as part of the fanfare pool when
            shuffling or disabling fanfares. Note that these
            are a bit longer than most fanfares.
        ''',
        gui_params  = {
            "hide_when_disabled": True,
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                (True, 1),
            ]
        },
        default        = False,
    ),
    Checkbutton(
        name           = 'display_dpad',
        gui_text       = 'Display D-Pad HUD',
        shared         = False,
        cosmetic       = True,
        gui_tooltip    = '''\
            Shows an additional HUD element displaying
            current available options on the D-Pad.
        ''',
        default        = True,
    ),
    Checkbutton(
        name           = 'correct_model_colors',
        gui_text       = 'Item Model Colors Match Cosmetics',
        shared         = False,
        cosmetic       = True,
        gui_tooltip    = '''\
            In-game models for items such as Heart Containers have
            colors matching the colors chosen for cosmetic settings.
            Heart and magic drop icons also have matching colors.

            Tunic colors are excluded from this to prevent not being 
            able to discern freestanding Tunics from each other.
        ''',
        default        = False,
    ),
    Checkbutton(
        name           = 'randomize_all_cosmetics',
        gui_text       = 'Randomize All Cosmetics',
        shared         = False,
        cosmetic       = True,
        gui_tooltip    = '''\
            Randomize all cosmetics settings.
        ''',
        default        = False,
        disable    = {
            True : {'sections' : [ "equipment_color_section", "ui_color_section", "misc_color_section" ]
            }
        }
    ),
    Setting_Info(
        name           = 'kokiri_color',
        type           = str,
        gui_text       = "Kokiri Tunic",
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_tunic_color_options(),
        default        = 'Kokiri Green',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }
    ),
    Setting_Info(
        name           = 'goron_color',
        type           = str,
        gui_text       = "Goron Tunic",
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_tunic_color_options(),
        default        = 'Goron Red',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }

    ),
    Setting_Info(
        name           = 'zora_color',
        type           = str,
        gui_text       = "Zora Tunic",
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_tunic_color_options(),
        default        = 'Zora Blue',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }

    ),
    Setting_Info(
        name           = 'navi_color_default_inner',
        type           = str,
        gui_text       = "Navi Idle Inner",
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_navi_color_options(),
        default        = 'White',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'no_line_break' : True,
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }
    ),
    Setting_Info(
        name           = 'navi_color_default_outer',
        type           = str,
        gui_text       = "Outer",
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_navi_color_options(True),
        default        = '[Same as Inner]',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }

    ),
    Setting_Info(
        name           = 'navi_color_enemy_inner',
        type           = str,
        gui_text       = 'Navi Targeting Enemy Inner',
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_navi_color_options(),
        default        = 'Yellow',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'no_line_break' : True,
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }

    ),
    Setting_Info(
        name           = 'navi_color_enemy_outer',
        type           = str,
        gui_text       = 'Outer',
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_navi_color_options(True),
        default        = '[Same as Inner]',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }

    ),
    Setting_Info(
        name           = 'navi_color_npc_inner',
        type           = str,
        gui_text       = 'Navi Targeting NPC Inner',
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_navi_color_options(),
        default        = 'Light Blue',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'no_line_break' : True,
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }

    ),
    Setting_Info(
        name           = 'navi_color_npc_outer',
        type           = str,
        gui_text       = 'Outer',
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_navi_color_options(True),
        default        = '[Same as Inner]',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }

    ),
    Setting_Info(
        name           = 'navi_color_prop_inner',
        type           = str,
        gui_text       = 'Navi Targeting Prop Inner',
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_navi_color_options(),
        default        = 'Green',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'no_line_break' : True,
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }

    ),
    Setting_Info(
        name           = 'navi_color_prop_outer',
        type           = str,
        gui_text       = 'Outer',
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_navi_color_options(True),
        default        = '[Same as Inner]',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }

    ),
    Setting_Info(
        name           = 'bombchu_trail_color_inner',
        type           = str,
        gui_text       = 'Bombchu Trail Inner',
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_bombchu_trail_color_options(),
        default        = 'Red',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'no_line_break' : True,
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }

    ),
    Setting_Info(
        name           = 'bombchu_trail_color_outer',
        type           = str,
        gui_text       = 'Outer',
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_bombchu_trail_color_options(True),
        default        = '[Same as Inner]',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }

    ),
    Setting_Info(
        name           = 'boomerang_trail_color_inner',
        type           = str,
        gui_text       = 'Boomerang Trail Inner',
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_boomerang_trail_color_options(),
        default        = 'Yellow',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'no_line_break' : True,
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }

    ),
    Setting_Info(
        name           = 'boomerang_trail_color_outer',
        type           = str,
        gui_text       = 'Outer',
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_boomerang_trail_color_options(True),
        default        = '[Same as Inner]',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }

    ),
    Setting_Info(
        name           = 'sword_trail_color_inner',
        type           = str,
        gui_text       = 'Sword Trail Inner',
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_sword_trail_color_options(),
        default        = 'White',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'no_line_break' : True,
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }

    ),
    Setting_Info(
        name           = 'sword_trail_color_outer',
        type           = str,
        gui_text       = 'Outer',
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_sword_trail_color_options(True),
        default        = '[Same as Inner]',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Cycle through a color rainbow.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }

    ),
    Combobox(
        name           = 'sword_trail_duration',
        gui_text       = 'Sword Trail Duration',
        shared         = False,
        cosmetic       = True,
        choices        = {
            4: 'Default',
            10: 'Long',
            15: 'Very Long',
            20: 'Lightsaber',
        },
        default        = 4,
        gui_tooltip    = '''\
            Select the duration for sword trails.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                (4, 1),
                (10, 1),
                (15, 1),
                (20, 1)
            ]
        }
    ),
    Setting_Info(
        name           = 'silver_gauntlets_color',
        type           = str,
        gui_text       = 'Silver Gauntlets Color',
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_gauntlet_color_options(),
        default        = 'Silver',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }

    ),
    Setting_Info(
        name           = 'golden_gauntlets_color',
        type           = str,
        gui_text       = 'Golden Gauntlets Color',
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_gauntlet_color_options(),
        default        = 'Gold',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }

    ),
    Setting_Info(
        name           = 'mirror_shield_frame_color',
        type           = str,
        gui_text       = 'Mirror Shield Frame Color',
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_shield_frame_color_options(),
        default        = 'Red',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }

    ),
    Setting_Info(
        name           = 'heart_color',
        type           = str,
        gui_text       = 'Heart Color',
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_heart_color_options(),
        default        = 'Red',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }

    ),
    Setting_Info(
        name           = 'magic_color',
        type           = str,
        gui_text       = 'Magic Color',
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_magic_color_options(),
        default        = 'Green',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }

    ),
    Setting_Info(
        name           = 'a_button_color',
        type           = str,
        gui_text       = 'A Button Color',
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_a_button_color_options(),
        default        = 'N64 Blue',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }

    ),
    Setting_Info(
        name           = 'b_button_color',
        type           = str,
        gui_text       = 'B Button Color',
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_b_button_color_options(),
        default        = 'N64 Green',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }

    ),
    Setting_Info(
        name           = 'c_button_color',
        type           = str,
        gui_text       = 'C Button Color',
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_c_button_color_options(),
        default        = 'Yellow',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }

    ),
    Setting_Info(
        name           = 'start_button_color',
        type           = str,
        gui_text       = 'Start Button Color',
        gui_type       = "Combobox",
        shared         = False,
        cosmetic       = True,
        choices        = get_start_button_color_options(),
        default        = 'N64 Red',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_cosmetics',
            'distribution': [
                ('Completely Random', 1),
            ]
        }

    ),
    Checkbutton(
        name           = 'randomize_all_sfx',
        gui_text       = 'Randomize All Sound Effects',
        shared         = False,
        cosmetic       = True,
        gui_tooltip    = '''\
            Randomize all sound effects and music settings (ear safe)
        ''',
        default        = False,
        disable    = {
            True : {'sections' : [ "generalsfx_section", "menusfx_section", "npcsfx_section" ]
            }
        }

    ),
    Combobox(
        name           = 'sfx_low_hp',
        gui_text       = 'Low HP',
        shared         = False,
        cosmetic       = True,
        choices        = sfx.get_setting_choices(sfx.SoundHooks.HP_LOW),
        default        = 'default',
        gui_tooltip    = '''\
            'Random Choice': Choose a random sound from this list.
            'Default': Beep. Beep. Beep.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    ),
    Combobox(
        name           = 'sfx_navi_overworld',
        gui_text       = 'Navi Overworld',
        shared         = False,
        cosmetic       = True,
        choices        = sfx.get_setting_choices(sfx.SoundHooks.NAVI_OVERWORLD),
        default        = 'default',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    ),
    Combobox(
        name           = 'sfx_navi_enemy',
        gui_text       = 'Navi Enemy',
        shared         = False,
        cosmetic       = True,
        choices        = sfx.get_setting_choices(sfx.SoundHooks.NAVI_ENEMY),
        default        = 'default',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    ),
    Combobox(
        name           = 'sfx_menu_cursor',
        gui_text       = 'Menu Cursor',
        shared         = False,
        cosmetic       = True,
        choices        = sfx.get_setting_choices(sfx.SoundHooks.MENU_CURSOR),
        default        = 'default',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    ),
    Combobox(
        name           = 'sfx_menu_select',
        gui_text       = 'Menu Select',
        shared         = False,
        cosmetic       = True,
        choices        = sfx.get_setting_choices(sfx.SoundHooks.MENU_SELECT),
        default        = 'default',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    ),
    Combobox(
        name           = 'sfx_horse_neigh',
        gui_text       = 'Horse',
        shared         = False,
        cosmetic       = True,
        choices        = sfx.get_setting_choices(sfx.SoundHooks.HORSE_NEIGH),
        default        = 'default',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    ),
    Combobox(
        name           = 'sfx_nightfall',
        gui_text       = 'Nightfall',
        shared         = False,
        cosmetic       = True,
        choices        = sfx.get_setting_choices(sfx.SoundHooks.NIGHTFALL),
        default        = 'default',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    ),
    Combobox(
        name           = 'sfx_hover_boots',
        gui_text       = 'Hover Boots',
        shared         = False,
        cosmetic       = True,
        choices        = sfx.get_setting_choices(sfx.SoundHooks.BOOTS_HOVER),
        default        = 'default',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-ear-safe', 1),
            ]
        }
    ),
    Combobox(
        name           = 'sfx_ocarina',
        gui_text       = 'Ocarina',
        shared         = False,
        cosmetic       = True,
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
        gui_tooltip    = '''\
            Change the sound of the ocarina.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_all_sfx',
            'distribution': [
                ('random-choice', 1),
            ]
        }
    ),
]


si_dict = {si.name: si for si in setting_infos}
def get_setting_info(name):
    return si_dict[name]


def create_dependency(setting, disabling_setting, option, negative=False):
    disabled_info = get_setting_info(setting)
    op = operator.__ne__ if negative else operator.__eq__
    if disabled_info.dependency is None:
        disabled_info.dependency = lambda settings: op(getattr(settings, disabling_setting.name), option)
    else:
        old_dependency = disabled_info.dependency
        disabled_info.dependency = lambda settings: op(getattr(settings, disabling_setting.name), option) or old_dependency(settings)


def get_settings_from_section(section_name):
    for tab in setting_map['Tabs']:
        for section in tab['sections']:
            if section['name'] == section_name:
                for setting in section['settings']:
                    yield setting
                return


def get_settings_from_tab(tab_name):
    for tab in setting_map['Tabs']:
        if tab['name'] == tab_name:
            for section in tab['sections']:
                for setting in section['settings']:
                    yield setting
            return

def is_mapped(setting_name):
    for tab in setting_map['Tabs']:
        for section in tab['sections']:
            if setting_name in section['settings']:
                return True
    return False


# When a string isn't found in the source list, attempt to get closest match from the list
# ex. Given "Recovery Hart" returns "Did you mean 'Recovery Heart'?"
def build_close_match(name, value_type, source_list=None):
    source = []
    if value_type == 'item':
        source = item_table.keys()
    elif value_type == 'location':
        source = location_table.keys()
    elif value_type == 'entrance':
        for pool in source_list.values():
            for entrance in pool:
                source.append(entrance.name)
    elif value_type == 'stone':
        source = [x.name for x in gossipLocations.values()]
    elif value_type == 'setting':
        source = [x.name for x in setting_infos]
    elif value_type == 'choice':
        source = source_list
    close_match = difflib.get_close_matches(name, source, 1)
    if len(close_match) > 0:
        return "Did you mean %r?" % (close_match[0])
    return "" # No matches


def validate_settings(settings_dict):
    for setting, choice in settings_dict.items():
        # Ensure the supplied setting name is a real setting
        if setting not in [x.name for x in setting_infos]:
            raise TypeError('%r is not a valid setting. %s' % (setting, build_close_match(setting, 'setting')))
        info = get_setting_info(setting)
        # Ensure the type of the supplied choice is correct
        if type(choice) != info.type:
            raise TypeError('Supplied choice %r for setting %r is of type %r, expecting %r' % (choice, setting, type(choice).__name__, info.type.__name__))
        # If setting is a list, must check each element
        if isinstance(choice, list):
            for element in choice:
                if element not in info.choice_list:
                    raise ValueError('%r is not a valid choice for setting %r. %s' % (element, setting, build_close_match(element, 'choice', info.choice_list)))
        # Ignore dictionary settings such as hint_dist_user
        elif isinstance(choice, dict):
            continue
        # Ensure that the given choice is a valid choice for the setting
        elif info.choice_list and choice not in info.choice_list:
            if setting == 'compress_rom' and choice == 'Temp':
                continue
            raise ValueError('%r is not a valid choice for setting %r. %s' % (choice, setting, build_close_match(choice, 'choice', info.choice_list)))

class UnmappedSettingError(Exception):
    pass


with open(data_path('settings_mapping.json')) as f:
    setting_map = json.load(f)

for info in setting_infos:
    if info.gui_text is not None and not info.gui_params.get('optional') and not is_mapped(info.name):
        raise UnmappedSettingError(f'{info.name} is defined but is not in the settings map. Add it to the settings_mapping or set the gui_text to None to suppress.')

    if info.disable != None:
        for option, disabling in info.disable.items():
            negative = False
            if isinstance(option, str) and option[0] == '!':
                negative = True
                option = option[1:]
            for setting in disabling.get('settings', []):
                create_dependency(setting, info, option, negative)
            for section in disabling.get('sections', []):
                for setting in get_settings_from_section(section):
                    create_dependency(setting, info, option, negative)
            for tab in disabling.get('tabs', []):
                for setting in get_settings_from_tab(tab):
                    create_dependency(setting, info, option, negative)
