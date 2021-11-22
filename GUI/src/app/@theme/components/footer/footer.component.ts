import { Component } from '@angular/core';
import { NbDialogService } from '@nebular/theme';
import { GUIGlobal } from '../../../providers/GUIGlobal';

import { ConfirmationWindow } from '../../../pages/generator/confirmationWindow/confirmationWindow.component';

@Component({
  selector: 'ngx-footer',
  styleUrls: ['./footer.component.scss'],
  template: `
    <span *ngIf="!hasUpdate">Version <b>{{localVersion}}</b> © ZeldaSpeedRuns Community</span>
    <span *ngIf="hasUpdate">Version <b>{{localVersion}}</b> © ZeldaSpeedRuns Community - <a id="updateButton" href="#" (click)="promptUpdate()"><b>New Version Available!</b></a></span>
    <div class="socials">
      <a href="https://wiki.ootrandomizer.com" target="_blank" class="fab fa-wikipedia-w"></a>
      <a href="https://www.patreon.com/zeldaspeedruns" target="_blank" class="fab fa-patreon"></a>
      <a href="https://discord.gg/ootrandomizer" target="_blank" class="fab fa-discord"></a>
      <a href="https://twitter.com/zeldaspeedruns" target="_blank" class="fab fa-twitter"></a>
      <a href="https://twitch.tv/zeldaspeedruns" target="_blank" class="fab fa-twitch"></a>
      <a href="https://www.youtube.com/ZSRVideos" target="_blank" class="ion ion-social-youtube"></a>
    </div>
  `,
})
export class FooterComponent {

  localVersion: string = "";
  remoteVersion: string = "";
  hasUpdate: boolean = false;

  constructor(public global: GUIGlobal, private dialogService: NbDialogService) { }

  ngOnInit() {

    if (this.global.getGlobalVar('electronAvailable')) { //Version check is Electron only

      this.global.globalEmitter.subscribe(eventObj => {

        if (eventObj.name == "init_finished") {
          this.runVersionCheck();
        }
        else if (eventObj.name == "local_version_checked") {
          this.localVersion = eventObj.version;
        }      
      });

      if (this.global.getGlobalVar("appReady")) {
        this.runVersionCheck();
      }
    }
  }

  runVersionCheck() { //Electron only
    this.global.versionCheck().then(res => {
      if (res && res.hasUpdate) {
        this.remoteVersion = res.latestVersion;
        this.hasUpdate = true;
      }
    }).catch((err) => {
      console.log('Error checking version', err);
    });
  }

  promptUpdate() {
    this.dialogService.open(ConfirmationWindow, {
      autoFocus: true, closeOnBackdropClick: true, closeOnEsc: true, hasBackdrop: true, hasScroll: false, context: { dialogHeader: "New Version Available!", dialogMessage: "You are using version " + this.localVersion + ", and the latest is version " + this.remoteVersion + ". Do you want to download the latest version now?" + ((this.remoteVersion.includes("Release")) ? "" : " (Note that you are using a development build and therefore will have to redownload and compile the source off GitHub yourself)") }
    }).onClose.subscribe(confirmed => {

      if (confirmed) {
        let link = this.remoteVersion.includes("Release") ? "https://www.ootrandomizer.com/downloads" : "https://github.com/TestRunnerSRL/OoT-Randomizer/tree/Dev";
        (<any>window).open(link, "_blank");
      }
    });
  }
}
