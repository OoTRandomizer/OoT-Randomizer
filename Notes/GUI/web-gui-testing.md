# Testing GUI in web mode

Within this repo, there is a small testing suite for website interoperability.

After having compiled all code one can use the GUI/webTest folder to spin up a stripped down instance of the OoTR web server.

Both Python3 and NodeJS v12+ are required.

## Instructions

### Step 1

Run `SettingsToJson.py --web` to ensure the right set of settings will be used.

### Step 2

Execute `npm run ng-release` inside the `GUI` directory to build the latest frontend code.

### Step 3

Go to `GUI/webTest/settingsParser` and run `node index.js`.

This will generate the `settings_list.json` required for the GUI to function.

### Step 4

Drop back into `GUI/webTest` and run `node server.js`.

This will spin up a small web server on http://localhost:80/ and start your browser (if compatible).

From there, one can check their code changes as they would look like on https://ootrandomizer.com

### Branch integration on ootrandomizer.com

In addition, a fully automated CI/CD pipeline exists to automatically build and publish dev branches
 on the actual website. A developer account is required for this.
