import random
import os

from Dungeon import Dungeon
from Item import ItemFactory
from Utils import data_path


dungeon_table = [
    {
        'name': 'Deku Tree',
        'name_jp': 'デクの樹',
        'hint': 'the Deku Tree',
        'hint_jp': 'デクの樹',
        'font_color': 'Green',
        'boss_key':     0,
        'small_key':    0,
        'small_key_mq': 0,
        'dungeon_item': 1,
    },
    {
        'name': 'Dodongos Cavern',
        'name_jp': 'ドドンゴの洞窟',
        'hint': "Dodongo's Cavern",
        'hint_jp': 'ドドンゴの洞窟',
        'font_color': 'Red',
        'boss_key':     0,
        'small_key':    0,
        'small_key_mq': 0,
        'dungeon_item': 1,
    },
    {
        'name': 'Jabu Jabus Belly',
        'name_jp': 'ジャブジャブ様のお腹',
        'hint': "Jabu Jabu's Belly",
        'hint_jp': 'ジャブジャブの中',
        'font_color': 'Blue',
        'boss_key':     0,
        'small_key':    0,
        'small_key_mq': 0,
        'dungeon_item': 1,
    },
    {
        'name': 'Forest Temple',
        'name_jp': '森の神殿',
        'hint': 'the Forest Temple',
        'hint_jp': '森の神殿',
        'font_color': 'Green',
        'boss_key':     1,
        'small_key':    5,
        'small_key_mq': 6,
        'dungeon_item': 1,
    },
    {
        'name': 'Bottom of the Well',
        'name_jp': '井戸の底',
        'hint': 'the Bottom of the Well',
        'hint_jp': '井戸の底',
        'font_color': 'Pink',
        'boss_key':     0,
        'small_key':    3,
        'small_key_mq': 2,
        'dungeon_item': 1,
    },
    {
        'name': 'Fire Temple',
        'name_jp': '炎の神殿',
        'hint': 'the Fire Temple',
        'hint_jp': '炎の神殿',
        'font_color': 'Red',
        'boss_key':     1,
        'small_key':    8,
        'small_key_mq': 5,
        'dungeon_item': 1,
    },
    {
        'name': 'Ice Cavern',
        'name_jp': '氷の洞窟',
        'hint': 'the Ice Cavern',
        'hint_jp': '氷の洞窟',
        'font_color': 'Blue',
        'boss_key':     0,
        'small_key':    0,
        'small_key_mq': 0,
        'dungeon_item': 1,
    },
    {
        'name': 'Water Temple',
        'name_jp': '水の神殿',
        'hint': 'the Water Temple',
        'hint_jp': '水の神殿',
        'font_color': 'Blue',
        'boss_key':     1,
        'small_key':    6,
        'small_key_mq': 2,
        'dungeon_item': 1,
    },
    {
        'name': 'Shadow Temple',
        'name_jp': '闇の神殿',
        'hint': 'the Shadow Temple',
        'hint_jp': '闇の神殿',
        'font_color': 'Pink',
        'boss_key':     1,
        'small_key':    5,
        'small_key_mq': 6,
        'dungeon_item': 1,
    },
    {
        'name': 'Gerudo Training Ground',
        'name_jp': 'ゲルド修練場',
        'hint': 'the Gerudo Training Ground',
        'hint_jp': '修練場',
        'font_color': 'Yellow',
        'boss_key':     0,
        'small_key':    9,
        'small_key_mq': 3,
        'dungeon_item': 0,
    },
    {
        'name': 'Spirit Temple',
        'name_jp': '魂の神殿',
        'hint': 'the Spirit Temple',
        'hint_jp': '魂の神殿',
        'font_color': 'Yellow',
        'boss_key':     1,
        'small_key':    5,
        'small_key_mq': 7,
        'dungeon_item': 1,
    },
    {
        'name': 'Ganons Castle',
        'name_jp': 'ガノン城',
        'hint': "inside Ganon's Castle",
        'hint_jp': 'ガノン城内',
        'boss_key':     1,
        'small_key':    2,
        'small_key_mq': 3,
        'dungeon_item': 0,
    },
]


def create_dungeons(world):
    for dungeon_info in dungeon_table:
        name = dungeon_info['name']
        name_JP = dungeon_info['name_jp']
        hint = dungeon_info['hint'] if 'hint' in dungeon_info else name
        hint_JP = dungeon_info['hint_jp'] if 'hint_jp' in dungeon_info else name_jp
        font_color = dungeon_info['font_color'] if 'font_color' in dungeon_info else 'White'

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

        boss_keys = ItemFactory(['Boss Key (%s)' % name] * dungeon_info['boss_key'])
        if dungeon_info['name'] in world.settings.key_rings and world.settings.shuffle_smallkeys != "vanilla":
            small_keys = ItemFactory(['Small Key Ring (%s)' % name])
        else:
            if not world.dungeon_mq[dungeon_info['name']]:
                small_keys = ItemFactory(['Small Key (%s)' % name] * dungeon_info['small_key'])
            else:
                small_keys = ItemFactory(['Small Key (%s)' % name] * dungeon_info['small_key_mq'])
        dungeon_items = ItemFactory(['Map (%s)' % name,
                                     'Compass (%s)' % name] * dungeon_info['dungeon_item'])
        if world.settings.shuffle_mapcompass in ['any_dungeon', 'overworld']:
            for item in dungeon_items:
                item.priority = True

        world.dungeons.append(Dungeon(world, name, name_JP, hint, hint_JP, font_color, boss_keys, small_keys, dungeon_items))

