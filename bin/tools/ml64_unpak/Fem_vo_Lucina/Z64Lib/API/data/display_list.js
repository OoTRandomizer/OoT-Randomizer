"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Display_List_Command = void 0;
const toPaddedHexString_1 = require("./toPaddedHexString");
class Display_List_Command {
    constructor(code, address, actualFileOffset) {
        this.code = toPaddedHexString_1.toPaddedHexString(code, 8).toUpperCase();
        this.address = address;
        this.actualFileOffsetCode = actualFileOffset;
        this.actualFileOffsetAddress = actualFileOffset + 4;
        this.addressAsString = toPaddedHexString_1.toPaddedHexString(this.address, 8);
        if (this.is06()) {
            this.address -= 0x06000000;
        }
        this.actualCode = code;
    }
    is06() {
        return this.addressAsString.startsWith('06');
    }
}
exports.Display_List_Command = Display_List_Command;
//# sourceMappingURL=display_list.js.map