import { fork, ForkOptions } from 'child_process';
import path from 'path';
import fs from 'fs';
import { IModLoaderAPI } from 'modloader64_api/IModLoaderAPI';
import { Pak } from 'modloader64_api/PakFormat';
import { zzstatic_cache, zzstatic } from './zzstatic';
import { Z64LibSupportedGames } from './Z64LibSupportedGames';

export class ModelThread {
  model: Buffer;
  child: any;
  ModLoader: IModLoaderAPI;

  constructor(model: Buffer, ModLoader: IModLoaderAPI) {
    this.model = model;
    this.ModLoader = ModLoader;
  }

  startThread() {
    console.log('Starting worker thread for custom model.');
    const options = {
      stdio: ['pipe', 'pipe', 'pipe', 'ipc'],
    };
    let filename: string =
      this.ModLoader.utils.hashBuffer(this.model) + '.zobj';
    filename = path.join(__dirname, filename);
    fs.writeFileSync(filename, this.model);
    this.child = fork(
      path.resolve(path.join(__dirname, 'ModelThreadWorker.js')),
      [filename],
      options as ForkOptions
    );
    this.child.on('exit', (code: any, signal: any) => {
      let dest: string = path.join(
        __dirname,
        path.parse(filename).name + '.zzcache'
      );
      let pak: Pak = new Pak(dest);
      let cache: zzstatic_cache = JSON.parse(pak.load(0).toString());
      let zz: zzstatic = new zzstatic(Z64LibSupportedGames.OCARINA_OF_TIME);
      zz.addToCache(cache);
      console.log('Worker thread ended.');
    });
  }
}
