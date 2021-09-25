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


# Pretends to be an enum, but when the values are raw ints, it's much faster
class TimeOfDay(object):
    NONE = 0
    DAY = 1
    DAMPE = 2
    ALL = DAY | DAMPE


class Region(object):

    def __init__(self, name, type=RegionType.Overworld):
        self.name = name
        self.type = type
        self.entrances = []
        self.exits = []
        self.locations = []
        self.dungeon = None
        self.world = None
        self.hint = None
        self.price = None
        self.world = None
        self.time_passes = False
        self.provides_time = TimeOfDay.NONE
        self.scene = None


    def copy(self, new_world):
        new_region = Region(self.name, self.type)
        new_region.world = new_world
        new_region.price = self.price
        new_region.hint = self.hint
        new_region.time_passes = self.time_passes
        new_region.provides_time = self.provides_time
        new_region.scene = self.scene

        if self.dungeon:
            new_region.dungeon = self.dungeon.name
        new_region.locations = [location.copy(new_region) for location in self.locations]
        new_region.exits = [exit.copy(new_region) for exit in self.exits]

        return new_region


    def can_fill(self, item, manual=False):
        is_self_dungeon_restricted = False
        is_dungeon_restricted = False
        is_overworld_restricted = False
        if item.map or item.compass:
            is_self_dungeon_restricted = self.world.settings.shuffle_mapcompass in ['dungeon', 'vanilla']
            is_dungeon_restricted = self.world.settings.shuffle_mapcompass == 'any_dungeon'
            is_overworld_restricted = self.world.settings.shuffle_mapcompass == 'overworld'
        elif item.type == 'SmallKey':
            is_self_dungeon_restricted = self.world.settings.shuffle_smallkeys in ['dungeon', 'vanilla']
            is_dungeon_restricted = self.world.settings.shuffle_smallkeys == 'any_dungeon'
            is_overworld_restricted = self.world.settings.shuffle_smallkeys == 'overworld'
        elif item.type == 'HideoutSmallKey':
            is_dungeon_restricted = self.world.settings.shuffle_hideoutkeys == 'any_dungeon'
            is_overworld_restricted = self.world.settings.shuffle_hideoutkeys == 'overworld'
        elif item.type == 'BossKey':
            is_self_dungeon_restricted = self.world.settings.shuffle_bosskeys in ['dungeon', 'vanilla']
            is_dungeon_restricted = self.world.settings.shuffle_bosskeys == 'any_dungeon'
            is_overworld_restricted = self.world.settings.shuffle_bosskeys == 'overworld'
        elif item.type == 'GanonBossKey':
            is_self_dungeon_restricted = self.world.settings.shuffle_ganon_bosskey in ['dungeon', 'vanilla']
            is_dungeon_restricted = self.world.settings.shuffle_ganon_bosskey == 'any_dungeon'
            is_overworld_restricted = self.world.settings.shuffle_ganon_bosskey == 'overworld'

        if is_self_dungeon_restricted and not manual:
            return self.dungeon and self.dungeon.is_dungeon_item(item) and item.world.id == self.world.id

        if is_dungeon_restricted and not manual:
            return self.dungeon

        if is_overworld_restricted and not manual:
            return not self.dungeon

        if item.name == 'Triforce Piece':
            return item.world.id == self.world.id

        return True


    def get_scene(self):
        if self.scene: 
            return self.scene
        elif self.dungeon:
            return self.dungeon.name
        else: 
            return None


    def __str__(self):
        return str(self.__unicode__())


    def __unicode__(self):
        return '%s' % self.name

