from __future__ import annotations


# Below is the list of possible glitchless tricks.
# The order they are listed in is also the order in which
# they appear to the user in the GUI, so a sensible order was chosen

logic_tricks: dict[str, dict[str, str | tuple[str, ...]]] = {

    # General tricks

    'Pass Through Visible One-Way Collisions': {
        'name'    : 'logic_visible_collisions',
        'tags'    : ("General", "Entrance Shuffle", "Kakariko Village", "Overworld", "Child", "Adult",),
        'tooltip' : '''\
                    Allows climbing through the platform to reach
                    Impa's House Back as adult with no items and
                    going through the Kakariko Village Gate as child
                    when coming from the Mountain Trail side.

                    This is assumed on for Advanced Logic.
                    '''},
    'Hidden Grottos without Stone of Agony': {
        'name'    : 'logic_grottos_without_agony',
        'tags'    : ("General", "Entrance Shuffle", "Overworld", "Child", "Adult",),
        'tooltip' : '''\
                    Allows entering hidden grottos without the
                    Stone of Agony.
                    '''},
    'Fewer Tunic Requirements': {
        'name'    : 'logic_fewer_tunic_requirements',
        'tags'    : ("General", "Fire Temple", "Fire Temple MQ", "Water Temple", "Water Temple MQ", "Gerudo Training Ground", "Gerudo Training Ground MQ",
                    "Ganon's Castle", "Ganon's Castle MQ", "Zora's Fountain", "Death Mountain Crater", "Master Quest", "Overworld", "Vanilla Dungeons",
                    "Child", "Adult",),
        'tooltip' : '''\
                    Allows the following possible without Tunics:
                    - Enter Fire Temple as adult.
                    - Zora's Fountain bottom Freestandings. You
                    might not have enough time to resurface, and
                    you may need to make multiple trips.
                    - Traverse the first floor of the Fire Temple,
                    except the elevator room and Volvagia.
                    - Go underwater in the Water Temple. (The area
                    below the central pillar always requires Zora
                    Tunic.)
                    - Gerudo Training Ground Underwater Silver
                    Rupees. You may need to make multiple trips.
                    - Collecting some Silver Rupees in the Fire
                    Trial. You may need to make multiple trips.
                    - All instances also apply in Master Quest.
                    '''},
    'Beehives with Bombchus' : {
        'name'    : 'logic_beehives_bombchus',
        'tags'    : ("General", "Beehives", "Overworld", "Zora's Fountain", "Child", "Adult",),
        'tooltip' : '''\
                    Puts breaking beehives with bombchus into logic.
                    Using bombs is already expected on beehives that
                    that are low enough that a bomb throw will reach.
                    '''},
    'Boulder Freestandings with Boomerang' : {
        'name'    : 'logic_boomerang_boulders',
        'tags'    : ("General", "Freestandings", "Lost Woods", "Death Mountain Trail", "Ice Cavern", "Ganon's Castle MQ", "Vanilla Dungeons", "Master Quest", "Overworld", "Entrance Shuffle", "Child",),
        'tooltip' : '''\
                    Obtain freestandings inside boulders or red ice
                    without having to remove the boulder first.
                    Applies to:
                    - LW Under Boulder Blue Rupee
                    - DMT Rock Blue Rupee
                    - DMT Rock Red Rupee
                    - Ice Cavern Frozen Blue Rupee
                    - Ganons Castle MQ Water Trial Recovery Heart
                    '''},
    'Hammer Rusted Switches and Boulders Through Walls': {
        'name'    : 'logic_rusted_switches',
        'tags'    : ("General", "Fire Temple", "Fire Temple MQ", "Spirit Temple MQ", "Ganon's Castle MQ", "Master Quest", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    Applies to:
                    - Fire Temple Highest Goron Rusted Switch
                    - Water Trial block puzzle room
                    - MQ Fire Temple Lizalfos Maze Rusted Switch
                    - MQ Spirit Child Crawlspace Boulder
                    - MQ Spirit Trial Rusted Switch
                    '''},

    # Overworld tricks

    'Adult Kokiri Forest GS with Hover Boots': {
        'name'    : 'logic_adult_kokiri_gs_hovers',
        'tags'    : ("Kokiri Forest", "Gold Skulltulas", "Overworld", "Adult",),
        'tooltip' : '''\
                    The Skulltula can be obtained without Hookshot
                    by using the Hover Boots off of one of the roots.

                    This trick is assumed on for Advanced Logic.
                    '''},
    'Adult Kokiri Forest GS with Nothing': {
        'name'    : 'logic_adult_kokiri_gs_nothing',
        'tags'    : ("Kokiri Forest", "Gold Skulltulas", "Overworld", "Adult",),
        'tooltip' : '''\
                    The Skulltula can be obtained without Hookshot by
                    using a precise jump off of one of the roots.
                    '''},
    'Jump onto the Lost Woods Bridge as Adult with Nothing': {
        'name'    : 'logic_lost_woods_bridge',
        'tags'    : ("Lost Woods", "Entrance Shuffle", "Overworld", "Adult",),
        'tooltip' : '''\
                    With very precise movement it's possible for
                    adult to jump onto the bridge without needing
                    Longshot, Hover Boots, or Bean.
                    '''},
    'Backflip over Mido as Adult': {
        'name'    : 'logic_mido_backflip',
        'tags'    : ("Lost Woods", "Overworld", "Adult",),
        'tooltip' : '''\
                    With a specific position and angle, you can
                    backflip over Mido.
                    '''},
    'Lost Woods Adult GS without Bean': {
        'name'    : 'logic_lost_woods_gs_bean',
        'tags'    : ("Lost Woods", "Gold Skulltulas", "Overworld", "Adult",),
        'tooltip' : '''\
                    You can collect the token with a precise
                    Hookshot use, as long as you can kill the
                    Skulltula somehow first. It can be killed
                    using Longshot, Bow, Bombchus or Din's Fire.
                    '''},
    'Hyrule Castle Storms Grotto GS with Just Boomerang': {
        'name'    : 'logic_castle_storms_gs',
        'tags'    : ("Hyrule Castle", "Gold Skulltulas", "Overworld", "Child",),
        'tooltip' : '''\
                    With precise throws, the Boomerang alone can
                    kill the Skulltula and collect the token,
                    without first needing to blow up the wall.
                    '''},
    'Man on Roof without Hookshot': {
        'name'    : 'logic_man_on_roof',
        'tags'    : ("Kakariko Village", "Overworld", "Child", "Adult",),
        'tooltip' : '''\
                    He can be reached by side-hopping off
                    the watchtower as either age, or by
                    jumping onto the potion shop's roof
                    from the ledge as adult.

                    This is assumed true for Advanced Logic.
                    '''},
    'Kakariko Tower GS with Jump Slash': {
        'name'    : 'logic_kakariko_tower_gs',
        'tags'    : ("Kakariko Village", "Gold Skulltulas", "Overworld", "Child",),
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
        'tags'    : ("Kakariko Village", "Overworld", "Adult",),
        'tooltip' : '''\
                    You can jump up to the spinning platform from
                    below as adult.
                    '''},
    'Kakariko Rooftop GS with Hover Boots': {
        'name'    : 'logic_kakariko_rooftop_gs',
        'tags'    : ("Kakariko Village", "Gold Skulltulas", "Overworld", "Adult",),
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
        'tags'    : ("Graveyard", "Overworld", "Child",),
        'tooltip' : '''\
                    Using a precise moving setup you can obtain
                    the Piece of Heart by having the Boomerang
                    interact with it along the return path.
                    '''},
    'Second Dampe Race as Child': {
        'name'    : 'logic_child_dampe_race_poh',
        'tags'    : ("Graveyard", "Entrance Shuffle", "Overworld", "Child",),
        'tooltip' : '''\
                    It is possible to complete the second dampe
                    race as child in under a minute, but it is
                    a strict time limit.
                    '''},
    'Shadow Temple Entry with Fire Arrows': {
        'name'    : 'logic_shadow_fire_arrow_entry',
        'tags'    : ("Graveyard", "Overworld", "Adult",),
        'tooltip' : '''\
                    It is possible to light all of the torches to
                    open the Shadow Temple entrance with just Fire
                    Arrows, but you must be very quick, precise,
                    and strategic with how you take your shots.
                    '''},
    'Death Mountain Trail Soil GS without Destroying Boulder': {
        'name'    : 'logic_dmt_soil_gs',
        'tags'    : ("Death Mountain Trail", "Gold Skulltulas", "Overworld", "Child",),
        'tooltip' : '''\
                    Bugs will go into the soft soil even while the boulder is
                    still blocking the entrance.
                    Then, using a precise moving setup you can kill the Gold
                    Skulltula and obtain the token by having the Boomerang
                    interact with it along the return path.
                    '''},
    'Death Mountain Trail Chest with Strength': {
        'name'    : 'logic_dmt_bombable',
        'tags'    : ("Death Mountain Trail", "Overworld", "Child",),
        'tooltip' : '''\
                    Child Link can blow up the wall using a nearby bomb
                    flower. You must backwalk with the flower and then
                    quickly throw it toward the wall.
                    '''},
    'Death Mountain Trail Lower Red Rock GS with Jump Slash': {
        'name'    : 'logic_trail_gs_lower',
        'tags'    : ("Death Mountain Trail", "Gold Skulltulas", "Overworld", "Adult",),
        'tooltip' : '''\
                    After killing the Skulltula, the token can be fished
                    out of the rock without needing to destroy it, by
                    jumpslashing into it from a precise position.
                    '''},
    'Death Mountain Trail Climb with Hover Boots': {
        'name'    : 'logic_dmt_climb_hovers',
        'tags'    : ("Death Mountain Trail", "Overworld", "Adult",),
        'tooltip' : '''\
                    It is possible to use the Hover Boots to bypass
                    needing to destroy the boulders blocking the path
                    to the top of Death Mountain.
                    '''},
    'Death Mountain Trail Upper Red Rock GS without Hammer': {
        'name'    : 'logic_trail_gs_upper',
        'tags'    : ("Death Mountain Trail", "Gold Skulltulas", "Overworld", "Adult",),
        'tooltip' : '''\
                    After killing the Skulltula, the token can be collected
                    by backflipping into the rock at the correct angle.
                    '''},
    'Deliver Eye Drops with Bolero of Fire': {
        'name'    : 'logic_biggoron_bolero',
        'tags'    : ("Death Mountain Trail", "Overworld", "Adult",),
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
        'tags'    : ("Goron City", "Overworld", "Child",),
        'tooltip' : '''\
                    A Bombchu can be used to stop the spinning
                    pot, but it can be quite finicky to get it
                    to work.
                    '''},
    'Goron City Spinning Pot PoH with Strength': {
        'name'    : 'logic_goron_city_pot_with_strength',
        'tags'    : ("Goron City", "Overworld", "Child",),
        'tooltip' : '''\
                    Allows for stopping the Goron City Spinning
                    Pot using a bomb flower alone, requiring
                    strength in lieu of inventory explosives.
                    '''},
    'Rolling Goron (Hot Rodder Goron) as Child with Strength': {
        'name'    : 'logic_child_rolling_with_strength',
        'tags'    : ("Goron City", "Overworld", "Child",),
        'tooltip' : '''\
                    Use the bomb flower on the stairs or near Medigoron.
                    Timing is tight, especially without backwalking.
                    '''},
    'Stop Link the Goron with Din\'s Fire': {
        'name'    : 'logic_link_goron_dins',
        'tags'    : ("Goron City", "Overworld", "Adult",),
        'tooltip' : '''\
                    The timing is quite awkward.
                    '''},
    'Goron City Maze Left Chest with Hover Boots': {
        'name'    : 'logic_goron_city_leftmost',
        'tags'    : ("Goron City", "Overworld", "Adult",),
        'tooltip' : '''\
                    A precise backwalk starting from on top of the
                    crate and ending with a precisely-timed backflip
                    can reach this chest without needing either
                    the Hammer or Silver Gauntlets.
                    '''},
    'Goron City Grotto with Hookshot While Taking Damage': {
        'name'    : 'logic_goron_grotto',
        'tags'    : ("Goron City", "Overworld", "Adult",),
        'tooltip' : '''\
                    It is possible to reach the Goron City Grotto by
                    quickly using the Hookshot while in the midst of
                    taking damage from the lava floor. This trick will
                    not be expected on OHKO or quadruple damage.
                    '''},
    'Crater\'s Bean PoH with Hover Boots': {
        'name'    : 'logic_crater_bean_poh_with_hovers',
        'tags'    : ("Death Mountain Crater", "Overworld", "Adult",),
        'tooltip' : '''\
                    Hover from the base of the bridge
                    near Goron City and walk up the
                    very steep slope.
                    '''},
    'Death Mountain Crater Jump to Bolero': {
        'name'    : 'logic_crater_bolero_jump',
        'tags'    : ("Death Mountain Crater", "Overworld", "Adult",),
        'tooltip' : '''\
                    As Adult, using a shield to drop a pot while you have
                    the perfect speed and position, the pot can
                    push you that little extra distance you
                    need to jump across the gap in the bridge.
                    '''},
    'Death Mountain Crater Upper to Lower with Hammer': {
        'name'    : 'logic_crater_boulder_jumpslash',
        'tags'    : ("Death Mountain Crater", "Overworld", "Adult",),
        'tooltip' : '''\
                    With the Hammer, you can jump slash the rock twice
                    in the same jump in order to destroy it before you
                    fall into the lava.
                    '''},
    'Death Mountain Crater Upper to Lower Boulder Skip': {
        'name'    : 'logic_crater_boulder_skip',
        'tags'    : ("Death Mountain Crater", "Overworld", "Adult",),
        'tooltip' : '''\
                    As adult, with careful positioning, you can jump to the ledge
                    where the boulder is, then use repeated ledge grabs
                    to shimmy to a climbable ledge. This trick supersedes
                    "Death Mountain Crater Upper to Lower with Hammer".
                    '''},
    'Zora\'s River Lower Freestanding PoH as Adult with Nothing': {
        'name'    : 'logic_zora_river_lower',
        'tags'    : ("Zora's River", "Overworld", "Adult",),
        'tooltip' : '''\
                    Adult can reach this PoH with a precise jump,
                    no Hover Boots or Bean required.
                    '''},
    'Zora\'s River Upper Freestanding PoH as Adult with Nothing': {
        'name'    : 'logic_zora_river_upper',
        'tags'    : ("Zora's River", "Overworld", "Adult",),
        'tooltip' : '''\
                    Adult can reach this PoH with a precise jump,
                    no Hover Boots required.
                    '''},
    'Zora\'s Domain Entry with Cucco': {
        'name'    : 'logic_zora_with_cucco',
        'tags'    : ("Zora's River", "Overworld", "Child",),
        'tooltip' : '''\
                    You can fly behind the waterfall with
                    a Cucco as child.
                    '''},
    'Zora\'s Domain Entry with Hover Boots': {
        'name'    : 'logic_zora_with_hovers',
        'tags'    : ("Zora's River", "Overworld", "Adult",),
        'tooltip' : '''\
                    You can hover behind the waterfall as adult.
                    '''},
    'Zora\'s River Rupees with Jump Dive': {
        'name'    : 'logic_zora_river_rupees',
        'tags'    : ("Zora's River", "Freestandings", "Overworld", "Adult",),
        'tooltip' : '''\
                    You can jump down onto them from
                    above to skip needing Iron Boots.
                    '''},
    'Skip King Zora as Adult with Nothing': {
        'name'    : 'logic_king_zora_skip',
        'tags'    : ("Zora's Domain", "Overworld", "Adult",),
        'tooltip' : '''\
                    With a precise jump as adult, it is possible to
                    get on the fence next to King Zora from the front
                    to access Zora's Fountain.
                    '''},
    'Zora\'s Domain GS with No Additional Items': {
        'name'    : 'logic_domain_gs',
        'tags'    : ("Zora's Domain", "Gold Skulltulas", "Overworld", "Adult",),
        'tooltip' : '''\
                    A precise jump slash can kill the Skulltula and
                    recoil back onto the top of the frozen waterfall.
                    To kill it, the logic normally guarantees one of
                    Hookshot, Bow, or Magic.
                    '''},
    'Lake Hylia Lab Wall GS with Jump Slash': {
        'name'    : 'logic_lab_wall_gs',
        'tags'    : ("Lake Hylia", "Gold Skulltulas", "Overworld", "Child",),
        'tooltip' : '''\
                    The jump slash to actually collect the
                    token is somewhat precise.
                    '''},
    'Lake Hylia Lab Dive without Gold Scale': {
        'name'    : 'logic_lab_diving',
        'tags'    : ("Lake Hylia", "Overworld", "Adult",),
        'tooltip' : '''\
                    Remove the Iron Boots in the midst of
                    Hookshotting the underwater crate.
                    '''},
    'Water Temple Entry without Iron Boots using Hookshot': {
        'name'    : 'logic_water_hookshot_entry',
        'tags'    : ("Lake Hylia", "Overworld", "Adult",),
        'tooltip' : '''\
                    When entering Water Temple using Gold Scale instead
                    of Iron Boots, the Longshot is usually used to be
                    able to hit the switch and open the gate. But, by
                    standing in a particular spot, the switch can be hit
                    with only the reach of the Hookshot.
                    '''},
    'Gerudo Valley Crate PoH as Adult with Hover Boots': {
        'name'    : 'logic_valley_crate_hovers',
        'tags'    : ("Gerudo Valley", "Overworld", "Adult",),
        'tooltip' : '''\
                    From the far side of Gerudo Valley, a precise
                    Hover Boots movement and jump-slash recoil can
                    allow adult to reach the ledge with the crate
                    PoH without needing Longshot. You will take
                    fall damage.
                    '''},
    'Thieves\' Hideout "Kitchen" with No Additional Items': {
        'name'    : 'logic_gerudo_kitchen',
        'tags'    : ("Thieves' Hideout", "Gerudo's Fortress", "Overworld", "Child", "Adult",),
        'tooltip' : '''\
                    Allows passing through the kitchen by avoiding being
                    seen by the guards. The logic normally guarantees
                    Bow or Hookshot to stun them from a distance, or
                    Hover Boots to cross the room without needing to
                    deal with the guards.
                    '''},
    'Gerudo\'s Fortress Ledge Jumps': {
        'name'    : 'logic_gf_jump',
        'tags'    : ("Gerudo's Fortress", "Overworld", "Child", "Adult",),
        'tooltip' : '''\
                    Allows both ages to use a jump to reach the second
                    floor of the fortress from the southern roof with
                    the guard, and adult to jump to the top roof from
                    there, without going through the interiors of the
                    Thieves' Hideout.

                    In Advanced Logic this is enabled by default.
                    '''},
    'Gerudo\'s Fortress Break Room Entrance with Precise Jump': {
        'name'    : 'logic_gf_break_room_jump',
        'tags'    : ("Gerudo's Fortress", "Overworld", "Adult", "Entrance Shuffle", "Pots", "Crates",),
        'tooltip' : '''\
                    With a precise jump from the ledge below the
                    Gold Skullula, Adult can access the break room
                    entrance with no additional items. This trick
                    is only relevant if Thieves' Hideout entrances,
                    overworld pots, or overworld crates are shuffled.
                    '''},
    'Wasteland Crossing without Hover Boots or Longshot': {
        'name'    : 'logic_wasteland_crossing',
        'tags'    : ("Haunted Wasteland", "Overworld", "Child", "Adult",),
        'tooltip' : '''\
                    You can beat the quicksand by backwalking across it
                    in a specific way.
                    Note that jumping to the carpet merchant as child
                    typically requires a fairly precise jump slash.
                    '''},
    'Lensless Wasteland': {
        'name'    : 'logic_lens_wasteland',
        'tags'    : ("Lens of Truth", "Haunted Wasteland", "Overworld", "Child", "Adult",),
        'tooltip' : '''\
                    By memorizing the path, you can travel through the
                    Wasteland without using the Lens of Truth to see
                    the Poe.
                    The equivalent trick for going in reverse through
                    the Wasteland is "Reverse Wasteland".
                    '''},
    'Reverse Wasteland': {
        'name'    : 'logic_reverse_wasteland',
        'tags'    : ("Haunted Wasteland", "Overworld", "Child", "Adult",),
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
                    '''},
    'Colossus Hill GS with Hookshot': {
        'name'    : 'logic_colossus_gs',
        'tags'    : ("Desert Colossus", "Gold Skulltulas", "Overworld", "Adult",),
        'tooltip' : '''\
                    Somewhat precise. If you kill enough Leevers
                    you can get enough of a break to take some time
                    to aim more carefully.
                    '''},

    # Dungeon tricks

    'Deku Tree Basement Vines GS with Jump Slash': {
        'name'    : 'logic_deku_basement_gs',
        'tags'    : ("Deku Tree", "Gold Skulltulas", "Vanilla Dungeons", "Child", "Adult",),
        'tooltip' : '''\
                    The Skulltula can be defeated by doing
                    a precise jump slash.
                    '''},
    'Deku Tree Basement without Slingshot': {
        'name'    : 'logic_deku_b1_skip',
        'tags'    : ("Deku Tree", "Deku Tree MQ", "Master Quest", "Vanilla Dungeons", "Child",),
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
        'tags'    : ("Deku Tree", "Entrance Shuffle", "Vanilla Dungeons", "Adult",),
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
    'Deku Tree MQ Lobby Crate GS with Boomerang': {
        'name'    : 'logic_deku_mq_lobby_gs',
        'tags'    : ("Gold Skulltulas", "Deku Tree MQ", "Child",),
        'tooltip' : '''\
                    Throwing the Boomerang such that it hits the Gold
                    Skulltula on its return path, allows you to kill it
                    without having to break the crate or with other items.
                    '''},
    'Deku Tree MQ Compass Room GS Boulders with Just Hammer': {
        'name'    : 'logic_deku_mq_compass_gs',
        'tags'    : ("Deku Tree MQ", "Gold Skulltulas", "Master Quest", "Adult",),
        'tooltip' : '''\
                    Climb to the top of the vines, then let go
                    and jump slash immediately to destroy the
                    boulders using the Hammer, without needing
                    to spawn a Song of Time block.
                    '''},
    'Deku Tree MQ Roll Under the Spiked Log': {
        'name'    : 'logic_deku_mq_log',
        'tags'    : ("Deku Tree MQ", "Master Quest", "Child", "Adult",),
        'tooltip' : '''\
                    You can get past the spiked log by rolling
                    to briefly shrink your hitbox. As adult,
                    the timing is a bit more precise.
                    '''},
    'Dodongo\'s Cavern Scarecrow GS with Armos Statue': {
        'name'    : 'logic_dc_scarecrow_gs',
        'tags'    : ("Dodongo's Cavern", "Gold Skulltulas", "Vanilla Dungeons", "Child", "Adult",),
        'tooltip' : '''\
                    You can jump off an Armos Statue to reach the
                    alcove with the Gold Skulltula. It takes quite
                    a long time to pull the statue the entire way.
                    The jump to the alcove can be a bit picky when
                    done as child.
                    '''},
    'Dodongo\'s Cavern Vines GS from Below with Longshot': {
        'name'    : 'logic_dc_vines_gs',
        'tags'    : ("Dodongo's Cavern", "Gold Skulltulas", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    The vines upon which this Skulltula rests are one-
                    sided collision. You can use the Longshot to get it
                    from below, by shooting it through the vines,
                    bypassing the need to lower the staircase.

                    This is considered on for Advanced Logic.
                    '''},
    'Dodongo\'s Cavern Staircase with Bow': {
        'name'    : 'logic_dc_staircase',
        'tags'    : ("Dodongo's Cavern", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    The Bow can be used to knock down the stairs
                    with two well-timed shots.
                    '''},
    'Dodongo\'s Cavern Child Slingshot Skips': {
        'name'    : 'logic_dc_slingshot_skip',
        'tags'    : ("Dodongo's Cavern", "Vanilla Dungeons", "Child",),
        'tooltip' : '''\
                    With precise platforming, child can cross the
                    platforms while the flame circles are there.
                    When enabling this trick, it's recommended that
                    you also enable the Adult variant: "Dodongo's
                    Cavern Spike Trap Room Jump without Hover Boots".
                    '''},
    'Dodongo\'s Cavern Two Scrub Room with Strength': {
        'name'    : 'logic_dc_scrub_room',
        'tags'    : ("Dodongo's Cavern", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    With help from a conveniently-positioned block,
                    Adult can quickly carry a bomb flower over to
                    destroy the mud wall blocking the room with two
                    Deku Scrubs.
                    '''},
    'Dodongo\'s Cavern Spike Trap Room Jump without Hover Boots': {
        'name'    : 'logic_dc_jump',
        'tags'    : ("Dodongo's Cavern", "Dodongo's Cavern MQ", "Master Quest", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    The jump is adult Link only. Applies to both Vanilla and MQ.

                    This is on by default for Advanced Logic.
                    '''},
    'Dodongo\'s Cavern Bombchu the Eyes from Below': {
        'name'    : 'logic_dc_chu_eyes',
        'tags'    : ("Dodongo's Cavern", "Vanilla Dungeons", "Child", "Adult",),
        'tooltip' : '''\
                    You can use Bombchus to skip needing
                    to go through the dungeon, allowing
                    immediate access to the back areas.
                    '''},
    'Dodongo\'s Cavern Smash the Boss Lobby Floor': {
        'name'    : 'logic_dc_hammer_floor',
        'tags'    : ("Dodongo's Cavern", "Dodongo's Cavern MQ", "Entrance Shuffle", "Master Quest", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    The bombable floor before King Dodongo can be destroyed
                    with Hammer if hit in the very center. This is only
                    relevant with Shuffle Boss Entrances or if Dodongo's Cavern
                    is MQ and either variant of "Dodongo's Cavern MQ Light the
                    Eyes with Strength" is on.
                    '''},
    'Dodongo\'s Cavern MQ Early Bomb Bag Area as Child': {
        'name'    : 'logic_dc_mq_child_bombs',
        'tags'    : ("Dodongo's Cavern MQ", "Master Quest", "Child",),
        'tooltip' : '''\
                    With a precise jump slash from above, you
                    can reach the Bomb Bag area as only child
                    without needing a Slingshot. You will
                    take fall damage.
                    '''},
    'Dodongo\'s Cavern MQ Light the Eyes with Strength as Adult': {
        'name'    : 'logic_dc_mq_eyes_adult',
        'tags'    : ("Dodongo's Cavern MQ", "Master Quest", "Adult",),
        'tooltip' : '''\
                    If you move very quickly, it is possible to use
                    the bomb flower at the top of the room to light
                    the eyes.
                    '''},
    'Dodongo\'s Cavern MQ Light the Eyes with Strength as Child': {
        'name'    : 'logic_dc_mq_eyes_child',
        'tags'    : ("Dodongo's Cavern MQ", "Master Quest", "Child",),
        'tooltip' : '''\
                    If you move very quickly, it is possible to use
                    the bomb flower at the top of the room to light
                    the eyes. To perform this trick as child is
                    significantly more difficult than adult. The
                    player is also expected to complete the DC back
                    area without explosives, including getting past
                    the Armos wall to the switch for the boss door.
                    '''},
    'Jabu Underwater Alcove as Adult with Jump Dive': {
        'name'    : 'logic_jabu_alcove_jump_dive',
        'tags'    : ("Jabu Jabu's Belly", "Jabu Jabu's Belly MQ", "Entrance Shuffle", "Master Quest", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    Standing above the underwater tunnel leading to the scrub,
                    jump down and swim through the tunnel. This allows adult to
                    access the alcove with no Scale or Iron Boots. In vanilla Jabu,
                    this alcove has a business scrub. In MQ Jabu, it has the compass
                    chest and a door switch for the main floor.
                    '''},
    'Jabu Near Boss Room with Hover Boots': {
        'name'    : 'logic_jabu_boss_hover',
        'tags'    : ("Jabu Jabu's Belly", "Gold Skulltulas", "Entrance Shuffle", "Vanilla Dungeons", "Adult",),
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
        'tags'    : ("Jabu Jabu's Belly", "Jabu Jabu's Belly MQ", "Gold Skulltulas", "Entrance Shuffle", "Master Quest", "Vanilla Dungeons", "Child", "Adult", "Shortcuts",),
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
        'tags'    : ("Jabu Jabu's Belly", "Entrance Shuffle", "Vanilla Dungeons", "Child", "Adult",),
        'tooltip' : '''\
                    You can hit the switch that opens the door to the boss
                    room using a precisely-aimed Bombchu. Also, using the
                    Hover Boots, adult can throw a Bomb at the switch. This
                    trick is only relevant if "Shuffle Boss Entrances" is
                    enabled.
                    '''},
    'Jabu MQ without Lens of Truth': {
        'name'    : 'logic_lens_jabu_mq',
        'tags'    : ("Lens of Truth", "Jabu Jabu's Belly MQ", "Master Quest", "Child", "Adult",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Jabu MQ.
                    '''},
    'Jabu MQ Compass Chest with Boomerang': {
        'name'    : 'logic_jabu_mq_rang_jump',
        'tags'    : ("Jabu Jabu's Belly MQ", "Master Quest", "Child", "Shortcuts",),
        'tooltip' : '''\
                    Boomerang can reach the cow switch to spawn the chest by
                    targeting the cow, jumping off of the ledge where the
                    chest spawns, and throwing the Boomerang in mid-air. This
                    is only relevant with Jabu Jabu's Belly dungeon shortcuts
                    enabled.
                    '''},
    'Jabu MQ Song of Time Block GS with Boomerang': {
        'name'    : 'logic_jabu_mq_sot_gs',
        'tags'    : ("Jabu Jabu's Belly MQ", "Gold Skulltulas", "Master Quest", "Child",),
        'tooltip' : '''\
                    Allow the Boomerang to return to you through
                    the Song of Time block to grab the token.
                    '''},
    'Bottom of the Well without Lens of Truth': {
        'name'    : 'logic_lens_botw',
        'tags'    : ("Lens of Truth", "Bottom of the Well", "Vanilla Dungeons", "Child",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Bottom of the Well.
                    '''},
    'Child Dead Hand without Kokiri Sword': {
        'name'    : 'logic_child_deadhand',
        'tags'    : ("Bottom of the Well", "Bottom of the Well MQ", "Vanilla Dungeons", "Master Quest", "Child",),
        'tooltip' : '''\
                    Requires 9 sticks or 5 jump slashes.
                    '''},
    'Bottom of the Well Map Chest with Strength & Sticks': {
        'name'    : 'logic_botw_basement',
        'tags'    : ("Bottom of the Well", "Vanilla Dungeons", "Child",),
        'tooltip' : '''\
                    The chest in the basement can be reached with
                    strength by doing a jump slash with a lit
                    stick to access the bomb flowers.
                    '''},
    'Bottom of the Well MQ Jump Over the Pits': {
        'name'    : 'logic_botw_mq_pits',
        'tags'    : ("Bottom of the Well MQ", "Master Quest", "Child",),
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
        'tags'    : ("Bottom of the Well MQ", "Master Quest", "Child",),
        'tooltip' : '''\
                    Boomerang can fish the item out of the rubble without
                    needing explosives to blow it up.
                    '''},
    'Forest Temple First Room GS with Difficult-to-Use Weapons': {
        'name'    : 'logic_forest_first_gs',
        'tags'    : ("Forest Temple", "Entrance Shuffle", "Gold Skulltulas", "Vanilla Dungeons", "Child", "Adult",),
        'tooltip' : '''\
                    Allows killing this Skulltula with Sword or Sticks by
                    jump slashing it as you let go from the vines. You can
                    avoid taking fall damage by recoiling onto the tree.
                    Also allows killing it as Child with a Bomb throw. It's
                    much more difficult to use a Bomb as child due to
                    Child Link's shorter height.
                    '''},
    'Forest Temple West Courtyard Hearts with Boomerang': {
        'name'    : 'logic_forest_courtyard_hearts',
        'tags'    : ("Forest Temple", "Forest Temple MQ", "Entrance Shuffle", "Vanilla Dungeons", "Master Quest", "Child", "Freestandings",),
        'tooltip' : '''\
                    The recovery hearts in the western courtyard can be
                    obtained from below with a precise Boomerang throw.
                    Only relevant if dungeon Freestandings are shuffled.
                    Applies in both Vanilla and Master Quest.
                    '''},
    'Forest Temple East Courtyard GS with Boomerang': {
        'name'    : 'logic_forest_outdoor_east_gs',
        'tags'    : ("Forest Temple", "Entrance Shuffle", "Gold Skulltulas", "Vanilla Dungeons", "Child",),
        'tooltip' : '''\
                    Precise Boomerang throws can allow child to
                    kill the Skulltula and collect the token.
                    '''},
    'Forest Temple East Courtyard Vines with Hookshot': {
        'name'    : 'logic_forest_vines',
        'tags'    : ("Forest Temple", "Forest Temple MQ", "Master Quest", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    The vines in Forest Temple leading to where the well
                    drain switch is in the standard form can be barely
                    reached with just the Hookshot. Applies to MQ also.
                    '''},
    'Forest Temple NE Outdoors Ledge with Hover Boots': {
        'name'    : 'logic_forest_outdoors_ledge',
        'tags'    : ("Forest Temple", "Forest Temple MQ", "Entrance Shuffle", "Master Quest", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    With precise Hover Boots movement you can fall down
                    to this ledge from upper balconies. If done precisely
                    enough, it is not necessary to take fall damage.
                    In MQ, this skips a Longshot requirement.
                    In Vanilla, this can skip a Hookshot requirement if
                    dungeon entrances are randomized.
                    '''},
    'Forest Temple East Courtyard Door Frame with Hover Boots': {
        'name'    : 'logic_forest_door_frame',
        'tags'    : ("Forest Temple", "Forest Temple MQ", "Master Quest", "Vanilla Dungeons", "Adult",),
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
        'tags'    : ("Forest Temple", "Forest Temple MQ", "Master Quest", "Vanilla Dungeons", "Child", "Adult",),
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
        'tags'    : ("Forest Temple MQ", "Master Quest", "Adult",),
        'tooltip' : '''\
                    Shoot the vines in the well as low and as far to
                    the right as possible, and then immediately swim
                    under the ceiling to the right. This can only be
                    required if Forest Temple is in its Master Quest
                    form.
                    '''},
    'Skip Forest Temple MQ Block Puzzle with Bombchu': {
        'name'    : 'logic_forest_mq_block_puzzle',
        'tags'    : ("Forest Temple MQ", "Master Quest", "Child", "Adult",),
        'tooltip' : '''\
                    Send the Bombchu straight up the center of the
                    wall directly to the left upon entering the room.
                    '''},
    'Forest Temple MQ Twisted Hallway Switch with Jump Slash': {
        'name'    : 'logic_forest_mq_hallway_switch_jumpslash',
        'tags'    : ("Forest Temple MQ", "Master Quest", "Child", "Adult",),
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
    #    'tags'    : ("Forest Temple MQ", "Master Quest", "Adult",),
    #    'tooltip' : '''\
    #                There's a very small gap between the glass block
    #                and the wall. Through that gap you can hookshot
    #                the target on the ceiling.
    #                '''},
    'Forest Temple MQ Twisted Hallway Switch with Boomerang': {
        'name'    : 'logic_forest_mq_hallway_switch_boomerang',
        'tags'    : ("Forest Temple MQ", "Entrance Shuffle", "Master Quest", "Child",),
        'tooltip' : '''\
                    The Boomerang can return to Link through walls,
                    allowing child to hit the hallway switch. This
                    can be used to allow adult to pass through later,
                    or in conjuction with "Forest Temple Outside
                    Backdoor with Jump Slash".
                    '''},
    'Fire Temple Boss Door without Hover Boots or Pillar': {
        'name'    : 'logic_fire_boss_door_jump',
        'tags'    : ("Fire Temple", "Fire Temple MQ", "Master Quest", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    The Fire Temple Boss Door can be reached as adult with a precise
                    jump. You must be touching the side wall of the room so
                    that Link will grab the ledge from farther away than
                    is normally possible.
                    '''},
    'Fire Temple Song of Time Room GS without Song of Time': {
        'name'    : 'logic_fire_song_of_time',
        'tags'    : ("Fire Temple", "Gold Skulltulas", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    A precise jump can be used to reach this room.
                    '''},
    'Fire Temple Climb without Strength': {
        'name'    : 'logic_fire_strength',
        'tags'    : ("Fire Temple", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    A precise jump can be used to skip
                    pushing the block.
                    '''},
    'Fire Temple East Tower without Scarecrow\'s Song': {
        'name'    : 'logic_fire_scarecrow',
        'tags'    : ("Fire Temple", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    Also known as "Pixelshot".
                    The Longshot can reach the target on the elevator
                    itself, allowing you to skip needing to spawn the
                    scarecrow.
                    '''},
    'Fire Temple Flame Wall Maze Skip': {
        'name'    : 'logic_fire_flame_maze',
        'tags'    : ("Fire Temple", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    If you move quickly you can sneak past the edge of
                    a flame wall before it can rise up to block you.
                    To do it without taking damage is more precise.
                    Allows you to progress without needing either a
                    Small Key or Hover Boots.
                    '''},
    'Fire Temple MQ Entrance Flame Wall Skip as Child': {
        'name'    : 'logic_fire_mq_child_flame',
        'tags'    : ("Fire Temple MQ", "Master Quest", "Child", "Entrance Shuffle", "Crates",),
        'tooltip' : '''\
                    If you move quickly you can sneak past the edge of
                    a flame wall before it can rise up to block you.
                    To do it without taking damage is more precise.
                    Allows child to reach two crates in the room before
                    the boss. This trick is only relevant if both dungeon
                    entrances and dungeon crates are shuffled, and the
                    trick "Fewer Tunic Requirements" is also enabled.
                    '''},
    'Fire Temple MQ Chest Near Boss without Breaking Crate': {
        'name'    : 'logic_fire_mq_near_boss',
        'tags'    : ("Fire Temple MQ", "Master Quest", "Adult",),
        'tooltip' : '''\
                    The hitbox for the torch extends a bit outside of the crate.
                    Shoot a flaming arrow at the side of the crate to light the
                    torch without needing to get over there and break the crate.
                    '''},
    'Fire Temple MQ Big Lava Room Blocked Door without Hookshot': {
        'name'    : 'logic_fire_mq_blocked_chest',
        'tags'    : ("Fire Temple MQ", "Master Quest", "Adult",),
        'tooltip' : '''\
                    There is a gap between the hitboxes of the flame
                    wall in the big lava room. If you know where this
                    gap is located, you can jump through it and skip
                    needing to use the Hookshot. To do this without
                    taking damage is more precise.
                    '''},
    'Fire Temple MQ Boss Key Chest without Bow': {
        'name'    : 'logic_fire_mq_bk_chest',
        'tags'    : ("Fire Temple MQ", "Master Quest", "Adult",),
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
        'tags'    : ("Fire Temple MQ", "Master Quest", "Adult",),
        'tooltip' : '''\
                    You can use the Hover Boots to hover around to
                    the climbable wall, skipping the need to use a
                    fire source and spawn a Hookshot target.
                    '''},
    'Fire Temple MQ Lizalfos Maze Side Room without Box': {
        'name'    : 'logic_fire_mq_maze_side_room',
        'tags'    : ("Fire Temple MQ", "Master Quest", "Adult",),
        'tooltip' : '''\
                    You can walk from the blue switch to the door and
                    quickly open the door before the bars reclose. This
                    skips needing to reach the upper sections of the
                    maze to get a box to place on the switch.
                    '''},
    'Fire Temple MQ Lower to Upper Lizalfos Maze with Hover Boots': {
        'name'    : 'logic_fire_mq_maze_hovers',
        'tags'    : ("Fire Temple MQ", "Master Quest", "Adult",),
        'tooltip' : '''\
                    Use the Hover Boots off of a crate to
                    climb to the upper maze without needing
                    to spawn and use the Hookshot targets.
                    '''},
    'Fire Temple MQ Lower to Upper Lizalfos Maze with Precise Jump': {
        'name'    : 'logic_fire_mq_maze_jump',
        'tags'    : ("Fire Temple MQ", "Master Quest", "Adult",),
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
        'tags'    : ("Fire Temple MQ", "Gold Skulltulas", "Master Quest", "Adult",),
        'tooltip' : '''\
                    The floor of the room that contains this Skulltula
                    is only solid from above. From the maze below, the
                    Longshot can be shot through the ceiling to obtain
                    the token with two fewer small keys than normal.
                    '''},
    'Fire Temple MQ Flame Wall Maze Skip': {
        'name'    : 'logic_fire_mq_flame_maze',
        'tags'    : ("Fire Temple MQ", "Gold Skulltulas", "Master Quest", "Adult",),
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
        'tags'    : ("Water Temple", "Vanilla Dungeons", "Adult",),
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
        'tags'    : ("Water Temple", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    With a midair side-hop while wearing the Hover
                    Boots, you can reach the cracked wall without
                    needing to raise the water up to the middle level.
                    '''},
    'Water Temple Cracked Wall with No Additional Items': {
        'name'    : 'logic_water_cracked_wall_nothing',
        'tags'    : ("Water Temple", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    A precise jump slash (among other methods) will
                    get you to the cracked wall without needing the
                    Hover Boots or to raise the water to the middle
                    level. This trick supersedes "Water Temple
                    Cracked Wall with Hover Boots".
                    '''},
    'Water Temple North Basement with Hover Boots': {
        'name'    : 'logic_water_north_basement',
        'tags'    : ("Water Temple", "Water Temple MQ", "Vanilla Dungeons", "Master Quest", "Adult",),
        'tooltip' : '''\
                    With precise Hover Boots movement it is possible to reach
                    the northern basement region without needing the Longshot.
                    It is not necessary to take damage from the spikes. In
                    Vanilla, the Gold Skulltula Token in the following room can
                    also be obtained with just the Hover Boots. In Master Quest,
                    this trick is only relevant if "Water Temple MQ Reach Dark
                    Link without Longshot" is also enabled.
                    '''},
    'Water Temple North Basement Ledge with Precise Jump': {
        'name'    : 'logic_water_north_basement_ledge_jump',
        'tags'    : ("Water Temple", "Water Temple MQ", "Master Quest", "Vanilla Dungeons", "Adult",),
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
        'tags'    : ("Water Temple", "Vanilla Dungeons", "Adult",),
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
        'tags'    : ("Water Temple", "Gold Skulltulas", "Vanilla Dungeons", "Child", "Adult",),
        'tooltip' : '''\
                    If you set Farore's Wind inside the central pillar
                    and then return to that warp point after raising
                    the water to the highest level, you can obtain this
                    Skulltula Token with Hookshot or Boomerang.
                    '''},
    'Water Temple Central Pillar GS with Iron Boots': {
        'name'    : 'logic_water_central_gs_irons',
        'tags'    : ("Water Temple", "Gold Skulltulas", "Vanilla Dungeons", "Adult",),
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
        'tags'    : ("Water Temple", "Vanilla Dungeons", "Child", "Adult",),
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
        'tags'    : ("Water Temple", "Gold Skulltulas", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    If you stand on the very edge of the platform, this
                    Gold Skulltula can be obtained with only the Hookshot.
                    '''},
    'Water Temple Falling Platform Room GS with Boomerang': {
        'name'    : 'logic_water_falling_platform_gs_boomerang',
        'tags'    : ("Water Temple", "Gold Skulltulas", "Entrance Shuffle", "Vanilla Dungeons", "Child",),
        'tooltip' : '''\
                    If you stand on the very edge of the platform, this
                    Gold Skulltula can be obtained with only the Boomerang.
                    This trick is only relevant if dungeon entrances are randomized.
                    '''},
    'Water Temple River GS without Iron Boots': {
        'name'    : 'logic_water_river_gs',
        'tags'    : ("Water Temple", "Gold Skulltulas", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    Standing on the exposed ground toward the end of
                    the river, a precise Longshot use can obtain the
                    token. The Longshot cannot normally reach far
                    enough to kill the Skulltula, however. You'll
                    first have to find some other way of killing it.
                    '''},
    'Water Temple Dragon Statue Jump Dive': {
        'name'    : 'logic_water_dragon_jump_dive',
        'tags'    : ("Water Temple", "Water Temple MQ", "Master Quest", "Vanilla Dungeons", "Adult",),
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
        'tags'    : ("Water Temple", "Vanilla Dungeons", "Adult",),
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
        'tags'    : ("Water Temple", "Entrance Shuffle", "Vanilla Dungeons", "Child",),
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
    'Water Temple Morpha without Hookshot': {
        'name'    : 'logic_water_morpha',
        'tags'    : ("Water Temple", "Water Temple MQ", "Entrance Shuffle", "Vanilla Dungeons", "Master Quest", "Child", "Adult",),
        'tooltip' : '''\
                    Morpha sometimes bounces out of the water,
                    and during that time it is possible to hit
                    it with a sword. This is only relevant in
                    conjunction with shuffled boss entrances.
                    '''},
    'Water Temple MQ Central Pillar with Fire Arrows': {
        'name'    : 'logic_water_mq_central_pillar',
        'tags'    : ("Water Temple MQ", "Master Quest", "Adult",),
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
    'Water Temple MQ Reach Dark Link without Longshot': {
        'name'    : 'logic_water_mq_dark_link',
        'tags'    : ("Water Temple MQ", "Master Quest", "Adult",),
        'tooltip' : '''\
                    The chasm before Dark Link can be crossed
                    with precise use of the Hover Boots and
                    the Hookshot.
                    '''},
    'Water Temple MQ North Basement GS without Small Key': {
        'name'    : 'logic_water_mq_locked_gs',
        'tags'    : ("Water Temple MQ", "Gold Skulltulas", "Master Quest", "Adult",),
        'tooltip' : '''\
                    There is an invisible Hookshot target that can be used
                    to get over the gate that blocks you from going to this
                    Skulltula early, skipping a small key as well as
                    needing Hovers or Scarecrow to reach the locked door.
                    '''},
    'Shadow Temple Stationary Objects without Lens of Truth': {
        'name'    : 'logic_lens_shadow',
        'tags'    : ("Lens of Truth", "Shadow Temple", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Shadow Temple for most areas in the dungeon
                    except for crossing the moving platform in the huge
                    pit room and for fighting Bongo Bongo.
                    '''},
    'Shadow Temple Invisible Moving Platform without Lens of Truth': {
        'name'    : 'logic_lens_shadow_platform',
        'tags'    : ("Lens of Truth", "Shadow Temple", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Shadow Temple to cross the invisible moving
                    platform in the huge pit room in either direction.
                    '''},
    'Shadow Temple Bongo Bongo without Lens of Truth': {
        'name'    : 'logic_lens_bongo',
        'tags'    : ("Shadow Temple", "Shadow Temple MQ", "Entrance Shuffle", "Master Quest", "Vanilla Dungeons", "Child", "Adult",),
        'tooltip' : '''\
                    Bongo Bongo can be defeated without the use of
                    Lens of Truth, as the hands give a pretty good
                    idea of where the eye is.
                    '''},
    'Shadow Temple Stone Umbrella Skip': {
        'name'    : 'logic_shadow_umbrella',
        'tags'    : ("Shadow Temple", "Shadow Temple MQ", "Master Quest", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    A very precise Hover Boots movement
                    from off of the lower chest can get you
                    on top of the crushing spikes without
                    needing to pull the block. Applies to
                    both Vanilla and Master Quest.

                    In Advanced Logic, this also allows for backflipping
                    through the umbrella with the clipping glitch, or
                    damage boosting off the spike with the damage boost
                    trick.
                    '''},
    'Shadow Temple Falling Spikes GS with Hover Boots': {
        'name'    : 'logic_shadow_umbrella_gs',
        'tags'    : ("Shadow Temple", "Shadow Temple MQ", "Gold Skulltulas", "Master Quest", "Vanilla Dungeons", "Adult",),
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
        'tags'    : ("Shadow Temple", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    Release the Bombchu with good timing so that
                    it explodes near the bottom of the pot.
                    '''},
    'Shadow Temple River Statue with Bombchu': {
        'name'    : 'logic_shadow_statue',
        'tags'    : ("Shadow Temple", "Shadow Temple MQ", "Master Quest", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    By sending a Bombchu around the edge of the
                    gorge, you can knock down the statue without
                    needing a Bow.
                    Applies in both vanilla and MQ Shadow.
                    '''},
    'Shadow Temple Triple Spinning Pots with Bombchus': {
        'name'    : 'logic_shadow_triple_pots',
        'tags'    : ("Shadow Temple", "Shadow Temple MQ", "Vanilla Dungeons", "Master Quest", "Adult", "Freestandings",),
        'tooltip' : '''\
                    Release the Bombchus with good timing so that
                    they explode near the bottoms of the pots.
                    This trick is only relevant if dungeon
                    freestandings are shuffled.
                    '''},
    'Shadow Temple Bongo Bongo without projectiles': {
        'name'    : 'logic_shadow_bongo',
        'tags'    : ("Shadow Temple", "Shadow Temple MQ", "Entrance Shuffle", "Vanilla Dungeons", "Master Quest", "Child", "Adult", "Shortcuts",),
        'tooltip' : '''\
                    Using precise sword slashes, Bongo Bongo can be
                    defeated without using projectiles. This is
                    only relevant in conjunction with Shadow Temple
                    dungeon shortcuts or shuffled boss entrances.
                    '''},
    'Shadow Temple MQ Stationary Objects without Lens of Truth': {
        'name'    : 'logic_lens_shadow_mq',
        'tags'    : ("Lens of Truth", "Shadow Temple MQ", "Master Quest", "Adult",),
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
        'tags'    : ("Lens of Truth", "Shadow Temple MQ", "Master Quest", "Silver Rupees", "Adult",),
        'tooltip' : '''\
                    Removes the requirement for the Lens of Truth or
                    Nayru's Love in Shadow Temple MQ for the Invisible
                    Blades room silver rupee collection.
                    '''},
    'Shadow Temple MQ Invisible Moving Platform without Lens of Truth': {
        'name'    : 'logic_lens_shadow_mq_platform',
        'tags'    : ("Lens of Truth", "Shadow Temple MQ", "Master Quest", "Adult",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Shadow Temple MQ to cross the invisible moving
                    platform in the huge pit room in either direction.
                    '''},
    'Shadow Temple MQ 2nd Dead Hand without Lens of Truth': {
        'name'    : 'logic_lens_shadow_mq_dead_hand',
        'tags'    : ("Lens of Truth", "Shadow Temple MQ", "Master Quest", "Adult",),
        'tooltip' : '''\
                    Dead Hand spawns in a random spot within the room.
                    Having Lens removes the hassle of having to comb
                    the room looking for his spawn location.
                    '''},
    'Shadow Temple MQ Truth Spinner Gap with Longshot': {
        'name'    : 'logic_shadow_mq_gap',
        'tags'    : ("Shadow Temple MQ", "Master Quest", "Adult",),
        'tooltip' : '''\
                    You can Longshot a torch and jump-slash recoil onto
                    the tongue. It works best if you Longshot the right
                    torch from the left side of the room.
                    '''},
    'Shadow Temple MQ Invisible Blades without Song of Time': {
        'name'    : 'logic_shadow_mq_invisible_blades',
        'tags'    : ("Shadow Temple MQ", "Master Quest", "Silver Rupees", "Freestandings", "Adult",),
        'tooltip' : '''\
                    The Like Like can be used to boost you into the
                    silver rupee or recovery hearts that normally
                    require Song of Time. This cannot be performed
                    on OHKO since the Like Like does not boost you
                    high enough if you die.
                    '''},
    'Shadow Temple MQ Lower Huge Pit without Fire Source': {
        'name'    : 'logic_shadow_mq_huge_pit',
        'tags'    : ("Shadow Temple MQ", "Master Quest", "Adult",),
        'tooltip' : '''\
                    Normally a frozen eye switch spawns some platforms
                    that you can use to climb down, but there's actually
                    a small piece of ground that you can stand on that
                    you can just jump down to.
                    '''},
    'Shadow Temple MQ Windy Walkway Reverse without Hover Boots': {
        'name'    : 'logic_shadow_mq_windy_walkway',
        'tags'    : ("Shadow Temple MQ", "Master Quest", "Adult", "Shortcuts",),
        'tooltip' : '''\
                    With shadow dungeon shortcuts enabled, it is possible
                    to jump from the alcove in the windy hallway to the
                    middle platform. There are two methods: wait out the fan
                    opposite the door and hold forward, or jump to the right
                    to be pushed by the fan there towards the platform ledge.
                    Note that jumps of this distance are inconsistent, but
                    still possible.
                    '''},
    'Shadow Temple MQ After Boat GS without Hookshot': {
        'name'    : 'logic_shadow_mq_after_boat_gs',
        'tags'    : ("Shadow Temple MQ", "Master Quest", "Adult", "Gold Skulltulas", "Shortcuts",),
        'tooltip' : '''\
                    To obtain this Skulltula Token without the Hookshot
                    entails falling into the chasm. Any projectile or
                    Din's Fire can be used to kill the Skulltula, and
                    you can also use a nearby pot. However, with the
                    statue down, any trajectory to throw a pot is
                    blocked, so you must jump above the Skulltula and
                    shield-drop the pot onto it. This trick is only
                    relevant if Shadow dungeon shortcuts are enabled.
                    '''},
    'Spirit Temple without Lens of Truth': {
        'name'    : 'logic_lens_spirit',
        'tags'    : ("Lens of Truth", "Spirit Temple", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Spirit Temple.
                    '''},
    'Spirit Temple Child Side Bridge with Bombchu': {
        'name'    : 'logic_spirit_child_bombchu',
        'tags'    : ("Spirit Temple", "Vanilla Dungeons", "Child",),
        'tooltip' : '''\
                    A carefully-timed Bombchu can hit the switch.
                    '''},
    'Spirit Temple Collect Metal Fence GS Through the Fence': {
        'name'    : 'logic_spirit_fence_gs',
        'tags'    : ("Spirit Temple", "Silver Rupees", "Vanilla Dungeons", "Child",),
        'tooltip' : '''\
                    After killing the Skulltula through the fence, the token
                    can be collected from the wrong side of the fence by
                    moving against the fence in a certain way. Also, the
                    Skulltula can be defeated using the Kokiri Sword, by
                    jump slashing into it after letting go from the fence.
                    This trick is only relevant if Silver Rupees are shuffled.
                    '''},
    'Spirit Temple Main Room GS with Boomerang': {
        'name'    : 'logic_spirit_lobby_gs',
        'tags'    : ("Spirit Temple", "Gold Skulltulas", "Vanilla Dungeons", "Child",),
        'tooltip' : '''\
                    Standing on the highest part of the arm of the statue, a
                    precise Boomerang throw can kill and obtain this Gold
                    Skulltula. You must throw the Boomerang slightly off to
                    the side so that it curves into the Skulltula, as aiming
                    directly at it will clank off of the wall in front.
                    '''},
    'Spirit Temple Lower Adult Switch with Bombs': {
        'name'    : 'logic_spirit_lower_adult_switch',
        'tags'    : ("Spirit Temple", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    A bomb can be used to hit the switch on the ceiling,
                    but it must be thrown from a particular distance
                    away and with precise timing.
                    '''},
    'Spirit Temple Main Room Jump from Hands to Upper Ledges': {
        'name'    : 'logic_spirit_lobby_jump',
        'tags'    : ("Spirit Temple", "Spirit Temple MQ", "Gold Skulltulas", "Pots", "Master Quest", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    A precise jump to obtain the following as adult
                    without needing one of Hover Boots, or Hookshot
                    (in vanilla) or Song of Time (in MQ):
                    - Spirit Temple Statue Room Northeast Chest
                    - Spirit Temple GS Lobby
                    - Spirit Temple MQ Central Chamber Top Left Pot (Left)
                    - Spirit Temple MQ Central Chamber Top Left Pot (Right)
                    '''},
    'Spirit Temple Main Room Hookshot to Boss Platform': {
        'name'    : 'logic_spirit_platform_hookshot',
        'tags'    : ("Spirit Temple", "Vanilla Dungeons", "Adult", "Shortcuts",),
        'tooltip' : '''\
                    Precise hookshot aiming at the platform chains can be
                    used to reach the boss platform from the middle landings.
                    Using a jump slash immediately after reaching a chain
                    makes aiming more lenient. Relevant only when Spirit
                    Temple boss shortcuts are on.
                    '''},
    'Spirit Temple Climb to Adult Side with Hover Boots': {
        'name'    : 'logic_spirit_adult_side_hovers',
        'tags'    : ("Spirit Temple", "Vanilla Dungeons", "Adult", "Shortcuts",),
        'tooltip' : '''\
                    With some help from the nearby Armos, Adult
                    can use the Hover Boots to climb to the Adult
                    side of the dungeon. Relevant only when
                    Spirit Temple boss shortcuts are on.
                    '''},
    'Spirit Temple Map Chest with Bow': {
        'name'    : 'logic_spirit_map_chest',
        'tags'    : ("Spirit Temple", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    To get a line of sight from the upper torch to
                    the map chest torches, you must pull an Armos
                    statue all the way up the stairs.
                    '''},
    'Spirit Temple Sun Block Room Chest with Bow': {
        'name'    : 'logic_spirit_sun_chest_bow',
        'tags'    : ("Spirit Temple", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    Using the blocks in the room as platforms you can
                    get lines of sight to all three torches. The timer
                    on the torches is quite short so you must move
                    quickly in order to light all three.
                    '''},
    'Spirit Temple Sun Block Room Chest with Sticks without Silver Rupees': {
        'name'    : 'logic_spirit_sun_chest_no_rupees',
        'tags'    : ("Spirit Temple", "Silver Rupees", "Vanilla Dungeons", "Child",),
        'tooltip' : '''\
                    With lightning fast movement, the chest can
                    be spawned using a lit stick brought in from
                    the main room. This trick is only relevant
                    if Silver Rupees are shuffled.
                    '''},
    'Spirit Temple Shifting Wall with No Additional Items': {
        'name'    : 'logic_spirit_wall',
        'tags'    : ("Spirit Temple", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    Logic normally guarantees a way of dealing with both
                    the Beamos and the Walltula before climbing the wall.
                    '''},
    'Spirit Temple MQ without Lens of Truth': {
        'name'    : 'logic_lens_spirit_mq',
        'tags'    : ("Lens of Truth", "Spirit Temple MQ", "Master Quest", "Adult",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Spirit Temple MQ.
                    '''},
    'Spirit Temple MQ Sun Block Room as Child without Song of Time': {
        'name'    : 'logic_spirit_mq_sun_block_sot',
        'tags'    : ("Spirit Temple MQ", "Master Quest", "Child",),
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
        'tags'    : ("Spirit Temple MQ", "Gold Skulltulas", "Master Quest", "Child",),
        'tooltip' : '''\
                    Throw the Boomerang in such a way that it
                    curves through the side of the glass block
                    to hit the Gold Skulltula.
                    '''},
    'Spirit Temple MQ Lower Adult without Fire Arrows': {
        'name'    : 'logic_spirit_mq_lower_adult',
        'tags'    : ("Spirit Temple MQ", "Master Quest", "Adult",),
        'tooltip' : '''\
                    By standing in a precise position it is possible to
                    light two of the torches with a single use of Din\'s
                    Fire. This saves enough time to be able to light all
                    three torches with only Din\'s.
                    '''},
    'Spirit Temple MQ Frozen Eye Switch without Fire': {
        'name'    : 'logic_spirit_mq_frozen_eye',
        'tags'    : ("Spirit Temple MQ", "Master Quest", "Adult",),
        'tooltip' : '''\
                    You can melt the ice by shooting an arrow through a
                    torch. The only way to find a line of sight for this
                    shot is to first spawn a Song of Time block, and then
                    stand on the very edge of it.
                    '''},
    'Spirit Temple MQ Water Jet Silver Rupee without Hammer': {
        'name'    : 'logic_spirit_mq_water_rupee',
        'tags'    : ("Spirit Temple MQ", "Master Quest", "Adult", "Silver Rupees",),
        'tooltip' : '''\
                    You can obtain the Silver Rupee inside the water
                    jet by Longshotting through it to a chest in the
                    first room. Because this is the very chest that
                    collecting this rupee normally spawns, this trick
                    is only relevant when Silver Rupees are shuffled.
                    '''},
    'Ice Cavern Frozen Rupee with Nothing': {
        'name'    : 'logic_ice_frozen_rupee',
        'tags'    : ("Ice Cavern", "Vanilla Dungeons", "Freestandings", "Child", "Adult",),
        'tooltip' : '''\
                    This rupee can be obtained with no items by
                    side-hopping into the corner behind the ice.
                    '''},
    'Ice Cavern Frozen Pot with No Additional Items': {
        'name'    : 'logic_ice_frozen_pot',
        'tags'    : ("Ice Cavern", "Vanilla Dungeons", "Pots", "Adult",),
        'tooltip' : '''\
                    A spin attack can slash the
                    pot through the red ice.
                    '''},
    'Ice Cavern Block Room GS with Hover Boots': {
        'name'    : 'logic_ice_block_gs',
        'tags'    : ("Ice Cavern", "Gold Skulltulas", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    The Hover Boots can be used to get in front of the
                    Skulltula to kill it with a jump slash. Then, the
                    Hover Boots can again be used to obtain the Token,
                    all without Hookshot or Boomerang.
                    '''},
    'Ice Cavern MQ Red Ice GS without Song of Time': {
        'name'    : 'logic_ice_mq_red_ice_gs',
        'tags'    : ("Ice Cavern MQ", "Gold Skulltulas", "Master Quest", "Adult",),
        'tooltip' : '''\
                    If you side-hop into the perfect position, you
                    can briefly stand on the platform with the red
                    ice just long enough to dump some blue fire.
                    '''},
    'Ice Cavern MQ Scarecrow GS with No Additional Items': {
        'name'    : 'logic_ice_mq_scarecrow',
        'tags'    : ("Ice Cavern MQ", "Gold Skulltulas", "Master Quest", "Adult",),
        'tooltip' : '''\
                    As adult a precise jump can be used to reach this alcove.
                    '''},
    'Gerudo Training Ground without Lens of Truth': {
        'name'    : 'logic_lens_gtg',
        'tags'    : ("Lens of Truth", "Gerudo Training Ground", "Vanilla Dungeons", "Child", "Adult",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Gerudo Training Ground.
                    '''},
    'Gerudo Training Ground Highest Underwater Rupee with Gold Scale': {
        'name'    : 'logic_gtg_underwater_highest',
        'tags'    : ("Gerudo Training Ground", "Vanilla Dungeons", "Silver Rupees", "Child", "Adult",),
        'tooltip' : '''\
                    The camera is a menance while attempting to do this,
                    though, as least as Adult, you will be automatically
                    pulled by the current into the rupee. This trick is
                    only relevant if Silver Rupees are shuffled.
                    '''},
    'Gerudo Training Ground Left Side Ceiling Silver Rupee without Hookshot': {
        'name'    : 'logic_gtg_without_hookshot',
        'tags'    : ("Gerudo Training Ground", "Gerudo Training Ground MQ", "Silver Rupees", "Master Quest", "Vanilla Dungeons", "Child", "Adult",),
        'tooltip' : '''\
                    The Silver Rupee on the ceiling can be reached by being pulled
                    up into it by the Wallmaster. If Silver Rupees are not shuffled,
                    you can save this rupee for last to unbar the door to the next
                    room. In MQ, this trick is a bit more difficult since the
                    Wallmaster will not track you to directly beneath the rupee, so
                    you must inch forward after it begins its attempt to grab you.
                    This trick is relevant if Silver Rupees are shuffled, or if GTG
                    is in its MQ form, or if "Gerudo Training Ground Boulder Room
                    Flame Wall Skip" is also enabled. This trick supersedes "Gerudo
                    Training Ground MQ Left Side Ceiling Silver Rupee with Hookshot".
                    '''},
    'Gerudo Training Ground Boulder Room Flame Wall Skip': {
        'name'    : 'logic_gtg_flame_wall',
        'tags'    : ("Gerudo Training Ground", "Vanilla Dungeons", "Silver Rupees", "Child", "Adult",),
        'tooltip' : '''\
                    If you move quickly you can sneak past the edge of a flame wall
                    before it can rise up to block you. To do so without taking damage
                    is more precise. This trick is only relevant if Silver Rupees are
                    shuffled, or if "Gerudo Training Ground Left Side Ceiling Silver
                    Rupee without Hookshot" is also enabled.
                    '''},
    'Reach Gerudo Training Ground Fake Wall Ledge with Hover Boots': {
        'name'    : 'logic_gtg_fake_wall',
        'tags'    : ("Gerudo Training Ground", "Gerudo Training Ground MQ", "Master Quest", "Vanilla Dungeons", "Silver Rupees", "Adult",),
        'tooltip' : '''\
                    A precise Hover Boots use from the top of the chest can allow you
                    to grab the ledge without needing the usual requirements. In Master
                    Quest, this always skips a Song of Time requirement. In Vanilla,
                    this can skip a Hookshot requirement, but it is only relevant if
                    Silver Rupees are shuffled, or if "Gerudo Training Ground Left Side
                    Ceiling Silver Rupee without Hookshot" is enabled.
                    '''},
    'Gerudo Training Ground MQ without Lens of Truth': {
        'name'    : 'logic_lens_gtg_mq',
        'tags'    : ("Lens of Truth", "Gerudo Training Ground MQ", "Master Quest", "Child", "Adult",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Gerudo Training Ground MQ.
                    '''},
    'Gerudo Training Ground MQ Left Side Ceiling Silver Rupee with Hookshot': {
        'name'    : 'logic_gtg_mq_with_hookshot',
        'tags'    : ("Gerudo Training Ground MQ", "Silver Rupees", "Master Quest", "Adult",),
        'tooltip' : '''\
                    The highest Silver Rupee can be obtained by
                    hookshotting the target and then immediately jump
                    slashing toward the rupee.
                    '''},
    'Gerudo Training Ground MQ Eye Statue Room Switch with Jump Slash': {
        'name'    : 'logic_gtg_mq_eye_statue_jumpslash',
        'tags'    : ("Gerudo Training Ground MQ", "Silver Rupees", "Master Quest", "Adult",),
        'tooltip' : '''\
                    The switch that unbars the door to the Ice Arrows chest
                    can be hit with a precise jump slash. This trick is
                    only relevant if Silver Rupees are shuffled, or if
                    "Gerudo Training Ground Left Side Ceiling Silver Rupee
                    without Hookshot" is also enabled.
                    '''},
    'Gerudo Training Ground Eye Statue Room Wonderitem with Jump Slash': {
        'name'    : 'logic_gtg_eye_statue_wonderitem',
        'tags'    : ("Gerudo Training Ground", "Gerudo Training Ground MQ", "Wonderitems", "Master Quest", "Vanilla Dungeons", "Adult",),
        'tooltip' : '''\
                    The wonderitem on top of the eye statue can be reached
                    with a precise jump slash.
                    '''
    },
    'Gerudo Training Ground MQ Central Maze Right to Dinolfos Room with Hookshot': {
        'name'    : 'logic_gtg_mq_maze_right',
        'tags'    : ("Gerudo Training Ground MQ", "Silver Rupees", "Master Quest", "Adult",),
        'tooltip' : '''\
                    You can stand next to the flame circle to the right of
                    the entrance into the lava room from central maze right.
                    From there, Hookshot can reach the torch to access the
                    Dinolfos room without Bow. This trick is only relevant
                    if Silver Rupees are shuffled or if one of the two tricks
                    to collect the ceiling Silver Rupee without Longshot
                    is enabled.
                    '''},
    'Ganon\'s Castle without Lens of Truth': {
        'name'    : 'logic_lens_castle',
        'tags'    : ("Lens of Truth", "Ganon's Castle", "Vanilla Dungeons", "Child", "Adult",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Ganon's Castle.
                    '''},
    'Fire Trial Torch Slug Silver Rupee as Child': {
        'name'    : 'logic_fire_trial_slug_rupee',
        'tags'    : ("Ganon's Castle", "Entrance Shuffle", "Vanilla Dungeons", "Silver Rupees", "Child"),
        'tooltip' : '''\
                    To jump to the platform with the Torch Slug as child requires
                    that the sinking platform be almost as high as possible. This
                    trick is only relevant if Silver Rupees and the Ganon's Castle
                    entrance are both shuffled, and the Fewer Tunic Requirements
                    trick is also enabled.
                    '''},
    'Spirit Trial Ceiling Silver Rupee without Hookshot': {
        'name'    : 'logic_spirit_trial_hookshot',
        'tags'    : ("Ganon's Castle", "Vanilla Dungeons", "Silver Rupees", "Child", "Adult",),
        'tooltip' : '''\
                    The highest rupee can be obtained as either age by performing
                    a precise jump and a well-timed jumpslash off of an Armos.
                    '''},
    'Ganon\'s Castle MQ Except Shadow Trial without Lens of Truth': {
        'name'    : 'logic_lens_castle_mq',
        'tags'    : ("Lens of Truth", "Ganon's Castle MQ", "Master Quest", "Child", "Adult",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in Ganon's Castle MQ, except for the Lens
                    requirements in Shadow Trial.
                    '''},
    'Ganon\'s Castle MQ Shadow Trial without Lens of Truth': {
        'name'    : 'logic_lens_shadow_trial_mq',
        'tags'    : ("Lens of Truth", "Ganon's Castle MQ", "Master Quest", "Adult",),
        'tooltip' : '''\
                    Removes the requirements for the Lens of Truth
                    in the Shadow Trial in Ganon's Castle MQ.
                    Be sure to also enable "Ganon\'s Castle MQ Except
                    Shadow Trial without Lens of Truth" to remove
                    the Lens requirement for the rest of the Castle.
                    '''},
    'Fire Trial MQ with Hookshot': {
        'name'    : 'logic_fire_trial_mq',
        'tags'    : ("Ganon's Castle MQ", "Master Quest", "Adult",),
        'tooltip' : '''\
                    It's possible to hook the target at the end of
                    fire trial with just Hookshot, but it requires
                    precise aim and perfect positioning. The main
                    difficulty comes from getting on the very corner
                    of the obelisk without falling into the lava.
                    '''},
    'Shadow Trial MQ Torch with Bow': {
        'name'    : 'logic_shadow_trial_mq',
        'tags'    : ("Ganon's Castle MQ", "Master Quest", "Adult",),
        'tooltip' : '''\
                    You can light the torch in this room without a fire
                    source by shooting an arrow through the lit torch
                    at the beginning of the room. Because the room is
                    so dark and the unlit torch is so far away, it can
                    be difficult to aim the shot correctly.
                    '''},
    'Light Trial MQ without Hookshot': {
        'name'    : 'logic_light_trial_mq',
        'tags'    : ("Ganon's Castle MQ", "Master Quest", "Adult",),
        'tooltip' : '''\
                    If you move quickly you can sneak past the edge of
                    a flame wall before it can rise up to block you.
                    In this case to do it without taking damage is
                    especially precise.
                    '''}
}

advanced_logic_tricks: dict[str, dict[str, str | tuple[str, ...]]] = {
    #   Advanced glitchless tricks will be first, followed by General Glitch Tricks and then Dungeon tricks
    #   For glitches with multiple trick variants, refer to tooltip description
    '(Glitch) Infinite Sword Glitch (ISG)': {
        'name'    : 'glitch_isg',
        'tags'    : ("Glitch","Child", "Adult",),
        'tooltip' : '''\
                    Crouch stabbing and interrupting it puts Link in a state
                    where he is constantly swinging his sword. This can be used
                    for damage output or for the secondary property of being
                    unable to fall off ledges while in this state.

                    This is required for hovering.
                    '''},
    '(Glitch) Groundjumps': {
        'name'    : 'glitch_groundjump',
        'tags'    : ("Glitch","Child", "Adult",),
        'tooltip' : '''\
                    Shielding while attempting to pick up a Bomb stores that
                    state. If you then backflip, the backflip will be cancelled
                    allowing Link to grab ledges higher than usual.  Useful
                    in some places and easier than the glitchless alternative
                    of Recoil Jumps.
                    '''},
    '(Glitch) Clipping': {
        'name'    : 'glitch_clipping',
        'tags'    : ("Glitch","Child", "Adult",),
        'tooltip' : '''\
                    As we all know the collision in this game is a mere suggestion
                    at times. Enabling this will allow for the logical use of many
                    damage clips, clipping through acute angles, squeezing through
                    boulders, and generally used clips through the game.
                    Some more niche ones will have their own
                    trick unrelated to this one.
                    '''},
    '(Glitch) Triple Slash Clip': {
        'name'    : 'glitch_tsc',
        'tags'    : ("Glitch","Child", "Adult",),
        'tooltip' : '''\
                    Using the Triple Slash animation and a first person item on
                    a particular frame window can displace Link through some
                    corners.

                    This is not dependent on the Clipping trick.
                    '''},
    '(Glitch) Ledge Clips': {
        'name'    : 'glitch_ledge_clip',
        'tags'    : ("Glitch","Adult",),
        'tooltip' : '''\
                    Enables general Ledge Clipping as Adult Link.
                    Useful in a few places such as Forest Temple to skip
                    the Song of Time block.
                    '''},
    '(Glitch) Lunge Storage': {
        'name'    : 'glitch_lunge_storage',
        'tags'    : ("Glitch","Child", "Adult",),
        'tooltip' : '''\
                    Lunge storage allows acute angle clips to be possible by
                    cancelling the attack early and storing the forward
                    displacement to reach places a normal jumpslash
                    cannot bypass.
                    '''},
    '(Glitch) Equip Swap': {
        'name'    : 'glitch_equip_swap',
        'tags'    : ("Glitch","Child", "Adult",),
        'tooltip' : '''\
                    This has a built-in assumption that
                    to successfully be able to equip swap
                    Child needs access to anything in the
                    leftmost column, and Adult needs access
                    to a spell due to the child trade item.
                    No other slot targets are
                    considered by logic, even if you can
                    perform them.
                    '''},
    '(Glitch) Itemless Forest Escape': {
        'name'    : 'glitch_itemless_forest_escape',
        'tags'    : ("Glitch","Child","Entrance Shuffle",),
        'tooltip' : '''\
                    Itemless escape requires precise
                    timing using a rock in front of Midos
                    House. If enabling, be warned it may
                    be required in Entrance Shuffle.
                    '''},
    '(Glitch) Pokey Escape': {
        'name'    : 'glitch_pokey_escape',
        'tags'    : ("Glitch","Child","Entrance Shuffle",),
        'tooltip' : '''\
                    A different variation of forest escape
                    but more accessible. This requires a stick
                    or sword and shield to pass to LW Bridge.
                    '''},
    '(Glitch) WESS Escape': {
        'name'    : 'glitch_wess_escape',
        'tags'    : ("Glitch","Child","Entrance Shuffle",),
        'tooltip' : '''\
                    A minimal items escape compared to Pokey.
                    Requires only sword or stick. Useful for
                    Entrance Shuffle and minimal items or
                    preferences.
                    '''},
    '(Glitch) Hovering with Explosives': {
        'name'    : 'glitch_hovering',
        'tags'    : ("Glitch","Child", "Adult",),
        'tooltip' : '''\
                    Requires a way to get ISG, a shield, and
                    both bombs and chus. This trick makes no
                    distinction between bombs and chus for the
                    purpose of generalized hovering and by having
                    access to both explosives.
                    '''},
    '(Glitch) Megaflips and Megasidehops': {
        'name'    : 'glitch_megaflip',
        'tags'    : ("Glitch","Child", "Adult",),
        'tooltip' : '''\
                    Megaflips and megasidehops are used to cross
                    gaps or obstacles that cannot be reached by jumping.
                    as it preserves the same momentum as a superslide.
                    Either explosive is accounted for in this trick.
                    Enemy boosts are not included in logic.
                    '''},
    '(Glitch) Ocarina Items': {
        'name'    : 'glitch_oi',
        'tags'    : ("Glitch","Child", "Adult",),
        'tooltip' : '''\
                    This trick only logically considers Putaway
                    OI as it only requires a bottle and nothing
                    else so it is usable in more places. Be warned
                    that this can dupe over items if done
                    incorrectly!
                    '''},
    '(Glitch) Superslide': {
        'name'    : 'glitch_superslide',
        'tags'    : ("Glitch","Child", "Adult",),
        'tooltip' : '''\
                    Supersliding can be an alternative to HESS
                    to access items through obstacles in some
                    cases. This is a good beginning into HESS.
                    Superslide teleports are not included in logic.
                    '''},
    '(Glitch) HESS': {
        'name'    : 'glitch_hess',
        'tags'    : ("Glitch","Child", "Adult",),
        'tooltip' : '''\
                    Hyper Extended Superslides have numerous
                    uses for passing obstacles. There are the same
                    requirements for Superslide versus HESS however
                    the ability to change direction opens up a few
                    more locations.
                    '''},
    '(Advanced) Hoverboots Recoil': {
        'name'    : 'adv_hovers_recoil',
        'tags'    : ("Glitchless","Adult",),
        'tooltip' : '''\
                    Allows for the use of Hover Boots momentum
                    after a recoil or damage
                    in many scenarios to reach regions or cross through
                    obstacles. In the case of a clip it would be
                    specified differently in logic to allow use for
                    GGJ or advanced play.
                    '''},
    '(Advanced) Recoil Jumps': {
        'name'    : 'adv_recoil_jump',
        'tags'    : ("Glitchless","Adult",),
        'tooltip' : '''\
                    By shielding an explosion or damage midair, usually
                    out of a twisted backflip, Link is able to gain the
                    height from the backflip but also be able to grab
                    ledges. This is the glitchless variant of a
                    groundjump as they achieve similar goals.
                    '''},
    '(Glitch) Glitch Damage Value': {
        'name'    : 'glitch_damage_value',
        'tags'    : ("Glitch","QPA","Glitch Damage Value",),
        'tooltip' : '''\
                    Allows for use of QPA or Empty Jumpslash
                    to store the glitch damage value and use
                    it for power crouch stabbing or isg.
                    Other specific use cases may have a separate
                    trick.
                    '''},
    '(Glitch) Ledge Cancel': {
        'name'    : 'glitch_ledge_cancel',
        'tags'    : ("Glitch","Child","Adult",),
        'tooltip' : '''\
                    Climb a ledge and shield at the end of the
                    animation to activate. This glitch makes Link
                    ignore hitboxes of actors to walk through
                    boulders and NPCs.
                    '''},
    '(Glitch) Weirdshot': {
        'name'    : 'glitch_weirdshot',
        'tags'    : ("Glitch","Adult","Bouldersanity", "Entrance Shuffle",),
        'tooltip' : '''\
                    Weirdshotting is in logic with bombs, though
                    chus can be utilized. Weirdshots are a pre-
                    requisite for weirdslides to be enabled.
                    Weirdslides are for entering grottos
                    without hammer or strength or pressing
                    switches under unmovable boulders.
                    '''},
    '(Advanced) Damage Boost': {
        'name'    : 'adv_damage_boost',
        'tags'    : ("Glitchless","Child","Adult",),
        'tooltip' : '''\
                    Damage boosting has multiple uses for
                    crossing gaps without hover boots or
                    crossing obstacles. This is not suitable
                    for OHKO.
                    '''},
    '(Advanced) Wallwalking': {
        'name'    : 'adv_wallwalking',
        'tags'    : ("Glitchless","Child","Adult",),
        'tooltip' : '''\
                    Previously known as Seamwalking, this allows you to
                    walk on the sides and tops of walls as in certain
                    situations the game counts them as floors.  Some uses
                    are the Desert Colossus GS on the rock, and grabbing
                    the Lake Hylia underwater rupees with the Boomerang.
                    '''},
    '(Glitch) Hookshot Jumps': {
        'name'    : 'glitch_hookshot_jump',
        'tags'    : ("Glitch","Adult",),
        'tooltip' : '''\
                    Fly high in the air by cancelling hook
                    animation. There are various checks that
                    can be reached with a jump. Doom jump
                    is a separate trick.
                    '''},
    '(Glitch) Open Underwater Chests': {
        'name'    : 'glitch_underwater_chests',
        'tags'    : ("Glitch","Adult",),
        'tooltip' : '''\
                    While wearing Iron Boots, you can hookshot something
                    to set Link's state and be able to open chests
                    underwater.
                    '''},
    '(Glitch) LW Target with GDV': {
        'name'    : 'glitch_lw_target_hover',
        'tags'    : ("Glitch","QPA","Glitch Damage Value",),
        'tooltip' : '''\
                    Includes hovering to reach the slingshot target.
                    '''},
    '(Glitch) Navi Dive': {
        'name'    : 'glitch_navi_dive',
        'tags'    : ("Glitch","Child","Adult", "Entrance Shuffle",),
        'tooltip' : '''\
                    Useful for Entrance Shuffle to dive
                    without Scale or Iron Boots. Relevant for both
                    ages and is distintive for each use case in logic.
                    '''},
    '(Glitch) Aqua Escape Child': {
        'name'    : 'glitch_aqua_escape_child',
        'tags'    : ("Glitch","Child","Entrance Shuffle",),
        'tooltip' : '''\
                    Useful for Entrance Shuffle where Navi may
                    not be available to be called upon. Requires
                    only a stick.
                    '''},
    '(Glitch) Aqua Escape Adult': {
        'name'    : 'glitch_aqua_escape_adult',
        'tags'    : ("Glitch","Adult", "Entrance Shuffle",),
        'tooltip' : '''\
                    Requires only sword and shield. Useful
                    for access to entrance without Navi call.
                    '''},
    '(Advanced) LH Tree GS with only Hookshot': {
        'name'    : 'adv_lh_tree_gs_hookshot',
        'tags'    : ("Glitchless","Adult",),
        'tooltip' : '''\
                    Wall walk up the tree stump and reach
                    this skull without longshot to collect.

                    This requires Wallwalking to be enabled.
                    '''},
    '(Glitch) LH to Zora\'s Domain as Child with Nothing': {
        'name'    : 'glitch_lh_to_zd_child_nothing',
        'tags'    : ("Glitch","Child","Entrance Shuffle",),
        'tooltip' : '''\
                    Clip into the Lakeside Lab house through
                    the corner and swim OOB to reach the load.
                    '''},
    '(Glitch) Enter Water Groundclip': {
        'name'    : 'glitch_enter_water_groundclip',
        'tags'    : ("Glitch","Adult","Entrance Shuffle",),
        'tooltip' : '''\
                    Enter water from the warp pad with a
                    serious of movements ending with a jumpslash
                    into the loading zone to the dungeon. One of
                    many variations.
                    '''},
    '(Glitch) Enter Water Ledge Clip': {
        'name'    : 'glitch_enter_water_ledgeclip',
        'tags'    : ("Glitch","Adult","Entrance Shuffle",),
        'tooltip' : '''\
                    Enter Water by Ledge Clipping on the island with
                    the grave to get underground and swim to the
                    load Out of Bounds.
                    '''},
    '(Glitch) Enter Water Slippery Dive with Ocarina': {
        'name'    : 'glitch_enter_water_ocarina',
        'tags'    : ("Glitch","Adult","Entrance Shuffle",),
        'tooltip' : '''\
                    Enter water from the central island by walking
                    onto the slippery slope over the entrance
                    and pulling Ocarina at the time time to dive
                    through the water and swim in after opening
                    the gate.
                    '''},
    '(Glitch) Enter Water Lab Clip Adult': {
        'name'    : 'glitch_enter_water_lab_clip_adult',
        'tags'    : ("Glitch","Adult","Entrance Shuffle",),
        'tooltip' : '''\
                    The traditional minimal item entrance into water.
                    Same item requirements as groundclip, this is
                    down to preference. One of many variations.
                    '''},
    '(Glitch) Enter Water Lab Clip Child': {
        'name'    : 'glitch_enter_water_lab_clip_child',
        'tags'    : ("Glitch","Child","Entrance Shuffle",),
        'tooltip' : '''\
                    Enter water as child through the lab clip
                    and swim to the loading zone. Refer to videos
                    for the swim without mashing.
                    '''},
    '(Glitch) Lakeside Lab with less stuff': {
        'name'    : 'glitch_lakeside_lab_with_less',
        'tags'    : ("Glitch","Adult",),
        'tooltip' : '''\
                    Achieve the lakeside lab reward without
                    gold scale, irons or hookshot. Utilizes a
                    bottle and Hover Boots for the method.
                    '''},
    '(Glitch) Unfreeze King Zora with Nothing': {
        'name'    : 'glitch_kz_with_nothing',
        'tags'    : ("Glitch","Adult","King Zora","Zora's Domain",),
        'tooltip' : '''\
                    Reading a sign whilst standing in the correct
                    spot and facing the correct way will cause
                    the red ice around King Zora to permanently
                    disappear.
                    '''},
    '(Advanced) GV Broken Bridge with Hookshot': {
        'name'    : 'adv_gv_bridge_hookshot',
        'tags'    : ("Glitchless","Adult",),
        'tooltip' : '''\
                    Cross the GV bridge with Hookshot Extension.
                    '''},
    '(Advanced) GV Broken Bridge Cucco Jump': {
        'name'    : 'adv_cucco_jump',
        'tags'    : ("Glitch","Child",),
        'tooltip' : '''\
                    Jump over the gerudo guard and gate at
                    the bridge with the cucco. Requires shield
                    and sword for this trick.
                    '''},
    '(Advanced) GV Cross Broken Bridge with Recoil off Boulder': {
        'name'    : 'adv_gv_boulder_recoil',
        'tags'    : ("Glitchless","Adult",),
        'tooltip' : '''\
                    With semi-precise positioning, you can recoil
                    off a boulder and preserve the momentum with
                    Hover Boots to cross the broken bridge.
                    '''},
    '(Advanced) GV Tent as Child': {
        'name'    : 'adv_gv_tent_child',
        'tags'    : ("Glitchless","Child","Entrance Shuffle",),
        'tooltip' : '''\
                    The tent while invisible, the loading zone
                    can be reached as child. Including this trick
                    makes it logically accessible for Entrance Shuffle.
                    '''},
    '(Glitch) GV Chest with Longshot': {
        'name'    : 'glitch_gv_chest_longshot',
        'tags'    : ("Glitch","Adult","Gerudo Valley",),
        'tooltip' : '''\
                    Moving far enough away from the boulders
                    disables their collision, allowing the tip
                    of the Longshot to reach the chest and pull
                    Link through.
                    '''},
    '(Advanced) GV Grotto Ledge to Upper Stream': {
        'name'    : 'adv_gv_grotto_ledge_to_upper',
        'tags'    : ("Glitchless","Child","Adult",),
        'tooltip' : '''\
                    With a backward sidehop and jumpslash recoil off
                    the wall, you can reach the upper stream area from
                    the grotto ledge without taking damage.
                    '''},
    '(Glitch) GTG Adult Groundclip': {
        'name'    : 'glitch_gtg_adult_groundclip',
        'tags'    : ("Glitch","Adult","Entrance Shuffle",),
        'tooltip' : '''\
                    Ledgecancel at the top of the fortress and
                    drop down into the loading zone of GTG to skip
                    freeing the guards or paying the fee.
                    '''},
    '(Glitch) GTG Child Groundclip': {
        'name'    : 'glitch_gtg_child_groundclip',
        'tags'    : ("Glitch","Child","Entrance Shuffle",),
        'tooltip' : '''\
                    Requires stick or sword, and shield. Enter
                    GTG entrance by jumpslashing through the gate.
                    '''},
    '(Advanced) GF Gate Skip': {
        'name'    : 'adv_gf_gateskip',
        'tags'    : ("Glitchless","Adult","Entrance Shuffle",),
        'tooltip' : '''\
                     Jump the fence from the balcony of GF
                     and use hover boots to land on the wall to walk down
                     towards the gate and pass. Can be done day or night.
                    '''},
    '(Advanced) GF Unload with Antigrav': {
        'name'    : 'adv_gf_unload',
        'tags'    : ("Glitchless","Child","Adult","Entrance Shuffle",),
        'tooltip' : '''\
                    Unload the bottom level of GF by wall walking
                    and jumping off creating antigravity and floating
                    down to unload. Walking into GTG or leaving GF to
                    Colossus is in logic with this trick. If shuffled
                    GF entrances, access to Archery area as adult must
                    also be met. Child can access always.
                    '''},
    '(Advanced) GF Archery Area without Gerudo Card as Adult': {
        'name'    : 'adv_gf_archery_no_card',
        'tags'    : ("Glitch","Adult","Entrance Shuffle",),
        'tooltip' : '''\
                    Day or night, pass the guard on the hill
                    towards archery with a backwalk movement.
                    '''},
    '(Glitch) GF Gate Skip Groundclip': {
        'name'    : 'glitch_gf_gate_groundclip',
        'tags'    : ("Glitch","Adult","Entrance Shuffle",),
        'tooltip' : '''\
                    Pass the gate from the ground level with a
                    double bomb hover groundclip as adult without
                    Gerudo Card. Can be done day or night.
                    '''},
    '(Advanced) TH Breakroom to Balcony as Child': {
        'name'    : 'adv_th_breakroom_to_balcony_child',
        'tags'    : ("Glitchless","Child","Entrance Shuffle",),
        'tooltip' : '''\
                    Jump from the breakroom to the balcony entrance
                    hallway with a damage boost and jumpslash to pass
                    the wall.
                    '''},
    '(Glitch) Spirit Hover': {
        'name'    : 'glitch_spirit_hover',
        'tags'    : ("Glitch","Adult","Entrance Shuffle","Spirit Temple",),
        'tooltip' : '''\
                    An iconic trick in OoT. This exists to allow it to be
                    considered in logic without general hovering also being
                    enabled. Logically expects the version with Hover Boots,
                    Bombs, and Chus.

                    This trick is not dependent on the ISG or Hovering tricks.
                    '''},
    '(Glitch) Colossus Grotto Weirdclip': {
        'name'    : 'glitch_colossus_grotto_weirdclip',
        'tags'    : ("Glitch","Adult","Bouldersanity","Entrance Shuffle",),
        'tooltip' : '''\
                    Separated trick from weirdshots and weirdslides
                    due to the sand adding complexity. Logic requires
                    chus.
                    '''},
    '(Glitch) Colossus Great Fairy Fountain without Explosives': {
        'name'    : 'glitch_colossus_fairy_no_explosives',
        'tags'    : ("Glitch","Adult","Entrance Shuffle","Colossus",),
        'tooltip' : '''\
                    Using a Hookshot Jump and some out of bounds Hover
                    Boots movement, it's possible to touch the load
                    for the Fairy Fountain without opening the wall.

                    Requires the Hookshot Jump glitch to be enabled.

                    This trick is super annoying because Leevers, kill them
                    to spawn the purple one which gives you a window to do it.
                    '''},
    '(Advanced) Market Night Baz and Sling': {
        'name'    : 'adv_market_night_baz_sling',
        'tags'    : ("Glitchless","Child","Entrance Shuffle","Market",),
        'tooltip' : '''\
                    Jumping from the crate over the door to access Bazaar
                    and Slingshot Gallery at night. Both are similar jumps
                    from a crate.
                    '''},
    '(Advanced) Market Night Potion': {
        'name'    : 'adv_market_night_potion',
        'tags'    : ("Glitchless","Child","Entrance Shuffle","Market",),
        'tooltip' : '''\
                    Same jumpslash from crate to reach Bazaar, except
                    do not walk into loading zone and instead walk
                    behind the houses into Potion shop load.
                    '''},
    '(Advanced) Market Night Mask Shop': {
        'name'    : 'adv_market_night_mask_shop',
        'tags'    : ("Glitchless","Child","Entrance Shuffle","Market",),
        'tooltip' : '''\
                    Watch the video. https://www.youtube.com/watch?v=17nWTtSuIYs
                    Jumpslash over door from Shooting
                    Gallery and walk through houses OoB to the shop.
                    This is tedious as it passes in front of the load to HC.
                    '''},
    '(Advanced) Market Day Treasure Chest Game': {
        'name'    : 'adv_market_day_tcg',
        'tags'    : ("Glitchless","Child","Entrance Shuffle","Market",),
        'tooltip' : '''\
                    Jumpslash over the Shooting Gallery door and walk behind
                    the Chu Bowling and houses around the edge OoB until
                    entering the load to the TCG.
                    '''},
    '(Glitch) ToT DoT Skip Child with Lunge Storage': {
        'name'    : 'glitch_dot_skip_child_lunge',
        'tags'    : ("Glitch","Child",),
        'tooltip' : '''\
                    Requires sword and shield, clip through DoT with a
                    lunge storage. There are many variations to
                    achieve.
                    '''},
    '(Glitch) ToT DoT Skip Child Swordless': {
        'name'    : 'glitch_dot_skip_child_swordless',
        'tags'    : ("Glitch","Child",),
        'tooltip' : '''\
                    Itemless DoT skip as child for fewer
                    requirements.
                    '''},
    '(Glitch) ToT DoT Skip Adult with Hover Recoil': {
        'name'    : 'glitch_dot_skip_adult_hover_recoil',
        'tags'    : ("Glitch","Adult",),
        'tooltip' : '''\
                    Adult DoT skip with a crouchstab recoil and
                    equipping hover boots to clip through the door
                    and float to the other side.
                    '''},
    '(Glitch) ToT DoT Skip Adult with Hovers and BGS': {
        'name'    : 'glitch_dot_skip_adult_hovers_bgs',
        'tags'    : ("Glitch","Adult",),
        'tooltip' : '''\
                    Easier DoT skip, crouchstab 3x with BGS and
                    hover boots equipped. Does work with Giant's Knife
                    as well but logic requires the BGS due to
                    overwritting progressives.
                    '''},
    '(Glitch) ToT DoT Skip Adult with BGS only': {
        'name'    : 'glitch_dot_skip_adult_bgs_only',
        'tags'    : ("Glitch","Adult",),
        'tooltip' : '''\
                    Skip DoT with only BGS. Pause buffering is
                    highly recommended and soft required due to
                    multiple frame perfect inputs.
                    '''},
    '(Glitch) HC Garden Ledge without Trade Item': {
        'name'    : 'glitch_hc_garden_no_trade',
        'tags'    : ("Glitch","Glitchless","Child",),
        'tooltip' : '''\
                    Access ZL check without Weird Egg using a damage boost
                    or megaflip, the other trick must also be enabled.

                    (Potential for softlock with letter shenanigans and is
                    in testing)
                    '''},
    '(Glitch) HC Fairy Fountain Wallwalk': {
        'name'    : 'glitch_hc_fairy_wallwalk',
        'tags'    : ("Glitch","Child","Entrance Shuffle","Bouldersanity",),
        'tooltip' : '''\
                    Wallwalk up the seam in front of the HC fairy,
                    and drop down into the load to bypass the boulder.
                    Useful in bouldersanity or no explosives.

                    Requires wallwalking and clipping to be enabled.
                    '''},
     '(Glitch) Treasure Chest Game with Suns Song and OI': {
        'name'    : 'glitch_tcg_suns',
        'tags'    : ("Glitch","Child",),
        'tooltip' : '''\
                    Perform Putaway OI (required to do this version)
                    with Suns Song to continue buying keys to reach
                    the final chest. This is not compatible with
                    shuffled TCG keys as you cannot buy more keys
                    from the front.
                    '''},
    '(Glitch) Kakariko Tower GS with ISG': {
        'name'    : 'glitch_kakariko_tower_gs_isg',
        'tags'    : ("Glitch","Child",),
        'tooltip' : '''\
                    Glitch alternative to the jumpslash trick in glitchless logic.
                    '''},
    '(Glitch) Kak to BotW Odie Clip': {
        'name'    : 'glitch_kak_botw_odie',
        'tags'    : ("Glitch","Adult","Entrance Shuffle",),
        'tooltip' : '''\
                    Itemless (sword and shield) clip into the
                    bottom of the well as adult.
                    '''},
    '(Glitch) Kak to BotW Ledge Clip Damage Boost': {
        'name'    : 'glitch_kak_botw_ledge',
        'tags'    : ("Glitch","Adult","Entrance Shuffle",),
        'tooltip' : '''\
                    Drop a chu, then perform a ledgeclip from the edge near windmill
                    entrance to clip into BotW as adult. Alternative to Odie clip.
                    '''},
    '(Glitch) BotW Blank A': {
        'name'    : 'glitch_botw_blank_a',
        'tags'    : ("Glitch","Child","Bottom of the Well",),
        'tooltip' : '''\
                    Softlock potential with Ocarina, only the
                    method with timestop considered because
                    we can\'t logically check for a lack of a
                    sword.
                    '''},
    '(Glitch) Kak Granny\'s House as Child': {
        'name'    : 'glitch_kak_child_granny',
        'tags'    : ("Glitch","Child","Entrance Shuffle",),
        'tooltip' : '''\
                    Enter Granny's house as child using some bomb movements.
                    There are several setups. Be cautious of N64 crashing OoB on
                    emulator.
                    '''},
    '(Glitch) Impa\'s House Front to Back': {
        'name'    : 'glitch_impas_cow_clip',
        'tags'    : ("Glitch","Adult",),
        'tooltip' : '''\
                    Ledgeclip fall into the cow gate from the front
                    of Impas house to reach Cow and freestanding item.
                    '''},
    '(Advanced) Kak Windmill HP Child Jumpslash': {
        'name'    : 'adv_kak_windmill_heart_child',
        'tags'    : ("Glitchless","Child",),
        'tooltip' : '''\
                    Child can reach the spinning windwill ledge with
                    a precise jumpslash timing and then jump to
                    the freestanding item to collect without boomerang.
                    '''},
    '(Advanced) Kakariko Tower GS with Boomerang': {
        'name'    : 'adv_kak_tower_gs_rang',
        'tags'    : ("Glitchless","Child","GS",),
        'tooltip' : '''\
                    By standing in a precise position, and manipulating
                    the Boomerang's flight path, it's possible to kill
                    the Gold Skulltula with the Boomerang, and then
                    climb up and collect the token.
                    '''},
    '(Advanced) Kakariko Backyard as Child with Jumpslash': {
        'name'    : 'adv_kak_backyard_night',
        'tags'    : ("Glitchless","Child",),
        'tooltip' : '''\
                    Doing a forward sidehop from the edge of
                    the fence outside the windmill allows you
                    to get close enough for a jumpslash to
                    reach on top of the fence of the Odd Potion
                    house, granting nighttime access to the
                    grotto area.
                    '''},
    '(Advanced) Graveyard Box HP Damage Boost': {
        'name'    : 'adv_graveyard_hp_damage_boost',
        'tags'    : ("Glitchless","Adult",),
        'tooltip' : '''\
                    Damage boost from the fence to the create
                    to reach the graveyard HP. Wallwalking from here to
                    Shadow is not included in logic.
                    '''},
    '(Glitch) Graveyard Royal Tomb Jumpslash Clip Child': {
        'name'    : 'glitch_rft_js_clip_child',
        'tags'    : ("Glitch","Child","Entrance Shuffle",),
        'tooltip' : '''\
                    Clip into the Royal Tomb as child to skip
                    Zeldas Lullaby requirement.
                    '''},
    '(Glitch) Royal Family Tomb Chest with Sticks': {
        'name'    : 'glitch_rft_chest_sticks',
        'tags'    : ("Glitch","Child","Adult",),
        'tooltip' : '''\
                    Using Flame Storage, it's possible to carry
                    the fire from the light torches near the
                    Sun's Song altar to light the front torches.
                    '''},
    '(Glitch) Graveyard to Shadow Early Hookshot Jump': {
        'name'    : 'glitch_graveyard_shadow_early_hookshot',
        'tags'    : ("Glitch","Adult","Entrance Shuffle",),
        'tooltip' : '''\
                    Hookshot jump from fence or Dampe Hut to
                    reach the wall, and walk to the loading zone
                    for Shadow Temple. This includes jumping over
                    the wall into the load passing the door.
                    '''},
    '(Glitch) Graveyard to Shadow Early Hover': {
        'name'    : 'glitch_graveyard_shadow_early_hover',
        'tags'    : ("Glitch","Adult","Entrance Shuffle",),
        'tooltip' : '''\
                    Without hookshot, hover onto the seam wall
                    to cross towards the Shadow Temple loading zone.
                    '''},
    '(Glitch) Graveyard to Shadow Early Bomb Push': {
        'name'    : 'glitch_graveyard_shadow_early_bomb_push',
        'tags'    : ("Glitch","Adult","Entrance Shuffle",),
        'tooltip' : '''\
                    If from the warp pad, without hookshot, use
                    triple bomb push to unload the door and bypass
                    into the dungeon. Adds nocturne as requirement
                    to reach the pad without hovering. Intermediate
                    option between no hookshot and full hover.
                    '''},
    '(Advanced) DMT Heart Piece Damageless Jump': {
        'name'    : 'adv_dmt_hp_jump',
        'tags'    : ("Glitch","Adult",),
        'tooltip' : '''\
                    With a well placed jump it's possible to force
                    Link to roll when he lands on top of the DC
                    entrance rather than break his legs.
                    '''},
    '(Glitch) DMT to Summit with Hookshot Jump': {
        'name'    : 'glitch_dmt_hookshot_jump',
        'tags'    : ("Glitch","Adult","Bouldersanity",),
        'tooltip' : '''\
                    Hookshot jump from below the boulders to reach the summit
                    access without having to cross boulders. Useful in
                    bouldersanity.
                    '''},
    '(Glitch) DMT to DC Groundclip': {
        'name'    : 'glitch_dmt_dc_groundclip',
        'tags'    : ("Glitch","Child","Entrance Shuffle",),
        'tooltip' : '''\
                    Sidehop groundclip as child from the bomb flower
                    platform to enter DC without strength or explosives.
                    '''},
    '(Glitch) DMT Explosiveless Magic': {
        'name'    : 'glitch_dmt_explosiveless_magic',
        'tags'    : ("Glitch","Adult","Entrance Shuffle",),
        'tooltip' : '''\
                    Perform a more precise lunge storage to enter
                    DMT Fairy without explosives.
                    '''},
    '(Advanced) Goron City LW Boulders with Bow': {
        'name'    : 'adv_gc_lw_boulders_bow',
        'tags'    : ("Glitchless","Adult",),
        'tooltip' : '''\
                    Using a precise shot, you can hit one of
                    the bomb flowers with an arrow through the
                    boulders when going from LW to Goron City
                    '''},
    '(Glitch) GC to DMC as Child': {
        'name'    : 'glitch_gc_dmc_child',
        'tags'    : ("Glitch","Child","Entrance Shuffle",),
        'tooltip' : '''\
                    Clip into the statue behind Darunia with a slash
                    and bombchu to enter DMT lower from GC as child.
                    '''},
    '(Glitch) Goron City Darunia\'s Room No Explosives': {
        'name'    : 'glitch_gc_darunia_no_explosives',
        'tags'    : ("Glitch","Adult","Entrance Shuffle",),
        'tooltip' : '''\
                    With a precise Ledge Clip it's possible to
                    enter Darunia's Room without stopping the rolling
                    goron or using explosives for other glitches.
                    '''},
    '(Glitch) DMC Fairy Fountain from Trail': {
        'name'    : 'glitch_dmc_fairy_from_trail',
        'tags'    : ("Glitch","Adult","Entrance Shuffle","Bouldersanity",),
        'tooltip' : '''\
                    Perform a megaflip from the DMC Upper to land
                    in the loading zone of DMC Fairy without
                    destroying the boulders.
                    '''},
    '(Glitch) LW Underwater Rupees without Diving or Rang': {
        'name'    : 'glitch_lw_uw_rupees',
        'tags'    : ("Glitch","Child","Lost Woods","Rupees",),
        'tooltip' : '''\
                    Requires Navi Dive or Child Aqua Escape to be enabled
                    as well. Using one of these techniques repeatedly,
                    it is possible to collect every rupee.
                    '''},
    '(Glitch) ZR to LW as Adult Ledge Clip': {
        'name'    : 'glitch_zr_lw_adult_ledge_clip',
        'tags'    : ("Glitch","Adult","Entrance Shuffle",),
        'tooltip' : '''\
                    Perform a ledgeclip and OoB swim to reach the LW
                    loading zone without iron boots or scales.
                    '''},
    '(Glitch) ZR to LW as Child Megasideohp': {
        'name'    : 'glitch_zr_lw_child_mega',
        'tags'    : ("Glitch","Child","Entrance Shuffle",),
        'tooltip' : '''\
                    Megaflip from the bridges to the LW loading zone to
                    bypass a Navi dive or scales as child
                    '''},
    '(Glitch) ZR to ZD Itemless': {
        'name'    : 'glitch_zr_zd_itemless',
        'tags'    : ("Glitch","Adult","Entrance Shuffle",),
        'tooltip' : '''\
                    Ladder clip from lower ZR and swim OoB to the ZD
                    entrance with minimal items. Watch a setup before
                    enabling this trick.
                    '''},
    '(Glitch) Zora\'s River upper GS with Boomerang': {
        'name'    : 'glitch_zr_upper_skull_rang',
        'tags'    : ("Glitch","Adult","Entrance Shuffle",),
        'tooltip' : '''\
                    Equip swapping Boomerang and doing 1 hover with a
                    setup allows you to get this skulltula without
                    Hookshot or a long hover.

                    Requires Equip Swap to be enabled, but
                    independent of Hovering and ISG glitches.
                    '''},
    '(Glitch) ZD Child OoB': {
        'name'    : 'glitch_zd_child_oob',
        'tags'    : ("Glitch","Child",),
        'tooltip' : '''\
                    Bombchu damage boost clip from KZ throne area. Enabling
                    this reaches both behind KZ and also to the LH entrance
                    by unloading the area near diving minigame.
                    '''},
    '(Glitch) ZD to ZF Ledge Cancel': {
        'name'    : 'glitch_zd_zf_ledge_cancel',
        'tags'    : ("Glitch","Child",),
        'tooltip' : '''\
                    Other variation of passing behind KZ when he is not
                    moved. Requires explosives.
                    '''},
    '(Glitch) ZD to ZF Burning Stick': {
        'name'    : 'glitch_zd_zf_burning_stick',
        'tags'    : ("Glitch","Child",),
        'tooltip' : '''\
                    Minimal/zero items for passing KZ when he is not moved.
                    Requires only a stick, which can be gotten from pots even
                    in potsanity (collect item first).
                    '''},
    '(Glitch) ZD Reverse KZ Adult': {
        'name'    : 'glitch_zd_reverse_kz_adult',
        'tags'    : ("Glitch","Child","Entrance Shuffle",),
        'tooltip' : '''\
                    If KZ is not moved, use longshot to clip through him by
                    hooking the torch. This just works.
                    '''},
    '(Glitch) ZD Reverse KZ Child': {
        'name'    : 'glitch_zd_reverse_kz_child',
        'tags'    : ("Glitch","Child","Entrance Shuffle",),
        'tooltip' : '''\
                    Perform a weirdslide as child with first person item
                    to cross under KZ if he is not moved.
                    '''},
    '(Advanced) ZF Enter Jabu Jumpslash': {
        'name'    : 'adv_jabu_no_fish',
        'tags'    : ("Glitchless","Child","Jabu Jabu's Belly", "Jabu Jabu's Belly MQ","Entrance Shuffle",),
        'tooltip' : '''\
                    Jump and then Jumpslash into the head for a glitchless access to Jabu.
                    This is not the jumpslash from the edge which is a recoil. It is logically equivalent.
                    '''},
    '(Glitch) ZF Child Wall GS with Hover': {
        'name'    : 'glitch_zf_child_gs_hover',
        'tags'    : ("Glitch","Child","Gold Skulltula","GS",),
        'tooltip' : '''\
                    Hovering off the skulltula after walking up
                    an invisible seam, you can get this without
                    Boomerang or explosives.

                    Does not require the ISG or Hovering glitches
                    to be enabled.
                    '''},
    '(Glitch) ZF Enter Jabu Adult with Hovers': {
        'name'    : 'glitch_adult_jabu_hovers',
        'tags'    : ("Glitch","Adult","Jabu Jabu's Belly", "Jabu Jabu's Belly MQ","Entrance Shuffle",),
        'tooltip' : '''\
                    Requires Bombs and Hover boots to do a megasidehop into
                    Jabu as Adult.

                    Does not require other glitches to be enabled.
                    '''},
    '(Glitch) ZF Enter Jabu Adult without Hovers': {
        'name'    : 'glitch_adult_jabu_no_hovers',
        'tags'    : ("Glitch","Adult","Jabu Jabu's Belly", "Jabu Jabu's Belly MQ","Entrance Shuffle",),
        'tooltip' : '''\
                    Removes the hover boots requirement, and requires
                    chus to enter Jabu as adult. Minimized item requirement.

                    Does not require other glitches to be enabled.
                    '''},
    '(Glitch) Child Ice Cavern Hover': {
        'name'    : 'glitch_child_ice',
        'tags'    : ("Glitch","Child","Ice Cavern", "Ice Cavern MQ","Entrance Shuffle",),
        'tooltip' : '''\
                    Child can hover into Ice Cavern Entrance.

                    Does not require other glitches to be enabled.
                    '''},
    '(Advanced) ZF Great Fairy Fountain without Explosives': {
        'name'    : 'adv_zf_fairy_no_explosives',
        'tags'    : ("Glitchless","Adult","Entrance Shuffle",),
        'tooltip' : '''\
                    Climb onto the wall, and walk along the floor
                    to the entrance for the Fairy Fountain. Jumpslash
                    into the load area from the top.
                    '''},
    '(Glitch) HF Web Grotto Groundclip': {
        'name'    : 'glitch_hf_web_groundclip',
        'tags'    : ("Glitch","Adult","Entrance Shuffle","Bouldersanity",),
        'tooltip' : '''\
                    If glitched damage value is not enabled, alternative is
                    a double bomb groundclip hover through the web to
                    access the locations.
                    '''},
    '(Advanced) HF Tektite Grotto with Rang': {
        'name'    : 'adv_tektite_hp_rang',
        'tags'    : ("Glitchless","Child","Adult",),
        'tooltip' : '''\
                    If standalone glitchless logic and no equipswap, this is enabled for child.
                    If equipswap is enabled, this works for child and adult.
                    '''},
    '(Glitch) Moustache Clip': {
        'name'    : 'glitch_moustache_clip',
        'tags'    : ("Glitch","Adult", "Entrance Shuffle",),
        'tooltip' : '''\
                    Clip into the Deku Tree as Adult with
                    a precise setup and some well timed sidehops.
                    '''},
    '(Advanced) Deku 231 with Hammer': {
        'name'    : 'adv_231_hammer',
        'tags'    : ("Glitchless","Adult","Deku Tree",),
        'tooltip' : '''\
                    Stun the dekus in the basement with Hammer
                    instead of shield, to reach Queen Gohma's room.
                    '''},
    '(Glitch) Deku Boss Door Skip': {
        'name'    : 'glitch_deku_boss_door_skip',
        'tags'    : ("Glitch","Adult","Deku Tree","Deku Tree MQ",),
        'tooltip' : '''\
                    Boss Door skip (or BK skip) for both vanilla and MQ from
                    the upper pillar room. Note that MQ skip is a different pillar
                    to jumpslash from.
                    '''},
    '(Glitch) MQ Deku SoT Chest with Hookshot': {
        'name'    : 'glitch_deku_mq_sot_skull_hook',
        'tags'    : ("Glitch","Adult","Deku Tree MQ",),
        'tooltip' : '''\
                    You can skip SoT and clip into the block to
                    obtain the chest past the rolling spike log with
                    only hookshot.
                    '''},
    '(Glitch) DC Beyond the Head without Explosives': {
        'name'    : 'glitch_dc_head_clip',
        'tags'    : ("Glitch","Adult","Dodongo's Cavern",),
        'tooltip' : '''\
                    This trick is both clipping into the head, as well
                    as jumping up to the doorframe to open the door to
                    reach beyond the head without explosives.
                    '''},
    '(Glitch) Death Hookshot Jumps': {
        'name'    : 'glitch_death_hookshot_jump',
        'tags'    : ("Glitch","Adult","Dodongo's Cavern","Dodongo's Cavern MQ",),
        'tooltip' : '''\
                    Death or Doom jump in DC and MQ DC to reach the upper bridge with
                    fairy revival. Alternative for backwards DC without GDV or explosives
                    or strength.
                    '''},
    '(Advanced) KD with Chus': {
        'name'    : 'adv_kd_chus',
        'tags'    : ("Glitchless","Adult","Dodongo's Cavern","Dodongo's Cavern MQ","King Dodongo",),
        'tooltip' : '''\
                    With a well timed backflip and chu pull,
                    Adult can down KD with only chus.
                    '''},
    '(Advanced) MQ DC Pass Boulder with Hoverboots Jump': {
        'name'    : 'adv_dc_mq_hoverboots_boulder_jump',
        'tags'    : ("Glitchless","Adult","Dodongo's Cavern MQ","Bouldersanity",),
        'tooltip' : '''\
                    If the boulders are inaccessible, you can cross the gap and jump
                    over with precise hoverboots timing. Similar to other
                    hoverboots over boulder jumps like DMT Fairy
                    or GC Boulder Maze.
                    '''},
    '(Advanced) MQ DC jump around stair Skulltulas': {
        'name'    : 'adv_dc_mq_stairs_skulltula_jump',
        'tags'    : ("Glitchless","Dodongo's Cavern MQ","Child"),
        'tooltip' : '''\
                    It's possible to jump around the Skulltulas
                    blocking the path above the stairs.
                    '''},
    '(Glitch) Jabu First Switch Hover': {
        'name'    : 'glitch_jabu_switch_hover',
        'tags'    : ("Glitch","Child","Adult","Jabu Jabu's Belly",),
        'tooltip' : '''\
                    Hover to reach the switch in the lobby of Jabu
                    to skip projectile requirement. For either age.
                    '''},
    '(Glitch) Jabu Compass Tentacle Skip': {
        'name'    : 'glitch_jabu_compass_skip_tentacle',
        'tags'    : ("Glitch","Adult","Jabu Jabu's Belly","Enemy Souls",),
        'tooltip' : '''\
                    Using explosives and hoverboots, damage boost
                    through the corner of Jabu wall and into the compass
                    room load without boomerang or souls.
                    '''},
    '(Glitch) Jabu Compass with Death': {
        'name'    : 'glitch_jabu_compass_with_death',
        'tags'    : ("Glitch","Child","Adult","Jabu Jabu's Belly","Enemy Souls",),
        'tooltip' : '''\
                    Death revival with Fairy to utilize i-frames and
                    pass the tentacle without boomerang or souls.
                    '''},
    '(Glitch) Jabu Jabu Biri Hover': {
        'name'    : 'glitch_jabu_biri_hover',
        'tags'    : ("Glitch","Child","Adult","Jabu Jabu's Belly",),
        'tooltip' : '''\
                    Hover to reach the rooms after Big Octo.
                    '''},
    '(Advanced) Jabu Jabu GS Near Boss with Jumpslash': {
        'name'    : 'adv_jabu_gs_near_boss_js',
        'tags'    : ("Child","Adult","Jabu Jabu's Belly",),
        'tooltip' : '''\
                    You can kill this Gold Skulltula through
                    the wall with a jumpslash and climb
                    the vines to collect it
                    '''},
    '(Glitch) Forest Temple Basement': {
        'name'    : 'glitch_forest_temple_basement',
        'tags'    : ("Glitch","Adult","Forest Temple","Forest Temple MQ",),
        'tooltip' : '''\
                    While the elevator can be skipped, logically access to
                    basement will require hoverboots and explosives.
                    This creates repeatable access using the megasidehop
                    method ignoring elevator.
                    '''},
    '(Glitch) Forest Basement GS Hover': {
        'name'    : 'glitch_forest_basement_gs',
        'tags'    : ("Glitch","Adult","Forest Temple",),
        'tooltip' : '''\
                    If in the basement, can hover to the GS from the chest.
                    Seprate from the can_hover group.
                    '''},
    '(Glitch) Forest Temple Boss Key Skip': {
        'name'    : 'glitch_forest_bk_skip',
        'tags'    : ("Glitch","Child","Adult","Forest Temple","Forest Temple MQ",),
        'tooltip' : '''\
                    Pick a variation, there are several. Logically will require
                    only sword and shield for adult.
                    Child requires bombchus for vineclip from the courtyard.
                    '''},
    '(Glitch) Fire Temple Boss Key Skip (Ledge clip)': {
        'name'    : 'glitch_fire_bk_skip_ledge',
        'tags'    : ("Glitch","Adult","Fire Temple","Fire Temple MQ",),
        'tooltip' : '''\
                    This BK skip requires all keys and traverse the dungeon to
                    where the shortcut block would be hammered. A ledgeclip and
                    jumpslash can be done in front of this block to fall
                    over the loading zone.
                    '''},
    '(Glitch) Fire Temple Boss Key Skip (Hover)': {
        'name'    : 'glitch_fire_bk_skip_hover',
        'tags'    : ("Glitch","Adult","Fire Temple","Fire Temple MQ",),
        'tooltip' : '''\
                    Hovering from in front of door over/under the loading
                    zone. This skips key requirements to traverse the
                    dungeon.
                    '''},
    '(Glitch) Fire Temple Child enemy room': {
        'name'    : 'glitch_fire_child_enemy_room',
        'tags'    : ("Glitch","Child","Fire Temple",),
        'tooltip' : '''\
                    Child can clip behind the hammer pillar without using
                    hammer. Enabling this trick requires bombchus.
                    '''},
    '(Glitch) Fire Temple Block skip': {
        'name'    : 'glitch_fire_block_skip',
        'tags'    : ("Glitch","Adult","Fire Temple",),
        'tooltip' : '''\
                    Similar requirements to the shortcuts being active in Fire.
                    Use of bomb or chu to clip through the block into the shortcut
                    area.
                    '''},
    '(Glitch) Fire Temple Scarecrow Hover': {
        'name'    : 'glitch_fire_scarecrow_hover',
        'tags'    : ("Glitch","Adult","Fire Temple",),
        'tooltip' : '''\
                    Hover to Piere with hover boots and bombchus to skip
                    needing access to Pierre or playing song.
                    '''},
    '(Glitch) MQ Fire Before Boss Torch puzzle with GDV': {
        'name'    : 'glitch_fire_mq_torch_puzzle',
        'tags'    : ("Glitch",),
        'tooltip' : '''\
                    Using glitched damage value and hover boots, you can
                    light all torches in the before boss room. Hover boots
                    is only to gain faster movement. After review it could be
                    adjusted with megaflips. The torches have a semi-long burn.
                    '''},
    '(Advanced) MQ Fire Boss Key Chest Flame Skip': {
        'name'    : 'adv_fire_mq_bk_chest_flame_skip',
        'tags'    : ("Advanced",),
        'tooltip' : '''\
                    Backflipping from a specific spot lets you avoid the fire
                    wall's hitbox, going over it while taking minimal damage.

                    You can also do the same by abusing invincibility frames
                    if not on ohko.
                    '''},
    '(Glitch) Water Temple Antigrav to Boss Key Area': {
        'name'    : 'glitch_water_bk_area_antigrav',
        'tags'    : ("Glitch","Adult","Water Temple","Water Temple MQ",),
        'tooltip' : '''\
                    After ledge clipping from the alcove, you can skip crossing
                    the gap before the locked north basement door by timing
                    a jumpslash to hit the ceiling as you fall through it
                    to gain extra distance and land on the spikes.
                    '''},
    '(Glitch) Water Temple Cutscene Dive to Eastern Column': {
        'name'    : 'glitch_water_bottle_dive',
        'tags'    : ("Glitch","Adult","Water Temple","Water Temple MQ",),
        'tooltip' : '''\
                    Using Hoverboots, and Fish or Bugs, it's possible to cutscene
                    dive to the eastern column without iron boots or ledge clipping
                    from the alcove.
                    '''},
    '(Glitch) Water Temple Ledge clip to South Basement': {
        'name'    : 'glitch_water_south_basement_clip',
        'tags'    : ("Glitch","Adult","Water Temple","Water Temple MQ",),
        'tooltip' : '''\
                    Access to alcove is base logic, ledgeclip OoB
                    and drop down to the south basement and float into
                    the loading zone. This does not require scale or
                    iron boots.
                    '''},
    '(Glitch) Water Temple Central Pillar with Torch Clip and Irons': {
        'name'    : 'glitch_water_central_pillar_with_torch_clip',
        'tags'    : ("Glitch","Adult","Water Temple","Water Temple MQ",),
        'tooltip' : '''\
                    Gives access to the Central Pillar with the water
                    raised by clipping out with a torch and swimming up
                    into the doorway.
                    '''},
    '(Glitch) Water Temple Torch Clips': {
        'name'    : 'glitch_water_torch_clip',
        'tags'    : ("Glitch","Adult","Water Temple","Water Temple MQ",),
        'tooltip' : '''\
                    Alternative clip OoB to reach areas by using hookshot
                    to clip thru the wall from the torch in the basement.
                    Access to OoB rooms such as dragon head.
                    '''},
    '(Glitch) Water Temple Dragon Head Cutscene Dive': {
        'name'    : 'glitch_water_dragon_cs_dive',
        'tags'    : ("Glitch","Adult","Water Temple",),
        'tooltip' : '''\
                    Using bombchus, explode the switch and dive during the explosion
                    to remove the iron boots requirement to reach the chest.
                    '''},
    '(Glitch) Water Temple Dragon Head Hover': {
        'name'    : 'glitch_water_dragon_hover',
        'tags'    : ("Glitch","Adult","Water Temple","Water Temple MQ",),
        'tooltip' : '''\
                    Hover to the alcove to reach the river chest in vanilla. In MQ
                    this skips the hookshot requirement to reach river locations.
                    '''},
    '(Glitch) Water Temple Song of Time Block Skip': {
        'name'    : 'glitch_water_sot_block_skip',
        'tags'    : ("Glitch","Adult","Water Temple","Water Temple MQ",),
        'tooltip' : '''\
                    Logically require explosives and a ledgeclip. This works the same
                    for vanilla and MQ to clip through the block. MQ is more tedious
                    because the gate can push you with collision. This does not access
                    enemies, only the chest.
                    '''},
    '(Glitch) Water Temple Boss Key Skip with Bombs': {
        'name'    : 'glitch_water_bk_skip_bombs',
        'tags'    : ("Glitch","Adult","Water Temple",),
        'tooltip' : '''\
                    Typical staircase hover, easier variation with bombs.
                    Can use either BGS or Master Sword. BGS is different
                    pull sword frame.
                    '''},
    '(Glitch) Water Temple Boss Key Skip with Chus': {
        'name'    : 'glitch_water_bk_skip_chus',
        'tags'    : ("Glitch","Adult","Water Temple",),
        'tooltip' : '''\
                    Alternative to bomb version, slightly more precise.
                    Separated out for preference style. Enable both
                    if no preference.
                    '''},
    '(Glitch) MQ Water BK Skip': {
        'name'    : 'glitch_water_mq_bk_skip',
        'tags'    : ("Glitch","Adult","Water Temple MQ",),
        'tooltip' : '''\
                    Best BK skip. Climb the longshot target and jump over the door. That's it.
                    '''},
    '(Glitch) MQ Water Temple Boss Key Room Spout Pit': {
        'name'    : 'glitch_water_mq_bk_pit',
        'tags'    : ("Glitch","Adult","Water Temple MQ",),
        'tooltip' : '''\
                    After doing the ledge clip from the alcove, you can swim out of bounds
                    and load the boss key room. You can skirt around
                    the gate in front of the boss key chest by swimming in some out of
                    bounds water.
                    '''},
    '(Advanced) Shadow Temple Double Damage Boosts': {
        'name'    : 'adv_shadow_double_boosts',
        'tags'    : ("Glitch","Adult","Shadow Temple",),
        'tooltip' : '''\
                    Hoverboots no longer needed to traverse Shadow Temple.
                    Damage boosts are not OHKO friendly. Double damage boosts
                    are needed to cross the gaps to reach Beamos room. Removes
                    requirement for hook.
                    '''},
    '(Glitch) Shadow Temple as Child': {
        'name'    : 'glitch_child_shadow',
        'tags'    : ("Glitch","Child","Shadow Temple",),
        'tooltip' : '''\
                    This is an all encompassing trick for access to multiple
                    rooms as child, including the boat. Most of the dungeon
                    would be accessible as child with hovering, clips, and
                    megaflips. MQ not included currently.
                    '''},
    '(Glitch) Shadow Temple Gate clip to Falling Spikes': {
        'name'    : 'glitch_shadow_gate_falling_spikes',
        'tags'    : ("Glitch","Child","Adult","Shadow Temple","Silver Rupee Shuffle",),
        'tooltip' : '''\
                    Negate the need for silver rupees or pouch with a roll through the sliver
                    of a gap between wall and gate. Works as both ages.
                    '''},
    '(Glitch) Shadow Boat Skull without Longshot Master': {
        'name'    : 'glitch_shadow_boat_skull',
        'tags'    : ("Glitch","Child","Adult","Shadow Temple",),
        'tooltip' : '''\
                    Various methods to reach the alcove near shadow boat without
                    Pierre or a longshot. Inclusions are:
                    vineclip as child, and megaflip superslide with hoverboots or hover
                    without hoverboots.
                    '''},
    '(Glitch) Shadow Boat Skull as Adult with Nothing': {
        'name'    : 'glitch_shadow_boat_skull_adult_nothing',
        'tags'    : ("Glitch","Adult","Shadow Temple",),
        'tooltip' : '''\
                    With gate clip, you can reach the skull and hearts with
                    only sword and shield, this is a separate trick from the
                    other with alternatives but more item requirements.
                    Enable both for more options.

                    Requires clipping as this also grants access to the boat.
                    '''},
    '(Glitch) Shadow Temple no Boat': {
        'name'    : 'glitch_shadow_no_Boat',
        'tags'    : ("Glitch","Adult","Shadow Temple",),
        'tooltip' : '''\
                    Hover down the slippery slopes with 50+ bombchus. This is a meme.
                    It does nothing.
                    '''},
    '(Glitch) Shadow Temple Before Boss Recovery Hearts Hovers': {
        'name'    : 'glitch_shadow_heart_chasm_hovers',
        'tags'    : ("Glitch","Adult","Shadow Temple",),
        'tooltip' : '''\
                    Hover to the recovery hearts without usable boomerang or
                    SoT.
                    '''},
    '(Glitch) Shadow Temple Boss Key Skip Boat Key': {
        'name'    : 'glitch_shadow_bk_skip_boat_key',
        'tags'    : ("Glitch","Shadow Temple","Shadow Temple MQ",),
        'tooltip' : '''\
                    This can be either the HESS or Superslide variation.
                    Item requirements are the same. Logically requires bombs
                    and hover boots. This goes directly from dead hand
                    into the boss loading zone.
                    '''},
    '(Glitch) Shadow Temple Boss Key Skip from Deadhand': {
        'name'    : 'glitch_shadow_bk_skip_deadhand',
        'tags'    : ("Glitch","Shadow Temple","Shadow Temple MQ",),
        'tooltip' : '''\
                    Alternative with minimal items, no hover boots.
                    Can megaflip or TSC from Dead hand to unloaded
                    pre-boss room. Then BK skip thru the unloaded door
                    with bombchu.
                    '''},
    '(Glitch) Shadow Temple Boss Key Skip pre-boss': {
        'name'    : 'glitch_shadow_bk_skip_boss',
        'tags'    : ("Glitch","Shadow Temple","Shadow Temple MQ",),
        'tooltip' : '''\
                    Same as before deadhand BK skip, except this is from the
                    loaded room before boss door. Logical access to this
                    room through the dungeon is required and all
                    small keys to have been acquired. Same BK skip with
                    bombchu.
                    '''},
    '(Glitch) Spirit Temple Child side as Adult': {
        'name'    : 'glitch_spirit_child_side_as_adult',
        'tags'    : ("Glitch","Adult","Spirit Temple",),
        'tooltip' : '''\
                    Allows Adult to reach the child side of spirit through either
                    a Hoverboots superslide or a TSC and megaflip. Both methods
                    also require their underlying glitches to be enabled.
                    '''},
    '(Glitch) Spirit Temple Adult side Block Skip': {
        'name'    : 'glitch_spirit_adult_block_skip',
        'tags'    : ("Glitch","Adult","Spirit Temple",),
        'tooltip' : '''\
                    Adult side clip is a Triple Slash Clip (TSC) or a superslide
                    based on the enabled grouped logic tricks.
                    '''},
    '(Glitch) Spirit Temple Child side Crawlspace skip as Adult': {
        'name'    : 'glitch_spirit_child_side_crawlspace_skip',
        'tags'    : ("Glitch","Adult","Spirit Temple",),
        'tooltip' : '''\
                    Allows Adult to skip the second crawlspace on the child side
                    to reach the child climb. Requires being able to do an Entrance
                    Point Glich and survive a void.
                    '''},
    '(Advanced) Spirit Compass with just Hoverboots': {
        'name'    : 'adv_spirit_compass_hoverboots_only',
        'tags'    : ("Glitchless","Adult","Spirit Temple",),
        'tooltip' : '''\
                    Glitchless movement to reach the compass chest without hookshot.
                    '''},
    '(Glitch) Spirit Hover': {
        'name'    : 'glitch_spirit_hover',
        'tags'    : ("Glitch","Adult","Spirit Temple",),
        'tooltip' : '''\
                    Spirit hover with bombchus and hover boots, and hookshot from
                    Colossus up to silver gauntlets hand.
                    If superslides are enabled, this also gives access to Mirror
                    Shield chest.
                    '''},
    '(Glitch) Spirit Temple Boss Key Skip Groundclip': {
        'name'    : 'glitch_spirit_bk_skip_groundclip',
        'tags'    : ("Glitch","Spirit Temple","Spirit Temple MQ",),
        'tooltip' : '''\
                    Megaflip or double bomb staircase to clip through
                    the boss door. The staircase is equivalent to the
                    boss key skip in Water Temple. This requires access
                    to the head from the top and mirror shield to melt
                    the face.
                    '''},
    '(Glitch) Spirit Temple Boss Key Skip Headclip': {
        'name'    : 'glitch_spirit_bk_skip_headclip',
        'tags'    : ("Glitch","Spirit Temple","Spirit Temple MQ",),
        'tooltip' : '''\
                    Headclip using explosives and hookshot to reach the
                    boss room directly from the main statue room instead
                    of key requirements.
                    '''},
    '(Advanced) MQ Spirit Temple Lobby Eye Switch without Explosives': {
        'name'    : 'adv_spirit_mq_lobby_eye',
        'tags'    : ("Glitchless","Spirit Temple MQ",),
        'tooltip' : '''\
                    Standing far enough away from a boulder removes its
                    collision, allowing you to hit things inside or
                    through them without exploding them.
                    '''},
     '(Advanced) MQ Spirit Temple Child Gibdo Eye Switch without Explosives': {
        'name'    : 'adv_spirit_mq_child_gibdo_eye',
        'tags'    : ("Glitchless","Spirit Temple MQ",),
        'tooltip' : '''\
                    Standing far enough away from a boulder removes its
                    collision, allowing you to hit things inside or
                    through them without exploding them.
                    '''},
    '(Glitch) MQ Spirit Temple Silver Block Skip': {
        'name'    : 'glitch_spirit_mq_silver_block_skip',
        'tags'    : ("Glitch","Spirit Temple MQ",),
        'tooltip' : '''\
                    With a precise setup, you can skip the silver block
                    in the upper hallway to the main room as adult
                    with a groundclip and hoverboots.
                    '''},
    '(Glitch) MQ Spirit Temple Ceiling Boulder Skip': {
        'name'    : 'glitch_spirit_mq_ceiling_boulder_skip',
        'tags'    : ("Glitch","Spirit Temple MQ",),
        'tooltip' : '''\
                    By targetting after shooting the Longshot, you can
                    disable the boulder's collision, allowing Link to
                    hit the hookshot target without exploding the boulder.
                    '''},
    '(Advanced) MQ Spirit Temple Lower Adult from Lobby': {
        'name'    : 'adv_spirit_mq_lower_adult_from_lobby',
        'tags'    : ("Advanced","Spirit Temple MQ","Adult"),
        'tooltip' : '''\
                    Using Hover Boots it's possible to conserve enough
                    momentum to pass through the water jet.
                    '''},
    '(Glitch) MQ Spirit Temple Lower Adult without Fire': {
        'name'    : 'glitch_spirit_mq_lower_adult_no_fire',
        'tags'    : ("Glitch","Spirit Temple MQ",),
        'tooltip' : '''\
                    With Glitch Damage Value and ISG, Hookshotting to the
                    tops of the torches will light them. Moving quickly,
                    you can light all three to open the door.
                    '''},
    '(Glitch) MQ Spirit Temple Symphony Room with just Lullaby': {
        'name'    : 'glitch_spirit_mq_symphony_lullaby',
        'tags'    : ("Glitch","Spirit Temple MQ",),
        'tooltip' : '''\
                    Using Time Stop from the Leever room, you can store
                    the music staff and reactivate it on the Lullaby
                    trigger in the Symphony Room, skipping every other
                    song.

                    To note, the staff will not reappear in the Leever
                    room if you've used it to open the door. To get the
                    staff back, you have to leave the dungeon entirely.
                    '''},
    '(Glitch) Ice Cavern Ledges Room as Child': {
        'name'    : 'glitch_ice_ledges_child',
        'tags'    : ("Glitch","Child","Ice Cavern",),
        'tooltip' : '''\
                    Use groundjumps and glitchless-style jumps to
                    climb the tall ledges.

                    In Vanilla, this goes to the map room and requires
                    the 5 silver rupees.

                    In MQ, this goes to the compass room.
                    '''},
    '(Advanced) Ice Cavern HP without Bottle': {
        'name'    : 'adv_ice_hp_no_bottle',
        'tags'    : ("Advanced","Adult","Ice Cavern",),
        'tooltip' : '''\
                    Bomb push into the ice to obtain the freestanding item.
                    This puts the trick directly into logic.
                    '''},
    '(Advanced) Ice Cavern Push Block Silver Rupee Jumpslash': {
        'name'    : 'adv_ice_push_block_silver',
        'tags'    : ("Glitch","Adult","Ice Cavern",),
        'tooltip' : '''\
                    Previously, a bottle is required to dispel the ice.
                    This allows for more usage of Blue Fire Arrows to traverse
                    Ice Cavern glitchlelssly.
                    '''},
    '(Glitch) Reverse Ice Cavern': {
        'name'    : 'glitch_reverse_ice',
        'tags'    : ("Glitch","Adult","Ice Cavern",),
        'tooltip' : '''\
                    Adult can backflip onto the crystal in the Freezard room lobby
                    to clip OoB and slide towards the back end of the past Iron
                    Boots chest. To go through the door, iron boots are required.
                    '''},
    '(Glitch) Void Warps (ToDo)': {
        'name'    : 'glitch_',
        'tags'    : ("Glitch",),
        'tooltip' : '''\
                    TBD
                    '''},
    '(Glitch) GTG Lobby Eye Switch Hover': {
        'name'    : 'glitch_gtg_lobby_eye',
        'tags'    : ("Glitch","Adult","Child","Gerudo Training Grounds","Glitched Damage Value",),
        'tooltip' : '''\
                    Obtaining glitched damage value, and hovering to the eye
                    switch to drop the chests without slingshot or bow.
                    '''},
    '(Glitch) GTG Vine Clips': {
        'name'    : 'glitch_gtg_vine_clip',
        'tags'    : ("Glitch","Adult","Child","Gerudo Training Grounds","Enemy Souls",),
        'tooltip' : '''\
                    Enabling this trick puts the entire maze into logic. This
                    also allows access to the open lava room without SoT or enemy
                    souls.
                    Both child and adult can vineclip (adult is sideways
                    vineclips).
                    '''},
    '(Advanced) GTG Pillar Jumps': {
        'name'    : 'adv_gtg_pillar_jumps',
        'tags'    : ("Advanced","Adult","Gerudo Training Grounds",),
        'tooltip' : '''\
                    Remove the logic requirement to have hover boots to cross
                    the pillars. With precise jumps it can be reached without
                    them.
                    '''},
    '(Advanced) GTG Burning Chest without Hammer': {
        'name'    : 'adv_gtg_burning_chest_without_hammer',
        'tags'    : ("Advanced","Child","Adult","Gerudo Training Grounds",),
        'tooltip' : '''\
                    Putting this chest into logic without excessive item
                    requirements. Not OHKO friendly as it requires taking
                    damage.
                    '''},
    '(Advanced) MQ GTG Enemy Rooms as child': {
        'name'    : 'adv_gtg_mq_enemy_rooms_as_child',
        'tags'    : ("Advanced","Child","Adult","Gerudo Training Grounds",),
        'tooltip' : '''\
                    Allows child to logically defeat the enemy rooms in
                    MQ GTG. This has no extra item requirements.
                    '''},
    '(Glitch) MQ GTG Blue Fire Wall Skip': {
        'name'    : 'glitch_gtg_mq_blue_fire_skip',
        'tags'    : ("Glitch","Child","Adult","Gerudo Training Grounds",),
        'tooltip' : '''\
                    Child can clip through with lunge storage and a jumpslash.
                    Adult needs to hess into the corner and have Hover Boots
                    to go back in bounds.
                    '''},
    '(Glitch) Ganon\'s Tower Rainbow Bridge Skip': {
        'name'    : 'glitch_igc_rainbow_bridge',
        'tags'    : ("Glitch","Adult","Inside Ganon's Castle","Rainbow Bridge",),
        'tooltip' : '''\
                    Allows for logical use of skipping the Rainbow Bridge
                    by hovering.  This is independent of the Hovering and ISG
                    tricks.

                    Enabling this will not affect path hints or WotH.
                    '''},
    '(Glitch) Ganon\'s Tower Trials Skip': {
        'name'    : 'glitch_igc_trials_skip',
        'tags'    : ("Glitch","Adult","Inside Ganon's Castle",),
        'tooltip' : '''\
                    Includes the hover in the main room of both
                    vanilla and MQ, and for MQ also includes
                    the torch clip from the initial hallway.
                    '''},
    '(Glitch) Ganon\'s Tower Trials Skip from Spirit Trial': {
        'name'    : 'glitch_igc_trials_skip_spirit_trial',
        'tags'    : ("Glitch","Adult","Inside Ganon's Castle",),
        'tooltip' : '''\
                    Pushing the armos to the door creates a jumpslash clip
                    to clip out into the lobby area and can walk up the stairs,
                    across the carpet and into the loading zone. Utilize sound cues.
                    If trials are active, the colored beams help guide the way.
                    '''},
    '(Advanced) Shadow Trial First Gap Without Fire': {
        'name'    : 'adv_shadow_trial_no_fire_gap',
        'tags'    : ("Advanced","Adult","Inside Ganon's Castle",),
        'tooltip' : '''\
                    Hammer recoil hoverboost from the door to the torch, and then recoil
                    boost ending with bombchu damage boost to the likelike. Removes
                    logic requirement for longshot or fire source.
                    '''},
    '(Glitch) Shadow Trial Hess': {
        'name'    : 'glitch_shadow_trial_hess',
        'tags'    : ("Glitch","Adult","Inside Ganon's Castle",),
        'tooltip' : '''\
                    HESS from the door with hover boots to the torch, then to likelike.
                    Removes logic requirement for longshot or fire source.
                    '''},
    '(Glitch) Fire Trial Pillar Silver without Gauntlets': {
        'name'    : 'glitch_fire_trial_pillar_silver',
        'tags'    : ("Glitch","Adult","Inside Ganon's Castle",),
        'tooltip' : '''\
                    Skip strength 3 requirement to obtain the silver rupee under
                    the block. Logic does not require hover boots but there are
                    variations that can make it easier if they are available.
                    '''},
    '(Advanced) Fire Trial Longshot Skip': {
        'name'    : 'adv_fire_trial_longshot_skip',
        'tags'    : ("Glitchless","Adult","Inside Ganon's Castle",),
        'tooltip' : '''\
                    Damage boost hoverslide to the door without the need
                    for the Longshot. Enabling damage boosts in general
                    is not required, this trick stands alone.
                    '''}
}
