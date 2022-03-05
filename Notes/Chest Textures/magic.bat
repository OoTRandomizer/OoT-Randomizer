@echo off
magick -size 32x32 -depth 8 silver_base.png ^
-channel R +level 0,31 -evaluate leftshift 11 -evaluate and 63488 +channel ^
-channel G +level 0,31 -evaluate leftshift 6 -evaluate and 1984 +channel ^
-channel B +level 0,31 -evaluate leftshift 1 -evaluate and 62 +channel ^
-channel A -evaluate and 1 +channel ^
-channel RGBA -separate +channel ^
-channel R -evaluate-sequence add  +channel ^
-depth 16 -endian MSB R:silver_chest_base.bin

magick -size 32x64 -depth 8 silver_front.png ^
-channel R +level 0,31 -evaluate leftshift 11 -evaluate and 63488 +channel ^
-channel G +level 0,31 -evaluate leftshift 6 -evaluate and 1984 +channel ^
-channel B +level 0,31 -evaluate leftshift 1 -evaluate and 62 +channel ^
-channel A -evaluate and 1 +channel ^
-channel RGBA -separate +channel ^
-channel R -evaluate-sequence add  +channel ^
-depth 16 -endian MSB R:silver_chest_front.bin

magick -size 32x32 -depth 8 gilded_base.png ^
-channel R +level 0,31 -evaluate leftshift 11 -evaluate and 63488 +channel ^
-channel G +level 0,31 -evaluate leftshift 6 -evaluate and 1984 +channel ^
-channel B +level 0,31 -evaluate leftshift 1 -evaluate and 62 +channel ^
-channel A -evaluate and 1 +channel ^
-channel RGBA -separate +channel ^
-channel R -evaluate-sequence add  +channel ^
-depth 16 -endian MSB R:gilded_chest_base.bin

magick -size 32x64 -depth 8 gilded_front.png ^
-channel R +level 0,31 -evaluate leftshift 11 -evaluate and 63488 +channel ^
-channel G +level 0,31 -evaluate leftshift 6 -evaluate and 1984 +channel ^
-channel B +level 0,31 -evaluate leftshift 1 -evaluate and 62 +channel ^
-channel A -evaluate and 1 +channel ^
-channel RGBA -separate +channel ^
-channel R -evaluate-sequence add  +channel ^
-depth 16 -endian MSB R:gilded_chest_front.bin

magick -size 32x32 -depth 8 spider_base.png ^
-channel R +level 0,31 -evaluate leftshift 11 -evaluate and 63488 +channel ^
-channel G +level 0,31 -evaluate leftshift 6 -evaluate and 1984 +channel ^
-channel B +level 0,31 -evaluate leftshift 1 -evaluate and 62 +channel ^
-channel A -evaluate and 1 +channel ^
-channel RGBA -separate +channel ^
-channel R -evaluate-sequence add  +channel ^
-depth 16 -endian MSB R:skull_chest_base.bin

magick -size 32x64 -depth 8 spider_front.png ^
-channel R +level 0,31 -evaluate leftshift 11 -evaluate and 63488 +channel ^
-channel G +level 0,31 -evaluate leftshift 6 -evaluate and 1984 +channel ^
-channel B +level 0,31 -evaluate leftshift 1 -evaluate and 62 +channel ^
-channel A -evaluate and 1 +channel ^
-channel RGBA -separate +channel ^
-channel R -evaluate-sequence add  +channel ^
-depth 16 -endian MSB R:skull_chest_front.bin