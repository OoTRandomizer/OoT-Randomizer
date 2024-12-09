import { Zobj } from './data/zobj';
import { Display_List_Command } from './data/display_list';
import { Skeleton } from './data/skeleton';
import { Skeleton_Entry } from './data/skeleton_entry';
import crypto from 'crypto';
import { Z64LibSupportedGames } from './Z64LibSupportedGames';

const ZZSTATIC_CACHE_DATA: Map<string, zzstatic_cache> = new Map<
  string,
  zzstatic_cache
>();

export class zzstatic_cache {
  cache: Display_List_Command[] = new Array<Display_List_Command>();
  skeleton!: Skeleton;
  hash!: string;

  doRepoint(index: number, buf: Buffer, rebase = 0x80800000): Buffer {
    let copy: Buffer = Buffer.alloc(buf.byteLength);
    buf.copy(copy);
    //console.log('Loading ' + this.cache.length + ' repoints from cache.');
    let header_start: number = copy.indexOf(Buffer.from("MODLOADER64"));
    let modeByte: number = copy.readUInt8(header_start + 0xB);
    rebase += index * 0x37800;
    for (let i = 0; i < this.cache.length; i++) {
      try {
        copy.writeUInt32BE(
          rebase + this.cache[i].address,
          this.cache[i].actualFileOffsetAddress
        );
      } catch (err) {
        //console.log('Recorded an error!');
        continue;
      }
    }
    if (modeByte !== 0x69) {
      let pointer_to_skeleton_pointer: number =
        copy.readUInt32BE(0x500c) - 0x06000000;
      let pointer_to_skeleton: number =
        copy.readUInt32BE(pointer_to_skeleton_pointer) - 0x06000000;
      copy.writeUInt32BE(
        pointer_to_skeleton + rebase,
        pointer_to_skeleton_pointer
      );
      copy.writeUInt32BE(pointer_to_skeleton_pointer + rebase, 0x500c);
      for (let i = 0; i < this.skeleton.bones.length; i++) {
        copy.writeUInt32BE(
          this.skeleton.bones[i].pointer + rebase,
          this.skeleton.bones[i].actualFileOffset
        );
      }
    }
    //console.log('Repoint done');
    return copy;
  }
}

export class zzstatic {

  game: Z64LibSupportedGames;

  constructor(game: Z64LibSupportedGames) {
    this.game = game;
  }

  addToCache(c: zzstatic_cache) {
    let cache = new zzstatic_cache();
    cache.cache = c.cache;
    cache.skeleton = c.skeleton;
    ZZSTATIC_CACHE_DATA.set(c.hash, cache);
  }

  generateCache(buf: Buffer): zzstatic_cache {
    let hash: string = crypto
      .createHash('md5')
      .update(buf)
      .digest('hex');
    this.doRepoint(buf, 0);
    return ZZSTATIC_CACHE_DATA.get(hash) as zzstatic_cache;
  }

  doRepoint(buf: Buffer, index: number, cache = true, rebase = 0x80800000): Buffer {
    let copy: Buffer = Buffer.alloc(buf.byteLength);
    buf.copy(copy);
    let zobj: Zobj = new Zobj(buf);
    let r = rebase + (index * 0x37800);

    //console.log(r.toString(16));

    let zzCache: zzstatic_cache = new zzstatic_cache();

    let hash: string = crypto
      .createHash('md5')
      .update(buf)
      .digest('hex');

    if (ZZSTATIC_CACHE_DATA.has(hash)) {
      return ZZSTATIC_CACHE_DATA.get(hash)!.doRepoint(index, buf, rebase);
    }

    let ALIAS_TABLE_START = 0x5090;
    let ALIAS_TABLE_END = 0x5380;

    let header_start: number = zobj.buf.indexOf(Buffer.from("MODLOADER64"));

    let modeByte: number = zobj.buf.readUInt8(header_start + 0xB);

    if (this.game === Z64LibSupportedGames.OCARINA_OF_TIME) {
      if (modeByte === 0x0) {
        //console.log('This is an adult ZOBJ.');
      } else if (modeByte === 0x1) {
        ALIAS_TABLE_START = 0x50d0;
        ALIAS_TABLE_END = 0x53A8;
        //console.log('This is a child ZOBJ.');
      } else if (modeByte === 0x69) {
        //console.log("This is an equipment ZOBJ.");
        ALIAS_TABLE_START = 0x10;
        ALIAS_TABLE_END = 0x300;
      }
    } else if (this.game === Z64LibSupportedGames.MAJORAS_MASK) {
      // FD
      switch (modeByte) {
        case 0:
          ALIAS_TABLE_START = 0x5010;
          ALIAS_TABLE_END = 0X5018
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

    let alias_table: Buffer = zobj.buf.slice(
      ALIAS_TABLE_START,
      ALIAS_TABLE_END
    );
    let commands: Display_List_Command[] = new Array<Display_List_Command>();

    for (let i = 0; i < alias_table.byteLength; i += 8) {
      commands.push(
        new Display_List_Command(
          alias_table.readUInt32BE(i),
          alias_table.readUInt32BE(i + 0x4),
          ALIAS_TABLE_START + i
        )
      );
    }

    //console.log('Found ' + commands.length + ' total things in the alias table.');

    let traverse: Display_List_Command[] = new Array<Display_List_Command>();

    function manualTraversal(dl: Display_List_Command) {
      let test = '';
      let cur: number = dl.actualFileOffsetCode;
      while (!test.startsWith('DF') && !test.startsWith('DE01')) {
        let ndl: Display_List_Command = new Display_List_Command(
          zobj.buf.readUInt32BE(cur),
          zobj.buf.readUInt32BE(cur + 4),
          cur
        );
        traverse.push(ndl);
        test = ndl.code;
        cur += 8;
      }
      traverse.push(dl);
    }

    function traverseDisplayList(dl: Display_List_Command) {
      if (dl.code.startsWith('DE') && dl.is06()) {
        // Jump
        let test = '';
        let cur: number = dl.address;
        console.log("Jumping to " + dl.code + " at position " + dl.actualFileOffsetCode.toString(16) + " to " + dl.address.toString(16));
        while (!test.startsWith('DF') && !test.startsWith('DE01')) {
          let ndl: Display_List_Command = new Display_List_Command(
            zobj.buf.readUInt32BE(cur),
            zobj.buf.readUInt32BE(cur + 4),
            cur
          );
          traverseDisplayList(ndl);
          test = ndl.code;
          cur += 8;
        }
        console.log("Exiting display list due to DF or DE01");
      } else {
        //console.log(dl.code + " at position " + dl.actualFileOffsetCode.toString(16) + " is not a jump. Add to traversal pool.")
      }
      traverse.push(dl);
    }

    for (let i = 0; i < commands.length; i++) {
      traverseDisplayList(commands[i]);
    }

    console.log('Found ' + traverse.length + ' traversable nodes.');

    let repoints: Display_List_Command[] = new Array<Display_List_Command>();

    function lookForRepoints() {
      for (let i = 0; i < traverse.length; i++) {
        let dl: Display_List_Command = traverse[i];
        if (
          dl.code.startsWith('DE') ||
          dl.code.startsWith('01') ||
          dl.code.startsWith('FD') ||
          dl.code.startsWith('DA')
        ) {
          if (dl.is06()) {
            repoints.push(dl);
          }
        }
      }
    }

    lookForRepoints();

    if (modeByte !== 0x69) {
      let pointer_to_skeleton_pointer: number =
        zobj.buf.readUInt32BE(0x500c) - 0x06000000;
      let pointer_to_skeleton: number =
        zobj.buf.readUInt32BE(pointer_to_skeleton_pointer) - 0x06000000;

      console.log('Looking in the closet...');

      let dem_bones: number = zobj.buf.readUInt8(
        pointer_to_skeleton_pointer + 0x4
      );
      let spooky_scary: Skeleton = new Skeleton(dem_bones);

      console.log('Found a skeleton with ' + dem_bones + ' bones.');

      for (let i = 0; i < spooky_scary.total; i++) {
        spooky_scary.bones.push(
          new Skeleton_Entry(
            zobj.buf.readUInt32BE(pointer_to_skeleton + 4 * i) - 0x06000000,
            pointer_to_skeleton + 4 * i
          )
        );
      }

      for (let i = 0; i < spooky_scary.bones.length; i++) {
        let lookingForFF = '';
        let cur: number = spooky_scary.bones[i].pointer;
        let dl: Display_List_Command = new Display_List_Command(
          0xdeadbeef,
          zobj.buf.readUInt32BE(cur + 0xc),
          cur + 0xc - 0x4
        );
        if (dl.is06()) {
          repoints.push(dl);
        }
        let dl2: Display_List_Command = new Display_List_Command(
          0xdeadbeef,
          zobj.buf.readUInt32BE(cur + 0x8),
          cur + 0x8 - 0x4
        );
        if (dl2.is06()) {
          repoints.push(dl2);
        }
        lookingForFF = zobj.buf
          .readUInt8(cur + 0x6)
          .toString(16)
          .toUpperCase();
        cur += 0x10;
        while (lookingForFF !== 'FF') {
          let dl: Display_List_Command = new Display_List_Command(
            0xdeadbeef,
            zobj.buf.readUInt32BE(cur + 0xc),
            cur + 0xc - 0x4
          );
          if (dl.is06()) {
            repoints.push(dl);
          }
          let dl2: Display_List_Command = new Display_List_Command(
            0xdeadbeef,
            zobj.buf.readUInt32BE(cur + 0x8),
            cur + 0x8 - 0x4
          );
          if (dl2.is06()) {
            repoints.push(dl2);
          }
          lookingForFF = zobj.buf
            .readUInt8(cur + 0x6)
            .toString(16)
            .toUpperCase();
          cur += 0x10;
        }
        zobj.buf.writeUInt32BE(
          spooky_scary.bones[i].pointer + r,
          spooky_scary.bones[i].actualFileOffset
        );
      }

      let after_bones: number =
        spooky_scary.bones[dem_bones - 1].actualFileOffset + 0x4;

      repoints.push(
        new Display_List_Command(
          0xdeadbeef,
          zobj.buf.readUInt32BE(after_bones),
          after_bones - 0x4
        )
      );
      zobj.buf.writeUInt32BE(
        pointer_to_skeleton + r,
        pointer_to_skeleton_pointer
      );
      zobj.buf.writeUInt32BE(pointer_to_skeleton_pointer + r, 0x500c);
      zzCache.skeleton = spooky_scary;
    }

    function doRepoints() {
      console.log('Found ' + repoints.length + ' things in need of a repoint.');
      for (let i = 0; i < repoints.length; i++) {
        try {
          zobj.buf.writeUInt32BE(
            r + repoints[i].address,
            repoints[i].actualFileOffsetAddress
          );
          zzCache.cache.push(repoints[i]);
        } catch (err) {
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
      let word: number = zobj.buf.readUInt32BE(i);
      let addr: number = zobj.buf.readUInt32BE(i + 4);
      let dl: Display_List_Command = new Display_List_Command(word, addr, i);
      if (dl.code === 'E7000000' && dl.addressAsString === '00000000') {
        manualTraversal(dl);
      }
    }

    lookForRepoints();
    doRepoints();

    hash = crypto
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
