import { Component, Input } from '@angular/core';
import { NbDialogRef } from '@nebular/theme';

@Component({
  template: `
    <nb-card class="dialog-window">
      <nb-card-header>
      {{ dialogHeader }}
      <button nbButton class="headerButton" size="xsmall" status="danger" (click)="closeDialog()">X</button>
      </nb-card-header>
      <nb-card-body>
        {{ dialogMessage }}
      </nb-card-body>
      <nb-card-footer>
        <div class="footerButtonWrapper">
          <button nbButton size="small" status="primary" (click)="closeDialog()">OK</button>
        </div>
      </nb-card-footer>
    </nb-card>
  `,
  styleUrls: ['./dialogWindow.scss'],
})
export class DialogWindowComponent {

  @Input() dialogHeader: string = "Info";
  @Input() dialogMessage: string = "";

  constructor(protected ref: NbDialogRef<DialogWindowComponent>) {
  }

  closeDialog() {
    this.ref.close();
  }
}
