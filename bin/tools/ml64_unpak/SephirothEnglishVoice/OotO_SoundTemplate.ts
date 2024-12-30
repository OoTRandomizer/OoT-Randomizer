import { IPlugin, IModLoaderAPI } from 'modloader64_api/IModLoaderAPI';
import { IOOTCore } from 'modloader64_api/OOT/OOTAPI';
import { InjectCore } from 'modloader64_api/CoreInjection';
import path from 'path';
import fs from 'fs-extra';
import { bus } from 'modloader64_api/EventHandler';
import { OotOnlineEvents } from './OotoAPI/OotoAPI';
import zlib from 'zlib';

class DrAhsidVoice implements IPlugin {

    ModLoader!: IModLoaderAPI;
    @InjectCore()
    core!: IOOTCore;
    rawSounds: any = {};

    preinit(): void {
        let sound_folder: string = path.resolve(__dirname, "sounds");
        fs.readdirSync(sound_folder).forEach((file: string) => {
            let f: string = path.resolve(sound_folder, file);
            let id: number = parseInt(path.parse(file).name.split("-")[0].trim(), 16);
            if (fs.lstatSync(f).isDirectory()) {
                this.rawSounds[id] = [];
                fs.readdirSync(f).forEach((sound: string) => {
                    let s: string = path.resolve(f, sound);
                    this.rawSounds[id].push(zlib.deflateSync(fs.readFileSync(s)));
                });
            }
        });
        bus.emit(OotOnlineEvents.ON_LOAD_SOUND_PACK, {id: (this as any)['metadata']["name"], data: this.rawSounds});
    }

    init(): void {
    }

    postinit(): void {
    }

    onTick(frame?: number | undefined): void {
    }

}

module.exports = DrAhsidVoice;