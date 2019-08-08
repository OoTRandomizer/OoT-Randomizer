//Static modules
const os = require('os');
const fs = require('fs');
const spawn = require('child_process').spawn;

//Helpers
const waitFor = (ms) => new Promise(r => setTimeout(r, ms));

//Dynamic modules are loaded later
var commander = null;
var ping = null;
var crc32 = null;

//Command line args
var forceRecompile = false;
var releaseMode = false;
var pythonPath = os.platform() == "win32" ? "python" : "python3";

//Globals
var environmentChecked = false;
var devServerStarted = false;
var angularIndex = {};
var electronIndex = {};

function promiseFromChildProcess(child) {
    return new Promise(function (resolve, reject) {
        child.addListener("error", reject);
        child.on("exit", (exitCode) => resolve(exitCode));
    });
}

function addFileToIndex(index, file) {
    let stats = fs.statSync(file);
    index[file] = { s: stats.size, m: stats.mtimeMs, h: crc32(fs.readFileSync(file, 'utf8')) };
}

function indexFolder(index, type, basePath) {

    //Check if folder is excluded
    if (type == "electron") { //Electron
        if (basePath == "electron/src/assets/" || basePath == "electron/src/modules/" || basePath == "electron/src/utils/") {
            return;
        }
    }
    else { //Angular
        if (basePath == "src/environments/") {
            return;
        }
    }

    let files = fs.readdirSync(basePath);

    files.forEach(file => {

        let stats = fs.statSync(basePath + file);

        if (stats.isDirectory()) {
            indexFolder(index, type, basePath + file + '/');
        }
        else {
            let filePath = basePath + file;
            index[filePath] = { s: stats.size, m: stats.mtimeMs, h: crc32(fs.readFileSync(filePath, 'utf8')) };
        }
    });
}

async function indexProject(type) {

    let basePath = (type == "electron" ? "electron/src/" : "src/");
    let index = {};

    indexFolder(index, type, basePath);

    return index;
}

function compareFileToIndex(index, file, stats = null) {

    let currentStats = stats ? stats : fs.statSync(file);
    let indexStats = file in index ? index[file] : null;

    if (!indexStats) //File isn't indexed yet
        return { s: currentStats.size, m: currentStats.mtimeMs, h: crc32(fs.readFileSync(file, 'utf8')) };

    if (indexStats.m == currentStats.mtimeMs) //Check last edit time first, if it hasn't changed file is still identical
        return false;

    if (indexStats.s != currentStats.size) //If size is different it has surely changed
        return { s: currentStats.size, m: currentStats.mtimeMs, h: crc32(fs.readFileSync(file, 'utf8')) };

    let newHash = crc32(fs.readFileSync(file, 'utf8'));

    if (newHash == indexStats.h) //Last edit date has changed, but size and hash are still identical, so the file hasn't truly changed
        return false;
    else
        return { s: currentStats.size, m: currentStats.mtimeMs, h: newHash };
}

function compareFolderToIndex(index, type, basePath) {

    //Check if folder is excluded
    if (type == "electron") { //Electron
        if (basePath == "electron/src/assets/" || basePath == "electron/src/modules/" || basePath == "electron/src/utils/") {
            return;
        }
    }
    else { //Angular
        if (basePath == "src/environments/") {
            return;
        }
    }

    let files = fs.readdirSync(basePath);

    for (let i = 0; i < files.length; i++) {

        let file = files[i];
        let stats = fs.statSync(basePath + file);

        if (stats.isDirectory()) {
            if (compareFolderToIndex(index, type, basePath + file + '/'))
                return true;
        }
        else {
            let filePath = basePath + file;

            if (compareFileToIndex(index, filePath, stats))
                return true;
            else
                delete index[filePath]; //Remove every file checked to find possibly deleted files at the end
        }
    }

    return false;
}

function compareProjectToIndex(type, index) {

    let indexUpdated = false;
    let basePath = (type == "electron" ? "electron/src/" : "src/");

    let tempIndex = {};
    Object.assign(tempIndex, index);

    if (type == "electron") //package.json is not included within electron folder
        delete tempIndex["package.json"];

    indexUpdated = compareFolderToIndex(tempIndex, type, basePath);

    if (!indexUpdated && Object.keys(tempIndex).length > 0) //No file added or changed, but index has files that were deleted!
        indexUpdated = true;

    return indexUpdated;
}

async function pingService(host, port) {
    return new Promise(function (resolve, reject) {
        ping.probe(host, port, function (err, available) {

            if (err) {
                reject(err);
                return;
            }

            resolve(available);
        });
    });
}

async function pingServiceUntilLive(host, port) {

    let running = false;

    while (!running) {
        running = await pingService(host, port).catch(err => { throw Error("Can't connect to local network: " + err); });

        if (!running)
            await waitFor(500);     
    }
}

async function spawnDetachedSubProcess(path, args, shell, hide) {

  var npmSpawn = args ? spawn(path, args, { shell: shell, detached: true, windowsHide: hide, stdio: 'ignore' }) : spawn(path, { shell: shell, detached: true, windowsHide: hide, stdio: 'ignore' });

    npmSpawn.on('error', err => {
        throw Error(err);
    });

    await waitFor(2000);
    npmSpawn.unref();
}

async function spawnChildSubProcess(path, args, shell, verbose) {

    var lastMessage = "";
    var npmSpawn = args ? spawn(path, args, { shell: shell }) : spawn(path, { shell: shell });

    npmSpawn.on('error', err => {
        throw Error(err);
    });

    function handleMessage(data) {

        if (data.toLowerCase().includes("exception") || data.toLowerCase().includes("error") || verbose) {
            console.log(data);
        }

        lastMessage = data;
    }

    npmSpawn.stderr.on('data', data => {
        handleMessage(data.toString());
    });

    npmSpawn.stdout.on('data', data => {
        handleMessage(data.toString());
    });

    let exitCode = await promiseFromChildProcess(npmSpawn);

    if (exitCode != 0) {
        console.error("Child Process failed with exit code: " + exitCode + " ; last message:", lastMessage);
        throw Error("process_error");  
    } 
}

async function setupNodeEnvironment(freshSetup = false) {

    if (freshSetup)
        console.log("Creating environment. Please be patient, this can take up to 5 minutes depending on your internet connection...");
    else
        console.log("Updating environment. Please wait...");

    environmentChecked = true;

    await spawnChildSubProcess("npm install --verbose", null, true, true).catch(err => { throw Error("Environment setup failed"); });

    console.log("Environment setup completed");
}

async function compileElectron() {

    console.log("Compiling Electron...");

    await spawnChildSubProcess("npm run electron-compile", null, true, false).catch(err => { throw Error("Electron compile failed"); });

    console.log("Electron compile completed");
}

async function runElectron() {

    if (releaseMode || !devServerStarted) {
        console.log("Running Electron...");
    }
    else if (devServerStarted) {
        console.log("Running Electron. Please wait until Angular finishes initial compile...");
        await waitFor(5000);
  }

    if (releaseMode)
        await spawnDetachedSubProcess("node", ["node_modules/electron/cli.js", ".", "release", "python", pythonPath], false, true).catch(err => { throw Error("Failed to launch Electron"); }); //Spawn without a shell so the window is hidden on Windows
    else
        await spawnDetachedSubProcess("npm run electron-dev", ["python", '"' + pythonPath + '"'], true, false).catch(err => { throw Error("Failed to launch Electron"); }); //Need to wrap pythonPath again since it gets passed to another batch file which removes one layer

  console.log("Electron started");
}

async function compileAngular() {

    console.log("Compiling Angular. This can take a minute...");

    await spawnChildSubProcess("npm run ng-release", null, true, false).catch(err => { throw Error("Angular compile failed"); });
 
    console.log("Angular compile completed");
}

async function runAngularDevServer() {

    console.log("Checking status of Angular dev server...");

    let running = await pingService('localhost', 4200).catch(err => { throw Error("Can't connect to local network: " + err); });

    if (running) {
        console.log("Angular dev server is running");
    }
    else {
        console.log("Angular dev server is NOT running");
        console.log("Starting Angular dev server...");

        await spawnDetachedSubProcess("npm run ng-dev", null, true, false).catch(err => { throw Error("Failed to launch Angular dev server"); });

        console.log("Waiting for server to come live. This can take a bit...");

        await pingServiceUntilLive('localhost', 4200);

        console.log("Angular dev server is running");
        devServerStarted = true;
    }   
}

async function main(commandLine) {

    console.log("OoT Randomizer GUI is booting up");

    //Verify basic environment
    if (!fs.existsSync("./node_modules"))
        await setupNodeEnvironment(true);

    //Verify binary folder exists
    if (!fs.existsSync("./node_modules/.bin")) {
        //throw Error("GUI/node_modules/.bin folder is missing. Please delete the entire GUI/node_modules folder and try again!");
    }

    //Verify core modules
    if (!fs.existsSync("./node_modules/@angular") || !fs.existsSync("./node_modules/electron"))
        await setupNodeEnvironment();

    //Verify dynamic modules needed by run.js
    if (!fs.existsSync("./node_modules/commander") || !fs.existsSync("./node_modules/tcp-ping") || !fs.existsSync("./node_modules/crc"))
        await setupNodeEnvironment();

    //Load dynamic modules
    commander = require('commander');
    ping = require('tcp-ping');
    crc32 = require('crc').crc32;

    //Parse command line
    commander
        .option('p, python <path>', 'Path to your python executable')
        .option('r, release', 'Runs electron in release mode')
        .option('f, force', 'Force an environment check and Angular/Electron re-compile')
        .parse(commandLine);

    if (commander["python"] && typeof (commander["python"]) == "string" && commander["python"].trim().length > 0)
        pythonPath = commander["python"];

    if (commander["release"])
        releaseMode = true;

    if (commander["force"])
        forceRecompile = true;

    console.log("Mode: " + (releaseMode ? "Release" : "Dev"));
    console.log("Python Path:", pythonPath);

    if (forceRecompile)
        console.log("Force recompile activated!");

    //Verify environment in forceRecompile mode if not already checked
    if (forceRecompile && !environmentChecked)
        await setupNodeEnvironment();

    var electronIndexUpdated = false;

    //Check if electron index and compiled build exists
    if (forceRecompile || !fs.existsSync("./electron/dist") || !fs.existsSync("./electron/dist/index.json") || !fs.existsSync("./electron/dist/main.js")) {

        if (!environmentChecked)
            await setupNodeEnvironment();

        console.log("Create Electron Index...");

        if (!fs.existsSync("./electron/dist"))
            fs.mkdirSync("./electron/dist");

        addFileToIndex(electronIndex, "package.json");

        //Compile Electron
        let compilePromise = compileElectron();

        //Index project
        let indexPromise = indexProject("electron");

        let results = await Promise.all([compilePromise, indexPromise]);
        Object.assign(electronIndex, results[1]);

        electronIndexUpdated = true;

        console.log("Electron Index created");
    }
    else {

        console.log("Verify Electron Index...");

        //Load electron index and see if package.json differs
        electronIndex = JSON.parse(fs.readFileSync("./electron/dist/index.json", 'utf8'));

        let packageJsonChanged = compareFileToIndex(electronIndex, "package.json");

        if (packageJsonChanged) {

            //package.json got changed, update environment
            if (!environmentChecked)
                await setupNodeEnvironment();

            electronIndex["package.json"] = packageJsonChanged;
            electronIndexUpdated = true;
        }

        if (compareProjectToIndex("electron", electronIndex)) {

            console.log("Electron Index changed");

            //Re-compile Electron
            let compilePromise = compileElectron();

            //Re-index project
            let indexPromise = indexProject("electron");

            let results = await Promise.all([compilePromise, indexPromise]);

            let newIndex = results[1];
            newIndex["package.json"] = electronIndex["package.json"];

            electronIndex = newIndex;
            electronIndexUpdated = true;
        }

        console.log("Electron Index verified");
    }

    //Write updated electron index to file if neccesary
    if (electronIndexUpdated)
        fs.writeFileSync("./electron/dist/index.json", JSON.stringify(electronIndex));

    if (!releaseMode) { //Start Angular dev server in dev mode
        await runAngularDevServer();
    }
    else { //Release mode

        var angularIndexUpdated = false;

        //Check if Angular index and compiled build exists
        if (forceRecompile || !fs.existsSync("./dist") || !fs.existsSync("./dist/index.json") || !fs.existsSync("./dist/ootr-electron-gui") || !fs.existsSync("./dist/ootr-electron-gui/index.html")) {

            console.log("Create Angular Index...");

            if (!fs.existsSync("./dist"))
                fs.mkdirSync("./dist");

            //Compile Angular
            let compilePromise = compileAngular();

            //Index project
            let indexPromise = indexProject("angular");

            let results = await Promise.all([compilePromise, indexPromise]);

            angularIndex = results[1];
            angularIndexUpdated = true;

            console.log("Angular Index created");
        }
        else {

            console.log("Verify Angular Index...");

            //Load Angular index and see if it differs to current src folder
            angularIndex = JSON.parse(fs.readFileSync("./dist/index.json", 'utf8'));

            if (compareProjectToIndex("angular", angularIndex)) {

                console.log("Angular Index changed");

                //Re-compile Angular
                let compilePromise = compileAngular();

                //Re-index project
                let indexPromise = indexProject("angular");

                let results = await Promise.all([compilePromise, indexPromise]);

                angularIndex = results[1];
                angularIndexUpdated = true;
            }

            console.log("Angular Index verified");
        }

        //Write updated Angular index to file if neccesary
        if (angularIndexUpdated)
            fs.writeFileSync("./dist/index.json", JSON.stringify(angularIndex));
    }

    //Finally start Electron
    await runElectron();
    console.log("All done");

    setTimeout(() => {
        console.log("Exit Success");
    }, 2000);
}

main(process.argv).catch((err) => { console.error(err); setTimeout(() => console.log("Exit Error"), 60000); });
