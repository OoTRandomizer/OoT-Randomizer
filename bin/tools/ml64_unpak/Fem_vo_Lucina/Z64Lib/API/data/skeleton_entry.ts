export class Skeleton_Entry {
  pointer: number;
  actualFileOffset: number;

  constructor(pointer: number, actualFileOffset: number) {
    this.pointer = pointer;
    this.actualFileOffset = actualFileOffset;
  }
}
