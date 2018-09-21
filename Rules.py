import collections
import logging


def set_rules(world):
    global_rules(world)

    if world.bridge == 'medallions':
        # require all medallions to form the bridge
        set_rule(world.get_entrance('Rainbow Bridge'), lambda state: state.has('Forest Medallion') and state.has('Fire Medallion') and state.has('Water Medallion') and state.has('Shadow Medallion') and state.has('Spirit Medallion') and state.has('Light Medallion'))
    elif world.bridge == 'vanilla':
        # require only what vanilla did to form the bridge
        set_rule(world.get_entrance('Rainbow Bridge'), lambda state: state.has('Light Arrows') and state.has('Shadow Medallion') and state.has('Spirit Medallion'))
    elif world.bridge == 'dungeons':
        # require all medallions and stones to form the bridge
        set_rule(world.get_entrance('Rainbow Bridge'), lambda state: state.has('Forest Medallion') and state.has('Fire Medallion') and state.has('Water Medallion') and state.has('Shadow Medallion') and state.has('Spirit Medallion') and state.has('Light Medallion') and state.has('Kokiri Emerald') and state.has('Goron Ruby') and state.has('Zora Sapphire'))


def set_rule(spot, rule):
    spot.access_rule = rule

def set_always_allow(spot, rule):
    spot.always_allow = rule


def add_rule(spot, rule, combine='and'):
    old_rule = spot.access_rule
    if combine == 'or':
        spot.access_rule = lambda state: rule(state) or old_rule(state)
    else:
        spot.access_rule = lambda state: rule(state) and old_rule(state)

def add_item_rule(spot, rule, combine='and'):
    old_rule = spot.item_rule
    if combine == 'or':
        spot.item_rule = lambda item: rule(item) or old_rule(item)
    else:
        spot.item_rule = lambda item: rule(item) and old_rule(item)

def forbid_item(location, item):
    old_rule = location.item_rule
    location.item_rule = lambda i: i.name != item and old_rule(i)


def item_in_locations(state, item, locations):
    for location in locations:
        if item_name(state, location) == item:
            return True
    return False

def item_name(state, location):
    location = state.world.get_location(location)
    if location.item is None:
        return None
    return location.item.name


def global_rules(world):

    expected_skulltulas = world.logic_skulltulas

    # ganon can only carry triforce
    world.get_location('Ganon').item_rule = lambda item: item.name == 'Triforce'

    # these are default save&quit points and always accessible
    world.get_region('Links House').can_reach = lambda state: True

	# dungeon requirements (including gold skulltulas)
    dung_rules_dt0(world)
    dung_rules_dc0(world)
    dung_rules_jb0(world)
    dung_rules_fot0(world)
    dung_rules_fit0(world)
    dung_rules_wt0(world)
    dung_rules_spt0(world)
    dung_rules_sht0(world)
    dung_rules_bw0(world)
    dung_rules_ic0(world)
    dung_rules_gtg0(world)
    dung_rules_gc0(world)

    # overworld requirements
    set_rule(world.get_location('Deku Baba Sticks'), lambda state: (state.has('Kokiri Sword') and state.has_deku_shield()) or (world.open_forest and (state.is_adult() or state.has('Kokiri Sword') or state.has('Boomerang'))))
    set_rule(world.get_location('Deku Baba Nuts'), lambda state: (state.has('Kokiri Sword') and state.has_deku_shield()) or (world.open_forest and (state.is_adult() or state.has_slingshot() or state.has_explosives() or state.can_child_melee_attack() or state.can_cast_dins_fire())))
    set_rule(world.get_entrance('Deku Tree'), lambda state: (state.has('Kokiri Sword') and state.has_deku_shield()) or world.open_forest)
    set_rule(world.get_entrance('Lost Woods Bridge'), lambda state: state.can_leave_forest())
    set_rule(world.get_location('Skull Kid'), lambda state: state.can_play('Sarias Song'))
    set_rule(world.get_location('Ocarina Memory Game'), lambda state: (not world.logic_no_memory_game) and state.has_ocarina())
    set_rule(world.get_location('Target in Woods'), lambda state: state.has_slingshot())
    set_rule(world.get_location('Deku Theater Skull Mask'), lambda state: (not world.logic_no_trade_skull_mask) and state.has('Zeldas Letter'))
    set_rule(world.get_location('Deku Theater Mask of Truth'), lambda state: (not world.logic_no_trade_mask_of_truth) and (state.has('Zeldas Letter') and state.can_play('Sarias Song') and state.has('Kokiri Emerald') and state.has('Goron Ruby') and state.has('Zora Sapphire') and state.guarantee_hint())) #Must befriend Skull Kid to sell Skull Mask, all stones to spawn running man.
    set_rule(world.get_location('Anju as Adult'), lambda state: state.is_adult())
    set_rule(world.get_location('Man on Roof'), lambda state: world.logic_man_on_roof or (state.has('Progressive Hookshot') and state.is_adult()))
    set_rule(world.get_location('10 Gold Skulltulla Reward'), lambda state: (expected_skulltulas >= 10) and state.has('Gold Skulltulla Token', 10))
    set_rule(world.get_location('20 Gold Skulltulla Reward'), lambda state: (expected_skulltulas >= 20) and state.has('Gold Skulltulla Token', 20))
    set_rule(world.get_location('30 Gold Skulltulla Reward'), lambda state: (expected_skulltulas >= 30) and state.has('Gold Skulltulla Token', 30) and state.guarantee_hint())
    set_rule(world.get_location('40 Gold Skulltulla Reward'), lambda state: (expected_skulltulas >= 40) and state.has('Gold Skulltulla Token', 40) and state.guarantee_hint())
    set_rule(world.get_location('50 Gold Skulltulla Reward'), lambda state: (expected_skulltulas >= 50) and state.has('Gold Skulltulla Token', 50) and state.guarantee_hint())
    set_rule(world.get_location('Heart Piece Grave Chest'), lambda state: state.can_play('Suns Song'))
    set_rule(world.get_entrance('Composer Grave'), lambda state: state.can_play('Zeldas Lullaby'))
    set_rule(world.get_location('Song from Composer Grave'), lambda state: state.is_adult() or (state.has_slingshot() or state.has('Boomerang') or state.has_explosives() or state.can_child_melee_attack()))
    set_rule(world.get_location('Composer Grave Chest'), lambda state: state.has_fire_source())
    set_rule(world.get_entrance('Bottom of the Well'), lambda state: state.can_play('Song of Storms') and (world.dungeon_mq['BW'] or (state.has_slingshot() or state.has_explosives() or state.can_child_melee_attack() or state.can_cast_dins_fire())))
    set_rule(world.get_entrance('Death Mountain Entrance'), lambda state: state.has('Zeldas Letter') or state.is_adult() or world.open_kakariko)
    # In the future, 'Buy Fairy\'s Spirit' should be changed to has_fairy() so that other potential sources of fairies could be added.
    set_rule(world.get_location('DM Trail Freestanding PoH'), lambda state: world.open_kakariko or (world.difficulty != 'ohko') or state.has('Zeldas Letter') or state.can_blast_or_smash() or (state.can_cast_dins_fire() or (state.has('Nayrus Love') and state.has('Magic Meter'))) or state.has_bow() or state.has('Progressive Strength Upgrade') or state.has('Buy Fairy\'s Spirit') or state.has('Hover Boots'))
    set_rule(world.get_location('Death Mountain Bombable Chest'), lambda state: state.can_blast_or_smash())
    set_rule(world.get_location('Biggoron'), lambda state: (not world.logic_no_trade_biggoron) and state.is_adult() and state.can_finish_adult_trades() and state.guarantee_hint())
    set_rule(world.get_location('Goron City Leftmost Maze Chest'), lambda state: state.is_adult() and (state.has('Progressive Strength Upgrade', 2) or state.has('Hammer')))
    set_rule(world.get_location('Goron City Left Maze Chest'), lambda state: state.can_blast_or_smash() or (state.has('Progressive Strength Upgrade', 2) and state.is_adult()))
    set_rule(world.get_location('Goron City Right Maze Chest'), lambda state: state.can_blast_or_smash() or (state.has('Progressive Strength Upgrade', 2) and state.is_adult()))
    set_rule(world.get_location('Rolling Goron as Child'), lambda state: state.has('Bomb Bag') and state.has_explosives())
    set_rule(world.get_location('Goron City Pot Freestanding PoH'), lambda state: (state.has_bombs() or state.has('Progressive Strength Upgrade')) and ((state.can_play('Zeldas Lullaby') and state.has_sticks()) or state.can_cast_dins_fire()))
    set_rule(world.get_entrance('Darunias Chamber'), lambda state: state.can_play('Zeldas Lullaby'))
    set_rule(world.get_location('Darunias Joy'), lambda state: state.can_play('Sarias Song'))
    set_rule(world.get_location('Goron City Stick Pot'), lambda state: world.open_kakariko or state.has('Zeldas Letter') or state.has_explosives() or (state.has('Dins Fire') and state.has('Magic Meter')))
    set_rule(world.get_entrance('Goron City from Woods'), lambda state: (state.can_blast_or_smash() or state.can_cast_dins_fire() or ((state.has_bow() or state.has('Progressive Strength Upgrade')) and state.is_adult())) and state.can_leave_forest())
    set_rule(world.get_location('Song from Saria'), lambda state: state.has('Zeldas Letter'))
    set_rule(world.get_entrance('Mountain Summit Fairy'), lambda state: state.can_blast_or_smash())
    set_rule(world.get_location('Crater Fairy Reward'), lambda state: state.can_play('Zeldas Lullaby'))
    set_rule(world.get_location('Mountain Summit Fairy Reward'), lambda state: state.can_play('Zeldas Lullaby'))
    set_rule(world.get_entrance('Mountain Crater Entrance'), lambda state: state.can_blast_or_smash())
    set_rule(world.get_entrance('Hyrule Castle Fairy'), lambda state: state.has_explosives())
    set_rule(world.get_location('Hyrule Castle Fairy Reward'), lambda state: state.can_play('Zeldas Lullaby'))
    set_rule(world.get_entrance('Hyrule Castle Garden'), lambda state: state.has('Weird Egg') or (not world.shuffle_weird_egg))
    set_rule(world.get_entrance('Ganons Castle Grounds'), lambda state: state.is_adult())
    set_rule(world.get_entrance('Ganons Castle Fairy'), lambda state: state.has('Progressive Strength Upgrade', 3))
    set_rule(world.get_location('Ganons Castle Fairy Reward'), lambda state: state.can_play('Zeldas Lullaby'))
    set_rule(world.get_location('Bombchu Bowling Bomb Bag'), lambda state: state.has_bombchus())
    set_rule(world.get_location('Bombchu Bowling Piece of Heart'), lambda state: state.has_bombchus())
    set_rule(world.get_location('Adult Shooting Gallery'), lambda state: state.has('Bow') and state.is_adult())
    set_rule(world.get_location('10 Big Poes'), lambda state: (not world.logic_no_big_poes) and (state.has_bow() and state.has('Epona') and state.has_bottle() and state.is_adult() and state.guarantee_hint()))
    set_rule(world.get_location('Treasure Chest Game'), lambda state: state.has('Lens of Truth') and state.has('Magic Meter'))
    set_rule(world.get_entrance('Lost Woods Dive Warp'), lambda state: state.can_dive() and state.can_leave_forest())
    set_rule(world.get_entrance('Zora River Dive Warp'), lambda state: state.can_dive())
    set_rule(world.get_entrance('Lake Hylia Dive Warp'), lambda state: state.can_dive())
    set_rule(world.get_entrance('Zoras Domain Dive Warp'), lambda state: state.can_dive())
    set_rule(world.get_entrance('Zora River Waterfall'), lambda state: state.can_play('Zeldas Lullaby') or world.logic_zora_with_cucco)
    set_rule(world.get_entrance('Zora River Rocks'), lambda state: state.has_explosives())
    set_rule(world.get_location('Zora River Lower Freestanding PoH'), lambda state: state.has_explosives() or state.has('Progressive Scale') or (state.has('Hover Boots') and state.is_adult()))
    set_rule(world.get_location('Zora River Upper Freestanding PoH'), lambda state: state.has_explosives() or state.has('Progressive Scale') or (state.has('Hover Boots') and state.is_adult()))
    set_rule(world.get_location('Frog Ocarina Game'), lambda state: state.can_play('Zeldas Lullaby') and state.can_play('Sarias Song') and state.can_play('Suns Song') and state.can_play('Eponas Song') and state.can_play('Song of Time') and state.can_play('Song of Storms'))
    set_rule(world.get_location('Frogs in the Rain'), lambda state: state.can_play('Song of Storms'))
    set_rule(world.get_location('Underwater Bottle'), lambda state: state.can_dive())
    set_rule(world.get_location('King Zora Moves'), lambda state: state.has('Bottle with Letter'))
    set_rule(world.get_entrance('Behind King Zora'), lambda state: state.has('Bottle with Letter'))
    set_rule(world.get_entrance('Zora River Adult'), lambda state: state.is_adult())
    set_rule(world.get_entrance('Zoras Domain Adult Access'), lambda state: state.can_play('Zeldas Lullaby') or (state.has('Hover Boots') and world.logic_zora_with_hovers))
    set_rule(world.get_entrance('Zoras Fountain Adult Access'), lambda state: state.can_reach('Zoras Fountain'))
    set_rule(world.get_location('Zoras Domain Torch Run'), lambda state: state.has_sticks())
    set_rule(world.get_entrance('Jabu Jabus Belly'), lambda state: state.has_bottle())
    set_rule(world.get_entrance('Zoras Fountain Fairy'), lambda state: state.has_explosives())
    set_rule(world.get_location('Zoras Fountain Fairy Reward'), lambda state: state.can_play('Zeldas Lullaby'))
    set_rule(world.get_location('Ocarina of Time'), lambda state: state.has('Kokiri Emerald') and state.has('Goron Ruby') and state.has('Zora Sapphire') and state.guarantee_hint())
    set_rule(world.get_location('Song from Ocarina of Time'), lambda state: state.has('Kokiri Emerald') and state.has('Goron Ruby') and state.has('Zora Sapphire') and state.guarantee_hint())
    set_rule(world.get_entrance('Door of Time'), lambda state: state.can_play('Song of Time') or world.open_door_of_time)
    set_rule(world.get_location('Talons Chickens'), lambda state: state.has('Zeldas Letter'))
    set_rule(world.get_location('Song from Malon'), lambda state: state.has('Zeldas Letter') and state.has_ocarina())
    set_rule(world.get_location('Epona'), lambda state: state.can_play('Eponas Song') and state.is_adult())
    set_rule(world.get_entrance('Adult Forest Warp Pad'), lambda state: state.can_play('Minuet of Forest') and state.is_adult())
    set_rule(world.get_entrance('Child Forest Warp Pad'), lambda state: state.can_play('Minuet of Forest'))
    set_rule(world.get_entrance('Adult Meadow Access'), lambda state: state.can_play('Sarias Song') and state.is_adult())
    set_rule(world.get_entrance('Forest Temple Entrance'), lambda state: state.has('Progressive Hookshot') and state.is_adult())
    set_rule(world.get_entrance('Dampes Grave'), lambda state: state.is_adult())
    set_rule(world.get_location('Dampe Race Freestanding PoH'), lambda state: not world.logic_no_second_dampe_race)
    set_rule(world.get_location('Graveyard Freestanding PoH'), lambda state: state.is_adult() and (state.has('Magic Bean') or state.has('Progressive Hookshot', 2)))
    set_rule(world.get_location('Song at Windmill'), lambda state: state.is_adult() and state.has_ocarina())
    set_rule(world.get_location('Windmill Freestanding PoH'), lambda state: (state.is_adult() and ( world.logic_windmill_hp or state.can_play('Song of Time') )) or state.has('Boomerang'))
    set_rule(world.get_entrance('Temple Warp Pad'), lambda state: state.can_play('Prelude of Light') and state.can_leave_forest())
    set_rule(world.get_location('Sheik at Temple'), lambda state: state.has('Forest Medallion') and state.is_adult())
    set_rule(world.get_location('Diving in the Lab'), lambda state: state.has('Progressive Scale', 2))
    set_rule(world.get_location('Child Fishing'), lambda state: (not world.logic_no_child_fishing) and state.has('Kokiri Sword'))
    set_rule(world.get_location('Adult Fishing'), lambda state: (not world.logic_no_adult_fishing) and state.is_adult() and ((state.has('Progressive Hookshot') and state.has_ocarina()) or state.has('Magic Bean') or state.can_reach(world.get_location('Morpha'))))
    set_rule(world.get_location('Lake Hylia Freestanding PoH'), lambda state: state.is_adult() and ((state.has('Progressive Hookshot') and state.has_ocarina()) or state.has('Magic Bean')))
    set_rule(world.get_location('Lake Hylia Sun'), lambda state: ((state.has('Progressive Hookshot', 2) and state.has_ocarina()) or state.can_reach(world.get_location('Morpha'))) and state.has_bow() and state.is_adult())
    set_rule(world.get_entrance('Crater Hover Boots'), lambda state: state.is_adult() and state.has('Hover Boots'))
    set_rule(world.get_entrance('Crater Ascent'), lambda state: state.is_adult())
    set_rule(world.get_entrance('Crater Scarecrow'), lambda state: state.is_adult() and state.has_ocarina() and state.has('Progressive Hookshot', 2))
    set_rule(world.get_entrance('Crater Bridge'), lambda state: state.is_adult() and (state.has('Hover Boots') or state.has('Progressive Hookshot')))
    set_rule(world.get_entrance('Crater Bridge Reverse'), lambda state: state.is_adult() and (state.has('Hover Boots') or state.has('Progressive Hookshot') or state.has('Magic Bean')))
    set_rule(world.get_entrance('Crater Warp Pad'), lambda state: state.can_play('Bolero of Fire') and state.can_leave_forest())
    set_rule(world.get_entrance('Crater Fairy'), lambda state: state.is_adult() and state.has('Hammer'))
    set_rule(world.get_location('DM Crater Volcano Freestanding PoH'), lambda state: state.is_adult() and ( (state.has('Magic Bean') and state.can_play('Bolero of Fire')) or (world.logic_crater_bean_hp_with_hovers and state.has('Hover Boots')) ) )
    set_rule(world.get_entrance('Fire Temple Entrance'), lambda state: state.is_adult() and (world.logic_fewer_tunic_requirements or state.has_GoronTunic()))
    set_rule(world.get_location('Sheik in Crater'), lambda state: state.is_adult())
    set_rule(world.get_location('Link the Goron'), lambda state: state.is_adult() and (state.has('Progressive Strength Upgrade') or state.has_explosives() or state.has_bow()))
    set_rule(world.get_entrance('Crater Access'), lambda state: state.is_adult() and (state.has('Progressive Strength Upgrade') or state.has_explosives() or state.has_bow()))
    set_rule(world.get_entrance('Goron Shop'), lambda state: state.has_explosives() or state.has('Progressive Strength') or (state.has_bow() and state.is_adult()) or state.can_cast_dins_fire() or ((state.has('Zeldas Letter') or world.open_kakariko or (state.has('Hammer') and state.is_adult())) and (state.can_play('Zeldas Lullaby') and state.has_sticks())))
    set_rule(world.get_entrance('Lake Warp Pad'), lambda state: state.can_play('Serenade of Water') and state.can_leave_forest())
    set_rule(world.get_location('King Zora Thawed'), lambda state: state.has_blue_fire())
    set_rule(world.get_entrance('Zora Shop Adult Access'), lambda state: state.has_blue_fire())
    set_rule(world.get_location('Zoras Fountain Bottom Freestanding PoH'), lambda state: state.has('Iron Boots') and (world.logic_fewer_tunic_requirements or state.has_ZoraTunic()))
    set_rule(world.get_entrance('Water Temple Entrance'), lambda state: state.is_adult() and state.has('Iron Boots') and state.has('Progressive Hookshot') and (world.logic_fewer_tunic_requirements or state.has_ZoraTunic()))
    set_rule(world.get_location('Sheik in Kakariko'), lambda state: state.is_adult() and state.has('Forest Medallion') and state.has('Fire Medallion') and state.has('Water Medallion'))
    set_rule(world.get_entrance('Kakariko Potion Shop Front'), lambda state: state.is_adult())
    set_rule(world.get_entrance('Kakariko Potion Shop Back'), lambda state: state.is_adult())
    set_rule(world.get_entrance('Kakariko Bazaar'), lambda state: state.is_adult())
    set_rule(world.get_entrance('Graveyard Warp Pad'), lambda state: state.can_play('Nocturne of Shadow') and state.can_leave_forest())
    set_rule(world.get_entrance('Shadow Temple Entrance'), lambda state: state.can_cast_dins_fire() and state.can_see_with_lens() and state.is_adult() and (state.has('Hover Boots') or state.has('Progressive Hookshot')))
    set_rule(world.get_entrance('Bridge Crossing'), lambda state: (state.has('Epona') or state.has('Progressive Hookshot', 2) or world.gerudo_fortress == 'open') and state.is_adult())
    set_rule(world.get_location('Gerudo Valley Hammer Rocks Chest'), lambda state: state.has('Hammer') and state.is_adult())
    set_rule(world.get_location('Gerudo Fortress North F2 Carpenter'), lambda state: (state.has_bow() or state.has('Progressive Hookshot') or state.has('Hover Boots')) and state.is_adult())
    set_rule(world.get_location('Gerudo Fortress Carpenter Rescue'), lambda state: ( (world.gerudo_fortress == 'normal' and state.has('Small Key (Gerudo Fortress)', 4) and (state.has_bow() or state.has('Progressive Hookshot') or state.has('Hover Boots'))) or (world.gerudo_fortress == 'fast' and state.has('Small Key (Gerudo Fortress)', 1)) or world.gerudo_fortress == 'open') and state.is_adult())
    set_rule(world.get_location('Gerudo Fortress Membership Card'), lambda state: ( (world.gerudo_fortress == 'normal' and state.has('Small Key (Gerudo Fortress)', 4) and (state.has_bow() or state.has('Progressive Hookshot') or state.has('Hover Boots'))) or (world.gerudo_fortress == 'fast' and state.has('Small Key (Gerudo Fortress)', 1)) or world.gerudo_fortress == 'open') and state.is_adult())
    set_rule(world.get_entrance('Gerudo Training Grounds Entrance'), lambda state: state.has('Carpenter Rescue') and state.has('Gerudo Membership Card') and state.is_adult())
    set_rule(world.get_entrance('Haunted Wasteland Entrance'), lambda state: state.has('Carpenter Rescue') and state.is_adult() and (state.has('Hover Boots') or state.has('Progressive Hookshot', 2)))
    set_rule(world.get_entrance('Haunted Wasteland Crossing'), lambda state: (world.logic_lens == 'chest') or (state.has('Lens of Truth') and state.has('Magic Meter')))
    set_rule(world.get_entrance('Colossus Warp Pad'), lambda state: state.can_play('Requiem of Spirit') and state.can_leave_forest())
    set_rule(world.get_entrance('Colossus Fairy'), lambda state: state.has_explosives())
    set_rule(world.get_location('Colossus Freestanding PoH'), lambda state: state.can_play('Requiem of Spirit') and state.has('Magic Bean') and state.is_adult())
    set_rule(world.get_location('Desert Colossus Fairy Reward'), lambda state: state.can_play('Zeldas Lullaby'))
    set_rule(world.get_location('Gerudo Fortress Rooftop Chest'), lambda state: (state.has('Hover Boots') or (state.has('Progressive Hookshot') and state.has_ocarina()) or (state.has('Progressive Hookshot', 2))) and state.is_adult())
    set_rule(world.get_location('Horseback Archery 1000 Points'), lambda state: state.has('Carpenter Rescue') and state.has('Epona') and state.has('Bow') and state.is_adult())
    set_rule(world.get_location('Horseback Archery 1500 Points'), lambda state: (not world.logic_no_1500_archery) and (state.has('Carpenter Rescue') and state.has('Epona') and state.has('Bow') and state.is_adult()))
    set_rule(world.get_location('Haunted Wasteland Structure Chest'), lambda state: state.has_fire_source())
    set_rule(world.get_location('Zelda'), lambda state: state.has('Shadow Medallion') and state.has('Spirit Medallion') and state.is_adult())
    set_rule(world.get_location('Ganon'), lambda state: (state.has('Boss Key (Ganons Castle)') or world.unlocked_ganondorf) and state.can_shoot_light_arrows())
    set_rule(world.get_entrance('Kokiri Forest Storms Grotto'), lambda state: state.can_play('Song of Storms'))
    set_rule(world.get_entrance('Lost Woods Generic Grotto'), lambda state: state.can_blast_or_smash())
    set_rule(world.get_entrance('Lost Woods Sales Grotto'), lambda state: state.has_explosives() or (state.has('Hammer') and state.is_adult() and (state.can_play('Minuet of Forest') or state.can_play('Sarias Song'))))
    set_rule(world.get_entrance('Front of Meadow Grotto'), lambda state: state.has_explosives() or (state.has('Hammer') and state.is_adult() and (state.can_play('Minuet of Forest') or state.can_play('Sarias Song'))))
    set_rule(world.get_entrance('Meadow Gate'), lambda state: state.has_slingshot() or state.has_explosives() or state.can_child_melee_attack() or state.can_cast_dins_fire())
    set_rule(world.get_entrance('Remote Southern Grotto'), lambda state: state.can_blast_or_smash())
    set_rule(world.get_entrance('Field Near Lake Inside Fence Grotto'), lambda state: state.can_blast_or_smash())
    set_rule(world.get_entrance('Field Valley Grotto'), lambda state: state.can_blast_or_smash())
    set_rule(world.get_entrance('Field West Castle Town Grotto'), lambda state: state.can_blast_or_smash())
    set_rule(world.get_entrance('Field Far West Castle Town Grotto'), lambda state: state.can_blast_or_smash())
    set_rule(world.get_entrance('Field Kakariko Grotto'), lambda state: state.can_blast_or_smash())
    set_rule(world.get_entrance('Field North Lon Lon Grotto'), lambda state: state.can_blast_or_smash())
    set_rule(world.get_entrance('Castle Storms Grotto'), lambda state: state.can_play('Song of Storms'))
    set_rule(world.get_entrance('Kakariko Bombable Grotto'), lambda state: state.can_blast_or_smash() and (state.is_adult() or (state.can_child_melee_attack() or state.can_cast_dins_fire())))
    set_rule(world.get_entrance('Mountain Bombable Grotto'), lambda state: state.can_blast_or_smash())
    set_rule(world.get_entrance('Mountain Storms Grotto'), lambda state: state.can_play('Song of Storms'))
    set_rule(world.get_entrance('Top of Crater Grotto'), lambda state: state.can_blast_or_smash())
    set_rule(world.get_entrance('Zora River Plateau Open Grotto'), lambda state: state.has_explosives() or state.has('Progressive Scale') or state.is_adult())
    set_rule(world.get_entrance('Zora River Plateau Bombable Grotto'), lambda state: state.can_blast_or_smash())
    set_rule(world.get_location('Tektite Grotto Freestanding PoH'), lambda state: state.has('Progressive Scale', 2) or (state.has('Iron Boots') and state.is_adult()))
    set_rule(world.get_location('GS Kokiri Know It All House'), lambda state: state.nighttime() and (state.can_leave_forest() or state.can_play('Suns Song')) and state.can_child_attack())
    set_rule(world.get_location('GS Kokiri Bean Patch'), lambda state: state.has_bottle() and state.can_child_attack() and (state.can_leave_forest() or state.can_child_melee_attack() or state.has('Boomerang') or state.has_explosives() or state.has('Buy Bottle Bug')))
    set_rule(world.get_location('GS Kokiri House of Twins'), lambda state: state.has('Progressive Hookshot') and state.is_adult() and state.nighttime())
    set_rule(world.get_location('GS Lost Woods Bean Patch Near Bridge'), lambda state: state.has_bottle() and state.can_child_attack() and (state.can_leave_forest() or state.can_child_melee_attack() or state.has('Boomerang') or state.has_explosives() or state.has('Buy Bottle Bug')))
    set_rule(world.get_location('GS Lost Woods Bean Patch Near Stage'), lambda state: state.has_bottle() and (state.can_child_attack() or (not world.shuffle_scrubs and state.has_deku_shield())) and (state.can_leave_forest() or state.can_child_melee_attack() or state.has('Boomerang') or state.has_explosives() or state.has('Buy Bottle Bug')))
    set_rule(world.get_location('GS Lost Woods Above Stage'), lambda state: state.has('Magic Bean') and state.nighttime())
    set_rule(world.get_location('GS Sacred Forest Meadow'), lambda state: state.has('Progressive Hookshot') and state.is_adult() and state.nighttime())
    set_rule(world.get_location('GS Hyrule Field near Kakariko'), lambda state: (state.has('Boomerang') and state.has_explosives()) or (state.has('Progressive Hookshot') and state.is_adult()))
    set_rule(world.get_location('GS Hyrule Field Near Gerudo Valley'), lambda state: (state.has('Hammer') and state.has_fire_source() and state.has('Progressive Hookshot') and state.is_adult()) or (state.has('Boomerang') and state.has_explosives()))
    set_rule(world.get_location('GS Hyrule Castle Tree'), lambda state: state.can_child_attack())
    set_rule(world.get_location('GS Hyrule Castle Grotto'), lambda state: state.has('Boomerang') and state.has_explosives())
    set_rule(world.get_location('GS Lon Lon Ranch Rain Shed'), lambda state: state.nighttime())
    set_rule(world.get_location('GS Lon Lon Ranch House Window'), lambda state: state.has('Boomerang') and state.nighttime())
    set_rule(world.get_location('GS Lon Lon Ranch Back Wall'), lambda state: state.has('Boomerang') and state.nighttime())
    set_rule(world.get_location('GS Kakariko House Under Construction'), lambda state: state.nighttime())
    set_rule(world.get_location('GS Kakariko Skulltula House'), lambda state: state.nighttime())
    set_rule(world.get_location('GS Kakariko Guard\'s House'), lambda state: state.nighttime())
    set_rule(world.get_location('GS Kakariko Tree'), lambda state: state.nighttime())
    set_rule(world.get_location('GS Kakariko Watchtower'), lambda state: (state.has_slingshot() or state.has_bombchus()) and state.nighttime())
    set_rule(world.get_location('GS Kakariko Above Impa\'s House'), lambda state: state.has('Progressive Hookshot') and state.is_adult() and state.nighttime())
    set_rule(world.get_location('GS Graveyard Wall'), lambda state: state.has('Boomerang') and state.nighttime())
    set_rule(world.get_location('GS Graveyard Bean Patch'), lambda state: state.has_bottle() and state.can_child_attack())
    set_rule(world.get_location('GS Mountain Trail Bean Patch'), lambda state: state.has_bottle() and (state.has_explosives() or state.has('Progressive Strength Upgrade')))
    set_rule(world.get_location('GS Mountain Trail Bomb Alcove'), lambda state: state.can_blast_or_smash())
    set_rule(world.get_location('GS Mountain Trail Path to Crater'), lambda state: state.has('Hammer') and state.is_adult() and state.nighttime())
    set_rule(world.get_location('GS Mountain Trail Above Dodongo\'s Cavern'), lambda state: state.has('Hammer') and state.is_adult() and state.nighttime())
    set_rule(world.get_location('GS Goron City Boulder Maze'), lambda state: state.has_explosives())
    set_rule(world.get_location('GS Death Mountain Crater Crate'), lambda state: state.can_blast_or_smash() and state.can_child_attack())
    set_rule(world.get_location('GS Goron City Center Platform'), lambda state: state.is_adult())
    set_rule(world.get_location('GS Mountain Crater Bean Patch'), lambda state: state.can_play('Bolero of Fire') and state.has_bottle() and state.can_child_attack())
    set_rule(world.get_location('GS Zora River Ladder'), lambda state: state.nighttime() and state.can_child_attack())
    set_rule(world.get_location('GS Zora River Near Raised Grottos'), lambda state: state.has('Progressive Hookshot') and state.nighttime())
    set_rule(world.get_location('GS Zora River Above Bridge'), lambda state: state.has('Progressive Hookshot') and state.nighttime())
    set_rule(world.get_location('GS Zora\'s Domain Frozen Waterfall'), lambda state: state.nighttime() and (state.has('Progressive Hookshot') or state.has_bow() or state.has('Magic Meter')))
    set_rule(world.get_location('GS Zora\'s Fountain Above the Log'), lambda state: state.has('Boomerang') and state.nighttime())
    set_rule(world.get_location('GS Zora\'s Fountain Hidden Cave'), lambda state: state.has('Progressive Strength Upgrade', 2) and state.can_blast_or_smash() and state.has('Progressive Hookshot') and state.nighttime())
# Jabu Jabu GS need no reqs becuase the access reqs for their zones cover them.
    set_rule(world.get_location('GS Lake Hylia Bean Patch'), lambda state: state.has_bottle() and state.can_child_attack())
    set_rule(world.get_location('GS Lake Hylia Lab Wall'), lambda state: state.has('Boomerang') and state.nighttime())
    set_rule(world.get_location('GS Lake Hylia Small Island'), lambda state: state.nighttime() and state.can_child_attack())
    set_rule(world.get_location('GS Lake Hylia Giant Tree'), lambda state: state.is_adult() and state.has('Progressive Hookshot', 2))
    set_rule(world.get_location('GS Lab Underwater Crate'), lambda state: state.is_adult() and state.has('Iron Boots') and state.has('Progressive Hookshot'))
    set_rule(world.get_location('GS Gerudo Valley Small Bridge'), lambda state: state.has('Boomerang') and state.nighttime())
    set_rule(world.get_location('GS Gerudo Valley Bean Patch'), lambda state: state.has_bottle() and state.can_child_attack())
    set_rule(world.get_location('GS Gerudo Valley Behind Tent'), lambda state: state.has('Progressive Hookshot') and state.is_adult() and state.nighttime())
    set_rule(world.get_location('GS Gerudo Valley Pillar'), lambda state: state.has('Progressive Hookshot') and state.is_adult() and state.nighttime())
    set_rule(world.get_location('GS Gerudo Fortress Archery Range'), lambda state: state.has('Progressive Hookshot') and state.has('Carpenter Rescue') and state.is_adult() and state.nighttime())
    set_rule(world.get_location('GS Gerudo Fortress Top Floor'), lambda state: state.nighttime())
    set_rule(world.get_location('GS Wasteland Ruins'), lambda state: state.has('Progressive Hookshot') and state.is_adult())
    set_rule(world.get_location('GS Desert Colossus Bean Patch'), lambda state: state.has_bottle() and state.can_play('Requiem of Spirit') and state.can_child_attack())
    set_rule(world.get_location('GS Desert Colossus Tree'), lambda state: state.has('Progressive Hookshot') and state.is_adult() and state.nighttime())
    set_rule(world.get_location('GS Desert Colossus Hill'), lambda state: ((state.has('Magic Bean') and state.can_play('Requiem of Spirit')) or state.has('Progressive Hookshot', 2)) and state.is_adult() and state.nighttime())
    set_rule(world.get_location('GS Zora River Tree'), lambda state: state.can_child_attack())
    set_rule(world.get_location('HF Grotto Deku Scrub Piece of Heart'), lambda state: state.can_stun_deku()) 
    set_rule(world.get_entrance('Zora River Storms Grotto'), lambda state: state.can_play('Song of Storms') and state.can_stun_deku())
    set_rule(world.get_entrance('Meadow Storms Grotto Child Access'), lambda state: state.can_play('Song of Storms') and (state.can_child_attack() or state.has_nuts() or state.has_deku_shield()))
    set_rule(world.get_entrance('Meadow Storms Grotto Adult Access'), lambda state: state.can_play('Song of Storms'))
    set_rule(world.get_entrance('Lake Hylia Grotto'), lambda state: state.can_stun_deku())
    set_rule(world.get_location('LW Deku Scrub Deku Nuts'), lambda state: state.can_stun_deku()) 
    set_rule(world.get_location('LW Deku Scrub Deku Sticks'), lambda state: state.can_stun_deku()) 
    set_rule(world.get_location('LW Deku Scrub Deku Stick Upgrade'), lambda state: state.can_stun_deku()) 
    set_rule(world.get_entrance('Desert Colossus Grotto'), lambda state: state.has('Progressive Strength', 2) and state.is_adult())
    set_rule(world.get_location('DMC Deku Scrub Bombs'), lambda state: state.can_blast_or_smash() and (state.can_child_attack() or state.has_nuts() or state.has_deku_shield()))
    set_rule(world.get_entrance('DMC Hammer Grotto'), lambda state: state.has('Hammer') and state.is_adult())
    set_rule(world.get_entrance('Goron City Grotto'), lambda state: state.is_adult() and ((state.can_play('Song of Time') and (world.difficulty != 'ohko' or state.has_GoronTunic() or state.has('Progressive Hookshot', 2) or (state.has('Nayrus Love') and state.has('Magic Meter')))) or (world.difficulty != 'ohko' and state.has_GoronTunic() and state.has('Progressive Hookshot')) or (state.has('Nayrus Love') and state.has('Magic Meter') and state.has('Progressive Hookshot'))))
    set_rule(world.get_entrance('Lon Lon Grotto'), lambda state: state.can_child_attack() or state.has_nuts() or state.has_deku_shield())
    set_rule(world.get_entrance('Gerudo Valley Storms Grotto'), lambda state: state.can_play('Song of Storms'))


    for location in world.get_locations():
        if location.type != 'Chest':
            forbid_item(location, 'Ice Trap')
        add_item_rule(location, lambda i: not (i.type == 'Song' and not i.world.shuffle_song_items and i.world.id != location.world.id))
        add_item_rule(location, lambda i: not (i.type == 'Shop' and i.world.id != location.world.id))
        if location.type == 'Shop':
            forbid_item(location, 'Biggoron Sword')

            if location.name in world.shop_prices:
                location.price = world.shop_prices[location.name]
                if location.price > 200:
                    set_rule(location, lambda state: state.has('Progressive Wallet', 2))
                elif location.price > 99:
                    set_rule(location, lambda state: state.has('Progressive Wallet'))

    # Biggoron Sword at bombchu bowling seems to lead to a soft lock.
    # Unsure what causes this, but I'm leaving this to original devs.
    # For now just avoiding this combination, since BigSword is not that important.
    forbid_item(world.get_location('Bombchu Bowling Bomb Bag'), 'Biggoron Sword')
    forbid_item(world.get_location('Bombchu Bowling Piece of Heart'), 'Biggoron Sword')


# This function should be ran once after the shop items are placed in the world.
# It should be ran before other items are placed in the world so that logic has
# the correct checks for them. This is save to do since every shop is still
# accessible when all items are obtained and every shop item is not.
# This function should also be called when a world is copied if the original world
# had called this function because the world.copy does not copy the rules
def set_shop_rules(world):
    for location in world.get_filled_locations():
        if location.item.type == 'Shop':
            # Add wallet requirements
            if location.item.name in ['Buy Arrows (50)', 'Buy Fish', 'Buy Goron Tunic', 'Buy Bombchu (20)', 'Buy Bombs (30)']:
                add_rule(location, lambda state: state.has('Progressive Wallet'))
            elif location.item.name in ['Buy Zora Tunic', 'Buy Blue Fire']:
                add_rule(location, lambda state: state.has('Progressive Wallet', 2))

            # Add adult only checks
            if location.item.name in ['Buy Goron Tunic', 'Buy Zora Tunic']:
                if location.parent_region.name == 'Goron Shop':
                    add_rule(location, lambda state: state.is_adult() and (state.has_explosives() or state.has('Progressive Strength Upgrade') or state.has_bow()))
                elif location.parent_region.name == 'Zora Shop':
                    add_rule(location, lambda state: state.can_reach('Zora Shop Adult Access', 'Entrance'))
                elif location.parent_region.name in ['Castle Town Bombchu Shop', 'Castle Town Potion Shop', 'Castle Town Bazaar']:
                    set_rule(location, lambda state: False)
                else:
                    add_rule(location, lambda state: state.is_adult())

            # Add item prerequisit checks
            if location.item.name in ['Buy Blue Fire', 'Buy Blue Potion', 'Buy Bottle Bug', 'Buy Fish', 'Buy Green Potion', 'Buy Poe', 'Buy Red Potion [30]', 'Buy Red Potion [40]', 'Buy Red Potion [50]', 'Fairy\'s Spirit']:
                add_rule(location, lambda state: state.has_bottle())
            if location.item.name in ['Buy Bombchu (10)', 'Buy Bombchu (20)', 'Buy Bombchu (5)']:
                add_rule(location, lambda state: state.has_bombchus_item())


def dung_rules_dt0(world):
	# Deku Tree Vanilla
    set_rule(world.get_entrance('Deku Tree Basement Path'), lambda state: state.has_slingshot() and (state.has_sticks() or state.can_cast_dins_fire()))
    set_rule(world.get_entrance('Deku Tree Slingshot Passage'), lambda state: state.has_deku_shield())

    set_rule(world.get_location('Queen Gohma Heart'), lambda state: state.has_deku_shield() and state.can_child_melee_attack())
    set_rule(world.get_location('Queen Gohma'), lambda state: state.has_deku_shield() and state.can_child_melee_attack())

	# GS
    set_rule(world.get_location('GS Deku Tree Basement Back Room'), lambda state: state.has('Boomerang') and (state.has_explosives()))
    set_rule(world.get_location('GS Deku Tree Basement Gate'), lambda state: state.can_child_attack())
    set_rule(world.get_location('GS Deku Tree Basement Vines'), lambda state: state.has_slingshot() or state.has('Boomerang') or state.has_explosives() or state.can_cast_dins_fire())

    set_rule(world.get_location('GS Deku Tree Compass Room'), lambda state: state.can_child_attack())

def dung_rules_dc0(world):
	# Dodongo's Cavern Vanilla
    set_rule(world.get_entrance('Dodongos Cavern Rocks'), lambda state: state.can_blast_or_smash() or state.has('Progressive Strength Upgrade') or state.is_adult())
    set_rule(world.get_entrance('Dodongos Cavern Lobby'), lambda state: state.can_blast_or_smash() or state.has('Progressive Strength Upgrade'))
    set_rule(world.get_entrance('Dodongos Cavern Left Door'), lambda state: (state.is_adult() or ((state.has_sticks() or state.can_cast_dins_fire()) and (state.has_slingshot() or state.has_explosives() or state.can_child_melee_attack()))) and (state.has_explosives() or state.has('Progressive Strength Upgrade') or state.can_cast_dins_fire() or (state.has_bow() and state.is_adult())))
    set_rule(world.get_location('Dodongos Cavern Compass Chest'), lambda state: state.is_adult() or ((state.has_sticks() or state.can_cast_dins_fire()) and (state.has_slingshot() or state.has_explosives() or state.can_child_melee_attack())))
    set_rule(world.get_location('DC Deku Scrub Deku Sticks'), lambda state: (state.is_adult() or (state.has_slingshot() or state.has_explosives() or state.can_child_melee_attack())))

    set_rule(world.get_entrance('Dodongos Cavern Slingshot Target'), lambda state: (state.has_slingshot() and (state.has_explosives() or state.has('Progressive Strength Upgrade'))) or ((state.has_bow() or state.has('Hover Boots') or state.has('Progressive Hookshot', 2) or world.logic_dc_jump) and state.is_adult()))
    set_rule(world.get_location('DC Deku Scrub Deku Nuts'), lambda state: state.can_blast_or_smash())
    set_rule(world.get_location('DC Deku Scrub Deku Seeds'), lambda state: state.can_blast_or_smash())
    set_rule(world.get_location('Dodongos Cavern End of Bridge Chest'), lambda state: state.can_blast_or_smash())
    set_rule(world.get_entrance('Dodongos Cavern Bomb Drop'), lambda state: state.has_explosives())

    # Boss
    set_rule(world.get_location('King Dodongo'), lambda state: (state.has_bombs() or state.has('Progressive Strength Upgrade')) and (state.is_adult() or state.can_child_melee_attack()))
    set_rule(world.get_location('King Dodongo Heart'), lambda state: (state.has_bombs() or state.has('Progressive Strength Upgrade')) and (state.is_adult() or state.can_child_melee_attack()))

    # GS
    set_rule(world.get_location('GS Dodongo\'s Cavern East Side Room'), lambda state: state.has_explosives() or state.is_adult() or state.has_slingshot() or state.has('Boomerang') or state.can_child_melee_attack())
    set_rule(world.get_location('GS Dodongo\'s Cavern Alcove Above Stairs'), lambda state: (state.has('Progressive Hookshot') and state.is_adult()) or (state.has('Boomerang') and (state.has_explosives() or state.has('Progressive Strength Upgrade'))))
    set_rule(world.get_location('GS Dodongo\'s Cavern Scarecrow'), lambda state: state.is_adult() and ( (state.has('Progressive Hookshot') and state.has_ocarina()) or state.has('Progressive Hookshot', 2) ))

def dung_rules_jb0(world):
    set_rule(world.get_entrance('Jabu Jabus Belly Ceiling Switch'), lambda state: state.has_slingshot() or state.has_explosives() or state.has('Boomerang'))
    set_rule(world.get_entrance('Jabu Jabus Belly Tentacles'), lambda state: state.has('Boomerang'))
    set_rule(world.get_entrance('Jabu Jabus Belly Octopus'), lambda state: state.can_child_melee_attack())

def dung_rules_fot0(world):
	# Forest Temple Vanilla
    set_rule(world.get_entrance('Forest Temple Song of Time Block'), lambda state: state.can_play('Song of Time'))
    set_rule(world.get_entrance('Forest Temple Lobby Eyeball Switch'), lambda state: state.has_bow() and state.is_adult())
    set_rule(world.get_entrance('Forest Temple Lobby Locked Door'), lambda state: state.has('Small Key (Forest Temple)', 1))
    set_rule(world.get_entrance('Forest Temple Well Connection'), lambda state: ((state.has('Iron Boots') or state.has('Progressive Hookshot', 2)) and state.is_adult()) or state.has('Progressive Scale', 2)) #Longshot can grab some very high up vines to drain the well.
    set_rule(world.get_entrance('Forest Temple Scarecrows Song'), lambda state: False) #For some reason you can't actually activate this from below. Cool game.
    set_rule(world.get_entrance('Forest Temple Elevator'), lambda state: state.has_bow() and state.is_adult() and state.has('Progressive Strength Upgrade') and state.has('Small Key (Forest Temple)', 3))
    set_rule(world.get_entrance('Forest Temple Outside Backdoor'), lambda state: state.has('Hover Boots') and state.is_adult())
    set_rule(world.get_entrance('Forest Temple Twisted Hall'), lambda state: state.has('Progressive Strength Upgrade') and state.has('Small Key (Forest Temple)', 3))
    set_rule(world.get_entrance('Forest Temple Straightened Hall'), lambda state: state.has('Progressive Strength Upgrade') and state.has('Small Key (Forest Temple)', 2) and state.has_bow())
    set_rule(world.get_entrance('Forest Temple Drop to Falling Room'), lambda state: state.has('Small Key (Forest Temple)', 5) and (state.has_bow() or state.can_cast_dins_fire()))
    set_rule(world.get_location('Forest Temple Block Push Chest'), lambda state: state.has('Progressive Strength Upgrade') and state.has_bow() and state.is_adult())
    set_rule(world.get_location('Forest Temple Red Poe Chest'), lambda state: state.has_bow() and state.is_adult())
    set_rule(world.get_location('Forest Temple Blue Poe Chest'), lambda state: state.has_bow() and state.is_adult())

    # Boss 
    set_rule(world.get_location('Phantom Ganon'), lambda state: state.has('Boss Key (Forest Temple)'))
    set_rule(world.get_location('Phantom Ganon Heart'), lambda state: state.has('Boss Key (Forest Temple)'))

	# GS
    set_rule(world.get_location('GS Forest Temple First Room'), lambda state: (state.has('Progressive Hookshot') or state.has_bow() or state.can_cast_dins_fire()) and state.is_adult())
    set_rule(world.get_location('GS Forest Temple Lobby'), lambda state: state.has('Progressive Hookshot') and state.is_adult())
    set_rule(world.get_location('GS Forest Temple Outdoor East'), lambda state: state.has('Progressive Hookshot') and state.is_adult())
    set_rule(world.get_location('GS Forest Temple Outdoor West'), lambda state: (state.has('Progressive Hookshot', 2) or (state.has('Progressive Hookshot') and state.can_reach('Forest Temple Outside Upper Ledge'))) and state.is_adult())
    set_rule(world.get_location('GS Forest Temple Basement'), lambda state: state.has('Progressive Hookshot'))

def dung_rules_fit0(world):
	# Fire Temple Vanilla
    set_rule(world.get_entrance('Fire Temple Early Climb'), lambda state: state.has_GoronTunic() and state.has('Small Key (Fire Temple)', 4) and state.has('Progressive Strength Upgrade') and (state.has_explosives() or ((state.has_bow() or state.has('Progressive Hookshot')) and state.is_adult())))
    set_rule(world.get_entrance('Fire Temple Fire Maze Escape'), lambda state: state.has('Small Key (Fire Temple)', 8) or (state.has('Small Key (Fire Temple)', 7) and state.has('Hover Boots') and state.has('Hammer') and state.is_adult()))
    set_rule(world.get_location('Fire Temple Fire Dancer Chest'), lambda state: (state.has('Small Key (Fire Temple)', 8) or (not world.keysanity and not world.dungeon_mq['FiT'])) and state.is_adult() and state.has('Hammer'))
    set_rule(world.get_location('Fire Temple Boss Key Chest'), lambda state: (state.has('Small Key (Fire Temple)', 8) or (not world.keysanity and not world.dungeon_mq['FiT'])) and state.is_adult() and state.has('Hammer'))
    set_rule(world.get_location('Fire Temple Big Lava Room Bombable Chest'), lambda state: state.has('Small Key (Fire Temple)', 2) and state.has_explosives())
    set_rule(world.get_location('Fire Temple Big Lava Room Open Chest'), lambda state: state.has('Small Key (Fire Temple)', 2))
    set_rule(world.get_location('Fire Temple Map Chest'), lambda state: state.has('Small Key (Fire Temple)', 6) or (state.has('Small Key (Fire Temple)', 5) and state.is_adult() and state.has_bow()))
    set_rule(world.get_location('Fire Temple Boulder Maze Upper Chest'), lambda state: state.has('Small Key (Fire Temple)', 6))
    set_rule(world.get_location('Fire Temple Boulder Maze Bombable Pit'), lambda state: state.has('Small Key (Fire Temple)', 6) and state.has_explosives())
    set_rule(world.get_location('Fire Temple Scarecrow Chest'), lambda state: state.has_ocarina() and state.has('Small Key (Fire Temple)', 6) and state.has('Progressive Hookshot') and state.is_adult())
    set_rule(world.get_location('Fire Temple Compass Chest'), lambda state: state.has('Small Key (Fire Temple)', 7))
    set_rule(world.get_location('Fire Temple Highest Goron Chest'), lambda state: state.can_play('Song of Time') and state.has('Hammer') and state.is_adult())
    set_rule(world.get_location('Fire Temple Megaton Hammer Chest'), lambda state: state.has_explosives())

    #boss
    set_rule(world.get_location('Volvagia'), lambda state: state.has_GoronTunic() and state.has('Hammer') and state.is_adult() and state.has('Boss Key (Fire Temple)') and (state.has('Hover Boots') or (state.can_reach('Fire Temple Upper') and (state.can_play('Song of Time') or state.has_explosives()))))
    set_rule(world.get_location('Volvagia Heart'), lambda state: state.has_GoronTunic() and state.has('Hammer') and state.is_adult() and state.has('Boss Key (Fire Temple)') and (state.has('Hover Boots') or (state.can_reach('Fire Temple Upper') and (state.can_play('Song of Time') or state.has_explosives()))))

	# GS
    set_rule(world.get_location('GS Fire Temple Song of Time Room'), lambda state: state.has('Small Key (Fire Temple)', 2) and state.can_play('Song of Time'))
    set_rule(world.get_location('GS Fire Temple Unmarked Bomb Wall'), lambda state: state.has('Small Key (Fire Temple)', 4) and state.has_explosives())
    set_rule(world.get_location('GS Fire Temple East Tower Climb'), lambda state: state.has_ocarina() and state.has('Small Key (Fire Temple)', 6) and state.has('Progressive Hookshot') and state.is_adult())
    set_rule(world.get_location('GS Fire Temple East Tower Top'), lambda state: state.has_ocarina() and state.has('Small Key (Fire Temple)', 6) and state.has('Progressive Hookshot') and state.is_adult())
    set_rule(world.get_location('GS Fire Temple Basement'), lambda state: (state.has('Small Key (Fire Temple)', 8) or (not world.keysanity and not world.dungeon_mq['FiT'])) and state.has('Hammer') and state.is_adult())

def dung_rules_wt0(world):
	# Water Temple vanilla
    set_rule(world.get_entrance('Water Temple Central Pillar'), lambda state: (state.has_bow() or state.can_cast_dins_fire() or state.has('Small Key (Water Temple)', 5)) and state.can_play('Zeldas Lullaby'))
    set_rule(world.get_entrance('Water Temple Upper Locked Door'), lambda state: state.has('Small Key (Water Temple)', 5) and (state.can_play('Zeldas Lullaby') or world.keysanity))
    set_rule(world.get_location('Water Temple Torches Chest'), lambda state: (state.has_bow() or state.can_cast_dins_fire()) and state.can_play('Zeldas Lullaby'))
    set_rule(world.get_location('Water Temple Dragon Chest'), lambda state: (state.has('Progressive Strength Upgrade') and state.can_play('Zeldas Lullaby')) or (state.has('Small Key (Water Temple)', 6) and (state.can_play('Zeldas Lullaby') or world.keysanity) and state.can_play('Song of Time') and state.has_bow()))
    set_rule(world.get_location('Water Temple Central Bow Target Chest'), lambda state: state.has_bow() and state.has('Progressive Strength Upgrade') and state.can_play('Zeldas Lullaby') and (state.has('Hover Boots') or state.has('Progressive Hookshot', 2)))
    set_always_allow(world.get_location('Water Temple Boss Key Chest'), lambda item, state: item.name == 'Small Key (Water Temple)')
    set_rule(world.get_location('Water Temple Boss Key Chest'), lambda state: (state.has('Small Key (Water Temple)', 6) and (state.can_play('Zeldas Lullaby') or world.keysanity) and ((state.has_explosives() and state.has('Progressive Strength Upgrade')) or state.has('Hover Boots')) and state.has('Progressive Hookshot', 2)) or item_name(state, 'Water Temple Boss Key Chest') == 'Small Key (Water Temple)') #If key for key, this lets the logic reduce the small key reqs for every other locked door.
    set_rule(world.get_location('Water Temple Cracked Wall Chest'), lambda state: state.has_explosives())
    set_rule(world.get_location('Water Temple Dark Link Chest'), lambda state: state.has('Small Key (Water Temple)', 6) and (state.can_play('Zeldas Lullaby') or world.keysanity))
    set_rule(world.get_location('Water Temple River Chest'), lambda state: state.has('Small Key (Water Temple)', 6) and state.can_play('Song of Time') and state.has_bow() and (state.can_play('Zeldas Lullaby') or world.keysanity))
    set_rule(world.get_location('Water Temple Central Pillar Chest'), lambda state: state.has_ZoraTunic())

	# boss rules
    set_rule(world.get_location('Morpha'), lambda state: state.has('Boss Key (Water Temple)') and state.has('Progressive Hookshot', 2))
    set_rule(world.get_location('Morpha Heart'), lambda state: state.has('Boss Key (Water Temple)') and state.has('Progressive Hookshot', 2))

    # GS
    set_rule(world.get_location('GS Water Temple South Basement'), lambda state: state.has_explosives() and state.can_play('Zeldas Lullaby'))
    set_rule(world.get_location('GS Water Temple Serpent River'), lambda state: state.can_play('Song of Time') and state.has('Small Key (Water Temple)', 6))
    set_rule(world.get_location('GS Water Temple Falling Platform Room'), lambda state: state.has('Progressive Hookshot', 2))
    set_rule(world.get_location('GS Water Temple Central Room'), lambda state: state.has('Progressive Hookshot', 2) or (state.has('Farores Wind') and state.has('Magic Meter')))
    #5 keys would be better but it wouldn't be compatible with the key for key scenarios, 6 will be identical pre-keysanity.
    set_rule(world.get_location('GS Water Temple Near Boss Key Chest'), lambda state: state.has('Progressive Hookshot', 2) and ((state.has_explosives() and state.has('Progressive Strength Upgrade')) or state.has('Hover Boots')) and (state.can_play('Zeldas Lullaby') or world.keysanity) and state.has('Small Key (Water Temple)', 6))

def dung_rules_spt0(world):
	# Spirit Temple vanilla
    set_rule(world.get_entrance('Spirit Temple Crawl Passage'), lambda state: state.can_play('Requiem of Spirit'))
    set_rule(world.get_entrance('Spirit Temple Silver Block'), lambda state: state.has('Progressive Strength Upgrade', 2) and state.is_adult())
    set_rule(world.get_entrance('Child Spirit Temple Climb'), lambda state: state.has('Small Key (Spirit Temple)', 1))
    set_rule(world.get_entrance('Child Spirit Temple Passthrough'), lambda state: state.has_explosives())
    set_rule(world.get_entrance('Adult Spirit Temple Passthrough'), lambda state: state.has('Small Key (Spirit Temple)', 1))
    set_rule(world.get_entrance('Spirit Temple Central Locked Door'), lambda state: state.has('Small Key (Spirit Temple)', 4) and state.has('Progressive Strength Upgrade', 2) and state.is_adult())
    set_rule(world.get_entrance('Spirit Temple Final Locked Door'), lambda state: state.has('Small Key (Spirit Temple)', 5) and (state.has('Progressive Hookshot') or state.has_bow() or state.has_explosives()))
    set_rule(world.get_location('Spirit Temple Child Left Chest'), lambda state: (state.has('Boomerang') or state.has_slingshot() or state.has_bombchus()) and (state.has_sticks() or state.has_explosives() or ((state.has_nuts() or state.has('Boomerang')) and (state.has('Kokiri Sword') or state.has_slingshot()))))
    set_rule(world.get_location('Spirit Temple Child Right Chest'), lambda state: (state.has('Boomerang') or state.has_slingshot() or state.has_bombchus()) and (state.has_sticks() or state.has_explosives() or ((state.has_nuts() or state.has('Boomerang')) and (state.has('Kokiri Sword') or state.has_slingshot()))) and (state.has_sticks() or state.can_cast_dins_fire()))
    set_rule(world.get_location('Spirit Temple Compass Chest'), lambda state: state.has('Progressive Hookshot') and state.can_play('Zeldas Lullaby'))
    set_rule(world.get_location('Spirit Temple Early Adult Right Chest'), lambda state: state.has_bow() or state.has('Progressive Hookshot') or state.has_bombchus()) #requires a very specific Bombchu use, Hover Boots can be skipped by jumping on top of the rolling rock.
    set_rule(world.get_location('Spirit Temple First Mirror Right Chest'), lambda state: state.has('Small Key (Spirit Temple)', 3))
    set_rule(world.get_location('Spirit Temple First Mirror Left Chest'), lambda state: state.has('Small Key (Spirit Temple)', 3))
    # All of these paths that include a check for bombchus_in_logic need to ensure that you have access to bombchu refills as well. That's currently always true thanks to bombchu bowling. But other the sources require bombchus already to be bought, which is not how we'd need it to work if bombchu refills were suddenly to become more scarce. So for now I opted not to put in the check for bombchu refills.
    set_rule(world.get_location('Spirit Temple Map Chest'), lambda state: ((state.has_explosives() or state.has('Small Key (Spirit Temple)', 3) or (state.has('Small Key (Spirit Temple)', 2) and world.bombchus_in_logic)) and (state.can_cast_dins_fire() or (state.can_shoot_fire_arrows() and state.has_sticks()))) or (state.has('Small Key (Spirit Temple)', 5) and state.has_explosives() and state.can_play('Requiem of Spirit') and state.has_sticks()) or (state.has('Small Key (Spirit Temple)', 3) and state.can_shoot_fire_arrows() and state.has('Progressive Strength Upgrade', 2)))
    set_rule(world.get_location('Spirit Temple Child Climb East Chest'), lambda state: state.has_explosives() or ((state.has('Boomerang') or state.has_slingshot()) and (state.has('Progressive Hookshot') or state.has_bow())) or ((state.has('Small Key (Spirit Temple)', 3) or (state.has('Small Key (Spirit Temple)', 2) and world.bombchus_in_logic)) and state.has('Progressive Strength Upgrade', 2) and state.is_adult() and (state.has('Progressive Hookshot') or state.has_bow())) or (state.has('Small Key (Spirit Temple)', 5) and state.can_play('Requiem of Spirit') and (state.has('Boomerang') or state.has_slingshot())))
    set_rule(world.get_location('Spirit Temple Child Climb North Chest'), lambda state: state.has_explosives() or ((state.has('Boomerang') or state.has_slingshot()) and (state.has('Progressive Hookshot') or state.has_bow())) or ((state.has('Small Key (Spirit Temple)', 3) or (state.has('Small Key (Spirit Temple)', 2) and world.bombchus_in_logic)) and state.has('Progressive Strength Upgrade', 2) and state.is_adult() and (state.has('Progressive Hookshot') or state.has_bow())) or (state.has('Small Key (Spirit Temple)', 5) and state.can_play('Requiem of Spirit') and (state.has('Boomerang') or state.has_slingshot())))
    set_rule(world.get_location('Spirit Temple Sun Block Room Chest'), lambda state: ((state.has_explosives() or state.has('Small Key (Spirit Temple)', 3) or (state.has('Small Key (Spirit Temple)', 2) and world.bombchus_in_logic)) and (state.can_cast_dins_fire() or (state.can_shoot_fire_arrows() and state.has_sticks()))) or (state.has('Small Key (Spirit Temple)', 5) and state.has_explosives() and state.can_play('Requiem of Spirit') and state.has_sticks()) or (state.has('Small Key (Spirit Temple)', 3) and state.can_shoot_fire_arrows() and state.has('Progressive Strength Upgrade', 2)))
    set_rule(world.get_location('Spirit Temple Statue Hand Chest'), lambda state: state.has('Small Key (Spirit Temple)', 3) and state.has('Progressive Strength Upgrade', 2) and state.is_adult() and state.can_play('Zeldas Lullaby'))
    set_rule(world.get_location('Spirit Temple NE Main Room Chest'), lambda state: state.has('Small Key (Spirit Temple)', 3) and state.has('Progressive Strength Upgrade', 2) and state.is_adult() and state.can_play('Zeldas Lullaby') and (state.has('Progressive Hookshot') or state.has("Hover Boots")))
    set_rule(world.get_location('Mirror Shield Chest'), lambda state: state.has('Small Key (Spirit Temple)', 4) and state.has('Progressive Strength Upgrade', 2) and state.is_adult() and state.has_explosives())
    set_rule(world.get_location('Silver Gauntlets Chest'), lambda state: (state.has('Small Key (Spirit Temple)', 3) and state.has('Progressive Hookshot', 2) and state.has_explosives()) or state.has('Small Key (Spirit Temple)', 5))
    set_rule(world.get_location('Spirit Temple Near Four Armos Chest'), lambda state: state.has('Mirror Shield') and state.has_explosives())
    set_rule(world.get_location('Spirit Temple Hallway Left Invisible Chest'), lambda state: state.can_see_with_lens() and state.has_explosives())
    set_rule(world.get_location('Spirit Temple Hallway Right Invisible Chest'), lambda state: state.can_see_with_lens() and state.has_explosives())
    set_rule(world.get_location('Spirit Temple Boss Key Chest'), lambda state: state.can_play('Zeldas Lullaby') and state.has_bow() and state.has('Progressive Hookshot') and state.can_blast_or_smash())
    set_rule(world.get_location('Spirit Temple Topmost Chest'), lambda state: state.has('Mirror Shield'))
    set_rule(world.get_location('Twinrova'), lambda state: state.has('Mirror Shield') and state.has_explosives() and state.has('Progressive Hookshot') and state.has('Boss Key (Spirit Temple)'))
    set_rule(world.get_location('Twinrova Heart'), lambda state: state.has('Mirror Shield') and state.has_explosives() and state.has('Progressive Hookshot') and state.has('Boss Key (Spirit Temple)'))

	# GS
    set_rule(world.get_location('GS Spirit Temple Metal Fence'), lambda state: (state.has('Boomerang') or state.has_slingshot() or state.has_bombchus()) and (state.has_sticks() or state.has_explosives() or ((state.has_nuts() or state.has('Boomerang')) and (state.has('Kokiri Sword') or state.has_slingshot()))))
    set_rule(world.get_location('GS Spirit Temple Hall to West Iron Knuckle'), lambda state: (state.has_explosives() and state.has('Boomerang') and state.has('Progressive Hookshot')) or (state.has('Boomerang') and state.has('Small Key (Spirit Temple)', 5) and state.has_explosives() and state.can_play('Requiem of Spirit')) or (state.has('Progressive Hookshot') and state.has('Progressive Strength Upgrade', 2) and state.is_adult() and (state.has('Small Key (Spirit Temple)', 3) or (state.has('Small Key (Spirit Temple)', 2) and state.has('Boomerang') and world.bombchus_in_logic))))
    set_rule(world.get_location('GS Spirit Temple Boulder Room'), lambda state: state.can_play('Song of Time') and (state.has_bow() or state.has('Progressive Hookshot') or state.has_bombchus()))
    set_rule(world.get_location('GS Spirit Temple Lobby'), lambda state: state.has('Progressive Strength Upgrade', 2) and state.has('Small Key (Spirit Temple)', 3) and state.is_adult() and (state.has('Progressive Hookshot', 2) or (state.has('Progressive Hookshot') and state.has_ocarina()) or state.has('Hover Boots')))
    set_rule(world.get_location('GS Spirit Temple Bomb for Light Room'), lambda state: state.can_child_attack() or ((state.has('Small Key (Spirit Temple)', 3) or (state.has('Small Key (Spirit Temple)', 2) and world.bombchus_in_logic)) and state.has('Progressive Strength Upgrade', 2) and state.is_adult()))

def dung_rules_sht0(world):
	# Shadow Temple Vanilla
    set_rule(world.get_entrance('Shadow Temple First Pit'), lambda state: state.has('Hover Boots'))
    set_rule(world.get_entrance('Shadow Temple Bomb Wall'), lambda state: state.has_explosives() and state.has('Small Key (Shadow Temple)', 1))
    set_rule(world.get_entrance('Shadow Temple Hookshot Target'), lambda state: state.has('Progressive Hookshot') and state.has('Small Key (Shadow Temple)', 3))
    set_rule(world.get_entrance('Shadow Temple Boat'), lambda state: state.can_play('Zeldas Lullaby') and state.has('Small Key (Shadow Temple)', 4))
    set_rule(world.get_location('Shadow Temple Falling Spikes Upper Chest'), lambda state: state.has('Progressive Strength Upgrade'))
    set_rule(world.get_location('Shadow Temple Falling Spikes Switch Chest'), lambda state: state.has('Progressive Strength Upgrade'))
    set_rule(world.get_location('Shadow Temple Invisible Spikes Chest'), lambda state: state.has('Small Key (Shadow Temple)', 2))
    set_rule(world.get_location('Shadow Temple Freestanding Key'), lambda state: state.has('Small Key (Shadow Temple)', 2) and state.has('Progressive Hookshot') and (state.has_bombs() or state.has('Progressive Strength Upgrade')))

    # boss rules
    set_rule(world.get_location('Bongo Bongo'), lambda state: state.has('Small Key (Shadow Temple)', 5) and (state.has_bow() or state.has('Progressive Hookshot', 2)) and state.has('Boss Key (Shadow Temple)'))
    set_rule(world.get_location('Bongo Bongo Heart'), lambda state: state.has('Small Key (Shadow Temple)', 5) and (state.has_bow() or state.has('Progressive Hookshot', 2)) and state.has('Boss Key (Shadow Temple)'))

    # GS
    set_rule(world.get_location('GS Shadow Temple Like Like Room'), lambda state: state.has('Progressive Hookshot'))
    set_rule(world.get_location('GS Shadow Temple Crusher Room'), lambda state: state.has('Progressive Hookshot'))
    set_rule(world.get_location('GS Shadow Temple Single Giant Pot'), lambda state: state.has('Small Key (Shadow Temple)', 2) and state.has('Progressive Hookshot'))
    set_rule(world.get_location('GS Shadow Temple Near Ship'), lambda state: state.has('Progressive Hookshot', 2) and state.has('Small Key (Shadow Temple)', 4))

def dung_rules_bw0(world):
	# Bottom of the Well Vanilla
    set_rule(world.get_location('Bottom of the Well Front Left Hidden Wall'), lambda state: state.can_see_with_lens())
    set_rule(world.get_location('Bottom of the Well Front Center Bombable'), lambda state: state.has_explosives())
    set_rule(world.get_location('Bottom of the Well Right Bottom Hidden Wall'), lambda state: state.can_see_with_lens())
    set_rule(world.get_location('Bottom of the Well Center Large Chest'), lambda state: state.can_see_with_lens())
    set_rule(world.get_location('Bottom of the Well Center Small Chest'), lambda state: state.can_see_with_lens())
    set_rule(world.get_location('Bottom of the Well Back Left Bombable'), lambda state: state.has_explosives())
    set_rule(world.get_location('Bottom of the Well Defeat Boss'), lambda state: state.can_play('Zeldas Lullaby') and (state.has('Kokiri Sword') or (state.has_sticks() and world.logic_child_deadhand))) #Sword not strictly necessary but frankly being forced to do this with sticks isn't fair
    set_rule(world.get_location('Bottom of the Well Invisible Chest'), lambda state: state.can_play('Zeldas Lullaby') and state.can_see_with_lens())
    set_rule(world.get_location('Bottom of the Well Underwater Front Chest'), lambda state: state.can_play('Zeldas Lullaby'))
    set_rule(world.get_location('Bottom of the Well Underwater Left Chest'), lambda state: state.can_play('Zeldas Lullaby'))
    set_rule(world.get_location('Bottom of the Well Basement Chest'), lambda state: state.has_explosives() or (((state.has('Small Key (Bottom of the Well)', 3) and state.can_see_with_lens()) or state.can_cast_dins_fire()) and state.has('Progressive Strength Upgrade')))
    set_rule(world.get_location('Bottom of the Well Locked Pits'), lambda state: state.has('Small Key (Bottom of the Well)', 3) and state.can_see_with_lens()) #These pits are really unfair.
    set_rule(world.get_location('Bottom of the Well Behind Right Grate'), lambda state: state.has('Small Key (Bottom of the Well)', 3) and state.can_see_with_lens())
    set_rule(world.get_location('Bottom of the Well Freestanding Key'), lambda state: state.has_sticks() or state.can_cast_dins_fire())

    # GS
    set_always_allow(world.get_location('GS Well West Inner Room'), lambda item, state: item.name == 'Small Key (Bottom of the Well)')
    set_rule(world.get_location('GS Well West Inner Room'), lambda state: state.has('Boomerang') and state.can_see_with_lens() and (state.has('Small Key (Bottom of the Well)', 3) or item_name(state, 'GS Well West Inner Room') == 'Small Key (Bottom of the Well)')) #If key for key, this lets the logic reduce the small key reqs for every other locked door.
    set_always_allow(world.get_location('GS Well East Inner Room'), lambda item, state: item.name == 'Small Key (Bottom of the Well)')
    set_rule(world.get_location('GS Well East Inner Room'), lambda state: state.has('Boomerang') and state.can_see_with_lens() and (state.has('Small Key (Bottom of the Well)', 3) or item_name(state, 'GS Well East Inner Room') == 'Small Key (Bottom of the Well)')) #If key for key, this lets the logic reduce the small key reqs for every other locked door.
    set_rule(world.get_location('GS Well Like Like Cage'), lambda state: state.has('Boomerang') and state.can_see_with_lens() and state.has('Small Key (Bottom of the Well)', 3))

def dung_rules_ic0(world):
	# Ice Cavern Vanilla
    set_rule(world.get_location('Ice Cavern Map Chest'), lambda state: state.has_bottle())
    set_rule(world.get_location('Ice Cavern Compass Chest'), lambda state: state.has_bottle())
    set_rule(world.get_location('Ice Cavern Freestanding PoH'), lambda state: state.has_bottle())
    set_rule(world.get_location('Ice Cavern Iron Boots Chest'), lambda state: state.has_bottle())
    set_rule(world.get_location('Sheik in Ice Cavern'), lambda state: state.has_bottle() and state.is_adult())

	# GS
    set_rule(world.get_location('GS Ice Cavern Spinning Scythe Room'), lambda state: state.has('Progressive Hookshot') and state.is_adult())
    set_rule(world.get_location('GS Ice Cavern Heart Piece Room'), lambda state: state.has('Progressive Hookshot') and state.is_adult() and state.has_bottle())
    set_rule(world.get_location('GS Ice Cavern Push Block Room'), lambda state: state.has('Progressive Hookshot') and state.is_adult() and state.has_bottle())

def dung_rules_gtg0(world):
    set_rule(world.get_entrance('Gerudo Training Ground Left Silver Rupees'), lambda state: state.has('Progressive Hookshot') and state.is_adult())
    set_rule(world.get_entrance('Gerudo Training Ground Beamos'), lambda state: state.has_explosives())
    set_rule(world.get_entrance('Gerudo Training Grounds Right Locked Doors'), lambda state: state.has('Small Key (Gerudo Training Grounds)', 9))
    set_rule(world.get_entrance('Gerudo Training Grounds Maze Ledge'), lambda state: state.can_play('Song of Time'))
    set_rule(world.get_entrance('Gerudo Training Grounds Right Hookshot Target'), lambda state: state.has('Progressive Hookshot') and state.is_adult())
    set_rule(world.get_entrance('Gerudo Training Grounds Hammer Target'), lambda state: state.has('Hammer') and state.has_bow() and state.is_adult())
    set_rule(world.get_entrance('Gerudo Training Grounds Hidden Hookshot Target'), lambda state: state.has('Progressive Hookshot') and state.can_see_with_lens() and state.is_adult())
    set_rule(world.get_location('Gerudo Training Grounds Lobby Left Chest'), lambda state: state.has_bow() and state.is_adult())
    set_rule(world.get_location('Gerudo Training Grounds Lobby Right Chest'), lambda state: state.has_bow() and state.is_adult())
    set_rule(world.get_location('Gerudo Training Grounds Beamos Chest'), lambda state: state.has_explosives())
    set_rule(world.get_location('Gerudo Training Grounds Hidden Ceiling Chest'), lambda state: state.has('Small Key (Gerudo Training Grounds)', 3) and state.can_see_with_lens())
    set_rule(world.get_location('Gerudo Training Grounds Maze Path First Chest'), lambda state: state.has('Small Key (Gerudo Training Grounds)', 4))
    set_rule(world.get_location('Gerudo Training Grounds Maze Path Second Chest'), lambda state: state.has('Small Key (Gerudo Training Grounds)', 6))
    set_rule(world.get_location('Gerudo Training Grounds Maze Path Third Chest'), lambda state: state.has('Small Key (Gerudo Training Grounds)', 7))
    set_rule(world.get_location('Gerudo Training Grounds Maze Path Final Chest'), lambda state: (state.has('Small Key (Gerudo Training Grounds)', 9)) or (item_name(state, 'Gerudo Training Grounds Maze Path Final Chest') == 'Small Key (Gerudo Training Grounds)' and state.has('Small Key (Gerudo Training Grounds)', 8))) #Allow key for key
    set_always_allow(world.get_location('Gerudo Training Grounds Maze Path Final Chest'), lambda item, state: item.name == 'Small Key (Gerudo Training Grounds)')
    set_rule(world.get_location('Gerudo Training Grounds Underwater Silver Rupee Chest'), lambda state: state.has('Progressive Hookshot') and state.can_play('Song of Time') and state.has('Iron Boots') and state.is_adult() and (world.logic_fewer_tunic_requirements or state.has_ZoraTunic()))
    set_rule(world.get_location('Gerudo Training Grounds Hammer Room Switch Chest'), lambda state: state.has('Hammer') and state.is_adult())
    set_rule(world.get_location('Gerudo Training Grounds Eye Statue Chest'), lambda state: state.has_bow() and state.is_adult())
    set_rule(world.get_location('Gerudo Training Grounds Near Scarecrow Chest'), lambda state: state.has_bow() and state.is_adult())
    set_rule(world.get_location('Gerudo Training Grounds Heavy Block First Chest'), lambda state: state.has('Progressive Strength Upgrade', 2) and state.can_see_with_lens() and state.is_adult())
    set_rule(world.get_location('Gerudo Training Grounds Heavy Block Second Chest'), lambda state: state.has('Progressive Strength Upgrade', 2) and state.can_see_with_lens() and state.is_adult())
    set_rule(world.get_location('Gerudo Training Grounds Heavy Block Third Chest'), lambda state: state.has('Progressive Strength Upgrade', 2) and state.can_see_with_lens() and state.is_adult())
    set_rule(world.get_location('Gerudo Training Grounds Heavy Block Fourth Chest'), lambda state: state.has('Progressive Strength Upgrade', 2) and state.can_see_with_lens() and state.is_adult())

def dung_rules_gc0(world):
    set_rule(world.get_entrance('Ganons Castle Light Trial'), lambda state: state.has('Progressive Strength Upgrade', 3))
    set_rule(world.get_entrance('Ganons Castle Tower'), lambda state: (world.skipped_trials['Forest'] or state.has('Forest Trial Clear')) and (world.skipped_trials['Fire'] or state.has('Fire Trial Clear')) and (world.skipped_trials['Water'] or state.has('Water Trial Clear')) and (world.skipped_trials['Shadow'] or state.has('Shadow Trial Clear')) and (world.skipped_trials['Spirit'] or state.has('Spirit Trial Clear')) and (world.skipped_trials['Light'] or state.has('Light Trial Clear')))
    set_rule(world.get_location('Ganons Castle Forest Trial Clear'), lambda state: state.can_shoot_light_arrows() and (state.can_shoot_fire_arrows() or state.can_cast_dins_fire()))
    set_rule(world.get_location('Ganons Castle Fire Trial Clear'), lambda state: state.has_GoronTunic() and state.has('Progressive Strength Upgrade', 3) and state.can_shoot_light_arrows() and state.has('Progressive Hookshot', 2))
    set_rule(world.get_location('Ganons Castle Water Trial Clear'), lambda state: state.has_bottle() and state.has('Hammer') and state.can_shoot_light_arrows())
    set_rule(world.get_location('Ganons Castle Shadow Trial Clear'), lambda state: state.can_shoot_light_arrows() and state.has('Hammer') and ((state.can_shoot_fire_arrows() and (state.has('Hover Boots') or state.can_see_with_lens())) or (state.has('Progressive Hookshot', 2) and (state.has('Hover Boots') or (state.can_cast_dins_fire() and state.can_see_with_lens())))))
    set_rule(world.get_location('Ganons Castle Shadow Trial First Chest'), lambda state: state.can_shoot_fire_arrows() or state.has('Progressive Hookshot') or state.has('Hover Boots') or state.can_play('Song of Time'))
    set_rule(world.get_location('Ganons Castle Shadow Trial Second Chest'), lambda state: state.can_shoot_fire_arrows() or (state.has('Progressive Hookshot', 2) and (state.has('Hover Boots') or state.can_cast_dins_fire())))
    set_rule(world.get_location('Ganons Castle Spirit Trial Clear'), lambda state: state.can_shoot_light_arrows() and state.has('Mirror Shield') and state.has_bombchus() and state.has('Progressive Hookshot'))
    set_rule(world.get_location('Ganons Castle Spirit Trial First Chest'), lambda state: state.has('Progressive Hookshot'))
    set_rule(world.get_location('Ganons Castle Spirit Trial Second Chest'), lambda state: state.has('Progressive Hookshot') and state.has_bombchus() and state.can_see_with_lens())
    set_rule(world.get_location('Ganons Castle Light Trial Clear'), lambda state: state.can_shoot_light_arrows() and state.has('Progressive Hookshot') and state.has('Small Key (Ganons Castle)', 2))
    set_rule(world.get_location('Ganons Castle Light Trail Invisible Enemies Chest'), lambda state: state.can_see_with_lens())
    set_rule(world.get_location('Ganons Castle Light Trial Lullaby Chest'), lambda state: state.can_play('Zeldas Lullaby') and state.has('Small Key (Ganons Castle)', 1))
