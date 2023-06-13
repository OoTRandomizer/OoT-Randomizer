from __future__ import annotations
from collections import namedtuple
from itertools import chain
from typing import Optional

Entry = namedtuple("Entry", ['setting_name', 'item_name', 'available', 'gui_text', 'special', 'ammo', 'i'])


def _entry(setting_name: str, item_name: Optional[str] = None, available: int = 1, gui_text: Optional[str] = None,
           special: bool = False, ammo: Optional[dict[str, tuple[int, ...]]] = None) -> list[tuple[str, Entry]]:
    if item_name is None:
        item_name = setting_name.capitalize()
    if gui_text is None:
        gui_text = item_name
    result = []
    for i in range(available):
        if i == 0:
            name = setting_name
        else:
            name = f"{setting_name}{i + 1}"
        result.append((name, Entry(name, item_name, available, gui_text, special, ammo, i)))
    return result


# Ammo items must be declared in ItemList.py.
inventory: dict[str, Entry] = dict(chain(
    _entry('deku_stick', 'Deku Stick Capacity', available=2, ammo={'Deku Sticks': (20, 30)}),
    _entry('deku_nut', 'Deku Nut Capacity', available=2, ammo={'Deku Nuts': (30, 40)}),
    _entry('bombs', 'Bomb Bag', available=3, ammo={'Bombs': (20, 30, 40)}),
    _entry('bow', available=3, ammo={'Arrows': (30, 40, 50)}),
    _entry('fire_arrow', 'Fire Arrows'),
    _entry('dins_fire', 'Dins Fire', gui_text="Din's Fire"),
    _entry('slingshot', available=3, ammo={'Deku Seeds': (30, 40, 50)}),
    _entry('ocarina', available=2),
    _entry('bombchus', ammo={'Bombchus': (20,)}),  # start with additional bombchus
    _entry('hookshot', 'Progressive Hookshot', available=2),
    _entry('ice_arrow', 'Ice Arrows'),
    _entry('farores_wind', 'Farores Wind', gui_text="Farore's Wind"),
    _entry('boomerang'),
    _entry('lens', 'Lens of Truth'),
    _entry('beans', 'Magic Bean', ammo={'Magic Bean': (10,)}),  # start with additional beans
    _entry('megaton_hammer', 'Megaton Hammer', gui_text='Megaton Hammer'),
    _entry('light_arrow', 'Light Arrows'),
    _entry('nayrus_love', 'Nayrus Love', gui_text="Nayru's Love"),
    _entry('bottle', available=3, special=True),
    _entry('letter', 'Rutos Letter', gui_text="Ruto's Letter", special=True),
    _entry("pocket_egg",   "Pocket Egg", gui_text="Pocket Egg"),
    _entry("pocket_cucco", "Pocket Cucco", gui_text="Pocket Cucco"),
    _entry("cojiro",       "Cojiro", gui_text="Cojiro"),
    _entry("odd_mushroom", "Odd Mushroom", gui_text="Odd Mushroom"),
    _entry("odd_potion",   "Odd Potion", gui_text="Odd Potion"),
    _entry("poachers_saw", "Poachers Saw", gui_text="Poacher's Saw"),
    _entry("broken_sword", "Broken Sword", gui_text="Broken Sword"),
    _entry("prescription", "Prescription", gui_text="Prescription"),
    _entry("eyeball_frog", "Eyeball Frog", gui_text="Eyeball Frog"),
    _entry("eyedrops",     "Eyedrops", gui_text="Eyedrops"),
    _entry("claim_check",  "Claim Check", gui_text="Claim Check"),
    _entry("weird_egg",    "Weird Egg", gui_text="Weird Egg"),
    _entry("chicken",      "Chicken", gui_text="Chicken"),
    _entry("zeldas_letter","Zeldas Letter", gui_text="Zelda's Letter"),
    _entry("keaton_mask",  "Keaton Mask", gui_text="Keaton Mask"),
    _entry("skull_mask",   "Skull Mask", gui_text="Skull Mask"),
    _entry("spooky_mask",  "Spooky Mask", gui_text="Spooky Mask"),
    _entry("bunny_hood",   "Bunny Hood", gui_text="Bunny Hood"),
    _entry("goron_mask",   "Goron Mask", gui_text="Goron Mask"),
    _entry("zora_mask",    "Zora Mask", gui_text="Zora Mask"),
    _entry("gerudo_mask",  "Gerudo Mask", gui_text="Gerudo Mask"),
    _entry("mask_of_truth","Mask of Truth", gui_text="Mask of Truth"),
))

songs: dict[str, Entry] = dict(chain(
    _entry('lullaby', 'Zeldas Lullaby', gui_text="Zelda's Lullaby"),
    _entry('eponas_song', 'Eponas Song', gui_text="Epona's Song"),
    _entry('sarias_song', 'Sarias Song', gui_text="Saria's Song"),
    _entry('suns_song', 'Suns Song', gui_text="Sun's Song"),
    _entry('song_of_time', 'Song of Time'),
    _entry('song_of_storms', 'Song of Storms'),
    _entry('minuet', 'Minuet of Forest'),
    _entry('bolero', 'Bolero of Fire'),
    _entry('serenade', 'Serenade of Water'),
    _entry('requiem', 'Requiem of Spirit'),
    _entry('nocturne', 'Nocturne of Shadow'),
    _entry('prelude', 'Prelude of Light'),
))

equipment: dict[str, Entry] = dict(chain(
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
    _entry('strength', 'Progressive Strength Upgrade', available=3, gui_text='Progressive Strength'),
    _entry('scale', 'Progressive Scale', available=2),
    _entry('wallet', 'Progressive Wallet', available=3),
    _entry('stone_of_agony', 'Stone of Agony'),
    _entry('defense', 'Double Defense'),
))

everything: dict[str, Entry] = {**equipment, **inventory, **songs}
