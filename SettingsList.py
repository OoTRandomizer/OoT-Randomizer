import argparse
import re
import math
import json
from Cosmetics import get_tunic_color_options, get_navi_color_options, get_sword_color_options, get_gauntlet_color_options, get_magic_color_options, get_heart_color_options
from Location import LocationIterator
import Sounds as sfx
from Utils import data_path

# holds the info for a single setting
class Setting_Info():

    def __init__(self, name, type, gui_text, gui_type, shared, choices, default=None, disabled_default=None, disable=None, gui_tooltip=None, gui_params=None):
        self.name = name # name of the setting, used as a key to retrieve the setting's value everywhere
        self.type = type # type of the setting's value, used to properly convert types to setting strings
        self.shared = shared # whether or not the setting is one that should be shared, used in converting settings to a string
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
            return math.ceil(math.log(count, 2))
        return 0


class Checkbutton(Setting_Info):

    def __init__(self, name, gui_text, gui_tooltip=None, disable=None, 
            disabled_default=None, default=False, shared=False, gui_params=None):

        choices = {
            True:  'checked',
            False: 'unchecked',
        }

        super().__init__(name, bool, gui_text, 'Checkbutton', shared, choices, default, disabled_default, disable, gui_tooltip, gui_params)


class Combobox(Setting_Info):

    def __init__(self, name, gui_text, choices, default, gui_tooltip=None, 
            disable=None, disabled_default=None, shared=False, gui_params=None):

        super().__init__(name, str, gui_text, 'Combobox', shared, choices, default, disabled_default, disable, gui_tooltip, gui_params)


class Scale(Setting_Info):

    def __init__(self, name, gui_text, min, max, default, step=1,
            gui_tooltip=None, disable=None, disabled_default=None, 
            shared=False, gui_params=None):

        choices = {
            i: str(i) for i in range(min, max+1, step)
        }
        if gui_params == None:
            gui_params = {}       
        gui_params['min']    = min
        gui_params['max']    = max
        gui_params['step']   = step

        super().__init__(name, int, gui_text, 'Scale', shared, choices, default, disabled_default, disable, gui_tooltip, gui_params)


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
    'Pass Through Visible One-Way Collisions': {
        'name'    : 'logic_visible_collisions',
        'tooltip' : '''\
                    Allows climbing through the platform to reach 
                    Impa's House Back as adult with no items and 
                    going through the Kakariko Village Gate as child
                    when coming from the Mountain Trail side.
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
    'Deku Tree Basement Webs with Bow': {
        'name'    : 'logic_deku_b1_webs_with_bow',
        'tooltip' : '''\
                    All spider web walls in Deku Tree basement can be burnt
                    by adult using just a bow shooting through torches. Applies
                    to the web obstructing the door to the single scrub room,
                    the web obstrcuting the bombable wall in the back room
                    and the circular floor web dropping to Gohma.

                    For the cicular web dropping to Gohma, backflip onto the
                    chest near the torch at the bottom of the vine wall. With a
                    precise position you can shoot throught the torch to the
                    right edge of the circular web.

                    This allows complete adult Deku Tree with no fire source.
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
    'Reach Forest Temple MQ Twisted Hallway Switch with Hookshot': {
        'name'    : 'logic_forest_mq_hallway_switch',
        'tooltip' : '''\
                    There's a very small gap between the glass block
                    and the wall. Through that gap you can hookshot
                    the target on the ceiling.
                    '''},
    'Death Mountain Trail Bombable Chest with Strength': {
        'name'    : 'logic_dmt_bombable',
        'tooltip' : '''\
                    Child Link can blow up the wall using a nearby bomb
                    flower. You must backwalk with the flower and then
                    quickly throw it toward the wall.
                    '''},
    'Water Temple Boss Key Chest with Iron Boots': {
        'name'    : 'logic_water_bk_chest',
        'tooltip' : '''\
                    Stand on the blue switch in the Stinger room with the
                    Iron Boots, wait for the water to rise all the way up,
                    and then swim straight to the exit. You should grab the
                    ledge as you surface. It works best if you don't mash B.
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
    'Jabu Scrub as Adult with Jump Dive': {
        'name'    : 'logic_jabu_scrub_jump_dive',
        'tooltip' : '''\
                    Standing above the underwater tunnel leading to the scrub,
                    jump down and swim through the tunnel. This allows adult to
                    access the scrub with no Scale or Iron Boots.
                    '''},
    'Jabu MQ Song of Time Block GS with Boomerang': {
        'name'    : 'logic_jabu_mq_sot_gs',
        'tooltip' : '''\
                    Allow the Boomerang to return to you through
                    the Song of Time block to grab the token.
                    '''},
    'Bottom of the Well Cage GS without Boomerang': {
        'name'    : 'logic_botw_cage_gs',
        'tooltip' : '''\
                    After killing the Skulltula, the Like Like
                    can be used to boost you into the token.
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
                    Allows you to progress without needing either a
                    Small Key or Hover Boots.
                    '''},
    'Fire Temple MQ Flame Wall Maze Skip': {
        'name'    : 'logic_fire_mq_flame_maze',
        'tooltip' : '''\
                    If you move quickly you can sneak past the edge of
                    a flame wall before it can rise up to block you.
                    To do it without taking damage is more precise.
                    Allows you to reach a GS without needing either
                    Song of Time or Hover Boots.
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
    'Fire Temple Boss Door without Hover Boots or Pillar': {
        'name'    : 'logic_fire_boss_door_jump',
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
    'Shadow Trial MQ Torch with Bow': {
        'name'    : 'logic_shadow_trial_mq',
        'tooltip' : '''\
                    You can light the torch in this room without a fire
                    source by shooting an arrow through the lit torch
                    at the beginning of the room. Because the room is
                    so dark and the unlit torch is so far away, it can
                    be difficult to aim the shot correctly.
                    '''},
    'Forest Temple NE Outdoors Ledge with Hover Boots': {
        'name'    : 'logic_forest_outdoors_ledge',
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
        'tooltip' : '''\
                    With precise Hover Boots movement it is possible
                    to reach the boss key chest's region without
                    needing the Longshot. It is not necessary to take
                    damage from the spikes. The Gold Skulltula Token
                    in the following room can also be obtained with
                    just the Hover Boots.
                    '''},
    'Water Temple Falling Platform Room GS with Hookshot': {
        'name'    : 'logic_water_falling_platform_gs',
        'tooltip' : '''\
                    If you stand on the very edge of the platform, this
                    Gold Skulltula can be obtained with only the Hookshot.
                    '''},
    'Death Mountain Trail Upper Red Rock GS without Hammer': {
        'name'    : 'logic_trail_gs_upper',
        'tooltip' : '''\
                    After killing the Skulltula, the token can be collected
                    by backflipping into the rock at the correct angle.
                    '''},
    'Death Mountain Trail Lower Red Rock GS without Hammer': {
        'name'    : 'logic_trail_gs_lower',
        'tooltip' : '''\
                    After killing the Skulltula, the token can be fished
                    out of the rock without needing to destroy it, by
                    using the Hookshot in the correct way.
                    '''},
    'Death Mountain Crater Upper to Lower with Hammer': {
        'name'    : 'logic_crater_upper_to_lower',
        'tooltip' : '''\
                    With the Hammer, you can jumpslash the rock twice
                    in the same jump in order to destroy it before you
                    fall into the lava.
                    '''},
    'Zora\'s Domain Entry with Hover Boots': {
        'name'    : 'logic_zora_with_hovers',
        'tooltip' : '''\
                    Can hover behind the waterfall as adult.
                    '''},
    'Shadow Temple River Statue with Bombchu': {
        'name'    : 'logic_shadow_statue',
        'tooltip' : '''\
                    By sending a Bombchu around the edge of the
                    gorge, you can knock down the statue without
                    needing a Bow.
                    Applies in both vanilla and MQ Shadow.
                    '''},
    'Stop Link the Goron with Din\'s Fire': {
        'name'    : 'logic_link_goron_dins',
        'tooltip' : '''\
                    The timing is quite awkward.
                    '''},
    'Fire Temple Song of Time Room GS without Song of Time': {
        'name'    : 'logic_fire_song_of_time',
        'tooltip' : '''\
                    A precise jump can be used to reach this room.
                    '''},
    'Climb Fire Temple without Strength': {
        'name'    : 'logic_fire_strength',
        'tooltip' : '''\
                    A precise jump can be used to skip
                    pushing the block.
                    '''},
    'Fire Temple MQ Big Lava Room Bombable Chest without Hookshot': {
        'name'    : 'logic_fire_mq_bombable_chest',
        'tooltip' : '''\
                    A precisely-angled jump can get over the wall
                    of fire in this room. It's expected that you
                    will take damage as you do this. As it may
                    take multiple attempts, you won't be expected
                    to use a fairy to survive.
                    '''},
    'Light Trial MQ without Hookshot': {
        'name'    : 'logic_light_trial_mq',
        'tooltip' : '''\
                    If you move quickly you can sneak past the edge of
                    a flame wall before it can rise up to block you.
                    In this case it doesn't seem possible to do it
                    without taking damage.
                    '''},
    'Ice Cavern MQ Scarecrow GS with No Additional Items': {
        'name'    : 'logic_ice_mq_scarecrow',
        'tooltip' : '''\
                    A precise jump can be used to reach this alcove.
                    '''},
    'Reverse Wasteland': {
        'name'    : 'logic_reverse_wasteland',
        'tooltip' : '''\
                    By memorizing the path, you can travel through the
                    Wasteland in reverse.
                    Note that jumping to the carpet merchant as child
                    requires a fairly precise jumpslash.
                    To enable the equivalent trick for going forward
                    through the Wasteland, set the Lens of Truth logic
                    to "Only Chest Minigame."
                    To cross the river of sand with no additional items,
                    be sure to also enable "Wasteland Crossing without
                    Hover Boots or Longshot."
                    Unless all overworld entrances are randomized, child
                    Link will not be expected to do anything at Gerudo's
                    Fortress.
                    '''},
    'Zora\'s River Upper Freestanding PoH as Adult with Nothing': {
        'name'    : 'logic_zora_river_upper',
        'tooltip' : '''\
                    Adult can reach this PoH with a precise jump,
                    no Hover Boots required.
                    '''},
    'Shadow Temple MQ Truth Spinner Gap with Longshot': {
        'name'    : 'logic_shadow_mq_gap',
        'tooltip' : '''\
                    You can Longshot a torch and jumpslash-recoil onto
                    the tongue. It works best if you Longshot the right
                    torch from the left side of the room.
                    '''},
    'Lost Woods Adult GS without Bean': {
        'name'    : 'logic_lost_woods_gs_bean',
        'tooltip' : '''\
                    You can collect the token with a precise
                    Hookshot use, as long as you can kill the
                    Skulltula somehow first. It can be killed
                    using Longshot, Bow, Bombchus or Din's Fire.
                    '''},
    'Graveyard Freestanding PoH with Boomerang': {
        'name'    : 'logic_graveyard_poh',
        'tooltip' : '''\
                    Using a precise moving setup you can obtain
                    the Piece of Heart by having the Boomerang
                    interact with it along the return path.
                    '''},
    'Death Mountain Trail Soil GS without Destroying Boulder': {
        'name'    : 'logic_dmt_soil_gs',
        'tooltip' : '''\
                    Bugs will go into the soft soil even while the boulder is
                    still blocking the entrance.
                    Then, using a precise moving setup you can kill the Gold
                    Skulltula and obtain the token by having the Boomerang
                    interact with it along the return path.
                    '''},
    'Gerudo Training Grounds Left Side Silver Rupees without Hookshot': {
        'name'    : 'logic_gtg_without_hookshot',
        'tooltip' : '''\
                    After collecting the rest of the silver rupees in the room,
                    you can reach the final silver rupee on the ceiling by being
                    pulled up into it after getting grabbed by the Wallmaster.
                    Then, you must also reach the exit of the room without the
                    use of the Hookshot. If you move quickly you can sneak past
                    the edge of a flame wall before it can rise up to block you.
                    To do so without taking damage is more precise.
                    '''},
    'Gerudo Training Grounds MQ Left Side Silver Rupees without Hookshot': {
        'name'    : 'logic_gtg_mq_without_hookshot',
        'tooltip' : '''\
                    After collecting the rest of the silver rupees in the room,
                    you can reach the final silver rupee on the ceiling by being
                    pulled up into it after getting grabbed by the Wallmaster.
                    The Wallmaster will not track you to directly underneath the
                    rupee. You should take the last step to be under the rupee
                    after the Wallmaster has begun its attempt to grab you.
                    Also included with this trick is that fact that the switch
                    that unbars the door to the final chest of GTG can be hit
                    without a projectile, using a precise jumpslash.
                    This trick supersedes "Gerudo Training Grounds MQ Left Side
                    Silver Rupees with Hookshot".
                    '''},
    'Reach Gerudo Training Grounds Fake Wall Ledge with Hover Boots': {
        'name'    : 'logic_gtg_fake_wall',
        'tooltip' : '''\
                    A precise Hover Boots use from the top of the chest can allow
                    you to grab the ledge without needing the usual requirements.
                    In Master Quest, this always skips a Song of Time requirement.
                    In Vanilla, this skips a Hookshot requirement, but is only
                    relevant if "Gerudo Training Grounds Left Side Silver Rupees
                    without Hookshot" is enabled.
                    '''},
    'Water Temple Boss Key Jump Dive': {
        'name'    : 'logic_water_bk_jump_dive',
        'tooltip' : '''\
                    Stand on the very edge of raised corridor leading from the
                    push block room to the rolling boulder corridor. Face the
                    gold skulltula on the waterfall and jump over the boulder
                    corridor floor into the pool of water, swimming right once
                    underwater. This allows access to the boss key room without
                    Iron boots. 
                    '''},
    'Water Temple Cracked Wall with No Additional Items': {
        'name'    : 'logic_water_cracked_wall_nothing',
        'tooltip' : '''\
                    A precise jumpslash (among other methods) will
                    get you to the cracked wall without needing the
                    Hover Boots or to raise the water to the middle
                    level. This trick supersedes "Water Temple
                    Cracked Wall with Hover Boots".
                    '''},
    'Water Temple North Basement Ledge with Precise Jump': {
        'name'    : 'logic_water_north_basement_ledge_jump',
        'tooltip' : '''\
                    In the northern basement there's a ledge from where, in
                    vanilla Water Temple, boulders roll out into the room.
                    Normally to jump directly to this ledge logically
                    requires the Hover Boots, but with precise jump, it can
                    be done without them. This trick supersedes "Water Temple
                    Boss Key Chest with Iron Boots" and applies to both
                    Vanilla and Master Quest.
                    '''},
    'Water Temple Torch Longshot': {
        'name'    : 'logic_water_temple_torch_longshot',
        'tooltip' : '''\
                    Stand on the eastern side of the central pillar and longshot
                    the torches on the bottom level. Swim through the corridor
                    and float up to the top level. This allows access to this
                    area and lower water levels without Iron Boots.
                    '''},
    'Goron City Leftmost Maze Chest with Hover Boots': {
        'name'    : 'logic_goron_city_leftmost',
        'tooltip' : '''\
                    A precise backwalk starting from on top of the
                    crate and ending with a precisely-timed backflip
                    can reach this chest without needing either
                    the Hammer or Silver Gauntlets.
                    '''},
    'Deku Tree Basement without Slingshot': {
        'name'    : 'logic_deku_b1_skip',
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
        'tooltip' : '''\
                    A bomb can be used to hit the switch on the ceiling,
                    but it must be thrown from a particular distance
                    away and with precise timing.
                    '''},
    'Forest Temple Outside Backdoor without Hover Boots': {
        'name'    : 'logic_forest_outside_backdoor',
        'tooltip' : '''\
                    With a precise jumpslash from above, you
                    can reach the backdoor to the west
                    countyard without Hover Boots.
                    '''},
    'Forest Temple Scarecrow Route': {
        'name'    : 'logic_forest_scarecrow',
        'tooltip' : '''\
                    From on top of the door frame in the NE
                    courtyard, you can summon Pierre. You
                    can get there with a precise Hover Boots
                    movement. You will take fall damage.
                    This allows you to reach the falling
                    ceiling room early.
                    '''},
    'Dodongo\'s Cavern MQ Early Bomb Bag Area as Child': {
        'name'    : 'logic_dc_mq_child_bombs',
        'tooltip' : '''\
                    With a precise jumpslash from above, you
                    can reach the Bomb Bag area as only child
                    without needing a Slingshot. You will
                    take fall damage.
                    '''},
    'Dodongo\'s Cavern Child Slingshot Skips': {
        'name'    : 'logic_dc_slingshot_skip',
        'tooltip' : '''\
                    With precise platforming, child can cross the
                    platforms while the flame circles are there.
                    When enabling this trick, it's recommended that
                    you also enable the Adult variant: "Dodongo's
                    Cavern Spike Trap Room Jump without Hover Boots."
                    '''},
    'Goron City Spinning Pot PoH with Bombchu': {
        'name'    : 'logic_goron_city_pot',
        'tooltip' : '''\
                    A Bombchu can be used to stop the spinning
                    pot, but it can be quite finicky to get it
                    to work.
                    '''},
    'Spirit Trial without Hookshot': {
        'name'    : 'logic_spirit_trial_hookshot',
        'tooltip' : '''\
                    A precise jump off of an Armos can
                    collect the highest rupee.
                    '''},
    'Shadow Temple Stone Umbrella Skip': {
        'name'    : 'logic_shadow_umbrella',
        'tooltip' : '''\
                    A very precise Hover Boots movement
                    from off of the lower chest can get you
                    on top of the crushing spikes without
                    needing to pull the block. Applies to
                    both Vanilla and Master Quest.
                    '''},
    'Water Temple Central Bow Target without Longshot or Hover Boots': {
        'name'    : 'logic_water_central_bow',
        'tooltip' : '''\
                    A very precise Bow shot can hit the eye
                    switch from the floor above. Then, you
                    can jump down into the hallway and make
                    through it before the gate closes.
                    '''},
    'Fire Temple East Tower without Scarecrow\'s Song': {
        'name'    : 'logic_fire_scarecrow',
        'tooltip' : '''\
                    Also known as "Pixelshot."
                    The Longshot can reach the target on the elevator
                    itself, allowing you to skip needing to spawn the
                    scarecrow.
                    '''},
    'Shadow Temple Entry with Fire Arrows': {
        'name'    : 'logic_shadow_fire_arrow_entry',
        'tooltip' : '''\
                    It is possible to light all of the torches to
                    open the Shadow Temple entrance with just Fire
                    Arrows, but you must be very quick, precise,
                    and strategic with how you take your shots.
                    '''},
    'Second Dampe Race as Child': {
        'name'    : 'logic_child_dampe_race_poh',
        'tooltip' : '''\
                    It is possible to complete the second dampe
                    race as child in under a minute, but it is
                    a strict time limit.
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
        default     = "OOTE",
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

    # Non-GUI Settings
    Checkbutton('cosmetics_only', None),
    Checkbutton('check_version', None),
    Setting_Info('distribution_file', str, "Distribution File", "Fileinput", False, {},
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
            ]        
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
    Setting_Info('patch_file',        str, None, None, False, {}),
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
    Setting_Info('open_output_dir',   str, "Open Output Directory", "Outputdirbutton", False, {}),   
    Setting_Info('repatch_cosmetics', bool, None, None, False, {},
        default        = True
    ),
    Checkbutton(
        name           = 'create_spoiler',
        gui_text       = 'Create Spoiler Log',
        gui_tooltip    = '''\
                         Enabling this will change the seed.
                         ''',
        default        = True,
        gui_params     = {
            'no_line_break' : True,
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
            'None'  : {'settings' : ['player_num', 'create_cosmetics_log']},
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
                         Randomizes most Main Rules.
                         ''',
        default        = False,
        disable        = {
            True : {
                'sections' : ['open_section', 'world_section', 'shuffle_section', 'shuffle_dungeon_section'],
            }
        },
        shared         = True,
    ),
    Combobox(
        name           = 'open_forest',
        gui_text       = 'Forest',
        default        = 'open',
        choices        = {
            'open':        'Open Forest',
            'closed_deku': 'Closed Deku',
            'closed':      'Closed Forest',
            },
        gui_tooltip    = '''\
            Open Forest: Mido no longer blocks the path to the
            Deku Tree, and the Kokiri boy no longer blocks the path
            out of the forest.
            
            Closed Deku: The Kokiri boy no longer blocks the path
            out of the forest, but Mido still blocks the path to the
            Deku Tree, requiring Kokiri Sword and Deku Shield to access
            the Deku Tree.

            Closed Forest: The Kokiri Sword and Slingshot are always
            available somewhere in the forest. This is incompatible with
            Start as Adult and shuffling "All Indoors" and/or "Overworld"
            entrances will force this to Closed Deku if selected.
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
    Checkbutton(
        name           = 'open_fountain',
        gui_text       = 'Open Zora\'s Fountain',
        gui_tooltip    = '''\
            King Zora starts out as moved. This also removes
            Ruto's Letter from the item pool.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
    ),
    Combobox(
        name           = 'gerudo_fortress',
        gui_text       = 'Gerudo Fortress',
        default        = 'normal',
        choices        = {
            'normal': 'Default Behavior',
            'fast':   'Rescue One Carpenter',
            'open':   'Open Gerudo Fortress',
        },
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
        gui_text       = 'Rainbow Bridge Requirement',
        default        = 'medallions',
        choices        = {
            'open':       'Always Open',
            'vanilla':    'Vanilla Requirements',
            'stones':	  'All Spiritual Stones',
            'medallions': 'All Medallions',
            'dungeons':   'All Dungeons',
            'tokens':     '100 Gold Skulltula Tokens'
        },
        gui_tooltip    = '''\
            'Always Open': Rainbow Bridge is always present.
            'Vanilla Requirements': Spirit/Shadow Medallions and Light Arrows.
            'All Spiritual Stones': All 3 Spiritual Stones.
            'All Medallions': All 6 Medallions.
            'All Dungeons': All Medallions and Spiritual Stones.
            '100 Gold Skulltula Tokens': All 100 Gold Skulltula Tokens.
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
        gui_text       = 'Logic Rules',
        default        = 'glitchless',
        choices        = {
            'glitchless': 'Glitchless',
            'glitched':   'Glitched',
            'none':       'No Logic',
            },
        gui_tooltip    = '''\
            Sets the rules the logic uses
            to determine accessibility.

            'Glitchless': No glitches are
            required, but may require some
            minor tricks.

            'Glitched': Movement oriented
            glitches are likely required.
            No locations excluded.

            'No Logic': All locations are
            considered available. May not
            be beatable.
            ''',
        disable        = {
            'glitched'  : {'settings' : ['entrance_shuffle', 'mq_dungeons_random', 'mq_dungeons']},
            'none'      : {'tabs'     : ['detailed_tab']},
        },
        shared         = True,
    ),
    Checkbutton(
        name           = 'all_reachable',
        gui_text       = 'All Locations Reachable',
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
        gui_tooltip    = '''\
                         Sets a random number of trials to
                         enter Ganon's Tower.
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
        gui_params     = {
            'randomize_key': 'randomize_settings',
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
        name           = 'start_with_fast_travel',
        gui_text       = 'Start with Fast Travel',
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
        gui_tooltip    = '''\
            Start the game with 99 rupees. Wallet upgrades fill wallet.
        ''',
        shared         = True,
    ),
    Checkbutton(
        name           = 'start_with_wallet',
        gui_text       = 'Start with Tycoon\'s Wallet',
        gui_tooltip    = '''\
            Start the game with the largest wallet (999 max).
        ''',
        shared         = True,
    ),
    Checkbutton(
        name           = 'start_with_deku_equipment',
        gui_text       = 'Start with Deku Equipment',
        gui_tooltip    = '''\
            Start the game with 10 Deku sticks and 20 Deku nuts.
            Additionally, start the game with a Deku shield equipped,
            unless playing with the Shopsanity setting.
        ''',
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
        name           = 'skull_reward_multiplier_random',
        gui_text       = 'Random Skull Reward Multiplier',
        gui_tooltip    = '''\
            A random skull reward multiplier will be chosed.
            Talking to the central cursed man in the skull house
            will reveal how many you need.
        ''',
        disable        = {
            True : {'settings' : ['skull_reward_multiplier']}
        },
        shared         = True,
    ),
    Scale(
        name           = 'skull_reward_multiplier',
        gui_text       = "Skull Reward Multiplier",
        default        = 10,
        min            = 1,
        max            = 20,
        gui_tooltip    = '''\
            Changes the amount of skulls required to get an item.
            For example, setting this to 5 gives you items at
            5, 10, 15, 20, and 25 skulls instead of the usual 10, 20, 30...
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
        default        = True,
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
        default        = True,
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
        name           = 'shuffle_song_items',
        gui_text       = 'Shuffle Songs with Items',
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
        gui_tooltip    = '''\
            Enabling this causes playing Epona's song infront
            of cows to give an item. There are 9 cows, and an
            extra in MQ Jabu.
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
    Combobox(
        name           = 'entrance_shuffle',
        gui_text       = 'Entrance Shuffle',
        default        = 'off',
        choices        = {
            'off':              'Off',
            'dungeons':         'Dungeons Only',
            'simple-indoors':   'Simple Indoors',
            'all-indoors':      'All Indoors',
            'all':              'All Indoors & Overworld',
        },
        gui_tooltip    = '''\
            Shuffle entrances bidirectionally within different pools.

            'Dungeons Only':
            Shuffle dungeon entrances with each other, including Bottom 
            of the Well, Ice Cavern, and Gerudo Training Grounds. 
            However, Ganon's Castle is not shuffled.
            Additionally, the entrances of Deku Tree, Fire Temple and 
            Bottom of the Well are opened for both adult and child.

            'Simple Indoors':
            Shuffle dungeon entrances along with simple Grotto and
            Interior entrances (i.e. most Houses and Great Fairies).

            'All Indoors':
            Extended version of 'Simple Indoors' with some extra entrances:
            Adult Potion Shop, Windmill, Link's House, Temple of Time and
            Dampe's Grave.
 
            'All Indoors & Overworld':
            Same as 'All Indoors' but with Overworld loading zones shuffled
            in a new separate pool. Owl drop positions are also randomized.

            Note: If Interior or Overworld entrances are shuffled, trade timers 
            are disabled and trade items don't revert when loading a save.
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution':  [
                ('off', 4),
                ('dungeons', 1),
                ('simple-indoors', 1),
                ('all-indoors', 1),
                ('all', 1),
            ],
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
            '0':      'Shuffled Shops (0 Items)',
            '1':      'Shuffled Shops (1 Items)',
            '2':      'Shuffled Shops (2 Items)',
            '3':      'Shuffled Shops (3 Items)',
            '4':      'Shuffled Shops (4 Items)',
            'random': 'Shuffled Shops (Random)',
        },
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
        gui_text       = 'Tokensanity',
        default        = 'off',
        choices        = {
            'off':      'Off',
            'dungeons': 'Dungeons Only',
            'all':      'All Tokens',
            },
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
        gui_text       = 'Maps & Compasses',
        default        = 'dungeon',
        choices        = {
            'remove':    'Remove',
            'startwith': 'Start With',
            'vanilla':   'Vanilla Locations',
            'dungeon':   'Dungeon Only',
            'keysanity': 'Anywhere'
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
        gui_text       = 'Small Keys',
        default        = 'dungeon',
        choices        = {
            'remove':    'Remove (Keysy)',
            'vanilla':   'Vanilla Locations',            
            'dungeon':   'Dungeon Only',
            'keysanity': 'Anywhere (Keysanity)'
        },
        gui_tooltip    = '''\
            'Remove': Small Keys are removed. All locked
            doors in dungeons will be unlocked. An easier
            mode.

            'Vanilla': Small Keys will appear in their 
            vanilla locations. You start with 3 keys in 
            Spirit Temple MQ because the vanilla key 
            layout is not beatable in logic.

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
        gui_text       = 'Boss Keys',
        default        = 'dungeon',
        choices        = {
            'remove':    'Remove (Keysy)',
            'vanilla':   'Vanilla Locations',            
            'dungeon':   'Dungeon Only',
            'keysanity': 'Anywhere (Keysanity)',
        },
        gui_tooltip    = '''\
            'Remove': Boss Keys are removed. All locked
            doors in dungeons will be unlocked. An easier
            mode.

            'Vanilla': Boss Keys will appear in their 
            vanilla locations.

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
    Combobox(
        name           = 'shuffle_ganon_bosskey',
        gui_text       = 'Ganon\'s Boss Key',
        default        = 'dungeon',
        choices        = {
            'remove':          "Remove",
            'dungeon':         "Dungeon Only",
            'vanilla':         "Vanilla",
            'keysanity':       "Anywhere",
            'lacs_vanilla':    "On LACS: Vanilla",
            'lacs_medallions': "On LACS: Medallions",
            'lacs_stones':     "On LACS: Stones",
            'lacs_dungeons':   "On LACS: Dungeons",
        },
        gui_tooltip    = '''\
            'Remove': Ganon's Castle Boss Key is removed
            and the boss door in Ganon's Tower starts unlocked.

            'Dungeon': Ganon's Castle Boss Key can only appear
            inside Ganon's Castle.

            'Vanilla': Ganon's Castle Boss Key will appear in 
            the vanilla location.

            'Anywhere': Ganon's Castle Boss Key can appear
            anywhere in the world.
            
            'On LACS': These settings put the boss key on the
            Light Arrow Cutscene location, from Zelda in Temple
            of Time as adult, with differing requirements.
            
            'On LACS: Vanilla': Shadow and Spirit Medallions.
            'On LACS: Medallions': All 6 Medallions.
            'On LACS: Stones': All 3 Spiritual Stones.
            'On LACS: Dungeons': All Spiritual Stones & Medallions.
            
        ''',
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution': [
                ('remove',          4),
                ('dungeon',         2),
                ('vanilla',         2),
                ('keysanity',       4),
                ('lacs_vanilla',    1),
                ('lacs_medallions', 1),
                ('lacs_stones',     1),
                ('lacs_dungeons',   1),
            ],            
        },
    ),
    Checkbutton(
        name           = 'enhance_map_compass',
        gui_text       = 'Maps and Compasses Give Information',
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
        gui_params     = {
            'randomize_key': 'randomize_settings',
            'distribution': [
                (True, 1),
            ],
        }
    ),
    Scale(
        name           = 'mq_dungeons',
        gui_text       = "Random MQ Dungeon Count",
        default        = 0,
        min            = 0,
        max            = 12,
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
        shared         = True,
        gui_params     = {
            'randomize_key': 'randomize_settings',
        },
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
            Prevent locations from being required. Major
            items can still appear there, however they
            will never be required to beat the game.

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
        }
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
    Combobox(
        name           = 'logic_lens',
        gui_text       = 'Lens of Truth',
        default        = 'all',
        choices        = {
            'all':             'Required Everywhere',
            'chest-wasteland': 'Wasteland and Chest Minigame',
            'chest':           'Only Chest Minigame',
        },
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
    ),
    Combobox(
        name           = 'hints',
        gui_text       = 'Gossip Stones',
        default        = 'agony',
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
        choices        = {
            'useless':     'Useless',
            'balanced':    'Balanced',
            'strong':      'Strong',
            'very_strong': 'Very Strong',
            'tournament':  'Tournament',
        },
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
        gui_text       = 'Text Shuffle',
        default        = 'none',
        choices        = {
            'none':         'No Text Shuffled',
            'except_hints': 'Shuffled except Hints and Keys',
            'complete':     'All Text Shuffled',
        },
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
        gui_text       = 'Item Pool',
        default        = 'balanced',
        choices        = {
            'plentiful': 'Plentiful',
            'balanced':  'Balanced',
            'scarce':    'Scarce',
            'minimal':   'Minimal'
        },
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
            'default':       'Default',
            'random':        'Random Choice',
            'sunrise':       'Sunrise',
            'morning':       'Morning',
            'noon':          'Noon',
            'afternoon':     'Afternoon',
            'sunset':        'Sunset',
            'evening':       'Evening',
            'midnight':      'Midnight',
            'witching-hour': 'Witching Hour',
        },
        gui_tooltip    = '''\
            Change up Link's sleep routine.

            Daytime officially starts at 6:30,
            nighttime at 18:00 (6:00 PM).

            Default is 10:00 in the morning.
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
        default        = 'hold',
        choices        = {
            'hold':   'Hold',
            'switch': 'Switch',
        },
    ),
    Combobox(
        name           = 'background_music',
        gui_text       = 'Background Music',
        default        = 'normal',
        choices        = {
            'normal': 'Normal',
            'off':    'No Music',
            'random': 'Random',
        },
        gui_tooltip    = '''\
            'No Music': No background music.
            is played.

            'Random': Area background music is
            randomized. Additional music can
            be loaded from data/Music/
        ''',
    ),
    Combobox(
        name           = 'fanfares',
        gui_text       = 'Fanfares',
        default        = 'normal',
        choices        = {
            'normal': 'Normal',
            'off':    'No Fanfares',
            'random': 'Random',
        },
        disable        = {
            'normal' : {'settings' : ['ocarina_fanfares']},
        },
        gui_tooltip    = '''\
            'No Fanfares': No fanfares 
            (short non-looping tracks)
            are played.

            'Random': Fanfares are randomized.
            Additional fanfares can be loaded
            from data/Music/
        ''',
    ),
    Checkbutton(
        name           = 'ocarina_fanfares',
        gui_text       = 'Ocarina Songs as Fanfares',
        gui_tooltip    = '''\
            Include the songs that play when an ocarina song
            is played as part of the fanfare pool when
            shuffling or disabling fanfares. Note that these
            are a bit longer than most fanfares.
        ''',
        gui_params  = {
            "hide_when_disabled": True,
        },
        default        = False,
    ),
    Checkbutton(
        name           = 'display_dpad',
        gui_text       = 'Display D-Pad HUD',
        gui_tooltip    = '''\
            Shows an additional HUD element displaying
            current available options on the D-Pad.
        ''',
        default        = True,
    ),

    Setting_Info(
        name           = 'kokiri_color',
        type           = str,
        gui_text       = "Kokiri Tunic",
        gui_type       = "Combobox",
        shared         = False,
        choices        = get_tunic_color_options(),
        default        = 'Kokiri Green',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        '''
    ),
    Setting_Info(
        name           = 'goron_color',
        type           = str,
        gui_text       = "Goron Tunic",
        gui_type       = "Combobox",
        shared         = False,
        choices        = get_tunic_color_options(),
        default        = 'Goron Red',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        '''
    ),
    Setting_Info(
        name           = 'zora_color',
        type           = str,
        gui_text       = "Zora Tunic",
        gui_type       = "Combobox",
        shared         = False,
        choices        = get_tunic_color_options(),
        default        = 'Zora Blue',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        '''
    ),
    Setting_Info(
        name           = 'navi_color_default_inner',
        type           = str,
        gui_text       = "Navi Idle Inner",
        gui_type       = "Combobox",
        gui_params     = {
            'no_line_break' : True,
        },
        shared         = False,
        choices        = get_navi_color_options(),
        default        = 'White',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        '''
    ),
        Setting_Info(
        name           = 'navi_color_default_outer',
        type           = str,
        gui_text       = "Outer",
        gui_type       = "Combobox",
        shared         = False,
        choices        = get_navi_color_options(True),
        default        = '[Same as Inner]',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        '''
    ),
    Setting_Info(
        name           = 'navi_color_enemy_inner',
        type           = str,
        gui_text       = 'Navi Targeting Enemy Inner',
        gui_type       = "Combobox",
        gui_params     = {
            'no_line_break' : True,
        },
        shared         = False,
        choices        = get_navi_color_options(),
        default        = 'Yellow',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        '''
    ),
    Setting_Info(
        name           = 'navi_color_enemy_outer',
        type           = str,
        gui_text       = 'Outer',
        gui_type       = "Combobox",
        shared         = False,
        choices        = get_navi_color_options(True),
        default        = '[Same as Inner]',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        '''
    ),
    Setting_Info(
        name           = 'navi_color_npc_inner',
        type           = str,
        gui_text       = 'Navi Targeting NPC Inner',
        gui_type       = "Combobox",
        gui_params     = {
            'no_line_break' : True,
        },
        shared         = False,
        choices        = get_navi_color_options(),
        default        = 'Light Blue',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        '''
    ),
    Setting_Info(
        name           = 'navi_color_npc_outer',
        type           = str,
        gui_text       = 'Outer',
        gui_type       = "Combobox",
        shared         = False,
        choices        = get_navi_color_options(True),
        default        = '[Same as Inner]',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        '''
    ),
    Setting_Info(
        name           = 'navi_color_prop_inner',
        type           = str,
        gui_text       = 'Navi Targeting Prop Inner',
        gui_type       = "Combobox",
        shared         = False,
        gui_params     = {
            'no_line_break' : True,
        },
        choices        = get_navi_color_options(),
        default        = 'Green',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        '''
    ),
    Setting_Info(
        name           = 'navi_color_prop_outer',
        type           = str,
        gui_text       = 'Outer',
        gui_type       = "Combobox",
        shared         = False,
        choices        = get_navi_color_options(True),
        default        = '[Same as Inner]',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        '''
    ),
    Combobox(
        name           = 'sword_trail_duration',
        gui_text       = 'Sword Trail Duration',
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
    ),
    Setting_Info(
        name           = 'sword_trail_color_inner',
        type           = str,
        gui_text       = 'Inner Color',
        gui_type       = "Combobox",
        shared         = False,
        choices        = get_sword_color_options(),
        default        = 'White',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Rainbow sword trails.
        '''
    ),
    Setting_Info(
        name           = 'sword_trail_color_outer',
        type           = str,
        gui_text       = 'Outer Color',
        gui_type       = "Combobox",
        shared         = False,
        choices        = get_sword_color_options(),
        default        = 'White',
        gui_tooltip    = '''\
                  'Random Choice': Choose a random
                  color from this list of colors.
                  'Completely Random': Choose a random
                  color from any color the N64 can draw.
                  'Rainbow': Rainbow sword trails.
        '''
    ),
    Setting_Info(
        name           = 'silver_gauntlets_color',
        type           = str,
        gui_text       = 'Silver Gauntlets Color',
        gui_type       = "Combobox",
        shared         = False,
        choices        = get_gauntlet_color_options(),
        default        = 'Silver',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Rainbow sword trails.
        '''
    ),
    Setting_Info(
        name           = 'golden_gauntlets_color',
        type           = str,
        gui_text       = 'Golden Gauntlets Color',
        gui_type       = "Combobox",
        shared         = False,
        choices        = get_gauntlet_color_options(),
        default        = 'Gold',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
            'Rainbow': Rainbow sword trails.
        '''
    ),
    Setting_Info(
        name           = 'heart_color',
        type           = str,
        gui_text       = 'Heart Color',
        gui_type       = "Combobox",
        shared         = False,
        choices        = get_heart_color_options(),
        default        = 'Red',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        '''
    ),
    Setting_Info(
        name           = 'magic_color',
        type           = str,
        gui_text       = 'Magic Color',
        gui_type       = "Combobox",
        shared         = False,
        choices        = get_magic_color_options(),
        default        = 'Green',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            color from this list of colors.
            'Completely Random': Choose a random
            color from any color the N64 can draw.
        '''
    ),
    Combobox(
        name           = 'sfx_low_hp',
        gui_text       = 'Low HP',
        choices        = sfx.get_setting_choices(sfx.SoundHooks.HP_LOW),
        default        = 'default',
        gui_tooltip    = '''\
            'Random Choice': Choose a random
            sound from this list.
            'Default': Beep. Beep. Beep.
        ''',
    ),
    Combobox(
        name           = 'sfx_navi_overworld',
        gui_text       = 'Navi Overworld',
        choices        = sfx.get_setting_choices(sfx.SoundHooks.NAVI_OVERWORLD),
        default        = 'default',
    ),
    Combobox(
        name           = 'sfx_navi_enemy',
        gui_text       = 'Navi Enemy',
        choices        = sfx.get_setting_choices(sfx.SoundHooks.NAVI_ENEMY),
        default        = 'default',
    ),
    Combobox(
        name           = 'sfx_menu_cursor',
        gui_text       = 'Menu Cursor',
        choices        = sfx.get_setting_choices(sfx.SoundHooks.MENU_CURSOR),
        default        = 'default',
    ),
    Combobox(
        name           = 'sfx_menu_select',
        gui_text       = 'Menu Select',
        choices        = sfx.get_setting_choices(sfx.SoundHooks.MENU_SELECT),
        default        = 'default',
    ),
    Combobox(
        name           = 'sfx_horse_neigh',
        gui_text       = 'Horse',
        choices        = sfx.get_setting_choices(sfx.SoundHooks.HORSE_NEIGH),
        default        = 'default',
    ),
    Combobox(
        name           = 'sfx_nightfall',
        gui_text       = 'Nightfall',
        choices        = sfx.get_setting_choices(sfx.SoundHooks.NIGHTFALL),
        default        = 'default',
    ),
    Combobox(
        name           = 'sfx_hover_boots',
        gui_text       = 'Hover Boots',
        choices        = sfx.get_setting_choices(sfx.SoundHooks.BOOTS_HOVER),
        default        = 'default',
    ),
    Combobox(
        name           = 'sfx_ocarina',
        gui_text       = 'Ocarina',
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
    ),
]


si_dict = {si.name: si for si in setting_infos}
def get_setting_info(name):
    return si_dict[name]


def create_dependency(setting, disabling_setting, option):
    disabled_info = get_setting_info(setting)
    if disabled_info.dependency is None:
        disabled_info.dependency = lambda settings: getattr(settings, disabling_setting.name) == option
    else:
        old_dependency = disabled_info.dependency
        disabled_info.dependency = lambda settings: getattr(settings, disabling_setting.name) == option or old_dependency(settings)


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


class UnmappedSettingError(Exception):
    pass


with open(data_path('settings_mapping.json')) as f:
    setting_map = json.load(f)

for info in setting_infos:
    if info.gui_text is not None and not is_mapped(info.name):
        raise UnmappedSettingError(f'{info.name} is defined but is not in the settings map. Add it to the settings_mapping or set the gui_text to None to suppress.')

    if info.disable != None:
        for option, disabling in info.disable.items():
            for setting in disabling.get('settings', []):
                create_dependency(setting, info, option)
            for section in disabling.get('setions', []):
                for setting in get_settings_from_section(section):
                    create_dependency(setting, info, option)
            for tab in disabling.get('tabs', []):
                for setting in get_settings_from_tab(tab):
                    create_dependency(setting, info, option)
