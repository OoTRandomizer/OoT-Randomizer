class Dungeon(object):

    def __init__(self, world, name, name_JP, hint, hint_JP, font_color, boss_key=None, small_keys=None, dungeon_items=None):
        self.world = world
        self.name = name
        self.name_JP = name_JP
        self.hint = hint
        self.hint_JP = hint_JP
        self.font_color = font_color
        self.regions = []
        self.boss_key = boss_key if boss_key is not None else []
        self.small_keys = small_keys if small_keys is not None else []
        self.dungeon_items = dungeon_items if dungeon_items is not None else []

        for region in world.regions:
            if region.dungeon == self.name:
                region.dungeon = self
                self.regions.append(region)                


    def copy(self, new_world):
        new_boss_key = [item.copy(new_world) for item in self.boss_key]
        new_small_keys = [item.copy(new_world) for item in self.small_keys]
        new_dungeon_items = [item.copy(new_world) for item in self.dungeon_items]

        new_dungeon = Dungeon(new_world, self.name, self.name_JP, self.hint, self.hint_JP, self.font_color, new_boss_key, new_small_keys, new_dungeon_items)

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

