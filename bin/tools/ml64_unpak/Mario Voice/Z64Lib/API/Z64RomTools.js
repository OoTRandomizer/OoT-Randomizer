"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Z64RomTools = exports.DMATable = exports.DMATableEntry = void 0;
class DMATableEntry {
    constructor(ModLoader, start, size, isCompressed) {
        this.ModLoader = ModLoader;
        this.start = start;
        this.size = size;
        this.isCompressed = isCompressed;
    }
    readFile() {
        let buf = this.ModLoader.rom.romReadBuffer(this.start, this.size);
        if (this.isCompressed) {
            buf = this.ModLoader.utils.yaz0Decode(buf);
        }
        return buf;
    }
    writeFile(buf) {
        let copy = Buffer.alloc(buf.byteLength);
        buf.copy(copy);
        if (this.isCompressed) {
            copy = this.ModLoader.utils.yaz0Encode(copy);
        }
        let original = this.ModLoader.rom.romReadBuffer(this.start, this.size);
        copy.copy(original);
        this.ModLoader.rom.romWriteBuffer(this.start, copy);
    }
}
exports.DMATableEntry = DMATableEntry;
class DMATable {
    constructor(ModLoader, DMA_Offset) {
        this.ModLoader = ModLoader;
        this.DMA_Offset = DMA_Offset;
    }
    getFileEntry(index) {
        let offset = (index * 0x10);
        let start = this.ModLoader.rom.romRead32(this.DMA_Offset + offset + 0x8);
        let end = this.ModLoader.rom.romRead32(this.DMA_Offset + offset + 0xC);
        let size = end - start;
        let isFileCompressed = true;
        if (end === 0) {
            isFileCompressed = false;
            size = this.ModLoader.rom.romRead32(this.DMA_Offset + offset + 0x4) - this.ModLoader.rom.romRead32(this.DMA_Offset + offset);
            end = start + size;
        }
        return new DMATableEntry(this.ModLoader, start, size, isFileCompressed);
    }
}
exports.DMATable = DMATable;
class Z64RomTools {
    constructor(ModLoader, DMA_Offset) {
        this.ModLoader = ModLoader;
        this.DMA_Offset = DMA_Offset;
    }
    decompressFileFromRom(rom, index) {
        let dma = this.DMA_Offset;
        let offset = index * 0x10;
        let start = rom.readUInt32BE(dma + offset + 0x8);
        let end = rom.readUInt32BE(dma + offset + 0xc);
        let size = end - start;
        let isFileCompressed = true;
        if (end === 0) {
            isFileCompressed = false;
            size = rom.readUInt32BE(dma + offset + 0x4) - rom.readUInt32BE(dma + offset);
            end = start + size;
        }
        if (start === 0) {
            return Buffer.alloc(1);
        }
        let buf = Buffer.alloc(size);
        if (start > rom.byteLength || end > rom.byteLength) {
            console.log(start.toString(16) + " | " + end.toString(16));
            return Buffer.alloc(1);
        }
        rom.copy(buf, 0, start, end);
        if (isFileCompressed) {
            if (buf.readUInt32BE(0) !== 0x59617A30) {
                return buf;
            }
            buf = this.ModLoader.utils.yaz0Decode(buf);
        }
        return buf;
    }
    recompressFileIntoRom(rom, index, file) {
        let dma = this.DMA_Offset;
        let offset = index * 0x10;
        let start = rom.readUInt32BE(dma + offset + 0x8);
        let end = rom.readUInt32BE(dma + offset + 0xc);
        let size = end - start;
        let isFileCompressed = true;
        if (end === 0) {
            isFileCompressed = false;
            size = rom.readUInt32BE(dma + offset + 0x4) - rom.readUInt32BE(dma + offset);
            end = start + size;
        }
        if (isFileCompressed) {
            let buf = this.ModLoader.utils.yaz0Encode(file);
            buf.copy(rom, start);
        }
        else {
            file.copy(rom, start);
        }
    }
}
exports.Z64RomTools = Z64RomTools;
//# sourceMappingURL=Z64RomTools.js.map