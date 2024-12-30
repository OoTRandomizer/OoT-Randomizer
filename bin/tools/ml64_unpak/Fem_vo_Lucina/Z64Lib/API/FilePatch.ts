export class FilePatch {
    offset: number;
    value: number;
    constructor(offset: number, value: number) {
        this.offset = offset;
        this.value = value;
    }
}
