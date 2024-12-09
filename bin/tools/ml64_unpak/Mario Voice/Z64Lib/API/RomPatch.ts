import { FilePatch } from "./FilePatch";
export class RomPatch {
    index: number;
    data: FilePatch[] = new Array<FilePatch>();
    constructor(index: number) {
        this.index = index;
    }
}
