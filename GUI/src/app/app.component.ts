import { Component, ViewContainerRef, ElementRef, ViewEncapsulation, Renderer2, Inject } from '@angular/core';
import { PipeTransform, Pipe } from '@angular/core';
import { Router } from '@angular/router';
import { DomSanitizer } from '@angular/platform-browser';

import { GUIGlobal } from './providers/GUIGlobal';
import { DOCUMENT } from '@angular/common';
import { OOTR_THEME, ThemeSwitcher } from './providers/theme-switcher.service';

@Pipe({ name: 'bypassSecurity' })
export class BypassSecurityPipe implements PipeTransform {
  constructor(private sanitizer: DomSanitizer) { }

  transform(url) {
    return this.sanitizer.bypassSecurityTrustResourceUrl(url);
  }
}

@Component({
  // keep ngx-app as name for websites backwards compatibility
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'ngx-app',
  template: `
      <div id="generator" class="${OOTR_THEME.DEFAULT}">
        <router-outlet></router-outlet>
      </div>
  `,
  // Shadow-DOM requires code tweaks within Nebular.
  // Style interference with website is addressed by usage of selector specificity.
  encapsulation: ViewEncapsulation.None
})
export class AppComponent {

  constructor(public viewContainerRef: ViewContainerRef,
              private elm: ElementRef,
              private router: Router,
              private global: GUIGlobal,
              private readonly renderer: Renderer2,
              @Inject(DOCUMENT) private readonly document: Document,
              private readonly themeSwitcher: ThemeSwitcher,
  ) {
    this.global.globalEmitter.subscribe(eventObj => {
      if (eventObj?.name === 'init_finished') {
        this.themeSwitcher.initTheme();
        this.fixInitialization();
      }
    });

    global.globalInit(elm.nativeElement.id);

    //Route manually at the start to avoid URL changes in the browser
    this.router.navigate(['/pages/generator'], { skipLocationChange: true });
  }

  private fixInitialization() {
    const body = this.document.getElementsByTagName('body')[0];

    if (!body?.classList?.value?.includes('pace-done')) {
      const paceProgressTag = this.document.getElementsByClassName('pace-progress')[0];
      const initDestroyTimeOutPace = () => {
        let counter = 0;

        const refreshIntervalId = setInterval(() => {
          const progress = paceProgressTag.getAttribute("data-progress-text");

          if (["99%", "100%"].includes(progress)) {
            counter++;
          }

          if (counter > 50) {
            clearInterval(refreshIntervalId);
            this.finishPace();
          }
        }, 100);
      };
      initDestroyTimeOutPace.bind(this)();
    }
  }

  private finishPace(): void {
    const body = this.document.getElementsByTagName('body')[0];

    body?.classList?.value
      ?.split(' ')
      .filter(c => c.startsWith('pace'))
      .forEach(c => this.renderer.removeClass(body, c));

    this.renderer.addClass(body, 'pace-done');
  }
}
