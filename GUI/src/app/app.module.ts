import { APP_BASE_HREF } from '@angular/common';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NgModule, ComponentFactoryResolver, ApplicationRef, CUSTOM_ELEMENTS_SCHEMA, DoBootstrap } from '@angular/core';
import { NbDialogModule } from '@nebular/theme';
import { NbEvaIconsModule } from '@nebular/eva-icons';

import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent, BypassSecurityPipe } from './app.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { ThemeModule } from './@theme/theme.module';

import { CdkTableModule } from '@angular/cdk/table';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDialogModule } from '@angular/material/dialog';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatListModule } from '@angular/material/list';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatRadioModule } from '@angular/material/radio';
import { MatSelectModule } from '@angular/material/select';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSliderModule } from '@angular/material/slider';
import { MatTableModule } from '@angular/material/table';

//Pages
import { GUIGlobal } from './providers/GUIGlobal';

//Custom Components
import { ProgressWindowComponent } from './pages/generator/progressWindow/progressWindow.component';
import { DialogWindowComponent } from './pages/generator/dialogWindow/dialogWindow.component';
import { ErrorDetailsWindowComponent } from './pages/generator/errorDetailsWindow/errorDetailsWindow.component';
import { ConfirmationWindowComponent } from './pages/generator/confirmationWindow/confirmationWindow.component';
import { TextInputWindowComponent } from './pages/generator/textInputWindow/textInputWindow.component';


@NgModule({
    declarations: [
        AppComponent,
        BypassSecurityPipe,
        ProgressWindowComponent,
        DialogWindowComponent,
        ErrorDetailsWindowComponent,
        ConfirmationWindowComponent,
        TextInputWindowComponent
    ],
    imports: [
        BrowserModule,
        BrowserAnimationsModule,
        AppRoutingModule,
        HttpClientModule,
        FormsModule,
        ReactiveFormsModule,
        CdkTableModule,
        ThemeModule.forRoot(),
        NbDialogModule.forRoot(),
        NbEvaIconsModule
    ],
    exports: [
        MatButtonModule,
        MatButtonToggleModule,
        MatCardModule,
        MatCheckboxModule,
        MatDialogModule,
        MatGridListModule,
        MatIconModule,
        MatInputModule,
        MatListModule,
        MatProgressBarModule,
        MatProgressSpinnerModule,
        MatRadioModule,
        MatSelectModule,
        MatSliderModule,
        MatSlideToggleModule,
        MatTableModule
    ],
    schemas: [
        CUSTOM_ELEMENTS_SCHEMA
    ],
    providers: [
        { provide: APP_BASE_HREF, useValue: '/' },
        GUIGlobal
    ]
})
export class AppModule implements DoBootstrap {

  constructor(private resolver: ComponentFactoryResolver) { }

  ngDoBootstrap(appRef: ApplicationRef) { //Custom bootstrapper allows to intialize multiple instances of the same app, e.g. generator and patcher
    const factory = this.resolver.resolveComponentFactory(AppComponent);
    const selectorName = factory.selector;

    let elements = document.getElementsByTagName(selectorName);

    //Return if no elements found
    if (elements.length == 0) {
      return;
    }

    //More than one root level component found, bootstrap unique instances
    if (elements.length > 1) {

      for (let i = 0; i < elements.length; i++) {
        console.log("Bootstrap:", elements[i].id);
        appRef.bootstrap(factory, elements[i]);
      }
    }
    else { //Only a single root level component found, bootstrap as usual
      console.log("Bootstrap single GUI app");
      appRef.bootstrap(factory);
    }
  }
}
