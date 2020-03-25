import { Injectable, HostBinding, EventEmitter, Output } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { ProgressWindow } from '../pages/generator/progressWindow/progressWindow.component';

import * as post from 'post-robot';

@Injectable()
export class GUIGlobal {

  //Globals for GUI HTML
  public generator_tabsVisibilityMap: Object = {};
  public generator_settingsVisibilityMap: Object = {};

  public generator_settingsMap: Object = {};
  public generator_customColorMap: Object = {};

  public generator_presets: Object = {};

  globalVars: Map<string, any>;
  electronEvents: Array<any> = [];

  @HostBinding('class.indigo-pink') materialStyleIndigo: boolean = true;

  @Output() globalEmitter: EventEmitter<object> = new EventEmitter();
  
  constructor(private http: HttpClient) {
    this.globalVars = new Map<string, any>([
      ["appReady", false],
      ["appType", null],
      ["electronAvailable", false],
      ["webSourceVersion", ""],
      ["webIsMasterVersion", false],
      ["generatorSettingsArray", []],
      ["generatorSettingsObj", {}],
      ["generatorCosmeticsArray", []],
      ["generatorCosmeticsObj", {}]
    ]);
  }

  globalInit(appType: string) {

    if (!appType)
      appType = "generator"; //Generator is the default

    console.log("APP Type:", appType);
    this.setGlobalVar("appType", appType);

    if ((<any>window).electronAvailable) { //Electron/Offline mode

      if ((<any>window).apiPythonSourceFound) {
        this.setGlobalVar("electronAvailable", true);
        console.log("Electron API available");
        console.log("Running on OS:", (<any>window).apiPlatform);

        this.createElectronEvents();
        this.electronInit();
      }
      else {
        console.error("Improper setup, exit GUI");
      }
    }
    else { //Online/Web mode
      console.log("Electron API not available, assume web mode");

      if (!(<any>window).pythonSourceVersion) {
        console.error("No python version defined, exit");
        return;
      }

      this.setGlobalVar("webSourceVersion", (<any>window).pythonSourceVersion);

      if ((<any>window).pythonSourceIsMasterVersion)
        this.setGlobalVar("webIsMasterVersion", (<any>window).pythonSourceIsMasterVersion);

      console.log("Web version: " + (<any>window).pythonSourceVersion + " ; master version:", this.getGlobalVar("webIsMasterVersion"));

      this.webInit();
    }
  }

  ngOnDestroy() {
    if ((<any>window).electronAvailable) {
      this.destroyElectronEvents();
    }
  }

  createElectronEvents() { //Electron only

    var self = this;

    let maximizedEvent = post.on('window-maximized', function (event) {
      let res = event.data;

      if (res == true)
        self.globalEmitter.emit({ name: "window_maximized" });
      else
        self.globalEmitter.emit({ name: "window_unmaximized" });
    });

    this.electronEvents.push(maximizedEvent);
  }

  createWebEvents() { //Web only

    var self = this;

    (<any>window).addEventListener('emscripten_cache_file_found', function (event) {

      let detail = event.detail;

      //Update settings entry for cached file and then refresh GUI
      if (detail) {

        if (detail.name == "ROM")
          self.generator_settingsMap["rom"] = "<using cached ROM>";
        else if (detail.name == "WAD")
          self.generator_settingsMap["web_wad_file"] = "<using cached WAD>";
        else if (detail.name == "COMMONKEY")
          self.generator_settingsMap["web_common_key_file"] = "<using cached common key>";

        self.globalEmitter.emit({ name: "refresh_gui" });
      }

    }, false);
  }

  destroyElectronEvents() {
    this.electronEvents.forEach(postRobotEvent => {
      postRobotEvent.cancel();
    });
  }

  electronInit() {
    this.electronLoadGeneratorGUISettings().then(() => {
      this.setGlobalVar("appReady", true);
      this.globalEmitter.emit({ name: "init_finished" });
    }).catch(err => {
      console.error("exit due error:", err);
    });
  }

  webInit() {
    this.webLoadGeneratorGUISettings().then(() => {
      this.setGlobalVar("appReady", true);
      this.globalEmitter.emit({ name: "init_finished" });
    }).catch(err => {
      console.error("exit due error:", err);
    });
  }

  setGlobalVar(key: string, value: any) {
    if (this.globalVars.has(key)) {
      this.globalVars.set(key, value);
    }
  }

  getGlobalVar(key: string) {

    if (this.globalVars.has(key))
      return this.globalVars.get(key);

    return "error";
  }

  copyToClipboard(content: string) {

    if (this.getGlobalVar('electronAvailable')) { //Electron
      post.send(window, 'copyToClipboard', { content: content }).then(event => {
        console.log('copied to clipboard');
      }).catch(err => {
        console.error(err);
      });
    }
    else { //Web
      let selBox = document.createElement('textarea');
      selBox.style.position = 'fixed';
      selBox.style.left = '0';
      selBox.style.top = '0';
      selBox.style.opacity = '0';
      selBox.value = content;

      document.body.appendChild(selBox);
      selBox.focus();
      selBox.select();
      document.execCommand('copy');

      document.body.removeChild(selBox);
    }
  }

  async browseForFile(fileTypes: any) { //Electron only

    if (!this.getGlobalVar('electronAvailable'))
      throw Error("electron_not_available");

    let event = await post.send(window, 'browseForFile', { fileTypes: fileTypes });
    let res = event.data;

    if (!res || res.length != 1 || !res[0] || res[0].length < 1)
      throw Error("dialog_cancelled");

    return res[0];
  }

  async browseForDirectory() { //Electron only

    if (!this.getGlobalVar('electronAvailable'))
      throw Error("electron_not_available");

    let event = await post.send(window, 'browseForDirectory');
    let res = event.data;

    if (!res || res.length != 1 || !res[0] || res[0].length < 1)
      throw Error("dialog_cancelled");

    return res[0];
  }

  async createAndOpenPath(path: string) { //Electron only

    if (!this.getGlobalVar('electronAvailable'))
      throw Error("electron_not_available");

    let event = await post.send(window, 'createAndOpenPath', path);
    let res = event.data;

    if (res == true)
      return true;
    else
      throw Error("path_not_opened");
  }

  minimizeWindow() { //Electron only

    if (!this.getGlobalVar('electronAvailable'))
      return;

    post.send(window, 'window-minimize').then(() => {
      console.log('window minimized');
    }).catch(err => {
      console.error(err);
    });
  }

  maximizeWindow() { //Electron only

    if (!this.getGlobalVar('electronAvailable'))
      return;

    post.send(window, 'window-maximize').then(() => {
      console.log('window maximize state updated');
    }).catch(err => {
      console.error(err);
    });
  }

  async isWindowMaximized() { //Electron only

    if (!this.getGlobalVar('electronAvailable'))
      throw Error("electron_not_available");

    try {
      let event = await post.send(window, 'window-is-maximized');
      let res = event.data;

      //console.log("window maximized state:", res);
      return res;
    }
    catch (err) {
      console.error(err);
      throw Error(err);
    }
  }

  closeWindow() { //Electron only

    if (!this.getGlobalVar('electronAvailable'))
      return;

    this.saveCurrentSettingsToFile();

    setTimeout(() => {

      post.send(window, 'window-close').then(() => {
        console.log('window closed');
      }).catch(err => {
        console.error(err);
      });
    });
  }

  async electronLoadGeneratorGUISettings() {

    var guiSettings = post.send(window, 'getGeneratorGUISettings');
    var lastUserSettings = post.send(window, 'getGeneratorGUILastUserSettings');

    try {
      var results = await Promise.all([guiSettings, lastUserSettings]);

      let res = JSON.parse(results[0].data);
      let userSettings = results[1].data;

      if (userSettings)
        userSettings = JSON.parse(userSettings);

      this.parseGeneratorGUISettings(res, userSettings);

    } catch (err) {
      console.error(err);
      throw Error(err);
    }
  }

  async webLoadGeneratorGUISettings() {

    var res = null;
    var userSettings = null;

    //Get generator settings
    if ((<any>window).webGeneratorSettingsMap) { //Master versions on the web pre-define a settings map to use before Angular will load
      res = (<any>window).webGeneratorSettingsMap;
      console.log("Settings map is available from the DOM");
    }
    else { //Dev versions on the web request a pre-built settings map from the server at runtime

      let url = (<any>window).location.protocol + "//" + (<any>window).location.host + "/angular/dev/" + this.getGlobalVar("webSourceVersion").replace(/ /g, "_") + "/utils/settings_list.json";
      console.log("Settings map is not available. Request it:", url);

      res = await this.http.get(url, { responseType: "json" }).toPromise();
    }

    //Get last user settings from browser cache for the appropriate app
    try {
      userSettings = localStorage.getItem(this.getGlobalVar("appType") == "generator" ? "generatorSettings_" + this.getGlobalVar("webSourceVersion") : "patcherSettings_" + this.getGlobalVar("webSourceVersion"));

      if (userSettings && userSettings.length > 0) {
        userSettings = JSON.parse(userSettings);
      }
      else { //Try the opposite app type to see if a cached settings map is available there
        userSettings = localStorage.getItem(this.getGlobalVar("appType") == "generator" ? "patcherSettings_" + this.getGlobalVar("webSourceVersion") : "generatorSettings_" + this.getGlobalVar("webSourceVersion"));

        if (userSettings && userSettings.length > 0) {
          userSettings = JSON.parse(userSettings);
        }
      }
    } catch (err) {
      console.error("Local storage not available");
    }

    //Get user presets if appType = generator
    if (this.getGlobalVar("appType") == "generator") {

      let userPresets = null;

      try {
        userPresets = localStorage.getItem("generatorPresets_" + this.getGlobalVar("webSourceVersion"));
      } catch { }

      if (userPresets && userPresets.length > 0) {

        userPresets = JSON.parse(userPresets);

        let adjustedUserPresets = {};

        //Tag user presets appropiately
        Object.keys(userPresets).forEach(presetName => {
          if (!(presetName in res.presets))
            adjustedUserPresets[presetName] = { settings: userPresets[presetName] };
        });

        Object.assign(res.presets, adjustedUserPresets);       
      }
    }

    this.parseGeneratorGUISettings(res, userSettings);

    //Check for cached files and then create web events after
    if ((<any>window).emscriptenFoundCachedROMFile)
      this.generator_settingsMap["rom"] = "<using cached ROM>";

    if ((<any>window).emscriptenFoundCachedWADFile)
      this.generator_settingsMap["web_wad_file"] = "<using cached WAD>";

    if ((<any>window).emscriptenFoundCachedCommonKeyFile)
      this.generator_settingsMap["web_common_key_file"] = "<using cached common key>";

    this.createWebEvents();
  }

  parseGeneratorGUISettings(guiSettings, userSettings) {

    const isRGBHex = /[0-9A-Fa-f]{6}/;

    //Intialize settings maps
    for (let tabIndex = 0; tabIndex < guiSettings.settingsArray.length; tabIndex++) {
      let tab = guiSettings.settingsArray[tabIndex];

      //Skip tabs that don't belong to this app and delete them from the guiSettings
      if ("app_type" in tab && tab.app_type && tab.app_type.indexOf(this.getGlobalVar("appType")) == -1) {

        guiSettings.settingsArray.splice(tabIndex, 1);
        tabIndex--;

        let index = guiSettings.cosmeticsArray.findIndex(entry => entry.name == tab.name);
        if (index != -1)
          guiSettings.cosmeticsArray.splice(index, 1);

        delete guiSettings.settingsObj[tab.name];
        delete guiSettings.cosmeticsObj[tab.name];

        continue;
      }

      this.generator_tabsVisibilityMap[tab.name] = true;

      tab.sections.forEach(section => {
        section.settings.forEach(setting => {

          this.generator_settingsVisibilityMap[setting.name] = true;

          if (setting.type == "SearchBox" && userSettings && setting.name in userSettings) { //Special parsing for SearchBox data

            let valueArray = [];

            userSettings[setting.name].forEach(entry => {

              let optionEntry = setting.options.find(option => {
                if (option.name == entry)
                  return true;

                return false;
              });

              if (optionEntry)
                valueArray.push(optionEntry);
            });

            this.generator_settingsMap[setting.name] = valueArray;
          }
          else if (setting.type == "Combobox" && userSettings && setting.name in userSettings) { //Ensure combobox option exists before applying it (in case of outdated settings being loaded)

            if (section.is_colors && typeof (userSettings[setting.name]) == "string" && isRGBHex.test(userSettings[setting.name])) { //Custom Color is treated as an exception
              this.generator_settingsMap[setting.name] = userSettings[setting.name];
            }
            else {
              let optionEntry = setting.options.find(option => {
                if (option.name == userSettings[setting.name])
                  return true;

                return false;
              });

              this.generator_settingsMap[setting.name] = optionEntry ? userSettings[setting.name] : setting.default;
            }
          }
          else if (userSettings && setting.name in userSettings && (setting.type == "Scale" || setting.type == "Numberinput")) { //Validate numberic values again before applying them
            this.verifyNumericSetting(userSettings, setting, false);
            this.generator_settingsMap[setting.name] = userSettings[setting.name];
          }
          else { //Everything else
            this.generator_settingsMap[setting.name] = userSettings && setting.name in userSettings ? userSettings[setting.name] : setting.default;
          }

          //Color section handling
          if (section.is_colors) {
            if (typeof (this.generator_settingsMap[setting.name]) == "string" && isRGBHex.test(this.generator_settingsMap[setting.name])) { //Resolve Custom Color
              this.generator_customColorMap[setting.name] = "#" + this.generator_settingsMap[setting.name];
              this.generator_settingsMap[setting.name] = "Custom Color";
            }
            else {
              this.generator_customColorMap[setting.name] = "";
            }
          }
        });
      });
    }

    //Add GUI only options
    this.generator_settingsMap["settings_string"] = userSettings && "settings_string" in userSettings ? userSettings["settings_string"] : "";
    this.generator_settingsVisibilityMap["settings_string"] = true;

    console.log("JSON Settings Data:", guiSettings);
    console.log("Last User Settings:", userSettings);
    console.log("Final Settings Map", this.generator_settingsMap);

    //Save settings after parsing them
    this.setGlobalVar('generatorSettingsArray', guiSettings.settingsArray);
    this.setGlobalVar('generatorSettingsObj', guiSettings.settingsObj);
    this.setGlobalVar('generatorCosmeticsArray', guiSettings.cosmeticsArray);
    this.setGlobalVar('generatorCosmeticsObj', guiSettings.cosmeticsObj);

    this.generator_presets = guiSettings.presets;
  }

  async versionCheck() { //Electron only

    if (!this.getGlobalVar('electronAvailable'))
      throw Error("electron_not_available");

    try {

      var event = await post.send(window, 'getCurrentSourceVersion');

      var res: string = event.data;
      var result = { hasUpdate: false, currentVersion: "", latestVersion: "" };

      if (res && res.length > 0) {

        console.log("Local:", res);
        result.currentVersion = res;

        this.globalEmitter.emit({ name: "local_version_checked", version: res });

        let branch = res.includes("Release") ? "master" : "Dev";
        var remoteFile = await this.http.get("https://raw.githubusercontent.com/TestRunnerSRL/OoT-Randomizer/" + branch + "/version.py", { responseType: "text" }).toPromise();

        let remoteVersion = remoteFile.substr(remoteFile.indexOf("'") + 1);
        remoteVersion = remoteVersion.substr(0, remoteVersion.indexOf("'"));

        console.log("Remote:", remoteVersion);
        result.latestVersion = remoteVersion;

        let currentSplit = res.replace('v', '').replace(' ', '.').split('.');
        let remoteSplit = remoteVersion.replace('v', '').replace(' ', '.').split('.');

        //Compare versions
        if (Number(remoteSplit[0]) > Number(currentSplit[0])) {
          result.hasUpdate = true;
        }
        else if (Number(remoteSplit[0]) == Number(currentSplit[0])) {
          if (Number(remoteSplit[1]) > Number(currentSplit[1])) {
            result.hasUpdate = true;
          }
          else if (Number(remoteSplit[1]) == Number(currentSplit[1])) {
            if (Number(remoteSplit[2]) > Number(currentSplit[2])) {
              result.hasUpdate = true;
            }
          }
        }

        return result;  
      }
      else {
        return result;
      }
    }
    catch (err) {
      console.error(err);
      throw Error(err);
    }
  }

  verifyNumericSetting(settingsFile: any, setting: any, syncToGlobalMap: boolean = false) {

    let settingValue: any = settingsFile[setting.name];
    let error = false;
    let didCast = false;

    if (typeof (settingValue) != "string" && typeof (settingValue) != "number") { //Can't recover, bad type
      error = true;
    }
    else if (typeof (settingValue) == "string") { //Try to cast it

      if (Number(parseInt(settingValue)) != Number(settingValue)) { //Cast failed, not numeric    
        error = true;
      }
      else {
        settingValue = parseInt(settingValue);
        didCast = true;
      }
    }

    if (!error) {

      //Min/Max check
      let settingMin: number = setting["min"];
      let settingMax: number = setting["max"];

      if (("min" in setting) && settingValue < settingMin) {

        settingsFile[setting.name]  = settingMin;

        if (syncToGlobalMap) { //Global too if needed and refresh GUI after to signal change
          this.generator_settingsMap[setting.name] = settingMin;
          this.globalEmitter.emit({ name: "refresh_gui" });
        }

        error = true;
      }
      else if (("max" in setting) && settingValue > settingMax) {

        settingsFile[setting.name]  = settingMax;

        if (syncToGlobalMap) { //Global too if needed and refresh GUI after to signal change
          this.generator_settingsMap[setting.name] = settingMax;
          this.globalEmitter.emit({ name: "refresh_gui" });
        }

        error = true;
      }

      if (!error && didCast) { //No error, but setting had to be casted from string, fix it
        settingsFile[setting.name] = settingValue;

        if (syncToGlobalMap) { //Global too if needed and refresh GUI after to signal change
          this.generator_settingsMap[setting.name] = settingValue;
          this.globalEmitter.emit({ name: "refresh_gui" });
        }
      }
    }
    else { //Critical error, reset local value to default
      settingsFile[setting.name] = setting.default;

      if (syncToGlobalMap) { //Global too if needed and refresh GUI after to signal change
        this.generator_settingsMap[setting.name] = setting.default;
        this.globalEmitter.emit({ name: "refresh_gui" });
      }
    }

    return error;
  }

  applySettingsObject(settingsObj) {

    if (!settingsObj)
      return;

    const isRGBHex = /[0-9A-Fa-f]{6}/;

    this.getGlobalVar('generatorSettingsArray').forEach(tab => {
      tab.sections.forEach(section => {
        section.settings.forEach(setting => {

          if (setting.name in settingsObj) {

            if (setting.type == "SearchBox") { //Special parsing for SearchBox data

              let valueArray = [];

              settingsObj[setting.name].forEach(entry => {

                let optionEntry = setting.options.find(option => {
                  if (option.name == entry)
                    return true;

                  return false;
                });

                if (optionEntry)
                  valueArray.push(optionEntry);
              });

              this.generator_settingsMap[setting.name] = valueArray;
            }
            else if (setting.type == "Combobox") { //Ensure combobox option exists before applying it (in case of outdated settings being loaded)

              let optionEntry = setting.options.find(option => {
                if (option.name == settingsObj[setting.name])
                  return true;

                return false;
              });

              if (optionEntry)
                this.generator_settingsMap[setting.name] = settingsObj[setting.name];
            }
            else if (setting.type == "Scale" || setting.type == "Numberinput") { //Validate numberic values again before applying them
              this.verifyNumericSetting(settingsObj, setting, false);
              this.generator_settingsMap[setting.name] = settingsObj[setting.name];
            }
            else { //Everything else
              this.generator_settingsMap[setting.name] = settingsObj[setting.name];
            }

            //Color section handling
            if (section.is_colors) {

              if (typeof (settingsObj[setting.name]) == "string" && isRGBHex.test(settingsObj[setting.name])) { //Resolve Custom Color
                this.generator_customColorMap[setting.name] = "#" + settingsObj[setting.name];
                this.generator_settingsMap[setting.name] = "Custom Color";
              }
              else {
                this.generator_customColorMap[setting.name] = "";
              }
            }
          }
        });
      });
    });
  }

  applyDefaultSettings() {

    let cleanSettings = this.createSettingsFileObject(false, true, !this.getGlobalVar('electronAvailable'));

    this.getGlobalVar('generatorSettingsArray').forEach(tab => {
      tab.sections.forEach(section => {
        section.settings.forEach(setting => {

          if (setting.name in cleanSettings) {
            this.generator_settingsMap[setting.name] = setting.default; 
          }
        });
      });
    });
  }

  deleteSettingsFromMapWithCondition(settingsMap: any, keyName: string, keyValue: any) {

    this.getGlobalVar("generatorSettingsArray").forEach(tab => {

      tab.sections.forEach(section => {
        section.settings.forEach(setting => {

          if (keyName in setting && setting[keyName] == keyValue) {
            delete settingsMap[setting.name];
          }
        });
      });
    });
  }

  createSettingsFileObject(includeFromPatchFileSettings: boolean = true, includeSeedSettingsOnly: boolean = false, sanitizeForBrowserCache: boolean = false, cancelWhenError: boolean = false) {

    let settingsFile: any = {};

    Object.assign(settingsFile, this.generator_settingsMap);

    //Add in custom colors
    Object.keys(this.generator_customColorMap).forEach(colorSettingName => {
      if (this.generator_customColorMap[colorSettingName].length > 0 && settingsFile[colorSettingName] === "Custom Color") {
        settingsFile[colorSettingName] = this.generator_customColorMap[colorSettingName].substr(1);
      }
    });

    let invalidSettingsList = [];

    //Resolve search box entries (name only)
    this.getGlobalVar("generatorSettingsArray").forEach(tab => {

      tab.sections.forEach(section => {
        section.settings.forEach(setting => {

          if (setting.type == "SearchBox") {

            let valueArray = [];

            settingsFile[setting.name].forEach(entry => {
              valueArray.push(entry.name);
            });

            settingsFile[setting.name] = valueArray;
          }
          else if (setting.type == "Scale" || setting.type == "Numberinput") { //Validate numberic values again before saving them

            let error = this.verifyNumericSetting(settingsFile, setting, true);

            if (error) { //Input could not be recovered, abort
              invalidSettingsList.push(setting.text);
            }       
          }     
        });
      });
    });

    //Abort if any invalid settings were found
    if (invalidSettingsList && invalidSettingsList.length > 0) {
      this.globalEmitter.emit({ name: "dialog_error", message: "Some invalid settings were detected and had to be reset! This can happen if you type too fast into an input box. Please try again. The following settings were affected: " + invalidSettingsList.join(", ") });

      if (cancelWhenError)
        return null;
    }

    //Delete keys the python source doesn't need
    delete settingsFile["presets"];
    delete settingsFile["open_output_dir"];
    delete settingsFile["open_python_dir"];
    delete settingsFile["open_wiki_readme"];
    delete settingsFile["generate_from_file"];

    //Delete fromPatchFile keys if mode is fromSeed
    if (!includeFromPatchFileSettings) {
      delete settingsFile["patch_file"];
      delete settingsFile["repatch_cosmetics"];

      //Web only keys
      if (!this.getGlobalVar('electronAvailable')) {
        delete settingsFile["web_persist_in_cache"];
      }
    }

    //Delete keys not included in the seed
    if (includeSeedSettingsOnly) {

      //Not mapped settings need to be deleted manually
      delete settingsFile["settings_string"];

      //Delete all shared = false keys from map since they aren't included in the seed
      this.deleteSettingsFromMapWithCondition(settingsFile, "shared", false);
    }

    //Delete keys the browser can't save (web only)
    if (sanitizeForBrowserCache) {

      //Delete all settings of type Fileinput/Directoryinput. File objects can not be saved due browser sandbox
      this.deleteSettingsFromMapWithCondition(settingsFile, "type", "Fileinput");
      this.deleteSettingsFromMapWithCondition(settingsFile, "type", "Directoryinput");
    }

    return settingsFile;
  }

  saveCurrentSettingsToFile() {

    if (this.getGlobalVar('electronAvailable')) { //Electron
      post.send(window, 'saveCurrentSettingsToFile', this.createSettingsFileObject()).then(event => {
        console.log("settings saved to file");
      }).catch(err => {
        console.error(err);
      });
    }
    else { //Web
      try {
        localStorage.setItem(this.getGlobalVar("appType") == "generator" ? "generatorSettings_" + this.getGlobalVar("webSourceVersion") : "patcherSettings_" + this.getGlobalVar("webSourceVersion"), JSON.stringify(this.createSettingsFileObject(true, false, true)));
      } catch { }
    }
  }

  convertSettingsToString() {
    var self = this;

    return new Promise<string>(function (resolve, reject) {

      if (self.getGlobalVar('electronAvailable')) { //Electron

        post.send(window, 'convertSettingsToString', self.createSettingsFileObject(false, true)).then(event => {

          var listenerSuccess = post.once('convertSettingsToStringSuccess', function (event) {

            listenerError.cancel();

            let data = event.data;
            resolve(data);
          });

          var listenerError = post.once('convertSettingsToStringError', function (event) {

            listenerSuccess.cancel();

            let data = event.data;

            console.error("[convertSettingsToString] Python Error:", data);
            reject(data);
          });

        }).catch(err => {
          console.error("[convertSettingsToString] Post-Robot Error:", err);
          reject(err);
        });
      }
      else { //Web
        let url = (<any>window).location.protocol + "//" + (<any>window).location.host + "/settings/parse?version=" + self.getGlobalVar("webSourceVersion");
        console.log("Request string from:", url);

        self.http.post(url, JSON.stringify(self.createSettingsFileObject(false, true, true)), { responseType: "text", headers: { "Content-Type": "application/json" } }).toPromise().then(res => {
          resolve(res);
        }).catch(err => {
          console.error("[convertSettingsToString] Web Error:", err);
          reject(err);
        });
      }
    });
  }

  convertStringToSettings(settingsString: string) {
    var self = this;

    return new Promise(function (resolve, reject) {

      if (self.getGlobalVar('electronAvailable')) { //Electron

        post.send(window, 'convertStringToSettings', settingsString).then(event => {

          var listenerSuccess = post.once('convertStringToSettingsSuccess', function (event) {

            listenerError.cancel();

            let data = JSON.parse(event.data);
            resolve(data);
          });

          var listenerError = post.once('convertStringToSettingsError', function (event) {

            listenerSuccess.cancel();

            let data = event.data;

            console.error("[convertStringToSettings] Python Error:", data);
            reject(data);
          });

        }).catch(err => {
          console.error("[convertStringToSettings] Post-Robot Error:", err);
          reject(err);
        });
      }
      else { //Web
        let url = (<any>window).location.protocol + "//" + (<any>window).location.host + "/settings/get?version=" + self.getGlobalVar("webSourceVersion") + "&settingsString=" + settingsString;
        console.log("Request settings from:", url);

        self.http.get(url, { responseType: "json" }).toPromise().then(res => {
          resolve(res);
        }).catch(err => {
          console.error("[convertStringToSettings] Web Error:", err);
          reject(err);
        });
      }
    });
  }

  createPresetFileObject() {

    let presetsFile: any = {};

    //Create presets object
    Object.keys(this.generator_presets).forEach(presetKey => {
      let preset = this.generator_presets[presetKey];

      if (!("isNewPreset" in preset) && !("isDefaultPreset" in preset) && !("isProtectedPreset" in preset) && ("settings" in preset) && typeof (preset.settings) == "object" && Object.keys(preset.settings).length > 0) {
        //console.log("store " + presetKey, preset.settings);
        presetsFile[presetKey] = preset.settings;
      }
    });

    return presetsFile;
  }

  saveCurrentPresetsToFile() {

    if (this.getGlobalVar('electronAvailable')) { //Electron
      post.send(window, 'saveCurrentPresetsToFile', JSON.stringify(this.createPresetFileObject(), null, 4)).then(event => {
        console.log("presets saved to file");
      }).catch(err => {
        console.error(err);
      });
    }
    else { //Web
      if (this.getGlobalVar("appType") == "generator") { //Generator only
        try {
          localStorage.setItem("generatorPresets_" + this.getGlobalVar("webSourceVersion"), JSON.stringify(this.createPresetFileObject(), null, 4));
        } catch { }
      }
    }
  }

  generateSeedElectron(progressWindowRef: ProgressWindow, fromPatchFile: boolean = false, useStaticSeed: string = "") { //Electron only
    var self = this;

    return new Promise(function (resolve, reject) {

      let settingsMap = self.createSettingsFileObject(fromPatchFile, false, false, true);

      if (!settingsMap) {
        reject({ short: "Generation aborted.", long: "Generation aborted." });
        return;
      }

      post.send(window, 'generateSeed', { settingsFile: settingsMap, staticSeed: useStaticSeed }).then(event => {

        var listenerProgress = post.on('generateSeedProgress', function (event) {

          let data = event.data;

          //console.log("progress report", data);

          if (progressWindowRef) {
            progressWindowRef.currentGenerationIndex = data.generationIndex;
            progressWindowRef.progressPercentageCurrent = data.progressCurrent;
            progressWindowRef.progressPercentageTotal = data.progressTotal;
            progressWindowRef.progressMessage = data.message;
            progressWindowRef.refreshLayout();
          }
        });

        var listenerSuccess = post.once('generateSeedSuccess', function (event) {

          listenerProgress.cancel();
          listenerCancel.cancel();
          listenerError.cancel();

          let data = event.data;
          resolve();
        });

        var listenerError = post.once('generateSeedError', function (event) {

          listenerProgress.cancel();
          listenerCancel.cancel();
          listenerSuccess.cancel();

          let data = event.data;

          console.error("[generateSeedElectron] Python Error:", data);
          reject(data);
        });

        var listenerCancel = post.once('generateSeedCancelled', function (event) {

          listenerProgress.cancel();
          listenerSuccess.cancel();
          listenerError.cancel();

          reject({ short: "Generation cancelled.", long: "Generation cancelled." });
        });
      }).catch(err => {
        console.error("[generateSeedElectron] Post-Robot Error:", err);
        reject({ short: err, long: err });
      });
    });
  }

  async cancelGenerateSeedElectron() { //Electron only

    if (!this.getGlobalVar('electronAvailable'))
      throw Error("electron_not_available");

    try {

      let event = await post.send(window, 'cancelGenerateSeed');
      let data = event.data;

      if (data == true)
        return;
      else
        throw Error("cancel_failed");
    }
    catch (err) {
      console.error("[cancelGenerateSeedElectron] Couldn't cancel due Post-Robot Error:", err);
      throw Error(err);
    }
  }

  readFileIntoMemoryWeb(fileObject: any, useArrayBuffer: boolean) { //Web only

    return new Promise<any>(function (resolve, reject) {

      let fileReader = new FileReader();
      fileReader.onabort = function (event) {
        console.error("Loading of the file was aborted unexpectedly!");
        reject();
      };
      fileReader.onerror = function (event) {
        console.error("An error occurred during the loading of the file!");
        reject();
      };
      fileReader.onload = function (event) {

        console.log("Read in file successfully");
        resolve(event.target["result"]); 
      };

      if (useArrayBuffer)
        fileReader.readAsArrayBuffer(fileObject);
      else
        fileReader.readAsText(fileObject);
    });
  }

  async generateSeedWeb(raceSeed: boolean = false, useStaticSeed: string = "") { //Web only

    //Plando Logic
    let plandoFile = null;
    if (this.generator_settingsMap["enable_distribution_file"]) {

      plandoFile = this.generator_settingsMap["distribution_file"];

      if (plandoFile && typeof (plandoFile) == "object" && plandoFile.name && plandoFile.name.length > 0) {

        if (plandoFile.name.toLowerCase().endsWith(".z64") || plandoFile.name.toLowerCase().endsWith(".n64") || plandoFile.name.toLowerCase().endsWith(".v64")) { //Not a ROM check...
          throw { error_rom_in_plando: "Your Ocarina of Time ROM doesn't belong in the plandomizer setting. This entirely optional setting is used to plan out seeds before generation by manipulating spoiler log files. If you want to generate a normal seed instead, please click YES!" };
        }

        if (raceSeed) { //No support for race seeds
          throw { error: "Plandomizer is currently not supported for race seeds due security concerns. Please use a normal seed instead!" };
        }

        //Try to resolve the distribution file by reading it into memory
        console.log("Read Plando JSON file: " + plandoFile.name);

        let plandoFileJSON;

        try {
          plandoFileJSON = await this.readFileIntoMemoryWeb(plandoFile, false);
        }
        catch (ex) {
          throw { error: "An error occurred during the loading of the plandomizer file! Please try to enter it again." };
        }

        if (!plandoFileJSON || plandoFileJSON.length < 1) {
          throw { error: "The plandomizer file specified is not valid!" };
        }

        if (plandoFileJSON.length > 500000) { //Impose size limit to avoid server overload
          throw { error: "The plandomizer file specified is too big! The maximum file size allowed is 500 KB." };
        }

        //Test JSON parse it
        try {
          let plandoFileParsed = JSON.parse(plandoFileJSON);

          if (!plandoFileParsed || Object.keys(plandoFileParsed).length < 1) {
            throw { error: "The plandomizer file specified is not valid JSON! Please verify the syntax." };
          }
        }
        catch (err) {
          console.error(err);
          throw { error: "The plandomizer file specified is not valid JSON! Please verify the syntax. Detail: " + err.message };
        }

        plandoFile = plandoFileJSON;
      }
      else {
        plandoFile = null;
      }
    }

    let settingsFile = this.createSettingsFileObject(false, false, true, true);

    if (!settingsFile) {
      throw { error: "The generation was aborted due to previous errors!" };
    }

    //Add distribution file back into map as string if available, else clear it
    if (plandoFile) {
      settingsFile["distribution_file"] = plandoFile;
    }
    else {
      settingsFile["enable_distribution_file"] = false;
      settingsFile["distribution_file"] = "";
    }

    if (raceSeed) {
      useStaticSeed = ""; //Static seeds aren't allowed in race mode
      settingsFile["create_spoiler"] = true; //Force spoiler mode to on
      settingsFile["encrypt"] = true;
    }
    else {
      delete settingsFile["encrypt"];
    }

    if (useStaticSeed) {
      console.log("Use Static Seed:", useStaticSeed);
      settingsFile["seed"] = useStaticSeed;
    }
    else {
      delete settingsFile["seed"];
    }

    console.log(settingsFile);
    console.log("Race Seed:", raceSeed);

    //Request Seed Generation
    let url = (<any>window).location.protocol + "//" + (<any>window).location.host + "/seed/create?version=" + this.getGlobalVar("webSourceVersion");
    console.log("Request seed id from:", url);

    try {
      let res = await this.http.post(url, JSON.stringify(settingsFile), { responseType: "text", headers: { "Content-Type": "application/json" } }).toPromise();
      return res;
    }
    catch (err) {
      console.error("[generateSeedWeb] Web Error:", err);
      throw err;
    }
  }

  patchROMWeb() { //Web only
 
    let settingsFile = this.createSettingsFileObject(true, false, false, true);

    if (!settingsFile) {
      return;
    }

    if (typeof (<any>window).patchROM === "function") //Try to call patchROM function on the DOM
      (<any>window).patchROM(5, settingsFile); //Patch Version 5
    else
      console.error("[patchROMWeb] Patcher not available!");
  }
}
