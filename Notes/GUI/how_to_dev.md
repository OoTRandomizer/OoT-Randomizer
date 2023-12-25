# How to develop

### Run the Electron GUI in dev mode

1. Start a terminal, go to the OoT-Randomizer directory

2. Run python3 SettingsToJson.py

3. Change current directory to the GUI folder

4. Execute `npm ci` to delete your node_modules folder and install all dependencies as specified in package-lock.json

5. Execute `npm run ng-dev` to start Angular webpack dev server

6. In a secondary shell execute `npm run electron-compile` followed by `npm run electron-dev`

7. As soon as Electron has started, you may open DevTools as required (`Ctrl+Shift+I` or `F12`)

Any saved changes to a file will then prompt the GUI to hot reload, making debugging very easy. You will also see console.log() and the likes in the javascript console.

That's it! Happy coding!

### Web view testing

For web view testing, follow the guide under [web-gui-testing.md](https://github.com/TestRunnerSRL/OoT-Randomizer/blob/Dev/Notes/web-gui-testing.md).
