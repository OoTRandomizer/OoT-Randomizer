"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ModelThreadWorker = void 0;
const fs_1 = __importDefault(require("fs"));
const PakFormat_1 = require("modloader64_api/PakFormat");
const path_1 = __importDefault(require("path"));
const zzstatic_1 = require("./zzstatic");
let myArgs = process.argv.slice(2);
class ModelThreadWorker {
    constructor() { }
    work() {
        let zz = new zzstatic_1.zzstatic(0 /* OCARINA_OF_TIME */);
        let buf = fs_1.default.readFileSync(myArgs[0]);
        let cache = zz.generateCache(buf);
        let pakf = path_1.default.join(__dirname, path_1.default.parse(myArgs[0]).name + '.zzcache');
        let pak = new PakFormat_1.Pak(pakf);
        pak.save(cache);
        pak.update();
    }
}
exports.ModelThreadWorker = ModelThreadWorker;
const thread = new ModelThreadWorker();
thread.work();
//# sourceMappingURL=ModelThreadWorker.js.map