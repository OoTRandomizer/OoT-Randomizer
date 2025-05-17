# OoTRandomizer

This is a randomizer for _The Legend of Zelda: Ocarina of Time_ for the Nintendo 64.

* [Installation](#installation)
* [General Description](#general-description)
  * [Getting Stuck](#getting-stuck)
  * [Settings](#settings)
  * [Known Issues](#known-issues)
* [Changelog](#changelog)

## Installation

It is strongly suggested users use the web generator from here:

<https://ootrandomizer.com/>

If you wish to run the script raw, clone this repository and either run ```Gui.py``` for a
graphical interface or ```OoTRandomizer.py``` for the command line version. They both require Python 3.8+.
To use the GUI, [NodeJS](https://nodejs.org/download/release/v20.17.0/) (v20 LTS, with npm) will additionally need to be installed. NodeJS v14.14.0 and earlier are no longer supported.
The first time ```Gui.py``` is run it will need to install necessary components, which could take a few minutes. Subsequent instances will run much quicker.
Supported output formats are .z64 (N64/Emulator), .wad (Wii VC, channel IDs NICE/NRKE recommended), Uncompressed ROM (for developmental purposes, offline build only)
and .zpf/.zpfz (patch files, for sharing seeds with others).

This randomizer requires The Legend of Zelda: Ocarina of Time version ```1.0 NTSC-US```. This randomizer includes an in-built decompressor, but if
the user wishes a pre-decompressed ROM may be supplied as input. Please be sure your input ROM filename is either a .n64 or .z64 file. For users
playing via any means other than on real N64 hardware, the use of the "Compress patched ROM" flag is strongly encouraged as uncompressed ROMs are
impossible to inject for the Virtual Console and have random crashing problems on all emulators.

For general use, there are four recommended emulators: [Project64 (v3.0+)](https://wiki.ootrandomizer.com/index.php?title=Project64), [Bizhawk](https://wiki.ootrandomizer.com/index.php?title=Bizhawk), [RetroArch](https://wiki.ootrandomizer.com/index.php?title=Retroarch) and [Dolphin (latest beta)](https://wiki.ootrandomizer.com/index.php?title=Dolphin). All are race-legal when configured appropriately.
In a nutshell the differences are:
* Project64 is the lightest emulator and the easiest to setup, however, you will need the 3.0.0 version or later to run OoTR well (and earlier versions are not permitted for use in OoTR races).
* Bizhawk is the most resource-intensive, but easier to set up than RetroArch and the only race-legal emulator to support [Multiworld](https://wiki.ootrandomizer.com/index.php?title=Multiworld).
* RetroArch is less resource-intensive than Bizhawk and the only of the three N64 emulators to work on platforms other than Windows, but it can be frustrating to set up.
* Dolphin lets you emulate Wii VC, giving you access to faster pauses. It's also lightweight, available on other platforms than Windows, easy to setup (on Windows at least) and offers good native support with most Gamecube Controller Adapters. It does come with more lag, although that can be mitigated through overclocking (this is not permitted for racing).

Please follow [the guides on our wiki](https://wiki.ootrandomizer.com/index.php?title=Setup#Emulators) carefully to ensure a stable game experience and that
[the settings requirements for races](https://wiki.ootrandomizer.com/index.php?title=Racing#Emulator_Settings_Requirements) are met. OoTR can also be run on
an N64 using an [EverDrive](https://wiki.ootrandomizer.com/index.php?title=Everdrive), or on [Wii Virtual Console](https://wiki.ootrandomizer.com/index.php?title=Wii_Virtual_Console). For questions and tech support we kindly refer you to our [Discord](https://discord.gg/q6m6kzK).

## General Description

This program takes _The Legend of Zelda: Ocarina of Time_ and randomizes the locations of the items for a new, more dynamic play experience.
Proper logic is used to ensure every seed is possible to complete without the use of glitches and will be safe from the possibility of softlocks with any possible usage of keys in dungeons.

The randomizer will ensure a glitchless path through the seed will exist, but the randomizer will not prevent the use of glitches for those players who enjoy that sort of thing, though we offer no guarantees that all glitches will have identical behavior to the original game.
Glitchless can still mean that clever or unintuitive strategies may be required involving the use of things like Hover Boots, the Hookshot, or other items that may not have been as important in the original game.

Each major dungeon will earn you a random Spiritual Stone or Medallion once completed.
The particular dungeons where these can be found, as well as other relevant dungeon information can be viewed in the pause menu by holding the D-Pad buttons on the C-Item Menu.
Note, however, that the unlock conditions for dungeon information are settings-dependent.

As a service to the player in this very long game, many cutscenes have been greatly shortened or removed, and text is as often as possible either omitted or sped up. It is likely that someone somewhere will miss the owl's interjections; to that person, I'm sorry I guess?

### Getting Stuck

With a game the size of _Ocarina of Time_, it's quite easy for new Randomizer players to get stuck in certain situations with no apparent path to progressing. 
Before reporting an issue, please make sure to check out [our Logic wiki page](https://wiki.ootrandomizer.com/index.php?title=Logic). 
We also have many community members who can help out in our [Discord](https://discord.gg/8nmX7fa).

### Settings

The OoT Randomizer offers many different settings to customize your play experience.
A comprehensive list can be found [here](https://wiki.ootrandomizer.com/index.php?title=Readme).

#### Plandomizer

"Plan"-domizer is a feature that gives some additional control over the seed generation using a separate distribution file. In such a file you can:
* Place items at specific locations or restrict items from being placed at specific locations.
* Add or remove items from the item pool.
* Select items to start with.
* Set specific dungeons to be vanilla vs Master Quest.
* Set which trials are required.
* Set any regular settings.

Caveat: Plandomizer settings will override most settings in the main OoTR generator settings, particularly list-based settings like enabled tricks or starting inventory. For example, if the Plandomizer distribution file contains an empty list of starting items, and the generator settings include additional starting equipment, the player will start with none of them instead. You will have to edit the Plandomizer file to change such settings, or **delete** completely the line in the Plandomizer file with the given setting to allow the main generator to alter the setting.

See [the Plandomizer wiki page](https://wiki.ootrandomizer.com/index.php?title=Plandomizer) for full details.

#### Custom Models

Save the .ZOBJ file of the desired model in `data/Models/Adult` or `data/Models/Child`. The file must be in .ZOBJ format (the compressed .PAK files are not compatible), but most Modloader64 models will work. Exceptions are models which are larger than the base Link models (the randomizer will give an error message) and those created on the new pipeline (technically load but the textures get wonky). Please see notes regarding known model files that are floating around [in this spreadsheet](https://docs.google.com/spreadsheets/d/1xbJnYw8lGR_qAkpvOQXlzvSUobWdX6phTm1SRbXy4TQ/edit#gid=1223582726) before asking why a model doesn't work.

Once the models are saved, the program may be opened and the model(s) selected under the `Cosmetics` tab.

If the model's skeleton is similar enough to Link, the randomizer will use Link's skeleton. If it is substantially different, then a note will be placed on the pause screen to make it clear that the skeleton was changed.

### Known issues

Unfortunately, a few known issues exist. These will hopefully be addressed in future versions.

* The fishing minigame sometimes refuses to allow you to catch fish when playing specifically on Bizhawk. Save and Hard Reset (NOT savestate) and return to fix the
issue. You should always Hard Reset to avoid this issue entirely.
* Versions older than 3.0 of Project64 have known compatablity issues with OoTR. To avoid this either 
[update to v3.0 and follow the rest of our Project64 guide](https://wiki.ootrandomizer.com/index.php?title=Project64) or change to one of our other two supported emulators.
* Executing the collection delay glitch on various NPCs may have unpredictable and undesirable consequences.
* This randomizer is based on the 1.0 version of _Ocarina of Time_, so some of its specific bugs remain.

## Changelog

The changelog has moved to [CHANGELOG.md](CHANGELOG.md).

For an overview of settings additions by release, see [the wiki](https://wiki.ootrandomizer.com/index.php?title=Readme#Generation_Options).
