# Loading custom sequences
To load custom sequences, you need to package into a zip archive with a .ootrs extension: 
  - A raw N64 sequence file with a `.seq` file extension 
  - A metadata file with a `.meta` file extension. The `.meta` file should be a plaintext file as defined below

Any sub-directories in this folder will also be read from. Only .ootrs files with a minimum of a `.seq` and `.meta` are supported

# .Meta file format
A .meta file must contain a minimum of two lines.
  - Line 1: Sequence Name
  - Line 2: Instrument set to use in base 16. Set to `-` if using a custom instrument set
  - Line 3: `bgm` or `fanfare` depending on the type of sequence (`bgm` = background music, `fanfare` = non-looping fanfare). If the file is less than 3 lines, `bgm` is assumed
  - Line 4 (optional): One or more sequence groups, separated by commas
  - Line 5+: Additional metadata. All additional data should use the format COMMAND:DATA:DATA
    Currently support additional metadata types:
    ZSOUND:path_to_zsound_file:bank_address

# Using custom instrument sets
Custom instrument sets may be used in sequences. A full tutorial on creating sequences can be found at https://gist.github.com/owlisnotacat1/e5445c154b46a9d7804b139800dfffbe
To use custom instrument sets, the following additional files must be present in the .ootrs archive
  - An instrument set (soundfont/bank) file with a `.zbank` file extension
  - A bank metadata file with a `.bankmeta` file extension
  - Instrument samples for custom instruments contained in files with `.zsound` (if the custom instrument set also defines new instruments)

Sequences are in the seq64 format. Other known games that use this format and may be compatible are (list from https://github.com/sauraen/seq64)
```
Super Mario 64
Mario Kart 64
Yoshi's Story
Legend of Zelda: Majora's Mask
1080 Snowboarding
F-ZERO X
Lylat Wars
Pokemon Stadium
Pokemon Stadium 2
Wave Race 64
```

There are also tools available to help convert midi files to valid seq64 files.

The instrument list is as follows (from https://github.com/sauraen/seq64):
```
0x00 - Ocarina Songs?
0x01 - Actor Sounds
0x02 - Nature Sounds
0x03 - Hyrule Field (often the best choice, main orchestra with percussion)
0x04 - Deku Tree
0x05 - Castle Market
0x06 - Title Screen
0x07 - Jabu Jabu's Belly
0x08 - Kakariko Village (Guitar)
0x09 - Fairy Fountain (Harp, Strings)
0x0A - Fire Temple
0x0B - Dodongo's Cavern
0x0C - Forest Temple
0x0D - Lon Lon Ranch
0x0E - Goron City
0x0F - Kokiri Forest
0x10 - Spirit Temple
0x11 - Horse Race
0x12 - Warp Songs
0x13 - Goddess Cutscene
0x14 - Shooting Gallery
0x15 - Zora's Domain
0x16 - Shop
0x17 - Ice Cavern
0x18 - Shadow Temple
0x19 - Water Temple
0x1A - Unused Piano
0x1B - Gerudo Valley
0x1C - Lakeside Laboratory
0x1D - Kotake and Koume's Theme
0x1E - Ganon's Castle (Organ)
0x1F - Inside Ganon's Castle
0x20 - Ganondorf Battle
0x21 - Ending 1
0x22 - Ending 2
0x23 - Game Over / Fanfares
0x24 - Owl
0x25 - Unknown (probably should not use)
```
