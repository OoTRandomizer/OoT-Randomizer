"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.PlayerModelInjector = void 0;
const IModLoaderAPI_1 = require("modloader64_api/IModLoaderAPI");
const ModLoaderAPIInjector_1 = require("modloader64_api/ModLoaderAPIInjector");
const EventHandler_1 = require("modloader64_api/EventHandler");
const fs_1 = __importDefault(require("fs"));
const Z64RomTools_1 = require("./Z64RomTools");
class PlayerModelInjector {
    constructor(game) {
        this.customModelFileAdult = '';
        this.customModelFileChild = '';
        this.customModelFileZora = '';
        this.customModelFileAnims = '';
        this.customModelRepointsAdult = __dirname + '/zobjs/adult.json';
        this.customModelRepointsChild = __dirname + '/zobjs/child.json';
        this.customModelRepointsZora = __dirname + "/zobjs/zora.json";
        switch (game) {
            case 0 /* OCARINA_OF_TIME */:
                this.dma = 0x7430;
                this.anims = 7;
                this.adult = 502;
                this.child = 503;
                this.code = 27;
                this.zora = -1;
                this.adult_skeleton_offset = 0xe65a0;
                this.child_skeleton_offset = this.adult_skeleton_offset + 0x4;
                this.zora_skeleton_offset = -1;
                break;
            case 1 /* MAJORAS_MASK */:
                this.dma = 0x1A500;
                this.anims = 730;
                this.adult = -1;
                this.child = 654;
                this.code = 31;
                this.zora = 656;
                this.adult_skeleton_offset = -1;
                this.child_skeleton_offset = 0x11A350;
                this.zora_skeleton_offset = 0x11A348;
                break;
        }
    }
    trimBuffer(buffer) {
        var pos = 0;
        for (var i = buffer.length - 1; i >= 0; i--) {
            if (buffer[i] !== 0x00) {
                pos = i;
                break;
            }
        }
        pos++;
        while (pos % 0x10 !== 0) {
            pos++;
        }
        return buffer.slice(0, pos);
    }
    loadAdultModel(evt, file) {
        let tools = new Z64RomTools_1.Z64RomTools(this.ModLoader, 0x7430);
        this.ModLoader.logger.info('Loading new Link model (Adult)...');
        let adult_model = fs_1.default.readFileSync(file);
        let adult_zobj = tools.decompressFileFromRom(evt.rom, this.adult);
        this.ModLoader.utils.clearBuffer(adult_zobj);
        adult_model.copy(adult_zobj);
        let patch = new Array();
        patch = JSON.parse(fs_1.default.readFileSync(this.customModelRepointsAdult).toString());
        for (let i = 0; i < patch.length; i++) {
            let buf = tools.decompressFileFromRom(evt.rom, patch[i].index);
            for (let j = 0; j < patch[i].data.length; j++) {
                buf[patch[i].data[j].offset] = patch[i].data[j].value;
            }
            tools.recompressFileIntoRom(evt.rom, patch[i].index, buf);
        }
        let code_file = tools.decompressFileFromRom(evt.rom, this.code);
        adult_zobj.writeUInt32BE(code_file.readUInt32BE(this.adult_skeleton_offset), 0x500c);
        tools.recompressFileIntoRom(evt.rom, this.adult, adult_zobj);
    }
    loadChildModel(evt, file) {
        let tools = new Z64RomTools_1.Z64RomTools(this.ModLoader, this.dma);
        this.ModLoader.logger.info('Loading new Link model (Child)...');
        let child_model = fs_1.default.readFileSync(file);
        let child_zobj = tools.decompressFileFromRom(evt.rom, this.child);
        this.ModLoader.utils.clearBuffer(child_zobj);
        child_model.copy(child_zobj);
        let patch = new Array();
        patch = JSON.parse(fs_1.default.readFileSync(this.customModelRepointsChild).toString());
        for (let i = 0; i < patch.length; i++) {
            let buf = tools.decompressFileFromRom(evt.rom, patch[i].index);
            for (let j = 0; j < patch[i].data.length; j++) {
                buf[patch[i].data[j].offset] = patch[i].data[j].value;
            }
            tools.recompressFileIntoRom(evt.rom, patch[i].index, buf);
        }
        let code_file = tools.decompressFileFromRom(evt.rom, this.code);
        child_zobj.writeUInt32BE(code_file.readUInt32BE(this.child_skeleton_offset), 0x500c);
        tools.recompressFileIntoRom(evt.rom, this.child, child_zobj);
    }
    loadZoraModel(evt, file) {
        let tools = new Z64RomTools_1.Z64RomTools(this.ModLoader, this.dma);
        this.ModLoader.logger.info('Loading new Link model (Zora)...');
        let zora_model = fs_1.default.readFileSync(file);
        let zora_zobj = tools.decompressFileFromRom(evt.rom, this.zora);
        this.ModLoader.utils.clearBuffer(zora_zobj);
        zora_model.copy(zora_zobj);
        let patch = new Array();
        patch = JSON.parse(fs_1.default.readFileSync(this.customModelRepointsZora).toString());
        for (let i = 0; i < patch.length; i++) {
            let buf = tools.decompressFileFromRom(evt.rom, patch[i].index);
            for (let j = 0; j < patch[i].data.length; j++) {
                buf[patch[i].data[j].offset] = patch[i].data[j].value;
            }
            tools.recompressFileIntoRom(evt.rom, patch[i].index, buf);
        }
        let code_file = tools.decompressFileFromRom(evt.rom, this.code);
        zora_zobj.writeUInt32BE(code_file.readUInt32BE(this.zora_skeleton_offset), 0x500c);
        tools.recompressFileIntoRom(evt.rom, this.zora, zora_zobj);
    }
    loadAnims(evt, file) {
        let tools = new Z64RomTools_1.Z64RomTools(this.ModLoader, this.dma);
        let anims = tools.decompressFileFromRom(evt, this.anims);
        this.ModLoader.utils.clearBuffer(anims);
        let data = fs_1.default.readFileSync(file);
        EventHandler_1.bus.emit("ANIM_FILE_PRELOAD" /* ANIM_FILE_PRELOAD */, data);
        data.copy(anims);
        tools.recompressFileIntoRom(evt, this.anims, anims);
        EventHandler_1.bus.emit("ANIM_FILE_POSTLOAD" /* ANIM_FILE_POSTLOAD */, anims);
    }
    onRomPatched(evt) {
        this.ModLoader.logger.info('Starting custom model setup...');
        if (this.customModelFileAdult !== '') {
            this.loadAdultModel(evt, this.customModelFileAdult);
        }
        if (this.customModelFileChild !== '') {
            this.loadChildModel(evt, this.customModelFileChild);
        }
        if (this.customModelFileZora !== '') {
            this.loadZoraModel(evt, this.customModelFileZora);
        }
        if (this.customModelFileAnims !== '') {
            this.loadAnims(evt, this.customModelFileAnims);
        }
        this.ModLoader.logger.info('Done.');
    }
}
__decorate([
    ModLoaderAPIInjector_1.ModLoaderAPIInject()
], PlayerModelInjector.prototype, "ModLoader", void 0);
__decorate([
    EventHandler_1.EventHandler(IModLoaderAPI_1.ModLoaderEvents.ON_ROM_PATCHED)
], PlayerModelInjector.prototype, "onRomPatched", null);
exports.PlayerModelInjector = PlayerModelInjector;
//# sourceMappingURL=PlayerModelInjector.js.map