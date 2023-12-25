from __future__ import annotations
import os
import random
from enum import IntEnum
from typing import TYPE_CHECKING

from Utils import data_path

if TYPE_CHECKING:
    from Cosmetics import CosmeticsLog
    from Rom import Rom
    from Settings import Settings


def get_model_choices(age: int) -> list[str]:
    names = ["Default"]
    path = data_path("Models/Adult")
    if age == 1:
        path = data_path("Models/Child")
    if os.path.exists(path):
        for file in os.listdir(path):
            if file.endswith(".zobj"):
                names.append(file[:-5])
    if len(names) > 2:
        # If more than 2 non-default model choices, add random option
        names.insert(1, "Random")
    return names


class ModelError(RuntimeError):
    pass


class ModelDefinitionError(ModelError):
    pass


# Used for writer model pointers to the rom in place of the vanilla pointers
class ModelPointerWriter:
    def __init__(self, rom: Rom) -> None:
        self.rom: Rom = rom
        self.offset: int = 0
        self.advance: int = 4
        self.base: int = CODE_START

    def SetBase(self, base: str) -> None:
        if base == 'Code':
            self.base = CODE_START
        elif base == 'Player':
            self.base = PLAYER_START
        elif base == 'Hook':
            self.base = HOOK_START
        elif base == 'Shield':
            self.base = SHIELD_START
        elif base == 'Stick':
            self.base = STICK_START
        elif base == 'GraveyardKid':
            self.base = GRAVEYARD_KID_START
        elif base == 'Guard':
            self.base = GUARD_START
        elif base == 'RunningMan':
            self.base = RUNNING_MAN_START

    def GoTo(self, dest: int) -> None:
        self.offset = dest

    def SetAdvance(self, adv: int) -> None:
        self.advance = adv

    def GetAddress(self) -> int:
        return self.base + self.offset

    def WriteModelData(self, data: int) -> None:
        self.rom.write_bytes(self.GetAddress(), data.to_bytes(4, 'big'))
        self.offset += self.advance

    def WriteModelData16(self, data: int) -> None:
        self.rom.write_bytes(self.GetAddress(), data.to_bytes(2, 'big'))
        self.offset += 2

    def WriteModelDataHi(self, data: int) -> None:
        bytes = data.to_bytes(4, 'big')
        for i in range(2):
            self.rom.write_byte(self.GetAddress(), bytes[i])
            self.offset += 1

    def WriteModelDataLo(self, data: int) -> None:
        bytes = data.to_bytes(4, 'big')
        for i in range(2, 4):
            self.rom.write_byte(self.GetAddress(), bytes[i])
            self.offset += 1


# Either return the starting index of the requested data (when start == 0)
# or the offset of the element in the footer, if it exists (start > 0)
def scan(bytes: bytearray, data: bytearray | str, start: int = 0) -> int:
    databytes = data
    # If a string was passed, encode string as bytes
    if isinstance(data, str):
        databytes = data.encode()
    dataindex = 0
    for i in range(start, len(bytes)):
        # Byte matches next byte in string
        if bytes[i] == databytes[dataindex]:
            dataindex += 1
            # Special case: Bottle, Bow, Slingshot, Fist.L, and Fist.R are subsets of
            # Bottle.Hand.L, Bow.String, Slingshot.String, Gauntlet.Fist.L, and Gauntlet.Fist.R respectively
            # And Hookshot which is a subset of Hookshot.Spike, Hookshot.Chain, Hookshot.Aiming.Reticule
            # This leads to false positives. So if the next byte is . (0x2E) then reset the count.
            if isinstance(data, str) and data in ["Bottle", "Bow", "Slingshot", "Hookshot", "Fist.L", "Fist.R", "Blade.3"] and i < len(bytes) - 1 and bytes[i+1] == 0x2E:
                # Blade.3 is even wackier, as it is a subset of Blade.3.Break,
                # and also a forward subset of Broken.Blade.3, and has a period in it
                if data == "Blade.3":
                    resetCount = False
                    # If current byte is the "e" in "Blade.3", the period detected is the expected one- Carry on
                    # If it isn't, then reset the count
                    if bytes[i] != 0x65:
                        resetCount = True
                    # Make sure i is large enough, "Broken.Blad" is 11 chars (remember we're currently at the e)
                    if not resetCount and i > 10:
                        # Check if "Broken." immediately preceeds this string
                        preceedingBytes = bytes[i-11:i-4]
                        if preceedingBytes == bytearray(b'Broken.'):
                            resetCount = True
                    if resetCount:
                        dataindex = 0
                # Fist.L and Fist.R are forward subsets of Gauntlet.Fist.x, check for "Gauntlet."
                # "Gauntlet.Fis" is 12 chars (we are currently at the t)
                elif data in ["Fist.L", "Fist.R"] and i > 11:
                    # Check if "Gauntlet." immediately preceeds this string
                    preceedingBytes = bytes[i-12:i-3]
                    if preceedingBytes == bytearray(b'Gauntlet.'):
                        dataindex = 0
                # Default case for Bottle, Bow, Slingshot, Hookshot, reset count
                else:
                    dataindex = 0
            # Special case for Hookshot: Forward subset of FPS.Hookshot, "FPS." is 4 chars
            # (Blade.3 and fists can check in the previous stanza since a . will be encountered at some point)
            if isinstance(data, str) and data == "Hookshot" and dataindex == 1 and i > 3:
                # Check if "FPS." immediately preceeds this string
                preceedingBytes = bytes[i-4:i]
                if preceedingBytes == bytearray(b'FPS.'):
                    dataindex = 0
            # More special cases added by the new pipeline...
            # Hand.L and Hand.R are forward subsets of Gauntlet.Hand.X, FPS.Hand.X
            # And Hand.L specifically is a forward subset of Bottle.Hand.L
            if isinstance(data, str) and data in ["Hand.L", "Hand.R"] and dataindex == 1:
                if i > 8:
                    preceedingBytes = bytes[i-9:i]
                    if preceedingBytes == bytearray(b'Gauntlet.'):
                        dataindex = 0
                if dataindex == 1 and i > 3:
                    preceedingBytes = bytes[i-4:i]
                    if preceedingBytes == bytearray(b'FPS.'):
                        dataindex = 0
                if data == "Hand.L" and dataindex == 1 and i > 6:
                    preceedingBytes = bytes[i-7:i]
                    if preceedingBytes == bytearray(b'Bottle.'):
                        dataindex = 0
            # Forearm.L and Forearm.R are forward subsets of FPS.Forearm.X
            if isinstance(data, str) and data in ["Forearm.L", "Forearm.R"] and dataindex == 1 and i > 3:
                preceedingBytes = bytes[i-4:i]
                if preceedingBytes == bytearray(b'FPS.'):
                    dataindex = 0
            # All bytes have been found, so a match
            if dataindex == len(databytes):
                # If start is 0 then looking for the footer, return the index
                if start == 0:
                    return i + 1
                # Else, we want to know the offset, which will be after the footer and 1 padding byte
                else:
                    i += 2
                    offsetbytes = []
                    for j in range(4):
                        offsetbytes.append(bytes[i + j])
                    return int.from_bytes(offsetbytes, 'big')
        # Match has been broken, reset to start of string
        else:
            dataindex = 0
    return -1


# Follows pointers from the LUT until finding the actual DList, and returns the offset of the DList
def unwrap(zobj: bytearray, address: int) -> int:
    # An entry in the LUT will look something like 0xDE 01 0000 06014050
    # Only the last 3 bytes should be necessary.
    data = int.from_bytes(zobj[address+5:address+8], 'big')
    # If the data here points to another entry in the LUT, keep searching until
    # an address outside the table is found.
    while LUT_START <= data <= LUT_END:
        address = data
        data = int.from_bytes(zobj[address+5:address+8], 'big')
    return address


# Used to overwrite pointers in the displaylist with new ones
def WriteDLPointer(dl: list[int], index: int, data: int) -> None:
    bytes = data.to_bytes(4, 'big')
    for i in range(4):
        dl[index + i] = bytes[i]


# An extensive function which loads pieces from the vanilla Link model to add to the user-provided zobj
# Based on https://github.com/hylian-modding/ML64-Z64Lib/blob/master/cores/Z64Lib/API/zzoptimize.ts function optimize()
def LoadVanilla(rom: Rom, missing: list[str], rebase: int, linkstart: int, linksize: int,
                pieces: dict[str, tuple[Offsets, int]], skips: dict[str, list[tuple[int, int]]]) -> tuple[list[int], dict[str, int]]:
    # Get vanilla "zobj" of Link's model
    vanillaData = []
    for i in range(linksize):
        vanillaData.append(rom.buffer[linkstart + i])
    segment = 0x06
    vertices = {}
    matrices = {}
    textures = {}
    displayLists = {}
    # For each missing piece, grab data from its vanilla display list
    for item in missing:
        offset = pieces[item][1]
        i = offset
        displayList = []
        # Crawl displaylist bytecode and handle each command
        while i < len(vanillaData):
            # Check if these bytes need to be skipped
            if item in skips.keys():
                skip = False
                for skippedRanges in skips[item]:
                    itemIndex = i - offset
                    # Byte is in a range that must be skipped
                    if skippedRanges[0] <= itemIndex and itemIndex < skippedRanges[1]:
                        skip = True
                if skip:
                    i += 8
                    continue
            op = vanillaData[i]
            seg = vanillaData[i+4]
            lo = int.from_bytes(vanillaData[i+4:i+8], 'big')
            # Source for displaylist bytecode: https://hack64.net/wiki/doku.php?id=f3dex2
            if op == 0xDF: # End of list
                # DF: G_ENDDL
                # Terminates the current displaylist
                # DF 00 00 00 00 00 00 00
                displayList.extend(vanillaData[i:i+8]) # Make sure to write the DF
                break
            # Shouldn't have to deal with DE (branch to new display list)
            elif op == 0x01 and seg == segment: # Vertex data
                # 01: G_VTX
                # Fills the vertex buffer with vertex information
                # 01 0[N N]0 [II] [SS SS SS SS]
                # N: Number of vertices
                # I: Where to start writing vertices inside the vertex buffer (start = II - N*2)
                # S: Segmented address to load vertices from
                # Grab the address from the low byte without teh base offset
                vtxStart = lo & 0x00FFFFFF
                # Grab the length of vertices from the instruction
                # (Number of vertices will be from the 4th and 5th nibble as shown above, but each length 16)
                vtxLen = int.from_bytes(vanillaData[i+1:i+3], 'big')
                if vtxStart not in vertices or len(vertices[vtxStart]) < vtxLen:
                    vertices[vtxStart] = vanillaData[vtxStart:vtxStart+vtxLen]
            elif op == 0xDA and seg == segment: # Push matrix
                # DA: G_MTX
                # Apply transformation matrix
                # DA 38 00 [PP] [AA AA AA AA]
                # P: Parameters for matrix
                # A: Segmented address of vectors of matrix
                # Grab the address from the low byte without the base offset
                mtxStart = lo & 0x00FFFFFF
                if mtxStart not in matrices:
                    matrices[mtxStart] = vanillaData[mtxStart:mtxStart+0x40] # Matrices always 0x40 long
            elif op == 0xFD and seg == segment: # Texture
                # G_SETTIMG
                # Sets the texture image offset
                # FD [fi] 00 00 [bb bb bb bb]
                # [fi] -> fffi i000
                # f: Texture format
                # i: Texture bitsize
                # b: Segmented address of texture
                # Use 3rd nibble to get the texture type
                textureType = (vanillaData[i+1] >> 3) & 0x1F
                # Find the number of texel bits from the type
                numTexelBits = 4 * (2 ** (textureType & 0x3))
                # Get how many bytes there are per texel
                bytesPerTexel = int(numTexelBits / 8)
                # Grab the address from the low byte without the base offset
                texOffset = lo & 0x00FFFFFF
                numTexels = -1
                returnStack = []
                j = i+8
                # The point of this loop is just to find the number of texels
                # so that it may be multiplied by the bytesPerTexel so we know
                # the length of the texture.
                while j < len(vanillaData) and numTexels == -1:
                    opJ = vanillaData[j]
                    segJ = vanillaData[j+4]
                    loJ = int.from_bytes(vanillaData[j+4:j+8], 'big')
                    if opJ == 0xDF:
                        # End of branched texture, or something wrong
                        if len(returnStack) == 0:
                            numTexels = 0
                            break
                        else:
                            j = returnStack.pop()
                    elif opJ == 0xFD:
                        # Another texture command encountered, something wrong
                        numTexels = 0
                        break
                    elif opJ == 0xDE:
                        # Branch to another texture
                        if segJ == segment:
                            if vanillaData[j+1] == 0x0:
                                returnStack.append(j)
                            j = loJ & 0x00FFFFFF
                    elif opJ == 0xF0:
                        # F0: G_LOADTLUT
                        # Loads a number of colors for a pallette
                        # F0 00 00 00 0[t] [cc c]0 00
                        # t: Tile descriptor to load from
                        # c: ((colour count-1) & 0x3FF) << 2
                        # Just grab c from the instruction above
                        # Shift right 12 to get past the first 3 0s, then
                        # 2 more since c is shifted left twice, then add 1
                        # to get the color count of this pallette.
                        numTexels = ((loJ & 0x00FFF000) >> 14) + 1
                        break
                        # Also error if numTexels > 256
                    elif opJ == 0xF3:
                        # F3: G_LOADBLOCK
                        # Determines how much data to load after SETTIMG
                        # F3 [SS S][T TT] 0[I] [XX X][D DD]
                        # S: Upper left corner of texture's S-axis
                        # T: Upper left corner of texture's T-axis
                        # I: Tile descriptor
                        # X: Number of texels to load, minus one
                        # D: dxt (?)
                        # Just grab X from the instruction, shift
                        # right 12 times to get past 0s
                        numTexels = ((loJ & 0x00FFF000) >> 12) + 1
                        break
                    j += 8
                dataLen = bytesPerTexel * numTexels
                if texOffset not in textures or len(textures[texOffset]) < dataLen:
                    textures[texOffset] = vanillaData[texOffset:texOffset+dataLen]
            displayList.extend(vanillaData[i:i+8])
            i += 8
        displayLists[item] = (displayList, offset)
    # Create vanilla zobj of the pieces from data collected during crawl
    vanillaZobj = []
    # Add textures, vertices, and matrices to the beginning of the zobj
    # Textures
    oldTex2New = {}
    for (offset, texture) in textures.items():
        newOffset = len(vanillaZobj)
        oldTex2New[offset] = newOffset
        vanillaZobj.extend(texture)
    # Vertices
    oldVer2New = {}
    for (offset, vertex) in vertices.items():
        newOffset = len(vanillaZobj)
        oldVer2New[offset] = newOffset
        vanillaZobj.extend(vertex)
    # Matrices
    oldMtx2New = {}
    for (offset, matrix) in matrices.items():
        newOffset = len(vanillaZobj)
        oldMtx2New[offset] = newOffset
        vanillaZobj.extend(matrix)
    # Now add display lists which will reference the data from the beginning of the zobj
    # Display lists
    oldDL2New = {}
    for data in displayLists.values():
        dl = data[0]
        offset = data[1]
        oldDL2New[offset] = len(vanillaZobj)
        for i in range (0, len(dl), 8):
            op = dl[i]
            seg = dl[i+4]
            lo = int.from_bytes(dl[i+4:i+8], 'big')
            if seg == segment:
                # If this instruction points to some data, it must be repointed
                if op == 0x01:
                    vertEntry = oldVer2New[lo & 0x00FFFFFF]
                    WriteDLPointer(dl, i + 4, BASE_OFFSET + vertEntry + rebase)
                elif op == 0xDA:
                    mtxEntry = oldMtx2New[lo & 0x00FFFFFF]
                    WriteDLPointer(dl, i + 4, BASE_OFFSET + mtxEntry + rebase)
                elif op == 0xFD:
                    texEntry = oldTex2New[lo & 0x00FFFFFF]
                    WriteDLPointer(dl, i + 4, BASE_OFFSET + texEntry + rebase)
                elif op == 0xDE:
                    dlEntry = oldDL2New[lo & 0x00FFFFFF]
                    WriteDLPointer(dl, i + 4, BASE_OFFSET + dlEntry + rebase)
        vanillaZobj.extend(dl)
        # Pad to the nearest multiple of 16
        while len(vanillaZobj) % 0x10 != 0:
            vanillaZobj.append(0x00)
    # Now find the relation of items to new offsets
    DLOffsets = {}
    for item in missing:
        DLOffsets[item] = oldDL2New[pieces[item][1]]
    return vanillaZobj, DLOffsets


# Finds the address of the model's hierarchy so we can write the hierarchy pointer
# Based on https://github.com/hylian-modding/Z64Online/blob/master/src/Z64Online/common/cosmetics/UniversalAliasTable.ts function findHierarchy()
def FindHierarchy(zobj: bytearray, agestr: str) -> int:
    # Scan until we find a segmented pointer which is 0x0C or 0x10 more than
    # the preceeding data and loop until something that's not a segmented pointer is found
    # then return the position of the last segemented pointer.
    for i in range(0, len(zobj), 4):
        if zobj[i] == 0x06:
            possible = int.from_bytes(zobj[i+1:i+4], 'big')
            if possible < len(zobj):
                possible2 = int.from_bytes(zobj[i-3:i], 'big')
                diff = possible - possible2
                if diff == 0x0C or diff == 0x10:
                    pos = i + 4
                    count = 1
                    while zobj[pos] == 0x06:
                        pos += 4
                        count += 1
                    a = zobj[pos]
                    if a != count:
                        continue
                    return pos - 4
    raise ModelDefinitionError("No hierarchy found in " + agestr + " model- Did you check \"Link hierarchy format\" in zzconvert?")


TOLERANCE: int = 0x100


def CheckDiff(limb: int, skeleton: int) -> bool:
    # The normal difference
    normalDiff = abs(limb - skeleton)
    # Underflow/overflow diff
    # For example, if limb is 0xFFFF and skeleton is 0x0001, then they are technically only 2 apart
    # So subtract 0xFFFF from the absolute value of the difference to get the true difference in this case
    # Necessary since values are signed, but not represented as signed here
    flowDiff = abs(normalDiff - 0xFFFF)
    # Take the minimum of the two differences
    diff = min(normalDiff, flowDiff)
    # Return true if diff is too big
    return diff > TOLERANCE


def CorrectSkeleton(zobj: bytearray, skeleton: list[list[int]], agestr: str) -> bool:
    # Get the hierarchy pointer
    hierarchy = FindHierarchy(zobj, agestr)
    # Get what the hierarchy pointer points to (pointer to limb 0)
    limbPointer = int.from_bytes(zobj[hierarchy+1:hierarchy+4], 'big')
    # Get the limb this points to
    limb = int.from_bytes(zobj[limbPointer+1:limbPointer+4], 'big')
    # Go through each limb in the table
    hasVanillaSkeleton = True
    withinTolerance = True
    for i in range(1, 21):
        offset = limb + i * 0x10
        # X, Y, Z components are 2 bytes each
        limbX = int.from_bytes(zobj[offset:offset+2], 'big')
        limbY = int.from_bytes(zobj[offset+2:offset+4], 'big')
        limbZ = int.from_bytes(zobj[offset+4:offset+6], 'big')
        skeletonX = skeleton[i][0]
        skeletonY = skeleton[i][1]
        skeletonZ = skeleton[i][2]
        # Check if the X, Y, and Z components all match
        if limbX != skeletonX or limbY != skeletonY or limbZ != skeletonZ:
            hasVanillaSkeleton = False
            # Now check if the components are within a tolerance
            # Exclude limb 0 since that one is always zeroed out on models for some reason
            if CheckDiff(limbX, skeletonX) or CheckDiff(limbY, skeletonY) or CheckDiff(limbZ, skeletonZ):
                withinTolerance = False
                break
    # If the skeleton is not vanilla but all components are within the tolerance, then force to vanilla
    if not hasVanillaSkeleton and withinTolerance:
        hasVanillaSkeleton = True
        for i in range(21):
            offset = limb + i * 0x10
            bytes = []
            bytes.extend(int.to_bytes(skeleton[i][0], 2, 'big'))
            bytes.extend(int.to_bytes(skeleton[i][1], 2, 'big'))
            bytes.extend(int.to_bytes(skeleton[i][2], 2, 'big'))
            # Overwrite the X, Y, Z bytes with their vanilla values
            for j in range(6):
                zobj[offset+j] = bytes[j]
    return hasVanillaSkeleton


# Loads model from file and processes it by adding vanilla pieces and setting up the LUT if necessary.
def LoadModel(rom: Rom, model: str, age: int) -> int:
    # age 0 = adult, 1 = child
    linkstart = ADULT_START
    linksize = ADULT_SIZE
    hierarchy = ADULT_HIERARCHY
    postconstantstart = ADULT_POST_START
    pieces = AdultPieces
    path = data_path('Models/Adult')
    skips = adultSkips
    skeleton = adultSkeleton
    agestr = "adult" # Just used for error messages
    if age == 1:
        linkstart = CHILD_START
        linksize = CHILD_SIZE
        hierarchy = CHILD_HIERARCHY
        postconstantstart = CHILD_POST_START
        pieces = ChildPieces
        path = data_path('Models/Child')
        skips = childSkips
        skeleton = childSkeleton
        agestr = "child"
    # Read model data from file
    file = open(model, "rb")
    zobj = file.read()
    file.close()
    zobj = bytearray(zobj)
    if len(zobj) > linksize:
        raise ModelDefinitionError("Model for " + agestr + " too large- It is " + str(len(zobj)) + " bytes, but must be at most " + str(linksize) + " bytes.")
    # See if the string MODLOADER64 appears before the LUT- if so this is a PlayAs model and needs no further processing
    if scan(zobj, "MODLOADER64") == -1:
        # First, make sure all important bytes are zeroed out
        for i in range(LUT_START, LUT_END):
            zobj[i] = 0x00
        # Locate the manifest
        footerstart = scan(zobj, "!PlayAsManifest0")
        if footerstart == -1:
            raise ModelDefinitionError("No manifest found in " + agestr + " model- Did you check \"Embed play-as data\" in zzconvert?")
        startaddr = footerstart - len("!PlayAsManifest0")
        # Check if this is a new pipeline model
        if scan(zobj, "riggedmesh", startaddr) != -1:
            # Replace Limb x names with the new pipeline names
            for oldName, newName in oldToNewPipeline.items():
                pieces[newName] = pieces.pop(oldName)
        # Find which pieces, if any, are missing from this model
        missing = []
        present = {}
        DLOffsets = {}
        for piece in pieces:
            offset = scan(zobj, piece, footerstart)
            if offset == -1:
                missing.append(piece)
            else:
                present[piece] = offset
        if len(missing) > 0:
            # Load vanilla model data for missing pieces
            (vanillaZobj, DLOffsets) = LoadVanilla(rom, missing, startaddr, linkstart, linksize, pieces, skips)
            # Write vanilla zobj data to end of model zobj
            i = 0
            for byte in vanillaZobj:
                zobj.insert(startaddr + i, byte)
                i += 1
            if len(zobj) > linksize:
                raise ModelDefinitionError("After processing, model for " + agestr + " too large- It is "
                + str(len(zobj)) + " bytes, but must be at most " + str(linksize) + " bytes.")
        # Now we have to set the lookup table for each item
        for (piece, offset) in DLOffsets.items():
            # Add the starting address to each offset so they're accurate to the updated zobj
            DLOffsets[piece] = offset + startaddr
        DLOffsets.update(present)
        for item in pieces:
            lut = pieces[item][0] - BASE_OFFSET
            entry = unwrap(zobj, lut)
            zobj[entry] = 0xDE
            zobj[entry+1] = 0x01
            entry += 4
            dladdress = DLOffsets[item] + BASE_OFFSET
            dladdressbytes = dladdress.to_bytes(4, 'big')
            for byte in dladdressbytes:
                zobj[entry] = byte
                entry += 1
        # Put prefix for easily finding LUT in RAM
        i = 0
        for byte in "HEYLOOKHERE".encode():
            zobj[LUT_START+i] = byte
            i += 1
        # Set constants in the LUT
        file = open(os.path.join(path, 'Constants/preconstants.zobj'), "rb")
        constants = file.read()
        file.close()
        i = 0
        for byte in constants:
            zobj[PRE_CONSTANT_START + i] = byte
            i += 1
        file = open(os.path.join(path, 'Constants/postconstants.zobj'), "rb")
        constants = file.read()
        file.close()
        i = 0
        for byte in constants:
            zobj[postconstantstart + i] = byte
            i += 1
        # Set up hierarchy pointer
        hierarchyOffset = FindHierarchy(zobj, agestr)
        hierarchyBytes = zobj[hierarchyOffset:hierarchyOffset+4] # Get the data the offset points to
        for i in range(4):
            zobj[hierarchy - BASE_OFFSET + i] = hierarchyBytes[i]
        zobj[hierarchy - BASE_OFFSET + 4] = 0x15 # Number of limbs
        zobj[hierarchy - BASE_OFFSET + 8] = 0x12 # Number of limbs to draw
        # Save zobj for testing
        #with open(path + "/Test_Processed.zobj", "wb") as f:
        #    f.write(zobj)
    # Correct skeleton if it should be corrected
    CorrectSkeleton(zobj, skeleton, agestr)
    # Write zobj to vanilla object (object_link_boy or object_link_child)
    rom.write_bytes(linkstart, zobj)
    # Finally, want to return an address with a DF instruction for use when writing the model data
    dfBytes = bytearray(b'\xDF\x00\x00\x00\x00\x00\x00\x00')
    return scan(zobj, dfBytes) - 8


# Write in the adult model and repoint references to it
def patch_model_adult(rom: Rom, settings: Settings, log: CosmeticsLog) -> None:
    # Get model filepath
    model = settings.model_adult_filepicker
    # Default to filepicker if non-empty
    if len(model) == 0:
        model = settings.model_adult
        if settings.model_adult == "Random":
            choices = get_model_choices(0)
            choices.remove("Default")
            choices.remove("Random")
            model = random.choice(choices)
        model = data_path(f'Models/Adult/{model}.zobj')
    pathsplit = os.path.basename(model)
    log.settings.model_adult = pathsplit.split('.')[0]

    # Load and process model
    dfAddress = LoadModel(rom, model, 0)
    dfAddress = dfAddress | 0x06000000  # Add segment to DF address

    # Write adult Link pointer data
    writer = ModelPointerWriter(rom)
    writer.GoTo(0xE6718)
    writer.SetAdvance(8)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST)
    writer.WriteModelData(dfAddress)
    writer.WriteModelData(dfAddress)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST_SHIELD_HYLIAN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST_SHIELD_HYLIAN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST_SHIELD_MIRROR)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST_SHIELD_MIRROR)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SWORD_SHEATHED)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SWORD_SHEATHED)
    writer.WriteModelData(dfAddress)
    writer.WriteModelData(dfAddress)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SWORD_SHIELD_HYLIAN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SWORD_SHIELD_HYLIAN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SWORD_SHIELD_MIRROR)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SWORD_SHIELD_MIRROR)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SWORD_SHEATH)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SWORD_SHEATH)
    writer.WriteModelData(dfAddress)
    writer.WriteModelData(dfAddress)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SHEATH0_HYLIAN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SHEATH0_HYLIAN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SHEATH0_MIRROR)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SHEATH0_MIRROR)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LFIST_LONGSWORD)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LFIST_LONGSWORD)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LFIST_LONGSWORD_BROKEN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LFIST_LONGSWORD_BROKEN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LHAND)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LHAND)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LFIST)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LFIST)
    writer.WriteModelData(dfAddress)
    writer.WriteModelData(dfAddress)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LFIST_SWORD)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LFIST_SWORD)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RHAND)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RHAND)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST_BOW)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST_BOW)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SWORD_SHEATHED)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SWORD_SHEATHED)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SWORD_SHEATH)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SWORD_SHEATH)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_WAIST)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_WAIST)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST_BOW)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST_BOW)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RHAND_OCARINA_TIME)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RHAND_OCARINA_TIME)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RHAND_OCARINA_TIME)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RHAND_OCARINA_TIME)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST_HOOKSHOT)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST_HOOKSHOT)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LFIST_HAMMER)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LFIST_HAMMER)
    writer.WriteModelData(dfAddress)
    writer.WriteModelData(dfAddress)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LHAND_BOTTLE)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LHAND_BOTTLE)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_FPS_LFOREARM)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_FPS_LHAND)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RSHOULDER)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_FPS_RFOREARM)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_FPS_RHAND_BOW)

    writer.GoTo(0xE6A4C)
    writer.SetAdvance(4)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_BOOT_LIRON)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_BOOT_RIRON)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_BOOT_LHOVER)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_BOOT_RHOVER)

    writer.GoTo(0xE6B28)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_BOTTLE)

    writer.GoTo(0xE6B64)
    writer.SetAdvance(4)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_BOW_STRING)
    writer.WriteModelData(0x00000000)  # string anchor x: 0.0
    writer.WriteModelData(0xC3B43333)  # string anchor y: -360.4

    writer.GoTo(0x69112)
    writer.WriteModelDataHi(Offsets.ADULT_LINK_LUT_DL_UPGRADE_LFOREARM)
    writer.GoTo(0x69116)
    writer.WriteModelDataLo(Offsets.ADULT_LINK_LUT_DL_UPGRADE_LFOREARM)
    writer.GoTo(0x6912E)
    writer.WriteModelDataHi(Offsets.ADULT_LINK_LUT_DL_UPGRADE_RFOREARM)
    writer.GoTo(0x69132)
    writer.WriteModelDataLo(Offsets.ADULT_LINK_LUT_DL_UPGRADE_RFOREARM)
    writer.GoTo(0x6914E)
    writer.WriteModelDataHi(Offsets.ADULT_LINK_LUT_DL_UPGRADE_LFIST)
    writer.GoTo(0x69162)
    writer.WriteModelDataLo(Offsets.ADULT_LINK_LUT_DL_UPGRADE_LFIST)
    writer.GoTo(0x69166)
    writer.WriteModelDataHi(Offsets.ADULT_LINK_LUT_DL_UPGRADE_LHAND)
    writer.GoTo(0x69172)
    writer.WriteModelDataLo(Offsets.ADULT_LINK_LUT_DL_UPGRADE_LHAND)
    writer.GoTo(0x6919E)
    writer.WriteModelDataHi(Offsets.ADULT_LINK_LUT_DL_UPGRADE_RFIST)
    writer.GoTo(0x691A2)
    writer.WriteModelDataLo(Offsets.ADULT_LINK_LUT_DL_UPGRADE_RFIST)
    writer.GoTo(0x691AE)
    writer.WriteModelDataHi(Offsets.ADULT_LINK_LUT_DL_UPGRADE_RHAND)
    writer.GoTo(0x691B2)
    writer.WriteModelDataLo(Offsets.ADULT_LINK_LUT_DL_UPGRADE_RHAND)
    writer.GoTo(0x69DEA)
    writer.WriteModelDataHi(Offsets.ADULT_LINK_LUT_DL_FPS_LHAND_HOOKSHOT)
    writer.GoTo(0x69DEE)
    writer.WriteModelDataLo(Offsets.ADULT_LINK_LUT_DL_FPS_LHAND_HOOKSHOT)
    writer.GoTo(0x6A666)
    writer.WriteModelDataHi(Offsets.ADULT_LINK_LUT_DL_HOOKSHOT_AIM)
    writer.GoTo(0x6A66A)
    writer.WriteModelDataLo(Offsets.ADULT_LINK_LUT_DL_HOOKSHOT_AIM)

    writer.SetBase('Hook')
    writer.GoTo(0xA72)
    writer.WriteModelDataHi(Offsets.ADULT_LINK_LUT_DL_HOOKSHOT_HOOK)
    writer.GoTo(0xA76)
    writer.WriteModelDataLo(Offsets.ADULT_LINK_LUT_DL_HOOKSHOT_HOOK)
    writer.GoTo(0xB66)
    writer.WriteModelDataHi(Offsets.ADULT_LINK_LUT_DL_HOOKSHOT_CHAIN)
    writer.GoTo(0xB6A)
    writer.WriteModelDataLo(Offsets.ADULT_LINK_LUT_DL_HOOKSHOT_CHAIN)
    writer.GoTo(0xBA8)
    writer.WriteModelData16(0x0014)

    writer.SetBase('Stick')
    writer.GoTo(0x32C)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_BLADEBREAK)
    writer.GoTo(0x328)
    writer.WriteModelData16(0x0014)

    writer.SetBase('Code')
    writer.GoTo(0xE65A0)
    writer.WriteModelData(ADULT_HIERARCHY)  # Hierarchy pointer


# Write in the child model and repoint references to it
def patch_model_child(rom: Rom, settings: Settings, log: CosmeticsLog) -> None:
    # Get model filepath
    model = settings.model_child_filepicker
    # Default to filepicker if non-empty
    if len(model) == 0:
        model = settings.model_child
        if settings.model_child == "Random":
            choices = get_model_choices(1)
            choices.remove("Default")
            choices.remove("Random")
            model = random.choice(choices)
        model = data_path(f'Models/Child/{model}.zobj')
    pathsplit = os.path.basename(model)
    log.settings.model_child = pathsplit.split('.')[0]

    # Load and process model
    dfAddress = LoadModel(rom, model, 1)
    dfAddress = dfAddress | 0x06000000  # Add segment to DF address

    # Write child Link pointer data
    writer = ModelPointerWriter(rom)
    writer.GoTo(0xE671C)
    writer.SetAdvance(8)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST_SHIELD_DEKU)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST_SHIELD_DEKU)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST)
    writer.WriteModelData(dfAddress)
    writer.WriteModelData(dfAddress)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SWORD_SHEATHED)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SWORD_SHEATHED)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SWORD_SHIELD_DEKU)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SWORD_SHIELD_DEKU)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SWORD_SHIELD_HYLIAN)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SWORD_SHIELD_HYLIAN)
    writer.WriteModelData(dfAddress)
    writer.WriteModelData(dfAddress)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SHIELD_DEKU_BACK)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SHIELD_DEKU_BACK)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SWORD_SHEATH)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SWORD_SHEATH)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SHEATH0_DEKU)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SHEATH0_DEKU)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SHEATH0_HYLIAN)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SHEATH0_HYLIAN)
    writer.WriteModelData(dfAddress)
    writer.WriteModelData(dfAddress)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SHIELD_DEKU_BACK)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SHIELD_DEKU_BACK)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LHAND_PEDESTALSWORD)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LHAND_PEDESTALSWORD)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LHAND_PEDESTALSWORD)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LHAND_PEDESTALSWORD)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LHAND)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LHAND)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LFIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LFIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LFIST_SWORD)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LFIST_SWORD)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LFIST_SWORD)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LFIST_SWORD)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RHAND)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RHAND)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST_SLINGSHOT)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST_SLINGSHOT)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SWORD_SHEATHED)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SWORD_SHEATHED)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SWORD_SHEATH)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SWORD_SHEATH)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_WAIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_WAIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST_SLINGSHOT)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST_SLINGSHOT)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RHAND_OCARINA_FAIRY)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RHAND_OCARINA_FAIRY)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RHAND_OCARINA_TIME)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RHAND_OCARINA_TIME)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LFIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LFIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LFIST_BOOMERANG)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LFIST_BOOMERANG)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LHAND_BOTTLE)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LHAND_BOTTLE)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RSHOULDER)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_FPS_RARM_SLINGSHOT)

    writer.GoTo(0xE6B2C)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_BOTTLE)

    writer.GoTo(0xE6B74)
    writer.SetAdvance(4)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SLINGSHOT_STRING)
    writer.WriteModelData(0x44178000)  # string anchor x: 606.0
    writer.WriteModelData(0x436C0000)  # string anchor y: 236.0

    writer.GoTo(0x6922E)
    writer.WriteModelDataHi(Offsets.CHILD_LINK_LUT_DL_GORON_BRACELET)
    writer.GoTo(0x69232)
    writer.WriteModelDataLo(Offsets.CHILD_LINK_LUT_DL_GORON_BRACELET)
    writer.GoTo(0x6A80E)
    writer.WriteModelDataHi(Offsets.CHILD_LINK_LUT_DL_DEKU_STICK)
    writer.GoTo(0x6A812)
    writer.WriteModelDataLo(Offsets.CHILD_LINK_LUT_DL_DEKU_STICK)

    writer.SetBase('Stick')
    writer.GoTo(0x334)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_DEKU_STICK)
    writer.GoTo(0x330)
    writer.WriteModelData16(0x0015)

    writer.SetBase('Shield')
    writer.GoTo(0x7EE)
    writer.WriteModelDataHi(Offsets.CHILD_LINK_LUT_DL_SHIELD_DEKU_ODD)
    writer.GoTo(0x7F2)
    writer.WriteModelDataLo(Offsets.CHILD_LINK_LUT_DL_SHIELD_DEKU_ODD)

    writer.SetBase('Player')
    writer.GoTo(0x2253C)
    writer.SetAdvance(4)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_MASK_KEATON)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_MASK_SKULL)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_MASK_SPOOKY)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_MASK_BUNNY)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_MASK_GORON)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_MASK_ZORA)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_MASK_GERUDO)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_MASK_TRUTH)

    writer.SetBase('GraveyardKid')
    writer.GoTo(0xE62)
    writer.WriteModelDataHi(Offsets.CHILD_LINK_LUT_DL_MASK_SPOOKY)
    writer.GoTo(0xE66)
    writer.WriteModelDataLo(Offsets.CHILD_LINK_LUT_DL_MASK_SPOOKY)

    writer.SetBase('Guard')
    writer.GoTo(0x1EA2)
    writer.WriteModelDataHi(Offsets.CHILD_LINK_LUT_DL_MASK_KEATON)
    writer.GoTo(0x1EA6)
    writer.WriteModelDataLo(Offsets.CHILD_LINK_LUT_DL_MASK_KEATON)

    writer.SetBase('RunningMan')
    writer.GoTo(0x1142)
    writer.WriteModelDataHi(Offsets.CHILD_LINK_LUT_DL_MASK_BUNNY)
    writer.GoTo(0x1146)
    writer.WriteModelDataLo(Offsets.CHILD_LINK_LUT_DL_MASK_BUNNY)

    writer.SetBase('Code')
    writer.GoTo(0xE65A4)
    writer.WriteModelData(CHILD_HIERARCHY)  # Hierarchy pointer


# LUT offsets for adult and child
class Offsets(IntEnum):
    ADULT_LINK_LUT_DL_WAIST = 0x06005090
    ADULT_LINK_LUT_DL_RTHIGH = 0x06005098
    ADULT_LINK_LUT_DL_RSHIN = 0x060050A0
    ADULT_LINK_LUT_DL_RFOOT = 0x060050A8
    ADULT_LINK_LUT_DL_LTHIGH = 0x060050B0
    ADULT_LINK_LUT_DL_LSHIN = 0x060050B8
    ADULT_LINK_LUT_DL_LFOOT = 0x060050C0
    ADULT_LINK_LUT_DL_HEAD = 0x060050C8
    ADULT_LINK_LUT_DL_HAT = 0x060050D0
    ADULT_LINK_LUT_DL_COLLAR = 0x060050D8
    ADULT_LINK_LUT_DL_LSHOULDER = 0x060050E0
    ADULT_LINK_LUT_DL_LFOREARM = 0x060050E8
    ADULT_LINK_LUT_DL_RSHOULDER = 0x060050F0
    ADULT_LINK_LUT_DL_RFOREARM = 0x060050F8
    ADULT_LINK_LUT_DL_TORSO = 0x06005100
    ADULT_LINK_LUT_DL_LHAND = 0x06005108
    ADULT_LINK_LUT_DL_LFIST = 0x06005110
    ADULT_LINK_LUT_DL_LHAND_BOTTLE = 0x06005118
    ADULT_LINK_LUT_DL_RHAND = 0x06005120
    ADULT_LINK_LUT_DL_RFIST = 0x06005128
    ADULT_LINK_LUT_DL_SWORD_SHEATH = 0x06005130
    ADULT_LINK_LUT_DL_SWORD_HILT = 0x06005138
    ADULT_LINK_LUT_DL_SWORD_BLADE = 0x06005140
    ADULT_LINK_LUT_DL_LONGSWORD_HILT = 0x06005148
    ADULT_LINK_LUT_DL_LONGSWORD_BLADE = 0x06005150
    ADULT_LINK_LUT_DL_LONGSWORD_BROKEN = 0x06005158
    ADULT_LINK_LUT_DL_SHIELD_HYLIAN = 0x06005160
    ADULT_LINK_LUT_DL_SHIELD_MIRROR = 0x06005168
    ADULT_LINK_LUT_DL_HAMMER = 0x06005170
    ADULT_LINK_LUT_DL_BOTTLE = 0x06005178
    ADULT_LINK_LUT_DL_BOW = 0x06005180
    ADULT_LINK_LUT_DL_OCARINA_TIME = 0x06005188
    ADULT_LINK_LUT_DL_HOOKSHOT = 0x06005190
    ADULT_LINK_LUT_DL_UPGRADE_LFOREARM = 0x06005198
    ADULT_LINK_LUT_DL_UPGRADE_LHAND = 0x060051A0
    ADULT_LINK_LUT_DL_UPGRADE_LFIST = 0x060051A8
    ADULT_LINK_LUT_DL_UPGRADE_RFOREARM = 0x060051B0
    ADULT_LINK_LUT_DL_UPGRADE_RHAND = 0x060051B8
    ADULT_LINK_LUT_DL_UPGRADE_RFIST = 0x060051C0
    ADULT_LINK_LUT_DL_BOOT_LIRON = 0x060051C8
    ADULT_LINK_LUT_DL_BOOT_RIRON = 0x060051D0
    ADULT_LINK_LUT_DL_BOOT_LHOVER = 0x060051D8
    ADULT_LINK_LUT_DL_BOOT_RHOVER = 0x060051E0
    ADULT_LINK_LUT_DL_FPS_LFOREARM = 0x060051E8
    ADULT_LINK_LUT_DL_FPS_LHAND = 0x060051F0
    ADULT_LINK_LUT_DL_FPS_RFOREARM = 0x060051F8
    ADULT_LINK_LUT_DL_FPS_RHAND = 0x06005200
    ADULT_LINK_LUT_DL_FPS_HOOKSHOT = 0x06005208
    ADULT_LINK_LUT_DL_HOOKSHOT_CHAIN = 0x06005210
    ADULT_LINK_LUT_DL_HOOKSHOT_HOOK = 0x06005218
    ADULT_LINK_LUT_DL_HOOKSHOT_AIM = 0x06005220
    ADULT_LINK_LUT_DL_BOW_STRING = 0x06005228
    ADULT_LINK_LUT_DL_BLADEBREAK = 0x06005230
    ADULT_LINK_LUT_DL_SWORD_SHEATHED = 0x06005238
    ADULT_LINK_LUT_DL_SHIELD_HYLIAN_BACK = 0x06005258
    ADULT_LINK_LUT_DL_SHIELD_MIRROR_BACK = 0x06005268
    ADULT_LINK_LUT_DL_SWORD_SHIELD_HYLIAN = 0x06005278
    ADULT_LINK_LUT_DL_SWORD_SHIELD_MIRROR = 0x06005288
    ADULT_LINK_LUT_DL_SHEATH0_HYLIAN = 0x06005298
    ADULT_LINK_LUT_DL_SHEATH0_MIRROR = 0x060052A8
    ADULT_LINK_LUT_DL_LFIST_SWORD = 0x060052B8
    ADULT_LINK_LUT_DL_LFIST_LONGSWORD = 0x060052D0
    ADULT_LINK_LUT_DL_LFIST_LONGSWORD_BROKEN = 0x060052E8
    ADULT_LINK_LUT_DL_LFIST_HAMMER = 0x06005300
    ADULT_LINK_LUT_DL_RFIST_SHIELD_HYLIAN = 0x06005310
    ADULT_LINK_LUT_DL_RFIST_SHIELD_MIRROR = 0x06005320
    ADULT_LINK_LUT_DL_RFIST_BOW = 0x06005330
    ADULT_LINK_LUT_DL_RFIST_HOOKSHOT = 0x06005340
    ADULT_LINK_LUT_DL_RHAND_OCARINA_TIME = 0x06005350
    ADULT_LINK_LUT_DL_FPS_RHAND_BOW = 0x06005360
    ADULT_LINK_LUT_DL_FPS_LHAND_HOOKSHOT = 0x06005370

    CHILD_LINK_LUT_DL_SHIELD_DEKU = 0x060050D0
    CHILD_LINK_LUT_DL_WAIST = 0x060050D8
    CHILD_LINK_LUT_DL_RTHIGH = 0x060050E0
    CHILD_LINK_LUT_DL_RSHIN = 0x060050E8
    CHILD_LINK_LUT_DL_RFOOT = 0x060050F0
    CHILD_LINK_LUT_DL_LTHIGH = 0x060050F8
    CHILD_LINK_LUT_DL_LSHIN = 0x06005100
    CHILD_LINK_LUT_DL_LFOOT = 0x06005108
    CHILD_LINK_LUT_DL_HEAD = 0x06005110
    CHILD_LINK_LUT_DL_HAT = 0x06005118
    CHILD_LINK_LUT_DL_COLLAR = 0x06005120
    CHILD_LINK_LUT_DL_LSHOULDER = 0x06005128
    CHILD_LINK_LUT_DL_LFOREARM = 0x06005130
    CHILD_LINK_LUT_DL_RSHOULDER = 0x06005138
    CHILD_LINK_LUT_DL_RFOREARM = 0x06005140
    CHILD_LINK_LUT_DL_TORSO = 0x06005148
    CHILD_LINK_LUT_DL_LHAND = 0x06005150
    CHILD_LINK_LUT_DL_LFIST = 0x06005158
    CHILD_LINK_LUT_DL_LHAND_BOTTLE = 0x06005160
    CHILD_LINK_LUT_DL_RHAND = 0x06005168
    CHILD_LINK_LUT_DL_RFIST = 0x06005170
    CHILD_LINK_LUT_DL_SWORD_SHEATH = 0x06005178
    CHILD_LINK_LUT_DL_SWORD_HILT = 0x06005180
    CHILD_LINK_LUT_DL_SWORD_BLADE = 0x06005188
    CHILD_LINK_LUT_DL_SLINGSHOT = 0x06005190
    CHILD_LINK_LUT_DL_OCARINA_FAIRY = 0x06005198
    CHILD_LINK_LUT_DL_OCARINA_TIME = 0x060051A0
    CHILD_LINK_LUT_DL_DEKU_STICK = 0x060051A8
    CHILD_LINK_LUT_DL_BOOMERANG = 0x060051B0
    CHILD_LINK_LUT_DL_SHIELD_HYLIAN_BACK = 0x060051B8
    CHILD_LINK_LUT_DL_BOTTLE = 0x060051C0
    CHILD_LINK_LUT_DL_MASTER_SWORD = 0x060051C8
    CHILD_LINK_LUT_DL_GORON_BRACELET = 0x060051D0
    CHILD_LINK_LUT_DL_FPS_RIGHT_ARM = 0x060051D8
    CHILD_LINK_LUT_DL_SLINGSHOT_STRING = 0x060051E0
    CHILD_LINK_LUT_DL_MASK_BUNNY = 0x060051E8
    CHILD_LINK_LUT_DL_MASK_GERUDO = 0x060051F0
    CHILD_LINK_LUT_DL_MASK_GORON = 0x060051F8
    CHILD_LINK_LUT_DL_MASK_KEATON = 0x06005200
    CHILD_LINK_LUT_DL_MASK_SPOOKY = 0x06005208
    CHILD_LINK_LUT_DL_MASK_TRUTH = 0x06005210
    CHILD_LINK_LUT_DL_MASK_ZORA = 0x06005218
    CHILD_LINK_LUT_DL_MASK_SKULL = 0x06005220
    CHILD_LINK_DL_SWORD_SHEATHED = 0x06005228
    CHILD_LINK_LUT_DL_SWORD_SHEATHED = 0x06005248
    CHILD_LINK_DL_SHIELD_DEKU_ODD = 0x06005250
    CHILD_LINK_LUT_DL_SHIELD_DEKU_ODD = 0x06005260
    CHILD_LINK_DL_SHIELD_DEKU_BACK = 0x06005268
    CHILD_LINK_LUT_DL_SHIELD_DEKU_BACK = 0x06005278
    CHILD_LINK_DL_SWORD_SHIELD_HYLIAN = 0x06005280
    CHILD_LINK_LUT_DL_SWORD_SHIELD_HYLIAN = 0x06005290
    CHILD_LINK_DL_SWORD_SHIELD_DEKU = 0x06005298
    CHILD_LINK_LUT_DL_SWORD_SHIELD_DEKU = 0x060052A8
    CHILD_LINK_DL_SHEATH0_HYLIAN = 0x060052B0
    CHILD_LINK_LUT_DL_SHEATH0_HYLIAN = 0x060052C0
    CHILD_LINK_DL_SHEATH0_DEKU = 0x060052C8
    CHILD_LINK_LUT_DL_SHEATH0_DEKU = 0x060052D8
    CHILD_LINK_DL_LFIST_SWORD = 0x060052E0
    CHILD_LINK_LUT_DL_LFIST_SWORD = 0x060052F8
    CHILD_LINK_DL_LHAND_PEDESTALSWORD = 0x06005300
    CHILD_LINK_LUT_DL_LHAND_PEDESTALSWORD = 0x06005310
    CHILD_LINK_DL_LFIST_BOOMERANG = 0x06005318
    CHILD_LINK_LUT_DL_LFIST_BOOMERANG = 0x06005328
    CHILD_LINK_DL_RFIST_SHIELD_DEKU = 0x06005330
    CHILD_LINK_LUT_DL_RFIST_SHIELD_DEKU = 0x06005340
    CHILD_LINK_DL_RFIST_SLINGSHOT = 0x06005348
    CHILD_LINK_LUT_DL_RFIST_SLINGSHOT = 0x06005358
    CHILD_LINK_DL_RHAND_OCARINA_FAIRY = 0x06005360
    CHILD_LINK_LUT_DL_RHAND_OCARINA_FAIRY = 0x06005370
    CHILD_LINK_DL_RHAND_OCARINA_TIME = 0x06005378
    CHILD_LINK_LUT_DL_RHAND_OCARINA_TIME = 0x06005388
    CHILD_LINK_DL_FPS_RARM_SLINGSHOT = 0x06005390
    CHILD_LINK_LUT_DL_FPS_RARM_SLINGSHOT = 0x060053A0


# Adult model pieces and their offsets, both in the LUT and in vanilla
AdultPieces: dict[str, tuple[Offsets, int]] = {
    "Sheath": (Offsets.ADULT_LINK_LUT_DL_SWORD_SHEATH, 0x249D8),
    "FPS.Hookshot": (Offsets.ADULT_LINK_LUT_DL_FPS_HOOKSHOT, 0x2A738),
    "Hilt.2": (Offsets.ADULT_LINK_LUT_DL_SWORD_HILT, 0x22060),  # 0x21F78 + 0xE8, skips blade
    "Hilt.3": (Offsets.ADULT_LINK_LUT_DL_LONGSWORD_HILT, 0x238C8),
    "Blade.2": (Offsets.ADULT_LINK_LUT_DL_SWORD_BLADE, 0x21F78),
    "Hookshot.Spike": (Offsets.ADULT_LINK_LUT_DL_HOOKSHOT_HOOK, 0x2B288),
    "Hookshot": (Offsets.ADULT_LINK_LUT_DL_HOOKSHOT, 0x24D70),
    "Fist.L": (Offsets.ADULT_LINK_LUT_DL_LFIST, 0x21CE8),
    "Fist.R": (Offsets.ADULT_LINK_LUT_DL_RFIST, 0x226E0),
    "FPS.Forearm.L": (Offsets.ADULT_LINK_LUT_DL_FPS_LFOREARM, 0x29FA0),
    "FPS.Forearm.R": (Offsets.ADULT_LINK_LUT_DL_FPS_RFOREARM, 0x29918),
    "Gauntlet.Fist.L": (Offsets.ADULT_LINK_LUT_DL_UPGRADE_LFIST, 0x25438),
    "Gauntlet.Fist.R": (Offsets.ADULT_LINK_LUT_DL_UPGRADE_RFIST, 0x257B8),
    "Gauntlet.Forearm.L": (Offsets.ADULT_LINK_LUT_DL_UPGRADE_LFOREARM, 0x25218),
    "Gauntlet.Forearm.R": (Offsets.ADULT_LINK_LUT_DL_UPGRADE_RFOREARM, 0x25598),
    "Gauntlet.Hand.L": (Offsets.ADULT_LINK_LUT_DL_UPGRADE_LHAND, 0x252D8),
    "Gauntlet.Hand.R": (Offsets.ADULT_LINK_LUT_DL_UPGRADE_RHAND, 0x25658),
    "Bottle.Hand.L": (Offsets.ADULT_LINK_LUT_DL_LHAND_BOTTLE, 0x29600),
    "FPS.Hand.L": (Offsets.ADULT_LINK_LUT_DL_FPS_LHAND, 0x24B58),
    "FPS.Hand.R": (Offsets.ADULT_LINK_LUT_DL_FPS_RHAND, 0x29C20),
    "Bow.String": (Offsets.ADULT_LINK_LUT_DL_BOW_STRING, 0x2B108),
    "Bow": (Offsets.ADULT_LINK_LUT_DL_BOW, 0x22DA8),
    "Blade.3.Break": (Offsets.ADULT_LINK_LUT_DL_BLADEBREAK, 0x2BA38),
    "Blade.3": (Offsets.ADULT_LINK_LUT_DL_LONGSWORD_BLADE, 0x23A28),  # 0x238C8 + 0x160, skips hilt
    "Bottle": (Offsets.ADULT_LINK_LUT_DL_BOTTLE, 0x2AD58),
    "Broken.Blade.3": (Offsets.ADULT_LINK_LUT_DL_LONGSWORD_BROKEN, 0x23EB0),  # 0x23D50 + 0x160, skips hilt
    "Foot.2.L": (Offsets.ADULT_LINK_LUT_DL_BOOT_LIRON, 0x25918),
    "Foot.2.R": (Offsets.ADULT_LINK_LUT_DL_BOOT_RIRON, 0x25A60),
    "Foot.3.L": (Offsets.ADULT_LINK_LUT_DL_BOOT_LHOVER, 0x25BA8),
    "Foot.3.R": (Offsets.ADULT_LINK_LUT_DL_BOOT_RHOVER, 0x25DB0),
    "Hammer": (Offsets.ADULT_LINK_LUT_DL_HAMMER, 0x233E0),
    "Hookshot.Aiming.Reticule": (Offsets.ADULT_LINK_LUT_DL_HOOKSHOT_AIM, 0x2CB48),
    "Hookshot.Chain": (Offsets.ADULT_LINK_LUT_DL_HOOKSHOT_CHAIN, 0x2AFF0),
    "Ocarina.2": (Offsets.ADULT_LINK_LUT_DL_OCARINA_TIME, 0x248D8),  # 0x24698 + 0x240, skips hand
    "Shield.2": (Offsets.ADULT_LINK_LUT_DL_SHIELD_HYLIAN, 0x22970),
    "Shield.3": (Offsets.ADULT_LINK_LUT_DL_SHIELD_MIRROR, 0x241C0),
    "Limb 1": (Offsets.ADULT_LINK_LUT_DL_WAIST, 0x35330),
    "Limb 3": (Offsets.ADULT_LINK_LUT_DL_RTHIGH, 0x35678),
    "Limb 4": (Offsets.ADULT_LINK_LUT_DL_RSHIN, 0x358B0),
    "Limb 5": (Offsets.ADULT_LINK_LUT_DL_RFOOT, 0x358B0),
    "Limb 6": (Offsets.ADULT_LINK_LUT_DL_LTHIGH, 0x35CB8),
    "Limb 7": (Offsets.ADULT_LINK_LUT_DL_LSHIN, 0x35EF0),
    "Limb 8": (Offsets.ADULT_LINK_LUT_DL_LFOOT, 0x361A0),
    "Limb 10": (Offsets.ADULT_LINK_LUT_DL_HEAD, 0x365E8),
    "Limb 11": (Offsets.ADULT_LINK_LUT_DL_HAT, 0x36D30),
    "Limb 12": (Offsets.ADULT_LINK_LUT_DL_COLLAR, 0x362F8),
    "Limb 13": (Offsets.ADULT_LINK_LUT_DL_LSHOULDER, 0x37210),
    "Limb 14": (Offsets.ADULT_LINK_LUT_DL_LFOREARM, 0x373D8),
    "Limb 15": (Offsets.ADULT_LINK_LUT_DL_LHAND, 0x21AA8),
    "Limb 16": (Offsets.ADULT_LINK_LUT_DL_RSHOULDER, 0x36E58),
    "Limb 17": (Offsets.ADULT_LINK_LUT_DL_RFOREARM, 0x37018),
    "Limb 18": (Offsets.ADULT_LINK_LUT_DL_RHAND, 0x22498),
    "Limb 20": (Offsets.ADULT_LINK_LUT_DL_TORSO, 0x363B8),
}


# Note: Some skips which can be implemented by skipping the beginning portion of the model
# rather than specifying those indices here, simply have their offset in the table above
# increased by whatever amount of starting indices would be skipped.
adultSkips: dict[str, list[tuple[int, int]]] = {
    "FPS.Hookshot":  [(0x2F0, 0x618)],
    "Hilt.2": [(0x1E8, 0x430)],
    "Hilt.3": [(0x160, 0x480)],
    "Blade.2": [(0xE8, 0x518)],
    "Hookshot": [(0x250, 0x4A0)],
    "Bow": [(0x158, 0x3B0)],
    "Blade.3": [(0xB8, 0x320)],
    "Broken.Blade.3": [(0xA0, 0x308)],
    "Hammer": [(0x278, 0x4E0)],
    "Shield.2": [(0x158, 0x2B8), (0x3A8, 0x430)],  # Fist is in 2 pieces
    "Shield.3": [(0x1B8, 0x3E8)],
}

adultSkeleton: list[list[int]] = [
    [0xFFC7, 0x0D31, 0x0000],  # Limb 0
    [0x0000, 0x0000, 0x0000],  # Limb 1
    [0x03B1, 0x0000, 0x0000],  # Limb 2
    [0xFE71, 0x0045, 0xFF07],  # Limb 3
    [0x051A, 0x0000, 0x0000],  # Limb 4
    [0x04E8, 0x0005, 0x000B],  # Limb 5
    [0xFE74, 0x004C, 0x0108],  # Limb 6
    [0x0518, 0x0000, 0x0000],  # Limb 7
    [0x04E9, 0x0006, 0x0003],  # Limb 8
    [0x0000, 0x0015, 0xFFF9],  # Limb 9
    [0x0570, 0xFEFD, 0x0000],  # Limb 10
    [0xFED6, 0xFD44, 0x0000],  # Limb 11
    [0x0000, 0x0000, 0x0000],  # Limb 12
    [0x040F, 0xFF54, 0x02A8],  # Limb 13
    [0x0397, 0x0000, 0x0000],  # Limb 14
    [0x02F2, 0x0000, 0x0000],  # Limb 15
    [0x040F, 0xFF53, 0xFD58],  # Limb 16
    [0x0397, 0x0000, 0x0000],  # Limb 17
    [0x02F2, 0x0000, 0x0000],  # Limb 18
    [0x03D2, 0xFD4C, 0x0156],  # Limb 19
    [0x0000, 0x0000, 0x0000],  # Limb 20
]


ChildPieces: dict[str, tuple[Offsets, int]] = {
    "Slingshot.String": (Offsets.CHILD_LINK_LUT_DL_SLINGSHOT_STRING, 0x221A8),
    "Sheath": (Offsets.CHILD_LINK_LUT_DL_SWORD_SHEATH, 0x15408),
    "Blade.2": (Offsets.CHILD_LINK_LUT_DL_MASTER_SWORD, 0x15698),  # 0x15540 + 0x158, skips fist
    "Blade.1": (Offsets.CHILD_LINK_LUT_DL_SWORD_BLADE, 0x14110),  # 0x13F38 + 0x1D8, skips fist and hilt
    "Boomerang": (Offsets.CHILD_LINK_LUT_DL_BOOMERANG, 0x14660),
    "Fist.L": (Offsets.CHILD_LINK_LUT_DL_LFIST, 0x13E18),
    "Fist.R": (Offsets.CHILD_LINK_LUT_DL_RFIST, 0x14320),
    "Hilt.1": (Offsets.CHILD_LINK_LUT_DL_SWORD_HILT, 0x14048),  # 0x13F38 + 0x110, skips fist
    "Shield.1": (Offsets.CHILD_LINK_LUT_DL_SHIELD_DEKU, 0x14440),
    "Slingshot": (Offsets.CHILD_LINK_LUT_DL_SLINGSHOT, 0x15F08),  # 0x15DF0 + 0x118, skips fist
    "Ocarina.1": (Offsets.CHILD_LINK_LUT_DL_OCARINA_FAIRY, 0x15BA8),
    "Bottle": (Offsets.CHILD_LINK_LUT_DL_BOTTLE, 0x18478),
    "Ocarina.2": (Offsets.CHILD_LINK_LUT_DL_OCARINA_TIME, 0x15AB8),  # 0x15958 + 0x160, skips hand
    "Bottle.Hand.L": (Offsets.CHILD_LINK_LUT_DL_LHAND_BOTTLE, 0x18478),  # Just the bottle, couldn't find one with hand and bottle
    "GoronBracelet": (Offsets.CHILD_LINK_LUT_DL_GORON_BRACELET, 0x16118),
    "Mask.Bunny": (Offsets.CHILD_LINK_LUT_DL_MASK_BUNNY, 0x2CA38),
    "Mask.Skull": (Offsets.CHILD_LINK_LUT_DL_MASK_SKULL, 0x2AD40),
    "Mask.Spooky": (Offsets.CHILD_LINK_LUT_DL_MASK_SPOOKY, 0x2AF70),
    "Mask.Gerudo": (Offsets.CHILD_LINK_LUT_DL_MASK_GERUDO, 0x2B788),
    "Mask.Goron": (Offsets.CHILD_LINK_LUT_DL_MASK_GORON, 0x2B350),
    "Mask.Keaton": (Offsets.CHILD_LINK_LUT_DL_MASK_KEATON, 0x2B060),
    "Mask.Truth": (Offsets.CHILD_LINK_LUT_DL_MASK_TRUTH, 0x2B1F0),
    "Mask.Zora": (Offsets.CHILD_LINK_LUT_DL_MASK_ZORA, 0x2B580),
    "FPS.Forearm.R": (Offsets.CHILD_LINK_LUT_DL_FPS_RIGHT_ARM, 0x18048),
    "DekuStick": (Offsets.CHILD_LINK_LUT_DL_DEKU_STICK, 0x6CC0),
    "Shield.2": (Offsets.CHILD_LINK_LUT_DL_SHIELD_HYLIAN_BACK, 0x14C30),  # 0x14B40 + 0xF0, skips sheath
    "Limb 1": (Offsets.CHILD_LINK_LUT_DL_WAIST, 0x202A8),
    "Limb 3": (Offsets.CHILD_LINK_LUT_DL_RTHIGH, 0x204F0),
    "Limb 4": (Offsets.CHILD_LINK_LUT_DL_RSHIN, 0x206E8),
    "Limb 5": (Offsets.CHILD_LINK_LUT_DL_RFOOT, 0x20978),
    "Limb 6": (Offsets.CHILD_LINK_LUT_DL_LTHIGH, 0x20AD8),
    "Limb 7": (Offsets.CHILD_LINK_LUT_DL_LSHIN, 0x20CD0),
    "Limb 8": (Offsets.CHILD_LINK_LUT_DL_LFOOT, 0x20F60),
    "Limb 10": (Offsets.CHILD_LINK_LUT_DL_HEAD, 0x21360),
    "Limb 11": (Offsets.CHILD_LINK_LUT_DL_HAT, 0x219B0),
    "Limb 12": (Offsets.CHILD_LINK_LUT_DL_COLLAR, 0x210C0),
    "Limb 13": (Offsets.CHILD_LINK_LUT_DL_LSHOULDER, 0x21E18),
    "Limb 14": (Offsets.CHILD_LINK_LUT_DL_LFOREARM, 0x21FE8),
    "Limb 15": (Offsets.CHILD_LINK_LUT_DL_LHAND, 0x13CB0),
    "Limb 16": (Offsets.CHILD_LINK_LUT_DL_RSHOULDER, 0x21AE8),
    "Limb 17": (Offsets.CHILD_LINK_LUT_DL_RFOREARM, 0x21CB8),
    "Limb 18": (Offsets.CHILD_LINK_LUT_DL_RHAND, 0x141C0),
    "Limb 20": (Offsets.CHILD_LINK_LUT_DL_TORSO, 0x21130),
}


childSkips: dict[str, list[tuple[int, int]]] = {
    "Boomerang": [(0x140, 0x240)],
    "Hilt.1": [(0xC8, 0x170)],
    "Shield.1": [(0x140, 0x218)],
    "Ocarina.1": [(0x110, 0x240)],
}

childSkeleton: list[list[int]] = [
    [0x0000, 0x0948, 0x0000],  # Limb 0
    [0xFFFC, 0xFF98, 0x0000],  # Limb 1
    [0x025F, 0x0000, 0x0000],  # Limb 2
    [0xFF54, 0x0032, 0xFF42],  # Limb 3
    [0x02B9, 0x0000, 0x0000],  # Limb 4
    [0x0339, 0x0005, 0x000B],  # Limb 5
    [0xFF56, 0x0039, 0x00C0],  # Limb 6
    [0x02B7, 0x0000, 0x0000],  # Limb 7
    [0x0331, 0x0008, 0x0004],  # Limb 8
    [0x0000, 0xFF99, 0xFFF9],  # Limb 9
    [0x03E4, 0xFF37, 0xFFFF],  # Limb 10
    [0xFE93, 0xFD62, 0x0000],  # Limb 11
    [0x0000, 0x0000, 0x0000],  # Limb 12
    [0x02B8, 0xFF51, 0x01D2],  # Limb 13
    [0x0245, 0x0000, 0x0000],  # Limb 14
    [0x0202, 0x0000, 0x0000],  # Limb 15
    [0x02B8, 0xFF51, 0xFE2E],  # Limb 16
    [0x0241, 0x0000, 0x0000],  # Limb 17
    [0x020D, 0x0000, 0x0000],  # Limb 18
    [0x0291, 0xFDF5, 0x016F],  # Limb 19
    [0x0000, 0x0000, 0x0000],  # Limb 20
]

# Maps old pipeline limb names to new pipeline names
oldToNewPipeline = {
    "Limb 1": "Waist",
    "Limb 3": "Thigh.R",
    "Limb 4": "Shin.R",
    "Limb 5": "Foot.R",
    "Limb 6": "Thigh.L",
    "Limb 7": "Shin.L",
    "Limb 8": "Foot.L",
    "Limb 10": "Head",
    "Limb 11": "Hat",
    "Limb 12": "Collar",
    "Limb 13": "Shoulder.L",
    "Limb 14": "Forearm.L",
    "Limb 15": "Hand.L",
    "Limb 16": "Shoulder.R",
    "Limb 17": "Forearm.R",
    "Limb 18": "Hand.R",
    "Limb 20": "Torso",
}

# Misc. constants
CODE_START: int          = 0x00A87000
PLAYER_START: int        = 0x00BCDB70
HOOK_START: int          = 0x00CAD2C0
SHIELD_START: int        = 0x00DB1F40
STICK_START: int         = 0x00EAD0F0
GRAVEYARD_KID_START: int = 0x00E60920
GUARD_START: int         = 0x00D1A690
RUNNING_MAN_START: int   = 0x00E50440

BASE_OFFSET: int         = 0x06000000
LUT_START: int           = 0x00005000
LUT_END: int             = 0x00005800
PRE_CONSTANT_START: int  = 0X0000500C

ADULT_START: int         = 0x00F86000
ADULT_SIZE: int          = 0x00037800
ADULT_HIERARCHY: int     = 0x06005380
ADULT_POST_START: int    = 0x00005238

CHILD_START: int         = 0x00FBE000
CHILD_SIZE: int          = 0x0002CF80
CHILD_HIERARCHY: int     = 0x060053A8
CHILD_POST_START: int    = 0x00005228

# Parts of the rom to not overwrite when applying a patch file
restrictiveBytes: list[tuple[int, int]] = [
    (ADULT_START, ADULT_SIZE),  # Ignore adult model
    (CHILD_START, CHILD_SIZE),  # Ignore child model
    # Adult model pointers
    (CODE_START + 0xE6718, 75 * 8),  # Writes 75 4-byte pointers with 4 bytes between
    (CODE_START + 0xE6A4C, 4 * 4),  # Writes 4 4-byte pointers
    (CODE_START + 0xE6B28, 1 * 4),  # Writes 1 4-byte pointer
    (CODE_START + 0xE6B64, 3 * 4),  # Writes 1 4-byte pointer and 2 4-byte values
    # 2 byte hi/lo segments of pointers
    (CODE_START + 0x69112, 2),
    (CODE_START + 0x69116, 2),
    (CODE_START + 0x6912E, 2),
    (CODE_START + 0x69132, 2),
    (CODE_START + 0x6914E, 2),
    (CODE_START + 0x69162, 2),
    (CODE_START + 0x69166, 2),
    (CODE_START + 0x69172, 2),
    (CODE_START + 0x6919E, 2),
    (CODE_START + 0x691A2, 2),
    (CODE_START + 0x691AE, 2),
    (CODE_START + 0x691B2, 2),
    (CODE_START + 0x69DEA, 2),
    (CODE_START + 0x69DEE, 2),
    (CODE_START + 0x6A666, 2),
    (CODE_START + 0x6A66A, 2),
    (HOOK_START + 0xA72, 2),
    (HOOK_START + 0xA76, 2),
    (HOOK_START + 0xB66, 2),
    (HOOK_START + 0xB6A, 2),
    (HOOK_START + 0xBA8, 1 * 2),  # Writes 1 2-byte value
    (STICK_START + 0x32C, 1 * 4),  # Writes 1 4-byte pointer
    (STICK_START + 0x328, 1 * 2),  # Writes 1 2-byte value
    (CODE_START + 0xE65A0, 1 * 4),  # Writes 4-byte hierarchy pointer
    # Child model pointers
    (CODE_START + 0xE671C, 75 * 8),  # Writes 75 4-byte pointers with 4 bytes between
    (CODE_START + 0xE6B2C, 1 * 8),  # Writes 1 4-byte pointer with 4 bytes after
    (CODE_START + 0xE6B74, 3 * 4),  # Writes 1 4-byte pointer and 2 4-byte values
    (CODE_START + 0x6922E, 2),
    (CODE_START + 0x69232, 2),
    (CODE_START + 0x6A80E, 2),
    (CODE_START + 0x6A812, 2),
    (STICK_START + 0x334, 1 * 4),  # Writes 1 4-byte pointer
    (STICK_START + 0x330, 1 * 2),  # Writes 1 2-byte value
    (SHIELD_START + 0x7EE, 2),
    (SHIELD_START + 0x7F2, 2),
    (PLAYER_START + 0x2253C, 8 * 4),  # Writes 8 4-byte pointers
    (GRAVEYARD_KID_START + 0xE62, 2),
    (GRAVEYARD_KID_START + 0xE66, 2),
    (GUARD_START + 0x1EA2, 2),
    (GUARD_START + 0x1EA6, 2),
    (RUNNING_MAN_START + 0x1142, 2),
    (RUNNING_MAN_START + 0x1146, 2),
    (CODE_START + 0xE65A4, 1 * 4),  # Writes 4-byte hierarchy pointer
]
