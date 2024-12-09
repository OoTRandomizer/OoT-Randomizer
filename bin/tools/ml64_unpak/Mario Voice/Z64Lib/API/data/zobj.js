"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Zobj = void 0;
class Zobj {
    constructor(buf) {
        this.buf = buf;
    }
    cloneBuffer() {
        let copy = Buffer.alloc(this.buf.byteLength);
        this.buf.copy(copy);
        return copy;
    }
    isModLoaderZobj() {
        let b = this.buf.slice(0x5000, 0x500b);
        return b.toString() === 'MODLOADER64';
    }
}
exports.Zobj = Zobj;
//# sourceMappingURL=zobj.js.map