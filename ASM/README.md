- Download the armips assembler: <https://github.com/Kingcom/armips> and put
  the executable in the `scripts` directory, or somewhere in your PATH
- Put the ROM you want to patch at `roms/base.z64`
- Run `python scripts/build.py`, which will:
  - create `roms/patched.z64`
  - update `../data/rom_patch.txt` and `../data/symbols.json`

To generate debugging symbols for the Project 64 debugger, use the `--pj64sym`
option:
`python scripts/build.py --pj64sym 'path_to_pj64/Saves/THE LEGEND OF ZELDA.sym'`.

To recompile the C modules, use the `--compile-c` option. This requires the
N64 development tools to be installed: <https://github.com/glankk/n64>
