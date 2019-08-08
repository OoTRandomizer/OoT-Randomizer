# OoTRandomizer

This is a randomizer for _The Legend of Zelda: Ocarina of Time_ for the Nintendo 64.

* [Installation](#installation)
* [General Description](#general-description)
  * [Getting Stuck](#getting-stuck)
  * [Settings](#settings)
  * [Known Issues](#known-issues)
* [Changelog](#changelog)
  * [New Features](#new-features)
  * [New Options](#new-options)
  * [Updated Features](#updated-features)
  * [Updated Options](#updated-options)
  * [Bug Fixes](#bug-fixes)
  * [Multiworld Changes](#multiworld-changes)
  * [Development Version Changes](#development-version-changes)

## Installation

It is strongly suggested users use the web generator from here:

https://ootrandomizer.com

If you wish to run the script raw, clone this repository and either run ```Gui.py``` for a
graphical interface or ```OoTRandomizer.py``` for the command line version. They both require Python 3.6+. This will be fully featured,
but the seeds you generate will have different random factors than the bundled release.

This randomizer requires The Legend of Zelda: Ocarina of Time version ```1.0 NTSC-US```. This randomizer includes an in-built decompressor, but if
the user wishes a pre-decompressed ROM may be supplied as input. Please be sure your input ROM filename is either a .n64 or .z64 file. For users
playing via any means other than on real N64 hardware, the use of the "Compress patched ROM" flag is strongly encouraged as uncompressed ROMs are
impossible to inject for the Virtual Console and have random crashing problems on all emulators.

For general use, the recommended emulator is RetroArch; it has been shown to work with minimal issues. Bizhawk and Mupen64plus are generally good choices
too. If you want to play on Project 64 for whatever reason, you can, but you will need to set the rando to use 8 MB of RAM and will want to play with the
cheat code ```8109C58A 0000``` to partially fix Project 64's tragically poor handling of OoT's pause menu. Project 64 also has one particular crash that only
happens for some unknown settings configurations; we cannot support this. We cannot emphasize enough that it is a discouraged emulator to use.

## General Description

This program takes _The Legend of Zelda: Ocarina of Time_ and randomizes the locations of the items for a new, more dynamic play experience.
Proper logic is used to ensure every seed is possible to complete without the use of glitches and will be safe from the possibility of softlocks with any possible usage of keys in dungeons.

The randomizer will ensure a glitchless path through the seed will exist, but the randomizer will not prevent the use of glitches for those players who enjoy that sort of thing though we offer no guarantees that all glitches will have identical behavior to the original game.
Glitchless can still mean that clever or unintuitive strategies may be required involving the use of things like Hover Boots, the Hookshot, or other items that may not have been as important in the original game.

Each major dungeon will earn you a random Spiritual Stone or Medallion once completed.
The particular dungeons where these can be found, as well as other relevant dungeon inforomation can be viewed in the pause menu by holding the "A" button on the C-Item Menu.

As a service to the player in this very long game, many cutscenes have been greatly shortened, and text is as often as possible either omitted or sped up. It is likely that someone somewhere will miss the owl's interjections; to that person, I'm sorry I guess?

### Getting Stuck

With a game the size of _Ocarina of Time_, it's quite easy for new Randomizer players to get stuck in certain situations with no apparent path to progressing. Before reporting an issue, please make sure to check out [our Logic wiki page](https://wiki.ootrandomizer.com/index.php?title=Logic).

### Settings

The OoT Randomizer offers many different settings to customize your play experience.
A comprehensive list can be found [here](https://wiki.ootrandomizer.com/index.php?title=Readme).

### Known issues

Unfortunately, a few known issues exist. These will hopefully be addressed in future versions.

* The fishing minigame sometimes refuses to allow you to catch fish when playing specifically on Bizhawk. Save and Hard Reset (NOT savestate) and return to fix the
issue. You should always Hard Reset to avoid this issue entirely.
* Draining the Bottom of the Well with Song of Storms sometimes crashes on specific configurations of Project 64. We aren't sure of the exact story, but this bug is
easily avoided by playing on a different emulator and probably also avoidable by changing your settings and maybe graphics plug-in.
* Executing the collection delay glitch on various NPCs may have unpredictable and undesirable consequences.
* Saving and quitting on the very first frame after becoming an adult when you would trigger the Light Arrow cutscene can have undesired consequences. Just don't
do that.
* This randomizer is based on the 1.0 version of _Ocarina of Time_, so some of its specific bugs remain. Some of these like "empty bomb" can be disadvantagous to the
player.

## Changelog

### 5.0

#### New Features
* New Electron GUI
  * New GUI now utilizes both Python and Node to bring you an even better interface
  * Now requires Node (with NPM), in addition to the Python requirement
* Glitched Logic
  * New Logic Rules option that takes movement glitches into consideration
  * Check out the Wiki for more information
* Entrance Randomizer
  * Randomize entrances/loading zones
  * Entrances are connected bidirectionally, and only shuffled with other entrances of the same pool
  * Ability to randomize entrances (loading zones) among multiple pools:
    * `Dungeons Only`: All Dungeons except Ganon's Castle
    * `Simple Indoors`: Dungeons; as well as Houses, Great Fairies, all Open and Hidden Grottos (including small Fairy Fountains and the Lost Woods Stage), and Graves.
    * `All Indoors`: Dungeons and Simple Indoors, as well as Link’s House, the Temple of Time, the Windmill, and Dampe’s Grave.
    * `All Indoors & Overworld Entrances`: Almost all loading zones connecting overworld areas, including Owls
  * Deku Tree, Fire Temple, and Bottom of the Well dungeon entrances are accessible as both ages
* Starting Age Option
  * Can now start as child, adult, or random
* Plan-domizer
  * Create a custom seed by placing items, hints and/or entrances where you want them
  * Customize starting items, item pools, active trials and Master Quest dungeons
  * Distribution files match the spoiler log JSON format
* Additional Customization
  * Additional Background Music Sequences can now be provided to be shuffled in
  * Fanfares randomization
  * Customizable Heart, Magic Meter, and Gauntlet colors
  * Separate inner and outer Navi colors
* Added `Randomize Main Rules` option
* Cow Sanity
  * Playing Epona's Song for a cow for the first time gives a randomized item.
* Shuffle Magic Beans
  * A pack of 10 beans is shuffled into the pool and the Bean Salesman sells a random item once for 60 rupees.
* Cucco Count
  * The number of cuccos to be gathered for Anju can be reduced or randomized, and Anju will tell you in-game the target number to catch (similar to 10 Big Poes).
* Enable Useful Cutscenes prevents some useful cutscenes from being skipped
  * Re-enables Poes at Forest Temple, Darunia at Fire Temple, and Twinrova at Spirit Temple

#### Major Changes
* Seeds generation is significantly faster
* Major refactor of logic for performance and ER
* Spoiler log is now in JSON format
* Log files are produced in `Logs` during generation to record any errors.
* Major Logic Changes
  * Desert Colossus Hands are now logically part of Spirit Temple
  * Added the ability to enter drain the Lake Hylia water as Adult after beating Morpha using a new Gossip Stone near the Serenade Warp Pad. Entering Water Temple with Gold Scale and Longshot is now always in logic, however no locations are accessible without additional tricks, Keysanity/Keysy, or Iron Boots.
  * Disabled Locations will always hold Junk items (except song locations if songs are not shuffled with items)
* Gameplay Changes
  * Mechanically, Hot Rodder Goron no longer checks for Bomb Bag
  * Wearing Bunny Hood increases running speed to match backwalking speed
  * All Gerudo now check for Gerudo Membership Card instead of Carpenters being freed
    * This only affects when `Shuffle Gerudo Card` is enabled or in Entrance Randomizer
    * In the affected modes, a Gerudo is added behind the Wasteland gate who can open the gate
* Hint Changes
  * Every generic grotto gossip stone has their own hint.
  * The "Very Strong" hint setting can now give multiple Foolish dungeon hints.
* Cutscene Changes
  * Burning Kakariko Cutscene can be triggered when entering Kakariko Village from any entrance.
  * Speedup Owl Flying cutscenes to be almost instant.
  * Enable Useful Cutscenes setting added (see above in New Features)

#### Updated Settings 
* Filter added to `Location Exclusion` dropdown
* More tricks added to the `Enable Tricks` dropdown
* Shuffle Gerudo Card can now be enabled alongside Open Gerudo Fortress.
* Forest Options
  * `Closed Deku`: Open Forest except Mido still blocks the Deku Tree
* Dungeon Item Options
  * Added `Vanilla` placement option for small keys, boss keys and maps/compasses
* Ganon's Boss Key 
  * Split Ganon’s Boss Key settings from the rest of the Boss Keys setting
  * Added LACS options that place the key there.
    * This allows playing with open bridge while still requiring dungeon completion
  * This replaces the Remove Ganon’s Boss Door Lock option
* Plentiful Item Pool
  * Duplicate Letter in a Bottle added to plentiful item pool
* With `Start With Max Rupees` option enabled, wallet upgrades items now fill to max rupees

#### Bug Fixes
* No longer able to buy Bombchus with only bomb bag when Bombchus in logic
* Dampé freestanding Piece of Heart no longer requires opening the chest
* Buying Piece of Heart/Heart Container fully heals Link
* Learning Sun's Song from Malon no longer causes a softlock
* Castle and Gerudo guards can no longer cause softlock when catching you
* Vanilla shop items have correct price in spoiler log with shopsanity enabled
* Fixed Song of Storms not being usable in Sacred Forest Meadow immediately after learning it
* Improved Bottled Fairy logic rules for OHKO in ER
* Fixed `Starting Time of Day` times to better reflect their descriptions with the in-game state
  * `Night` options will spawn Skulltulas
* Add compatibility support for Python 3.8
* Improved Spoiler Logs for Multiworlds with differing Random settings between worlds
* Lab Dive now completable even with Eyedrops in your possession
* Great Fairy cutscene no longer plays on additional visits for health and magic refills.


### 4.0

#### New Features

* Quick boot equips
  * Use D-pad left to equip Iron Boots if they're in the inventory, or D-pad right to equip Hover Boots if they're in the inventory.
  * Press the button again to equip Kokiri Boots.
* Quck Ocarina
  * Use D-pad down to pull out the Ocarina.
* Freestanding models
  * All freestanding item locations now display the model of the item you will receive.
* Ice traps now work from any location.
  * In freestanding locations, appears as a random major item
  * In shops, appears as a random major item with a misspelling
* Various speedups
  * No Talon cutscene when he runs away
  * Skip "Caught By Gerudo" cutscene
  * Shorten cutscene when getting Bullet Bag from the Deku Scrub in Lost Woods
  * Fast pushing and pulling
    * All types of blocks
    * Spinnable mirrors in Spirit Temple
    * Truth spinner in Shadow Temple
    * Puzzle in basement of Forest Temple
  * Ocarina minigame shortened to the first round
    * 5 notes instead of 8
  * Jabu-Jabu's Belly elevator spawns in a more convenient position
  * Kakariko carpenter position is offset so he is no longer in your way during the cucco route.
  * Warp songs now have a normal transition with no cutscene.
  * Pause screen starts on Inventory Screen instead of Map Screen
* Gold Skulltula textbox displays current number obtained
* Poe salesman tells point limit without needing to sell
* Patch files added so that generated seeds can be distributed legally

#### New Options

* Master Quest dungeon slider
  * Selects a number of Master Quest dungeons to appear in the game
    * Ex: 0 - All dungeons will have their default designs.
    * Ex: 6 - Half of all dungeons will have Master Quest redesigns.
    * Ex: 12 - All dungeons will have Master Quest redesigns.
* Damage multiplier
  * Changes the amount of damage taken
  * OHKO: Link dies in one hit
* Item pool
  * Replaces difficulty
  * Changes the number of bonus items that are available in the game
    * Plentiful: Extra major items are added
    * Balanced: The original item pool
    * Scarce: Some excess items are removed, including health upgrades
    * Minimal: Most excess items are removed
* Start with max rupees
  * The player begins the game with 99 rupees.
* Start with Deku equipment
  * The player begins the game with 10 Deku sticks and 20 Deku nuts.
  * If playing without shopsanity, the player begins with a Deku shield equipped.
* Start with fast travel
  * The player begins the game with the Prelude of Light and Serenade of Water songs learned and the Farore's Wind spell in the inventory.
  * These three items increase Link's mobility around the map, but don't actually unlock any new items or areas.
* Start with Tycoon wallet
* Open Zora's Fountain
  * King Zora is moved to the side from the start of the game.
  * Letter in a Bottle is removed from the item pool and replaced with an Empty Bottle.
* Randomize starting time of day
* Ice traps setting
    * Off: All ice traps are removed
    * Normal: Only ice traps from base pool are placed
    * Extra ice traps: Chance to add extra ice traps when junk items are added to the item pool
    * Ice trap mayhem: All junk items added will be ice traps
    * Ice trap onslaught: All junk items will be ice traps, including ones in the base pool
* New Cosmetics
  * Added options for Sword Trail colors
    * Can set the length of the trails
    * Can set the inner and outer colors
    * Can set color to "Rainbow"
  * Additional SFX options

#### Updated Features

* Hints distribution
    * Changes how many useful hints are available in the game
    * Useless: Has nothing but junk hints
    * Balanced: Gives you a mix of useless and useful hints. Hints will not be repeated
    * Strong: Has some duplicate hints and no junk hints
    * Very Strong: Has only very useful hints
    * Tournament: Similar to strong but has no variation in hint types
* Frogs Ocarina Game added to always hints
* Hints are only in logic once you are able to reach the location of the gossip stone by logic.
    * Hints ignore logic if inaccessible
* Foolish choice hint added
  * Regions that are a foolish choice will not have any required items no matter what route is taken in logic.
* Big Poes location does not require a hint if the count set to 3 or less.
* Add medallion icons to the Temple of Time altar hint
* Add a hint for 0/6 trials if trial count is random
* Scrub Shuffle now updates the Business Scrubs' textboxes with the updated price for buying their item.

#### Updated Options

* Chest size matches contents updated
  * Boss keys appear in gold chests
  * Small keys appear in small gold chests
* Free Scarecrow's Song changes
  * Pulling out ocarina near a spot where Pierre can spawn will do so.
* Rainbow Bridge changes
  * Spiritual Stones added as bridge requirement
  * 100 Gold Skulltula tokens added as bridge requirement
* Any location can now be excluded from being required.
* Various advanced tricks has been split into individual tricks to be selected.
* Choose sound effects ocarina uses when played

#### Bug Fixes

* Deku and Hylian shields from chests no longer become Blue Rupees.
* Force game language to be English even if a Japanese rom is supplied
* Door of Time now opens when entering Temple of Time from all spawns.
* Fix empty bomb glitch
* Move item cost to after Player in the spoiler log
* Add Wasteland Bombchu Salesman to spoiler log when required for first Bombchus
* Fix message text table is too long error when using settings that add a lot of text to the ROM
* Kokiri Sword no longer required for fishing as child
* Fix Biggoron Sword collection delay
* Twinrova phase 2 textbox fix
* Switches in Forest and Fire Temple lowered by 1 unit to make it easier to press them
* Equipment menu will now show the name of the item you have in the first column
* Hover Boots will no longer show up as adult in the first equipment menu slot if a Fairy Slingshot was not gotten before becoming adult.
* Ammo items now use the correct item fanfare.
* Fix chest size matches contents to work for all chests
* Removed key for key logic
* Removed unused locked door in Water Temple
* Scarecrow's Song should no longer cause softlocks when played in laggy areas.
* Text error messages no longer display the Pocket Egg text.
* Ice traps added back to OHKO as the softlock appears fixed
* Ganon now says "my castle" instead of "Ganon's Castle" for light arrow hint.
* Fix various typos in text
  * Gerudo's Fortress
  * Zora's River
  * Red Rupee
  * Textbox about Dampé's grave
* "Ganon's Tower" is now just "Ganon's Castle".
* Dampé's Gravedigging Tour reward correctly flags collection on pickup.
* Castle Moat Bridge no longer closes when playing the Zelda Escape cutscene.
* Various logic fixes

#### Multiworld Changes

* Maximum player count increased from 31 to 255
* Ice traps can now be sent to other worlds.
* Ganon now tells you the location of your Light Arrows, not the location of some Light Arrows that may exist in your world.
* Item placement rebalanced so that an item for another player can only be placed on a location that both players can reach in logic

#### Development Version Changes

* Output patch file
  * Creates a binary patch file instead of a ROM which allows sharing a seed without sharing copyright protected material
* Patch ROM from file
  * Applies a generated patch file to the base ROM and creates a randomizer ROM which allows sharing a seed without sharing copyright protected material
* Settings presets
  * Adds a functionality to save settings strings for future use
  * Several presets are already provided.
* Create settings log if spoiler log is disabled
* File names no longer include a settings string.
  * Instead display a shortened SHA-1 hash of the settings string
* Add option for converting settings to a string and back
  * Only convert the specified settings to a settings string
  * If a settings string is specified output the used settings instead
* Python 3.5 is no longer supported.
  * You must have Python 3.6 or higher installed to run the randomizer code.
* Add option to only apply cosmetic patch without generating world data
* CLI uses a specified settings file instead of taking in each option.
  * Uses settings.sav as default if it exists
  * Uses default settings if no settings file is provided and no settings.sav exists
* Version check is no longer a dialog
  * Appears in a frame in the main randomizer window
* Copy settings string button
* The cosmetic versioning has been added to the ROM. Some cosmetics are only applied if they are safe to do so.
* Added ability to set the output file name and added file creation logs
* Major refactor of code
