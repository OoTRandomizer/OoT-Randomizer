#!/usr/bin/env node
'use strict';

const path = require('path');
const { spawn } = require('child_process');

function resolveElectron() {
  try {
    return require('electron');
  } catch (error) {
    console.error('Electron is not available from this GUI install.');
    console.error('Run npm install in the main GUI folder first, then retry.');
    console.error(error.message);
    process.exit(1);
  }
}

const electronPath = resolveElectron();
const mainPath = path.join(__dirname, 'main.js');
const child = spawn(electronPath, [mainPath], {
  stdio: 'inherit',
  cwd: path.resolve(__dirname, '../../..'),
});

child.on('exit', code => process.exit(code ?? 0));
