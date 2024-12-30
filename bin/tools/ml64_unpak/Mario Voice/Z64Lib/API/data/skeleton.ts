import { Skeleton_Entry } from './skeleton_entry';

export class Skeleton {
  bones: Skeleton_Entry[] = new Array<Skeleton_Entry>();
  total: number;

  constructor(num: number) {
    this.total = num;
  }
}
