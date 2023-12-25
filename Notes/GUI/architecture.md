# Architecture

This markdown note is originally based on a GitHub comment made by dragonbane0 from 2019. ([Reference](https://github.com/TestRunnerSRL/OoT-Randomizer/pull/736#issuecomment-507002499))

It provides an overview of the GUI architecture.

## Electron

### Overview

The Electron source is contained within GUI/electron/src and written in TypeScript. Main.ts is managing the Electron process (the main side which has full access to the host system) and is used as the entry point. The preload.ts gets injected into any given browser window created by the main process and managed by the renderer process.

The renderer process (the "client") acts mostly as a normal browser environment and is thus isolated from the host system. The preload.ts has restricted access to the main process and the renderer process and thus sits in the middle as an mediator of sorts. It gets loaded as part of a browser window before the first webpage does, in a separate JavaScript execution context. The webpage is thus only able to communicate with the preload.ts via a process called postMessage.

If the webpage loaded in Electron were to be high-jacked in some way or Electron tricked into loading a remote webpage instead of a local one stored on the computer, the page then does not have full access to the host computer which would be catastrophic, but can only communicate with the preload.ts and the preload.ts gets the desired information from the main process / the host computer limiting access (the preload.ts should thus not implement a generic file IO API for example).

### Modules

electron/src/modules/generator.js is the low level module which handles all communication with the ootr python source.

The settingsParser.js module is used at run time to combine the 3 json files in electron/src/utils together into a single object the main Electron process shares with the browser app to initialize the GUI settings view. The settingsParser can be launched with a flag to indicate Electron mode or web mode. In web mode certain Electron only sections are not included within the output object, but different web sections are included instead. This gets used by the ootrandomizer.com server.

### The settings_list.json structure

utils/settings_list.json contains every single setting of the GUI as an array of objects. The following keys per setting entry are supported:

* default &rarr; The default value in the GUI
* name &rarr; Internal name of the setting
* text &rarr; Name of the setting as shown to the user
* tooltip &rarr; The tooltip shown to the user when he hovers/clicks on the setting. Line breaks are inserted by adding a HTML `<br>` tag into the string
* type &rarr; Type of the GUI element to use to control the setting. Available types are:

  1. Checkbutton: A boolean on/off toggle
  2. Radiobutton: A radio in-line list of buttons you can select one option of
  3. Combobox: A dropdown box that offers multiple options you can select one of
  4. Scale: A numerical scale that goes from a minimum to a maximum value and is accompanied by a number input box for manual input
  5. Textinput: An input box designed for text
  6. Numberinput: An input box designed for numbers (no scale)
  7. Fileinput: An input box designed for file paths accompanied by a browse button that opens a system file dialog
  8. Directoryinput: An input box designed for directory paths accompanied by a browse button that opens a system directory dialog
  9. SearchBox: A dual list of options that the user can select multiple options of and move them between active and not active. Also allows to text search for an option or select all at once. Drag and drop is also supported
  10. Presetinput: Designed for the main tab only. Adds a combobox and 3 buttons for the preset handling
  11. Outputdirbutton: Designed for the main tab only. The button to open the currently set output directory
* options &rarr; An array of options the setting can have. This is used for the settings type Checkbutton (redundant), Radiobutton, Combobox and SearchBox. Each option entry can have the following keys:

  1. name: Internal name of the option value
  2. text: Name of the option as shown to the user
  3. tooltip: The tooltip shown to the user when he hovers over the option. This is only supported by SearchBox at the moment. Line breaks are again added by a `<br>` tag
  4. controls-visibility-tab: What tab(s) to disable when this option is selected. Multiple tabs can be separated by comma and are addressed by their internal name (see mapping.json structure)
  5. controls-visibility-section: What section(s) to disable when this option is selected
  6. controls-visibility-setting: What specific setting(s) to disable when this option is selected

### The settings_mapping.json structure

Used to extend the settings_list.json and define the visual layout of the GUI for Electron and the website. Could possibly be collapsed into one if needed.

Starts with an array of tabs that are shown in the GUI. The following keys are supported:

* name &rarr; Internal name of the tab
* text &rarr; Name of the tab as shown in the GUI
* is-cosmetics &rarr; Whether the tab contains only cosmetic settings or not. Used to exclude cosmetics and sfx settings from presets and so on
* app-type &rarr; Restricts in which app the tab should be rendered in the GUI. Can be 'generator' or 'patcher '. Used on the website to differentiate between the seed generator and the standalone patcher that gets shown on the seed detail page. The latter only has the cosmetic tabs shown
* exclude-from-electron &rarr; If set then the settingsParser will skip over these tabs when in Electron mode
* exclude-from-web &rarr; If set then the settingsParser will skip over these tabs when in web mode
* sections &rarr; An array of sections to render in the tab, see next

The sections array follows that is used to group settings together in a tab. The following keys are supported:

* name &rarr; Internal name of the section
* text &rarr; Name of the section as shown in the GUI (can be left empty to not show a section header)
* subheader &rarr; Can be used to render a batch of text directly below the section header. `<br>` tags for line breaks are supported, as well as `<a>`  tags for  hyperlinks
* is-colors &rarr; Used to identify sections that contain settings with a Custom Color option which attaches the color picker module to these sections
* is-sfx &rarr;Used to identify SFX related sections. Not used at the moment and can be removed
* col-span &rarr; How many columns this section should try to occupy, affecting its width. If not set, the GUI will calculate a proper col-span automatically based on the number of columns available. On its biggest size the GUI can fit 4 columns per row, on its smallest 1. If this setting is used and not enough columns are available to satisfy this setting, it takes as many as possible. Thus setting a col-span of 4 will ensure that the section always takes up one full row regardless of GUI size
* row-span &rarr; Required and has to be set. How many rows this section should try to occupy, affecting its height. The GUI will distribute the available height evenly between each row, thus giving a section 2 rows will proportionally make it have a greater height than with 1. The three different numbers represent three different screen size presets: mobile, tablet, desktop
* settings &rarr; An array of settings to render in the section, see next

The settings array follows that defines the settings that should appear in this section. The following keys are supported:

* name &rarr; Internal name of the setting. Has to match with a setting defined in the settings_list.json
* controls-visibility-tab &rarr; What tab(s) to disable when this setting is enabled, used for Checkbuttons. Multiple tabs can be separated by comma and are addressed by their internal name
* controls-visibility-section &rarr; What section(s) to disable when this setting is enabled
* controls-visibility-setting &rarr; What specific setting(s) to disable when this setting is enabled
* hide-when-disabled &rarr; If this setting should be completely hidden when it gets disabled, not just greyed out. Used on the website to make the difference between generator and patcher more distinct
* min &rarr; The minimum numeric value allowed. Used for Scales and Numberinputs
* max &rarr; The maximum numeric value allowed. Used for Scales and Numberinputs. Can differ between Electron and website (e.g. multi world limit)
* size &rarr; How big the input field should be. Used for Numberinputs, Textinputs and Scales. Allowed values are: small, medium, full (=as wide as the section is) (default: extra small)
* max-length &rarr; How many characters are maximum allowed in this input field. Used for Textinputs (default: 260)
* file-types &rarr; Used for Fileinput. An array of allowed file types the system dialog should allow the user to pick (name and extensions)
* no-line-break &rarr;If set, then there will be no line break between this setting and the next one allowing to put 2 settings onto the same line to conserve space

### presets.json

The presets.json is structurally identical with the presets_default.json and thus can be made redundant.

## run.js

The GUI/run.js is used to boot the GUI as conveniently as possible for the user and maintains an index to decide quickly whether the GUI needs a rebuild or not in release mode. The following command line arguments are supported:

* p or python. Used to override the python executable path used to communicate with the ootr source. By default it takes python from your PATH
* r or release. Enables release mode. By default dev mode is assumed, which uses the Angular development server for fast GUI iterations instead of a local one-time compile
* f or force. If set, than a mandatory environment check is performed no matter what and Electron and Angular are always re-compiled
* -h or --help. Outputs usage information

## Angular

### Overview

The Angular source is contained in the GUI/src folder and consists of components and modules. Each component has a HTML template with custom Angular specific directives, styles written in Sass (a CSS extension) and component code written in TypeScript. The src/index.html serves as the entry point and bootstraps Angular.

Mostly relevant for GUI development is the src/app/pages/generator component. The HTML file provides the template that renders the entire settings section and all its tabs. The scss file provides the Sass (CSS) styling immediately relevant to this. The ts file contains the code immediately used when the user interacts with the GUI elements.

The src/app/providers/GUIGlobal.ts is a global service and can be included with any component. It provides a lot of functionality that might be used from multiple components, as well as manages the GUI initialization. After Angular core this is the main entry point for our own logic. It will request the settings map from the preload.ts/the Electron main process via postMessage and store this and other information globally, so it can be accessed from anywhere in the app. It also handles a lot of differences between Electron and web mode transparently. The generator component uses GUIGlobal constantly.

The applications header and footer bar can be found and customized within src/app/@theme/components.

src/app/@theme/layouts/GUI assembles the header bar, generator component and footer bar together as the singular app that the user sees in the end.

### Styling and Theming

In addition to individual angular component styles, files for global styling exist under GUI/src/app/@theme/styles.

Two themes exist at the moment. The default theme and the dark mode theme. Dark mode is an Electron-only feature and can be activated by clicking on the moon symbol in the header bar.

Colors and theme related properties are stored within theme.ootr-dark.scss and theme.ootr-default.scss.

To support theming it is crucial to work with $nb-theme() variables whenever colorizing backgrounds, texts, borders, etc.

Whether dark mode is active or not is saved inside settings.sav.

### Website compatibility

View encapsulation has been deactivated since it is not supported by Nebular and prevented us from further upgrading dependencies.

To prevent generator styles from interfering with the websites styling (and vice-versa) bootstrap was removed from the generator (previously used on both sides).
In addition, excessive use of selector specificity ensures interoperability.
