import { Component } from '@angular/core';
import { MENU_ITEMS } from './pages-menu';

@Component({
  selector: 'ootr-ngx-pages',
  template: `
    <ootr-gui-layout>
      <router-outlet></router-outlet>
    </ootr-gui-layout>
  `,
})
export class PagesComponent {
  menu = MENU_ITEMS;
}
