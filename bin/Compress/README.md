To build:

# Windows (ARM64)

On Windows ARM64, install MSYS2 ARM64 variant (see <https://www.msys2.org/wiki/arm64/> or `scoop install msys2`).

In `clangarm64`, run:

```console
$ pacman -Suy
$ pacman -S mingw-w64-clang-aarch64-clang
$ clang -pthread bin/Compress/src/compressor.c -o bin/Compress/Compress_ARM64.exe -static
```

# Windows (x86_64)

In `mingw64`, run:

```bash
gcc bin/Compress/src/compressor.c -o bin/Compress/Compress.exe --static
```

# Windows (i686)

Can be cross-compiled from x86_64.

In `mingw32`, run:

```bash
pacman -S mingw-w64-i686-toolchain # only needs to be run once (installs the toolchain into the mingw environment)
gcc bin/Compress/src/compressor.c -o bin/Compress/Compress32.exe --static
```

# macOS (Universal)

Compile on ARM64 (Apple Silicon).

```zsh
clang -pthread bin/Compress/src/compressor.c -o bin/Compress/Compress_ARM64.out
clang -arch x86_64 -pthread bin/Compress/src/compressor.c -o bin/Compress/Compress_x86_64.out
lipo -create bin/Compress/Compress_ARM64.out bin/Compress/Compress_x86_64.out -output bin/Compress/Compress.out
rm bin/Compress/Compress_ARM64.out bin/Compress/Compress_x86_64.out
```

# Linux (ARM64)

Can be cross-compiled from any arch.

On Ubuntu:

```bash
sudo apt-get install gcc-aarch64-linux-gnu
aarch64-linux-gnu-gcc bin/Compress/src/compressor.c -o bin/Compress/Compress_ARM64
```

# Linux (ARM32)

Can be cross-compiled from any arch.

On Ubuntu:

```bash
sudo apt-get install gcc-arm-linux-gnueabihf
arm-linux-gnueabihf-gcc bin/Compress/src/compressor.c -o bin/Compress/Compress_ARM32
```

# Linux (x86_64)

On Ubuntu:

```bash
gcc bin/Compress/src/compressor.c -o bin/Compress/Compress
```
