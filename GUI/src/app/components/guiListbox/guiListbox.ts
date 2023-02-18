import { Component, Input } from '@angular/core';
import { DualListComponent } from 'angular-dual-listbox';
import { BasicList } from 'angular-dual-listbox';

@Component({
  selector: 'ootr-gui-listbox',
  templateUrl: './guiListbox.html',
  styleUrls: ['./guiListbox.scss']
})
export class GUIListboxComponent extends DualListComponent {

  @Input() tooltip: any = 'tooltip';
  @Input() tooltipComponent: any = null;
  @Input() tagFilter: any = null;

  selectedTag: string = "(all)";

  clearFilter(source: BasicList, isAvailable: boolean = false) {
    if (source) {
      source.picker = '';
      this.selectedTag = "(all)";
      this.onFilter(source);
    }
  }

  onFilter(source: BasicList) {

    //Filter by Tag
    if (source.name == "available" && this.selectedTag != "(all)") {
      const filtered = source.list.filter((item: any) => {
        if (Object.prototype.toString.call(item) === '[object Object]') {
          if (item._tags !== undefined) {
            return item._tags.indexOf(this.selectedTag) !== -1;
          } else {
            return true;
          }
        } else {
          return false;
        }
      });
      source.sift = filtered;
      this.unpickExtended(source);
    } else {
      source.sift = source.list;
    }

    //Filter by Search Picker
    if (source.picker.length > 0) {
      try {
        const filtered = source.sift.filter((item: any) => {
          if (Object.prototype.toString.call(item) === '[object Object]') {
            if (item._name !== undefined) {
              // @ts-ignore: remove when d.ts has locale as an argument.
              return item._name.toLocaleLowerCase(this.format.locale).indexOf(source.picker.toLocaleLowerCase(this.format.locale)) !== -1;
            } else {
              // @ts-ignore: remove when d.ts has locale as an argument.
              return JSON.stringify(item).toLocaleLowerCase(this.format.locale).indexOf(source.picker.toLocaleLowerCase(this.format.locale)) !== -1;
            }
          } else {
            // @ts-ignore: remove when d.ts has locale as an argument.
            return item.toLocaleLowerCase(this.format.locale).indexOf(source.picker.toLocaleLowerCase(this.format.locale)) !== -1;
          }
        });
        source.sift = filtered;
        this.unpickExtended(source);
      } catch (e) {
        if (e instanceof RangeError) {
          this.format.locale = undefined;
        }
      }
    }
  }

  private unpickExtended(source: BasicList) {
    for (let i = source.pick.length - 1; i >= 0; i -= 1) {
      if (source.sift.indexOf(source.pick[i]) === -1) {
        source.pick.splice(i, 1);
      }
    }
  }

  buildAvailable(source: Array<any>): boolean
  {
    const sourceChanges = this.sourceDiffer.diff(source);
    if (sourceChanges) {
      sourceChanges.forEachRemovedItem((r: any) => {
        const idx = this.findItemIndex(this.available.list, r.item, this.key);
        if (idx !== -1) {
          this.available.list.splice(idx, 1);
        }
      });

      sourceChanges.forEachAddedItem((r: any) => {
        // Do not add duplicates even if source has duplicates.
        if (this.findItemIndex(this.available.list, r.item, this.key) === -1) {
          this.available.list.push({ _id: this.makeIdExtended(r.item), _name: this.makeName(r.item), _tags: this.makeTagsExtended(r.item), _tooltip: this.makeTooltipExtended(r.item) });
        }
      });

      if (this.compare !== undefined) {
        this.available.list.sort(this.compare);
      }
      this.available.sift = this.available.list;

      return true;
    }
    return false;
  }

  private makeIdExtended(item: any): string | number {
    if (typeof item === 'object') {
      return item[this.key];
    }
    else {
      return item;
    }
  }

  private makeTooltipExtended(item: any): string {
    if (typeof item === 'object') {
      return item[this.tooltip] ? item[this.tooltip] : "";
    }
    else {
      return item;
    }
  }

  private makeTagsExtended(item: any): string {
    if (typeof item === 'object') {
      return item["tags"] ? item["tags"] : "";
    }
    else {
      return item;
    }
  }
}
