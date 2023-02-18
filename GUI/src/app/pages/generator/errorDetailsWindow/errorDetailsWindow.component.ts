import { Component, Input } from '@angular/core';
import { NbDialogRef } from '@nebular/theme';
import { GUIGlobal } from '../../../providers/GUIGlobal';

@Component({
  template: `
    <nb-card class="error-window">
      <nb-card-header class="errorHeader">
        You encountered an error.<br>Please copy and post the following details in the OoTR Discord:
        <button nbButton class="headerButton" size="xsmall" status="danger" (click)="closeDialog()">X</button>
      </nb-card-header>
      <nb-card-body class="errorBody">
        <textarea class="textAreaError" nbInput fullWidth readonly>{{ errorMessage }}</textarea>
      </nb-card-body>
      <nb-card-footer>
        <div class="footerButtonWrapper">
          <button nbButton size="small" status="basic" (click)="closeDialog()">OK</button>
          <button nbButton size="small" status="info" (click)="copyErrorMessage()">Copy</button>
        </div>
      </nb-card-footer>
    </nb-card>
  `,
  styleUrls: ['./errorDetailsWindow.scss'],
})
export class ErrorDetailsWindowComponent {

  @Input() errorMessage: string = "";

  constructor(protected ref: NbDialogRef<ErrorDetailsWindowComponent>, public global: GUIGlobal) {
  }

  closeDialog() {
    this.ref.close();
  }

  copyErrorMessage() {
    this.global.copyToClipboard(this.errorMessage);
  }
}
