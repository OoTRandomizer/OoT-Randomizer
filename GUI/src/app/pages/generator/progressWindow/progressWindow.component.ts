import { Component, Input, ChangeDetectorRef } from '@angular/core';
import { NbDialogRef, NbDialogService } from '@nebular/theme';
import { ErrorDetailsWindowComponent } from '../errorDetailsWindow/errorDetailsWindow.component';

@Component({
  template: `
    <nb-card class="progress-window">
      <nb-card-header>
      Generating Seed
      <button nbButton class="headerButton" size="xsmall" status="danger" [disabled]="cancellationInProgress" (click)="cancelGeneration()">X</button>
      </nb-card-header>
      <nb-card-body>
        {{ progressMessage }}
        <p></p>
        {{ currentGenerationIndex }} / {{ totalGenerationCount }}:
        <nb-progress-bar [value]="progressPercentageCurrent" [status]="progressStatus === 0 ? 'primary': progressStatus === 1 ? 'success' : 'danger'" [displayValue]="true"></nb-progress-bar>
        <p></p>
        Total:
        <nb-progress-bar [value]="progressPercentageTotal" [status]="progressStatus === 0 ? 'info': progressStatus === 1 ? 'success' : 'danger'" [displayValue]="true"></nb-progress-bar>
        <div *ngIf="progressPercentageTotal === 100" class="footerButtonWrapper">
          <button nbButton [disabled]="cancellationInProgress" size="small" status="basic" (click)="cancelGeneration()">OK</button>
          <button *ngIf="progressErrorDetails.length > 0" nbButton [disabled]="cancellationInProgress" status="danger" size="small" (click)="showErrorDetails()">Details</button>
        </div>
      </nb-card-body>
    </nb-card>
  `,
  styleUrls: ['./progressWindow.scss'],
})
export class ProgressWindowComponent {

  @Input() dashboardRef: any;
  @Input() totalGenerationCount: number;

  currentGenerationIndex: number = 1;

  progressPercentageCurrent: number = 0;
  progressPercentageTotal: number = 0;

  progressStatus: number = 0;
  progressMessage: string = "Starting.";
  progressErrorDetails: string = "";

  cancellationInProgress: boolean = false;
  closed: boolean = false;

  constructor(protected ref: NbDialogRef<ProgressWindowComponent>, private cd: ChangeDetectorRef, private dialogService: NbDialogService) {
  }

  refreshLayout() {

    if (this.closed)
      return;

    this.cd.markForCheck();
    this.cd.detectChanges();
  }

  cancelGeneration() {

    this.cancellationInProgress = true;

    if (this.progressStatus == 0) { //Cancel active generation first before closing progress window
      this.dashboardRef.cancelGeneration().then(() => {
        console.log("Generation was cancelled");
        this.closed = true;
        this.ref.close();
      }).catch((err) => {
        console.log("Couldn't cancel the generation, window stays open. Error:", err);
        this.cancellationInProgress = false;
      });
    }
    else {
      this.closed = true;
      this.ref.close();
    }
  }

  showErrorDetails() {
    this.cancelGeneration();
    this.dialogService.open(ErrorDetailsWindowComponent, {
      autoFocus: true, closeOnBackdropClick: true, closeOnEsc: true, hasBackdrop: true, hasScroll: false, context: { errorMessage: this.progressErrorDetails }
    });
  }
}
