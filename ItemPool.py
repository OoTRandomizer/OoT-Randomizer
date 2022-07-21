import random
from collections import OrderedDict
from decimal import Decimal, ROUND_UP

from Item import ItemFactory, ItemInfo
from Utils import random_choices


# Generates item pools and places fixed items based on settings.

plentiful_items = ([
    'Biggoron Sword',
    'Boomerang',
    'Lens of Truth',
    'Megaton Hammer',
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
    ['Heart Container'] * 8
)

# Ludicrous replaces all health upgrades with heart containers
# as done in plentiful. The item list is used separately to
# dynamically replace all junk with even levels of each item.
ludicrous_health = ['Heart Container'] * 8

# List of items that can be multiplied in ludicrous mode.
# Used to filter the pre-plando pool for candidates instead
# of appending directly, making this list settings-independent.
# Excludes Gold Skulltula Tokens, Triforce Pieces, and health
# upgrades as they are directly tied to win conditions and
# already have a large count relative to available locations
# in the game.
#
# Base items will always be candidates to replace junk items,
# even if the player starts with all "normal" copies of an item.
ludicrous_items_base = [
    'Light Arrows',
    'Megaton Hammer',
    'Progressive Hookshot',
    'Progressive Strength Upgrade',
    'Dins Fire',
    'Hover Boots',
    'Mirror Shield',
    'Boomerang',
    'Iron Boots',
    'Fire Arrows',
    'Progressive Scale',
    'Progressive Wallet',
    'Magic Meter',
    'Bow',
    'Slingshot',
    'Bomb Bag',
    'Bombchus',
    'Lens of Truth',
    'Goron Tunic',
    'Zora Tunic',
    'Biggoron Sword',
    'Double Defense',
    'Farores Wind',
    'Nayrus Love',
    'Stone of Agony',
    'Ice Arrows',
    'Deku Stick Capacity',
    'Deku Nut Capacity'
]

ludicrous_items_extended = [
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
    'Requiem of Spirit',
    'Ocarina',
    'Kokiri Sword',
    'Boss Key (Ganons Castle)',
    'Boss Key (Forest Temple)',
    'Boss Key (Fire Temple)',
    'Boss Key (Water Temple)',
    'Boss Key (Shadow Temple)',
    'Boss Key (Spirit Temple)',
    'Gerudo Membership Card',
    'Small Key (Thieves Hideout)',
    'Small Key (Shadow Temple)',
    'Small Key (Ganons Castle)',
    'Small Key (Forest Temple)',
    'Small Key (Spirit Temple)',
    'Small Key (Fire Temple)',
    'Small Key (Water Temple)',
    'Small Key (Bottom of the Well)',
    'Small Key (Gerudo Training Ground)',
    'Small Key Ring (Thieves Hideout)',
    'Small Key Ring (Shadow Temple)',
    'Small Key Ring (Ganons Castle)',
    'Small Key Ring (Forest Temple)',
    'Small Key Ring (Spirit Temple)',
    'Small Key Ring (Fire Temple)',
    'Small Key Ring (Water Temple)',
    'Small Key Ring (Bottom of the Well)',
    'Small Key Ring (Gerudo Training Ground)',
    'Magic Bean Pack'
]

ludicrous_exclusions = [
    'Triforce Piece',
    'Gold Skulltula Token',
    'Rutos Letter',
    'Heart Container',
    'Piece of Heart',
    'Piece of Heart (Treasure Chest Game)'
]

item_difficulty_max = {
    'ludicrous': {
        'Piece of Heart': 3,
    },
    'plentiful': {
        'Piece of Heart': 3,
    },
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
        'Magic Meter': 1, 
        'Nayrus Love': 1,
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

shopsanity_rupees = (
    ['Rupees (20)'] * 5 +
    ['Rupees (50)'] * 3 +
    ['Rupees (200)'] * 2
)

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
    ['Buy Bombs (5) for 25 Rupees'] + ['Buy Bombs (5) for 35 Rupees'] + ['Buy Bombs (10)'] + ['Buy Bombs (20)'] +
    ['Buy Green Potion'] +
    ['Buy Red Potion for 30 Rupees'] +
    ['Buy Blue Fire'] +
    ["Buy Fairy's Spirit"] +
    ['Buy Bottle Bug'] +
    ['Buy Fish']
)

deku_scrubs_items = {
    'Buy Deku Shield':     'Deku Shield',
    'Buy Deku Nut (5)':    'Deku Nuts (5)',
    'Buy Deku Stick (1)':  'Deku Stick (1)',
    'Buy Bombs (5) for 35 Rupees':  'Bombs (5)',
    'Buy Red Potion for 30 Rupees': 'Recovery Heart',
    'Buy Green Potion':    'Rupees (5)',
    'Buy Arrows (30)':     [('Arrows (30)', 3), ('Deku Seeds (30)', 1)],
    'Buy Deku Seeds (30)': [('Arrows (30)', 3), ('Deku Seeds (30)', 1)],
}

trade_items = OrderedDict([
    ("pocket_egg",   "Pocket Egg"),
    ("pocket_cucco", "Pocket Cucco"),
    ("cojiro",       "Cojiro"),
    ("odd_mushroom", "Odd Mushroom"),
    ("poachers_saw", "Poachers Saw"),
    ("broken_sword", "Broken Sword"),
    ("prescription", "Prescription"),
    ("eyeball_frog", "Eyeball Frog"),
    ("eyedrops",     "Eyedrops"),
    ("claim_check",  "Claim Check"),
])

normal_bottles = [bottle for bottle in sorted(ItemInfo.bottles) if bottle not in ['Deliver Letter', 'Sell Big Poe']] + ['Bottle with Big Poe']
song_list = [item.name for item in sorted([i for n, i in ItemInfo.items.items() if i.type == 'Song'], key=lambda x: x.index)]
junk_pool_base = [(item, weight) for (item, weight) in sorted(ItemInfo.junk.items()) if weight > 0]
remove_junk_items = [item for (item, weight) in sorted(ItemInfo.junk.items()) if weight >= 0]

remove_junk_ludicrous_items = [
    'Ice Arrows',
    'Deku Nut Capacity',
    'Deku Stick Capacity',
    'Double Defense',
    'Biggoron Sword'
]

# a useless placeholder item placed at some skipped and inaccessible locations
# (e.g. HC Malon Egg with Skip Child Zelda, or the carpenters with Open Gerudo Fortress)
IGNORE_LOCATION = 'Recovery Heart'

pending_junk_pool = []
junk_pool = []

exclude_from_major = [ 
    'Deliver Letter',
    'Sell Big Poe',
    'Magic Bean',
    'Buy Magic Bean',
    'Zeldas Letter',
    'Bombchus (5)',
    'Bombchus (10)',
    'Bombchus (20)',
    'Odd Potion',
    'Triforce Piece'
]

item_groups = {
    'Junk': remove_junk_items,
    'JunkSong': ('Prelude of Light', 'Serenade of Water'),
    'AdultTrade': list(trade_items.values()),
    'Bottle': normal_bottles,
    'Spell': ('Dins Fire', 'Farores Wind', 'Nayrus Love'),
    'Shield': ('Deku Shield', 'Hylian Shield'),
    'Song': song_list,
    'NonWarpSong': song_list[6:],
    'WarpSong': song_list[0:6],
    'HealthUpgrade': ('Heart Container', 'Piece of Heart', 'Piece of Heart (Treasure Chest Game)'),
    'ProgressItem': sorted([name for name, item in ItemInfo.items.items() if item.type == 'Item' and item.advancement]),
    'MajorItem': sorted([name for name, item in ItemInfo.items.items() if item.type in ['Item', 'Song'] and item.advancement and name not in exclude_from_major]),
    'DungeonReward': [item.name for item in sorted([i for n, i in ItemInfo.items.items() if i.type == 'DungeonReward'], key=lambda x: x.special['item_id'])],

    'ForestFireWater': ('Forest Medallion', 'Fire Medallion', 'Water Medallion'),
    'FireWater': ('Fire Medallion', 'Water Medallion'),
}


def get_junk_item(count=1, pool=None, plando_pool=None):
    if count < 1:
        raise ValueError("get_junk_item argument 'count' must be greater than 0.")

    return_pool = []
    if pending_junk_pool:
        pending_count = min(len(pending_junk_pool), count)
        return_pool = [pending_junk_pool.pop() for _ in range(pending_count)]
        count -= pending_count

    if pool and plando_pool:
        jw_list = [(junk, weight) for (junk, weight) in junk_pool
                   if junk not in plando_pool or pool.count(junk) < plando_pool[junk].count]
        try:
            junk_items, junk_weights = zip(*jw_list)
        except ValueError:
            raise RuntimeError("Not enough junk is available in the item pool to replace removed items.")
    else:
        junk_items, junk_weights = zip(*junk_pool)
    return_pool.extend(random_choices(junk_items, weights=junk_weights, k=count))

    return return_pool


def replace_max_item(items, item, max_count):
    count = 0
    for i,val in enumerate(items):
        if val == item:
            if count >= max_count:
                items[i] = get_junk_item()[0]
            count += 1


def generate_itempool(world):
    junk_pool[:] = list(junk_pool_base)
    if world.settings.junk_ice_traps == 'on':
        junk_pool.append(('Ice Trap', 10))
    elif world.settings.junk_ice_traps in ['mayhem', 'onslaught']:
        junk_pool[:] = [('Ice Trap', 1)]

    # set up item pool
    (pool, placed_items) = get_pool_core(world)
    placed_items_count = {}
    world.itempool = ItemFactory(pool, world)
    placed_locations = list(filter(lambda loc: loc.name in placed_items, world.get_locations()))
    for location in placed_locations:
        item = placed_items[location.name]
        placed_items_count[item] = placed_items_count.get(item, 0) + 1
        world.push_item(location, ItemFactory(item, world))
        world.get_location(location).locked = True

    world.initialize_items()
    world.distribution.set_complete_itempool(world.itempool)

    # make sure that there are enough gold skulltulas for bridge/ganon boss key/lacs
    world.available_tokens = placed_items_count.get("Gold Skulltula Token", 0) \
                           + pool.count("Gold Skulltula Token") \
                           + world.distribution.get_starting_item("Gold Skulltula Token")
    if world.max_progressions["Gold Skulltula Token"] > world.available_tokens:
        raise ValueError(f"Not enough available Gold Skulltula Tokens to meet requirements. Available: {world.available_tokens}, Required: {world.max_progressions['Gold Skulltula Token']}.")

def get_pool_core(world):
    pool = []
    placed_items = {}
    remain_shop_items = []
    ruto_bottles = 1

    if world.settings.zora_fountain == 'open':
        ruto_bottles = 0

    if world.settings.shopsanity not in ['off', '0']:
        pending_junk_pool.append('Progressive Wallet')

    if world.settings.item_pool_value == 'plentiful':
        pending_junk_pool.extend(plentiful_items)
        if world.settings.zora_fountain != 'open':
            ruto_bottles += 1
        if world.settings.shuffle_kokiri_sword:
            pending_junk_pool.append('Kokiri Sword')
        if world.settings.shuffle_ocarinas:
            pending_junk_pool.append('Ocarina')
        if world.settings.shuffle_beans and world.distribution.get_starting_item('Magic Bean') < 10:
            pending_junk_pool.append('Magic Bean Pack')
        if (world.settings.gerudo_fortress != "open"
                and world.settings.shuffle_hideoutkeys in ['any_dungeon', 'overworld', 'keysanity']):
            if 'Thieves Hideout' in world.settings.key_rings and world.settings.gerudo_fortress != "fast":
                pending_junk_pool.extend(['Small Key Ring (Thieves Hideout)'])
            else:
                pending_junk_pool.append('Small Key (Thieves Hideout)')
        if world.settings.shuffle_gerudo_card:
            pending_junk_pool.append('Gerudo Membership Card')
        if world.settings.shuffle_smallkeys in ['any_dungeon', 'overworld', 'keysanity']:
            for dungeon in ['Forest Temple', 'Fire Temple', 'Water Temple', 'Shadow Temple', 'Spirit Temple',
                            'Bottom of the Well', 'Gerudo Training Ground', 'Ganons Castle']:
                if dungeon in world.settings.key_rings:
                    pending_junk_pool.append(f"Small Key Ring ({dungeon})")
                else:
                    pending_junk_pool.append(f"Small Key ({dungeon})")
        if world.settings.shuffle_bosskeys in ['any_dungeon', 'overworld', 'keysanity']:
            for dungeon in ['Forest Temple', 'Fire Temple', 'Water Temple', 'Shadow Temple', 'Spirit Temple']:
                pending_junk_pool.append(f"Boss Key ({dungeon})")
        if world.settings.shuffle_ganon_bosskey in ['any_dungeon', 'overworld', 'keysanity']:
            pending_junk_pool.append('Boss Key (Ganons Castle)')
        if world.settings.shuffle_song_items == 'any':
            pending_junk_pool.extend(song_list)

    if world.settings.item_pool_value == 'ludicrous':
        pending_junk_pool.extend(ludicrous_health)

    if world.settings.triforce_hunt:
        pending_junk_pool.extend(['Triforce Piece'] * world.settings.triforce_count_per_world)

    # Use the vanilla items in the world's locations when appropriate.
    for location in world.get_locations():
        if location.vanilla_item is None:
            continue

        item = location.vanilla_item
        shuffle_item = None  # None for don't handle, False for place item, True for add to pool.

        # Always Placed Items
        if (location.vanilla_item in ['Zeldas Letter', 'Triforce', 'Scarecrow Song',
                                      'Deliver Letter', 'Time Travel', 'Bombchu Drop']
                or location.type == 'Drop'):
            shuffle_item = False

        # Gold Skulltula Tokens
        elif location.vanilla_item == 'Gold Skulltula Token':
            shuffle_item = (world.settings.tokensanity == 'all'
                            or (world.settings.tokensanity == 'dungeons' and location.dungeon)
                            or (world.settings.tokensanity == 'overworld' and not location.dungeon))

        # Shops
        elif location.type == "Shop":
            if world.settings.shopsanity == 'off':
                if world.settings.bombchus_in_logic and location.name in ['KF Shop Item 8', 'Market Bazaar Item 4', 'Kak Bazaar Item 4']:
                    item = 'Buy Bombchu (5)'
                shuffle_item = False
            else:
                remain_shop_items.append(item)

        # Business Scrubs
        elif location.type in ["Scrub", "GrottoScrub"]:
            if location.vanilla_item in ['Piece of Heart', 'Deku Stick Capacity', 'Deku Nut Capacity']:
                shuffle_item = True
            elif world.settings.shuffle_scrubs == 'off':
                shuffle_item = False
            else:
                item = deku_scrubs_items[location.vanilla_item]
                if isinstance(item, list):
                    item = random.choices([i[0] for i in item], weights=[i[1] for i in item], k=1)[0]
                shuffle_item = True

        # Kokiri Sword
        elif location.vanilla_item == 'Kokiri Sword':
            shuffle_item = world.settings.shuffle_kokiri_sword

        # Weird Egg
        elif location.vanilla_item == 'Weird Egg':
            if world.settings.skip_child_zelda:
                item = IGNORE_LOCATION
                shuffle_item = False
            else:
                shuffle_item = world.settings.shuffle_weird_egg

        # Ocarinas
        elif location.vanilla_item == 'Ocarina':
            shuffle_item = world.settings.shuffle_ocarinas

        # Giant's Knife
        elif location.vanilla_item == 'Giants Knife':
            shuffle_item = world.settings.shuffle_medigoron_carpet_salesman

        # Bombchus
        elif location.vanilla_item in ['Bombchus', 'Bombchus (5)', 'Bombchus (10)', 'Bombchus (20)']:
            if world.settings.bombchus_in_logic:
                item = 'Bombchus'
            shuffle_item = location.name != 'Wasteland Bombchu Salesman' or world.settings.shuffle_medigoron_carpet_salesman

        # Cows
        elif location.vanilla_item == 'Milk':
            if world.settings.shuffle_cows:
                item = get_junk_item()[0]
            shuffle_item = world.settings.shuffle_cows

        # Gerudo Card
        elif location.vanilla_item == 'Gerudo Membership Card':
            shuffle_item = world.settings.shuffle_gerudo_card and world.settings.gerudo_fortress != 'open'
            if world.settings.shuffle_gerudo_card and world.settings.gerudo_fortress == 'open':
                pending_junk_pool.append(item)
                item = IGNORE_LOCATION

        # Bottles
        elif location.vanilla_item in ['Bottle', 'Bottle with Milk', 'Rutos Letter']:
            if ruto_bottles:
                item = 'Rutos Letter'
                ruto_bottles -= 1
            else:
                item = random.choice(normal_bottles)
            shuffle_item = True

        # Magic Beans
        elif location.vanilla_item == 'Buy Magic Bean':
            if world.settings.shuffle_beans:
                item = 'Magic Bean Pack' if world.distribution.get_starting_item('Magic Bean') < 10 else get_junk_item()[0]
            shuffle_item = world.settings.shuffle_beans

        # Frogs Purple Rupees
        elif location.scene == 0x54 and location.vanilla_item == 'Rupees (50)':
            shuffle_item = world.settings.shuffle_frog_song_rupees

        # Adult Trade Item
        elif location.vanilla_item == 'Pocket Egg':
            trade_item_options = list(trade_items.keys())
            earliest_trade = trade_item_options.index(world.settings.logic_earliest_adult_trade)
            latest_trade = trade_item_options.index(world.settings.logic_latest_adult_trade)
            if earliest_trade > latest_trade:
                earliest_trade, latest_trade = latest_trade, earliest_trade
            item = trade_items[random.choice(trade_item_options[earliest_trade:latest_trade + 1])]
            world.selected_adult_trade_item = item
            shuffle_item = True

        # Thieves' Hideout
        elif location.vanilla_item == 'Small Key (Thieves Hideout)':
            shuffle_item = world.settings.shuffle_hideoutkeys in ['any_dungeon', 'overworld', 'keysanity']
            if (world.settings.gerudo_fortress == 'open'
                    or world.settings.gerudo_fortress == 'fast' and location.name != 'Hideout Jail Guard (1 Torch)'):
                item = IGNORE_LOCATION
                shuffle_item = False
            if shuffle_item and world.settings.gerudo_fortress == 'normal' and 'Thieves Hideout' in world.settings.key_rings:
                item = get_junk_item()[0] if location.name != 'Hideout Jail Guard (1 Torch)' else 'Small Key Ring (Thieves Hideout)'

        # Dungeon Items
        elif location.dungeon is not None:
            dungeon = location.dungeon
            shuffle_setting = None
            dungeon_collection = None

            # Boss Key
            if location.vanilla_item == dungeon.item_name("Boss Key"):
                shuffle_setting = world.settings.shuffle_bosskeys if dungeon.name != 'Ganons Castle' else world.settings.shuffle_ganon_bosskey
                dungeon_collection = dungeon.boss_key
                if shuffle_setting == 'vanilla':
                    shuffle_item = False
            # Map or Compass
            elif location.vanilla_item in [dungeon.item_name("Map"), dungeon.item_name("Compass")]:
                shuffle_setting = world.settings.shuffle_mapcompass
                dungeon_collection = dungeon.dungeon_items
                if shuffle_setting == 'vanilla':
                    shuffle_item = False
            # Small Key
            elif location.vanilla_item == dungeon.item_name("Small Key"):
                shuffle_setting = world.settings.shuffle_smallkeys
                dungeon_collection = dungeon.small_keys
                if shuffle_setting == 'vanilla':
                    shuffle_item = False
                elif dungeon.name in world.settings.key_rings and not dungeon.small_keys:
                    item = dungeon.item_name("Small Key Ring")
                elif dungeon.name in world.settings.key_rings:
                    item = get_junk_item()[0]
                    shuffle_item = True
            # Any other item in a dungeon.
            elif location.type in ["Chest", "NPC", "Song", "Collectable", "Cutscene", "BossHeart"]:
                shuffle_item = True

            # Handle dungeon item.
            if shuffle_setting is not None and not shuffle_item:
                dungeon_collection.append(ItemFactory(item))
                if shuffle_setting in ['remove', 'startwith', 'triforce']:
                    world.state.collect(dungeon_collection[-1])
                    item = get_junk_item()[0]
                    shuffle_item = True
                elif shuffle_setting in ['any_dungeon', 'overworld']:
                    dungeon_collection[-1].priority = True

        # The rest of the overworld items.
        elif location.type in ["Chest", "NPC", "Song", "Collectable", "Cutscene", "BossHeart"]:
            shuffle_item = True

        # Now, handle the item as necessary.
        if shuffle_item:
            pool.append(item)
        elif shuffle_item is not None:
            placed_items[location.name] = item
    # End of Locations loop.

    # add unrestricted dungeon items to main item pool
    pool.extend([item.name for item in world.get_unrestricted_dungeon_items()])

    if world.settings.shopsanity != 'off':
        pool.extend(min_shop_items)
        for item in min_shop_items:
            remain_shop_items.remove(item)

        shop_slots_count = len(remain_shop_items)
        shop_non_item_count = len(world.shop_prices)
        shop_item_count = shop_slots_count - shop_non_item_count

        pool.extend(random.sample(remain_shop_items, shop_item_count))
        if shop_non_item_count:
            pool.extend(get_junk_item(shop_non_item_count))

    # Extra rupees for shopsanity.
    if world.settings.shopsanity not in ['off', '0']:
        for rupee in shopsanity_rupees:
            if 'Rupees (5)' in pool:
                pool[pool.index('Rupees (5)')] = rupee
            else:
                pending_junk_pool.append(rupee)

    if world.settings.free_scarecrow:
        world.state.collect(ItemFactory('Scarecrow Song'))
    
    if world.settings.no_epona_race:
        world.state.collect(ItemFactory('Epona', event=True))

    if world.settings.shuffle_smallkeys == 'vanilla':
        # Logic cannot handle vanilla key layout in some dungeons
        # this is because vanilla expects the dungeon major item to be
        # locked behind the keys, which is not always true in rando.
        # We can resolve this by starting with some extra keys
        if world.dungeon_mq['Spirit Temple']:
            # Yes somehow you need 3 keys. This dungeon is bonkers
            world.state.collect(ItemFactory('Small Key (Spirit Temple)'))
            world.state.collect(ItemFactory('Small Key (Spirit Temple)'))
            world.state.collect(ItemFactory('Small Key (Spirit Temple)'))
        if 'Shadow Temple' in world.settings.dungeon_shortcuts:
            # Reverse Shadow is broken with vanilla keys in both vanilla/MQ
            world.state.collect(ItemFactory('Small Key (Shadow Temple)'))
            world.state.collect(ItemFactory('Small Key (Shadow Temple)'))

    if not world.keysanity and not world.dungeon_mq['Fire Temple']:
        world.state.collect(ItemFactory('Small Key (Fire Temple)'))

    if world.settings.shuffle_ganon_bosskey == 'on_lacs':
        placed_items['ToT Light Arrows Cutscene'] = 'Boss Key (Ganons Castle)'

    if world.settings.shuffle_ganon_bosskey in ['stones', 'medallions', 'dungeons', 'tokens', 'hearts']:
        placed_items['Gift from Sages'] = 'Boss Key (Ganons Castle)'
        pool.extend(get_junk_item())
    else:
        placed_items['Gift from Sages'] = IGNORE_LOCATION

    if world.settings.junk_ice_traps == 'off':
        replace_max_item(pool, 'Ice Trap', 0)
    elif world.settings.junk_ice_traps == 'onslaught':
        for item in [item for item, weight in junk_pool_base] + ['Recovery Heart', 'Bombs (20)', 'Arrows (30)']:
            replace_max_item(pool, item, 0)

    for item, maximum in item_difficulty_max[world.settings.item_pool_value].items():
        replace_max_item(pool, item, maximum)

    world.distribution.alter_pool(world, pool)

    # Make sure our pending_junk_pool is empty. If not, remove some random junk here.
    if pending_junk_pool:
        for item in set(pending_junk_pool):
            # Ensure pending_junk_pool contents don't exceed values given by distribution file
            if item in world.distribution.item_pool:
                while pending_junk_pool.count(item) > world.distribution.item_pool[item].count:
                    pending_junk_pool.remove(item)
                # Remove pending junk already added to the pool by alter_pool from the pending_junk_pool
                if item in pool:
                    count = min(pool.count(item), pending_junk_pool.count(item))
                    for _ in range(count):
                        pending_junk_pool.remove(item)

        remove_junk_pool, _ = zip(*junk_pool_base)
        # Omits Rupees (200) and Deku Nuts (10)
        remove_junk_pool = list(remove_junk_pool) + ['Recovery Heart', 'Bombs (20)', 'Arrows (30)', 'Ice Trap']

        junk_candidates = [item for item in pool if item in remove_junk_pool]
        while pending_junk_pool:
            pending_item = pending_junk_pool.pop()
            if not junk_candidates:
                raise RuntimeError("Not enough junk exists in item pool for %s (+%d others) to be added." % (pending_item, len(pending_junk_pool) - 1))
            junk_item = random.choice(junk_candidates)
            junk_candidates.remove(junk_item)
            pool.remove(junk_item)
            pool.append(pending_item)

    if world.settings.item_pool_value == 'ludicrous':
        # Replace all junk items with major items
        # Overrides plando'd junk items
        # Songs are in the unrestricted pool even if their fill is restricted. Filter from candidates
        duplicate_candidates = [item for item in ludicrous_items_extended if item in pool and (ItemInfo.items[item].type != 'Song' or world.settings.shuffle_song_items == 'any')]
        duplicate_candidates.extend(ludicrous_items_base)
        junk_items = [
            item for item in pool
            if item not in duplicate_candidates
            and ItemInfo.items[item].type != 'Shop'
            and ItemInfo.items[item].type != 'Song'
            and not ItemInfo.items[item].trade
            and item not in normal_bottles
            and item not in ludicrous_exclusions
        ]
        max_extra_copies = int(Decimal(len(junk_items) / len(duplicate_candidates)).to_integral_value(rounding=ROUND_UP))
        duplicate_items = [item for item in duplicate_candidates for _ in range(max_extra_copies)]
        pool = [item if item not in junk_items else duplicate_items.pop(0) for item in pool]
        # Handle bottles separately since only 4 can be obtained
        pool_bottles = 0
        pool_letters = 0
        for item in pool:
            if item == 'Rutos Letter':
                pool.remove(item)
                pool_bottles += 1
                pool_letters += 1
            if item in normal_bottles:
                pool.remove(item)
                pool_bottles += 1
        letter_adds = 0
        # No Rutos Letters in the pool could be due to open fountain or starting with one
        if pool_letters > 0:
            # Enforce max 2 Rutos Letters to balance out regular bottle availability
            letter_adds = min(2, max_extra_copies)
            for _ in range(letter_adds):
                pool.append('Rutos Letter')
        # Dynamically add bottles back to pool, accounting for starting items
        for _ in range(pool_bottles - letter_adds):
            bottle = random.choice(normal_bottles)
            pool.append(bottle)
        # Disabled locations use the #Junk group for fill.
        # Update pattern matcher since all normal junk is removed.
        item_groups['Junk'] = remove_junk_ludicrous_items
        world.distribution.distribution.search_groups['Junk'] = remove_junk_ludicrous_items
    else:
        # Fix for unit tests reusing globals after ludicrous pool mutates them
        item_groups['Junk'] = remove_junk_items
        world.distribution.distribution.search_groups['Junk'] = remove_junk_items

    world.distribution.collect_starters(world.state)

    return pool, placed_items
