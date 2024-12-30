"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.FileSystemCompare = void 0;
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const RomPatch_1 = require("./RomPatch");
const FilePatch_1 = require("./FilePatch");
const Z64RomTools_1 = require("./Z64RomTools");
class FileSystemCompare {
    constructor(ModLoader, game) {
        this.ModLoader = ModLoader;
        switch (game) {
            case 0 /* OCARINA_OF_TIME */:
                this.dma = 0x7430;
                this.total = 1509;
                this.adult = 502;
                this.child = 503;
                this.startat = 3;
                this.zora = -1;
                break;
            case 1 /* MAJORAS_MASK */:
                this.dma = 0x1A500;
                this.total = 1551;
                this.adult = -1;
                this.child = 654;
                this.startat = 31;
                this.zora = 656;
                break;
        }
    }
    dumpVanilla(rom) {
        let tools = new Z64RomTools_1.Z64RomTools(this.ModLoader, this.dma);
        let target = "./vanilla";
        if (!fs_1.default.existsSync(target)) {
            fs_1.default.mkdirSync(target);
        }
        for (let i = this.startat; i < this.total; i++) {
            console.log(i);
            let buf = tools.decompressFileFromRom(rom, i);
            fs_1.default.writeFileSync(path_1.default.join(target, i + ".bin"), buf);
        }
    }
    dumpDirty(rom) {
        let tools = new Z64RomTools_1.Z64RomTools(this.ModLoader, this.dma);
        let target = "./dirty";
        if (!fs_1.default.existsSync(target)) {
            fs_1.default.mkdirSync(target);
        }
        for (let i = this.startat; i < this.total; i++) {
            console.log(i);
            let buf = tools.decompressFileFromRom(rom, i);
            fs_1.default.writeFileSync(path_1.default.join(target, i + ".bin"), buf);
        }
    }
    compare() {
        let v = "./vanilla";
        let d = "./dirty";
        let dest = "./patches";
        if (!fs_1.default.existsSync(dest)) {
            fs_1.default.mkdirSync(dest);
        }
        let total = 1509;
        let patches = {};
        for (let i = this.startat; i < total; i++) {
            if (i === this.adult || i === this.child || i === this.zora) {
                continue;
            }
            let buf1 = fs_1.default.readFileSync(path_1.default.join(v, i + ".bin"));
            let buf2 = fs_1.default.readFileSync(path_1.default.join(d, i + ".bin"));
            for (let j = 0; j < buf1.byteLength; j++) {
                if (buf1[j] !== buf2[j]) {
                    if (!patches.hasOwnProperty(i)) {
                        patches[i] = new RomPatch_1.RomPatch(i);
                        console.log(i);
                    }
                    patches[i].data.push(new FilePatch_1.FilePatch(j, buf2[j]));
                }
            }
        }
        let rp = [];
        Object.keys(patches).forEach((key) => {
            rp.push(patches[key]);
        });
        fs_1.default.writeFileSync(path_1.default.join(dest, "out.json"), JSON.stringify(rp, null, 2));
    }
}
exports.FileSystemCompare = FileSystemCompare;
//# sourceMappingURL=FileSystemCompare.js.map