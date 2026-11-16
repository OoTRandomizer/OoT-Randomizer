# Language Texture Notes
This file indicates what to do to create Language files

## Sources
### Useful links
* [Cloud Modding](https://wiki.cloudmodding.com/oot/Main_Page) - Allows to know the system / specific object addresses
* Zeldalegends - Search *OoT `language like german` text dump html zeldalegends* for the great resources for translation / actual texts

### Need to have
* [zeldaret/oot](https://github.com/zeldaret/oot) - Decompiler for OoT roms with various regions
* OoT Rom
* Photoshop or any other kind of drawing software
* Absurdly amount of patient

### Fonts
* Message text uses **Chiaro font**
* Title card for bosses uses **Kokinedo font**
* Title for Japanese (ゼルダの伝説 時のオカリナ under the title) uses **Matisse font**
* System font like `Action` in `assets/textures/do_action_static` is unknown

## Texture Placements
Most of textures are located in `assets/textures`  
Some of textures like Boss title cards and title are located in `assets/objects`

(The file path below ~/assets/~)
| Bin Patch Name | File Path | Notes |
| -- | -- | -- |
| title.bin | objects/object_mag | Title Screen logo |
| keaton.bin | textures/item_name_static | Only for English (It's within ItemNameEN.bin) |
| NESFont.bin | textures/nes_font_static | English Font for Messages |
| Kanji.bin | textures/kanji | Japanese Font for Messages |
| EXTitleCard.bin | textures/icon_item_static | Extra Pause Screen textures for some Languages (German for example has extra textures for PauseSelectItem) |
| Gameover.bin | textures/icon_item_gameover_static | Game Over Screen Assets (JP & EN) |
| TitleCardJP.bin | textures/icon_item_jpn_static | Pause Menu Labels & Dungeon Names for Japanese |
| TitleCardEN.bin | textures/icon_item_nes_static | Pause Menu Labels & Dungeon Names for English |
| ItemNameJP.bin | textures/item_name_static | Pause Menu Inventory Item Names for Japanese |
| ItemNameEN.bin | textures/item_name_static | Pause Menu Inventory Item Names for English |
| MapName.bin | textures/map_name_static | Pause Menu Overworld Location Names (JP & EN) |
| ActionJP.bin | textures/do_action_static | Action Button Labels for Japanese |
| ActionEN.bin | textures/do_action_static | Action Button Labels for English |
| PlaceName.bin | textures/place_title_cards | Place Name (JP & EN) |
| FileSelJP.bin | textures/title_static | File Select & Option Screen Assets for Japanese |
| FileSelEN.bin | textures/title_static | File Select & Option Screen Assets for English |
| -- | -- | -- |
| KingDodongo.bin | object/object_kingdodongo | Kingdodongo Titlecard |
| Gohma.bin | object/object_goma | Gohma Titlecard (object name missing h between o and m)|
| PhantomGanon.bin | object/object_fhg | Phantom Ganon Titlecard (object name was mislabeled name of itself, fh = ph) |
| Barinade.bin | object/object_bv | Barinade Titlecard (object name is short for Boss using Boomerang, v indicates the shape of Boomerang) |
| Volvagia.bin | object/object_fd | Volvagia Titlecard (object name is short for flying dragon) |
| Morpha.bin | object/object_mo | Morpha Titlecard (object name is short of the name of itself) |
| Twinrova.bin | object/object_tw | Twinrova Titlecard (object name is short for twin) |
| Ganondorf.bin | object/object_ganon | First phase Ganondorf Titlecard |
| Bongo.bin | object/object_sst | Bongobongo Titlecard (object name is short for S + Shadow Temple, object_st is for Gold Skulltula) |
| Ganon.bin | object/object_ganon2 | 2nd Phase Ganon Titlecard |
