"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.zzstatic = exports.zzstatic_cache = void 0;
const zobj_1 = require("./data/zobj");
const display_list_1 = require("./data/display_list");
const skeleton_1 = require("./data/skeleton");
const skeleton_entry_1 = require("./data/skeleton_entry");
const crypto_1 = __importDefault(require("crypto"));
const ZZSTATIC_CACHE_DATA = new Map();
class zzstatic_cache {
    constructor() {
        this.cache = new Array();
    }
    doRepoint(index, buf, rebase = 0x80800000) {
        let copy = Buffer.alloc(buf.byteLength);
        buf.copy(copy);
        //console.log('Loading ' + this.cache.length + ' repoints from cache.');
        let header_start = copy.indexOf(Buffer.from("MODLOADER64"));
        let modeByte = copy.readUInt8(header_start + 0xB);
        rebase += index * 0x37800;
        for (let i = 0; i < this.cache.length; i++) {
            try {
                copy.writeUInt32BE(rebase + this.cache[i].address, this.cache[i].actualFileOffsetAddress);
            }
            catch (err) {
                //console.log('Recorded an error!');
                continue;
            }
        }
        if (modeByte !== 0x69) {
            let pointer_to_skeleton_pointer = copy.readUInt32BE(0x500c) - 0x06000000;
            let pointer_to_skeleton = copy.readUInt32BE(pointer_to_skeleton_pointer) - 0x06000000;
            copy.writeUInt32BE(pointer_to_skeleton + rebase, pointer_to_skeleton_pointer);
            copy.writeUInt32BE(pointer_to_skeleton_pointer + rebase, 0x500c);
            for (let i = 0; i < this.skeleton.bones.length; i++) {
                copy.writeUInt32BE(this.skeleton.bones[i].pointer + rebase, this.skeleton.bones[i].actualFileOffset);
            }
        }
        //console.log('Repoint done');
        return copy;
    }
}
exports.zzstatic_cache = zzstatic_cache;
class zzstatic {
    constructor(game) {
        this.game = game;
    }
    addToCache(c) {
        let cache = new zzstatic_cache();
        cache.cache = c.cache;
        cache.skeleton = c.skeleton;
        ZZSTATIC_CACHE_DATA.set(c.hash, cache);
    }
    generateCache(buf) {
        let hash = crypto_1.default
            .createHash('md5')
            .update(buf)
            .digest('hex');
        this.doRepoint(buf, 0);
        return ZZSTATIC_CACHE_DATA.get(hash);
    }
    doRepoint(buf, index, cache = true, rebase = 0x80800000) {
        let copy = Buffer.alloc(buf.byteLength);
        buf.copy(copy);
        let zobj = new zobj_1.Zobj(buf);
        let r = rebase + (index * 0x37800);
        //console.log(r.toString(16));
        let zzCache = new zzstatic_cache();
        let hash = crypto_1.default
            .createHash('md5')
            .update(buf)
            .digest('hex');
        if (ZZSTATIC_CACHE_DATA.has(hash)) {
            return ZZSTATIC_CACHE_DATA.get(hash).doRepoint(index, buf, rebase);
        }
        let ALIAS_TABLE_START = 0x5090;
        let ALIAS_TABLE_END = 0x5380;
        let header_start = zobj.buf.indexOf(Buffer.from("MODLOADER64"));
        let modeByte = zobj.buf.readUInt8(header_start + 0xB);
        if (this.game === 0 /* OCARINA_OF_TIME */) {
            if (modeByte === 0x0) {
                //console.log('This is an adult ZOBJ.');
            }
            else if (modeByte === 0x1) {
                ALIAS_TABLE_START = 0x50d0;
                ALIAS_TABLE_END = 0x53A8;
                //console.log('This is a child ZOBJ.');
            }
            else if (modeByte === 0x69) {
                //console.log("This is an equipment ZOBJ.");
                ALIAS_TABLE_START = 0x10;
                ALIAS_TABLE_END = 0x300;
            }
        }
        else if (this.game === 1 /* MAJORAS_MASK */) {
            // FD
            switch (modeByte) {
                case 0:
                    ALIAS_TABLE_START = 0x5010;
                    ALIAS_TABLE_END = 0X5018;
                    break;
                case 1:
                    ALIAS_TABLE_START = 0x5010;
                    ALIAS_TABLE_END = 0x5090;
                    break;
                case 2:
                    ALIAS_TABLE_START = 0x5010;
                    ALIAS_TABLE_END = 0x50A0;
                    break;
                case 3:
                    ALIAS_TABLE_START = 0x5010;
                    ALIAS_TABLE_END = 0x50C8;
                    break;
                case 4:
                    ALIAS_TABLE_START = 0x5110;
                    ALIAS_TABLE_END = 0x5418;
                    break;
            }
        }
        //console.log('Extracting alias table...');
        let alias_table = zobj.buf.slice(ALIAS_TABLE_START, ALIAS_TABLE_END);
        let commands = new Array();
        for (let i = 0; i < alias_table.byteLength; i += 8) {
            commands.push(new display_list_1.Display_List_Command(alias_table.readUInt32BE(i), alias_table.readUInt32BE(i + 0x4), ALIAS_TABLE_START + i));
        }
        //console.log('Found ' + commands.length + ' total things in the alias table.');
        let traverse = new Array();
        function manualTraversal(dl) {
            let test = '';
            let cur = dl.actualFileOffsetCode;
            while (!test.startsWith('DF') && !test.startsWith('DE01')) {
                let ndl = new display_list_1.Display_List_Command(zobj.buf.readUInt32BE(cur), zobj.buf.readUInt32BE(cur + 4), cur);
                traverse.push(ndl);
                test = ndl.code;
                cur += 8;
            }
            traverse.push(dl);
        }
        function traverseDisplayList(dl) {
            if (dl.code.startsWith('DE') && dl.is06()) {
                // Jump
                let test = '';
                let cur = dl.address;
                console.log("Jumping to " + dl.code + " at position " + dl.actualFileOffsetCode.toString(16) + " to " + dl.address.toString(16));
                while (!test.startsWith('DF') && !test.startsWith('DE01')) {
                    let ndl = new display_list_1.Display_List_Command(zobj.buf.readUInt32BE(cur), zobj.buf.readUInt32BE(cur + 4), cur);
                    traverseDisplayList(ndl);
                    test = ndl.code;
                    cur += 8;
                }
                console.log("Exiting display list due to DF or DE01");
            }
            else {
                //console.log(dl.code + " at position " + dl.actualFileOffsetCode.toString(16) + " is not a jump. Add to traversal pool.")
            }
            traverse.push(dl);
        }
        for (let i = 0; i < commands.length; i++) {
            traverseDisplayList(commands[i]);
        }
        console.log('Found ' + traverse.length + ' traversable nodes.');
        let repoints = new Array();
        function lookForRepoints() {
            for (let i = 0; i < traverse.length; i++) {
                let dl = traverse[i];
                if (dl.code.startsWith('DE') ||
                    dl.code.startsWith('01') ||
                    dl.code.startsWith('FD') ||
                    dl.code.startsWith('DA')) {
                    if (dl.is06()) {
                        repoints.push(dl);
                    }
                }
            }
        }
        lookForRepoints();
        if (modeByte !== 0x69) {
            let pointer_to_skeleton_pointer = zobj.buf.readUInt32BE(0x500c) - 0x06000000;
            let pointer_to_skeleton = zobj.buf.readUInt32BE(pointer_to_skeleton_pointer) - 0x06000000;
            console.log('Looking in the closet...');
            let dem_bones = zobj.buf.readUInt8(pointer_to_skeleton_pointer + 0x4);
            let spooky_scary = new skeleton_1.Skeleton(dem_bones);
            console.log('Found a skeleton with ' + dem_bones + ' bones.');
            for (let i = 0; i < spooky_scary.total; i++) {
                spooky_scary.bones.push(new skeleton_entry_1.Skeleton_Entry(zobj.buf.readUInt32BE(pointer_to_skeleton + 4 * i) - 0x06000000, pointer_to_skeleton + 4 * i));
            }
            for (let i = 0; i < spooky_scary.bones.length; i++) {
                let lookingForFF = '';
                let cur = spooky_scary.bones[i].pointer;
                let dl = new display_list_1.Display_List_Command(0xdeadbeef, zobj.buf.readUInt32BE(cur + 0xc), cur + 0xc - 0x4);
                if (dl.is06()) {
                    repoints.push(dl);
                }
                let dl2 = new display_list_1.Display_List_Command(0xdeadbeef, zobj.buf.readUInt32BE(cur + 0x8), cur + 0x8 - 0x4);
                if (dl2.is06()) {
                    repoints.push(dl2);
                }
                lookingForFF = zobj.buf
                    .readUInt8(cur + 0x6)
                    .toString(16)
                    .toUpperCase();
                cur += 0x10;
                while (lookingForFF !== 'FF') {
                    let dl = new display_list_1.Display_List_Command(0xdeadbeef, zobj.buf.readUInt32BE(cur + 0xc), cur + 0xc - 0x4);
                    if (dl.is06()) {
                        repoints.push(dl);
                    }
                    let dl2 = new display_list_1.Display_List_Command(0xdeadbeef, zobj.buf.readUInt32BE(cur + 0x8), cur + 0x8 - 0x4);
                    if (dl2.is06()) {
                        repoints.push(dl2);
                    }
                    lookingForFF = zobj.buf
                        .readUInt8(cur + 0x6)
                        .toString(16)
                        .toUpperCase();
                    cur += 0x10;
                }
                zobj.buf.writeUInt32BE(spooky_scary.bones[i].pointer + r, spooky_scary.bones[i].actualFileOffset);
            }
            let after_bones = spooky_scary.bones[dem_bones - 1].actualFileOffset + 0x4;
            repoints.push(new display_list_1.Display_List_Command(0xdeadbeef, zobj.buf.readUInt32BE(after_bones), after_bones - 0x4));
            zobj.buf.writeUInt32BE(pointer_to_skeleton + r, pointer_to_skeleton_pointer);
            zobj.buf.writeUInt32BE(pointer_to_skeleton_pointer + r, 0x500c);
            zzCache.skeleton = spooky_scary;
        }
        function doRepoints() {
            console.log('Found ' + repoints.length + ' things in need of a repoint.');
            for (let i = 0; i < repoints.length; i++) {
                try {
                    zobj.buf.writeUInt32BE(r + repoints[i].address, repoints[i].actualFileOffsetAddress);
                    zzCache.cache.push(repoints[i]);
                }
                catch (err) {
                    console.log('Recorded an error!');
                    continue;
                }
            }
            repoints.length = 0;
        }
        doRepoints();
        repoints.length = 0;
        traverse.length = 0;
        for (let i = 0; i < zobj.buf.byteLength; i += 8) {
            let word = zobj.buf.readUInt32BE(i);
            let addr = zobj.buf.readUInt32BE(i + 4);
            let dl = new display_list_1.Display_List_Command(word, addr, i);
            if (dl.code === 'E7000000' && dl.addressAsString === '00000000') {
                manualTraversal(dl);
            }
        }
        lookForRepoints();
        doRepoints();
        hash = crypto_1.default
            .createHash('md5')
            .update(copy)
            .digest('hex');
        zzCache.hash = hash;
        if (cache) {
            ZZSTATIC_CACHE_DATA.set(hash, zzCache);
        }
        console.log('Done!');
        return zobj.buf;
    }
}
exports.zzstatic = zzstatic;
//# sourceMappingURL=zzstatic.js.map