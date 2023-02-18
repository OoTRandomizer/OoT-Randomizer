import { AfterViewChecked, Component, Inject, Input } from '@angular/core';
import { DOCUMENT } from '@angular/common';

@Component({
  selector: 'ootr-gui-tooltip',
  template: `
    <nb-card class="popover-card" style="height:100%;margin-bottom:0px">
      <nb-card-body>
        <span [innerHTML]="tooltip"></span>
      </nb-card-body>
    </nb-card>
  `
})
export class GUITooltipComponent implements AfterViewChecked {

  @Input()
  tooltip: string = '';

  constructor(@Inject(DOCUMENT) private readonly document: Document,
              private readonly window: Window,
  ) {
  }

  ngAfterViewChecked(): void {
    this.preventHintPositioningOutsideTopBounds();
    this.preventHintPositioningOutsideBottomBounds();
    this.preventHintOverlayingOnSelectOptions();
  }

  private preventHintPositioningOutsideTopBounds(): void {
    const cdkOverlayPanes = this.document.getElementsByClassName('cdk-overlay-pane');

    Array.from(cdkOverlayPanes)
      .filter((e: HTMLElement) => e.offsetTop < 0)
      .forEach((e: HTMLElement) => e.style.top = '16px');
  }

  private preventHintPositioningOutsideBottomBounds(): void {
    const cdkOverlayPanes = this.document.getElementsByClassName('cdk-overlay-pane');

    Array.from(cdkOverlayPanes)
      .filter((e: HTMLElement) => this.calculateFeasibleHeight(e) < e.offsetHeight)
      .forEach((e: HTMLElement) => e.style.maxHeight = `${this.calculateFeasibleHeight(e) }px`);
  }

  private preventHintOverlayingOnSelectOptions(): void {
    const cdkOverlayBoxes = this.document.getElementsByClassName('cdk-overlay-connected-position-bounding-box');

    Array.from(cdkOverlayBoxes)
      .forEach((e: HTMLElement, i: number) => i === cdkOverlayBoxes.length-1 ? e.style.zIndex = '999' : e.style.zIndex = '1000');
  }

  private calculateFeasibleHeight(element: HTMLElement): number {
    return this.window.innerHeight - element.offsetTop;
  }
}
