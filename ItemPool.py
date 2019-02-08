from collections import namedtuple
import logging
import random
from Utils import random_choices
from Item import ItemFactory


#This file sets the item pools for various modes. Timed modes and triforce hunt are enforced first, and then extra items are specified per mode to fill in the remaining space.
#Some basic items that various modes require are placed here, including pendants and crystals. Medallion requirements for the two relevant entrances are also decided.


alwaysitems = ([
    'Biggoron Sword',
    'Boomerang',
    'Lens of Truth',
    'Hammer',
    'Iron Boots',
    'Goron Tunic',
    'Zora Tunic',
    'Hover Boots',
    'Mirror Shield',
    'Stone of Agony',
    'Fire Arrows',
    'Ice Arrows',
    'Light Arrows',
    'Dins Fire',
    'Farores Wind',
    'Nayrus Love',
    'Rupee (1)']
    + ['Progressive Hookshot'] * 2
    + ['Deku Shield']
    + ['Hylian Shield']
    + ['Progressive Strength Upgrade'] * 3
    + ['Progressive Scale'] * 2
    + ['Recovery Heart'] * 6
    + ['Bow'] * 3
    + ['Slingshot'] * 3
    + ['Bomb Bag'] * 3
    + ['Bombs (5)'] * 2
    + ['Bombs (10)']
    + ['Bombs (20)']
    + ['Arrows (5)']
    + ['Arrows (10)'] * 5
    + ['Progressive Wallet'] * 2
    + ['Magic Meter'] * 2
    + ['Double Defense']
    + ['Deku Stick Capacity'] * 2
    + ['Deku Nut Capacity'] * 2
    + ['Piece of Heart (Treasure Chest Game)'])


easy_items = ([
    'Biggoron Sword',
    'Kokiri Sword',
    'Boomerang',
    'Lens of Truth',
    'Hammer',
    'Iron Boots',
    'Goron Tunic',
    'Zora Tunic',
    'Hover Boots',
    'Mirror Shield',
    'Fire Arrows',
    'Light Arrows',
    'Dins Fire',
    'Progressive Hookshot',
    'Progressive Strength Upgrade',
    'Progressive Scale',
    'Progressive Wallet',
    'Magic Meter',
    'Deku Stick Capacity', 
    'Deku Nut Capacity', 
    'Bow', 
    'Slingshot', 
    'Bomb Bag',
    'Double Defense'] +
    ['Heart Container'] * 16 +
    ['Piece of Heart'] * 3)

normal_items = (
    ['Heart Container'] * 8 +
    ['Piece of Heart'] * 35)


item_difficulty_max = {
    'plentiful': {},
    'balanced': {},
    'scarce': {
        'Bombchus': 3,
        'Bombchus (5)': 1,
        'Bombchus (10)': 2,
        'Bombchus (20)': 0,
        'Magic Meter': 1, 
        'Double Defense': 0, 
        'Deku Stick Capacity': 1, 
        'Deku Nut Capacity': 1, 
        'Bow': 2, 
        'Slingshot': 2, 
        'Bomb Bag': 2,
        'Heart Container': 0,
    },
    'minimal': {
        'Bombchus': 1,
        'Bombchus (5)': 1,
        'Bombchus (10)': 0,
        'Bombchus (20)': 0,
        'Nayrus Love': 0,
        'Magic Meter': 1, 
        'Double Defense': 0, 
        'Deku Stick Capacity': 0, 
        'Deku Nut Capacity': 0, 
        'Bow': 1, 
        'Slingshot': 1, 
        'Bomb Bag': 1,
        'Heart Container': 0,
        'Piece of Heart': 0,
    },
}


DT_vanilla = (
    ['Recovery Heart'] * 2)

DT_MQ = (
    ['Deku Shield'] * 2 +
    ['Rupees (50)'])

DC_vanilla = (
    ['Rupees (20)'])

DC_MQ = (
    ['Hylian Shield'] +
    ['Rupees (5)'])

JB_MQ = (
    ['Deku Nuts (5)'] * 4 +
    ['Recovery Heart'] +
    ['Deku Shield'] +
    ['Deku Stick (1)'])

FoT_vanilla = (
    ['Recovery Heart'] +
    ['Arrows (10)'] +
    ['Arrows (30)'])

FoT_MQ = (
    ['Arrows (5)'])

FiT_vanilla = (
    ['Rupees (200)'])

FiT_MQ = (
    ['Bombs (20)'] +
    ['Hylian Shield'])

SpT_vanilla = (
    ['Deku Shield'] * 2 +
    ['Recovery Heart'] +
    ['Bombs (20)'])

SpT_MQ = (
    ['Rupees (50)'] * 2 +
    ['Arrows (30)'])

ShT_vanilla = (
    ['Arrows (30)'])

ShT_MQ = (
    ['Arrows (5)'] * 2 +
    ['Rupees (20)'])

BW_vanilla = (
    ['Recovery Heart'] +
    ['Bombs (10)'] +
    ['Rupees (200)'] +
    ['Deku Nuts (5)'] +
    ['Deku Nuts (10)'] +
    ['Deku Shield'] +
    ['Hylian Shield'])

GTG_vanilla = (
    ['Arrows (30)'] * 3 +
    ['Rupees (200)'])

GTG_MQ = (
    ['Rupee (Treasure Chest Game)'] * 2 +
    ['Arrows (10)'] +
    ['Rupee (1)'] +
    ['Rupees (50)'])

GC_vanilla = (
    ['Rupees (5)'] * 3 +
    ['Arrows (30)'])

GC_MQ = (
    ['Arrows (10)'] * 2 +
    ['Bombs (5)'] +
    ['Rupees (20)'] +
    ['Recovery Heart'])


normal_bottles = [
    'Bottle',
    'Bottle with Milk',
    'Bottle with Red Potion',
    'Bottle with Green Potion',
    'Bottle with Blue Potion',
    'Bottle with Fairy',
    'Bottle with Fish',
    'Bottle with Bugs',
    'Bottle with Poe',
    'Bottle with Big Poe',
    'Bottle with Blue Fire']

normal_bottle_count = 3


normal_rupees = (
    ['Rupees (5)'] * 13 +
    ['Rupees (20)'] * 5 +
    ['Rupees (50)'] * 7 +
    ['Rupees (200)'] * 3)

shopsanity_rupees = (
    ['Rupees (5)'] * 2 +
    ['Rupees (20)'] * 10 +
    ['Rupees (50)'] * 10 +
    ['Rupees (200)'] * 5 +
    ['Progressive Wallet'])


vanilla_shop_items = {
    'Kokiri Shop Item 1': 'Buy Deku Shield',
    'Kokiri Shop Item 2': 'Buy Deku Nut (5)',
    'Kokiri Shop Item 3': 'Buy Deku Nut (10)',
    'Kokiri Shop Item 4': 'Buy Deku Stick (1)',
    'Kokiri Shop Item 5': 'Buy Deku Seeds (30)',
    'Kokiri Shop Item 6': 'Buy Arrows (10)',
    'Kokiri Shop Item 7': 'Buy Arrows (30)',
    'Kokiri Shop Item 8': 'Buy Heart',
    'Kakariko Potion Shop Item 1': 'Buy Deku Nut (5)',
    'Kakariko Potion Shop Item 2': 'Buy Fish',
    'Kakariko Potion Shop Item 3': 'Buy Red Potion [30]',
    'Kakariko Potion Shop Item 4': 'Buy Green Potion',
    'Kakariko Potion Shop Item 5': 'Buy Blue Fire',
    'Kakariko Potion Shop Item 6': 'Buy Bottle Bug',
    'Kakariko Potion Shop Item 7': 'Buy Poe',
    'Kakariko Potion Shop Item 8': 'Buy Fairy\'s Spirit',
    'Bombchu Shop Item 1': 'Buy Bombchu (5)',
    'Bombchu Shop Item 2': 'Buy Bombchu (10)',
    'Bombchu Shop Item 3': 'Buy Bombchu (10)',
    'Bombchu Shop Item 4': 'Buy Bombchu (10)',
    'Bombchu Shop Item 5': 'Buy Bombchu (20)',
    'Bombchu Shop Item 6': 'Buy Bombchu (20)',
    'Bombchu Shop Item 7': 'Buy Bombchu (20)',
    'Bombchu Shop Item 8': 'Buy Bombchu (20)',
    'Castle Town Potion Shop Item 1': 'Buy Green Potion',
    'Castle Town Potion Shop Item 2': 'Buy Blue Fire',
    'Castle Town Potion Shop Item 3': 'Buy Red Potion [30]',
    'Castle Town Potion Shop Item 4': 'Buy Fairy\'s Spirit',
    'Castle Town Potion Shop Item 5': 'Buy Deku Nut (5)',
    'Castle Town Potion Shop Item 6': 'Buy Bottle Bug',
    'Castle Town Potion Shop Item 7': 'Buy Poe',
    'Castle Town Potion Shop Item 8': 'Buy Fish',
    'Castle Town Bazaar Item 1': 'Buy Hylian Shield',
    'Castle Town Bazaar Item 2': 'Buy Bombs (5) [35]',
    'Castle Town Bazaar Item 3': 'Buy Deku Nut (5)',
    'Castle Town Bazaar Item 4': 'Buy Heart',
    'Castle Town Bazaar Item 5': 'Buy Arrows (10)',
    'Castle Town Bazaar Item 6': 'Buy Arrows (50)',
    'Castle Town Bazaar Item 7': 'Buy Deku Stick (1)',
    'Castle Town Bazaar Item 8': 'Buy Arrows (30)',
    'Kakariko Bazaar Item 1': 'Buy Hylian Shield',
    'Kakariko Bazaar Item 2': 'Buy Bombs (5) [35]',
    'Kakariko Bazaar Item 3': 'Buy Deku Nut (5)',
    'Kakariko Bazaar Item 4': 'Buy Heart',
    'Kakariko Bazaar Item 5': 'Buy Arrows (10)',
    'Kakariko Bazaar Item 6': 'Buy Arrows (50)',
    'Kakariko Bazaar Item 7': 'Buy Deku Stick (1)',
    'Kakariko Bazaar Item 8': 'Buy Arrows (30)',
    'Zora Shop Item 1': 'Buy Zora Tunic',
    'Zora Shop Item 2': 'Buy Arrows (10)',
    'Zora Shop Item 3': 'Buy Heart',
    'Zora Shop Item 4': 'Buy Arrows (30)',
    'Zora Shop Item 5': 'Buy Deku Nut (5)',
    'Zora Shop Item 6': 'Buy Arrows (50)',
    'Zora Shop Item 7': 'Buy Fish',
    'Zora Shop Item 8': 'Buy Red Potion [50]',
    'Goron Shop Item 1': 'Buy Bombs (5) [25]',
    'Goron Shop Item 2': 'Buy Bombs (10)',
    'Goron Shop Item 3': 'Buy Bombs (20)',
    'Goron Shop Item 4': 'Buy Bombs (30)',
    'Goron Shop Item 5': 'Buy Goron Tunic',
    'Goron Shop Item 6': 'Buy Heart',
    'Goron Shop Item 7': 'Buy Red Potion [40]',
    'Goron Shop Item 8': 'Buy Heart',
}


min_shop_items = (
    ['Buy Deku Shield'] +
    ['Buy Hylian Shield'] +
    ['Buy Goron Tunic'] +
    ['Buy Zora Tunic'] +
    ['Buy Deku Nut (5)'] * 2 + ['Buy Deku Nut (10)'] +
    ['Buy Deku Stick (1)'] * 2 +
    ['Buy Deku Seeds (30)'] +
    ['Buy Arrows (10)'] * 2 + ['Buy Arrows (30)'] + ['Buy Arrows (50)'] +
    ['Buy Bombchu (5)'] + ['Buy Bombchu (10)'] * 2 + ['Buy Bombchu (20)'] +
    ['Buy Bombs (5) [25]'] + ['Buy Bombs (5) [35]'] + ['Buy Bombs (10)'] + ['Buy Bombs (20)'] +
    ['Buy Green Potion'] +
    ['Buy Red Potion [30]'] +
    ['Buy Blue Fire'] +
    ['Buy Fairy\'s Spirit'] +
    ['Buy Bottle Bug'] +
    ['Buy Fish'])


vanilla_deku_scrubs = {
    'ZR Grotto Deku Scrub Red Potion': 'Buy Red Potion [30]',
    'ZR Grotto Deku Scrub Green Potion': 'Buy Green Potion',
    'SFM Grotto Deku Scrub Red Potion': 'Buy Red Potion [30]',
    'SFM Grotto Deku Scrub Green Potion': 'Buy Green Potion',
    'LH Grotto Deku Scrub Deku Nuts': 'Buy Deku Nut (5)',
    'LH Grotto Deku Scrub Bombs': 'Buy Bombs (5) [35]',
    'LH Grotto Deku Scrub Arrows': 'Buy Arrows (30)',
    'Valley Grotto Deku Scrub Red Potion': 'Buy Red Potion [30]',
    'Valley Grotto Deku Scrub Green Potion': 'Buy Green Potion',
    'LW Deku Scrub Deku Nuts': 'Buy Deku Nut (5)',
    'LW Deku Scrub Deku Sticks': 'Buy Deku Stick (1)',
    'LW Grotto Deku Scrub Arrows': 'Buy Arrows (30)',
    'Desert Grotto Deku Scrub Red Potion': 'Buy Red Potion [30]',
    'Desert Grotto Deku Scrub Green Potion': 'Buy Green Potion',
    'DMC Deku Scrub Bombs': 'Buy Bombs (5) [35]',
    'DMC Grotto Deku Scrub Deku Nuts': 'Buy Deku Nut (5)',
    'DMC Grotto Deku Scrub Bombs': 'Buy Bombs (5) [35]',
    'DMC Grotto Deku Scrub Arrows': 'Buy Arrows (30)',
    'Goron Grotto Deku Scrub Deku Nuts': 'Buy Deku Nut (5)',
    'Goron Grotto Deku Scrub Bombs': 'Buy Bombs (5) [35]',
    'Goron Grotto Deku Scrub Arrows': 'Buy Arrows (30)',
    'LLR Grotto Deku Scrub Deku Nuts': 'Buy Deku Nut (5)',
    'LLR Grotto Deku Scrub Bombs': 'Buy Bombs (5) [35]',
    'LLR Grotto Deku Scrub Arrows': 'Buy Arrows (30)',
}


deku_scrubs_items = (
    ['Deku Nuts (5)'] * 5 +
    ['Deku Stick (1)'] +
    ['Bombs (5)'] * 5 +
    ['Recovery Heart'] * 4 +
    ['Rupees (5)'] * 4) # ['Green Potion']


rewardlist = [
    'Kokiri Emerald',
    'Goron Ruby',
    'Zora Sapphire',
    'Forest Medallion',
    'Fire Medallion',
    'Water Medallion',
    'Spirit Medallion',
    'Shadow Medallion',
    'Light Medallion']


songlist = [
    'Zeldas Lullaby',
    'Eponas Song',
    'Suns Song',
    'Sarias Song',
    'Song of Time',
    'Song of Storms',
    'Minuet of Forest',
    'Prelude of Light',
    'Bolero of Fire',
    'Serenade of Water',
    'Nocturne of Shadow',
    'Requiem of Spirit']


skulltula_locations = ([
    'GS Kokiri Know It All House',
    'GS Kokiri Bean Patch',
    'GS Kokiri House of Twins',
    'GS Lost Woods Bean Patch Near Bridge',
    'GS Lost Woods Bean Patch Near Stage',
    'GS Lost Woods Above Stage',
    'GS Sacred Forest Meadow',
    'GS Hyrule Field near Kakariko',
    'GS Hyrule Field Near Gerudo Valley',
    'GS Castle Market Guard House',
    'GS Hyrule Castle Tree',
    'GS Hyrule Castle Grotto',
    'GS Outside Ganon\'s Castle',
    'GS Lon Lon Ranch Tree',
    'GS Lon Lon Ranch Rain Shed',
    'GS Lon Lon Ranch House Window',
    'GS Lon Lon Ranch Back Wall',
    'GS Kakariko House Under Construction',
    'GS Kakariko Skulltula House',
    'GS Kakariko Guard\'s House',
    'GS Kakariko Tree',
    'GS Kakariko Watchtower',
    'GS Kakariko Above Impa\'s House',
    'GS Graveyard Wall',
    'GS Graveyard Bean Patch',
    'GS Mountain Trail Bean Patch',
    'GS Mountain Trail Bomb Alcove',
    'GS Mountain Trail Path to Crater',
    'GS Mountain Trail Above Dodongo\'s Cavern',
    'GS Goron City Boulder Maze',
    'GS Goron City Center Platform',
    'GS Death Mountain Crater Crate',
    'GS Mountain Crater Bean Patch',
    'GS Zora River Ladder',
    'GS Zora River Tree',
    'GS Zora River Near Raised Grottos',
    'GS Zora River Above Bridge',
    'GS Zora\'s Domain Frozen Waterfall',
    'GS Zora\'s Fountain Tree',
    'GS Zora\'s Fountain Above the Log',
    'GS Zora\'s Fountain Hidden Cave',
    'GS Lake Hylia Bean Patch',
    'GS Lake Hylia Lab Wall',
    'GS Lake Hylia Small Island',
    'GS Lake Hylia Giant Tree',
    'GS Lab Underwater Crate',
    'GS Gerudo Valley Small Bridge',
    'GS Gerudo Valley Bean Patch',
    'GS Gerudo Valley Behind Tent',
    'GS Gerudo Valley Pillar',
    'GS Gerudo Fortress Archery Range',
    'GS Gerudo Fortress Top Floor',
    'GS Wasteland Ruins',
    'GS Desert Colossus Bean Patch',
    'GS Desert Colossus Tree',
    'GS Desert Colossus Hill'])


tradeitems = (
    'Pocket Egg',
    'Pocket Cucco',
    'Cojiro',
    'Odd Mushroom',
    'Poachers Saw',
    'Broken Sword',
    'Prescription',
    'Eyeball Frog',
    'Eyedrops',
    'Claim Check')

tradeitemoptions = (
    'pocket_egg',
    'pocket_cucco',
    'cojiro',
    'odd_mushroom',
    'poachers_saw',
    'broken_sword',
    'prescription',
    'eyeball_frog',
    'eyedrops',
    'claim_check')


eventlocations = {
    'Ganon': 'Triforce',
    'Zeldas Letter': 'Zeldas Letter',
    'Magic Bean Salesman': 'Magic Bean',
    'King Zora Moves': 'Bottle',
    'Master Sword Pedestal': 'Master Sword',
    'Epona': 'Epona',
    'Deku Baba Sticks': 'Deku Stick Drop',
    'Goron City Stick Pot': 'Deku Stick Drop',
    'Zoras Domain Stick Pot': 'Deku Stick Drop',
    'Deku Baba Nuts': 'Deku Nut Drop',
    'Zoras Domain Nut Pot': 'Deku Nut Drop',
    'Gerudo Fortress Carpenter Rescue': 'Carpenter Rescue',
    'Haunted Wasteland Bombchu Salesman': 'Bombchus',
    'Ganons Castle Forest Trial Clear': 'Forest Trial Clear',
    'Ganons Castle Fire Trial Clear': 'Fire Trial Clear',
    'Ganons Castle Water Trial Clear': 'Water Trial Clear',
    'Ganons Castle Shadow Trial Clear': 'Shadow Trial Clear',
    'Ganons Castle Spirit Trial Clear': 'Spirit Trial Clear',
    'Ganons Castle Light Trial Clear': 'Light Trial Clear'
}


junk_pool_base = [
    ('Bombs (5)',       8),
    ('Bombs (10)',      2),
    ('Arrows (5)',      8),
    ('Arrows (10)',     2),
    ('Deku Stick (1)',  5),
    ('Deku Nuts (5)',   5),
    ('Deku Seeds (30)', 5),
    ('Rupees (5)',      10),
    ('Rupees (20)',     4),
    ('Rupees (50)',     1),
]
junk_pool = []
def get_junk_item(count=1):
    junk_items, junk_weights = zip(*junk_pool)
    return random_choices(junk_items, weights=junk_weights, k=count)


def replace_max_item(items, item, max):
    count = 0
    for i,val in enumerate(items):
        if val == item:
            if count >= max:
                items[i] = get_junk_item()[0]
            count += 1


def generate_itempool(world):
    junk_pool[:] = list(junk_pool_base)
    if world.junk_ice_traps == 'on': 
        junk_pool.append(('Ice Trap', 10))
    elif world.junk_ice_traps in ['mayhem', 'onslaught']:
        junk_pool[:] = [('Ice Trap', 1)]

    for location, item in eventlocations.items():
        world.push_item(location, ItemFactory(item, world))
        world.get_location(location).locked = True

    # set up item pool
    (pool, placed_items) = get_pool_core(world)
    world.itempool = ItemFactory(pool, world)
    for (location, item) in placed_items.items():
        world.push_item(location, ItemFactory(item, world))
        world.get_location(location).locked = True

    choose_trials(world)
    fill_bosses(world)

    world.initialize_items()


def get_pool_core(world):
    pool = []
    placed_items = {}

    if world.shuffle_kokiri_sword:
        pool.append('Kokiri Sword')
    else:
        placed_items['Kokiri Sword Chest'] = 'Kokiri Sword'

    if world.open_fountain:
        bottle = random.choice(normal_bottles)
        pool.append(bottle)
    else:
        pool.append('Bottle with Letter')

    if world.shuffle_weird_egg:
        pool.append('Weird Egg')
    else:
        placed_items['Malon Egg'] = 'Weird Egg'

    if world.shuffle_ocarinas:
        pool.extend(['Ocarina'] * 2)
    else:
        placed_items['Gift from Saria'] = 'Ocarina'
        placed_items['Ocarina of Time'] = 'Ocarina'

    if world.dungeon_mq['Deku Tree']:
        skulltula_locations_final = skulltula_locations + [
            'GS Deku Tree MQ Lobby',
            'GS Deku Tree MQ Compass Room',
            'GS Deku Tree MQ Basement Ceiling',
            'GS Deku Tree MQ Basement Back Room']
    else:
        skulltula_locations_final = skulltula_locations + [
            'GS Deku Tree Compass Room',
            'GS Deku Tree Basement Vines',
            'GS Deku Tree Basement Gate',
            'GS Deku Tree Basement Back Room']
    if world.dungeon_mq['Dodongos Cavern']:
        skulltula_locations_final.extend([
            'GS Dodongo\'s Cavern MQ Scrub Room',
            'GS Dodongo\'s Cavern MQ Song of Time Block Room',
            'GS Dodongo\'s Cavern MQ Lizalfos Room',
            'GS Dodongo\'s Cavern MQ Larva Room',
            'GS Dodongo\'s Cavern MQ Back Area'])
    else:
        skulltula_locations_final.extend([
            'GS Dodongo\'s Cavern East Side Room',
            'GS Dodongo\'s Cavern Vines Above Stairs',
            'GS Dodongo\'s Cavern Back Room',
            'GS Dodongo\'s Cavern Alcove Above Stairs',
            'GS Dodongo\'s Cavern Scarecrow'])
    if world.dungeon_mq['Jabu Jabus Belly']:
        skulltula_locations_final.extend([
            'GS Jabu Jabu MQ Tailpasaran Room',
            'GS Jabu Jabu MQ Invisible Enemies Room',
            'GS Jabu Jabu MQ Boomerang Room',
            'GS Jabu Jabu MQ Near Boss'])
    else:
        skulltula_locations_final.extend([
            'GS Jabu Jabu Water Switch Room',
            'GS Jabu Jabu Lobby Basement Lower',
            'GS Jabu Jabu Lobby Basement Upper',
            'GS Jabu Jabu Near Boss'])
    if world.dungeon_mq['Forest Temple']:
        skulltula_locations_final.extend([
            'GS Forest Temple MQ First Hallway',
            'GS Forest Temple MQ Block Push Room',
            'GS Forest Temple MQ Outdoor East',
            'GS Forest Temple MQ Outdoor West',
            'GS Forest Temple MQ Well'])
    else:
        skulltula_locations_final.extend([
            'GS Forest Temple First Room',
            'GS Forest Temple Lobby',
            'GS Forest Temple Outdoor East',
            'GS Forest Temple Outdoor West',
            'GS Forest Temple Basement'])
    if world.dungeon_mq['Fire Temple']:
        skulltula_locations_final.extend([
            'GS Fire Temple MQ Above Fire Wall Maze',
            'GS Fire Temple MQ Fire Wall Maze Center',
            'GS Fire Temple MQ Big Lava Room',
            'GS Fire Temple MQ Fire Wall Maze Side Room',
            'GS Fire Temple MQ East Tower Top'])
    else:
        skulltula_locations_final.extend([
            'GS Fire Temple Song of Time Room',
            'GS Fire Temple Unmarked Bomb Wall',
            'GS Fire Temple East Tower Climb',
            'GS Fire Temple East Tower Top',
            'GS Fire Temple Basement'])
    if world.dungeon_mq['Water Temple']:
        skulltula_locations_final.extend([
            'GS Water Temple MQ Before Upper Water Switch',
            'GS Water Temple MQ North Basement',
            'GS Water Temple MQ Lizalfos Hallway',
            'GS Water Temple MQ Serpent River',
            'GS Water Temple MQ South Basement'])
    else:
        skulltula_locations_final.extend([
            'GS Water Temple South Basement',
            'GS Water Temple Serpent River',
            'GS Water Temple Falling Platform Room',
            'GS Water Temple Central Room',
            'GS Water Temple Near Boss Key Chest'])
    if world.dungeon_mq['Spirit Temple']:
        skulltula_locations_final.extend([
            'GS Spirit Temple MQ Lower Adult Right',
            'GS Spirit Temple MQ Lower Adult Left',
            'GS Spirit Temple MQ Iron Knuckle West',
            'GS Spirit Temple MQ Iron Knuckle North',
            'GS Spirit Temple MQ Sun Block Room'])
    else:
        skulltula_locations_final.extend([
            'GS Spirit Temple Metal Fence',
            'GS Spirit Temple Bomb for Light Room',
            'GS Spirit Temple Hall to West Iron Knuckle',
            'GS Spirit Temple Boulder Room',
            'GS Spirit Temple Lobby'])
    if world.dungeon_mq['Shadow Temple']:
        skulltula_locations_final.extend([
            'GS Shadow Temple MQ Crusher Room',
            'GS Shadow Temple MQ Wind Hint Room',
            'GS Shadow Temple MQ After Wind',
            'GS Shadow Temple MQ After Ship',
            'GS Shadow Temple MQ Near Boss'])
    else:
        skulltula_locations_final.extend([
            'GS Shadow Temple Like Like Room',
            'GS Shadow Temple Crusher Room',
            'GS Shadow Temple Single Giant Pot',
            'GS Shadow Temple Near Ship',
            'GS Shadow Temple Triple Giant Pot'])
    if world.dungeon_mq['Bottom of the Well']:
        skulltula_locations_final.extend([
            'GS Well MQ Basement',
            'GS Well MQ Coffin Room',
            'GS Well MQ West Inner Room'])
    else:
        skulltula_locations_final.extend([
            'GS Well West Inner Room',
            'GS Well East Inner Room',
            'GS Well Like Like Cage'])
    if world.dungeon_mq['Ice Cavern']:
        skulltula_locations_final.extend([
            'GS Ice Cavern MQ Scarecrow',
            'GS Ice Cavern MQ Ice Block',
            'GS Ice Cavern MQ Red Ice'])
    else:
        skulltula_locations_final.extend([
            'GS Ice Cavern Spinning Scythe Room',
            'GS Ice Cavern Heart Piece Room',
            'GS Ice Cavern Push Block Room'])
    if world.tokensanity == 'off':
        for location in skulltula_locations_final:
            placed_items[location] = 'Gold Skulltula Token'
    elif world.tokensanity == 'dungeons':
        for location in skulltula_locations_final:
            if world.get_location(location).scene >= 0x0A:
                placed_items[location] = 'Gold Skulltula Token'
            else:
                pool.append('Gold Skulltula Token')
    else:
        pool.extend(['Gold Skulltula Token'] * 100)


    if world.bombchus_in_logic:
        pool.extend(['Bombchus'] * 4)
        if world.dungeon_mq['Jabu Jabus Belly']:
            pool.extend(['Bombchus'])
        if world.dungeon_mq['Spirit Temple']:
            pool.extend(['Bombchus'] * 2)
        if not world.dungeon_mq['Bottom of the Well']:
            pool.extend(['Bombchus'])
        if world.dungeon_mq['Gerudo Training Grounds']:
            pool.extend(['Bombchus'])

    else:
        pool.extend(['Bombchus (5)'] + ['Bombchus (10)'] * 2)
        if world.dungeon_mq['Jabu Jabus Belly']:
                pool.extend(['Bombchus (10)'])
        if world.dungeon_mq['Spirit Temple']:
                pool.extend(['Bombchus (10)'] * 2)
        if not world.dungeon_mq['Bottom of the Well']:
                pool.extend(['Bombchus (10)'])
        if world.dungeon_mq['Gerudo Training Grounds']:
                pool.extend(['Bombchus (10)'])
        if world.dungeon_mq['Ganons Castle']:
            pool.extend(['Bombchus (10)'])
        else:
            pool.extend(['Bombchus (20)'])

    pool.extend(['Ice Trap'])
    if not world.dungeon_mq['Gerudo Training Grounds']:
        pool.extend(['Ice Trap'])
    if not world.dungeon_mq['Ganons Castle']:
        pool.extend(['Ice Trap'] * 4)

    if world.gerudo_fortress == 'open':
        placed_items['Gerudo Fortress North F1 Carpenter'] = 'Recovery Heart'
        placed_items['Gerudo Fortress North F2 Carpenter'] = 'Recovery Heart'
        placed_items['Gerudo Fortress South F1 Carpenter'] = 'Recovery Heart'
        placed_items['Gerudo Fortress South F2 Carpenter'] = 'Recovery Heart'
    elif world.shuffle_smallkeys == 'keysanity':
        if world.gerudo_fortress == 'fast':
            pool.append('Small Key (Gerudo Fortress)')
            placed_items['Gerudo Fortress North F2 Carpenter'] = 'Recovery Heart'
            placed_items['Gerudo Fortress South F1 Carpenter'] = 'Recovery Heart'
            placed_items['Gerudo Fortress South F2 Carpenter'] = 'Recovery Heart'
        else:
            pool.extend(['Small Key (Gerudo Fortress)'] * 4)
    else:
        if world.gerudo_fortress == 'fast':
            placed_items['Gerudo Fortress North F1 Carpenter'] = 'Small Key (Gerudo Fortress)'
            placed_items['Gerudo Fortress North F2 Carpenter'] = 'Recovery Heart'
            placed_items['Gerudo Fortress South F1 Carpenter'] = 'Recovery Heart'
            placed_items['Gerudo Fortress South F2 Carpenter'] = 'Recovery Heart'
        else:
            placed_items['Gerudo Fortress North F1 Carpenter'] = 'Small Key (Gerudo Fortress)'
            placed_items['Gerudo Fortress North F2 Carpenter'] = 'Small Key (Gerudo Fortress)'
            placed_items['Gerudo Fortress South F1 Carpenter'] = 'Small Key (Gerudo Fortress)'
            placed_items['Gerudo Fortress South F2 Carpenter'] = 'Small Key (Gerudo Fortress)'

    if world.shuffle_gerudo_card and world.gerudo_fortress != 'open':
        pool.append('Gerudo Membership Card')
    else:
        placed_items['Gerudo Fortress Membership Card'] = 'Gerudo Membership Card'

    if world.shopsanity == 'off':
        placed_items.update(vanilla_shop_items)
        if world.bombchus_in_logic:
            placed_items['Kokiri Shop Item 8'] = 'Buy Bombchu (5)'
            placed_items['Castle Town Bazaar Item 4'] = 'Buy Bombchu (5)'
            placed_items['Kakariko Bazaar Item 4'] = 'Buy Bombchu (5)'
        pool.extend(normal_rupees)

    else:
        remain_shop_items = list(vanilla_shop_items.values())
        pool.extend(min_shop_items)
        for item in min_shop_items:
            remain_shop_items.remove(item)

        shop_slots_count = len(remain_shop_items)
        shop_nonitem_count = len(world.shop_prices)
        shop_item_count = shop_slots_count - shop_nonitem_count

        pool.extend(random.sample(remain_shop_items, shop_item_count))
        pool.extend(get_junk_item(shop_nonitem_count))
        if world.shopsanity == '0':
            pool.extend(normal_rupees)
        else:
            pool.extend(shopsanity_rupees)

    if world.shuffle_scrubs != 'off':
        if world.dungeon_mq['Deku Tree']:
            pool.append('Deku Shield')
        if world.dungeon_mq['Dodongos Cavern']:
            pool.extend(['Deku Stick (1)', 'Deku Shield', 'Recovery Heart'])
        else:
            pool.extend(['Deku Nuts (5)', 'Deku Stick (1)', 'Deku Shield'])
        if not world.dungeon_mq['Jabu Jabus Belly']:
            pool.append('Deku Nuts (5)')
        if world.dungeon_mq['Ganons Castle']:
            pool.extend(['Bombs (5)', 'Recovery Heart', 'Rupees (5)', 'Deku Nuts (5)'])
        else:
            pool.extend(['Bombs (5)', 'Recovery Heart', 'Rupees (5)'])
        pool.extend(deku_scrubs_items)
        for _ in range(7):
            pool.append('Arrows (30)' if random.randint(0,3) > 0 else 'Deku Seeds (30)')

    else:
        if world.dungeon_mq['Deku Tree']:
            placed_items['DT MQ Deku Scrub Deku Shield'] = 'Buy Deku Shield'
        if world.dungeon_mq['Dodongos Cavern']:
            placed_items['DC MQ Deku Scrub Deku Sticks'] = 'Buy Deku Stick (1)'
            placed_items['DC MQ Deku Scrub Deku Seeds'] = 'Buy Deku Seeds (30)'
            placed_items['DC MQ Deku Scrub Deku Shield'] = 'Buy Deku Shield'
            placed_items['DC MQ Deku Scrub Red Potion'] = 'Buy Red Potion [30]'
        else:
            placed_items['DC Deku Scrub Deku Nuts'] = 'Buy Deku Nut (5)'
            placed_items['DC Deku Scrub Deku Sticks'] = 'Buy Deku Stick (1)'
            placed_items['DC Deku Scrub Deku Seeds'] = 'Buy Deku Seeds (30)'
            placed_items['DC Deku Scrub Deku Shield'] = 'Buy Deku Shield'
        if not world.dungeon_mq['Jabu Jabus Belly']:
            placed_items['Jabu Deku Scrub Deku Nuts'] = 'Buy Deku Nut (5)'
        if world.dungeon_mq['Ganons Castle']:
            placed_items['GC MQ Deku Scrub Deku Nuts'] = 'Buy Deku Nut (5)'
            placed_items['GC MQ Deku Scrub Bombs'] = 'Buy Bombs (5) [35]'
            placed_items['GC MQ Deku Scrub Arrows'] = 'Buy Arrows (30)'
            placed_items['GC MQ Deku Scrub Red Potion'] = 'Buy Red Potion [30]'
            placed_items['GC MQ Deku Scrub Green Potion'] = 'Buy Green Potion'
        else:
            placed_items['GC Deku Scrub Bombs'] = 'Buy Bombs (5) [35]'
            placed_items['GC Deku Scrub Arrows'] = 'Buy Arrows (30)'
            placed_items['GC Deku Scrub Red Potion'] = 'Buy Red Potion [30]'
            placed_items['GC Deku Scrub Green Potion'] = 'Buy Green Potion'
        placed_items.update(vanilla_deku_scrubs)

    pool.extend(alwaysitems)
    
    if world.dungeon_mq['Deku Tree']:
        pool.extend(DT_MQ)
    else:
        pool.extend(DT_vanilla)
    if world.dungeon_mq['Dodongos Cavern']:
        pool.extend(DC_MQ)
    else:
        pool.extend(DC_vanilla)
    if world.dungeon_mq['Jabu Jabus Belly']:
        pool.extend(JB_MQ)
    if world.dungeon_mq['Forest Temple']:
        pool.extend(FoT_MQ)
    else:
        pool.extend(FoT_vanilla)
    if world.dungeon_mq['Fire Temple']:
        pool.extend(FiT_MQ)
    else:
        pool.extend(FiT_vanilla)
    if world.dungeon_mq['Spirit Temple']:
        pool.extend(SpT_MQ)
    else:
        placed_items['Spirit Temple Nut Crate'] = 'Deku Nut Drop'
        pool.extend(SpT_vanilla)
    if world.dungeon_mq['Shadow Temple']:
        pool.extend(ShT_MQ)
    else:
        pool.extend(ShT_vanilla)
    if not world.dungeon_mq['Bottom of the Well']:
        placed_items['Bottom of the Well Stick Pot'] = 'Deku Stick Drop'
        pool.extend(BW_vanilla)
    if world.dungeon_mq['Gerudo Training Grounds']:
        pool.extend(GTG_MQ)
    else:
        pool.extend(GTG_vanilla)
    if world.dungeon_mq['Ganons Castle']:
        pool.extend(GC_MQ)
    else:
        pool.extend(GC_vanilla)

    for _ in range(normal_bottle_count):
        bottle = random.choice(normal_bottles)
        pool.append(bottle)

    earliest_trade = tradeitemoptions.index(world.logic_earliest_adult_trade)
    latest_trade = tradeitemoptions.index(world.logic_latest_adult_trade)
    if earliest_trade > latest_trade:
        earliest_trade, latest_trade = latest_trade, earliest_trade
    tradeitem = random.choice(tradeitems[earliest_trade:latest_trade+1])
    pool.append(tradeitem)

    pool.extend(songlist)
    if world.start_with_fast_travel:
        pool.remove('Prelude of Light')
        pool.remove('Serenade of Water')
        pool.remove('Farores Wind')
        world.state.collect(ItemFactory('Prelude of Light'))
        world.state.collect(ItemFactory('Serenade of Water'))
        world.state.collect(ItemFactory('Farores Wind'))
        pool.extend(get_junk_item(3))

    if world.shuffle_mapcompass == 'remove' or world.shuffle_mapcompass == 'startwith':
        for item in [item for dungeon in world.dungeons for item in dungeon.dungeon_items]:
            world.state.collect(item)
            pool.extend(get_junk_item())
    if world.shuffle_smallkeys == 'remove':
        for item in [item for dungeon in world.dungeons for item in dungeon.small_keys]:
            world.state.collect(item)
            pool.extend(get_junk_item())
    if world.shuffle_bosskeys == 'remove':
        for item in [item for dungeon in world.dungeons for item in dungeon.boss_key]:
            world.state.collect(item)
            pool.extend(get_junk_item())
    if not world.keysanity and not world.dungeon_mq['Fire Temple']:
        world.state.collect(ItemFactory('Small Key (Fire Temple)'))
    if not world.dungeon_mq['Water Temple']:
        world.state.collect(ItemFactory('Small Key (Water Temple)'))

    if world.item_pool_value == 'plentiful':
        pool.extend(easy_items)
    else:
        pool.extend(normal_items)

    if not world.shuffle_kokiri_sword:
        replace_max_item(pool, 'Kokiri Sword', 0)

    if world.junk_ice_traps == 'off': 
        replace_max_item(pool, 'Ice Trap', 0)
    elif world.junk_ice_traps == 'onslaught':
        for item in [item for item, weight in junk_pool_base] + ['Recovery Heart', 'Bombs (20)', 'Arrows (30)']:
            replace_max_item(pool, item, 0)

    for item,max in item_difficulty_max[world.item_pool_value].items():
        replace_max_item(pool, item, max)

    if world.start_with_wallet:
        replace_max_item(pool, 'Progressive Wallet', 0)
        for i in [1, 2, 3]: # collect wallets
            world.state.collect(ItemFactory('Progressive Wallet'))

    return (pool, placed_items)


def choose_trials(world):
    if world.trials_random:
        world.trials = random.randint(0, 6)
    num_trials = int(world.trials)
    choosen_trials = random.sample(['Forest', 'Fire', 'Water', 'Spirit', 'Shadow', 'Light'], num_trials)
    for trial in world.skipped_trials:
        if trial not in choosen_trials:
            world.skipped_trials[trial] = True


def fill_bosses(world, bossCount=9):
    boss_rewards = ItemFactory(rewardlist, world)
    boss_locations = [
        world.get_location('Queen Gohma'),
        world.get_location('King Dodongo'),
        world.get_location('Barinade'),
        world.get_location('Phantom Ganon'),
        world.get_location('Volvagia'),
        world.get_location('Morpha'),
        world.get_location('Bongo Bongo'),
        world.get_location('Twinrova'),
        world.get_location('Links Pocket')]

    placed_prizes = [loc.item.name for loc in boss_locations if loc.item is not None]
    unplaced_prizes = [item for item in boss_rewards if item.name not in placed_prizes]
    empty_boss_locations = [loc for loc in boss_locations if loc.item is None]
    prizepool = list(unplaced_prizes)
    prize_locs = list(empty_boss_locations)

    while bossCount:
        bossCount -= 1
        random.shuffle(prizepool)
        random.shuffle(prize_locs)
        item = prizepool.pop()
        loc = prize_locs.pop()
        world.push_item(loc, item)
