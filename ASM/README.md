Advanced modifications to the Randomizer source require a bit more software than what is needed for running it.

## Assembly: armips
### Windows Prerequisite
- Download and install the [Visual Studio 2015-202x Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170#visual-studio-2015-2017-2019-and-2022) package.
  - You will want the x64 Architecture version.
  - This is to run the automated build of armips. If you plan to compile it yourself you can ignore this, but that is an advanced setup not covered here.
### Running
- Download the armips assembler: <https://github.com/Kingcom/armips>
  - [Windows automated builds](https://buildbot.orphis.net/armips/)
  - On macOS or Linux with Homebrew, the OoTRandomizer tap can install it with:

        brew tap ootrandomizer/tap
        brew install --HEAD ootrandomizer/tap/armips

  - To compile armips yourself, install either `clang` or `gcc`, `cmake`, and either `ninja` or `make`, then follow the [building from source instructions](https://github.com/Kingcom/armips#22-building-from-source).
- Put the armips executable directly in `tools`, or install it somewhere already in your `PATH`.
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
- **macOS (Intel or Apple Silicon)**:
  - The simplest system-wide installation is the OoTRandomizer Homebrew tap:

        brew tap ootrandomizer/tap
        brew install --HEAD ootrandomizer/tap/n64

  - To keep the toolchain inside this checkout, build the patched n64 source with `ASM/tools` as its installation prefix. On macOS, `./install_deps` installs GNU Make as `gmake`:

        cd /path/to/n64
        ./install_deps
        ./configure --prefix="/absolute/path/to/OoT-Randomizer/ASM/tools"
        gmake toolchain-all
        gmake toolchain-install

    This installs `mips64-gcc`, `mips64-ld`, `mips64-objdump`, and `mips64-objcopy` in `ASM/tools/bin`, where `build.py` finds them automatically. Using `ASM/tools/n64` as the prefix is also supported.
  - The patched n64 build detects Homebrew under both `/opt/homebrew` and `/usr/local`, including the GMP, MPFR, MPC, zlib, Lua, libusb, GNU sed, and texinfo paths needed by native Apple Silicon builds. No permanent shell PATH change is required.
- **Any platform with a C/C++ compiler**: Build from the n64 source after applying the macOS compatibility patch, then follow the included readme. The upstream project is [glankk/n64](https://github.com/glankk/n64).
  - The dependency install script may not install all the necessary libraries depending on your OS version. Take a look at the output from the configure step to see if anything is missing.
  - It is easiest if you use `--prefix=/the/path/to/OoT-Randomizer/ASM/tools` for the `./configure` step. This installs the toolchain in a location used directly by the build script, although a system-wide prefix may be more convenient when sharing the toolchain with other projects.
  - Keep any explicitly selected `BINUTILS_VERSION`, `GCC_VERSION`, `NEWLIB_VERSION`, and `GDB_VERSION` archive stems unchanged. The patched n64 build still supports its automatic version selection and conditional newlib patches.
  - If you are trying to update the toolchain this way, it is easiest to just delete your local copy of the repository and clone it again to ensure all the packages get updated and are compatible.


`build.py` searches `ASM/tools`, `ASM/tools/bin`, and `ASM/tools/n64/bin` before the existing environment `PATH`. This supports a single executable copied into `tools`, a toolchain installed with `ASM/tools` as its prefix, a complete prefix copied to `ASM/tools/n64`, and normal system-wide installations without platform-specific build logic.
On POSIX hosts, `build.py` uses the platform-neutral `ASM/tools/toolchain` directory for compiler launchers so GCC and its assembler are selected from the same prefix. Apple Silicon uses the same layout and only adds an isolated environment for `as`, preventing MacPorts or Conda entries from replacing the assembler selected by GCC. Windows continues to use the discovered executables directly. Set `OOTR_N64_PREFIX=/absolute/path/to/n64-prefix` to select a local installation explicitly.
### Running
Before building, verify the ROM, project files, armips, make, and every required MIPS executable:

    python3 build.py --check-toolchains

The check prints every required project file separately with its expected absolute path and actual location. For each executable it prints the project-local candidate paths, whether each candidate exists, the command selected from `PATH`, its resolved target and version, and the assembler selected internally by GCC. Missing or invalid entries produce `Result: FAILED` and exit status 1.

To recompile the C modules, run `python build.py` in this directory, or run `python ASM/build.py` from the repository root (`python3` may be required on macOS and Linux). The default `mips64-` prefix matches a toolchain built from the n64 source; use `--mips-binutils-prefix` only for packages that intentionally use another target prefix.

## Debugging Symbols for Project64
To generate symbols for the Project64 debugger, use the `--pj64sym` option:

    python build.py --pj64sym 'path_to_pj64/Saves/THE LEGEND OF ZELDA.sym'

You'll need to disable `Unique Game Save Directory` in Project64 for these to work without copying them into each unique save folder. Remember that some changes in code will not be reflected in an existing save, and they need to be deleted and a new save created with this setting disabled.

--------------------------------------------------------------------------

How to use the Debug mode: 
- First put the DEBUG_MODE variable at 1 in debug.h.
- Now the N64 logo sequence at the start of the game will be skipped, the L button will allow you to levitate and you will then have access to a hidden menu with the following options:
  - Instant warps to Dungeons, Bosses or Overworld locations
  - Item inventory edits
  - Instant age switch with the current location kept
  - Bunny Hood
  - In-game clock
  - Actor and overlay list
  - Scene flags setters
The menu will appear if you press R + either L or Dpad Up.
Use Dpad-Left/Dpad-Right and A/B to navigate it.
The warps and items are easily customizable with the code at the top of debug.c.
- Additionally, you can call functions to print numbers on screen, to help you debug new features.
Call either draw_debug_int or draw_debug_float in your code, with the first argument being the number wanted to be displayed, and the 
second argument its place on the screen (up to 10 values).
