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
const CoreInjection_1 = require("modloader64_api/CoreInjection");
const path_1 = __importDefault(require("path"));
const fs_extra_1 = __importDefault(require("fs-extra"));
const EventHandler_1 = require("modloader64_api/EventHandler");
const OotoAPI_1 = require("./OotoAPI/OotoAPI");
const zlib_1 = __importDefault(require("zlib"));
class DrAhsidVoice {
    ModLoader;
    core;
    rawSounds = {};
    preinit() {
        let sound_folder = path_1.default.resolve(__dirname, "sounds");
        fs_extra_1.default.readdirSync(sound_folder).forEach((file) => {
            let f = path_1.default.resolve(sound_folder, file);
            let id = parseInt(path_1.default.parse(file).name.split("-")[0].trim(), 16);
            if (fs_extra_1.default.lstatSync(f).isDirectory()) {
                this.rawSounds[id] = [];
                fs_extra_1.default.readdirSync(f).forEach((sound) => {
                    let s = path_1.default.resolve(f, sound);
                    this.rawSounds[id].push(zlib_1.default.deflateSync(fs_extra_1.default.readFileSync(s)));
                });
            }
        });
        EventHandler_1.bus.emit(OotoAPI_1.OotOnlineEvents.ON_LOAD_SOUND_PACK, { id: this['metadata']["name"], data: this.rawSounds });
    }
    init() {
    }
    postinit() {
    }
    onTick(frame) {
    }
}
__decorate([
    CoreInjection_1.InjectCore()
], DrAhsidVoice.prototype, "core", void 0);
module.exports = DrAhsidVoice;
//# sourceMappingURL=OotO_SoundTemplate.js.map