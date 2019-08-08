const fs = require('fs');
const EventEmitter = require('events').EventEmitter;
const spawn = require('child_process').spawn;
const treeKill = require('tree-kill');

//Rom Building global vars
var romBuildingGenerator = null;
var romBuildingUserCancelled = false;

function promiseFromChildProcess(child) {
  return new Promise(function (resolve, reject) {
    child.addListener("error", reject);
    child.addListener("exit", resolve);
  });
}

function isMulti(args) {

  if (("world_count" in args) && args["world_count"] > 1)
    return true;

  return false;
}

function romBuilding(pythonPath, randoPath, settings) {

  var settingsObj = settings.settingsFile;
  var seedString = settings.staticSeed;

  //Kill existing generation if one exists
  if (romBuildingGenerator) {
    romBuildingUserCancelled = true;
    treeKill(romBuildingGenerator.pid);
  }

  return new Promise(function (resolve, reject) {

    let error = false;
    let errorMsg = "";
    let errorMsgFull = "";

    var isMultiWorld = isMulti(settingsObj);
    var percentagePerGeneration = settingsObj["count"] && settingsObj["count"] > 0 ? 100 / settingsObj["count"] : 100;
    var percentagePerWorldTotal = isMultiWorld ? (percentagePerGeneration / 5) / settingsObj["world_count"] : percentagePerGeneration / 5;
    var percentagePerWorldLocal = isMultiWorld ? 20 / settingsObj["world_count"] : 20;
    var maxWorldCount = isMultiWorld ? settingsObj["world_count"] : 1;

    var currentWorld = 1;
    var currentGeneration = 1;
    var lockGenerationCounter = false;
    var currentGenerationPercentage = 0;
    var nextGenerationPercentage = 0;

    var compressionTotalFiles = -1;
    var compressionPercentagePerFileLocal = -1;
    var compressionPercentagePerFileTotal = -1;

    //console.log("Trigger spawn");

    //Using a user defined static seed
    if (seedString.length > 0) {

      let args = ['--seed', seedString];
      //args["checked_version"] = false;

      romBuildingGenerator = spawn('"' + pythonPath + '"' + ' ' + '"' + randoPath + '"', args, { shell: true });
    }
    else { //Random Seed
      romBuildingGenerator = spawn('"' + pythonPath + '"' + ' ' + '"' + randoPath + '"', { shell: true });
    }

    romBuildingGenerator.on('error', err => {
      console.error("[romBuilding] Error spawning process:", err);
      romBuildingGenerator = null;
      reject({ short: err, long: err });
    });

    function handleMessage(data) {

      if (error == true)
        return;

      if (data.toString().includes("Generating World")) {
        currentGenerationPercentage = nextGenerationPercentage;

        module.exports.emit('patchJobProgress', { generationIndex: currentGeneration, progressCurrent: currentWorld * percentagePerWorldLocal, progressTotal: Math.floor(currentGenerationPercentage + (currentWorld * percentagePerWorldTotal)), message: data.toString().split("\n")[0] });

        if (currentWorld < maxWorldCount)
          currentWorld++;
      }
      else if (data.toString().includes("Fill the world")) {
        module.exports.emit('patchJobProgress', { generationIndex: currentGeneration, progressCurrent: 33, progressTotal: Math.floor(currentGenerationPercentage + (percentagePerGeneration / 3)), message: data.toString().split("\n")[0] });

        lockGenerationCounter = false;
        currentWorld = 1;
        compressionTotalFiles = -1;
        compressionPercentagePerFileLocal = -1;
        compressionPercentagePerFileTotal = -1;
      }
      else if (data.toString().includes("Unique dungeon items placed")) {
        module.exports.emit('patchJobProgress', { generationIndex: currentGeneration, progressCurrent: 50, progressTotal: Math.floor(currentGenerationPercentage + (percentagePerGeneration / 2)), message: data.toString().split("\n")[0] });
      }
      else if (data.toString().includes("Calculating playthrough")) {
        module.exports.emit('patchJobProgress', { generationIndex: currentGeneration, progressCurrent: 66, progressTotal: Math.floor(currentGenerationPercentage + (percentagePerGeneration / 1.5)), message: data.toString().split("\n")[0] });

        if (!lockGenerationCounter) {
          nextGenerationPercentage = percentagePerGeneration * currentGeneration;
          currentGeneration++;
        }

        lockGenerationCounter = true;
      }
      else if (data.toString().includes("Patching ROM")) {
        module.exports.emit('patchJobProgress', { generationIndex: lockGenerationCounter ? currentGeneration - 1 : currentGeneration, progressCurrent: 80, progressTotal: Math.floor(currentGenerationPercentage + (percentagePerGeneration / 1.25)), message: data.toString().split("\n")[0] });

        if (!lockGenerationCounter) {
          nextGenerationPercentage = percentagePerGeneration * currentGeneration;
          currentGeneration++;
        }

        lockGenerationCounter = true;
      }
      else if (data.toString().includes("Starting compression")) {
        module.exports.emit('patchJobProgress', { generationIndex: currentGeneration - 1, progressCurrent: 83, progressTotal: Math.floor(currentGenerationPercentage + (percentagePerGeneration / 1.2)), message: data.toString().split("\n")[0] });
      }
      else if (data.toString().includes("files remaining")) {

        let filesRemaining = parseInt(data.toString().substr(0, data.toString().indexOf("files") - 1));

        if (compressionTotalFiles == -1) {
          compressionTotalFiles = filesRemaining;
          compressionPercentagePerFileLocal = 16 / compressionTotalFiles;
          compressionPercentagePerFileTotal = Math.floor((currentGenerationPercentage + (percentagePerGeneration / 1.01)) - (currentGenerationPercentage + (percentagePerGeneration / 1.2))) / compressionTotalFiles;
        }

        module.exports.emit('patchJobProgress', { generationIndex: currentGeneration - 1, progressCurrent: Math.floor(84 + (compressionPercentagePerFileLocal * (compressionTotalFiles - filesRemaining))), progressTotal: Math.floor((currentGenerationPercentage + (percentagePerGeneration / 1.2)) + (compressionPercentagePerFileTotal * (compressionTotalFiles - filesRemaining))), message: data.toString().split("\n")[0] });
      }
      else if (data.toString().includes("Exception") || data.toString().includes("error") || data.toString().includes("Error") || data.toString().includes("PermissionError") || data.toString().includes("TypeError") || data.toString().includes("ValueError")) {
        error = true;

        //Filter out last line to show to the user provided it is safe to do so
        let errorRaw = data.toString().split("\n");
        errorMsg = data.toString().trim();
        errorMsgFull = errorMsg;

        if (errorRaw.length > 5) {
          let tempErrorMsg = errorRaw[errorRaw.length - 2];

          if (tempErrorMsg.includes("Exception") || tempErrorMsg.includes("error") || tempErrorMsg.includes("Error") || tempErrorMsg.includes("PermissionError") || tempErrorMsg.includes("TypeError") || tempErrorMsg.includes("ValueError")) {
            errorMsg = tempErrorMsg.trim();
          }
        }
      }
      else if (data.toString().includes("Could not find valid base rom")) { //Requires manual kill
        error = true;

        errorMsg = data.toString().replace("Please run with -h to see help for further information.", "").replace("Press Enter to exit.", "").trim();
        errorMsgFull = errorMsg; 

        if (romBuildingGenerator)
          treeKill(romBuildingGenerator.pid);
      }
    }

    romBuildingGenerator.stderr.on('data', data => {
      //console.log("stderr data", data.toString());
      handleMessage(data);    
    });

    romBuildingGenerator.stdout.on('data', data => {
      //console.log("stdout data", data.toString());
      handleMessage(data); 
    });

    module.exports.emit('patchJobProgress', { generationIndex: currentGeneration, progressCurrent: 0, progressTotal: 0, message: "Starting." });

    promiseFromChildProcess(romBuildingGenerator).then(function () {

      //console.log("Spawn Seed Generation finished");

      if (romBuildingUserCancelled) {

        romBuildingGenerator = null;
        romBuildingUserCancelled = false;

        reject({ short: "user_cancelled", long: "user_cancelled" });
        return;
      }
      else {

        romBuildingGenerator = null;
        romBuildingUserCancelled = false;

        if (error) {

          console.error('[romBuilding] romBuildingGenerator error: ' + errorMsgFull);

          if (errorMsgFull.length > 0)
            reject({ short: errorMsg, long: errorMsgFull });
          else
            reject({ short: "Python code error", long: "Python code error" });

          return;
        }
      }

      resolve();
      
    }).catch((err) => { //Promise RomGeneration
      console.error('[romBuilding] Rom promise rejected: ' + err);
      reject({ short: err, long: err });
    });
  });
}

function cancelRomBuilding() {

  //Kill existing generation if one exists
  if (romBuildingGenerator) {
    romBuildingUserCancelled = true;
    treeKill(romBuildingGenerator.pid);
    return true;
  }
  else {
    return false;
  }
}

function testPythonPath(pythonPath) {

  return new Promise(function (resolve, reject) {

    var error = "";

    let pythonExec = spawn('"' + pythonPath + '"', { shell: true }).on('error', err => {
      reject(err);
    });

    pythonExec.stderr.on('data', data => {
      error = data.toString();
    });

    promiseFromChildProcess(pythonExec).then(function () {

      pythonExec = null;

      if (error)
        reject(error);
      else
        resolve();
    }).catch(err => {
      reject(err);
    });

    setTimeout(() => {
      if (pythonExec)
        treeKill(pythonExec.pid);
    }, 2000);
  });
}

function getSettings(pythonPath, randoPath, settingsString) {

  return new Promise(function (resolve, reject) {

    let output = "";
    let error = false;

    let args = ['--convert_settings', '--settings_string', settingsString];

    //console.log("Get settings now with spawn!");

    let settingsPY = spawn('"' + pythonPath + '"' + ' ' + '"' + randoPath + '"', args, { shell: true }).on('error', err => {
      console.error("[getSettings] Error spawning process:", err);
      reject(err);
    });

    settingsPY.stdout.on('data', data => {
      output = output + data.toString();
      error = false;
    });
    settingsPY.stderr.on('data', data => {
      output = output + data.toString();
      error = true;
    });

    promiseFromChildProcess(settingsPY).then(function () {

      //console.log("Get settings DONE!");

      if (error) {
        console.error('[getSettings] settingsPY error: ' + output);
        reject(output);
      }
      else {
        resolve(output.replace(/\r?\n|\r/g, "\r\n"));
      }

    }).catch(err => {
      console.error('[getSettings] settingsPY promise rejected: ' + err);
      reject(err);
    });
  });
}

function parseSettings(pythonPath, randoPath) {

  return new Promise(function (resolve, reject) {

    let output = "";
    let error = false;

    //console.log("Parse settings now with spawn!");

    let args = ['--convert_settings'];

    let settingsPY = spawn('"' + pythonPath + '"' + ' ' + '"' + randoPath + '"', args, { shell: true }).on('error', err => {
      console.error("[parseSettings] Error spawning process:", err);
      reject(err);
    });
    settingsPY.stdout.on('data', data => {
      output = output + data.toString();
      error = false;
    });
    settingsPY.stderr.on('data', data => {
      output = output + data.toString();
      error = true;
    });

    promiseFromChildProcess(settingsPY).then(() => {

      //console.log("Settings fully parsed!");
      //console.log("output:" + output);

      if (error) {
        console.error('[parseSettings] settingsPY error: ' + output);
        reject(output);
      }
      else {
        resolve(output.match(/([a-zA-Z0-9])\w+/g)[0]);
      }

    }).catch(err => {
      console.error('[parseSettings] settingsPY promise rejected: ' + err);
      reject(err);
    });
  });
}

module.exports = new EventEmitter();

module.exports.getSettings = getSettings;
module.exports.parseSettings = parseSettings;
module.exports.romBuilding = romBuilding;
module.exports.cancelRomBuilding = cancelRomBuilding;
module.exports.testPythonPath = testPythonPath;
