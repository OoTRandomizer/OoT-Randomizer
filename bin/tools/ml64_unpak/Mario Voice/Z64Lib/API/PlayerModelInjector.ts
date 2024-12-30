import { IModLoaderAPI, ModLoaderEvents } from 'modloader64_api/IModLoaderAPI';
import { ModLoaderAPIInject } from 'modloader64_api/ModLoaderAPIInjector';
import { EventHandler, bus, } from 'modloader64_api/EventHandler';
import fs from 'fs';
import { Z64RomTools } from './Z64RomTools';
import { RomPatch } from './RomPatch';
import { Z64LibEvents } from './Z64LibEvents';
import { Z64LibSupportedGames } from './Z64LibSupportedGames';

export class PlayerModelInjector {
    @ModLoaderAPIInject()
    ModLoader!: IModLoaderAPI;
    customModelFileAdult = '';
    customModelFileChild = '';
    customModelFileZora = '';
    customModelFileAnims = '';
    customModelRepointsAdult = __dirname + '/zobjs/adult.json';
    customModelRepointsChild = __dirname + '/zobjs/child.json';
    customModelRepointsZora = __dirname + "/zobjs/zora.json";
    dma: number;
    adult: number;
    child: number;
    zora: number;
    anims: number;
    code: number;
    child_skeleton_offset: number;
    adult_skeleton_offset: number;
    zora_skeleton_offset: number;

    constructor(game: Z64LibSupportedGames) {
        switch (game) {
            case Z64LibSupportedGames.OCARINA_OF_TIME:
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
            case Z64LibSupportedGames.MAJORAS_MASK:
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

    trimBuffer(buffer: Buffer) {
        var pos = 0
        for (var i = buffer.length - 1; i >= 0; i--) {
            if (buffer[i] !== 0x00) {
                pos = i
                break
            }
        }
        pos++;
        while (pos % 0x10 !== 0) {
            pos++;
        }
        return buffer.slice(0, pos)
    }

    loadAdultModel(evt: any, file: string) {
        let tools: Z64RomTools = new Z64RomTools(this.ModLoader, 0x7430);
        this.ModLoader.logger.info('Loading new Link model (Adult)...');
        let adult_model: Buffer = fs.readFileSync(file);
        let adult_zobj = tools.decompressFileFromRom(evt.rom, this.adult);
        this.ModLoader.utils.clearBuffer(adult_zobj);
        adult_model.copy(adult_zobj);

        let patch: RomPatch[] = new Array<RomPatch>();
        patch = JSON.parse(fs.readFileSync(this.customModelRepointsAdult).toString());
        for (let i = 0; i < patch.length; i++) {
            let buf: Buffer = tools.decompressFileFromRom(evt.rom, patch[i].index);
            for (let j = 0; j < patch[i].data.length; j++) {
                buf[patch[i].data[j].offset] = patch[i].data[j].value;
            }
            tools.recompressFileIntoRom(evt.rom, patch[i].index, buf);
        }
        let code_file: Buffer = tools.decompressFileFromRom(evt.rom, this.code);
        adult_zobj.writeUInt32BE(code_file.readUInt32BE(this.adult_skeleton_offset), 0x500c);
        tools.recompressFileIntoRom(evt.rom, this.adult, adult_zobj);
    }

    loadChildModel(evt: any, file: string) {
        let tools: Z64RomTools = new Z64RomTools(this.ModLoader, this.dma);
        this.ModLoader.logger.info('Loading new Link model (Child)...');
        let child_model: Buffer = fs.readFileSync(file);

        let child_zobj = tools.decompressFileFromRom(evt.rom, this.child);
        this.ModLoader.utils.clearBuffer(child_zobj);
        child_model.copy(child_zobj);

        let patch: RomPatch[] = new Array<RomPatch>();
        patch = JSON.parse(fs.readFileSync(this.customModelRepointsChild).toString());
        for (let i = 0; i < patch.length; i++) {
            let buf: Buffer = tools.decompressFileFromRom(evt.rom, patch[i].index);
            for (let j = 0; j < patch[i].data.length; j++) {
                buf[patch[i].data[j].offset] = patch[i].data[j].value;
            }
            tools.recompressFileIntoRom(evt.rom, patch[i].index, buf);
        }

        let code_file: Buffer = tools.decompressFileFromRom(evt.rom, this.code);
        child_zobj.writeUInt32BE(code_file.readUInt32BE(this.child_skeleton_offset), 0x500c);
        tools.recompressFileIntoRom(evt.rom, this.child, child_zobj);
    }

    loadZoraModel(evt: any, file: string) {
        let tools: Z64RomTools = new Z64RomTools(this.ModLoader, this.dma);
        this.ModLoader.logger.info('Loading new Link model (Zora)...');
        let zora_model: Buffer = fs.readFileSync(file);

        let zora_zobj = tools.decompressFileFromRom(evt.rom, this.zora);
        this.ModLoader.utils.clearBuffer(zora_zobj);
        zora_model.copy(zora_zobj);

        let patch: RomPatch[] = new Array<RomPatch>();
        patch = JSON.parse(fs.readFileSync(this.customModelRepointsZora).toString());
        for (let i = 0; i < patch.length; i++) {
            let buf: Buffer = tools.decompressFileFromRom(evt.rom, patch[i].index);
            for (let j = 0; j < patch[i].data.length; j++) {
                buf[patch[i].data[j].offset] = patch[i].data[j].value;
            }
            tools.recompressFileIntoRom(evt.rom, patch[i].index, buf);
        }

        let code_file: Buffer = tools.decompressFileFromRom(evt.rom, this.code);
        zora_zobj.writeUInt32BE(code_file.readUInt32BE(this.zora_skeleton_offset), 0x500c);
        tools.recompressFileIntoRom(evt.rom, this.zora, zora_zobj);
    }

    loadAnims(evt: any, file: string) {
        let tools: Z64RomTools = new Z64RomTools(this.ModLoader, this.dma);
        let anims: Buffer = tools.decompressFileFromRom(evt, this.anims);
        this.ModLoader.utils.clearBuffer(anims);
        let data: Buffer = fs.readFileSync(file);
        bus.emit(Z64LibEvents.ANIM_FILE_PRELOAD, data);
        data.copy(anims);
        tools.recompressFileIntoRom(evt, this.anims, anims);
        bus.emit(Z64LibEvents.ANIM_FILE_POSTLOAD, anims);
    }

    @EventHandler(ModLoaderEvents.ON_ROM_PATCHED)
    onRomPatched(evt: any) {
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
