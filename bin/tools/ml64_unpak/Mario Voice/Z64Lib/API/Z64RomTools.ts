import { IModLoaderAPI } from 'modloader64_api/IModLoaderAPI';

export class DMATableEntry{

  private ModLoader: IModLoaderAPI;
  private start: number;
  private size: number;
  private isCompressed: boolean;

  constructor(ModLoader: IModLoaderAPI, start: number, size: number, isCompressed: boolean){
    this.ModLoader = ModLoader;
    this.start = start;
    this.size = size;
    this.isCompressed = isCompressed;
  }

  readFile(): Buffer{
    let buf: Buffer = this.ModLoader.rom.romReadBuffer(this.start, this.size);
    if (this.isCompressed){
      buf = this.ModLoader.utils.yaz0Decode(buf);
    }
    return buf;
  }

  writeFile(buf: Buffer): void{
    let copy: Buffer = Buffer.alloc(buf.byteLength);
    buf.copy(copy);
    if (this.isCompressed){
      copy = this.ModLoader.utils.yaz0Encode(copy);
    }
    let original: Buffer = this.ModLoader.rom.romReadBuffer(this.start, this.size);
    copy.copy(original);
    this.ModLoader.rom.romWriteBuffer(this.start, copy);
  }
}

export class DMATable{

  private ModLoader: IModLoaderAPI;
  private DMA_Offset: number;
  
  constructor(ModLoader: IModLoaderAPI, DMA_Offset: number){
    this.ModLoader = ModLoader;
    this.DMA_Offset = DMA_Offset;
  }

  getFileEntry(index: number): DMATableEntry{
    let offset: number = (index * 0x10);
    let start: number = this.ModLoader.rom.romRead32(this.DMA_Offset + offset + 0x8);
    let end: number = this.ModLoader.rom.romRead32(this.DMA_Offset + offset + 0xC);
    let size: number = end - start;
    let isFileCompressed = true;
    if (end === 0) {
      isFileCompressed = false;
      size = this.ModLoader.rom.romRead32(this.DMA_Offset + offset + 0x4) - this.ModLoader.rom.romRead32(this.DMA_Offset + offset);
      end = start + size;
    }
    return new DMATableEntry(this.ModLoader, start, size, isFileCompressed);
  }
}

export class Z64RomTools {

  private ModLoader: IModLoaderAPI;
  private DMA_Offset: number;

  constructor(ModLoader: IModLoaderAPI, DMA_Offset: number) {
    this.ModLoader = ModLoader;
    this.DMA_Offset = DMA_Offset;
  }

  decompressFileFromRom(rom: Buffer, index: number): Buffer {
    let dma = this.DMA_Offset;
    let offset: number = index * 0x10;
    let start: number = rom.readUInt32BE(dma + offset + 0x8);
    let end: number = rom.readUInt32BE(dma + offset + 0xc);
    let size: number = end - start;
    let isFileCompressed = true;
    if (end === 0) {
      isFileCompressed = false;
      size = rom.readUInt32BE(dma + offset + 0x4) - rom.readUInt32BE(dma + offset);
      end = start + size;
    }
    if (start === 0){
      return Buffer.alloc(1);
    }
    let buf: Buffer = Buffer.alloc(size);
    if (start > rom.byteLength || end > rom.byteLength){
      console.log(start.toString(16) + " | " + end.toString(16));
      return Buffer.alloc(1);
    }
    rom.copy(buf, 0, start, end);
    if (isFileCompressed) {
      if (buf.readUInt32BE(0) !== 0x59617A30){
        return buf;
      }
      buf = this.ModLoader.utils.yaz0Decode(buf);
    }
    return buf;
  }

  recompressFileIntoRom(rom: Buffer, index: number, file: Buffer) {
    let dma = this.DMA_Offset;
    let offset: number = index * 0x10;
    let start: number = rom.readUInt32BE(dma + offset + 0x8);
    let end: number = rom.readUInt32BE(dma + offset + 0xc);
    let size: number = end - start;
    let isFileCompressed = true;
    if (end === 0) {
      isFileCompressed = false;
      size = rom.readUInt32BE(dma + offset + 0x4) - rom.readUInt32BE(dma + offset);
      end = start + size;
    }
    if (isFileCompressed) {
      let buf: Buffer = this.ModLoader.utils.yaz0Encode(file);
      buf.copy(rom, start);
    } else {
      file.copy(rom, start);
    }
  }
}