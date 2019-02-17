import collections
import logging
from Location import DisableType
from LocationList import game_location_names


def set_rules(world):
    logger = logging.getLogger('')

    # ganon can only carry triforce
    world.get_location('Ganon').item_rule = lambda location, item: item.name == 'Triforce'

    # these are default save&quit points and always accessible
    world.get_region('Links House').can_reach = lambda state: True
    
    for location in world.get_locations():

        if not world.shuffle_song_items:
            if location.type == 'Song':
                if not world.start_with_fast_travel:
                    add_item_rule(location, lambda location, item: item.type == 'Song' and item.world.id == location.world.id)
                else:
                    # allow junk items, but songs must still have matching world
                    add_item_rule(location, lambda location, item: item.type != 'Song' or (item.type == 'Song' and item.world.id == location.world.id))
            else:
                add_item_rule(location, lambda location, item: item.type != 'Song')

        if location.type == 'Shop':
            if location.name in world.shop_prices:
                add_item_rule(location, lambda location, item: item.type != 'Shop')
                location.price = world.shop_prices[location.name]
                if location.price > 200:
                    set_rule(location, lambda state: state.has('Progressive Wallet', 2))
                elif location.price > 99:
                    set_rule(location, lambda state: state.has('Progressive Wallet'))
            else:
                add_item_rule(location, lambda location, item: item.type == 'Shop' and item.world.id == location.world.id)

            if location.parent_region.name in ['Castle Town Bombchu Shop', 'Castle Town Potion Shop', 'Castle Town Bazaar']:
                if not world.check_beatable_only:
                    forbid_item(location, 'Buy Goron Tunic')
                    forbid_item(location, 'Buy Zora Tunic')
        elif not 'Deku Scrub' in location.name:
            add_item_rule(location, lambda location, item: item.type != 'Shop')

        if location.name == 'Forest Temple MQ First Chest' and world.shuffle_bosskeys == 'dungeon' and world.shuffle_smallkeys == 'dungeon' and world.tokensanity == 'off':
            # This location needs to be a small key. Make sure the boss key isn't placed here.
            forbid_item(location, 'Boss Key (Forest Temple)')

        if not world.can_require_games:
            if location.name in game_location_names:
                add_item_rule(location, lambda location, item: not item.advancement)

    for location in world.disabled_locations:
        try:
            world.get_location(location).disabled = DisableType.PENDING
        except:
            logger.debug('Tried to disable location that does not exist: %s' % location)


def set_rule(spot, rule):
    spot.access_rule = rule


def add_rule(spot, rule, combine='and'):
    old_rule = spot.access_rule
    if combine == 'or':
        spot.access_rule = lambda state: rule(state) or old_rule(state)
    else:
        spot.access_rule = lambda state: rule(state) and old_rule(state)


def add_item_rule(spot, rule, combine='and'):
    old_rule = spot.item_rule
    if combine == 'or':
        spot.item_rule = lambda location, item: rule(location, item) or old_rule(location, item)
    else:
        spot.item_rule = lambda location, item: rule(location, item) and old_rule(location, item)


def forbid_item(location, item_name):
    old_rule = location.item_rule
    location.item_rule = lambda loc, item: item.name != item_name and old_rule(loc, item)


def item_in_locations(state, item, locations):
    for location in locations:
        if state.item_name(location) == item:
            return True
    return False


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
                    add_rule(
                        location,
                        lambda state: state.is_adult() and (state.has_explosives() or state.has('Progressive Strength Upgrade') or state.has_bow()))
                elif location.parent_region.name == 'Zora Shop':
                    add_rule(location, lambda state: state.can_reach('Zoras Domain Frozen -> Zora Shop', 'Entrance'))
                elif location.parent_region.name in ['Castle Town Bombchu Shop', 'Castle Town Potion Shop', 'Castle Town Bazaar']:
                    set_rule(location, lambda state: False)
                else:
                    add_rule(location, lambda state: state.is_adult())

            # Add item prerequisit checks
            if location.item.name in ['Buy Blue Fire',
                                      'Buy Blue Potion',
                                      'Buy Bottle Bug',
                                      'Buy Fish',
                                      'Buy Green Potion',
                                      'Buy Poe',
                                      'Buy Red Potion [30]',
                                      'Buy Red Potion [40]',
                                      'Buy Red Potion [50]',
                                      'Buy Fairy\'s Spirit']:
                add_rule(location, lambda state: state.has_bottle())
            if location.item.name in ['Buy Bombchu (10)', 'Buy Bombchu (20)', 'Buy Bombchu (5)']:
                add_rule(location, lambda state: state.has_bombchus_item())

