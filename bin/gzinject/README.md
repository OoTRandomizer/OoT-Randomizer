## About

gzinject is a wad editing utility, primarily used for patching N64 VC Emulators, and replacing the rom inside.  gzinject uses patch files to patch content files within the wad. A description of the patch file format can be seen in the [Patch](#Patch) section.  

## Executable 

To build your own, run ./configure, then make, and make install. See BUILDING for more instructions

Prebuilt Windows executable is contained under releases (https://github.com/krimtonz/gzinject/releases/latest)

## Usage 
```
Usage:
  gzinject -a extract -w SOURCEWAD [options]
  gzinject -a pack -w DESTWAD [options]
  gzinject -a inject -w SOURCEWAD -m ROM [options]
  gzinject -a genkey [options]
  gzinject --help
  gzinject --version

Actions:
  extract      extracts SOURCEWAD to directory
  pack         packs directory into DESTWAD
  inject       injects rom into SOURCEWAD
  genkey       generates wii common-key

Options:
  -i, --channelid=ID           New Channel ID For Pack and Inject actions (default: none)
  -t, --title=title            New Channel name for pack and inject actions (default: none)
  -h, --help                   Prints this help message
  -k, --key=keyfile            Location of the common-key file (default: common-key.bin)
  -r, --region=1-3             Region to use (default: 3)
  --verbose                    Print out verbose program execution information
  -d, --directory=directory    Directory to extract contents to, or directory to read contents from (default: wadextract)
  --cleanup                    Remove files before performing actions
  --version                    Prints the current version
  -m, --rom=rom                Rom to inject for inject action (default: none)
  -o, --outputwad=outwad       The output wad for inject actions (default: SOURCEWAD-inject.wad)
  -p, --patch-file=patchfile   gzi file to use for applying patches (default: none)
  -c, --content=contentfile    the primary content file (default: 5)
  --dol-inject                 Binary data to inject into the emulator program, requires --dol-loading
  --dol-loading                The loading address for the binary specified by --dol-inject
  --dol-after                  After which patch file to inject the dol, default: after all patches
```

## Patch
gzi files are text files with a command on each line.  A # starting the line indicates a comment.

line format:
ccss oooooooo dddddddd\
Where c indicates the command, s indicates the data size, o indicates the offset into the current file, and d indicates the data to replace with.

```
Commands:
  00: Begin using content file specified by d, offset and size are not used for this command
  01: lz77 decompress the current content file.  offset, size, and data are not used for this command
  02: lz77 compress the current content file.  offset, size, and data are not used for this command
  03: apply patch to currently selected file. If offset is higher than the file sizes, or a current file has not been selected, the patch is not applied

Sizes:
  01: a one byte value.  data & 0x000000FF is applied to content + offset
  02: a two byte value.  data & 0x0000FFFF is applied to content + offset
  04: a four byte value.  data is applied to content + offset
```


## Thanks/Authors

gzinject was primarily written by me.\n
Thanks to glankk (https://github.com/glankk) for providing memory/controller fixes for OOT as well as debugging, testing, and providing fixes for various errors\
The general workflow of extracting/packing the wad was taken from showmiiwads (https://github.com/dnasdw/showmiiwads/)\
AES encryption/decryption was taken from kokke (https://github.com/kokke/tiny-AES-c)\
SHA1 taken from clibs (https://github.com/clibs/sha1)\
MD5 taken from Alexander Peslyak http://openwall.info/wiki/people/solar/software/public-domain-source-code/md5
