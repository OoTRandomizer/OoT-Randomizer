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
from Hints import HintDistList, HintDistTips, gossipLocations
from Item import ItemInfo
from Location import LocationIterator
from LocationList import location_table
from Models import get_model_choices
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

    def __init__(self, name, gui_text, choices, default, gui_tooltip=None, disable=None,
            disabled_default=None, shared=False, gui_params=None, cosmetic=False, multiple_select=False):

        gui_type = 'Combobox' if not multiple_select else 'MultipleSelect'
        type = str if not multiple_select else list
        super().__init__(name, type, gui_text, gui_type, shared, choices, default, disabled_default, disable, gui_tooltip, gui_params, cosmetic)


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

# Below is the list of possible glitchless tricks.
# The order they are listed in is also the order in which
# they appear to the user in the GUI, so a sensible order was chosen

logic_tricks = {

    # General tricks

    'Pass Through Visible One-Way Collisions': {
        'name'    : 'logic_visible_collisions',
        'tags'    : ("Entrance", "Kakariko Village",),
        'tooltip' : '''\
                    Allows climbing through the platform to reach 
                    Impa's House Back as adult with no items and 
                    going through the Kakariko Village Gate as child
                    when coming from the Mountain Trail side.
                    '''},
    'Hidden Grottos without Stone of Agony': {
        'name'    : 'logic_grottos_without_agony',
        'tags'    : ("General", "Entrance",),
        'tooltip' : '''\
                    Allows entering hidden grottos without the
                    Stone of Agony.
                    '''},
    'Fewer Tunic Requirements': {
        'name'    : 'logic_fewer_tunic_requirements',
        'tags'    : ("General", "Fire Temple", "Water Temple", "Gerudo Training Ground", "Zora's Fountain", "Death Mountain Crater", "MQ",),
        'tooltip' : '''\
                    Allows the following possible without Tunics:
                    - Enter Water Temple. The area below the center
                    pillar still requires Zora Tunic. Applies to
                    MQ also.
                    - Enter Fire Temple. Only the first floor is
                    accessible, and not Volvagia. Applies to
                    MQ also.
                    - Zora's Fountain Bottom Freestanding PoH.
                    Might not have enough health to resurface.
                    - Gerudo Training Ground Underwater
                    Silver Rupee Chest. May need to make multiple
                    trips. Applies to MQ also.
                    '''},
    'Beehives with Bombchus' : {
        'name'    : 'logic_beehives_bombchus',
        'tags'    : ("Beehives",),
        'tooltip' : '''\
                    Puts breaking beehives with bombchus into logic.
                    Using bombs is already expected on beehives that
                    that are low enough that a bomb throw will reach.
                    '''},
    'Hammer Rusted Switches Through Walls': {
        'name'    : 'logic_rusted_switches',
        'tags'    : ("Fire Temple", "Ganon's Castle", "MQ",),
        'tooltip' : '''\
                    Applies to:
                    - Fire Temple Highest Goron Chest.
                    - MQ Fire Temple Lizalfos Maze.
                    - MQ Spirit Trial.
                    '''},

    # Overworld tricks

    'Adult Kokiri Forest GS with Hover Boots': {
        'name'    : 'logic_adult_kokiri_gs',
        'tags'    : ("Kokiri Forest", "Skulltulas",),
        'tooltip' : '''\
                    Can be obtained without Hookshot by using the Hover
                    Boots off of one of the roots.
                    '''},
    'Jump onto the Lost Woods Bridge as Adult with Nothing': {
        'name'    : 'logic_lost_woods_bridge',
        'tags'    : ("the Lost Woods", "Entrance",),
        'tooltip' : '''\
                    With very precise movement it's possible for
                    adult to jump onto the bridge without needing
                    Longshot, Hover Boots, or Bean.
                    '''},
    'Backflip over Mido as Adult': {
        'name'    : 'logic_mido_backflip',
        'tags'    : ("the Lost Woods",),
        'tooltip' : '''\
                    With a specific position and angle, you can
                    backflip over Mido.
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
    'Hyrule Castle Storms Grotto GS with Just Boomerang': {
        'name'    : 'logic_castle_storms_gs',
        'tags'    : ("Hyrule Castle", "Skulltulas",),
        'tooltip' : '''\
                    With precise throws, the Boomerang alone can
                    kill the Skulltula and collect the token,
                    without first needing to blow up the wall.
                    '''},
    'Man on Roof without Hookshot': {
        'name'    : 'logic_man_on_roof',
        'tags'    : ("Kakariko Village",),
        'tooltip' : '''\
                    Can be reached by side-hopping off
                    the watchtower as either age, or by
                    jumping onto the potion shop's roof
                    from the ledge as adult.
                    '''},
    'Kakariko Tower GS with Jump Slash': {
        'name'    : 'logic_kakariko_tower_gs',
        'tags'    : ("Kakariko Village", "Skulltulas",),
        'tooltip' : '''\
                    Climb the tower as high as you can without
                    touching the Gold Skulltula, then let go and
                    jump slash immediately. By jump-slashing from
                    as low on the ladder as possible to still
                    hit the Skulltula, this trick can be done
                    without taking fall damage.
                    '''},
    'Windmill PoH as Adult with Nothing': {
        'name'    : 'logic_windmill_poh',
        'tags'    : ("Kakariko Village",),
        'tooltip' : '''\
                    Can jump up to the spinning platform from
                    below as adult.
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
    'Second Dampe Race as Child': {
        'name'    : 'logic_child_dampe_race_poh',
        'tags'    : ("the Graveyard", "Entrance",),
        'tooltip' : '''\
                    It is possible to complete the second dampe
                    race as child in under a minute, but it is
                    a strict time limit.
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
    'Death Mountain Trail Chest with Strength': {
        'name'    : 'logic_dmt_bombable',
        'tags'    : ("Death Mountain Trail",),
        'tooltip' : '''\
                    Child Link can blow up the wall using a nearby bomb
                    flower. You must backwalk with the flower and then
                    quickly throw it toward the wall.
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
                    by quickly dipping in and out of Darunia's chamber or
                    quickly equipping and unequipping the Goron Tunic.
                    This trick does not apply if "Randomize Warp Song
                    Destinations" is enabled, or if the settings are such
                    that trade items do not need to be delivered within a
                    time limit.
                    '''},                    
    'Goron City Spinning Pot PoH with Bombchu': {
        'name'    : 'logic_goron_city_pot',
        'tags'    : ("Goron City",),
        'tooltip' : '''\
                    A Bombchu can be used to stop the spinning
                    pot, but it can be quite finicky to get it
                    to work.
                    '''},
    'Goron City Spinning Pot PoH with Strength': {
        'name'    : 'logic_goron_city_pot_with_strength',
        'tags'    : ("Goron City",),
        'tooltip' : '''\
                    Allows for stopping the Goron City Spinning
                    Pot using a bomb flower alone, requiring 
                    strength in lieu of inventory explosives.
                    '''},
    'Rolling Goron (Hot Rodder Goron) as Child with Strength': {
        'name'    : 'logic_child_rolling_with_strength',
        'tags'    : ("Goron City",),
        'tooltip' : '''\
                    Use the bombflower on the stairs or near Medigoron.
                    Timing is tight, especially without backwalking.
                    '''},
    'Stop Link the Goron with Din\'s Fire': {
        'name'    : 'logic_link_goron_dins',
        'tags'    : ("Goron City",),
        'tooltip' : '''\
                    The timing is quite awkward.
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
    'Crater\'s Bean PoH with Hover Boots': {
        'name'    : 'logic_crater_bean_poh_with_hovers',
        'tags'    : ("Death Mountain Crater",),
        'tooltip' : '''\
                    Hover from the base of the bridge
                    near Goron City and walk up the
                    very steep slope.
                    '''},
    'Death Mountain Crater Jump to Bolero': {
        'name'    : 'logic_crater_bolero_jump',
        'tags'    : ("Death Mountain Crater",),
        'tooltip' : '''\
                    Using a shield to drop a pot while you have
                    the perfect speed and position, the pot can
                    push you that little extra distance you
                    need to jump across the gap in the bridge.
                    '''},
    'Death Mountain Crater Upper to Lower with Hammer': {
        'name'    : 'logic_crater_boulder_jumpslash',
        'tags'    : ("Death Mountain Crater",),
        'tooltip' : '''\
                    With the Hammer, you can jump slash the rock twice
                    in the same jump in order to destroy it before you
                    fall into the lava.
                    '''},
    'Death Mountain Crater Upper to Lower Boulder Skip': {
        'name'    : 'logic_crater_boulder_skip',
        'tags'    : ("Death Mountain Crater",),
        'tooltip' : '''\
                    With careful positioning, you can jump to the ledge
                    where the boulder is, then use repeated ledge grabs
                    to shimmy to a climbable ledge. This trick supersedes
                    "Death Mountain Crater Upper to Lower with Hammer".
                    '''},
    'Zora\'s River Lower Freestanding PoH as Adult with Nothing': {
        'name'    : 'logic_zora_river_lower',
        'tags'    : ("Zora's River",),
        'tooltip' : '''\
                    Adult can reach this PoH with a precise jump,
                    no Hover Boots required.
                    '''},
    'Zora\'s River Upper Freestanding PoH as Adult with Nothing': {
        'name'    : 'logic_zora_river_upper',
        'tags'    : ("Zora's River",),
        'tooltip' : '''\
                    Adult can reach this PoH with a precise jump,
                    no Hover Boots required.
                    '''},
    'Zora\'s Domain Entry with Cucco': {
        'name'    : 'logic_zora_with_cucco',
        'tags'    : ("Zora's River",),
        'tooltip' : '''\
                    Can fly behind the waterfall with
                    a cucco as child.
                    '''},
    'Zora\'s Domain Entry with Hover Boots': {
        'name'    : 'logic_zora_with_hovers',
        'tags'    : ("Zora's River",),
        'tooltip' : '''\
                    Can hover behind the waterfall as adult.
                    '''},
    'Zora\'s River Rupees with Jump Dive': {
        'name'    : 'logic_zora_river_rupees',
        'tags'    : ("Zora's River", "Freestandings",),
        'tooltip' : '''\
                    You can jump down onto them from
                    above to skip needing Iron Boots.
                    '''},
    'Skip King Zora as Adult with Nothing': {
        'name'    : 'logic_king_zora_skip',
        'tags'    : ("Zora's Domain",),
        'tooltip' : '''\
                    With a precise jump as adult, it is possible to
                    get on the fence next to King Zora from the front
                    to access Zora's Fountain.
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
    'Lake Hylia Lab Wall GS with Jump Slash': {
        'name'    : 'logic_lab_wall_gs',
        'tags'    : ("Lake Hylia", "Skulltulas",),
        'tooltip' : '''\
                    The jump slash to actually collect the
                    token is somewhat precise.
                    '''},
    'Lake Hylia Lab Dive without Gold Scale': {
        'name'    : 'logic_lab_diving',
        'tags'    : ("Lake Hylia",),
        'tooltip' : '''\
                    Remove the Iron Boots in the midst of
                    Hookshotting the underwater crate.
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
    'Thieves\' Hideout "Kitchen" with No Additional Items': {
        'name'    : 'logic_gerudo_kitchen',
        'tags'    : ("Thieves' Hideout", "Gerudo's Fortress",),
        'tooltip' : '''\
                    Allows passing through the kitchen by avoiding being
                    seen by the guards. The logic normally guarantees
                    Bow or Hookshot to stun them from a distance, or
                    Hover Boots to cross the room without needing to
                    deal with the guards.
                    '''},
    'Gerudo\'s Fortress Ledge Jumps': {
        'name'    : 'logic_gf_jump',
        'tags'    : ("Gerudo's Fortress",),
        'tooltip' : '''\
                    Adult can jump onto the top roof of the fortress
                    without going through the interior of the hideout.
                    '''},
    'Wasteland Crossing without Hover Boots or Longshot': {
        'name'    : 'logic_wasteland_crossing',
        'tags'    : ("Haunted Wasteland",),
        'tooltip' : '''\
                    You can beat the quicksand by backwalking across it
                    in a specific way.
                    Note that jumping to the carpet merchant as child
                    typically requires a fairly precise jump slash.
                    '''},
    'Lensless Wasteland': {
        'name'    : 'logic_lens_wasteland',
        'tags'    : ("Lens of Truth", "Haunted Wasteland",),
        'tooltip' : '''\
                    By memorizing the path, you can travel through the
                    Wasteland without using the Lens of Truth to see
                    the Poe.
                    The equivalent trick for going in reverse through
                    the Wasteland is "Reverse Wasteland".
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
    'Colossus Hill GS with Hookshot': {
        'name'    : 'logic_colossus_gs',
        'tags'    : ("Desert Colossus", "Skulltulas",),
        'tooltip' : '''\
                    Somewhat precise. If you kill enough Leevers
                    you can get enough of a break to take some time
                    to aim more carefully.
                    '''},

    # Dungeons

        'Deku Tree Basement Vines GS with Jump Slash': {
        'name'    : 'logic_deku_basement_gs',
        'tags'    : ("Deku Tree", "Skulltulas",),
        'tooltip' : '''\
                    Can be defeated by doing a precise jump slash.
                    '''},
    'Deku Tree Basement without Slingshot': {
        'name'    : 'logic_deku_b1_skip',
        'tags'    : ("Deku Tree", "MQ",),
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
    'Deku Tree MQ Compass Room GS Boulders with Just Hammer': {
        'name'    : 'logic_deku_mq_compass_gs',
        'tags'    : ("Deku Tree", "Skulltulas", "MQ",),
        'tooltip' : '''\
                    Climb to the top of the vines, then let go
                    and jump slash immediately to destroy the
                    boulders using the Hammer, without needing
                    to spawn a Song of Time block.
                    '''},
    'Deku Tree MQ Roll Under the Spiked Log': {
        'name'    : 'logic_deku_mq_log',
        'tags'    : ("Deku Tree", "MQ",),
        'tooltip' : '''\
                    You can get past the spiked log by rolling
                    to briefly shrink your hitbox. As adult,
                    the timing is a bit more precise.
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
    'Dodongo\'s Cavern Vines GS from Below with Longshot': {
        'name'    : 'logic_dc_vines_gs',
        'tags'    : ("Dodongo's Cavern", "Skulltulas",),
        'tooltip' : '''\
                    The vines upon which this Skulltula rests are one-
                    sided collision. You can use the Longshot to get it
                    from below, by shooting it through the vines,
                    bypassing the need to lower the staircase.
                    '''},
    'Dodongo\'s Cavern Staircase with Bow': {
        'name'    : 'logic_dc_staircase',
        'tags'    : ("Dodongo's Cavern",),
        'tooltip' : '''\
                    The Bow can be used to knock down the stairs
                    with two well-timed shots.
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
    'Dodongo\'s Cavern Two Scrub Room with Strength': {
        'name'    : 'logic_dc_scrub_room',
        'tags'    : ("Dodongo's Cavern",),
        'tooltip' : '''\
                    With help from a conveniently-positioned block,
                    Adult can quickly carry a bomb flower over to
                    destroy the mud wall blocking the room with two
                    Deku Scrubs.
                    '''},
    'Dodongo\'s Cavern Spike Trap Room Jump without Hover Boots': {
        'name'    : 'logic_dc_jump',
        'tags'    : ("Dodongo's Cavern", "MQ",),
        'tooltip' : '''\
                    The jump is adult Link only. Applies to both Vanilla and MQ.
                    '''},
    'Dodongo\'s Cavern Smash the Boss Lobby Floor': {
        'name'    : 'logic_dc_hammer_floor',
        'tags'    : ("Dodongo's Cavern", "Entrance", "MQ",),
        'tooltip' : '''\
                    The bombable floor before King Dodongo can be destroyed
                    with Hammer if hit in the very center. This is only
                    relevant with Shuffle Boss Entrances or if Dodongo's Cavern
                    is MQ and either variant of "Dodongo's Cavern MQ Light the
                    Eyes with Strength" is on.
                    '''},
    'Dodongo\'s Cavern MQ Early Bomb Bag Area as Child': {
        'name'    : 'logic_dc_mq_child_bombs',
        'tags'    : ("Dodongo's Cavern", "MQ",),
        'tooltip' : '''\
                    With a precise jump slash from above, you
                    can reach the Bomb Bag area as only child
                    without needing a Slingshot. You will
                    take fall damage.
                    '''},
    'Dodongo\'s Cavern MQ Light the Eyes with Strength as Child': {
        'name'    : 'logic_dc_mq_eyes_child',
        'tags'    : ("Dodongo's Cavern", "MQ",),
        'tooltip' : '''\
                    If you move very quickly, it is possible to use
                    the bomb flower at the top of the room to light
                    the eyes. To perform this trick as child is
                    significantly more difficult than adult. The
                    player is also expected to complete the DC back
                    area without explosives, including getting past
                    the Armos wall to the switch for the boss door.
                    '''},
    'Dodongo\'s Cavern MQ Light the Eyes with Strength as Adult': {
        'name'    : 'logic_dc_mq_eyes_adult',
        'tags'    : ("Dodongo's Cavern", "MQ",),
        'tooltip' : '''\
                    If you move very quickly, it is possible to use
                    the bomb flower at the top of the room to light
                    the eyes.
                    '''},
    'Jabu Underwater Alcove as Adult with Jump Dive': {
        'name'    : 'logic_jabu_alcove_jump_dive',
        'tags'    : ("Jabu Jabu's Belly", "Entrance", "MQ",),
        'tooltip' : '''\
                    Standing above the underwater tunnel leading to the scrub,
                    jump down and swim through the tunnel. This allows adult to
                    access the alcove with no Scale or Iron Boots. In vanilla Jabu,
                    this alcove has a business scrub. In MQ Jabu, it has the compass
                    chest and a door switch for the main floor.
                    '''},
    'Jabu Near Boss Room with Hover Boots': {
        'name'    : 'logic_jabu_boss_hover',
        'tags'    : ("Jabu Jabu's Belly", "Skulltulas", "Entrance",),
        'tooltip' : '''\
                    A box for the blue switch can be carried over
                    by backwalking with one while the elevator is
                    at its peak. Alternatively, you can skip
                    transporting a box by quickly rolling from the
                    switch and opening the door before it closes.
                    However, the timing for this is very tight.
                    '''},
    'Jabu Near Boss Ceiling Switch/GS without Boomerang or Explosives': {
        'name'    : 'logic_jabu_near_boss_ranged',
        'tags'    : ("Jabu Jabu's Belly", "Skulltulas", "Entrance", "MQ",),
        'tooltip' : '''\
                    Vanilla Jabu: From near the entrance into the room, you can
                    hit the switch that opens the door to the boss room using a
                    precisely-aimed use of the Slingshot, Bow, or Longshot. As well,
                    if you climb to the top of the vines you can stand on the right
                    edge of the platform and shoot around the glass. From this
                    distance, even the Hookshot can reach the switch. This trick is
                    only relevant if "Shuffle Boss Entrances" is enabled.

                    MQ Jabu: A Gold Skulltula Token can be collected with the
                    Hookshot or Longshot using the same methods as hitting the switch
                    in vanilla. This trick is usually only relevant if Jabu dungeon
                    shortcuts are enabled.
                    '''},                    
    'Jabu Near Boss Ceiling Switch with Explosives': {
        'name'    : 'logic_jabu_near_boss_explosives',
        'tags'    : ("Jabu Jabu's Belly", "Entrance",),
        'tooltip' : '''\
                    You can hit the switch that opens the door to the boss
                    room using a precisely-aimed Bombchu. Also, using the
                    Hover Boots, adult can throw a Bomb at the switch. This
                    trick is only relevant if "Shuffle Boss Entrances" is
                    enabled.
                    '''},
    'Jabu MQ without Lens of Truth': {
        'name'    : 'logic_lens_jabu_mq',
        'tags'    : ("Lens of Truth", "Jabu Jabu's Belly", "MQ",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Jabu MQ.
                    '''},                                      
    'Jabu MQ Compass Chest with Boomerang': {
        'name'    : 'logic_jabu_mq_rang_jump',
        'tags'    : ("Jabu Jabu's Belly", "MQ",),
        'tooltip' : '''\
                    Boomerang can reach the cow switch to spawn the chest by
                    targeting the cow, jumping off of the ledge where the
                    chest spawns, and throwing the Boomerang in midair. This
                    is only relevant with Jabu Jabu's Belly dungeon shortcuts
                    enabled.
                    '''},
    'Jabu MQ Song of Time Block GS with Boomerang': {
        'name'    : 'logic_jabu_mq_sot_gs',
        'tags'    : ("Jabu Jabu's Belly", "Skulltulas", "MQ",),
        'tooltip' : '''\
                    Allow the Boomerang to return to you through
                    the Song of Time block to grab the token.
                    '''},
    'Bottom of the Well without Lens of Truth': {
        'name'    : 'logic_lens_botw',
        'tags'    : ("Lens of Truth", "Bottom of the Well",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Bottom of the Well.
                    '''},
    'Child Dead Hand without Kokiri Sword': {
        'name'    : 'logic_child_deadhand',
        'tags'    : ("Bottom of the Well",),
        'tooltip' : '''\
                    Requires 9 sticks or 5 jump slashes.
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
        'tags'    : ("Bottom of the Well", "MQ",),
        'tooltip' : '''\
                    While the pits in Bottom of the Well don't allow you to
                    jump just by running straight at them, you can still get
                    over them by side-hopping or backflipping across. With
                    explosives, this allows you to access the central areas
                    without Zelda's Lullaby. With Zelda's Lullaby, it allows
                    you to access the west inner room without explosives.
                    '''},
    'Bottom of the Well MQ Dead Hand Freestanding Key with Boomerang': {
        'name'    : 'logic_botw_mq_dead_hand_key',
        'tags'    : ("Bottom of the Well", "MQ",),
        'tooltip' : '''\
                    Boomerang can fish the item out of the rubble without
                    needing explosives to blow it up.
                    '''},
    'Forest Temple First Room GS with Difficult-to-Use Weapons': {
        'name'    : 'logic_forest_first_gs',
        'tags'    : ("Forest Temple", "Entrance", "Skulltulas",),
        'tooltip' : '''\
                    Allows killing this Skulltula with Sword or Sticks by
                    jump slashing it as you let go from the vines. You can
                    avoid taking fall damage by recoiling onto the tree.
                    Also allows killing it as Child with a Bomb throw. It's
                    much more difficult to use a Bomb as child due to
                    Child Link's shorter height.
                    '''},
    'Forest Temple East Courtyard GS with Boomerang': {
        'name'    : 'logic_forest_outdoor_east_gs',
        'tags'    : ("Forest Temple", "Entrance", "Skulltulas",),
        'tooltip' : '''\
                    Precise Boomerang throws can allow child to
                    kill the Skulltula and collect the token.
                    '''},                                      
    'Forest Temple East Courtyard Vines with Hookshot': {
        'name'    : 'logic_forest_vines',
        'tags'    : ("Forest Temple", "MQ",),
        'tooltip' : '''\
                    The vines in Forest Temple leading to where the well
                    drain switch is in the standard form can be barely
                    reached with just the Hookshot. Applies to MQ also.
                    '''},
    'Forest Temple NE Outdoors Ledge with Hover Boots': {
        'name'    : 'logic_forest_outdoors_ledge',
        'tags'    : ("Forest Temple", "Entrance", "MQ",),
        'tooltip' : '''\
                    With precise Hover Boots movement you can fall down
                    to this ledge from upper balconies. If done precisely
                    enough, it is not necessary to take fall damage.
                    In MQ, this skips a Longshot requirement.
                    In Vanilla, this can skip a Hookshot requirement in
                    entrance randomizer.
                    '''},
    'Forest Temple East Courtyard Door Frame with Hover Boots': {
        'name'    : 'logic_forest_door_frame',
        'tags'    : ("Forest Temple", "MQ",),
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
    'Forest Temple Outside Backdoor with Jump Slash': {
        'name'    : 'logic_forest_outside_backdoor',
        'tags'    : ("Forest Temple", "MQ",),
        'tooltip' : '''\
                    A jump slash recoil can be used to reach the
                    ledge in the block puzzle room that leads to
                    the west courtyard. This skips a potential
                    Hover Boots requirement in vanilla, and it
                    can sometimes apply in MQ as well. This trick
                    can be performed as both ages.
                    '''},
    'Swim Through Forest Temple MQ Well with Hookshot': {
        'name'    : 'logic_forest_well_swim',
        'tags'    : ("Forest Temple", "MQ",),
        'tooltip' : '''\
                    Shoot the vines in the well as low and as far to
                    the right as possible, and then immediately swim
                    under the ceiling to the right. This can only be
                    required if Forest Temple is in its Master Quest
                    form.
                    '''},
    'Skip Forest Temple MQ Block Puzzle with Bombchu': {
        'name'    : 'logic_forest_mq_block_puzzle',
        'tags'    : ("Forest Temple", "MQ",),
        'tooltip' : '''\
                    Send the Bombchu straight up the center of the
                    wall directly to the left upon entering the room.
                    '''},                    
    'Forest Temple MQ Twisted Hallway Switch with Jump Slash': {
        'name'    : 'logic_forest_mq_hallway_switch_jumpslash',
        'tags'    : ("Forest Temple", "MQ",),
        'tooltip' : '''\
                    The switch to twist the hallway can be hit with
                    a jump slash through the glass block. To get in
                    front of the switch, either use the Hover Boots
                    or hit the shortcut switch at the top of the
                    room and jump from the glass blocks that spawn.
                    Sticks can be used as child, but the Kokiri
                    Sword is too short to reach through the glass.
                    '''},
    #'Forest Temple MQ Twisted Hallway Switch with Hookshot': {
    #    'name'    : 'logic_forest_mq_hallway_switch_hookshot',
    #    'tags'    : ("Forest Temple", "MQ",),
    #    'tooltip' : '''\
    #                There's a very small gap between the glass block
    #                and the wall. Through that gap you can hookshot
    #                the target on the ceiling.
    #                '''},
    'Forest Temple MQ Twisted Hallway Switch with Boomerang': {
        'name'    : 'logic_forest_mq_hallway_switch_boomerang',
        'tags'    : ("Forest Temple", "Entrance", "MQ",),
        'tooltip' : '''\
                    The Boomerang can return to Link through walls,
                    allowing child to hit the hallway switch. This
                    can be used to allow adult to pass through later,
                    or in conjuction with "Forest Temple Outside
                    Backdoor with Jump Slash".
                    '''},
    'Fire Temple Boss Door without Hover Boots or Pillar': {
        'name'    : 'logic_fire_boss_door_jump',
        'tags'    : ("Fire Temple", "MQ",),
        'tooltip' : '''\
                    The Fire Temple Boss Door can be reached with a precise
                    jump. You must be touching the side wall of the room so
                    that Link will grab the ledge from farther away than
                    is normally possible.
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
    'Fire Temple East Tower without Scarecrow\'s Song': {
        'name'    : 'logic_fire_scarecrow',
        'tags'    : ("Fire Temple",),
        'tooltip' : '''\
                    Also known as "Pixelshot".
                    The Longshot can reach the target on the elevator
                    itself, allowing you to skip needing to spawn the
                    scarecrow.
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
    'Fire Temple MQ Chest Near Boss without Breaking Crate': {
        'name'    : 'logic_fire_mq_near_boss',
        'tags'    : ("Fire Temple", "MQ",),
        'tooltip' : '''\
                    The hitbox for the torch extends a bit outside of the crate.
                    Shoot a flaming arrow at the side of the crate to light the
                    torch without needing to get over there and break the crate.
                    '''},
    'Fire Temple MQ Big Lava Room Blocked Door without Hookshot': {
        'name'    : 'logic_fire_mq_blocked_chest',
        'tags'    : ("Fire Temple", "MQ",),
        'tooltip' : '''\
                    There is a gap between the hitboxes of the flame
                    wall in the big lava room. If you know where this
                    gap is located, you can jump through it and skip
                    needing to use the Hookshot. To do this without
                    taking damage is more precise.
                    '''},
    'Fire Temple MQ Boss Key Chest without Bow': {
        'name'    : 'logic_fire_mq_bk_chest',
        'tags'    : ("Fire Temple", "MQ",),
        'tooltip' : '''\
                    It is possible to light both of the timed torches
                    to unbar the door to the boss key chest's room
                    with just Din's Fire if you move very quickly
                    between the two torches. It is also possible to
                    unbar the door with just Din's by abusing an
                    oversight in the way the game counts how many
                    torches have been lit.
                    '''},
    'Fire Temple MQ Climb without Fire Source': {
        'name'    : 'logic_fire_mq_climb',
        'tags'    : ("Fire Temple", "MQ",),
        'tooltip' : '''\
                    You can use the Hover Boots to hover around to
                    the climbable wall, skipping the need to use a
                    fire source and spawn a Hookshot target.
                    '''},
    'Fire Temple MQ Lizalfos Maze Side Room without Box': {
        'name'    : 'logic_fire_mq_maze_side_room',
        'tags'    : ("Fire Temple", "MQ",),
        'tooltip' : '''\
                    You can walk from the blue switch to the door and
                    quickly open the door before the bars reclose. This
                    skips needing to reach the upper sections of the
                    maze to get a box to place on the switch.
                    '''},
    'Fire Temple MQ Lower to Upper Lizalfos Maze with Hover Boots': {
        'name'    : 'logic_fire_mq_maze_hovers',
        'tags'    : ("Fire Temple", "MQ",),
        'tooltip' : '''\
                    Use the Hover Boots off of a crate to
                    climb to the upper maze without needing
                    to spawn and use the Hookshot targets.
                    '''},
    'Fire Temple MQ Lower to Upper Lizalfos Maze with Precise Jump': {
        'name'    : 'logic_fire_mq_maze_jump',
        'tags'    : ("Fire Temple", "MQ",),
        'tooltip' : '''\
                    A precise jump off of a crate can be used to
                    climb to the upper maze without needing to spawn
                    and use the Hookshot targets. This trick
                    supersedes both "Fire Temple MQ Lower to Upper
                    Lizalfos Maze with Hover Boots" and "Fire Temple
                    MQ Lizalfos Maze Side Room without Box".
                    '''},
    'Fire Temple MQ Above Flame Wall Maze GS from Below with Longshot': {
        'name'    : 'logic_fire_mq_above_maze_gs',
        'tags'    : ("Fire Temple", "Skulltulas", "MQ",),
        'tooltip' : '''\
                    The floor of the room that contains this Skulltula
                    is only solid from above. From the maze below, the
                    Longshot can be shot through the ceiling to obtain 
                    the token with two fewer small keys than normal.
                    '''},                    
    'Fire Temple MQ Flame Wall Maze Skip': {
        'name'    : 'logic_fire_mq_flame_maze',
        'tags'    : ("Fire Temple", "Skulltulas", "MQ",),
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
    'Water Temple Cracked Wall with Hover Boots': {
        'name'    : 'logic_water_cracked_wall_hovers',
        'tags'    : ("Water Temple",),
        'tooltip' : '''\
                    With a midair side-hop while wearing the Hover
                    Boots, you can reach the cracked wall without
                    needing to raise the water up to the middle level.
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
    'Water Temple North Basement Ledge with Precise Jump': {
        'name'    : 'logic_water_north_basement_ledge_jump',
        'tags'    : ("Water Temple", "MQ",),
        'tooltip' : '''\
                    In the northern basement there's a ledge from where, in
                    vanilla Water Temple, boulders roll out into the room.
                    Normally to jump directly to this ledge logically
                    requires the Hover Boots, but with precise jump, it can
                    be done without them. This trick applies to both
                    Vanilla and Master Quest.
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
    'Water Temple Dragon Statue Jump Dive': {
        'name'    : 'logic_water_dragon_jump_dive',
        'tags'    : ("Water Temple", "MQ",),
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
    'Water Temple MQ Central Pillar with Fire Arrows': {
        'name'    : 'logic_water_mq_central_pillar',
        'tags'    : ("Water Temple", "MQ",),
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
    'Water Temple MQ North Basement GS without Small Key': {
        'name'    : 'logic_water_mq_locked_gs',
        'tags'    : ("Water Temple", "Skulltulas", "MQ",),
        'tooltip' : '''\
                    There is an invisible Hookshot target that can be used
                    to get over the gate that blocks you from going to this
                    Skulltula early, skipping a small key as well as
                    needing Hovers or Scarecrow to reach the locked door.
                    '''},
    'Shadow Temple Stationary Objects without Lens of Truth': {
        'name'    : 'logic_lens_shadow',
        'tags'    : ("Lens of Truth", "Shadow Temple",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Shadow Temple for most areas in the dungeon
                    except for crossing the moving platform in the huge
                    pit room and for fighting Bongo Bongo.
                    '''},
    'Shadow Temple Invisible Moving Platform without Lens of Truth': {
        'name'    : 'logic_lens_shadow_platform',
        'tags'    : ("Lens of Truth", "Shadow Temple",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Shadow Temple to cross the invisible moving
                    platform in the huge pit room in either direction.
                    '''},
    'Shadow Temple Bongo Bongo without Lens of Truth': {
        'name'    : 'logic_lens_bongo',
        'tags'    : ("Shadow Temple", "Entrance", "MQ",),
        'tooltip' : '''\
                    Bongo Bongo can be defeated without the use of
                    Lens of Truth, as the hands give a pretty good
                    idea of where the eye is.
                    '''},
    'Shadow Temple Stone Umbrella Skip': {
        'name'    : 'logic_shadow_umbrella',
        'tags'    : ("Shadow Temple", "MQ",),
        'tooltip' : '''\
                    A very precise Hover Boots movement
                    from off of the lower chest can get you
                    on top of the crushing spikes without
                    needing to pull the block. Applies to
                    both Vanilla and Master Quest.
                    '''},
    'Shadow Temple Falling Spikes GS with Hover Boots': {
        'name'    : 'logic_shadow_umbrella_gs',
        'tags'    : ("Shadow Temple", "Skulltulas", "MQ",),
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
    'Shadow Temple Freestanding Key with Bombchu': {
        'name'    : 'logic_shadow_freestanding_key',
        'tags'    : ("Shadow Temple",),
        'tooltip' : '''\
                    Release the Bombchu with good timing so that
                    it explodes near the bottom of the pot.
                    '''},
    'Shadow Temple River Statue with Bombchu': {
        'name'    : 'logic_shadow_statue',
        'tags'    : ("Shadow Temple", "MQ",),
        'tooltip' : '''\
                    By sending a Bombchu around the edge of the
                    gorge, you can knock down the statue without
                    needing a Bow.
                    Applies in both vanilla and MQ Shadow.
                    '''},
    'Shadow Temple Bongo Bongo without projectiles': {
        'name'    : 'logic_shadow_bongo',
        'tags'    : ("Shadow Temple", "Entrance",),
        'tooltip' : '''\
                    Using precise sword slashes, Bongo Bongo can be
                    defeated without using projectiles. This is
                    only relevant in conjunction with Shadow Temple
                    dungeon shortcuts or shuffled boss entrances.
                    '''},
    'Shadow Temple MQ Stationary Objects without Lens of Truth': {
        'name'    : 'logic_lens_shadow_mq',
        'tags'    : ("Lens of Truth", "Shadow Temple", "MQ",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Shadow Temple MQ for most areas in the dungeon.
                    See "Shadow Temple MQ Invisible Moving Platform
                    without Lens of Truth", "Shadow Temple MQ Invisible
                    Blades Silver Rupees without Lens of Truth",
                    "Shadow Temple MQ 2nd Dead Hand without Lens of Truth",
                    and "Shadow Temple Bongo Bongo without Lens of Truth"
                    for exceptions.
                    '''},
    'Shadow Temple MQ Invisible Blades Silver Rupees without Lens of Truth': {
        'name'    : 'logic_lens_shadow_mq_invisible_blades',
        'tags'    : ("Lens of Truth", "Shadow Temple", "MQ",),
        'tooltip' : '''\
                    Removes the requirement for the Lens of Truth or
                    Nayru's Love in Shadow Temple MQ for the Invisible
                    Blades room silver rupee collection.
                    '''},                    
    'Shadow Temple MQ Invisible Moving Platform without Lens of Truth': {
        'name'    : 'logic_lens_shadow_mq_platform',
        'tags'    : ("Lens of Truth", "Shadow Temple", "MQ",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Shadow Temple MQ to cross the invisible moving
                    platform in the huge pit room in either direction.
                    '''},
    'Shadow Temple MQ 2nd Dead Hand without Lens of Truth': {
        'name'    : 'logic_lens_shadow_mq_dead_hand',
        'tags'    : ("Lens of Truth", "Shadow Temple", "MQ",),
        'tooltip' : '''\
                    Dead Hand spawns in a random spot within the room.
                    Having Lens removes the hassle of having to comb
                    the room looking for his spawn location.
                    '''},
    'Shadow Temple MQ Truth Spinner Gap with Longshot': {
        'name'    : 'logic_shadow_mq_gap',
        'tags'    : ("Shadow Temple", "MQ",),
        'tooltip' : '''\
                    You can Longshot a torch and jump-slash recoil onto
                    the tongue. It works best if you Longshot the right
                    torch from the left side of the room.
                    '''},
    'Shadow Temple MQ Invisible Blades without Song of Time': {
        'name'    : 'logic_shadow_mq_invisible_blades',
        'tags'    : ("Shadow Temple", "MQ",),
        'tooltip' : '''\
                    The Like Like can be used to boost you into the
                    silver rupee or recovery hearts that normally
                    require Song of Time. This cannot be performed
                    on OHKO since the Like Like does not boost you
                    high enough if you die.
                    '''},
    'Shadow Temple MQ Lower Huge Pit without Fire Source': {
        'name'    : 'logic_shadow_mq_huge_pit',
        'tags'    : ("Shadow Temple", "MQ",),
        'tooltip' : '''\
                    Normally a frozen eye switch spawns some platforms
                    that you can use to climb down, but there's actually
                    a small piece of ground that you can stand on that
                    you can just jump down to.
                    '''},
    'Shadow Temple MQ Windy Walkway Reverse without Hover Boots': {
        'name'    : 'logic_shadow_mq_windy_walkway',
        'tags'    : ("Shadow Temple", "MQ",),
        'tooltip' : '''\
                    With shadow dungeon shortcuts enabled, it is possible
                    to jump from the alcove in the windy hallway to the
                    middle platform. There are two methods: wait out the fan
                    opposite the door and hold forward, or jump to the right
                    to be pushed by the fan there towards the platform ledge.
                    Note that jumps of this distance are inconsistent, but
                    still possible.
                    '''},
    'Spirit Temple without Lens of Truth': {
        'name'    : 'logic_lens_spirit',
        'tags'    : ("Lens of Truth", "Spirit Temple",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Spirit Temple.
                    '''},
    'Spirit Temple Child Side Bridge with Bombchu': {
        'name'    : 'logic_spirit_child_bombchu',
        'tags'    : ("Spirit Temple",),
        'tooltip' : '''\
                    A carefully-timed Bombchu can hit the switch.
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
    'Spirit Temple Lower Adult Switch with Bombs': {
        'name'    : 'logic_spirit_lower_adult_switch',
        'tags'    : ("Spirit Temple",),
        'tooltip' : '''\
                    A bomb can be used to hit the switch on the ceiling,
                    but it must be thrown from a particular distance
                    away and with precise timing.
                    '''},
    'Spirit Temple Main Room Jump from Hands to Upper Ledges': {
        'name'    : 'logic_spirit_lobby_jump',
        'tags'    : ("Spirit Temple", "Skulltulas", "MQ",),
        'tooltip' : '''\
                    A precise jump to obtain the following as adult
                    without needing one of Hover Boots, or Hookshot
                    (in vanilla) or Song of Time (in MQ):
                    - Spirit Temple Statue Room Northeast Chest
                    - Spirit Temple GS Lobby
                    - Spirit Temple MQ Central Chamber Top Left Pot 1
                    - Spirit Temple MQ Central Chamber Top Left Pot 2
                    '''},
    'Spirit Temple Main Room Hookshot to Boss Platform': {
        'name'    : 'logic_spirit_platform_hookshot',
        'tags'    : ("Spirit Temple",),
        'tooltip' : '''\
                    Precise hookshot aiming at the platform chains can be
                    used to reach the boss platform from the middle landings.
                    Using a jump slash immediately after reaching a chain
                    makes aiming more lenient. Relevant only when Spirit
                    Temple boss shortcuts are on.
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
    'Spirit Temple Shifting Wall with No Additional Items': {
        'name'    : 'logic_spirit_wall',
        'tags'    : ("Spirit Temple",),
        'tooltip' : '''\
                    Logic normally guarantees a way of dealing with both
                    the Beamos and the Walltula before climbing the wall.
                    '''},
    'Spirit Temple MQ without Lens of Truth': {
        'name'    : 'logic_lens_spirit_mq',
        'tags'    : ("Lens of Truth", "Spirit Temple", "MQ",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Spirit Temple MQ.
                    '''},
    'Spirit Temple MQ Sun Block Room as Child without Song of Time': {
        'name'    : 'logic_spirit_mq_sun_block_sot',
        'tags'    : ("Spirit Temple", "MQ",),
        'tooltip' : '''\
                    While adult can easily jump directly to the switch that
                    unbars the door to the sun block room, child Link cannot
                    make the jump without spawning a Song of Time block to
                    jump from. You can skip this by throwing the crate down
                    onto the switch from above, which does unbar the door,
                    however the crate immediately breaks, so you must move
                    quickly to get through the door before it closes back up.
                    '''},
    'Spirit Temple MQ Sun Block Room GS with Boomerang': {
        'name'    : 'logic_spirit_mq_sun_block_gs',
        'tags'    : ("Spirit Temple", "Skulltulas", "MQ",),
        'tooltip' : '''\
                    Throw the Boomerang in such a way that it
                    curves through the side of the glass block
                    to hit the Gold Skulltula.
                    '''},                    
    'Spirit Temple MQ Lower Adult without Fire Arrows': {
        'name'    : 'logic_spirit_mq_lower_adult',
        'tags'    : ("Spirit Temple", "MQ",),
        'tooltip' : '''\
                    By standing in a precise position it is possible to
                    light two of the torches with a single use of Din\'s
                    Fire. This saves enough time to be able to light all
                    three torches with only Din\'s.
                    '''},
    'Spirit Temple MQ Frozen Eye Switch without Fire': {
        'name'    : 'logic_spirit_mq_frozen_eye',
        'tags'    : ("Spirit Temple", "MQ",),
        'tooltip' : '''\
                    You can melt the ice by shooting an arrow through a
                    torch. The only way to find a line of sight for this
                    shot is to first spawn a Song of Time block, and then
                    stand on the very edge of it.
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
    'Ice Cavern MQ Red Ice GS without Song of Time': {
        'name'    : 'logic_ice_mq_red_ice_gs',
        'tags'    : ("Ice Cavern", "Skulltulas", "MQ",),
        'tooltip' : '''\
                    If you side-hop into the perfect position, you
                    can briefly stand on the platform with the red
                    ice just long enough to dump some blue fire.
                    '''},
    'Ice Cavern MQ Scarecrow GS with No Additional Items': {
        'name'    : 'logic_ice_mq_scarecrow',
        'tags'    : ("Ice Cavern", "Skulltulas", "MQ",),
        'tooltip' : '''\
                    A precise jump can be used to reach this alcove.
                    '''},
    'Gerudo Training Ground without Lens of Truth': {
        'name'    : 'logic_lens_gtg',
        'tags'    : ("Lens of Truth", "Gerudo Training Ground",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Gerudo Training Ground.
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
    'Reach Gerudo Training Ground Fake Wall Ledge with Hover Boots': {
        'name'    : 'logic_gtg_fake_wall',
        'tags'    : ("Gerudo Training Ground", "MQ",),
        'tooltip' : '''\
                    A precise Hover Boots use from the top of the chest can allow
                    you to grab the ledge without needing the usual requirements.
                    In Master Quest, this always skips a Song of Time requirement.
                    In Vanilla, this skips a Hookshot requirement, but is only
                    relevant if "Gerudo Training Ground Left Side Silver Rupees
                    without Hookshot" is enabled.
                    '''},
    'Gerudo Training Ground MQ without Lens of Truth': {
        'name'    : 'logic_lens_gtg_mq',
        'tags'    : ("Lens of Truth", "Gerudo Training Ground", "MQ",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Gerudo Training Ground MQ.
                    '''},
    'Gerudo Training Ground MQ Left Side Silver Rupees with Hookshot': {
        'name'    : 'logic_gtg_mq_with_hookshot',
        'tags'    : ("Gerudo Training Ground", "MQ",),
        'tooltip' : '''\
                    The highest silver rupee can be obtained by
                    hookshotting the target and then immediately jump
                    slashing toward the rupee.
                    '''},
    'Gerudo Training Ground MQ Left Side Silver Rupees without Hookshot': {
        'name'    : 'logic_gtg_mq_without_hookshot',
        'tags'    : ("Gerudo Training Ground", "MQ",),
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
    'Ganon\'s Castle without Lens of Truth': {
        'name'    : 'logic_lens_castle',
        'tags'    : ("Lens of Truth", "Ganon's Castle",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Ganon's Castle.
                    '''},
    'Spirit Trial without Hookshot': {
        'name'    : 'logic_spirit_trial_hookshot',
        'tags'    : ("Ganon's Castle",),
        'tooltip' : '''\
                    A precise jump off of an Armos can
                    collect the highest rupee.
                    '''},
    'Ganon\'s Castle MQ without Lens of Truth': {
        'name'    : 'logic_lens_castle_mq',
        'tags'    : ("Lens of Truth", "Ganon's Castle", "MQ",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Ganon's Castle MQ.
                    '''},
    'Fire Trial MQ with Hookshot': {
        'name'    : 'logic_fire_trial_mq',
        'tags'    : ("Ganon's Castle", "MQ",),
        'tooltip' : '''\
                    It's possible to hook the target at the end of
                    fire trial with just Hookshot, but it requires
                    precise aim and perfect positioning. The main
                    difficulty comes from getting on the very corner
                    of the obelisk without falling into the lava.
                    '''},
    'Shadow Trial MQ Torch with Bow': {
        'name'    : 'logic_shadow_trial_mq',
        'tags'    : ("Ganon's Castle", "MQ",),
        'tooltip' : '''\
                    You can light the torch in this room without a fire
                    source by shooting an arrow through the lit torch
                    at the beginning of the room. Because the room is
                    so dark and the unlit torch is so far away, it can
                    be difficult to aim the shot correctly.
                    '''},
    'Light Trial MQ without Hookshot': {
        'name'    : 'logic_light_trial_mq',
        'tags'    : ("Ganon's Castle", "MQ",),
        'tooltip' : '''\
                    If you move quickly you can sneak past the edge of
                    a flame wall before it can rise up to block you.
                    In this case to do it without taking damage is
                    especially precise.
                    '''},
}

# Below is the list of possible settings.
# They are mostly listed in the order in which they appear in the GUI
# (with the exception of major settings like ALR, Rainbow Bridge, Ganon's Boss Key, Triforce Hunt).
# This makes the Spoiler Log more readable for Support and users.

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
	Checkbutton(
        name           = 'web_wad_legacy_mode',
        gui_text       = 'WAD Legacy Mode',
		shared		   = False,
        default        = False,
		gui_tooltip	   = "Enabling this will avoid any patching of the VC emulator in case your Wii does not have support for it. Recommended to be left unchecked.",
		gui_params  = {
			"no_line_break"		 : False,
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
                'web_wad_channel_title',
				'web_wad_legacy_mode']
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
    Checkbutton('patch_without_output', None),
    Checkbutton('disable_custom_music', None),
    Checkbutton(
        name           = 'generate_from_file',
        gui_text       = 'Generate From Patch File',
        default        = False,
        disable        = {
            True : {
                'tabs' : ['main_tab', 'detailed_tab', 'starting_tab', 'other_tab'],
                'sections' : ['preset_section'],
                'settings' : ['count', 'create_spoiler', 'world_count', 'enable_distribution_file', 'distribution_file', 'create_patch_file', 'show_seed_info', 'user_message'],
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
                        'web_wad_channel_id','web_wad_channel_title', 'web_wad_legacy_mode',
                        'model_adult', 'model_child', 'model_adult_filepicker', 'model_child_filepicker',
                        'sfx_link_adult', 'sfx_link_child',
                    ],
                },
                True : {
                    'settings' : [
                        'model_adult', 'model_child', 'model_unavailable_msg',
                        'sfx_link_unavailable_msg',
                    ],
                },
            },
            'electron:disable' : {
                False : {
                    'settings' : [
                        'model_adult_filepicker', 'model_child_filepicker', 'model_unavailable_msg',
                        'sfx_link_unavailable_msg',
                    ],
                },
                True : {
                    'settings' : [
                        'model_adult_filepicker', 'model_child_filepicker', 'model_unavailable_msg',
                        'sfx_link_unavailable_msg',
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
    Checkbutton(
        name           = 'show_seed_info',
        gui_text       = 'Show Seed Info on File Screen',
        shared         = True,
        gui_tooltip    = '''\
            Display the version number, generation time, and user
            message on the file screen.
        ''',
        default        = True,
        disable        = {
            False : {'settings' : ["user_message"]}
        },
		gui_params = {
            "hide_when_disabled" : True,
        }
    ),
    Setting_Info(
        name           = 'user_message',
        type           = str,
        gui_text       = "User-Configurable Message",
        shared         = True,
        gui_type       = "Textinput",
        choices        = {},
        gui_tooltip    = """\
            Add a custom message to the seed info.
        """,
        default        = "",
        gui_params     = {
            "size"               : "full",
            "max_length"         : 42,
            "hide_when_disabled" : True,
        }
    ),
    Setting_Info('seed',              str, None, None, False, {}),
    Setting_Info('patch_file',        str, "Patch File", "Fileinput", False, {},
        gui_params = {
            "file_types": [
                {
                  "name": "Patch File Archive",
                  "extensions": [ "zpfz", "zpf", "patch" ]
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

    # ROM Options

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
        gui_tooltip='''\
                 Cosmetics Logs are only output if one of the output types below are enabled.
                 ''',
        default        = True,
        disabled_default = False,
    ),
    Setting_Info(
        name           = 'output_types',
        type           = str,
        gui_text       = "Output Types",
        gui_type       = "Textbox",
        shared         = False,
        choices        = {},
    ),
    Checkbutton(
        name           = 'create_patch_file',
        gui_text       = '.zpf (Patch File)',
        gui_tooltip    = '''\
            Patch files are used to send the patched data to other
            people without sending the ROM file.
        ''',
        shared         = False,
        gui_params     = {
            "no_line_break": True,
        },
    ),
    Checkbutton(
        name           = 'create_compressed_rom',
        gui_text       = '.z64 (N64/Emulator)',
        default        = True,
        gui_tooltip    = '''\
            A "compressed" .z64 ROM file for use on
            N64 emulators or with an N64 flash cart.
        ''',
        shared         = False,
        gui_params     = {
            "no_line_break": True,
        },
    ),
    Checkbutton(
        name           = 'create_wad_file',
        gui_text       = '.wad (Wii VC)',
        gui_tooltip    = '''\
            .wad files are used to play on Wii Virtual Console or Dolphin Emulator.
        ''',
        shared         = False,
        disable        = {
            False: {'settings' : ['wad_file', 'wad_channel_title', 'wad_channel_id']},
        },
        gui_params     = {
            "no_line_break": True,
        },
    ),
    Checkbutton(
        name           = 'create_uncompressed_rom',
        gui_text       = 'Uncompressed ROM (Development)',
        gui_tooltip    = '''\
            Uncompressed ROMs may be helpful for developers
            but should not be used to play through a seed
            normally as it will very likely cause crashes.
            Use a compressed ROM instead.
        ''',
        shared         = False,
    ),
    Setting_Info(
        name        = 'wad_file',
        type        = str,
        gui_text    = "Base WAD File",
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
        name        = 'wad_channel_id',
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
            "no_line_break": True,
            "hide_when_disabled" : True,
        }
    ),
    Setting_Info(
        name        = 'wad_channel_title',
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
    Setting_Info('presets',           str, "", "Presetinput", False, {},
        default        = "[New Preset]",
        gui_tooltip    = '''\
            Select a setting preset to apply.

            Default/Beginner is aimed at those familiar with the vanilla game who desire a similar progression.
            Uses base glitchless logic. No timesavers (See the tab "Other") are enabled in this preset 
            and the world begins closed. Expect a long playthrough.

            Easy Mode is aimed at those who have perhaps seen a few randomizer runs previously and/or 
            wish to dive right in. Uses base glitchless logic. Most timesavers (See the tab "Other") 
            are enabled and the world is more open after leaving Kokiri Forest.

            Hell Mode is designed to be as frustrating an experience as possible, with every setting enabled
            to provide maximum randomness as well as things like one-hit-KO, one-bonk-KO and max ice traps.
            It still uses glitchless logic to ensure a beatable seed. However, be aware that all glitchless 
            "tricks" are enabled which have the potential to require the player to perform difficult techniques. 
            Expect a long and painful playthrough, even with good note-taking.

            The other presets are for racing and/or tournaments. 

            After a preset is loaded, the settings can be viewed/changed in the other tabs before
            generating a seed.
            ''',
    ),

    # Main Rules (and "Guarantee Reachable Locations")

    Checkbutton(
        name           = 'randomize_settings',
        gui_text       = 'Randomize Main Rule Settings',
        gui_tooltip    = '''\
                         Randomizes all settings on the 'Main Rules' tab, except:

                         - Logic Rules
                         - (Random) Number of MQ Dungeons
                         - Pre-completed Dungeons
                         - Rainbow Bridge/Ganon Boss Key Requirements: Gold Skulltula Tokens
                         - Variable numbers of Spiritual Stones, Medallions, or Dungeons
                         for Rainbow Bridge and Ganon's Boss Key
                         (you will always be required to obtain all the relevant rewards)
                         - Scrub Shuffle will either be "Off" or "On (Affordable)"
                         ''',
        default        = False,
        disable        = {
            True : {
                'sections' : ['open_section', 'shuffle_section', 'shuffle_dungeon_section'],
                'settings': ['starting_age', 'shuffle_interior_entrances', 'shuffle_grotto_entrances', 'shuffle_dungeon_entrances',
                             'shuffle_bosses', 'shuffle_overworld_entrances', 'owl_drops', 'warp_songs', 'spawn_positions',
                             'triforce_hunt', 'triforce_count_per_world', 'triforce_goal_per_world', 'bombchus_in_logic', 'one_item_per_dungeon'],
            }
        },
        shared         = True,
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
                                         'warp_songs', 'spawn_positions', 'mq_dungeons_mode', 'mq_dungeons_specific',
                                         'mq_dungeons_count', 'shuffle_bosses', 'dungeon_shortcuts', 'deadly_bonks', 
                                         'shuffle_freestanding_items', 'shuffle_pots', 'shuffle_crates', 'shuffle_beehives']},
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
            be obtainable. In Triforce Hunt, this will instead guarantee that all Triforce Pieces can be obtained. Hint
            distributions that define custom goals or remove the default goals will affect item placement as well.

            'Required Only': Only items and locations required to beat the game will be guaranteed reachable.
        ''',
        gui_params={
            "hide_when_disabled": True,
        },
        shared         = True
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
            True  : {'settings' : ['shuffle_ganon_bosskey', 'ganon_bosskey_stones', 'ganon_bosskey_medallions', 'ganon_bosskey_rewards', 'ganon_bosskey_tokens', 'ganon_bosskey_hearts']},
            False : {'settings' : ['triforce_count_per_world', 'triforce_goal_per_world']}
        },
    ),
    Scale(
        name           = 'triforce_count_per_world',
        gui_text       = 'Triforces Per World',
        default        = 30,
        min            = 1,
        max            = 999,
        shared         = True,
        gui_tooltip    = '''\
            Select the amount of Triforce Pieces placed in each world.
            Each world will have the same number of triforces.

            A good number to choose is 1.5 times the amount of
            Triforce Pieces required per world, for example 30
            Triforces placed with a goal of 20. Higher ratios will
            result in easier and shorter seeds, while a ratio closer
            to 1 will generally be longer and more difficult.
        ''',
        gui_params     = {
            "hide_when_disabled": True,
            'web:max': 200,
            'electron:max': 200,
        },
    ),
    Scale(
        name           = 'triforce_goal_per_world',
        gui_text       = 'Required Triforces Per World',
        default        = 20,
        min            = 1,
        max            = 999,
        shared         = True,
        gui_tooltip    = '''\
            Select the amount of Triforce Pieces required to beat the game.

            In multiworld, the required amount will be per world collectively. 
            For example, if this is set to 20 in a 2 player multiworld, players 
            need 40 total, but one player could obtain 30 and the other 10. 
        ''',
        gui_params     = {
            "hide_when_disabled": True,
            'web:max': 100,
            'electron:max': 100,
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
            'hearts':     "Hearts",
        },
        gui_tooltip    = '''\
            Sets the condition for the Light Arrow Cutscene
            check to give you the item from Zelda.
            
            'Vanilla': Shadow and Spirit Medallions.
            'Stones': A configurable amount of Spiritual Stones.
            'Medallions': A configurable amount of Medallions.
            'Dungeons': A configurable amount of Dungeon Rewards.
            'Tokens': A configurable amount of Gold Skulltula Tokens.
            'Hearts': A configurable amount of hearts.
        ''',
        shared         = True,
        disable        = {
            '!stones':  {'settings': ['lacs_stones']},
            '!medallions':  {'settings': ['lacs_medallions']},
            '!dungeons':  {'settings': ['lacs_rewards']},
            '!tokens':  {'settings': ['lacs_tokens']},
            '!hearts':  {'settings': ['lacs_hearts']},
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
        max            = 999,
        gui_tooltip    = '''\
            Select the amount of Gold Skulltula Tokens
            required to trigger the Light Arrow Cutscene.
        ''',
        shared         = True,
        disabled_default = 0,
        gui_params     = {
            'optional': True,
            "hide_when_disabled": True,
            'web:max': 100,
            'electron:max': 100,
        },
    ),
    Scale(
        name           = 'lacs_hearts',
        gui_text       = "Hearts Required for LACS",
        default        = 20,
        min            = 4,
        max            = 20,
        gui_tooltip    = '''\
            Select the amount of hearts
            required to trigger the Light Arrow Cutscene.
        ''',
        shared         = True,
        disabled_default = 0,
        gui_params     = {
            'optional': True,
            "hide_when_disabled": True,
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
            'hearts':     'Hearts',
            'random':     'Random'
        },
        gui_tooltip    = '''\
            'Always Open': Rainbow Bridge is always present.
            'Vanilla Requirements': Spirit/Shadow Medallions and Light Arrows.
            'Spiritual Stones': A configurable amount of Spiritual Stones.
            'Medallions': A configurable amount of Medallions.
            'Dungeons': A configurable amount of Dungeon Rewards.
            'Gold Skulltula Tokens': A configurable amount of Gold Skulltula Tokens.
            'Hearts': A configurable amount of hearts.
            'Random': A random Rainbow Bridge requirement excluding Gold Skulltula Tokens.
        ''',
        shared         = True,
        disable        = {
            '!stones':     {'settings': ['bridge_stones']},
            '!medallions': {'settings': ['bridge_medallions']},
            '!dungeons':   {'settings': ['bridge_rewards']},
            '!tokens':     {'settings': ['bridge_tokens']},
            '!hearts':     {'settings': ['bridge_hearts']},
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
        max            = 999,
        gui_tooltip    = '''\
            Select the amount of Gold Skulltula Tokens required to spawn the rainbow bridge.
        ''',
        shared         = True,
        disabled_default = 0,
        gui_params     = {
            'hide_when_disabled': True,
            'web:max': 100,
            'electron:max': 100,
        },
    ),
    Scale(
        name           = 'bridge_hearts',
        gui_text       = "Hearts Required for Bridge",
        default        = 20,
        min            = 4,
        max            = 20,
        gui_tooltip    = '''\
            Select the amount of hearts required to spawn the rainbow bridge.
        ''',
        shared         = True,
        disabled_default = 0,
        gui_params     = {
            "hide_when_disabled": True,
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
    Combobox(
        name           = 'shuffle_ganon_bosskey',
        gui_text       = 'Ganon\'s Boss Key',
        default        = 'dungeon',
        disabled_default = 'triforce',
        choices        = {
            'remove':          "Remove (Keysy)",
            'vanilla':         "Vanilla Location",
            'dungeon':         "Own Dungeon",
            'regional':        "Regional",
            'overworld':       "Overworld Only",
            'any_dungeon':     "Any Dungeon",
            'keysanity':       "Anywhere (Keysanity)",
            'on_lacs':         "Light Arrow Cutscene",
            'stones':          "Stones",
            'medallions':      "Medallions",
            'dungeons':        "Dungeons",
            'tokens':          "Tokens",
            'hearts':          "Hearts",
        },
        gui_tooltip    = '''\
            'Remove': Ganon's Castle Boss Key is removed
            and the boss door in Ganon's Tower starts unlocked.
            
            'Vanilla': Ganon's Castle Boss Key will appear in 
            the vanilla location.
            
            'Own Dungeon': Ganon's Castle Boss Key can only appear
            inside Ganon's Castle.
            
            'Regional': Ganon's Castle Boss Key can only appear
            in Hyrule Field, Lon Lon Ranch, Market, Temple of Time, Hyrule Castle,
            (Outside) Ganon's Castle, and Inside Ganon's Castle.
            
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

            'Hearts': Ganon's Castle Boss Key will be awarded
            when reaching the target number of hearts.
        ''',
        shared         = True,
        disable        = {
            '!stones':  {'settings': ['ganon_bosskey_stones']},
            '!medallions':  {'settings': ['ganon_bosskey_medallions']},
            '!dungeons':  {'settings': ['ganon_bosskey_rewards']},
            '!tokens':  {'settings': ['ganon_bosskey_tokens']},
            '!hearts':  {'settings': ['ganon_bosskey_hearts']},
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
        max            = 999,
        gui_tooltip    = '''\
            Select the amount of Gold Skulltula Tokens
            required to receive Ganon's Castle Boss Key.
        ''',
        shared         = True,
        disabled_default = 0,
        gui_params     = {
            "hide_when_disabled": True,
            'web:max': 100,
            'electron:max': 100,
        },
    ),
    Scale(
        name           = 'ganon_bosskey_hearts',
        gui_text       = "Hearts Required for Ganon's BK",
        default        = 20,
        min            = 4,
        max            = 20,
        gui_tooltip    = '''\
            Select the amount of hearts
            required to receive Ganon's Castle Boss Key.
        ''',
        shared         = True,
        disabled_default = 0,
        gui_params     = {
            "hide_when_disabled": True,
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
            'regional':    'Regional',
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
            
            'Regional': Boss Keys can only appear in regions
            near the original dungeon (including the dungeon
            itself or other dungeons in the region).
            <a href="https://wiki.ootrandomizer.com/index.php?title=Hints#Hint_Regions" target="_blank">The Wiki has a list of corresponding regions here.</a>
            
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

            Try different combinations out, such as:
            'Small Keys: Dungeon' + 'Boss Keys: Anywhere'
            for a milder Keysanity experience.

            Regardless of the selected option, boss keys from
            pre-completed dungeons won't be placed outside their
            respective dungeons and boss keys from other dungeons
            won't be placed inside pre-completed dungeons.
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
            'regional':    'Regional',
            'overworld':   'Overworld Only',
            'any_dungeon': 'Any Dungeon',
            'keysanity':   'Anywhere (Keysanity)',
        },
        gui_tooltip    = '''\
            'Remove': Small Keys are removed. All locked doors in dungeons
            will be unlocked. An easier mode.

            'Vanilla': Small Keys will appear in their vanilla locations. You start
            with 3 keys in Spirit Temple MQ because the vanilla key layout is
            not beatable in logic. You start with 2 keys in Vanilla/MQ Shadow
            Temple with its dungeon shortcut enabled to prevent softlocks.

            'Own Dungeon': Small Keys can only appear in their respective
            dungeon. If Fire Temple is not a Master Quest dungeon, the door to
            the Boss Key chest will be unlocked.
            
            'Regional': Small Keys can only appear
            in regions near the original dungeon (including
            the dungeon itself or other dungeons in the region).
            <a href="https://wiki.ootrandomizer.com/index.php?title=Hints#Hint_Regions" target="_blank">The Wiki has a list of corresponding regions here.</a>
            
            'Overworld Only': Small Keys can only appear outside
            of dungeons. You may need to enter a dungeon multiple
            times to gain items to access the overworld locations
            with the keys required to finish a dungeon.
            
            'Any Dungeon': Small Keys can only appear inside of any dungeon, but
            won't necessarily be in the dungeon that the key is for. A difficult mode
            since it is more likely to need to enter a dungeon multiple times.

            'Anywhere': Small Keys can appear anywhere in the world. A difficult
            mode since it is more likely to need to enter a dungeon multiple times.

            Try different combination out, such as:
            'Small Keys: Dungeon' + 'Boss Keys: Anywhere'
            for a milder Keysanity experience.

            Regardless of the selected option, small keys from pre-completed dungeons
            won't be placed outside their respective dungeons and small keys from
            other dungeons won't be placed inside pre-completed dungeons.
        ''',
        disable        = {
            'any_dungeon': {'settings': ['one_item_per_dungeon']}
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
            'vanilla':     "Vanilla Locations",
            'fortress':    "Gerudo Fortress Region",
            'regional':    "Regional",
            'overworld':   "Overworld Only",
            'any_dungeon': "Any Dungeon",
            'keysanity':   "Anywhere (Keysanity)",
        },
        gui_tooltip    = '''\
            "Vanilla": Thieves' Hideout Keys will appear in their
            vanilla location, dropping from fighting Gerudo guards
            that attack when trying to free the jailed carpenters.
            
            "Regional": Thieves' Hideout Keys can only appear in
            Gerudo Valley, Gerudo Fortress, Thieves' Hideout, Gerudo
            Training Ground, Haunted Wasteland, Desert Colossus, or
            Spirit Temple.
            
            "Overworld Only": Thieves' Hideout Keys can only appear
            outside of dungeons.
            
            "Any Dungeon": Thieves' Hideout Keys can only appear
            inside of dungeons.

            "Anywhere": Thieves' Hideout Keys can appear anywhere
            in the world.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'option_remove': ['fortress'],
        },
    ),
    Combobox(
        name           = 'key_rings_choice',
        gui_text       = 'Key Rings Mode',
        default        = 'off',
        choices        = {
            'off':       'Off',
            'choice':    'Choose dungeons',
            'all':       'All dungeons',
            'random':    'Random dungeons'
        },
        gui_tooltip     = '''\
            Selected dungeons will have all of their keys found 
            at once in a ring rather than individually. 

            For example, instead of shuffling 5 Forest Temple 
            small keys into the pool, you will find a single
            key ring which will give you all 5 keys at once.

            Selecting key ring for dungeons will have no effect
            if Small Keys are set to Remove or Vanilla.

            Selecting key ring for Thieves' Hideout will have 
            no effect if Thieves' Hideout keys are in vanilla 
            locations or Gerudo's Fortress is set to Rescue
            One Carpenter.
        ''',
        shared         = True,
        disable={
            'off': {'settings' : ['key_rings']},
            'all': {'settings' : ['key_rings']},
            'random': {'settings' : ['key_rings']},
        },
    ),
    Combobox(
        name            = 'key_rings',
        multiple_select = True,
        gui_text        = 'Key Rings',
        choices         = {
            'Thieves Hideout':        "Thieves' Hideout",
            'Forest Temple':          "Forest Temple",
            'Fire Temple':            "Fire Temple",
            'Water Temple':           "Water Temple",
            'Shadow Temple':          "Shadow Temple",
            'Spirit Temple':          "Spirit Temple",
            'Bottom of the Well':     "Bottom of the Well",
            'Gerudo Training Ground': "Gerudo Training Ground",
            'Ganons Castle':          "Ganon's Castle"
        },
        default         = [],
        gui_params     = {
            "hide_when_disabled": True,
        },
        gui_tooltip    = '''\
            Select areas with keyring instead of multiple keys
        ''',
        shared          = True,
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
            'regional':    'Regional',
            'overworld':   'Overworld Only',
            'any_dungeon': 'Any Dungeon',
            'keysanity':   'Anywhere',
        },
        gui_tooltip    = '''\
            'Remove': Maps and Compasses are removed.
            This will add a small amount of money and refill items to the pool.

            'Start With': Maps and Compasses are given to you from the start.
            This will add a small amount of money and refill items to the pool.

            'Vanilla': Maps and Compasses will appear in their vanilla locations.

            'Own Dungeon': Maps and Compasses can only appear in their respective
            dungeon.
            
            'Regional': Maps and Compasses can only appear in regions near the
            original dungeon (including the dungeon itself or other dungeons in
            the region). <a href="https://wiki.ootrandomizer.com/index.php?title=Hints#Hint_Regions" target="_blank">The Wiki has a list of corresponding regions here.</a>
            
            'Overworld Only': Maps and Compasses can only appear
            outside of dungeons.

            'Any Dungeon': Maps and Compasses can only appear in a dungeon, but
            not necessarily the dungeon they are for.            

            'Anywhere': Maps and Compasses can appear anywhere in the world.

            Setting 'Remove', 'Start With', 'Overworld', or 'Anywhere' will add 2
            more possible locations to each Dungeons. This makes dungeons more
            profitable, especially Ice Cavern, Water Temple, and Jabu Jabu's Belly.
            
            Regardless of the selected option, maps and compasses from pre-completed
            dungeons won't be placed outside their respective dungeons and maps and
            compasses from other dungeons won't be placed inside pre-completed dungeons.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
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
        name           = 'dungeon_shortcuts_choice',
        gui_text       = 'Dungeon Boss Shortcuts Mode',
        default        = 'off',
        choices        = {
            'off':       'Off',
            'choice':    'Specific Dungeons',
            'all':       'All Dungeons',
            'random':    'Random Dungeons'
        },
        gui_tooltip    = '''\
            Shortcuts to dungeon bosses are available
            without any requirements.
            Incompatible with glitched logic.

            Changes include (vanilla shown, MQ similar):
            <b>Deku Tree</b>: webs burned, block in the
            basement moved, 231 scrubs defeated
            <b>Dodongo's Cavern</b>: mud wall bombed,
            mouth opened and boss lobby floor bombed
            <b>Jabu Jabu</b>: pathway lowered
            <b>Forest Temple</b>: elevator raised and
            basement gates open
            <b>Fire Temple</b>: pillar knocked down
            <b>Water Temple</b>: no change, but see the
            note on "Shuffle Boss Entrances" below
            <b>Shadow Temple</b>: Truthspinner solved, boat
            block moved, and statue bridge moved. You start
            with 2 small keys if Shuffle Small Keys is set
            to Vanilla.
            <b>Spirit Temple</b>: lobby elevator activated,
            shortcut silver blocks moved, central room
            platform lowered, and statue face melted

            With "Shuffle Boss Entrances", the floor above
            King Dodongo's arena is opened based on the
            shortcut setting for the dungeon that contains
            the entrance to King Dodongo's boss room, not
            necessarily Dodongo's Cavern.

            Choose: Select dungeons with shortcuts
            All: Enable all dungeons shortcuts
            Random: Random dungeon shortcuts
        ''',
        shared         = True,
        disable={
            'off': {'settings' : ['dungeon_shortcuts']},
            'all': {'settings' : ['dungeon_shortcuts']},
            'random': {'settings' : ['dungeon_shortcuts']},
        },
    ),
    Combobox(
        name            = 'dungeon_shortcuts',
        multiple_select = True,
        gui_text        = 'Dungeon Boss Shortcuts',
        choices         = {
            'Deku Tree':        "Deku Tree",
            'Dodongos Cavern':  "Dodongo's Cavern",
            'Jabu Jabus Belly': "Jabu Jabu's Belly",
            'Forest Temple':    "Forest Temple",
            'Fire Temple':      "Fire Temple",
            'Water Temple':     "Water Temple",  # affects King Dodongo if he's in Water
            'Shadow Temple':    "Shadow Temple",
            'Spirit Temple':    "Spirit Temple",
        },
        default        = [],
        gui_params     = {
            "hide_when_disabled": True,
        },
        gui_tooltip    = '''\
            Select dungeons with shortcuts
        ''',
        shared          = True,
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
        name           = 'mq_dungeons_mode',
        gui_text       = 'MQ Dungeon Mode',
        default        = 'vanilla',
        choices        = {
            'vanilla':    "Vanilla",
            'mq':         "Master Quest",
            'specific':   "Specific Dungeons",
            'count':      "Count",
            'random':     "Completely Random",
        },
        gui_tooltip    = '''\
            'Vanilla': All dungeons will be the original versions.
            'Master Quest': All dungeons will be the MQ versions.
            'Specific Dungeons': Choose which specific dungeons will be MQ versions.
            'Count': Choose how many MQ dungeons will be randomly chosen.
            'Completely Random': Each dungeon will vanilla or MQ at random.
        ''',
        shared         = True,
        disable        = {
            'vanilla':  {'settings': ['mq_dungeons_count', 'mq_dungeons_specific']},
            'mq':       {'settings': ['mq_dungeons_count', 'mq_dungeons_specific']},
            'specific': {'settings': ['mq_dungeons_count']},
            'count':    {'settings': ['mq_dungeons_specific']},
            'random':   {'settings': ['mq_dungeons_count', 'mq_dungeons_specific']},
        },
        gui_params     = {
            'distribution': [
                ('random', 1),
            ],
        },
    ),
    Combobox(
        name            = 'mq_dungeons_specific',
        multiple_select = True,
        gui_text        = 'MQ Dungeons',
        choices         = {
            'Deku Tree':              "Deku Tree",
            'Dodongos Cavern':        "Dodongo's Cavern",
            'Jabu Jabus Belly':       "Jabu Jabu's Belly",
            'Forest Temple':          "Forest Temple",
            'Fire Temple':            "Fire Temple",
            'Water Temple':           "Water Temple",
            'Shadow Temple':          "Shadow Temple",
            'Spirit Temple':          "Spirit Temple",
            'Bottom of the Well':     "Bottom of the Well",
            'Ice Cavern':             "Ice Cavern",
            'Gerudo Training Ground': "Gerudo Training Ground",
            'Ganons Castle':          "Ganon's Castle",
        },
        default         = [],
        gui_tooltip     = '''\
            Select the specific dungeons you would
            like the Master Quest version of.
            The unselected dungeons will be
            the original version.
        ''',
        shared          = True,
        gui_params     = {
            "hide_when_disabled": True,
        },
    ),
    Scale(
        name           = 'mq_dungeons_count',
        gui_text       = "MQ Dungeon Count",
        default        = 0,
        min            = 0,
        max            = 12,
        gui_tooltip    = '''\
            Specify the number of Master Quest
            dungeons to appear in the game.
        ''',
        shared         = True,
        gui_params     = {
            "hide_when_disabled": True,
        },
    ),
    Combobox(
        name           = 'empty_dungeons_mode',
        gui_text       = 'Pre-completed Dungeons Mode',
        default        = 'none',
        choices        = {
            'none':       'Off',
            'specific':   'Specific Dungeons',
            'count':      'Count',
        },
        gui_tooltip    = '''\
            Pre-completed dungeons are dungeons guaranteed to be barren and whose
            dungeon rewards are given for free to the player before the beginning
            of the game. This setting only applies to dungeons with dungeon rewards
            (blue warps).

            - 'None': No dungeon will be pre-completed. Some dungeons may still be
            randomly rolled with no major items, but their dungeon rewards won't
            be given for free.
            - 'Specific Dungeons': Choose which specific dungeons will be pre-completed.
            - 'Count': Choose how many pre-completed dungeons will be randomly chosen.

            A same dungeon won't be both MQ and pre-completed unless it has been
            explicitly specified as such or unless it is the only way to fulfill both MQ and
            pre-completed selected settings.

            Pre-completed dungeons won't contain major items even if "Dungeons Have
            One Major Item" is on.

            Regardless of "Shuffle Dungeon Items" settings, dungeon items from
            pre-completed dungeons won't be placed outside their respective dungeons
            and dungeon items from other dungeons won't be placed inside pre-completed
            dungeons.

            If "Shuffle Songs" is set to "Dungeon rewards", then songs that would have
            been placed in pre-completed dungeons are given for free along with the
            free dungeon rewards.
        ''',
        shared         = True,
        disable        = {
            '!specific': {'settings': ['empty_dungeons_specific']},
            '!count':    {'settings': ['empty_dungeons_count']}
        },
        gui_params     = {
            'distribution':  [
                ('none', 1)
            ],
        },   
    ),
    Combobox(
        name            = 'empty_dungeons_specific',
        multiple_select = True,
        gui_text        = 'Pre-completed Dungeons',
        choices         = {
            'Deku Tree':              "Deku Tree",
            'Dodongos Cavern':        "Dodongo's Cavern",
            'Jabu Jabus Belly':       "Jabu Jabu's Belly",
            'Forest Temple':          "Forest Temple",
            'Fire Temple':            "Fire Temple",
            'Water Temple':           "Water Temple",
            'Shadow Temple':          "Shadow Temple",
            'Spirit Temple':          "Spirit Temple"
        },
        default         = [],
        gui_tooltip     = '''\
            Select the specific dungeons you would
            like to be pre-completed.
        ''',
        shared          = True,
        gui_params     = {
            "hide_when_disabled": True,
        },
    ),
    Scale(
        name           = 'empty_dungeons_count',
        gui_text       = "Pre-completed Dungeon Count",
        default        = 2,
        min            = 1,
        max            = 8,
        gui_tooltip    = '''\
            Specify the number of pre-completed
            dungeons to appear in the game.
        ''',
        shared         = True,
        gui_params     = {
            "hide_when_disabled": True,
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
    Combobox(
        name           = 'shuffle_dungeon_entrances',
        gui_text       = 'Shuffle Dungeon Entrances',
        default        = 'off',
        choices        = {
            'off':       'Off',
            'simple':    'Dungeon',
            'all':       'Dungeon and Ganon',
        },
        gui_tooltip    = '''\
            Shuffle the pool of dungeon entrances, including Bottom
            of the Well, Ice Cavern, and Gerudo Training Ground.

            Additionally, the entrances of Deku Tree, Fire Temple and
            Bottom of the Well are opened for both adult and child.

            With Dungeon and Ganon selected, all dungeons including Ganon's
            castle will be shuffled.

            Thieves' Hideout is not shuffled.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution': [
                ('off', 2),
                ('simple', 1),
                ('all', 1),
            ],
        },
    ),
    Combobox(
        name           = 'shuffle_bosses',
        gui_text       = 'Shuffle Boss Entrances',
        gui_tooltip    = '''\
            Shuffle dungeon boss rooms.  This affects the boss rooms of all stone and medallion dungeons.

            'Age-Restricted':
            Shuffle the locations of child boss rooms and adult boss rooms separately.

            'Full':
            Shuffle the locations of all boss rooms together.  Child may be expected to defeat Phantom Ganon and/or Bongo Bongo.
        ''',
        default        = 'off',
        choices        = {
            'off':       'Off',
            'limited':   'Age-Restricted',
            'full':      'Full',
        },
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
    Combobox(
        name           = 'spawn_positions',
        gui_text       = 'Randomize Overworld Spawns',
        multiple_select = True,
        choices         = {
            'child': 'Child',
            'adult': 'Adult',
        },
        gui_tooltip    = '''\
            Randomize where you start when loading
            a save in the Overworld. This means you may not necessarily
            spawn inside Link's House or Temple of Time.

            'Child': Child overworld spawn will be randomized.
            
            'Adult': Adult overworld spawn will be randomized.

            Selecting both options will randomize both spawns.

            This stays consistent after saving and loading the game again.
        ''',
        default        = [],
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
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
            bridge or Ganon Boss Key requirements are
            set to "GS Tokens".

            Heart Containers and Pieces of Heart only
            count as major items if the bridge or Ganon
            Boss Key requirements are set to "Hearts".

            Bombchus only count as major items if they
            are considered in logic.

            Pre-completed dungeons (if any) won't have
            a major item.

            This setting has potential to conflict with
            other randomizer settings. Should seeds continuously
            fail to generate, consider turning this option off.
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

            If some dungeons are pre-completed, songs that would have
            been located inside these dungeons are given for free along
            with the free dungeon rewards.

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
        disable        = {
            'off':  {'settings': ['shopsanity_prices']},
            '0':    {'settings': ['shopsanity_prices']},
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
        name           = 'shopsanity_prices',
        gui_text       = 'Shopsanity Prices',
        default        = 'random',
        choices        = {
            'random':          'Random',
            'random_starting':    'Starting Wallet',
            'random_adult':   'Adult\'s Wallet',
            'random_giant':    'Giant\'s Wallet',
            'random_tycoon':   'Tycoon\'s Wallet',
            'affordable':      'Affordable',
        },
        disable        = {
        },
        gui_tooltip    = '''\
            Controls the randomization of prices for shopsanity items.
            For more control, utilize the plandomizer.

            'Random': The default randomization. Shop prices for
            shopsanity items will range between 0 to 300 rupees,
            with a bias towards values slightly below the middle of the
            range, in multiples of 5.

            'X Wallet': Shop prices for shopsanity items will range
            between 0 and the specified wallet's maximum capacity,
            in multiples of 5.

            'Affordable': Shop prices for shopsanity items will be
            fixed to 10 rupees.
        ''',
        disabled_default =  'random',
        shared         = True,
        gui_params     = {
            "hide_when_disabled": True,
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
        name           = 'shuffle_child_trade',
        gui_text       = 'Shuffle Child Trade Item',
        default        = 'vanilla',
        choices        = {
            'vanilla':          'Vanilla Locations',
            'shuffle':          'Shuffle Weird Egg',
            'skip_child_zelda': 'Skip Child Zelda',
            },
        gui_tooltip    = '''\
            This changes the beginning of the child trade quest.
            
            'Vanilla Locations': Weird Egg is found from Malon outside
            of Hyrule Castle and the child trade quest continues normally.
            
            'Shuffle Weird Egg': The Weird Egg is shuffled into the item pool
            and Malon gives a randomized item. This will require finding the
            Weird Egg to talk to Zelda in Hyrule Castle, which in turn locks
            rewards from Impa, Saria, Malon, and Talon, as well as the Happy
            Mask sidequest.
            
            'Skip Child Zelda': Start having already met Zelda and obtained
            Zelda's Letter along with the item from Impa.
            Supersedes "Skip Child Stealth" since the whole sequence is skipped.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution':  [
                ('vanilla', 1),
                ('shuffle', 1),
                ('skip_child_zelda', 1),
            ],
        },
        shared         = True,
    ),
    Combobox(
        name           = 'shuffle_freestanding_items',
        gui_text       = 'Shuffle Rupees & Hearts',
        default        = 'off',
        choices        = {
            'off':       'Off',
            'all':       'All',
            'overworld': 'Overworld Only',
            'dungeons':  'Dungeons Only',
        },
        gui_tooltip    = '''\
            Shuffles freestanding rupees and recovery hearts, also shuffles:
                Shadow Temple Spinning Pot Drop
                All Goron Pot faces

            Off: No freestanding rupees/recovery hearts are shuffled.
            All: All Visible freestanding rupees/recovery hearts are shuffled.
            Overworld Only: Freestanding rupees/recovery hearts in the overworld are shuffled.
            Dungeons Only: Freestanding rupees/recovery hearts in dungeons are shuffled.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
        shared         = True,
    ),
    Combobox(
        name           = 'shuffle_pots',
        gui_text       = 'Shuffle Pots',
        default        = 'off',
        choices        = {
            'off':       'Off',
            'all':       'All',
            'overworld': 'Overworld Only',
            'dungeons':  'Dungeons Only',
        },
        gui_tooltip    = '''\
            Shuffles pots, flying pots into the location pool.

            Off: Not shuffled.
            All: All pots/flying pots are shuffled.
            Overworld Only: Only overworld pots/flying pots are shuffled.
            Dungeons Only: Only dungeon pots/flying pots are shuffled.

            Note: Only pots which normally drop an item are shuffled.
            Empty pots are not shuffled. Pots containing fairies are not shuffled.

            When this setting is enabled, the pots in Ganon's Tower will be
            accessible without Ganon's Boss Key. Proceeding up the tower out
            of the room with the pots will require Ganon's Boss Key.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
        shared         = True,
    ),
    Combobox(
        name           = 'shuffle_crates',
        gui_text       = 'Shuffle Crates',
        default        = 'off',
        choices        = {
            'off':       'Off',
            'all':       'All',
            'overworld': 'Overworld Only',
            'dungeons':  'Dungeons Only',
        },
        gui_tooltip    = '''\
            Shuffles large and small crates into the location pool.

            Off: Not shuffled.
            All: crates are shuffled.
            Overworld Only: Only overworld crates are shuffled.
            Dungeons Only: Only dungeon crates are shuffled.

            Note: Only crates which normally drop an item are shuffled. Empty crates are not included.
        ''',
        gui_params     = {
            'randomize_key': 'randomize_settings',
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
        name           = 'shuffle_beehives',
        gui_text       = 'Shuffle Beehives',
        gui_tooltip    = '''\
            Enabling this will let beehives drop items. Beehives will shake if they contain anything important.
            There are 32 Beehives located in:
                Generic Grottos (x2 per grotto)
                2 Scrub Grottos (x1 per grotto)
                3 Scrub Grottos (x1 per grotto)
                DMT Cow Grotto (x1)
                Zora's Domain (x3 child only)
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
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
    Checkbutton(
        name           = 'shuffle_frog_song_rupees',
        gui_text       = 'Shuffle Frog Song Rupees',
        gui_tooltip    = '''\
            Enabling this adds 5 Purple Rupees to the item pool 
            and shuffles the rewards from playing Zelda's Lullaby,
            Epona's Song, Saria's Song, Sun's Song, and Song of Time
            to the frogs in Zora's River.
        ''',
        default        = False,
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),

    # Detailed Logic (except "Guarantee Reachable Locations")

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
    
    # Starting Inventory
    
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
    Checkbutton(
        name           = 'start_with_consumables',
        gui_text       = 'Start with Consumables',
        gui_tooltip    = '''\
            Start the game with maxed out Deku Sticks and Deku Nuts.
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
    
    # Other
    
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
        name           = 'complete_mask_quest',
        gui_text       = 'Complete Mask Quest',
        gui_tooltip    = '''\
            Once the Happy Mask Shop is opened,
            all masks will be available to be borrowed.
        ''',
        shared         = True,
    ),
    Checkbutton(
        name           = 'useful_cutscenes',
        gui_text       = 'Enable Specific Glitch-Useful Cutscenes',
        gui_tooltip    = '''\
            The cutscenes of the Poes in Forest Temple and Darunia in
            Fire Temple will not be skipped. These cutscenes are useful
            in glitched gameplay only and do not provide any timesave
            for glitchless playthroughs.
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
        name           = 'plant_beans',
        gui_text       = 'Plant Magic Beans',
        gui_tooltip    = '''\
            Enabling this plants all 10 magic beans in soft soil
            causing the bean plants to be available as adult. You
            can still get beans normally.
        ''',
        default        = False,
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
        name           = 'easier_fire_arrow_entry',
        gui_text       = 'Easier Fire Arrow Entry',
        gui_tooltip    = '''\
            It is possible to open the Shadow Temple entrance
            by lighting the torches with Fire Arrows, but
            can be difficult to light all 24 torches in time.
            Enabling this setting allows you to reduce the
            number of torches that need to be lit to open
            the entrance, making it easier to perform
            Fire Arrow Entry.

            Note that this setting does not affect logic.
            Whether it's used or not, the trick "Shadow Temple
            Entry with Fire Arrows" must be enabled for it to be
            in logic.
        ''',
        disable        = {
            False : {'settings' : ['fae_torch_count']}
        },
        shared         = True,
    ),
    Scale(
        name           = 'fae_torch_count',
        gui_text       = 'Fire Arrow Entry Torch Count',
        default        = 3,
        min            = 1,
        max            = 23,
        gui_tooltip    = '''\
            The entrance to Shadow Temple will open
            after the chosen number of torches are lit.
        ''',
        shared         = True,
        gui_params     = {
            "hide_when_disabled": True,
        }
    ),



    Combobox(
        name           = 'ocarina_songs',
        gui_text       = 'Randomize Ocarina Song Notes',
        default        = 'off',
        choices        = {
            'off': 'Off',
            'frog': 'Frog Songs Only',
            'warp': 'Warp Songs Only',
            'all':  'All Songs',
        },
        gui_tooltip    = '''\
            Will need to memorize a new set of songs.
            Can be silly, but difficult. All songs are
            generally sensible, but warp songs are
            typically more difficult than frog songs.
            ''',
        shared         = True,
    ),
    Combobox(
        name           = 'correct_chest_appearances',
        gui_text       = 'Chest Appearance Matches Contents',
        default        = 'off',
        choices        = {
            'off': 'Off',
            'textures': 'Texture',
            'both':  'Both Size and Texture',
            'classic': 'Classic'
        },
        gui_tooltip    = '''\
            
			
            If "Texture" is enabled, chest texture will reflect its contents
            regardless of size.  Fancy chests will contain keys,
            Gilded chests will contain major items, shuffled
            tokens will be in Webbed chests, and Wooden chests
            will contain the rest.
            This allows skipping chests if they are wooden. 
            However, skipping wooden chests will mean having 
            low health, ammo, and rupees, so doing so is a risk.
            
            "Size and Texture" will change chests with major
            items and boss keys into big chests, and everything
            else into small chests.
            
            "Classic" is the behavior of CSMC in previous versions of the randomizer.
            This will change chests with major items and boss keys into big chests.
            Boss keys will remain in their fancy chest, while small key will be in a
            smaller version of the fancy chest.
        ''',
        shared         = True,
        disable        = {
            'off' : {'settings' : ['minor_items_as_major_chest']},
        },
    ),
    Checkbutton(
        name           = 'minor_items_as_major_chest',
        gui_text       = 'Minor Items in Big/Gold chests',
        gui_tooltip    = '''\
            Chests with Hylian Shield, Deku Shield
            or Bombchus (regardless of the Bombchus
            In Logic setting), will appear in
            Big and/or Gold chests, depending on the 
            Chest Appearance Matches Contents setting.
        ''',
        shared         = True,
        disabled_default = False,
        gui_params       = {
            "hide_when_disabled" : True
        },
    ),
    Checkbutton(
        name           = 'invisible_chests',
        gui_text       = 'Invisible Chests',
        gui_tooltip    = '''\
            Chests will be only be visible with
            the Lens of Truth. Lens is not logically
            required for normally visible chests.
        ''',
        shared         = True,
    ),    
    Combobox(
        name           = 'correct_potcrate_appearances',
        gui_text       = 'Pot & Crate Appearance Matches Contents',
        default        = 'off',
        choices        = {
            'off':                'Off',
            'textures_content':   'Texture (Match Content)',
            'textures_unchecked': 'Texture (Unchecked)',
        },
        gui_tooltip    = '''\
            If enabled, pot/crate textures will reflect its contents.

            Off - Pot and crates will appear as vanilla

            Texture (Match Content) - Pot and crate textures will reflect the contents.
            Golden Pots/crates will contain major items.
            Pots/crates with keys on them will contain small keys.
            Pots/crates containing boss keys will use a variation of the boss key crate texture.
            Pots/crates with a spider web on them contain Gold Skulltula tokens.
            All other items will use the original texture.
            The texture will revert to the original texture once the item is collected.

            Texture (Unchecked) - All pots/crates containing shuffled items
            will appear with a golden texture. The texture will revert to the
            original texture once the item is collected.
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
    Setting_Info(
        name           = 'item_hints',
        type           =  list,
        gui_type       = None,
        gui_text       = None,
        shared         = True,
        choices        = [name for name, item in ItemInfo.items.items() if item.type == 'Item']
    ),
    Setting_Info('hint_dist_user',    dict, None, None, True, {}),
    Combobox(
        name            = 'misc_hints',
        multiple_select = True,
        gui_text        = 'Misc. Hints',
        choices         = {
            'altar':       'Temple of Time Altar',
            'dampe_diary': "Dampé's Diary (Hookshot)",
            'ganondorf':   'Ganondorf (Light Arrows)',
            'warp_songs':  'Warp Songs',
            '10_skulltulas':  'House of Skulltula: 10',
            '20_skulltulas':  'House of Skulltula: 20',
            '30_skulltulas':  'House of Skulltula: 30',
            '40_skulltulas':  'House of Skulltula: 40',
            '50_skulltulas':  'House of Skulltula: 50',
        },
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

            Reading the diary of Dampé the gravekeeper
            as adult will tell you the location of one
            of the Hookshots.

            Talking to Ganondorf in his boss room will
            tell you the location of the Light Arrows.
            If this option is enabled and Ganondorf
            is reachable without Light Arrows, Gossip
            Stones will never hint the Light Arrows.

            Playing a warp song will tell you where
            it leads. (If warp song destinations
            are vanilla, this is always enabled.)

            Talking to a cursed House of Skulltula 
            resident will tell you the reward they will 
            give you for removing their curse.
        ''',
        shared         = True,
        default        = ['altar', 'ganondorf', 'warp_songs'],
    ),
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
        name           = 'deadly_bonks',
        gui_text       = 'Bonks Do Damage',
        default        = 'none',
        choices        = {
            'none':      'No Damage',
            'half':      'Quarter Heart',
            'normal':    'Half Heart',
            'double':    'Whole Heart',
            'quadruple': 'Two Hearts',
            'ohko':      'One Bonk KO',
        },
        gui_tooltip    = '''\
            When rolling, hitting a wall or object
            will hurt Link. Damage is unaffected
            by the damage multiplier setting.
        ''',
        shared         = True,
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
    Checkbutton(
        name           = 'blue_fire_arrows',
        gui_text       = 'Blue Fire Arrows',
        gui_tooltip    = '''\
            Ice arrows gain the power of blue fire.
            They can be used to melt red ice
            and break the mud walls in Dodongo's Cavern.
        ''',
        default        = False,
        shared         = True,
    ),
    Checkbutton(
        name           = 'fix_broken_drops',
        gui_text       = 'Fix Broken Drops',
        gui_tooltip    = '''\
            Enabling this fixes drops that are broken in the vanilla game.

            There is a deku shield drop from a pot in the Spirit Temple child
            side Anubis room that does not appear in the vanilla game, and
            logic might require you to get a deku shield this way. There is a
            magic jar on top of the Gerudo Training Ground eye statue that does
            not always refill your magic in the vanilla game.
        ''',
        shared         = True,
    ),



    Combobox(
        name           = 'item_pool_value',
        gui_text       = 'Item Pool',
        default        = 'balanced',
        choices        = {
            'ludicrous': 'Ludicrous',
            'plentiful': 'Plentiful',
            'balanced':  'Balanced',
            'scarce':    'Scarce',
            'minimal':   'Minimal'
        },
        gui_tooltip    = '''\
            'Ludicrous': Every item in the game is a major
            item. Incompatible with one major item per dungeon.

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
        disable        = {
            'ludicrous':  {'settings': ['one_item_per_dungeon']}
        }
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
        name           = 'adult_trade_start',
        multiple_select= True,
        gui_text       = 'Adult Trade Sequence Items',
        default        = ['Pocket Egg', 'Pocket Cucco', 'Cojiro', 'Odd Mushroom', 'Poachers Saw',
                          'Broken Sword', 'Prescription', 'Eyeball Frog', 'Eyedrops', 'Claim Check'],
        choices        = {
            'Pocket Egg':   'Pocket Egg',
            'Pocket Cucco': 'Pocket Cucco',
            'Cojiro':       'Cojiro',
            'Odd Mushroom': 'Odd Mushroom',
            #'Odd Potion':   'Odd Potion',
            'Poachers Saw': "Poacher's Saw",
            'Broken Sword': 'Broken Sword',
            'Prescription': 'Prescription',
            'Eyeball Frog': 'Eyeball Frog',
            'Eyedrops':     'Eyedrops',
            'Claim Check':  'Claim Check',
        },
        gui_tooltip    = '''\
            Select the items that can appear to start the adult trade sequence.
            If none are selected, it will function as if all are selected.
        ''',
        shared         = True,
    ),

    # Cosmetics

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
        name           = 'dpad_dungeon_menu',
        gui_text       = 'Display D-Pad Dungeon Info',
        shared         = False,
        cosmetic       = True,
        gui_tooltip    = '''\
            Shows separated menus on the pause screen for dungeon
            keys, rewards, and Vanilla/MQ info. If disabled, these
            menus are still available by holding the A button and
            one of the D-Pad directions on the pause screen.
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
    Combobox(
        name           = 'model_adult',
        gui_text       = 'Adult Link Model',
        shared         = False,
        cosmetic       = True,
        choices        = get_model_choices(0),
        gui_tooltip    = '''\
            Link's model will be replaced by the model selected. 
            To add more model options, save the .zobj file to 
            data/Models/Adult.
            Cosmetics options might not be applied when a 
            custom model is in use.
            Caution: Any changes to Link's skeleton have the potential 
            to affect gameplay in significant ways and so are disallowed 
            for all recorded Racetime races. A note will appear at the top 
            of the pause screen if this is the case.
        ''',
        default        = 'Default',
        gui_params     = {
            "hide_when_disabled": True,
        }
    ),
    Setting_Info('model_adult_filepicker', str, "Adult Link Model", "Fileinput", False, {},
        gui_params = {
            "file_types": [
                {
                  "name": "Z64 Model Files",
                  "extensions": [ "zobj" ]
                },
                {
                  "name": "All Files",
                  "extensions": [ "*" ]
                }
            ],
            "hide_when_disabled": True,
    }),
    Combobox(
        name           = 'model_child',
        gui_text       = 'Child Link Model',
        shared         = False,
        cosmetic       = True,
        choices        = get_model_choices(1),
        gui_tooltip    = '''\
            Link's model will be replaced by the model selected. 
            To add more model options, save the .zobj file to 
            data/Models/Child.
            Cosmetics options might not be applied when a 
            custom model is in use.           
            Caution: Any changes to Link's skeleton have the potential 
            to affect gameplay in significant ways and so are disallowed 
            for all recorded Racetime races. A note will appear at the top 
            of the pause screen if this is the case.
        ''',
        default        = 'Default',
        gui_params     = {
            "hide_when_disabled": True,
        }
    ),
    Setting_Info('model_child_filepicker', str, "Child Link Model", "Fileinput", False, {},
        gui_params = {
            "file_types": [
                {
                  "name": "Z64 Model Files",
                  "extensions": [ "zobj" ]
                },
                {
                  "name": "All Files",
                  "extensions": [ "*" ]
                }
            ],
            "hide_when_disabled": True,
    }),
    Setting_Info(
        name           = 'model_unavailable_msg',
        type           = str,
        gui_text       = "Models can only be customized when patching.",
        gui_type       = "Textbox",
        shared         = False,
        gui_params     = {
            "hide_when_disabled": True
        },
        choices        = {},
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

# SFX

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
    Checkbutton(
        name           = 'disable_battle_music',
        gui_text       = 'Disable Battle Music',
        shared         = False,
        cosmetic       = True,
        gui_tooltip    = '''\
            Disable standard battle music.
	        This prevents background music from being
	        interrupted by the battle theme when being
	        near enemies.
        ''',
        default        = False,
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
        name           = 'sfx_link_adult',
        gui_text       = 'Adult Voice',
        shared         = False,
        cosmetic       = True,
        choices        = {
            'default':       'Default',
            'feminine':      'Feminine',
            'silent':        'Silent',
            'random-choice': 'Random Choice',
        },
        default        = 'default',
        gui_tooltip    = '''\
            Change Link's adult voice.
        ''',
        gui_params     = {
            "hide_when_disabled": True,
        }
    ),
    Combobox(
        name           = 'sfx_link_child',
        gui_text       = 'Child Voice',
        shared         = False,
        cosmetic       = True,
        choices        = {
            'default':       'Default',
            'feminine':      'Feminine',
            'silent':        'Silent',
            'random-choice': 'Random Choice',
        },
        default        = 'default',
        gui_tooltip    = '''\
            Change Link's child voice.
        ''',
        gui_params     = {
            "hide_when_disabled": True,
        }
    ),
    Setting_Info(
        name           = 'sfx_link_unavailable_msg',
        type           = str,
        gui_text       = "Link's Voice can only be customized when patching.",
        gui_type       = "Textbox",
        shared         = False,
        gui_params     = {
            "hide_when_disabled": True
        },
        choices        = {},
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
        source = ItemInfo.items.keys()
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
    # Ensure name and source are type string to prevent errors
    close_match = difflib.get_close_matches(str(name), map(str, source), 1)
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
            if setting != 'starting_items' or type(choice) != dict: # allow dict (plando syntax) for starting items in addition to the list syntax used by the GUI
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
            raise ValueError('%r is not a valid choice for setting %r. %s' % (choice, setting, build_close_match(choice, 'choice', info.choice_list)))
        # Ensure no conflicting settings are specified
        if info.disable != None:
            for option, disabling in info.disable.items():
                negative = False
                if isinstance(option, str) and option[0] == '!':
                    negative = True
                    option = option[1:]
                if (choice == option) != negative:
                    for other_setting in disabling.get('settings', []):
                        validate_disabled_setting(settings_dict, setting, choice, other_setting)
                    for section in disabling.get('sections', []):
                        for other_setting in get_settings_from_section(section):
                            validate_disabled_setting(settings_dict, setting, choice, other_setting)
                    for tab in disabling.get('tabs', []):
                        for other_setting in get_settings_from_tab(tab):
                            validate_disabled_setting(settings_dict, setting, choice, other_setting)

def validate_disabled_setting(settings_dict, setting, choice, other_setting):
    if other_setting in settings_dict:
        disabled_default = get_setting_info(other_setting).disabled_default
        if settings_dict[other_setting] != disabled_default:
            raise ValueError(f'{other_setting!r} must be set to {disabled_default!r} since {setting!r} is set to {choice!r}')

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
