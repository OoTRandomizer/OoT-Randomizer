import { Component, Input, ElementRef, ViewChild, OnInit } from '@angular/core';
import { NbDialogRef } from '@nebular/theme';

@Component({
  template: `
    <nb-card class="textInput-window">
      <nb-card-header>
      {{ dialogHeader }}
      <button nbButton class="headerButton" size="xsmall" status="danger" (click)="cancelDialog()">X</button>
      </nb-card-header>
      <nb-card-body>
        {{ dialogMessage }}
        <p></p>
        <input #inputBar class="textInput" type="text" maxlength="100" nbInput fieldSize="small" [(ngModel)]="inputText">
      </nb-card-body>
      <nb-card-footer>
        <div class="footerButtonWrapper">
          <button nbButton size="small" status="primary" (click)="confirmDialog()">OK</button>
        </div>
      </nb-card-footer>
    </nb-card>
  `,
  styleUrls: ['./textInputWindow.scss'],
})
export class TextInputWindowComponent implements OnInit {

  @Input() dialogHeader: string = "Enter name";
  @Input() dialogMessage: string = "";

  inputText: string = "";

  @ViewChild("inputBar", { static: true }) inputBarRef: ElementRef;

  constructor(protected ref: NbDialogRef<TextInputWindowComponent>) {
  }

  ngOnInit() {
    this.inputBarRef.nativeElement.focus();
  }

  cancelDialog() {
    this.ref.close();
  }

  confirmDialog() {
    this.ref.close(this.inputText);
  }
}
