1. Find the actor in [SceneNavi](https://github.com/xdanieldzd/SceneNavi/releases/latest)
2. Look up Actor Type as Id on <https://wiki.cloudmodding.com/oot/Actor_List_(Variables)> to find actor name
3. Find actor name with underscores removed in [decomp](https://github.com/zeldaret/oot)
4. Identify a function call to replace
5. Use [Ghidra 9.2](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_9.2_build) with [Zelda64Loader](https://github.com/Random06457/Zelda64Loader) to find the address of the function call. [1.0 disassembly](https://github.com/Roman971/oot-disassembly) is also a good reference.
6. If the function replaced is outside of the current overlay, then nothing more to do. Else for function calls within the same overlay, remove the corresponding relocation table entry. Building decomp should have provided "reloc.s" files, these show the format of the relocation table, including the name of the original functions.
