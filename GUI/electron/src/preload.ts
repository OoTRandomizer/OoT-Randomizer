import * as electron from 'electron';
import * as remote from '@electron/remote';
import * as os from "os";
import * as fs from 'fs';
import * as path from 'path';

import * as post from 'post-robot';

const generator = remote.require(path.join(__dirname, '../src/modules/generator.js'));
const commander = remote.getGlobal("commandLineArgs");

var testMode = commander.release || remote.app.isPackaged ? false : true;
console.log("Test Mode:", testMode);

var platform = os.platform();
console.log("Platform:", platform);

var pythonPath = commander.python ? '"' + commander.python + '"' : platform == "win32" ? "py" : "python3";
var pythonSourcePath = path.normalize(remote.app.isPackaged ? remote.app.getAppPath() + "/python/" : remote.app.getAppPath() + "/../");
var pythonGeneratorPath = pythonSourcePath + "OoTRandomizer.py";
var pythonSettingsToJsonPath = pythonSourcePath + "SettingsToJson.py";

console.log("Python Executable Path:", pythonPath);
console.log("Python Source Path:", pythonGeneratorPath);

//Enable API in client window
electron.webFrame.executeJavaScript('window.electronAvailable = true;');
electron.webFrame.executeJavaScript('window.apiTestMode = ' + testMode + ';');
electron.webFrame.executeJavaScript('window.apiPlatform = "' + platform + '";');

//ELECTRON EVENTS
remote.getCurrentWindow().on('maximize', () => {
  post.send(window, 'window-maximized', true);
});
remote.getCurrentWindow().on('enter-full-screen', () => { //macOS exclusive
  post.send(window, 'window-maximized', true);
});
remote.getCurrentWindow().on('enter-html-full-screen', () => {
  post.send(window, 'window-maximized', true);
});

remote.getCurrentWindow().on('unmaximize', () => {
  post.send(window, 'window-maximized', false);
});
remote.getCurrentWindow().on('leave-full-screen', () => {
  post.send(window, 'window-maximized', false);
});
remote.getCurrentWindow().on('leave-html-full-screen', () => {
  post.send(window, 'window-maximized', false);
});


//FUNCTIONS
function dumpSettingsToFile(settingsObj) {
  settingsObj["check_version"] = true;
  fs.writeFileSync(pythonSourcePath + "settings.sav", JSON.stringify(settingsObj, null, 4));
}

function dumpPresetsToFile(presetsString: string) {
  fs.writeFileSync(pythonSourcePath + "presets.sav", presetsString);
}

function displayPythonErrorAndExit(notPython3: boolean = false) {

  setTimeout(() => {

    if (notPython3)
      alert("The Python version used to run the GUI is not supported! Please ensure you have Python 3.6 or higher installed. You can specify the path to python using the 'python <path>' command line switch!");
    else
      alert("Please ensure you have Python 3.6 or higher installed before running the GUI. You can specify the path to python using the 'python <path>' command line switch!");

    remote.app.quit();
  }, 500);
}

function readSettingsFromFile() {

  let path = pythonSourcePath + "settings.sav";

  if (fs.existsSync(path))
    return fs.readFileSync(path, 'utf8');
  else
    return false;
}

//POST ROBOT
post.on('getCurrentSourceVersion', function (event) {
  type VersionData = {
    baseVersion: string;
    supplementaryVersion: number;
    fullVersion: string;
    branchUrl: string;
  };

  let versionFilePath = pythonSourcePath + "version.py"; //Read version.py from the python source
  let data: VersionData = { baseVersion : "", supplementaryVersion : 0, fullVersion : "", branchUrl : "" }

  if (fs.existsSync(versionFilePath)) {
    let versionFile = fs.readFileSync(versionFilePath, 'utf8');

    let baseMatch = versionFile.match(/^[ \t]*__version__ = ['"](.+)['"]/m);
    let supplementaryMatch = versionFile.match(/^[ \t]*supplementary_version = (\d+)$/m);
    let fullMatch = versionFile.match(/^[ \t]*__version__ = f['"]*(.+)['"]/m);
    let urlMatch = versionFile.match(/^[ \t]*branch_url = ['"](.+)['"]/m);

    data.baseVersion = baseMatch != null && baseMatch[1] !== undefined ? baseMatch[1] : "";
    data.supplementaryVersion = supplementaryMatch != null && supplementaryMatch[1] !== undefined ? parseInt(supplementaryMatch[1]) : 0;
    data.fullVersion = fullMatch != null && fullMatch[1] !== undefined ? fullMatch[1] : data.baseVersion;
    data.fullVersion = data.fullVersion
      .replace('{base_version}', data.baseVersion)
      .replace('{supplementary_version}', data.supplementaryVersion.toString())
    data.branchUrl = urlMatch != null && urlMatch[1] !== undefined ? urlMatch[1] : "";

    return data;
  }
  else {
    return null;
  }
});

post.on('getGeneratorGUISettings', function (event) {

  return electron.ipcRenderer.sendSync('getGeneratorGUISettings');
});

post.on('getGeneratorGUILastUserSettings', function (event) {

  return readSettingsFromFile();
});

post.on('copyToClipboard', function (event) {

  let data = event.data;

  if (!data || typeof (data) != "object" || Object.keys(data).length != 1 || !data["content"] || typeof (data["content"]) != "string" || data["content"].length < 1)
    return false;

  remote.clipboard.writeText(data.content);

  return true;
});

post.on('browseForFile', function (event) {

  let data = event.data;

  if (!data || typeof (data) != "object" || Object.keys(data).length != 1 || !data["fileTypes"] || typeof (data["fileTypes"]) != "object")
    return false;

  return remote.dialog.showOpenDialogSync({ filters: data.fileTypes, properties: ["openFile", "treatPackageAsDirectory"]});
});


post.on('browseForDirectory', function (event) {
  return remote.dialog.showOpenDialogSync({ properties: ["openDirectory", "createDirectory", "treatPackageAsDirectory"] });
});

post.on('createAndOpenPath', function (event) {

  let data = event.data;

  //Use python dir if not specified otherwise
  if (!data || typeof (data) != "string" || data.length < 1) {
    data = pythonSourcePath;
  }
  else {
    if (!path.isAbsolute(data))
      data = pythonSourcePath + data;
  }

  if (fs.existsSync(data)) {
    remote.shell.openPath(data);
    return true;
  }
  else {
    fs.mkdirSync(data);

    remote.shell.openPath(data).then(res => {
      post.send(window, 'createAndOpenPathResult', res);
    });

    return false;
  }
});

post.on('window-minimize', function (event) {
  remote.getCurrentWindow().minimize();
});

post.on('window-maximize', function (event) {

  let currentWindow = remote.getCurrentWindow();

  if (currentWindow.isMaximized()) {
    currentWindow.unmaximize();
  }
  else {
    currentWindow.maximize();
  }
});

post.on('window-is-maximized', function (event) {
  return remote.getCurrentWindow().isMaximized();
});

post.on('window-close', function (event) {

  //Only close the window on macOS, on every other OS exit immediately
  if (os.platform() == "darwin") {
    remote.getCurrentWindow().close();
  }
  else {
    remote.app.quit();
  }
});

post.on('saveCurrentSettingsToFile', function (event) {

  let data = event.data;

  if (!data || typeof (data) != "object" || Object.keys(data).length < 1)
    return false;

  //Write settings obj to settings.sav
  dumpSettingsToFile(data);
});

post.on('convertSettingsToString', function (event) {

  let data = event.data;

  if (!data || typeof (data) != "object" || Object.keys(data).length < 1)
    return false;

  //Write settings obj to settings.sav
  dumpSettingsToFile(data);

  //console.log("generate string with settings obj", data);

  generator.parseSettings(pythonPath, pythonGeneratorPath).then(res => {
    //console.log('[Preload] Success');

    post.send(window, 'convertSettingsToStringSuccess', res);
  }).catch((err) => {

    if (err.includes("ImportError: No module named tkinter")) {
      displayPythonErrorAndExit(true);
    }

    post.send(window, 'convertSettingsToStringError', err);
  });

  return true;
});

post.on('updateDynamicSetting', function (event) {
  let data = event.data;

  if (!data || typeof (data) != "string" || data.length < 1)
    return false;

  //console.log("get settings from string", data);

  generator.getUpdatedDynamicSetting(pythonPath, pythonSettingsToJsonPath, data).then(res => {
    //console.log('[Preload] Success');
      post.send(window, 'updateDynamicSettingSuccess', res);
      
  }).catch((err) => {
      post.send(window, 'updateDynamicSettingError', err);
  })
})

post.on('convertStringToSettings', function (event) {

  let data = event.data;

  if (!data || typeof (data) != "string" || data.length < 1)
    return false;

  //console.log("get settings from string", data);

  generator.getSettings(pythonPath, pythonGeneratorPath, data).then(res => {
    //console.log('[Preload] Success');

    post.send(window, 'convertStringToSettingsSuccess', res);
  }).catch((err) => {

    if (err.includes("ImportError: No module named tkinter")) {
      displayPythonErrorAndExit(true);
    }

    post.send(window, 'convertStringToSettingsError', err);
  });

  return true;
});

post.on('saveCurrentPresetsToFile', function (event) {

  let data = event.data;

  if (!data || typeof (data) != "string" || data.length < 1)
    return false;

  //Write file contents to presets.sav
  dumpPresetsToFile(data);

  //console.log("presets saved to .sav");
});

post.on('generateSeed', function (event) {

  let data = event.data;

  if (!data || typeof (data) != "object" || Object.keys(data).length != 2 || !("settingsFile" in data) || !("staticSeed" in data))
    return false;

  let settingsFile = data.settingsFile;

  if (!settingsFile || typeof (settingsFile) != "object" || Object.keys(settingsFile).length < 1)
    return false;

  //Write settings obj to settings.sav
  dumpSettingsToFile(settingsFile);

  //console.log("generate seed with settings:", data);

  generator.romBuilding(pythonPath, pythonGeneratorPath, data).then(res => {
    //console.log('[Preload] Success');
    post.send(window, 'generateSeedSuccess', res);
  }).catch((err) => {

    if (err.long.includes("ImportError: No module named tkinter")) {
      displayPythonErrorAndExit(true);
    }

    if (err.short == "user_cancelled")
      post.send(window, 'generateSeedCancelled');
    else
      post.send(window, 'generateSeedError', err);
  });

  return true;
});

post.on('cancelGenerateSeed', function (event) {

  if (generator.cancelRomBuilding())
    return true;

  return false;
});

//GENERATOR EVENTS
generator.on("patchJobProgress", status => {
  //console.log("Patch job reports in at " + status.progress + "%! Message: " + status.message);
  post.send(window, 'generateSeedProgress', status);
});


//STARTUP
//Test if we are in the proper path, else exit
if (fs.existsSync(pythonGeneratorPath)) {
  electron.webFrame.executeJavaScript('window.apiPythonSourceFound = true;');
}
else {
  alert("The GUI is not placed in the correct location...");
  remote.app.quit();
}

//Test if python executable exists and can be called
generator.testPythonPath(pythonPath).then(() => {
  console.log("Python executable confirmed working");
}).catch(err => {
  console.error(err);
  displayPythonErrorAndExit();
});