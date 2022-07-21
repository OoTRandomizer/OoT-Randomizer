from collections import namedtuple
from itertools import chain


_Entry = namedtuple("_Entry", ['settingname', 'itemname', 'available', 'guitext', 'special', 'ammo', 'i'])
def _entry(settingname, itemname=None, available=1, guitext=None, special=False, ammo=None):
    if itemname is None:
        itemname = settingname.capitalize()
    if guitext is None:
        guitext = itemname
    result = []
    for i in range(available):
        if i == 0:
            name = settingname
        else:
            name = "{}{}".format(settingname, i+1)
        result.append((name, _Entry(name, itemname, available, guitext, special, ammo, i)))
    return result

# Ammo items must be declared in ItemList.py.
inventory = dict(chain(
    _entry('deku_stick', 'Deku Stick Capacity', available=2, ammo={'Deku Sticks': (20, 30)}),
    _entry('deku_nut', 'Deku Nut Capacity', available=2, ammo={'Deku Nuts': (30, 40)}),
    _entry('bombs', 'Bomb Bag', available=3, ammo={'Bombs': (20, 30, 40)}),
    _entry('bow', available=3, ammo={'Arrows': (30, 40, 50)}),
    _entry('fire_arrow', 'Fire Arrows'),
    _entry('dins_fire', 'Dins Fire', guitext="Din's Fire"),
    _entry('slingshot', available=3, ammo={'Deku Seeds': (30, 40, 50)}),
    _entry('ocarina', available=2),
    _entry('bombchus', ammo={'Bombchus': (19,)}), # start with additional bombchus
    _entry('hookshot', 'Progressive Hookshot', available=2),
    _entry('ice_arrow', 'Ice Arrows'),
    _entry('farores_wind', 'Farores Wind', guitext="Farore's Wind"),
    _entry('boomerang'),
    _entry('lens', 'Lens of Truth'),
    _entry('beans', 'Magic Bean', ammo={'Magic Bean': (9,)}), # start with additional beans
    _entry('megaton_hammer', 'Megaton Hammer', guitext = 'Megaton Hammer'),
    _entry('light_arrow', 'Light Arrows'),
    _entry('nayrus_love', 'Nayrus Love', guitext="Nayru's Love"),
    _entry('bottle', available=3, special=True),
    _entry('letter', 'Rutos Letter', guitext="Ruto's Letter", special=True),
))

songs = dict(chain(
    _entry('lullaby', 'Zeldas Lullaby', guitext="Zelda's Lullaby"),
    _entry('eponas_song', 'Eponas Song', guitext="Epona's Song"),
    _entry('sarias_song', 'Sarias Song', guitext="Saria's Song"),
    _entry('suns_song', 'Suns Song', guitext="Sun's Song"),
    _entry('song_of_time', 'Song of Time'),
    _entry('song_of_storms', 'Song of Storms'),
    _entry('minuet', 'Minuet of Forest'),
    _entry('bolero', 'Bolero of Fire'),
    _entry('serenade', 'Serenade of Water'),
    _entry('requiem', 'Requiem of Spirit'),
    _entry('nocturne', 'Nocturne of Shadow'),
    _entry('prelude', 'Prelude of Light'),
))

equipment = dict(chain(
    _entry('kokiri_sword', 'Kokiri Sword'),
    _entry('giants_knife', 'Giants Knife'),
    _entry('biggoron_sword', 'Biggoron Sword'),
    _entry('deku_shield', 'Deku Shield'),
    _entry('hylian_shield', 'Hylian Shield'),
    _entry('mirror_shield', 'Mirror Shield'),
    _entry('goron_tunic', 'Goron Tunic'),
    _entry('zora_tunic', 'Zora Tunic'),
    _entry('iron_boots', 'Iron Boots'),
    _entry('hover_boots', 'Hover Boots'),
    _entry('magic', 'Magic Meter', available=2),
    _entry('strength', 'Progressive Strength Upgrade', guitext='Progressive Strength', available=3),
    _entry('scale', 'Progressive Scale', available=2),
    _entry('wallet', 'Progressive Wallet', available=3),
    _entry('stone_of_agony', 'Stone of Agony'),
    _entry('defense', 'Double Defense'),
))

everything = dict(chain(equipment.items(), inventory.items(), songs.items()))
