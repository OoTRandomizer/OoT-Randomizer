Advanced modifications to the Randomzier source require a bit more software than what is needed for running it.

## Assembly: armips
### Windows Prerequisite
- Download and install the [Visual Studio 2015-202x Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170#visual-studio-2015-2017-2019-and-2022) package.
  - You will want the x64 Architecture version.
  - This is to run the automated build of armips. If you plan to compile it yourself you can ignore this, but that is an advanced setup not covered here.
### Running
- Download the armips assembler: <https://github.com/Kingcom/armips>
  - [Windows automated builds](https://buildbot.orphis.net/armips/)
  - On other platforms you'll need either `clang` or `gcc`, `cmake`, and either `ninja` or `make` installed. All of these should be available in the package repositories of every major Linux distribution and Homebrew on macOS. After, follow the [building from source instructions](https://github.com/Kingcom/armips#22-building-from-source).
- Put the armips executable in the `tools` directory, or somewhere in your PATH.
- Put the ROM you want to patch at `roms/base.z64`. This needs to be an uncompressed ROM; OoTRandomizer will produce one at ZOOTDEC.z64 when you run it with a compressed ROM.
- Run `python build.py --no-compile-c`, which will:
  - create `roms/patched.z64`
  - update some `txt` files in `build/` and in `../data/generated/`. Check `git status` to see which ones have changed. Make sure you submit them all together!

## C: n64 toolchain
### Prerequisites
Recompiling the C code for randomizer requires the N64 development tools to be installed: <https://github.com/glankk/n64>. There are several ways to do this depending on your platform.
- **Windows**:
  - **Without WSL**: [Download this zip archive](https://discord.com/channels/274180765816848384/442752384834469908/1085678948614144081) and extract the `n64` folder into the `tools` directory alongside armips.
    - Download and install [MSYS2](https://www.msys2.org/#installation).
      1. Accept the defaults in the installer.
      2. After the installer completes a terminal window will open.
      3. In the terminal type `pacman -Syy make` and press Enter.
      4. Make sure it lists `make` for installation and press Enter again to confirm.
      5. After the installation finishes you can close the terminal window.
      6. In the Start search bar type "Environment Variables" and click "Edit the system environment variables".
      7. Near the bottom click on the button labeled "Environment Variables...".
      8. In the new window in the top section look for the variable called "Path" and click it.
      9. Click the "Edit..." button below the box you selected "Path" in.
      10. Click on "New" on the right side of the new window.
      11. Type `C:\msys64\usr\bin` and press Enter.
      12. Click "OK" on all three windows.
      13. You will now be able to compile the randomizer's C code from CMD, PowerShell, and MSYS2's terminal.
  - **Using WSL**: Install the latest Debian Linux from the Windows Store and follow the below instructions for Debian.
- **Debian**: [Follow this how-to](https://practicerom.com/public/packages/debian/howto.txt) on adding the toolchain's package repository and installing the pre-built binaries.
  - You will also need to run `apt install build-essential` or `apt install make` if `make` is not installed.
- **Any platform with a gcc compiler**: Build from source from the [glankk/n64](https://github.com/glankk/n64) repository. Simply follow the readme.
  - The dependency install script may not install all the necessary libraries depending on your OS version. Take a look at the output from the configure step to see if anything is missing.
  - It is easiest if you use `--prefix=/the/path/to/OoT-Randomizer/ASM/tools` for the `./configure` step. This will install all the toolchain in a way the build script can use, however this is inconvenient if you plan to use the toolchain for other projects as well.
  - If you are trying to update the toolchain this way, it is easiest to just delete your local copy of the repository and clone it again to ensure all the packages get updated and are compatible.


You can substitute using the `tools` folder with adding the `n64/bin` folder to your environment PATH if you need an advanced setup.
### Running
To recompile the C modules, use `python build.py` in this directory, or adjust the path to `build.py` relative to your terminal's working directory.

## Debugging Symbols for Project64
To generate symbols for the Project64 debugger, use the `--pj64sym` option:

    python build.py --pj64sym 'path_to_pj64/Saves/THE LEGEND OF ZELDA.sym'

You'll need to disable `Unique Game Save Directory` in Project64 for these to work without copying them into each unique save folder. Remember that some changes in code will not be reflected in an existing save, and they need to be deleted and a new save created with this setting disabled.

--------------------------------------------------------------------------

How to use the Debug mode: 
- First put the DEBUG_MODE variable at 1 in debug.h.
- Now the N64 logo sequence at the start of the game will be skipped, the L button will allow you to levitaten and you will then have access to a hidden menu with the following options:
  - Instant warps to Dungeons, Bosses or Overworld locations
  - Item inventory edits
  - Instant age switch with the current location kept
  - Bunny Hood
  - In-game clock
  - Actor and overlay list
  - Scene flags setters
The menu will appear if you press either Dpad-Up or L.
Use Dpad-Left/Dpad-Right and A/B to navigate it.
The warps and items are easily customizable with the code at the top of debug.c.
- Additionally, you can call functions to print numbers on screen, to help you debug new features.
Call either draw_debug_int or draw_debug_float in your code, with the first argument being the number wanted to be displayed, and the 
second argument its place on the screen (up to 10 values).
