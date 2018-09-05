- Download the armips assembler: <https://github.com/Kingcom/armips> and put the
  executable in the `scripts` directory, or somewhere in your PATH
- Put the ROM you want to patch at `roms/base.z64`
- Run `python3 scripts/build.py`, which will create `roms/patched.z64`
- To update the front-end patch file, run:
  ```python3 scripts/rom_diff.py roms/base.z64 roms/patched.z64 ../data/base2current.json```

To generate debugging symbols for the Project 64 debugger, run `python3 scripts/build.py --pj64sym 'path_to_pj64/Saves/THE LEGEND OF ZELDA.sym'`
