import os

from Hints import HintArea
from Utils import data_path


class Dungeon:
    def __init__(self, world, name, hint):
        self.world = world
        self.name = name
        self.hint = hint
        self.regions = []
        self.boss_key = []
        self.small_keys = []
        self.dungeon_items = []

        for region in world.regions:
            if region.dungeon == self.name:
                region.dungeon = self
                self.regions.append(region)


    def copy(self, new_world):
        new_dungeon = Dungeon(new_world, self.name, self.hint)

        new_dungeon.boss_key = [item.copy(new_world) for item in self.boss_key]
        new_dungeon.small_keys = [item.copy(new_world) for item in self.small_keys]
        new_dungeon.dungeon_items = [item.copy(new_world) for item in self.dungeon_items]

        return new_dungeon


    @property
    def keys(self):
        return self.small_keys + self.boss_key


    @property
    def all_items(self):
        return self.dungeon_items + self.keys


    def item_name(self, text):
        return f"{text} ({self.name})"


    def is_dungeon_item(self, item):
        return item.name in [dungeon_item.name for dungeon_item in self.all_items]


    def __str__(self):
        return str(self.__unicode__())


    def __unicode__(self):
        return '%s' % self.name


def create_dungeons(world):
    for hint_area in HintArea:
        if hint_area.is_dungeon:
            name = hint_area.dungeon_name

            if world.settings.logic_rules == 'glitched':
                if not world.dungeon_mq[name]:
                    dungeon_json = os.path.join(data_path('Glitched World'), name + '.json')
                else:
                    dungeon_json = os.path.join(data_path('Glitched World'), name + ' MQ.json')
            else:
                if not world.dungeon_mq[name]:
                    dungeon_json = os.path.join(data_path('World'), name + '.json')
                else:
                    dungeon_json = os.path.join(data_path('World'), name + ' MQ.json')

            world.load_regions_from_json(dungeon_json)
            world.dungeons.append(Dungeon(world, name, hint_area))
