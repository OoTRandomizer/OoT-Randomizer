import { NgModule, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';

import { ThemeModule } from '../../@theme/theme.module';
import { GeneratorComponent } from './generator.component';

import { FlexLayoutModule } from '@angular/flex-layout';

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

import { AngularDualListBoxModule } from 'angular-dual-listbox';
import { GUIListboxComponent } from '../../components/guiListbox/guiListbox';
import { ColorPickerModule } from 'ngx-color-picker';
import { ngfModule } from 'angular-file';

//Custom Directives
import { ResponsiveColsDirective } from '../../directives/responsiveCols.directive';

//Custom Components
import { GUITooltipComponent } from './guiTooltip/guiTooltip.component';

@NgModule({
    imports: [
        ThemeModule,
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
        MatTableModule,
        FlexLayoutModule,
        ColorPickerModule,
        ngfModule
    ],
    declarations: [
        GeneratorComponent,
        ResponsiveColsDirective,
        GUITooltipComponent,
        GUIListboxComponent
    ],
    providers: [
      { provide: Window, useValue: window }
    ],
    schemas: [
        CUSTOM_ELEMENTS_SCHEMA
    ]
})
export class GeneratorModule { }
