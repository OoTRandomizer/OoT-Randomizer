from collections import namedtuple
import logging
import random
from Utils import random_choices
from Item import ItemFactory
from ItemList import item_table
from LocationList import location_groups


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

bottle_count = 4


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


fixedlocations = {
    'Ganon': 'Triforce',
    'Zeldas Letter': 'Zeldas Letter',
    'Pierre': 'Scarecrow Song',
    'Deliver Ruto\'s Letter': 'Deliver Letter',
    'Master Sword Pedestal': 'Time Travel',
    'Bombchu Bowling Bombchus': 'Bombchu Drop',
    'Haunted Wasteland Bombchu Salesman': 'Bombchus',
}

droplocations = {
    'Deku Baba Sticks': 'Deku Stick Drop',
    'Deku Baba Nuts': 'Deku Nut Drop',
    'Stick Pot': 'Deku Stick Drop',
    'Nut Pot': 'Deku Nut Drop',
    'Nut Crate': 'Deku Nut Drop',
    'Blue Fire': 'Blue Fire',
    'Lone Fish': 'Fish',
    'Fish Group': 'Fish',
    'Bug Rock': 'Bugs',
    'Bug Shrub': 'Bugs',
    'Wandering Bugs': 'Bugs',
    'Fairy Pot': 'Fairy',
    'Free Fairies': 'Fairy',
    'Butterfly Fairy': 'Fairy',
    'Gossip Stone Fairy': 'Fairy',
    'Bean Plant Fairy': 'Fairy',
    'Fairy Pond': 'Fairy',
    'Big Poe Kill': 'Big Poe',
}

vanillaBK = {
    'Fire Temple Boss Key Chest': 'Boss Key (Fire Temple)',
    'Shadow Temple Boss Key Chest': 'Boss Key (Shadow Temple)',
    'Spirit Temple Boss Key Chest': 'Boss Key (Spirit Temple)',
    'Water Temple Boss Key Chest': 'Boss Key (Water Temple)',
    'Forest Temple Boss Key Chest': 'Boss Key (Forest Temple)',

    'Fire Temple MQ Boss Key Chest': 'Boss Key (Fire Temple)',
    'Shadow Temple MQ Boss Key Chest': 'Boss Key (Shadow Temple)',
    'Spirit Temple MQ Boss Key Chest': 'Boss Key (Spirit Temple)',
    'Water Temple MQ Boss Key Chest': 'Boss Key (Water Temple)',
    'Forest Temple MQ Boss Key Chest': 'Boss Key (Forest Temple)',    
}

vanillaMC = {
    'Bottom of the Well Center Large Chest': 'Compass (Bottom of the Well)',
    'Deku Tree Compass Chest': 'Compass (Deku Tree)',
    'Dodongos Cavern Compass Chest': 'Compass (Dodongos Cavern)',
    'Fire Temple Compass Chest': 'Compass (Fire Temple)',
    'Forest Temple Blue Poe Chest': 'Compass (Forest Temple)',
    'Ice Cavern Compass Chest': 'Compass (Ice Cavern)',
    'Jabu Jabus Belly Compass Chest': 'Compass (Jabu Jabus Belly)',
    'Shadow Temple Compass Chest': 'Compass (Shadow Temple)',
    'Spirit Temple Compass Chest': 'Compass (Spirit Temple)',
    'Water Temple Compass Chest': 'Compass (Water Temple)',

    'Bottom of the Well Basement Chest': 'Map (Bottom of the Well)',
    'Deku Tree Lobby Chest': 'Map (Deku Tree)',
    'Dodongos Cavern Map Chest': 'Map (Dodongos Cavern)',
    'Fire Temple Map Chest': 'Map (Fire Temple)',
    'Forest Temple Map Chest': 'Map (Forest Temple)',
    'Ice Cavern Map Chest': 'Map (Ice Cavern)',
    'Jabu Jabus Belly Map Chest': 'Map (Jabu Jabus Belly)',
    'Shadow Temple Map Chest': 'Map (Shadow Temple)',
    'Spirit Temple Map Chest': 'Map (Spirit Temple)',
    'Water Temple Map Chest': 'Map (Water Temple)',

    'Bottom of the Well MQ Compass Chest': 'Compass (Bottom of the Well)',
    'Deku Tree MQ Compass Chest': 'Compass (Deku Tree)',
    'Dodongos Cavern MQ Compass Chest': 'Compass (Dodongos Cavern)',
    'Fire Temple MQ Compass Chest': 'Compass (Fire Temple)',
    'Forest Temple MQ Compass Chest': 'Compass (Forest Temple)',
    'Ice Cavern MQ Compass Chest': 'Compass (Ice Cavern)',
    'Jabu Jabus Belly MQ Compass Chest': 'Compass (Jabu Jabus Belly)',
    'Shadow Temple MQ Compass Chest': 'Compass (Shadow Temple)',
    'Spirit Temple MQ Compass Chest': 'Compass (Spirit Temple)',
    'Water Temple MQ Compass Chest': 'Compass (Water Temple)',

    'Bottom of the Well MQ Map Chest': 'Map (Bottom of the Well)',
    'Deku Tree MQ Lobby Chest': 'Map (Deku Tree)',
    'Dodongos Cavern MQ Map Chest': 'Map (Dodongos Cavern)',
    'Fire Temple MQ Map Chest': 'Map (Fire Temple)',
    'Forest Temple MQ Map Chest': 'Map (Forest Temple)',
    'Ice Cavern MQ Map Chest': 'Map (Ice Cavern)',
    'Jabu Jabus Belly MQ Map Chest': 'Map (Jabu Jabus Belly)',
    'Shadow Temple MQ Early Gibdos Chest': 'Map (Shadow Temple)',
    'Spirit Temple MQ Map Chest': 'Map (Spirit Temple)',
    'Water Temple MQ Map Chest': 'Map (Water Temple)',
}

vanillaSK = {
    'Bottom of the Well Front Left Hidden Wall': 'Small Key (Bottom of the Well)',
    'Bottom of the Well Right Bottom Hidden Wall': 'Small Key (Bottom of the Well)',
    'Bottom of the Well Freestanding Key': 'Small Key (Bottom of the Well)',
    'Fire Temple Big Lava Room Bombable Chest': 'Small Key (Fire Temple)',
    'Fire Temple Big Lava Room Open Chest': 'Small Key (Fire Temple)',
    'Fire Temple Boulder Maze Bombable Pit': 'Small Key (Fire Temple)',
    'Fire Temple Boulder Maze Lower Chest': 'Small Key (Fire Temple)',
    'Fire Temple Boulder Maze Side Room': 'Small Key (Fire Temple)',
    'Fire Temple Boulder Maze Upper Chest': 'Small Key (Fire Temple)',
    'Fire Temple Chest Near Boss': 'Small Key (Fire Temple)',
    'Fire Temple Highest Goron Chest': 'Small Key (Fire Temple)',
    'Forest Temple Chest Behind Lobby': 'Small Key (Forest Temple)',
    'Forest Temple First Chest': 'Small Key (Forest Temple)',
    'Forest Temple Floormaster Chest': 'Small Key (Forest Temple)',
    'Forest Temple Red Poe Chest': 'Small Key (Forest Temple)',
    'Forest Temple Well Chest': 'Small Key (Forest Temple)',
    'Ganons Castle Light Trial Invisible Enemies Chest': 'Small Key (Ganons Castle)',
    'Ganons Castle Light Trial Lullaby Chest': 'Small Key (Ganons Castle)',
    'Gerudo Training Grounds Beamos Chest': 'Small Key (Gerudo Training Grounds)',
    'Gerudo Training Grounds Eye Statue Chest': 'Small Key (Gerudo Training Grounds)',
    'Gerudo Training Grounds Hammer Room Switch Chest': 'Small Key (Gerudo Training Grounds)',
    'Gerudo Training Grounds Heavy Block Third Chest': 'Small Key (Gerudo Training Grounds)',
    'Gerudo Training Grounds Hidden Ceiling Chest': 'Small Key (Gerudo Training Grounds)',
    'Gerudo Training Grounds Near Scarecrow Chest': 'Small Key (Gerudo Training Grounds)',
    'Gerudo Training Grounds Stalfos Chest': 'Small Key (Gerudo Training Grounds)',
    'Gerudo Training Grounds Underwater Silver Rupee Chest': 'Small Key (Gerudo Training Grounds)',
    'Gerudo Training Grounds Freestanding Key': 'Small Key (Gerudo Training Grounds)',
    'Shadow Temple After Wind Hidden Chest': 'Small Key (Shadow Temple)',
    'Shadow Temple Early Silver Rupee Chest': 'Small Key (Shadow Temple)',
    'Shadow Temple Falling Spikes Switch Chest': 'Small Key (Shadow Temple)',
    'Shadow Temple Hidden Floormaster Chest': 'Small Key (Shadow Temple)',
    'Shadow Temple Freestanding Key': 'Small Key (Shadow Temple)',
    'Spirit Temple Child Right Chest': 'Small Key (Spirit Temple)',
    'Spirit Temple Early Adult Right Chest': 'Small Key (Spirit Temple)',
    'Spirit Temple Near Four Armos Chest': 'Small Key (Spirit Temple)',
    'Spirit Temple Statue Hand Chest': 'Small Key (Spirit Temple)',
    'Spirit Temple Sun Block Room Chest': 'Small Key (Spirit Temple)',
    'Water Temple Central Bow Target Chest': 'Small Key (Water Temple)',
    'Water Temple Central Pillar Chest': 'Small Key (Water Temple)',
    'Water Temple Cracked Wall Chest': 'Small Key (Water Temple)',
    'Water Temple Dragon Chest': 'Small Key (Water Temple)',
    'Water Temple River Chest': 'Small Key (Water Temple)',
    'Water Temple Torches Chest': 'Small Key (Water Temple)',

    'Bottom of the Well MQ Dead Hand Freestanding Key': 'Small Key (Bottom of the Well)',
    'Bottom of the Well MQ East Inner Room Freestanding Key': 'Small Key (Bottom of the Well)',
    'Fire Temple MQ Big Lava Room Bombable Chest': 'Small Key (Fire Temple)',
    'Fire Temple MQ Chest Near Boss': 'Small Key (Fire Temple)',
    'Fire Temple MQ Maze Side Room': 'Small Key (Fire Temple)',
    'Fire Temple MQ West Tower Top Chest': 'Small Key (Fire Temple)',
    'Fire Temple MQ Freestanding Key': 'Small Key (Fire Temple)',
    'Forest Temple MQ Chest Behind Lobby': 'Small Key (Forest Temple)',
    'Forest Temple MQ First Chest': 'Small Key (Forest Temple)',
    'Forest Temple MQ NE Outdoors Lower Chest': 'Small Key (Forest Temple)',
    'Forest Temple MQ NE Outdoors Upper Chest': 'Small Key (Forest Temple)',
    'Forest Temple MQ Redead Chest': 'Small Key (Forest Temple)',
    'Forest Temple MQ Well Chest': 'Small Key (Forest Temple)',
    'Ganons Castle MQ Shadow Trial Second Chest': 'Small Key (Ganons Castle)',
    'Ganons Castle MQ Spirit Trial Sun Back Left Chest': 'Small Key (Ganons Castle)',
    'Ganons Castle MQ Forest Trial Freestanding Key': 'Small Key (Ganons Castle)',
    'Gerudo Training Grounds MQ Dinolfos Chest': 'Small Key (Gerudo Training Grounds)',
    'Gerudo Training Grounds MQ Flame Circle Chest': 'Small Key (Gerudo Training Grounds)',
    'Gerudo Training Grounds MQ Underwater Silver Rupee Chest': 'Small Key (Gerudo Training Grounds)',
    'Shadow Temple MQ Falling Spikes Switch Chest': 'Small Key (Shadow Temple)',
    'Shadow Temple MQ Invisible Blades Invisible Chest': 'Small Key (Shadow Temple)',
    'Shadow Temple MQ Map Chest': 'Small Key (Shadow Temple)',
    'Shadow Temple MQ Near Ship Invisible Chest': 'Small Key (Shadow Temple)',
    'Shadow Temple MQ Wind Hint Chest': 'Small Key (Shadow Temple)',
    'Shadow Temple MQ Freestanding Key': 'Small Key (Shadow Temple)',
    'Spirit Temple MQ Child Center Chest': 'Small Key (Spirit Temple)',
    'Spirit Temple MQ Child Climb South Chest': 'Small Key (Spirit Temple)',
    'Spirit Temple MQ Child Left Chest': 'Small Key (Spirit Temple)',
    'Spirit Temple MQ Entrance Back Left Chest': 'Small Key (Spirit Temple)',
    'Spirit Temple MQ Entrance Front Right Chest': 'Small Key (Spirit Temple)',
    'Spirit Temple MQ Mirror Puzzle Invisible Chest': 'Small Key (Spirit Temple)',
    'Spirit Temple MQ Silver Block Hallway Chest': 'Small Key (Spirit Temple)',
    'Water Temple MQ Central Pillar Chest': 'Small Key (Water Temple)',
    'Water Temple MQ Freestanding Key': 'Small Key (Water Temple)',    
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

pending_junk_pool = []
junk_pool = []


remove_junk_items = [
    'Bombs (5)',
    'Deku Nuts (5)',
    'Deku Stick (1)',
    'Recovery Heart',
    'Arrows (5)',
    'Arrows (10)',
    'Arrows (30)',
    'Rupees (5)',
    'Rupees (20)',
    'Rupees (50)',
    'Rupees (200)',
    'Deku Nuts (10)',
    'Bombs (10)',
    'Bombs (20)',
    'Deku Seeds (30)',
    'Ice Trap',
]


item_groups = {
    'Junk': remove_junk_items,
    'JunkSong': ('Prelude of Light', 'Serenade of Water'),
    'AdultTrade': tradeitems,
    'Bottle': normal_bottles,
    'Spell': ('Dins Fire', 'Farores Wind', 'Nayrus Love'),
    'Shield': ('Deku Shield', 'Hylian Shield'),
    'Song': songlist,
    'NonWarpSong': songlist[0:6],
    'WarpSong': songlist[6:],
    'HealthUpgrade': ('Heart Container', 'Piece of Heart'),
    'ProgressItem': [name for (name, data) in item_table.items() if data[0] == 'Item' and data[1]],

    'ForestFireWater': ('Forest Medallion', 'Fire Medallion', 'Water Medallion'),
    'FireWater': ('Fire Medallion', 'Water Medallion'),
}


def get_junk_item(count=1):
    if count < 1:
        raise ValueError("get_junk_item argument 'count' must be greater than 0.")

    return_pool = []
    if pending_junk_pool:
        pending_count = min(len(pending_junk_pool), count)
        return_pool = [pending_junk_pool.pop() for _ in range(pending_count)]
        count -= pending_count

    junk_items, junk_weights = zip(*junk_pool)
    return_pool.extend(random_choices(junk_items, weights=junk_weights, k=count))

    return return_pool


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

    fixed_locations = list(filter(lambda loc: loc.name in fixedlocations, world.get_locations()))
    for location in fixed_locations:
        item = fixedlocations[location.name]
        world.push_item(location, ItemFactory(item, world))
        location.locked = True

    drop_locations = list(filter(lambda loc: loc.type == 'Drop', world.get_locations()))
    for drop_location in drop_locations:
        item = droplocations[drop_location.name]
        world.push_item(drop_location, ItemFactory(item, world))
        drop_location.locked = True

    # set up item pool
    (pool, placed_items) = get_pool_core(world)
    world.itempool = ItemFactory(pool, world)
    for (location, item) in placed_items.items():
        world.push_item(location, ItemFactory(item, world))
        world.get_location(location).locked = True

    world.initialize_items()


def get_pool_core(world):
    pool = []
    placed_items = {}

    if world.shuffle_kokiri_sword:
        pool.append('Kokiri Sword')
    else:
        placed_items['Kokiri Sword Chest'] = 'Kokiri Sword'

    ruto_bottles = 1
    if world.open_fountain:
        ruto_bottles = 0
    elif world.item_pool_value == 'plentiful':
        ruto_bottles += 1

    if world.shuffle_weird_egg:
        pool.append('Weird Egg')
    else:
        placed_items['Malon Egg'] = 'Weird Egg'

    if world.shuffle_ocarinas:
        pool.extend(['Ocarina'] * 2)
    else:
        placed_items['Gift from Saria'] = 'Ocarina'
        placed_items['Ocarina of Time'] = 'Ocarina'

    if world.shuffle_cows:
        pool.extend(get_junk_item(10 if world.dungeon_mq['Jabu Jabus Belly'] else 9))
    else:
        placed_items['LLR Stables Left Cow'] = 'Milk'
        placed_items['LLR Stables Right Cow'] = 'Milk'
        placed_items['LLR Tower Left Cow'] = 'Milk'
        placed_items['LLR Tower Right Cow'] = 'Milk'
        placed_items['Links House Cow'] = 'Milk'
        placed_items['Impas House Cow'] = 'Milk'
        placed_items['Gerudo Valley Cow'] = 'Milk'
        placed_items['DMT Grotto Cow'] = 'Milk'
        placed_items['HF Grotto Cow'] = 'Milk'
        if world.dungeon_mq['Jabu Jabus Belly']:
            placed_items['Jabu Jabus Belly MQ Cow'] = 'Milk'

    if world.shuffle_beans:
        pool.append('Magic Bean Pack')
    else:
        placed_items['Magic Bean Salesman'] = 'Magic Bean'

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
    elif world.shuffle_gerudo_card:
        pending_junk_pool.append('Gerudo Membership Card')
        placed_items['Gerudo Fortress Membership Card'] = 'Ice Trap'
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
        if shop_nonitem_count:
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
        pool.extend(SpT_vanilla)
    if world.dungeon_mq['Shadow Temple']:
        pool.extend(ShT_MQ)
    else:
        pool.extend(ShT_vanilla)
    if not world.dungeon_mq['Bottom of the Well']:
        pool.extend(BW_vanilla)
    if world.dungeon_mq['Gerudo Training Grounds']:
        pool.extend(GTG_MQ)
    else:
        pool.extend(GTG_vanilla)
    if world.dungeon_mq['Ganons Castle']:
        pool.extend(GC_MQ)
    else:
        pool.extend(GC_vanilla)

    for i in range(bottle_count):
        if i >= ruto_bottles:
            bottle = random.choice(normal_bottles)
            pool.append(bottle)
        else:
            pool.append('Bottle with Letter')

    earliest_trade = tradeitemoptions.index(world.logic_earliest_adult_trade)
    latest_trade = tradeitemoptions.index(world.logic_latest_adult_trade)
    if earliest_trade > latest_trade:
        earliest_trade, latest_trade = latest_trade, earliest_trade
    tradeitem = random.choice(tradeitems[earliest_trade:latest_trade+1])
    world.selected_adult_trade_item = tradeitem
    pool.append(tradeitem)

    pool.extend(songlist)
    if world.start_with_fast_travel:
        pool.remove('Prelude of Light')
        pool.remove('Serenade of Water')
        pool.remove('Farores Wind')
        pool.extend(get_junk_item(3))
        
    if world.free_scarecrow:
        world.state.collect(ItemFactory('Scarecrow Song'))
    
    if world.no_epona_race:
        world.state.collect(ItemFactory('Epona', event=True))

    if world.shuffle_mapcompass == 'remove' or world.shuffle_mapcompass == 'startwith':
        for item in [item for dungeon in world.dungeons for item in dungeon.dungeon_items]:
            world.state.collect(item)
            pool.extend(get_junk_item())
    if world.shuffle_smallkeys == 'remove':
        for item in [item for dungeon in world.dungeons for item in dungeon.small_keys]:
            world.state.collect(item)
            pool.extend(get_junk_item())
    if world.shuffle_bosskeys == 'remove':
        for item in [item for dungeon in world.dungeons if dungeon.name != 'Ganons Castle' for item in dungeon.boss_key]:
            world.state.collect(item)
            pool.extend(get_junk_item())
    if world.shuffle_ganon_bosskey == 'remove':
        for item in [item for dungeon in world.dungeons if dungeon.name == 'Ganons Castle' for item in dungeon.boss_key]:
            world.state.collect(item)
            pool.extend(get_junk_item())

    if world.shuffle_mapcompass == 'vanilla':
        for location, item in vanillaMC.items():
            try:
                world.get_location(location)
                placed_items[location] = item
            except KeyError:
                continue
    if world.shuffle_smallkeys == 'vanilla':
        for location, item in vanillaSK.items():
            try:
                world.get_location(location)
                placed_items[location] = item
            except KeyError:
                continue
        # Logic cannot handle vanilla key layout in some dungeons
        # this is because vanilla expects the dungeon major item to be
        # locked behind the keys, which is not always true in rando.
        # We can resolve this by starting with some extra keys
        if world.dungeon_mq['Spirit Temple']:
            # Yes somehow you need 3 keys. This dungeon is bonkers
            world.state.collect(ItemFactory('Small Key (Spirit Temple)'))
            world.state.collect(ItemFactory('Small Key (Spirit Temple)'))
            world.state.collect(ItemFactory('Small Key (Spirit Temple)'))
        #if not world.dungeon_mq['Fire Temple']:
        #    world.state.collect(ItemFactory('Small Key (Fire Temple)'))
    if world.shuffle_bosskeys == 'vanilla':
        for location, item in vanillaBK.items():
            try:
                world.get_location(location)
                placed_items[location] = item
            except KeyError:
                continue

    if world.shuffle_ganon_bosskey == 'vanilla':
        placed_items['Ganons Tower Boss Key Chest'] = 'Boss Key (Ganons Castle)'

    if not world.keysanity and not world.dungeon_mq['Fire Temple']:
        world.state.collect(ItemFactory('Small Key (Fire Temple)'))
    if not world.dungeon_mq['Water Temple']:
        world.state.collect(ItemFactory('Small Key (Water Temple)'))

    if world.shuffle_ganon_bosskey in ['lacs_vanilla', 'lacs_medallions', 'lacs_stones', 'lacs_dungeons']:
        placed_items['Zelda'] = 'Boss Key (Ganons Castle)'

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

    # Make sure our pending_junk_pool is empty. If not, remove some random junk here.
    if pending_junk_pool:
        remove_junk_pool, _ = zip(*junk_pool_base)
        remove_junk_pool = list(remove_junk_pool) + ['Recovery Heart', 'Bombs (20)', 'Arrows (30)', 'Ice Trap']

        junk_candidates = [item for item in pool if item in remove_junk_pool]
        while pending_junk_pool:
            pending_item = pending_junk_pool.pop()
            if not junk_candidates:
                raise RuntimeError("Not enough junk exists in item pool for %s to be added." % pending_item)
            junk_item = random.choice(junk_candidates)
            junk_candidates.remove(junk_item)
            pool.remove(junk_item)
            pool.append(pending_item)

    world.distribution.alter_pool(world, pool)

    world.distribution.configure_stating_items_settings(world)
    world.distribution.collect_starters(world.state)

    return (pool, placed_items)
