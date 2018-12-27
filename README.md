# OoTRandomizer

This is a randomizer for _The Legend of Zelda: Ocarina of Time_ for the Nintendo 64.

### Installation

It is strongly suggested users get the latest release from here:  
  
https://github.com/AmazingAmpharos/OoT-Randomizer/releases  
  
Simply download the .msi installer and run it. We support  Windows, Mac, and Linux machines.

If you have an incompatible OS or you simply wish to run the script raw, clone this repository and either run ```Gui.py``` for a
graphical interface or ```OoTRandomizer.py``` for the command line version. Both require Python 3.6+. This will be fully featured,
but the seeds you generate will have different random factors than the bundled release.

This randomizer requires The Legend of Zelda: Ocarina of Time version ```1.0 NTSC-US```. This randomizer includes an in-built decompressor, but if
the user wishes a pre-decompressed ROM may be supplied as input. Please be sure your input ROM filename is either a .n64 or .z64 file. For users
playing via any means other than on real N64 hardware, the use of the "Compress patched ROM" flag is strongly encouraged as uncompressed ROMs are
impossible to inject for the Virtual Console and have random crashing problems on all emulators.

For general use, the recommended emulator is RetroArch; it has been shown to work with minimal issues. Bizhawk and Mupen64plus are generally good choices
too. If you want to play on Project 64 for whatever reason, you can but you will need to set the rando to use 8 MB of RAM and will want to play with the
cheat code ```8109C58A 0000``` to partially fix Project 64's tragically poor handling of OoT's pause menu. Project 64 also has one particular crash that only
happens for some unknown settings configurations; we cannot support this. I cannot emphasize enough that it is a discouraged emulator to use.

### General Description

This program takes _The Legend of Zelda: Ocarina of Time_ and randomizes the locations of the items for a new, more dynamic play experience.
Proper logic is used to ensure every seed is possible to complete without the use of glitches and will be safe from the possibility of softlocks with any possible usage of keys in dungeons.

The randomizer will ensure a glitchless path through the seed will exist, but the randomizer will not prevent the use of glitches for those players who enjoy that sort of thing though we offer no guarantees that all glitches will have identical behavior to the original game.
Glitchless can still mean that clever or unintuitive strategies may be required involving the use of things like Hover Boots, the Hookshot, or other items that may not have been as important in the original game.

Each major dungeon will earn you a random Spiritual Stone or Medallion once completed.
The particular dungeons where these can be found, as well as other relevant dungeon inforomation can be viewed in the pause menu by holding the "A" button on the C-Item Menu.

As a service to the player in this very long game, many cutscenes have been greatly shortened, and text is as often as possible either omitted or sped up. I'm sure someone somewhere will miss the owl's interjections; to that person, I'm sorry I guess?

### Getting Stuck

With a game the size of _Ocarina of Time_, it's quite easy for new Randomizer players to get stuck in certain situations with no apparent path to progressing. Before reporting an issue, please make sure to check out our **_new FAQ section_** [found here](../../wiki/FAQ---Broken-Seed).

### Settings

The OoT Randomizer offers many different settings to customize your play experience.
A comprehensive list can be found [here](../../wiki/Setting-Information).

### Known issues

Sadly a few known issues exist. These will hopefully be addressed in future versions.

* The fishing minigame sometimes refuses to allow you to catch fish when playing specifically on Bizhawk. Save and quit (NOT savestate) and return to fix the issue.
* Draining the Bottom of the Well with Song of Storms sometimes crashes on specific configurations of Project 64. We aren't sure of the exact story, but this bug is
easily avoided by playing on a different emulator and probably also avoidable by changing your settings and maybe graphics plug-in.
* Executing the collection delay glitch on various NPCs may have unpredictable and undesirable consequences. In particular this can be devastating with Biggoron;
it is strongly suggested the player save before turning in the Claim Check.
* Saving and quitting on the very first frame after becomming an adult when you would trigger the Light Arrow cutscene can have undesired consequences. Just don't
do that.
* This randomizer is based on the 1.0 version of Ocarina of Time so some of its specific bugs remain. Some of these like "empty bomb" can be disadvantagous to the
player.
