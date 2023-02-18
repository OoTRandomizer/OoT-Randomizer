import { Directive, Input, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatGridList } from '@angular/material/grid-list';
import { MediaObserver, MediaChange } from '@angular/flex-layout';

export interface IResponsiveColumnsMap {
  xs?: number;
  sm?: number;
  md?: number;
  lg?: number;
  xl?: number;
}

// Usage: <mat-grid-list [responsiveCols]="{xs: 2, sm: 2, md: 4, lg: 6, xl: 8}">
@Directive({
  selector: '[responsiveCols]'
})
export class ResponsiveColsDirective implements OnInit {
  private countBySize: IResponsiveColumnsMap = {xs: 2, sm: 2, md: 4, lg: 6, xl: 8};

  public get cols(): IResponsiveColumnsMap {
    return this.countBySize;
  }

  @Input('responsiveCols')
  public set cols(map: IResponsiveColumnsMap) {

    if (map && ('object' === (typeof map))) {
      this.countBySize = map;
    }
  }

  public constructor(
    private grid: MatGridList,
    private media: MediaObserver,
    private cd: ChangeDetectorRef
  ) {

    this.initializeColsCount();

    //Default
    if (!this.grid.cols)
      this.grid.cols = 2;

    cd.markForCheck();
  }

  public ngOnInit(): void {
    this.cd.detectChanges();
    this.initializeColsCount();

    //Default
    if (!this.grid.cols)
      this.grid.cols = 2;

    this.cd.markForCheck();
    this.cd.detectChanges();

    this.media.asObservable().subscribe((changes: MediaChange[]) => {
      if (changes[0]) {
        this.grid.cols = this.countBySize[changes[0].mqAlias];
        this.cd?.markForCheck();
      }
    });
  }

  private initializeColsCount(): void {
    Object.keys(this.countBySize).some(
      (mqAlias: string): boolean => {
        const isActive = this.media.isActive(mqAlias);

        this.grid.cols = this.countBySize[mqAlias];

        if (isActive) {
          this.grid.cols = this.countBySize[mqAlias];
        }

        return isActive;
    });
  }
}
