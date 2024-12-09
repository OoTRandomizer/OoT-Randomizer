import fs from 'fs';

export class Zobj {
  buf: Buffer;

  constructor(buf: Buffer) {
    this.buf = buf;
  }

  cloneBuffer(): Buffer {
    let copy: Buffer = Buffer.alloc(this.buf.byteLength);
    this.buf.copy(copy);
    return copy;
  }

  isModLoaderZobj(): boolean {
    let b: Buffer = this.buf.slice(0x5000, 0x500b);
    return b.toString() === 'MODLOADER64';
  }
}
