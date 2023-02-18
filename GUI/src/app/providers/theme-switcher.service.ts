import {Inject, Injectable, Renderer2, RendererFactory2} from '@angular/core';
import {DOCUMENT} from '@angular/common';
import {GUIGlobal} from './GUIGlobal';

export enum OOTR_THEME {
  DEFAULT = 'nb-theme-ootr-default',
  DARK = 'nb-theme-ootr-dark'
}

@Injectable()
export class ThemeSwitcher {

  isDarkThemeActive: boolean;

  private renderer: Renderer2;
  private body: Element;
  private generatorContainer: Element;

  constructor(
    private readonly rendererFactory: RendererFactory2,
    private readonly global: GUIGlobal,
    @Inject(DOCUMENT) private readonly document: Document,
  ) {
    this.renderer = rendererFactory.createRenderer(null, null);
  }

  initTheme() {
    this.body = this.document.getElementsByTagName('body')[0];
    this.generatorContainer = this.document.querySelector('div#generator');

    const themeFromSettings = this.global.generator_settingsMap["theme"];
    this.isDarkThemeActive = themeFromSettings === 'ootr-dark';

    this.removeAllThemes(this.body);
    this.removeAllThemes(this.generatorContainer);

    this.renderer.addClass(this.generatorContainer, this.isDarkThemeActive ? OOTR_THEME.DARK : OOTR_THEME.DEFAULT);
  }

  switchTheme() {
    if (this.isDarkThemeActive) {
      this.renderer.addClass(this.generatorContainer, OOTR_THEME.DEFAULT);
      this.renderer.removeClass(this.generatorContainer, OOTR_THEME.DARK);
      this.global.generator_settingsMap["theme"] = 'ootr-default';
    } else {
      this.renderer.addClass(this.generatorContainer, OOTR_THEME.DARK);
      this.renderer.removeClass(this.generatorContainer, OOTR_THEME.DEFAULT);
      this.global.generator_settingsMap["theme"] = 'ootr-dark';
    }

    this.isDarkThemeActive = !this.isDarkThemeActive;
    this.global.saveCurrentSettingsToFile();
  }

  private removeAllThemes(body: Element): void {
    body?.classList?.value
      ?.split(' ')
      .filter(c => c.startsWith('nb-theme'))
      .forEach(c => this.renderer.removeClass(body, c));
  }
}
