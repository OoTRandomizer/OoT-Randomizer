from enum import Enum, unique


@unique
class RegionType(Enum):

    Overworld = 1
    Interior = 2
    Dungeon = 3
    Grotto = 4


    @property
    def is_indoors(self):
        """Shorthand for checking if Interior or Dungeon"""
        return self in (RegionType.Interior, RegionType.Dungeon, RegionType.Grotto)


class Region(object):

    def __init__(self, name, type=RegionType.Overworld):
        self.name = name
        self.type = type
        self.entrances = []
        self.exits = []
        self.locations = []
        self.dungeon = None
        self.world = None
        self.spot_type = 'Region'
        self.recursion_count = 0
        self.price = None
        self.world = None


    def copy(self, new_world):
        new_region = Region(self.name, self.type)
        new_region.world = new_world
        new_region.spot_type = self.spot_type
        new_region.price = self.price
        new_region.can_reach = self.can_reach

        if self.dungeon:
            new_region.dungeon = self.dungeon.name
        new_region.locations = [location.copy(new_region) for location in self.locations]
        new_region.exits = [exit.copy(new_region) for exit in self.exits]

        return new_region


    def can_reach(self, state):
        for entrance in self.entrances:
            if state.can_reach(entrance):
                return True
        return False


    def can_fill(self, item):
        is_dungeon_restricted = False
        if item.map or item.compass:
            is_dungeon_restricted = self.world.shuffle_mapcompass == 'dungeon'
        elif item.smallkey and item.type != 'FortressSmallKey':
            is_dungeon_restricted = self.world.shuffle_smallkeys == 'dungeon'
        elif item.bosskey:
            is_dungeon_restricted = self.world.shuffle_bosskeys == 'dungeon'

        if is_dungeon_restricted:
            return self.dungeon and self.dungeon.is_dungeon_item(item) and item.world.id == self.world.id
        return True


    def __str__(self):
        return str(self.__unicode__())


    def __unicode__(self):
        return '%s' % self.name

