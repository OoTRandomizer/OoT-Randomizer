"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ModelThread = void 0;
const child_process_1 = require("child_process");
const path_1 = __importDefault(require("path"));
const fs_1 = __importDefault(require("fs"));
const PakFormat_1 = require("modloader64_api/PakFormat");
const zzstatic_1 = require("./zzstatic");
class ModelThread {
    constructor(model, ModLoader) {
        this.model = model;
        this.ModLoader = ModLoader;
    }
    startThread() {
        console.log('Starting worker thread for custom model.');
        const options = {
            stdio: ['pipe', 'pipe', 'pipe', 'ipc'],
        };
        let filename = this.ModLoader.utils.hashBuffer(this.model) + '.zobj';
        filename = path_1.default.join(__dirname, filename);
        fs_1.default.writeFileSync(filename, this.model);
        this.child = child_process_1.fork(path_1.default.resolve(path_1.default.join(__dirname, 'ModelThreadWorker.js')), [filename], options);
        this.child.on('exit', (code, signal) => {
            let dest = path_1.default.join(__dirname, path_1.default.parse(filename).name + '.zzcache');
            let pak = new PakFormat_1.Pak(dest);
            let cache = JSON.parse(pak.load(0).toString());
            let zz = new zzstatic_1.zzstatic(0 /* OCARINA_OF_TIME */);
            zz.addToCache(cache);
            console.log('Worker thread ended.');
        });
    }
}
exports.ModelThread = ModelThread;
//# sourceMappingURL=ModelThread.js.map