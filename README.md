# OoTRandomizer

Documentation for the core features of the randomizer from which this was forked can be found here: <https://github.com/AmazingAmpharos/OoT-Randomizer/blob/master/README.md>

# Notable Changes on this fork

The following were added or majorly changed on this fork:

## GUI changes

- Seeds can be text instead of just numbers
- Can get, share, and import a settings string to quickly set seed-changing options
- Options are saved when closing the GUI and loaded when opening it
- Can set Output directory

## Notable Logic changes

- The Heart Piece at the cow in Impa's house can be reached using only a chicken
- Giant stairs in Dodongo's Cavern can be lowered with the Bow as an adult (quickly shoot a bomb flower on both side of the stairs)
- The start of child-side Spirit Temple can be done with bombchus (aim the bombchu directly away from the bridge so that it crawls up the wall, across the ceiling, down the raised bridge, and explodes in front of the switch)
- The skulltula token in the central room of the Water Temple can be obtained without longshot by setting Farore's Wind in the room and using it to return to the room when the water level is back at its highest level
- In order to fix a potential softlock, Like-Likes do not steal tunics, but can still steal shields.

## Optional Logic changes

A bunch of optional logic changes can be applied from the "Detailed Logic" tab:

- Number of maximum expected gold skulltula tokens can be set
- Some particularly annoying locations can be removed from logic. This only makes it so that getting the item at the location is never required, it does not mean the location's vanilla item is not shuffled into the pool. For example, checking "No Biggoron Reward" just means that you cannot be expected to complete the adult trade sequence, it does not mean that the Biggoron Sword cannot be found somewhere in the world.
- A handful of easy tricks (that require some knowledge) can be marked to be usable
- Lens of Truth requirements and expectations can be set

## Fast Ganon broken into components

What was once called `fast_ganon` is now broken into 3 separate options:

- `trials`: specify the number of trials you need to do to dispel the barrier on Ganon's Tower (0-6). The trials you need to complete will be selected randomly.
- `unlocked_ganondorf`: the boss key door in Ganon's Tower will be unlocked from the start.
- `no_escape_sequence`: the tower collapse escape sequence between the Ganondorf and Ganon fights will be skipped .

## Gerudo Fortress options

Options for speeding up carpenter rescue portion of Gerudo Fortress

- fast: Only the carpenter nearest to the prison Link is tossed into needs to be freed to obtain the Gerudo Card; the other three carpenters are freed from the start
- open: All carpenters are freed from the start, and you start with the Gerudo Card (and thus the bridge across the valley is always built)

There is also an option to shuffle the Gerudo Card into the item pool; this will only work if fortress is not open. A few notes on the behavior of Gerudo Fortress:

- In order to not be caught by guards, you must have rescued all carpenters. The Gerudo Card itself will not protect you.
- In order to enter Gerudo Training Grounds, you must rescue all carpenters AND have the Gerudo Card. This is the Gerudo Card's only purpose.
- Horseback Archery only requires rescuing all carpenters.
- In keysanity, the keys dropped by the guards at each carpenter's cell will be random items, and the fortress keys will be somewhere in the world. However, a key is not sufficient to open a cell: in order to unlock a cell, you must first defeat the guard in the room and collect the item they drop.

## Other Conveniences

Options to skip some sequences that only pad the time of completing the game without ever really changing between seeds have been added:

- `no_guard_stealth`: the stealth sequence between the crawlspace into Hyrule Castle and Zelda's courtyard will be skipped.
- `no_epona_race`: you can summon Epona with her song without racing Ingo.
- `only_one_big_poe`: the poe buyer will give the reward after selling 1 Big Poe instead of 10.
- `default_targeting`: set the default targeting mode to be either `switch` or `hold`.
- `progressive_bombchus`: first bombchu pack is always 20. subsequent ones will give 10 if low, and 5 otherwise.
- `free_scarecrow`: Start with the Scarecrow Song. You do not need go to the scarecrow patch as adult or child to use the song.
- `scarecrow_song`: The song for the Scarecrow Song if `free_scarecrow` is True. Song notes can be any of AUDLR.

## Bombchus

Bombchus can be added to logic with `bombchus_in_logic`. That is, once you've found bombchus, you can be expected to use them as explosives, hit switches, etc. to make progress in the seed. In order to have this make sense, the following changes were made:

- The back alley bombchu shop will now stock bombchus once you have bombchus in your inventory (even if you have 0). All options in this shop no longer sell out, and the right shelf's bottom-left pack is a sale of 5 bombchus for 60 rupees. Thus, once you have found bombchus, you can always buy more.
- Bomchu Bowling is now playable only once you have bombchus in your inventory. This gives bombchus some unique power beyond the spirit trial, and also keeps them better self-contained (since you win bombchus from this mini-game).

As a note, if you have access to the Wasteland carpet salesman and have a wallet upgrade, you can buy bombchus from him to get your first pack.

## Malon Egg

The Weird Egg can be shuffled into the item pool with `shuffle_weird_egg`. This means that Malon will give a random item and that you must find the Weird Egg (and hatch it) before being able to visit Zelda.

Regardless of whether of not you use this option, Malon has been sped up in the following ways:
- Malon will never appear in the Castle Market, instead she will be waiting by the vines from the start of the game
- You do not need to talk to Malon twice to get her item. She will give it by talking only once
- The condition for Malon to move to Lon Lon Ranch is now obtaining her item and Talon fleeing the castle (instead of just Talon fleeing the castle)
- At Lon Lon Ranch, you no longer need to speak to Malon multiple times before she will teach you her song. You can simply walk up to her and pull out your Ocarina.

## Fairy Ocarina and Ocarina of Time

The Fairy Ocarina and Ocarina of Time can be shuffled into the item pool with `shuffle_ocarinas`. This means that Saria and the Ocarin of Time will give a random item and that you must find the Ocarina before being able to play any songs.

## Shuffle Songs into the Pool

Enabling `shuffle_song_items` will make learning songs into items and shuffle the songs into the item pool. Song can appear at any location, and any item can appear at the original song locations.

## Keysanity

Dungeon items (maps, compasses, small keys, boss keys) are shuffled into the item pool at large.

This was actually mostly implemented, I just pulled the trigger...

## Tokensanity

Gold Skulltula Token are added to the item pool, and Gold Skulltula locations give random items. There are two levels for this option: complete shuffle of all 100 tokens, or shuffling only the tokens inside dungeons (there are 44.) The later option can add variance to small key layout in dungeons when keysanity is turned off.

In addition there is an option for the logic to expect Sun's Song to obtain any night-only skulltula token.

## Changed hint system

The hint system has been changed to include different kinds of hints (such as saying a location has something good, but not saying what item it is, or saying a specific item is somewhere in a dungeon, instead of giving the specific location, and so on.) An option has been added to allow talking to gossip stones from the start. Yes, this makes the Stone of Agony completely useless.

## Text shuffle

You can shuffle most of the text in the game. This is hilarious, but can get really confusing when buying from shops and such, so make sure you really know what people are actually asking for.

## Ocarina song randomization

You can randomize the note pattern that is required to activate each song. The new songs will be properly taught to you when you learn them, and can always be checked on the quest status screen like normal.

## Navi color options

Similar to the tunic color options, you can change Navi's color for each of her different kinds of targets.

## Navi sound options

Similar to the low health sound option, you can change the sound Navi makes while targeting or when she has a hint for you.

## Chest size matches contents

`correct_chest_sizes`: Major items will appear in a large chest and other items in small chests. There are a few places that cannot be correctly updated:
- Chests in Generic Grottos
- Chests summoned by Zelda's Lullaby
- Chests summoned by Sun's Song Triggered
- Chests summoned by a switch that do not fall

## Difficulty options

If you seek an additional challenge in regards to combat during the randomizer, you can increase the difficulty with the following settings:

- `normal`: no changes to the item pool
- `hard`: double defense, double magic, and all 8 heart containers are removed
- `very_hard`: Double defense, double magic, Nayru's Love, and all health upgrades are removed
- `ohko`: Link die in one hit...

The `hard` difficulty still leaves the heart pieces in the pool, so you can gain up to 12 hearts total, likely a few less though. It also doesn't remove NL, but still takes away double magic so it can't be spammed for multiple minutes of invulnerability.
The `very_hard` difficulty just takes it all away, meaning the player will stay at 3 hearts without double defense or Nayru's Love.
