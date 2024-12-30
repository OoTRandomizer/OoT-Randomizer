import { toPaddedHexString } from './toPaddedHexString';

export class Display_List_Command {
  code: string;
  address: number;
  addressAsString: string;
  actualFileOffsetCode: number;
  actualFileOffsetAddress: number;
  actualCode: number;

  constructor(code: number, address: number, actualFileOffset: number) {
    this.code = toPaddedHexString(code, 8).toUpperCase();
    this.address = address;
    this.actualFileOffsetCode = actualFileOffset;
    this.actualFileOffsetAddress = actualFileOffset + 4;
    this.addressAsString = toPaddedHexString(this.address, 8);
    if (this.is06()) {
      this.address -= 0x06000000;
    }
    this.actualCode = code;
  }

  is06() {
    return this.addressAsString.startsWith('06');
  }
}
