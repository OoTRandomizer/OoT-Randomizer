import {ChangeDetectorRef, Component, OnInit} from '@angular/core';
import {GUIGlobal} from '../../../providers/GUIGlobal';
import {ThemeSwitcher} from '../../../providers/theme-switcher.service';

@Component({
  selector: 'ootr-header',
  styleUrls: ['./header.component.scss'],
  templateUrl: './header.component.html',
})
export class HeaderComponent implements OnInit {

  isMaximized: boolean = false;
  platform: string = (<any>window).apiPlatform;

  constructor(private cd: ChangeDetectorRef,
              public global: GUIGlobal,
              public themeSwitcher: ThemeSwitcher,
  ) { }

  ngOnInit() {
    if (this.global.getGlobalVar('electronAvailable')) {
      this.global.isWindowMaximized().then(res => {
        this.isMaximized = res;

        this.cd.markForCheck();
        this.cd.detectChanges();
      }).catch((err) => {
        console.log(err);
      });

      this.global.globalEmitter.subscribe(eventObj => {

        if (eventObj.name == "window_maximized") {
          //console.log("maximized event");
          this.isMaximized = true;

          this.cd.markForCheck();
          this.cd.detectChanges();
        }
        else if (eventObj.name == "window_unmaximized") {
          //console.log("unmaximized event");
          this.isMaximized = false;

          this.cd.markForCheck();
          this.cd.detectChanges();
        }
      });
    }
  }

  minimize() {
    this.global.minimizeWindow();
  }

  maximize() {
    this.global.maximizeWindow();
  }

  close() {
    this.global.closeWindow();
  }

  switchTheme() {
    this.themeSwitcher.switchTheme();
  }
}
