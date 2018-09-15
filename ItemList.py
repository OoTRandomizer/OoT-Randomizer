from collections import namedtuple
import logging
import random

from Items import ItemFactory

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
    'Rupee (1)'] 
    + ['Progressive Hookshot'] * 2
    + ['Deku Shield'] * 4
    + ['Hylian Shield'] * 2
    + ['Progressive Strength Upgrade'] * 3
    + ['Progressive Scale'] * 2
    + ['Recovery Heart'] * 9
    + ['Bow'] * 3
    + ['Slingshot'] * 3
    + ['Bomb Bag'] * 3
    + ['Bottle with Letter']
    + ['Bombs (5)'] * 2
    + ['Bombs (10)'] * 2
    + ['Bombs (20)'] * 2
    + ['Arrows (5)']
    + ['Arrows (10)'] * 6
    + ['Arrows (30)'] * 6
    + ['Deku Nuts (5)']
    + ['Deku Nuts (10)']
    + ['Progressive Wallet'] * 2
    + ['Deku Stick Capacity'] * 2
    + ['Deku Nut Capacity'] * 2
    + ['Magic Meter'])

DT_vanilla = (['Recovery Heart'] * 2)

DT_MQ = (['Deku Shield'] * 2
         + ['Rupees (50)'])

DC_vanilla = (['Rupees (20)'])

DC_MQ = (['Hylian Shield']
         + ['Rupees (5)'])

normal_bottles = [
    'Bottle',
    'Bottle with Milk',
    'Bottle with Red Potion',
    'Bottle with Green Potion',
    'Bottle with Blue Potion',
    'Bottle with Fairy',
    'Bottle with Fish',
    'Bottle with Bugs',
    'Bottle with Poe'] # 'Bottle with Blue Fire'

normal_bottle_count = 3

# 10 items get removed for hard+
harditems = (
    ['Bombs (5)'] * 2 
    + ['Arrows (5)'] * 2 
    + ['Deku Nuts (5)'] * 2 
    + ['Rupees (5)'] * 3 
    + ['Rupees (20)'])

# 37 items get removed for very hard
veryharditems = (
    ['Bombs (5)'] * 8 
    + ['Arrows (5)'] * 8 
    + ['Deku Nuts (5)'] * 8 
    + ['Rupees (5)'] * 10 
    + ['Rupees (20)'] * 2 
    + ['Rupees (50)'])

normal_rupees =(
    ['Rupees (5)'] * 16
    + ['Rupees (20)'] * 5
    + ['Rupees (50)'] * 7
    + ['Rupees (200)'] * 6)

shopsanity_rupees = (
    ['Rupees (5)'] * 5
    + ['Rupees (20)'] * 10
    + ['Rupees (50)'] * 10
    + ['Rupees (200)'] * 8
    + ['Progressive Wallet'])

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
      ['Buy Deku Shield'] 
    + ['Buy Hylian Shield'] 
    + ['Buy Goron Tunic'] 
    + ['Buy Zora Tunic'] 
    + ['Buy Deku Nut (5)'] * 2 + ['Buy Deku Nut (10)']
    + ['Buy Deku Stick (1)'] * 2 
    + ['Buy Deku Seeds (30)']
    + ['Buy Arrows (10)'] * 2 + ['Buy Arrows (30)'] + ['Buy Arrows (50)']
    + ['Buy Bombchu (5)'] + ['Buy Bombchu (10)'] * 2 + ['Buy Bombchu (20)']
    + ['Buy Bombs (5) [25]'] + ['Buy Bombs (5) [35]'] + ['Buy Bombs (10)'] + ['Buy Bombs (20)'] 
    + ['Buy Green Potion']
    + ['Buy Red Potion [30]']
    + ['Buy Blue Fire']
    + ['Buy Fairy\'s Spirit']
    + ['Buy Bottle Bug']
    + ['Buy Fish'])

vanilla_deku_scrubs = {
    'DC Deku Scrub Deku Nuts': 'Buy Deku Nut (5)',
    'DC Deku Scrub Deku Sticks': 'Buy Deku Stick (1)',
    'DC Deku Scrub Deku Seeds': 'Buy Deku Seeds (30)',
    'DC Deku Scrub Deku Shield': 'Buy Deku Shield',
    'Jabu Deku Scrub Deku Nuts': 'Buy Deku Nut (5)',
    'GC Deku Scrub Bombs': 'Buy Bombs (5) [35]',
    'GC Deku Scrub Arrows': 'Buy Arrows (30)',
    'GC Deku Scrub Red Potion': 'Buy Red Potion [30]',
    'GC Deku Scrub Green Potion': 'Buy Green Potion',
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
      ['Deku Nuts (5)'] * 7
    + ['Rupees (20)'] * 2  # ['Deku Stick (1)'] * 2
    + ['Arrows (5)'] # ['Deku Seeds (30)']
    + ['Deku Shield']
    + ['Bombs (5)'] * 6
    + ['Arrows (30)'] * 6
    + ['Recovery Heart'] * 5
    + ['Rupees (5)'] * 5 # ['Green Potion']
)

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

skulltulla_locations = ([
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
    'GS Jabu Jabu Water Switch Room',
    'GS Jabu Jabu Lobby Basement Lower',
    'GS Jabu Jabu Lobby Basement Upper',
    'GS Jabu Jabu Near Boss',
    'GS Lake Hylia Bean Patch',
    'GS Lake Hylia Lab Wall',
    'GS Lake Hylia Small Island',
    'GS Lake Hylia Giant Tree',
    'GS Lab Underwater Crate',
    'GS Forest Temple First Room',
    'GS Forest Temple Lobby',
    'GS Forest Temple Outdoor East',
    'GS Forest Temple Outdoor West',
    'GS Forest Temple Basement',
    'GS Fire Temple Song of Time Room',
    'GS Fire Temple Unmarked Bomb Wall',
    'GS Fire Temple East Tower Climb',
    'GS Fire Temple East Tower Top',
    'GS Fire Temple Basement',
    'GS Ice Cavern Spinning Scythe Room',
    'GS Ice Cavern Heart Piece Room',
    'GS Ice Cavern Push Block Room',
    'GS Water Temple South Basement',
    'GS Water Temple Serpent River',
    'GS Water Temple Falling Platform Room',
    'GS Water Temple Central Room',
    'GS Water Temple Near Boss Key Chest',
    'GS Well West Inner Room',
    'GS Well East Inner Room',
    'GS Well Like Like Cage',
    'GS Shadow Temple Like Like Room',
    'GS Shadow Temple Crusher Room',
    'GS Shadow Temple Single Giant Pot',
    'GS Shadow Temple Near Ship',
    'GS Shadow Temple Tripple Giant Pot',
    'GS Gerudo Valley Small Bridge',
    'GS Gerudo Valley Bean Patch',
    'GS Gerudo Valley Behind Tent',
    'GS Gerudo Valley Pillar',
    'GS Gerudo Fortress Archery Range',
    'GS Gerudo Fortress Top Floor',
    'GS Wasteland Ruins',
    'GS Desert Colossus Bean Patch',
    'GS Desert Colossus Tree',
    'GS Desert Colossus Hill',
    'GS Spirit Temple Metal Fence',
    'GS Spirit Temple Bomb for Light Room',
    'GS Spirit Temple Hall to West Iron Knuckle',
    'GS Spirit Temple Boulder Room',
    'GS Spirit Temple Lobby'])
    
tradeitems = [
    'Pocket Egg',
    'Pocket Cucco', 
    'Cojiro', 
    'Odd Mushroom', 
    'Poachers Saw', 
    'Broken Sword', 
    'Prescription', 
    'Eyeball Frog', 
    'Eyedrops', 
    'Claim Check']


eventlocations = {
    'Ganon': 'Triforce',
    'Zeldas Letter': 'Zeldas Letter',
    'Magic Bean Salesman': 'Magic Bean',
    'King Zora Moves': 'Bottle',
    'Master Sword Pedestal': 'Master Sword',
    'Epona': 'Epona',
    'Gerudo Fortress Carpenter Rescue': 'Carpenter Rescue',
    'Ganons Castle Forest Trial Clear': 'Forest Trial Clear',
    'Ganons Castle Fire Trial Clear': 'Fire Trial Clear',
    'Ganons Castle Water Trial Clear': 'Water Trial Clear',
    'Ganons Castle Shadow Trial Clear': 'Shadow Trial Clear',
    'Ganons Castle Spirit Trial Clear': 'Spirit Trial Clear',
    'Ganons Castle Light Trial Clear': 'Light Trial Clear'
}

#total_items_to_place = 5

def generate_itempool(world):
    for location, item in eventlocations.items():
        world.push_item(location, ItemFactory(item))
        world.get_location(location).event = True

    # set up item pool
    (pool, placed_items) = get_pool_core(world)
    world.itempool = ItemFactory(pool)
    for (location, item) in placed_items.items():
        new_item = ItemFactory(item)
        new_item.world = world
        world.push_item(location, new_item)
        world.get_location(location).event = True

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

    if world.shuffle_weird_egg:
        pool.append('Weird Egg')
    else:
        placed_items['Malon Egg'] = 'Weird Egg'

    if world.shuffle_ocarinas:
        pool.extend(['Ocarina'] * 2)
    else:
        placed_items['Gift from Saria'] = 'Ocarina'
        placed_items['Ocarina of Time'] = 'Ocarina'

    if world.dungeon_mq['DT']:
        skulltulla_locations_final = skulltulla_locations + [
            'GS Deku Tree MQ Lobby',
            'GS Deku Tree MQ Compass Room',
            'GS Deku Tree MQ Basement Ceiling',
            'GS Deku Tree MQ Basement Back Room']
    else:
        skulltulla_locations_final = skulltulla_locations + [
            'GS Deku Tree Compass Room',
            'GS Deku Tree Basement Vines',
            'GS Deku Tree Basement Gate',
            'GS Deku Tree Basement Back Room']
    if world.dungeon_mq['DC']:
        skulltulla_locations_final.extend([
            'GS Dodongo\'s Cavern MQ Scrub Room',
            'GS Dodongo\'s Cavern MQ Song of Time Block Room',
            'GS Dodongo\'s Cavern MQ Lizalfos Room',
            'GS Dodongo\'s Cavern MQ Larva Room',
            'GS Dodongo\'s Cavern MQ Back Area'])
    else:
        skulltulla_locations_final.extend([
            'GS Dodongo\'s Cavern East Side Room',
            'GS Dodongo\'s Cavern Vines Above Stairs',
            'GS Dodongo\'s Cavern Back Room',
            'GS Dodongo\'s Cavern Alcove Above Stairs',
            'GS Dodongo\'s Cavern Scarecrow'])
    if world.tokensanity == 'off':
        for location in skulltulla_locations_final:
            placed_items[location] = 'Gold Skulltulla Token'
    elif world.tokensanity == 'dungeons':
        for location in skulltulla_locations_final:
            if world.get_location(location).scene >= 0x0A:
                placed_items[location] = 'Gold Skulltulla Token'
            else:
                pool.append('Gold Skulltulla Token')
    else:
        pool.extend(['Gold Skulltulla Token'] * 100)

    if world.bombchus_in_logic:
        pool.extend(['Bombchus'] * 5)
    else:
        pool.extend(['Bombchus (5)'] + ['Bombchus (10)'] * 3 + ['Bombchus (20)'])

    if world.difficulty == 'ohko':
        pool.extend(['Recovery Heart'] * 6)
    else:
        pool.extend(['Ice Trap'] * 6)        

    if world.difficulty == 'normal':
        pool.extend(['Magic Meter', 'Double Defense'] + ['Heart Container'] * 8)
    else:
        pool.extend(harditems)

    if world.difficulty == 'very_hard' or world.difficulty == 'ohko':
        pool.extend(veryharditems)
    else:
        pool.extend(['Nayrus Love', 'Piece of Heart (Treasure Chest Game)'] + ['Piece of Heart'] * 35)

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
        remain_shop_items = [item for _,item in vanilla_shop_items.items()]
        pool.extend(min_shop_items)
        for item in min_shop_items:
            remain_shop_items.remove(item)

        shop_slots_count = len(remain_shop_items)
        shop_nonitem_count = len(world.shop_prices)
        shop_item_count = shop_slots_count - shop_nonitem_count

        pool.extend(random.sample(remain_shop_items, shop_item_count))
        pool.extend(random.sample(veryharditems, shop_nonitem_count))
        pool.extend(shopsanity_rupees)

    if world.shuffle_scrubs:
        pool.extend(deku_scrubs_items)
    else:        
        placed_items.update(vanilla_deku_scrubs)

    pool.extend(alwaysitems)
    if world.dungeon_mq['DT']:
        pool.extend(DT_MQ)
    else:
        pool.extend(DT_vanilla)
    if world.dungeon_mq['DC']:
        pool.extend(DC_MQ)
    else:
        pool.extend(DC_vanilla)
    for _ in range(normal_bottle_count):
        bottle = random.choice(normal_bottles)
        pool.append(bottle)
    tradeitem = random.choice(tradeitems)
    pool.append(tradeitem)
    pool.extend(songlist)

    if world.shuffle_mapcompass == 'remove':
        for item in [item for dungeon in world.dungeons for item in dungeon.dungeon_items]:
            world.state.collect(item)
            pool.append(random.choice(harditems))
    if world.shuffle_smallkeys == 'remove':
        for item in [item for dungeon in world.dungeons for item in dungeon.small_keys]:
            world.state.collect(item)
            pool.append(random.choice(harditems))
    if world.shuffle_bosskeys == 'remove':
        for item in [item for dungeon in world.dungeons for item in dungeon.boss_key]:
            world.state.collect(item)
            pool.append(random.choice(harditems))
    if not world.keysanity and not world.dungeon_mq['FiT']:
        world.state.collect(ItemFactory('Small Key (Fire Temple)'))


    return (pool, placed_items)

def choose_trials(world):
    choosen_trials=[]
    if world.trials_random:
        for trial in ['Forest', 'Fire', 'Water', 'Spirit', 'Shadow', 'Light']:
            flag = random.randint(0,1)
            if flag==1:
                choosen_trials.append(trial)

        world.trials = len(choosen_trials)
    else:
        num_trials = int(world.trials)
        choosen_trials = random.sample(['Forest', 'Fire', 'Water', 'Spirit', 'Shadow', 'Light'], num_trials)
    for trial in world.skipped_trials:
        if trial not in choosen_trials:
            world.skipped_trials[trial] = True

def fill_bosses(world, bossCount=9):
    boss_rewards = ItemFactory(rewardlist)
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
