import { IModLoaderAPI } from "modloader64_api/IModLoaderAPI";
import fs from 'fs';
import path from 'path';
import { RomPatch } from "./RomPatch";
import { FilePatch } from "./FilePatch";
import { Z64RomTools } from "./Z64RomTools";
import { Z64LibSupportedGames } from "./Z64LibSupportedGames";

export class FileSystemCompare {

    ModLoader: IModLoaderAPI;
    dma: number;
    total: number;
    adult: number;
    child: number;
    zora: number;
    startat: number;

    constructor(ModLoader: IModLoaderAPI, game: Z64LibSupportedGames) {
        this.ModLoader = ModLoader;
        switch (game) {
            case Z64LibSupportedGames.OCARINA_OF_TIME:
                this.dma = 0x7430
                this.total = 1509;
                this.adult = 502;
                this.child = 503;
                this.startat = 3;
                this.zora = -1;
                break;
            case Z64LibSupportedGames.MAJORAS_MASK:
                this.dma = 0x1A500;
                this.total = 1551;
                this.adult = -1;
                this.child = 654;
                this.startat = 31;
                this.zora = 656;
                break;
        }
    }

    dumpVanilla(rom: Buffer) {
        let tools: Z64RomTools = new Z64RomTools(this.ModLoader, this.dma);
        let target: string = "./vanilla";
        if (!fs.existsSync(target)) {
            fs.mkdirSync(target);
        }
        for (let i = this.startat; i < this.total; i++) {
            console.log(i);
            let buf: Buffer = tools.decompressFileFromRom(rom, i);
            fs.writeFileSync(path.join(target, i + ".bin"), buf);
        }
    }

    dumpDirty(rom: Buffer) {
        let tools: Z64RomTools = new Z64RomTools(this.ModLoader, this.dma);
        let target: string = "./dirty";
        if (!fs.existsSync(target)) {
            fs.mkdirSync(target);
        }
        for (let i = this.startat; i < this.total; i++) {
            console.log(i);
            let buf: Buffer = tools.decompressFileFromRom(rom, i);
            fs.writeFileSync(path.join(target, i + ".bin"), buf);
        }
    }

    compare() {
        let v: string = "./vanilla";
        let d: string = "./dirty";
        let dest: string = "./patches";
        if (!fs.existsSync(dest)) {
            fs.mkdirSync(dest);
        }
        let total: number = 1509;
        let patches: any = {};
        for (let i = this.startat; i < total; i++) {
            if (i === this.adult || i === this.child || i === this.zora) {
                continue;
            }
            let buf1: Buffer = fs.readFileSync(path.join(v, i + ".bin"));
            let buf2: Buffer = fs.readFileSync(path.join(d, i + ".bin"));
            for (let j = 0; j < buf1.byteLength; j++) {
                if (buf1[j] !== buf2[j]) {
                    if (!patches.hasOwnProperty(i)) {
                        patches[i] = new RomPatch(i);
                        console.log(i);
                    }
                    (patches[i] as RomPatch).data.push(new FilePatch(j, buf2[j]));
                }
            }
        }
        let rp: RomPatch[] = [];
        Object.keys(patches).forEach((key: string) => {
            rp.push(patches[key]);
        });
        fs.writeFileSync(path.join(dest, "out.json"), JSON.stringify(rp, null, 2));
    }
}