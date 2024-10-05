# VSCode

A lot of people on this project use VSCode as their coding environment.

## Extensions

There are a number of useful extensions available to make work more efficient:

- C/C++ IntelliSense
- Clang-Format
- HexInspector (hover on numbers for float and other info)
- NumberMonger (convert hex to decimal and vice versa)
- Better MIPS Support

## Useful keyboard shortcuts

- Ctrl + Alt + Up/Down (on Windows, on Linux it's Ctrl + Shift + Up/Down or Shift + Alt + Up/Down) gives multicursors across consecutive lines. If you want several cursors in a more diverse arrangement, middle clicking works, at least on Windows.
- Alt + Up/Down moves lines up/down.
- Shift + Alt + Up/Down (Linux: Ctrl + Shift + Alt + Up/Down) copies lines up/down.
- Ctrl + P offers a box to use to search for and open files.
- Ctrl + Shift + P offers a box for commands like editing settings or reloading the window.

- Make use of VSCode's search/search-and-replace features.
    - Ctrl + Click goes to a definition.
    - Ctrl + F for search in current file
    - Ctrl + H for replace in current file
    - Ctrl + Shift + F for search in all files
    - Ctrl + Shift + H for replace in all files
    - F2 for Rename symbol

Many of VS Code's other shortcuts can be found on [its getting started page](https://code.visualstudio.com/docs/getstarted/keybindings), which also has links to OS-specific PDFs.

## C/C++ configuration

You can create a `.vscode/c_cpp_properties.json` file with `C/C++: Edit Configurations (JSON)` in the command box to customise how IntelliSense reads the repository (stuff like where to look for includes, flags, compiler defines, etc.) to make VSCode's IntelliSense plugin better able to understand the structure of the repository. This is a good default one to use for this project's repository:

```jsonc
{
    "configurations": [
        {
            "name": "Linux",
            "compilerPath": "/usr/bin/mips64-gcc", // If using MSYS instead of WSL or Linux, change to your MSYS mips64-gcc path
            "intelliSenseMode": "${default}", // Shouldn't matter
            "includePath": [
                "${workspaceFolder}/**",
            ],
            "defines": [
                "_DEBUG",
                "UNICODE",
                "_UNICODE"
            ],
            "cStandard": "c17", // NOTE: later version than decomp
            "cppStandard": "${default}" // No OOTR code uses C++, so doesn't really matter
        }
    ],
    "version": 4
}
```

## Unit Tests

VS Code has a panel to run and debug Python unit tests. `pytest` is recommended for running the tests. It can be installed using `pip install pytest` or through your OS's package management system. You can then enable VS Code's testing panel by creating a `.vscode/settings.json` file with the following:

```jsonc
{
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "-n",
        "auto",
        "-v",
        "Unittest.py"
    ]
}
```

The testing panel can be opened by clicking the flask icon in the left toolbar. To run all tests, DO NOT use the Run All Tests button. Click the Run Test button next to Unittest.py in the test tree. For more information on VS Code unit testing, see [the official VS Code Python testing page](https://code.visualstudio.com/docs/python/testing#_run-tests).

## Dev Containers

If the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension is installed, it should automatically detect the configuration file in `/.devcontainer/devcontainer.json`. If you allow it to activate, it will create a Debian container with python, node, glankk's N64 toolchain, and armips for compiling and running all code for the randomizer. To manually activate it:

- Bring up the command palette with F1
- Select `Dev Container: Open Folder in Container...`
- Select the root of the randomizer repository and wait for the container to build.

Before using any of the build scripts, ensure an uncompressed v1.0 NTSC US ROM is placed at `ASM/roms/base.z64` relative to the repository's root. The randomizer will create this file for you when generating a patched ROM or wad.

Debugging and building options described below will work with no additional changes while inside the container. Alternatively, any new terminal prompt in VSCode will allow you to run commands inside the container. Randomizer source code is mounted to `/app/OoT-Randomizer`.

Running the GUI from the container is not currently supported. It is technically possible by either running an X server in the container or sharing the host's X server, but this approach is not cross-platform-friendly. The GUI can still be run from the host outside of VSCode. It will share code changes with the container through the container's mounted folders.

## Building the ASM/C code

Instead of manually running the build script in a terminal, you can add a build task to VS Code by creating a `.vscode/tasks.json` file with the following content:

```jsonc
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Compile C/ASM patch",
            "type": "shell",
            "command": "python3",
            "args": [
                "${workspaceFolder}/ASM/build.py",
                "--compile-c"
            ],
            "group": {
                "kind": "build",
                "isDefault": true
            }
        }
    ]
}
```

Additional build script arguments such as Project64 symbols export can be added as additional entries in the `args` list. You can then compile by pressing `Ctrl+Shift+B` or selecting "Run Build Task..." from the Terminal menu.

## Debugging the Python code

Adding a launch profile allows you to quickly run the randomizer without the GUI and enable additional debug information in the console. Enter the following in `.vscode/launch.json`:

```jsonc
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "OOTR Debug Profile (Integrated Terminal)",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/OoTRandomizer.py",
            "args": ["--loglevel", "debug"],
            "console": "integratedTerminal"
        }
    ]
}
```

Debugging can be started by pressing F5.
