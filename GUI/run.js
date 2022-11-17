//Static modules
const os = require('os');
const fs = require('fs');
const spawn = require('child_process').spawn;

//Helpers
const waitFor = (ms) => new Promise(r => setTimeout(r, ms));

//Dynamic modules are loaded later
var ping = null;
var crc32 = null;

//Command line args
var forceRecompile = false;
var releaseMode = false;
var webMode = false;
var pythonPath = os.platform() == "win32" ? "py" : "python3";

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

async function spawnDetachedSubProcess(path, args, shell, hide, cwd = "") {

    var npmSpawn = args ? spawn(path, args, { shell: shell, detached: true, windowsHide: hide, stdio: 'ignore', cwd: cwd }) : spawn(path, { shell: shell, detached: true, windowsHide: hide, stdio: 'ignore', cwd: cwd });

    npmSpawn.on('error', err => {
        throw Error(err);
    });

    await waitFor(2000);
    npmSpawn.unref();
}

async function spawnChildSubProcess(path, args, shell, verbose, stderrSetting = "pipe", cwd = "") {

    var lastMessage = "";
    var npmSpawn = args ? spawn(path, args, { shell: shell, stdio: ['pipe', 'pipe', stderrSetting], cwd: cwd }) : spawn(path, { shell: shell, stdio: ['pipe', 'pipe', stderrSetting], cwd: cwd });

    npmSpawn.on('error', err => {
        throw Error(err);
    });

    function handleMessage(data) {

        if (data.toLowerCase().includes("exception") || data.toLowerCase().includes("error") || verbose) {
            console.log(data);
        }

        lastMessage = data;
    }

    if (stderrSetting == "pipe") {
        npmSpawn.stderr.on('data', data => {
            handleMessage(data.toString());
        });
    }

    npmSpawn.stdout.on('data', data => {
        handleMessage(data.toString());
    });

    let exitCode = await promiseFromChildProcess(npmSpawn);

    if (exitCode != 0) {
        console.error("Child Process failed with exit code:", exitCode);

        if (lastMessage && lastMessage.length > 0)
            console.error("Last message:", lastMessage);

        throw Error("process_error");
    }
}

async function setupNodeEnvironment(freshSetup = false) {
    console.log(freshSetup
        ? "Creating environment. Please be patient, this can take 5-10 minutes depending on your internet connection and HDD speed..."
        : "Updating environment. Please wait...");

    await waitFor(1000);

    environmentChecked = true;

    let npmInstallCommand = freshSetup ? "npm ci --verbose" : "npm install --verbose --no-save";

    await spawnChildSubProcess(npmInstallCommand, null, true, true, "inherit")
        .catch(err => { throw Error("Environment setup failed", err); });

    console.log("Environment setup completed");
}

async function setupWebTestNodeEnvironment() {

    console.log("Creating web test environment...");

    await waitFor(1000);

    await spawnChildSubProcess("npm install --verbose", null, true, true, "inherit", "webTest").catch(err => { throw Error("Web test environment setup failed"); });

    console.log("Web test environment setup completed");
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

async function generateWebTestSettingsMap() {

    console.log("Generating settings map...");

    await spawnChildSubProcess("node", ["index.js"], true, false, "pipe", "webTest/settingsParser").catch(err => { throw Error("Failed to launch settings parser"); });

    console.log("Settings map generated");
}

async function runWebTestServer() {

    console.log("Running Web Server...");

    await spawnDetachedSubProcess("node", ["server.js"], true, false, "webTest").catch(err => { throw Error("Failed to launch Web Server"); });

    console.log("Web Server started");
}

async function main(commandLine) {

    console.log("OoT Randomizer GUI is booting up");

    //Verify node_modules
    if (["./node_modules",
        "./node_modules/.bin",
        "./node_modules/@angular",
        "./node_modules/electron",
        "./node_modules/tcp-ping",
        "./node_modules/crc"]
        .some(module => !fs.existsSync(module))) {
        await setupNodeEnvironment(true); // fresh npm ci run when node_modules are sus
    }

    //Load dynamic modules
    ping = require('tcp-ping');
    crc32 = require('crc').crc32;

    //Parse command line
    let programOpts = {};

    for (let i = 0; i < commandLine.length; i++) {
        let arg = commandLine[i];

        if ((arg === "p" || arg === "python") && i < (commandLine.length - 1)) { //Path to the python executable
            programOpts["python"] = commandLine[++i];
        }
        else if (arg === "r" || arg === "release") { //Runs electron in release mode
            programOpts["release"] = true;
        }
        else if (arg === "w" || arg === "web") { //Runs the GUI in the browser
            programOpts["web"] = true;
        }
        else if (arg === "f" || arg === "force") { //Force an environment check and Angular/Electron re-compile
            programOpts["force"] = true;
        }
    }

    if (programOpts["python"] && typeof (programOpts["python"]) == "string" && programOpts["python"].trim().length > 0)
        pythonPath = programOpts["python"];

    if (programOpts["release"])
        releaseMode = true;
    else
        if (programOpts["web"])
            webMode = true;

    if (programOpts["force"])
        forceRecompile = true;

    console.log("Mode: " + (releaseMode ? "Release" : webMode ? "Web" : "Dev"));
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
                await setupNodeEnvironment(true); // fresh setup to reduce peer conflicts with outdated node_modules

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

    if (!releaseMode && !webMode) { //Start Angular dev server in dev mode
        await runAngularDevServer();
    }
    else { //Release/Web mode

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

    if (webMode) { //Web mode
        if (!fs.existsSync("webTest/node_modules") || forceRecompile)
            await setupWebTestNodeEnvironment();

        //Generate settings map
        await generateWebTestSettingsMap();

        //Spawn web server
        await runWebTestServer();
    }
    else { //Release/dev mode
        //Finally start Electron
        await runElectron();
    }

    console.log("All done");

    setTimeout(() => {
        console.log("Exit Success");
    }, 2000);
}

main(process.argv).catch((err) => { console.error(err); setTimeout(() => console.log("Exit Error"), 60000); });
