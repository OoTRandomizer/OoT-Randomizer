from LocationList import location_table
from enum import Enum


class Location(object):

    def __init__(self, name='', address=None, address2=None, default=None, type='Chest', scene=None, hint='Termina', parent=None):
        self.name = name
        self.parent_region = parent
        self.item = None
        self.address = address
        self.address2 = address2
        self.default = default
        self.type = type
        self.scene = scene
        self.hint = hint
        self.spot_type = 'Location'
        self.recursion_count = 0
        self.staleness_count = 0
        self.access_rule = lambda state: True
        self.item_rule = lambda location, item: True
        self.locked = False
        self.price = None
        self.minor_only = False
        self.world = None
        self.disabled = DisableType.ENABLED


    def copy(self, new_region):
        new_location = Location(self.name, self.address, self.address2, self.default, self.type, self.scene, self.hint, new_region)
        new_location.world = new_region.world
        if self.item:
            new_location.item = self.item.copy(new_region.world)
            new_location.item.location = new_location
        new_location.spot_type = self.spot_type
        new_location.access_rule = self.access_rule
        new_location.item_rule = self.item_rule
        new_location.locked = self.locked
        new_location.minor_only = self.minor_only
        new_location.disabled = self.disabled

        return new_location


    def can_fill(self, state, item, check_access=True):
        if self.minor_only and item.majoritem:
            return False
        return (
            self.disabled != DisableType.DISABLED and 
            self.can_fill_fast(item) and
            (not check_access or state.can_reach(self)))


    def can_fill_fast(self, item):
        return (self.parent_region.can_fill(item) and self.item_rule(self, item))


    def can_reach(self, state):
        if self.disabled != DisableType.DISABLED and \
           self.access_rule(state) and \
           state.can_reach(self.parent_region):
            return True
        return False


    def __str__(self):
        return str(self.__unicode__())


    def __unicode__(self):
        return '%s' % self.name


def LocationFactory(locations, world=None):
    ret = []
    singleton = False
    if isinstance(locations, str):
        locations = [locations]
        singleton = True
    for location in locations:
        if location in location_table:
            type, scene, default, hint, addresses = location_table[location]
            if addresses is None:
                addresses = (None, None)
            address, address2 = addresses
            ret.append(Location(location, address, address2, default, type, scene, hint, ret))
        else:
            raise KeyError('Unknown Location: %s', item)

    if singleton:
        return ret[0]
    return ret


class DisableType(Enum):
    ENABLED  = 0
    PENDING = 1
    DISABLED = 2

