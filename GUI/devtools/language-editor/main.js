'use strict';

/*
 * Language Editor main process
 * 1. Paths and immutable defaults
 * 2. Configuration loaders
 * 3. ROM/text helpers
 * 4. Windows and menus
 * 5. IPC commands grouped by user action
 * 6. Application startup
 */

const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
const { app, BrowserWindow, dialog, ipcMain, Menu } = require('electron');

// macOS 26 + older Electron builds can crash inside AppKit accessibility
// cleanup when modal/child windows are destroyed. Keep this developer tool
// conservative: disable Chromium renderer accessibility and GPU acceleration
// before app readiness so closing dialogs/windows does not exercise the
// fragile native accessibility path.
if (process.platform === 'darwin') {
  app.commandLine.appendSwitch('disable-renderer-accessibility');
  app.commandLine.appendSwitch('disable-features', 'AccessibilityObjectModel');
}
app.disableHardwareAcceleration();

const TOOL_DIR = __dirname;
const UI_JSON_NAME = 'language_editor_ui.json';
const THEME_JSON_NAME = 'theme.json';
const CN_CHARMAP_JSON_NAME = 'charmap.chn.json';
const WORKSPACE_JSON_NAME = 'workspace.json';
const UI_JSON_PATH = path.join(TOOL_DIR, UI_JSON_NAME);
const THEME_JSON_PATH = path.join(TOOL_DIR, THEME_JSON_NAME);
const CN_CHARMAP_JSON_PATH = path.join(TOOL_DIR, CN_CHARMAP_JSON_NAME);
const WORKSPACE_JSON_PATH = path.join(TOOL_DIR, WORKSPACE_JSON_NAME);
const REPO_ROOT = path.resolve(TOOL_DIR, '../../..');
const DEFAULT_PROPERTY_PATH = path.join(REPO_ROOT, 'data', 'lang', 'English', 'property.json');
const HINT_LIST_PATH = path.join(REPO_ROOT, 'HintList.py');

const DEFAULT_BIN_PATCH_RANGES = {
  "title.bin": [
    "0x01795300",
    "0x017B4440"
  ],
  "keaton.bin": [
    "0x8A7C00",
    "0x8A7D00"
  ],
  "NESFont.bin": [
    "0x928000",
    "0x92C580"
  ],
  "Kanji.bin": [
    "0x4D9F40",
    "0x556240"
  ],
  "EXTitleCard.bin": [
    "0x7BD000",
    "0x8458A0"
  ],
  "Gameover.bin": [
    "0x860000",
    "0x863300"
  ],
  "TitleCardJP.bin": [
    "0x864000",
    "0x871C80"
  ],
  "TitleCardEN.bin": [
    "0x872000",
    "0x87FC80"
  ],
  "ItemNameJP.bin": [
    "0x880000",
    "0x89EC00"
  ],
  "ItemNameEN.bin": [
    "0x89EC00",
    "0x8BD800"
  ],
  "MapName.bin": [
    "0x8BE000",
    "0x8DF800"
  ],
  "ActionJP.bin": [
    "0x8E0000",
    "0x8E2B80"
  ],
  "ActionEN.bin": [
    "0x8E2B80",
    "0x8E5700"
  ],
  "PlaceName.bin": [
    "0x0198A000",
    "0x019FBB00"
  ],
  "FileSelJP.bin": [
    "0x01A02000",
    "0x01A2CF00"
  ],
  "FileSelEN.bin": [
    "0x01A2CF00",
    "0x01A3B5C0"
  ],
  "KingDodongo.bin": [
    "0x01054000",
    "0x010838E0"
  ],
  "Gohma.bin": [
    "0x010A9000",
    "0x010C7200"
  ],
  "PhantomGanon.bin": [
    "0x01238000",
    "0x01248DE0"
  ],
  "Barinade.bin": [
    "0x01340000",
    "0x0135DDB0"
  ],
  "Volvagia.bin": [
    "0x013C8000",
    "0x013D8270"
  ],
  "Morpha.bin": [
    "0x014AB000",
    "0x014B2C70"
  ],
  "Twinrova.bin": [
    "0x0156F000",
    "0x015A8BB0"
  ],
  "Ganondorf.bin": [
    "0x015C9000",
    "0x015D9100"
  ],
  "Bongo.bin": [
    "0x015DA000",
    "0x015F37B0"
  ],
  "Ganon.bin": [
    "0x017EA000",
    "0x0181E7F0"
  ]
};
let mainWindow = null;
let allowForcedClose = false;
let uiData = { strings: { en: {} }, languages: [{ code: 'en', label: 'English' }] };
let currentLanguage = 'en';
let currentUiTheme = 'dark';
let themeData = { default: 'dark', order: ['dark'], themes: { dark: { label: 'Dark', colorScheme: 'dark', variables: {} } } };
let defaultPropertyCache = null;
let cnCharmapReverseCache = null;
let workspaceDefinition = { schemaVersion: 1, panels: [], styles: [] };

function loadUiData() {
  try {
    uiData = JSON.parse(fs.readFileSync(UI_JSON_PATH, 'utf8'));
  } catch (error) {
    console.warn('Failed to load language_editor_ui.json:', error.message);
  }
}

function loadWorkspaceDefinition() {
  try {
    workspaceDefinition = JSON.parse(fs.readFileSync(WORKSPACE_JSON_PATH, 'utf8'));
  } catch (error) {
    console.warn('Failed to load workspace.json:', error.message);
    workspaceDefinition = { schemaVersion: 1, panels: [], styles: [] };
  }
}

function loadThemeData() {
  try {
    themeData = JSON.parse(fs.readFileSync(THEME_JSON_PATH, 'utf8'));
  } catch (error) {
    console.warn('Failed to load theme.json:', error.message);
    themeData = { default: 'dark', order: ['dark'], themes: { dark: { label: 'Dark', colorScheme: 'dark', variables: {} } } };
  }
  const themes = themeData && typeof themeData === 'object' && themeData.themes && typeof themeData.themes === 'object' ? themeData.themes : {};
  const order = Array.isArray(themeData.order) ? themeData.order.map(x => String(x).toLowerCase()).filter(x => themes[x]) : Object.keys(themes);
  themeData.order = order.length ? order : ['dark'];
  if (!themes.dark) themes.dark = { label: 'Dark', colorScheme: 'dark', variables: {} };
  if (!themeData.default || !themes[String(themeData.default).toLowerCase()]) themeData.default = 'dark';
  currentUiTheme = String(themeData.default || 'dark').toLowerCase();
}

function t(text, params = {}) {
  const table = uiData.strings?.[currentLanguage] || uiData.strings?.en || {};
  const fallback = uiData.strings?.en?.[text] || text;
  let out = table[text] || fallback;
  for (const [key, value] of Object.entries(params)) out = out.split(`{${key}}`).join(String(value));
  return out;
}

function loadDefaultProperty() {
  if (defaultPropertyCache) return JSON.parse(JSON.stringify(defaultPropertyCache));
  if (!fs.existsSync(DEFAULT_PROPERTY_PATH)) {
    throw new Error(`Default property template is missing: ${DEFAULT_PROPERTY_PATH}`);
  }
  const jsonText = fs.readFileSync(DEFAULT_PROPERTY_PATH, 'utf8');
  defaultPropertyCache = JSON.parse(jsonText);
  return JSON.parse(JSON.stringify(defaultPropertyCache));
}

function parseHintListOrder() {
  if (!fs.existsSync(HINT_LIST_PATH)) return [];
  const text = fs.readFileSync(HINT_LIST_PATH, 'utf8');
  const startMatch = text.match(/(?:^|\n)hintTable\s*:\s*dict[^=]*=\s*\{/);
  if (!startMatch) return [];
  let index = (startMatch.index || 0) + startMatch[0].length;
  let depth = 1;
  let quote = null;
  let escape = false;
  let body = '';
  for (; index < text.length; index++) {
    const ch = text[index];
    body += ch;
    if (quote) {
      if (escape) escape = false;
      else if (ch === '\\') escape = true;
      else if (ch === quote) quote = null;
      continue;
    }
    if (ch === '"' || ch === "'") { quote = ch; continue; }
    if (ch === '{') depth++;
    else if (ch === '}') {
      depth--;
      if (depth === 0) {
        body = body.slice(0, -1);
        break;
      }
    }
  }
  const order = [];
  const seen = new Set();
  for (const line of body.split(/\r?\n/)) {
    const match = line.match(/^\s*(['"])((?:\\.|(?!\1).)*?)\1\s*:/);
    if (!match) continue;
    const raw = match[2].replace(/\\(['"\\])/g, '$1');
    if (!seen.has(raw)) { seen.add(raw); order.push(raw); }
  }
  return order;
}

function send(channel, payload = {}) {
  if (mainWindow && !mainWindow.isDestroyed()) mainWindow.webContents.send(channel, payload);
}

function buildMenu() {
  const languageItems = (uiData.languages || [{ code: 'en', label: 'English' }]).map(lang => ({
    label: lang.label,
    type: 'radio',
    checked: lang.code === currentLanguage,
    click: () => {
      currentLanguage = lang.code;
      buildMenu();
      send('language-changed', { language: currentLanguage });
    },
  }));

  const themes = themeData?.themes || {};
  const themeOrder = Array.isArray(themeData?.order) && themeData.order.length ? themeData.order : Object.keys(themes);
  const uiThemeItems = themeOrder.map(key => {
    const theme = String(key).toLowerCase();
    const entry = themes[theme] || {};
    const label = entry.label || theme;
    return {
      label: t(label),
      type: 'radio',
      checked: currentUiTheme === theme,
      click: () => {
        currentUiTheme = theme;
        buildMenu();
        send('menu-ui-theme', { theme });
      },
    };
  });

  const template = [
    { label: t('File'), submenu: [
      { label: t('Load completed property.json...'), accelerator: 'CmdOrCtrl+O', click: () => send('menu-load-property') },
      { label: t('Load default template'), click: () => send('menu-load-default') },
      { label: t('Open work file...'), accelerator: 'CmdOrCtrl+Alt+O', click: () => send('menu-open-work-file') },
      { label: t('Merge missing defaults'), click: () => send('menu-merge-defaults') },
      { type: 'separator' },
      { label: t('Export property.json...'), accelerator: 'CmdOrCtrl+S', click: () => send('menu-save-property') },
      { label: t('Save work file...'), accelerator: 'CmdOrCtrl+Alt+S', click: () => send('menu-save-work-file') },
      { type: 'separator' },
      { label: t('Quit'), accelerator: process.platform === 'darwin' ? 'CmdOrCtrl+Q' : undefined, click: () => { if (mainWindow && !mainWindow.isDestroyed()) mainWindow.close(); } },
    ]},
    { label: t('Edit'), submenu: [
      { label: t('Undo'), accelerator: 'CmdOrCtrl+Z', click: () => send('menu-undo') },
      { label: t('Redo'), accelerator: 'CmdOrCtrl+Y', click: () => send('menu-redo') },
      { type: 'separator' },
      { role: 'cut', label: t('Cut') },
      { label: t('Copy'), accelerator: 'CmdOrCtrl+C', click: () => send('menu-smart-copy') },
      { label: t('Paste'), accelerator: 'CmdOrCtrl+V', click: () => send('menu-smart-paste') },
      { label: t('Duplicate'), accelerator: 'CmdOrCtrl+D', click: () => send('menu-smart-duplicate') },
      { role: 'selectAll', label: t('Select All') },
      { type: 'separator' },
      { label: t('Apply editor'), accelerator: 'CmdOrCtrl+Enter', click: () => send('menu-apply-editor') },
      { label: t('Save entry'), accelerator: 'CmdOrCtrl+Shift+S', click: () => send('menu-save-entry') },
      { label: t('Apply ID'), accelerator: 'CmdOrCtrl+Alt+I', click: () => send('menu-apply-entry-id') },
      { label: t('Add entry'), accelerator: 'CmdOrCtrl+N', click: () => send('menu-add-entry') },
      { label: t('Delete entry'), accelerator: 'CmdOrCtrl+Backspace', click: () => send('menu-delete-entry') },
      { label: t('Copy entry'), accelerator: 'CmdOrCtrl+Shift+C', click: () => send('menu-copy-entry') },
      { label: t('Paste entry'), accelerator: 'CmdOrCtrl+Shift+V', click: () => send('menu-paste-entry') },
      { label: t('Replace text in all entries...'), accelerator: 'CmdOrCtrl+Alt+Shift+R', click: () => send('menu-replace-all-entries') },
      { label: t('Duplicate entry'), accelerator: 'CmdOrCtrl+Shift+D', click: () => send('menu-duplicate-entry') },
      { label: t('Move entry up'), accelerator: 'CmdOrCtrl+Alt+Up', click: () => send('menu-move-entry-up') },
      { label: t('Move entry down'), accelerator: 'CmdOrCtrl+Alt+Down', click: () => send('menu-move-entry-down') },
      { label: t('Sort entries by ID'), accelerator: 'CmdOrCtrl+Alt+S', click: () => send('menu-sort-entries-by-id') },
      { label: t('Validate entry'), accelerator: 'CmdOrCtrl+Shift+Enter', click: () => send('menu-validate-entry') },
      { label: t('Validate property'), accelerator: 'CmdOrCtrl+Alt+V', click: () => send('menu-validate-property') },
      { type: 'separator' },
      { label: t('Language'), submenu: languageItems },
    ]},
    { label: t('View'), submenu: [
      { label: t('Text editor'), accelerator: 'CmdOrCtrl+1', click: () => send('menu-switch-tab', { tab: 'tabText' }) },
      { label: t('Raw preview'), accelerator: 'CmdOrCtrl+2', click: () => send('menu-switch-tab', { tab: 'tabRaw' }) },
      { label: t('Section JSON'), accelerator: 'CmdOrCtrl+3', click: () => send('menu-switch-tab', { tab: 'tabSectionJson' }) },
      { label: t('Patch maker'), accelerator: 'CmdOrCtrl+4', click: () => send('menu-switch-tab', { tab: 'tabPatch' }) },
      { label: t('Memo'), accelerator: 'CmdOrCtrl+5', click: () => send('menu-switch-tab', { tab: 'tabMemo' }) },
      { type: 'separator' },
      { label: t('Increase UI text size'), accelerator: 'CmdOrCtrl+Plus', click: () => send('menu-ui-zoom-in') },
      { label: t('Decrease UI text size'), accelerator: 'CmdOrCtrl+-', click: () => send('menu-ui-zoom-out') },
      { label: t('Reset UI text size'), accelerator: 'CmdOrCtrl+0', click: () => send('menu-ui-zoom-reset') },
      { type: 'separator' },
      { label: t('UI theme'), submenu: uiThemeItems },
      { type: 'separator' },
      { label: t('Reset layout'), click: () => send('menu-reset-layout') },
      { type: 'separator' },
      { role: 'reload', label: t('Reload') },
      { role: 'toggleDevTools', label: t('Toggle Developer Tools') },
    ]},
    { label: t('Tools'), submenu: [
      { label: t('Generate checked diff patches'), accelerator: 'CmdOrCtrl+Alt+P', click: () => send('menu-generate-patches') },
      { label: t('Export checked raw segments'), accelerator: 'CmdOrCtrl+Alt+R', click: () => send('menu-export-segments') },
      { label: t('Extract PLAIN_TEXTS from ROM'), accelerator: 'CmdOrCtrl+Alt+T', click: () => send('menu-extract-plain-texts') },
    ]},
  ];
  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}


function htmlEscape(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function safeJsonForHtml(value) {
  return JSON.stringify(value).replace(/</g, '\\u003c');
}

function replaceDialogHtml(payload) {
  const p = {
    title: 'Replace text in all entries',
    targetLabel: 'Target',
    targetValue: 'All editable entries',
    findLabel: 'Find text',
    replaceLabel: 'Replacement text',
    protectLabel: 'Protect control codes',
    protectHelp: 'Control code arguments will not be changed.',
    cancelLabel: 'Cancel',
    replaceLabelButton: 'Replace',
    ...payload,
  };
  return `<!doctype html>
<html><head><meta charset="utf-8"><title>${htmlEscape(p.title)}</title>
<style>
:root{color-scheme:dark;--bg:#11151c;--panel:#171d26;--line:#2c3542;--text:#e8edf5;--muted:#a8b2c2;--accent:#7bb7ff;--danger:#ff8f8f;}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font-family:"Hiragino Sans","Hiragino Kaku Gothic ProN","Apple SD Gothic Neo","PingFang SC","PingFang TC","Noto Sans CJK JP","Noto Sans CJK KR","Noto Sans CJK SC","Noto Sans CJK TC","Yu Gothic","Meiryo","Malgun Gothic","Arial Unicode MS",Arial;font-size:14px}.wrap{padding:18px;display:grid;gap:14px}.title{font-size:18px;font-weight:700}.field{display:grid;gap:6px}.label{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.04em}input{width:100%;padding:10px 11px;border-radius:8px;border:1px solid var(--line);background:#0e131a;color:var(--text);font:inherit}input:focus{outline:1px solid var(--accent);border-color:var(--accent)}.target{padding:10px 11px;border:1px solid var(--line);border-radius:8px;background:var(--panel);color:var(--text)}.check{display:flex;align-items:center;gap:8px;color:var(--text)}.check input{width:auto}.help{font-size:12px;color:var(--muted);margin-top:-8px}.buttons{display:flex;justify-content:flex-end;gap:10px;padding-top:8px}button{padding:9px 14px;border-radius:8px;border:1px solid var(--line);background:#202938;color:var(--text);font:inherit;cursor:pointer}button.primary{background:#245b97;border-color:#3982ce}.error{display:none;color:var(--danger);font-size:12px}.error.visible{display:block}</style>
</head><body><form class="wrap" id="form"><div class="title">${htmlEscape(p.title)}</div><div class="field"><div class="label">${htmlEscape(p.targetLabel)}</div><div class="target">${htmlEscape(p.targetValue)}</div></div><div class="field"><label class="label" for="find">${htmlEscape(p.findLabel)}</label><input id="find" autocomplete="off" autofocus></div><div class="field"><label class="label" for="replace">${htmlEscape(p.replaceLabel)}</label><input id="replace" autocomplete="off"></div><label class="check"><input id="protect" type="checkbox" checked> <span>${htmlEscape(p.protectLabel)}</span></label><div class="help">${htmlEscape(p.protectHelp)}</div><div class="error" id="error"></div><div class="buttons"><button type="button" id="cancel">${htmlEscape(p.cancelLabel)}</button><button type="submit" class="primary">${htmlEscape(p.replaceLabelButton)}</button></div></form><script id="payload" type="application/json">${safeJsonForHtml(p)}</script><script>
const { ipcRenderer } = require('electron');
const payload = JSON.parse(document.getElementById('payload').textContent);
const form = document.getElementById('form');
const find = document.getElementById('find');
const repl = document.getElementById('replace');
const protect = document.getElementById('protect');
const error = document.getElementById('error');
document.getElementById('cancel').onclick = () => ipcRenderer.send(payload.channel, null);
form.onsubmit = ev => { ev.preventDefault(); if(!find.value){ error.textContent = payload.emptyMessage || 'Find text is empty.'; error.classList.add('visible'); find.focus(); return; } ipcRenderer.send(payload.channel, {from: find.value, to: repl.value, protect: protect.checked}); };
window.addEventListener('keydown', ev => { if(ev.key === 'Escape') ipcRenderer.send(payload.channel, null); });
</script></body></html>`;
}


ipcMain.handle('window:unsaved-close-dialog', async () => {
  // Native message boxes can exercise AppKit accessibility cleanup paths on
  // macOS. The renderer now provides the close-confirmation UI in-page.
  return 'cancel';
});

ipcMain.handle('window:force-close', () => {
  allowForcedClose = true;
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.removeAllListeners('close');
    mainWindow.destroy();
  }
  return true;
});

ipcMain.handle('replace-dialog:open', async () => {
  // Kept for compatibility with older renderer code. The current renderer uses
  // an in-page dialog to avoid creating/destroying modal BrowserWindows on macOS.
  return null;
});

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1420,
    height: 900,
    minWidth: 1080,
    minHeight: 720,
    title: 'OOTR Language Editor Developer Tool',
    webPreferences: {
      preload: path.join(TOOL_DIR, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
      backgroundThrottling: false,
    },
  });
  mainWindow.webContents.on('render-process-gone', (_event, details) => {
    console.error('Language editor renderer process gone:', details);
  });
  mainWindow.on('unresponsive', () => {
    console.error('Language editor window became unresponsive.');
  });
  mainWindow.loadFile(path.join(TOOL_DIR, 'index.html'));
  mainWindow.on('close', event => {
    if (allowForcedClose) return;
    event.preventDefault();
    send('app-close-request');
  });
}



function normalizeRomPath(filePath) {
  return filePath ? String(filePath) : '';
}

function parseHexRange(range) {
  if (!Array.isArray(range) || range.length < 2) throw new Error('Invalid bin_patch range.');
  return [parseInt(String(range[0]), 16), parseInt(String(range[1]), 16)];
}

function xorCompressedDiff(originalPath, modifiedPath, range) {
  const original = fs.readFileSync(originalPath);
  const modified = fs.readFileSync(modifiedPath);
  const [start, end] = parseHexRange(range);
  if (!Number.isFinite(start) || !Number.isFinite(end) || end < start) throw new Error('Invalid range.');
  if (original.length < end || modified.length < end) throw new Error(`ROM is smaller than requested range 0x${end.toString(16).toUpperCase()}.`);
  const out = Buffer.alloc(end - start);
  for (let i = start; i < end; i++) out[i - start] = original[i] ^ modified[i];
  return zlib.deflateSync(out);
}

function rawSegment(originalPath, start, size) {
  const original = fs.readFileSync(originalPath);
  const s = Number(start);
  const n = Number(size);
  if (!Number.isFinite(s) || !Number.isFinite(n) || s < 0 || n < 0) throw new Error('Invalid segment start or size.');
  const end = s + n;
  if (original.length < end) throw new Error(`ROM is smaller than requested segment end 0x${end.toString(16).toUpperCase()}.`);
  return original.subarray(s, end);
}


function parseFlexibleHex(value, name) {
  const text = String(value ?? '').trim();
  if (!text) throw new Error(`${name} is required.`);
  const normalized = text.startsWith('$') ? `0x${text.slice(1)}` : text;
  const n = Number.parseInt(normalized, 0);
  if (!Number.isFinite(n) || n < 0) throw new Error(`${name} must be a positive hex address.`);
  return n;
}

function isLikelyDecompressedRom(buffer) {
  // Decompressed OoT ROMs are larger than the 0x2000000 compressed image.
  // Keep the extractor intentionally conservative; it does not call the external
  // decompressor and only reads already-expanded data.
  return buffer && buffer.length > 0x2000000;
}

function resolveMessagePointer(pointer, textAddress, romSize) {
  if (pointer >= 0 && pointer < romSize) return pointer;
  const low24 = pointer & 0x00FFFFFF;
  const candidate = textAddress + low24;
  if (candidate >= 0 && candidate < romSize) return candidate;
  if (low24 >= 0 && low24 < romSize) return low24;
  throw new Error(`Message pointer 0x${pointer.toString(16).toUpperCase()} does not resolve inside the ROM.`);
}

function readEnglishMessageBytes(buffer, start, hardEnd) {
  const out = [];
  const limit = Math.min(buffer.length, hardEnd || (start + 0x4000));
  for (let i = start; i < limit; i++) {
    const byte = buffer[i];
    if (byte === 0x02) break;
    out.push(byte);
  }
  return out;
}

function decodeEnglishMessageBytes(bytes) {
  const chunk = 0x4000;
  let out = '';
  for (let i = 0; i < bytes.length; i += chunk) {
    out += String.fromCharCode(...bytes.slice(i, i + chunk));
  }
  return out;
}

function readUInt24BE(buffer, offset) {
  return (buffer[offset] << 16) | (buffer[offset + 1] << 8) | buffer[offset + 2];
}

function detectPlainTextBase(payload, tableAddress, textAddress) {
  const requested = String(payload?.base || payload?.lang || '').trim().toLowerCase();
  if (requested === 'cn' || requested === 'chn' || requested === 'zh' || requested === 'zh-cn' || requested === 'ique' || requested === 'chinese') return 'cn';
  if (requested === 'jp' || requested === 'jpn' || requested === 'japanese') return 'jp';
  if (requested === 'en' || requested === 'eng' || requested === 'english') return 'en';
  // Standard NTSC-1.0 message areas from Messages.py. Keep this only as an
  // address heuristic; custom HEX addresses still work and default to English.
  if (tableAddress === 0xB808AC || textAddress === 0x8EB000) return 'jp';
  return 'en';
}

const JP_CONTROL_READ = new Map([
  [0x8140, { literal: '　', args: 0 }],
  [0x000A, { literal: '&', args: 0 }],
  [0x8170, { literal: '｝', args: 0, end: true }],
  [0x81A5, { literal: '^', args: 0 }],
  [0x000B, { literal: '#', args: 1, subtract: 0x0C00 }],
  [0x86C7, { literal: '☞', args: 1 }],
  [0x81CB, { literal: '⇒', args: 2 }],
  [0x8189, { literal: '♂', args: 0 }],
  [0x818A, { literal: '♀', args: 0 }],
  [0x86C8, { literal: '☜', args: 0 }],
  [0x819F, { literal: '◆', args: 0 }],
  [0x81A3, { literal: '▲', args: 1 }],
  [0x819E, { literal: '◇', args: 1 }],
  [0x874F, { literal: '@', args: 0 }],
  [0x81F0, { literal: 'Å', args: 0 }],
  [0x81F3, { literal: '♭', args: 2 }],
  [0x819A, { literal: '★', args: 1 }],
  [0x86C9, { literal: '☝', args: 1 }],
  [0x86B3, { literal: '〠', args: 3 }],
  [0x8791, { literal: '大⃝', args: 0 }],
  [0x8792, { literal: '小⃝', args: 0 }],
  [0x879B, { literal: '㊘', args: 0 }],
  [0x86A3, { literal: '♠', args: 0 }],
  [0x81A6, { literal: '☆', args: 0 }],
  [0x81BC, { literal: '⊂', args: 0 }],
  [0x81B8, { literal: '∈', args: 0 }],
  [0x86A4, { literal: '♣', args: 0 }],
  [0x869F, { literal: '♤', args: 1 }],
  [0x81A1, { literal: '■', args: 0 }],
  [0x87F0, { literal: '㍓', args: 1 }],
  [0x87F1, { literal: '♧', args: 1 }],
  [0x87F2, { literal: '☼', args: 0 }],
  [0x87F3, { literal: '▷', args: 0 }],
]);

let shiftJisDecoder = null;
function decodeShiftJisWord(word) {
  try {
    if (!shiftJisDecoder) shiftJisDecoder = new TextDecoder('shift_jis', { fatal: false });
    if (word <= 0xFF) return shiftJisDecoder.decode(Buffer.from([word]));
    return shiftJisDecoder.decode(Buffer.from([(word >> 8) & 0xFF, word & 0xFF]));
  } catch (_error) {
    return word <= 0xFF ? String.fromCharCode(word) : `\\x${word.toString(16).toUpperCase().padStart(4, '0')}`;
  }
}

function decodeJapaneseMessageBytes(buffer, start, hardEnd) {
  const limit = Math.min(buffer.length, hardEnd || (start + 0x8000));
  let out = '';
  for (let i = start; i + 1 < limit;) {
    const word = buffer.readUInt16BE(i);
    i += 2;
    const control = JP_CONTROL_READ.get(word);
    if (control) {
      if (control.end) break;
      out += control.literal;
      for (let a = 0; a < control.args && i + 1 < limit; a++) {
        let arg = buffer.readUInt16BE(i);
        i += 2;
        if (typeof control.subtract === 'number') arg -= control.subtract;
        out += arg.toString(16).toUpperCase().padStart(2, '0');
      }
      continue;
    }
    out += decodeShiftJisWord(word);
  }
  return out;
}

function loadCnCharmapReverse() {
  if (cnCharmapReverseCache) return cnCharmapReverseCache;
  let data = null;
  try {
    data = JSON.parse(fs.readFileSync(CN_CHARMAP_JSON_PATH, 'utf8'));
  } catch (error) {
    throw new Error(`CN charmap is missing or invalid: ${error.message}`);
  }
  const raw = data && typeof data === 'object' && data.codeToChar && typeof data.codeToChar === 'object' ? data.codeToChar : data;
  const map = new Map();
  for (const [key, value] of Object.entries(raw || {})) {
    const code = parseInt(String(key).replace(/^0x/i, ''), 16);
    if (Number.isFinite(code)) map.set(code, String(value));
  }
  cnCharmapReverseCache = map;
  return cnCharmapReverseCache;
}

const EN_CONTROL_ARG_LENGTHS = new Map([
  [0x00, 0], [0x01, 0], [0x02, 0], [0x04, 0], [0x05, 1], [0x06, 1], [0x07, 2],
  [0x08, 0], [0x09, 0], [0x0A, 0], [0x0B, 0], [0x0C, 1], [0x0E, 1], [0x0F, 0],
  [0x10, 0], [0x12, 2], [0x13, 1], [0x14, 1], [0x15, 3], [0x16, 0], [0x17, 0],
  [0x18, 0], [0x19, 0], [0x1A, 0], [0x1B, 0], [0x1C, 0], [0x1D, 0], [0x1E, 1],
  [0x1F, 0], [0xF0, 1], [0xF1, 1], [0xF2, 0], [0xF3, 0],
]);

function decodeChineseMessageBytes(buffer, start, hardEnd) {
  const map = loadCnCharmapReverse();
  const limit = Math.min(buffer.length, hardEnd || (start + 0x8000));
  let out = '';
  for (let i = start; i < limit;) {
    const byte = buffer[i++];
    if (byte === 0x02) break;
    if (EN_CONTROL_ARG_LENGTHS.has(byte)) {
      out += String.fromCharCode(byte);
      const argCount = EN_CONTROL_ARG_LENGTHS.get(byte) || 0;
      for (let a = 0; a < argCount && i < limit; a++) out += String.fromCharCode(buffer[i++]);
      continue;
    }
    if (byte >= 0x80 && i < limit) {
      const word = (byte << 8) | buffer[i];
      if (map.has(word)) {
        out += map.get(word);
        i += 1;
        continue;
      }
    }
    if (map.has(byte)) {
      out += map.get(byte);
    } else if (byte >= 0x20 && byte <= 0x7E) {
      out += String.fromCharCode(byte);
    } else {
      out += `\\x${byte.toString(16).toUpperCase().padStart(2, '0')}`;
    }
  }
  return out;
}

function extractPlainTextsFromRom(payload) {
  const romPath = normalizeRomPath(payload?.romPath);
  if (!romPath) throw new Error('ROM path is required.');
  const tableAddress = parseFlexibleHex(payload?.tableAddress, 'Table address');
  const textAddress = parseFlexibleHex(payload?.textAddress, 'Text address');
  const terminatorId = payload?.terminatorId === undefined || payload?.terminatorId === null || String(payload.terminatorId).trim() === ''
    ? 0xFFFF
    : parseFlexibleHex(payload.terminatorId, 'Terminator entry ID') & 0xFFFF;
  const buffer = fs.readFileSync(romPath);
  if (!isLikelyDecompressedRom(buffer)) {
    throw new Error('This extractor only accepts an already-decompressed ROM. Decompress the ROM first, then retry.');
  }
  if (tableAddress >= buffer.length || textAddress >= buffer.length) throw new Error('Table or text address is outside the ROM.');
  const base = detectPlainTextBase(payload, tableAddress, textAddress);
  const entries = [];
  let index = 0;
  let skippedSentinels = 0;
  let terminatorFound = null;
  while (true) {
    const entryOffset = tableAddress + index * 8;
    if (entryOffset + 8 > buffer.length) break;
    const id = buffer.readUInt16BE(entryOffset);
    if (id === terminatorId) {
      terminatorFound = id;
      break;
    }
    const opts = buffer[entryOffset + 2];
    const offset = readUInt24BE(buffer, entryOffset + 5);
    const nextOffset = entryOffset + 16 <= buffer.length ? readUInt24BE(buffer, entryOffset + 13) : offset + (base === 'jp' || base === 'cn' ? 0x8000 : 0x4000);
    if (id !== 0xFFFD) {
      const textStart = textAddress + offset;
      const textEnd = nextOffset > offset ? textAddress + nextOffset : textStart + (base === 'jp' || base === 'cn' ? 0x8000 : 0x4000);
      if (textStart >= 0 && textStart < buffer.length) {
        const text = base === 'jp'
          ? decodeJapaneseMessageBytes(buffer, textStart, textEnd)
          : base === 'cn'
            ? decodeChineseMessageBytes(buffer, textStart, textEnd)
            : decodeEnglishMessageBytes(readEnglishMessageBytes(buffer, textStart, textEnd));
        entries.push({ id, box_type: opts, text });
      }
    } else {
      skippedSentinels += 1;
    }
    index += 1;
    if (index > 0x8000) throw new Error('Message table terminator was not found before the safety limit. Check the table HEX address and Terminator entry ID.');
  }
  if (terminatorFound === null) {
    throw new Error(`Message table terminator 0x${terminatorId.toString(16).toUpperCase().padStart(4, '0')} was not found. Check the table HEX address or use the terminator used by this ROM/language patch.`);
  }
  return { entries, count: entries.length, tableEntriesRead: index, skippedSentinels, terminatorId, terminatorFound, source: romPath, tableAddress, textAddress, base };
}

// Configuration exposed to the renderer.
ipcMain.handle('ui:load', () => uiData);
ipcMain.handle('theme:load', () => themeData);
ipcMain.handle('workspace:load', () => workspaceDefinition);
ipcMain.handle('ui:get-language', () => currentLanguage);
ipcMain.handle('ui:set-language', (_event, language) => {
  currentLanguage = language || 'en';
  buildMenu();
  return currentLanguage;
});
ipcMain.handle('property:default', () => loadDefaultProperty());
ipcMain.handle('hintlist:order', () => parseHintListOrder());

// Property and change-set file commands.
async function openJsonFile(title) {
  const result = await dialog.showOpenDialog(mainWindow, {
    title,
    filters: [{ name: 'JSON', extensions: ['json'] }, { name: t('All files'), extensions: ['*'] }],
    properties: ['openFile'],
  });
  if (result.canceled || !result.filePaths.length) return null;
  const filePath = result.filePaths[0];
  const text = fs.readFileSync(filePath, 'utf8');
  return { filePath, data: JSON.parse(text) };
}

ipcMain.handle('property:open', () => openJsonFile(t('Load completed property.json...')));
ipcMain.handle('changes:open', () => openJsonFile(t('Import changes from property.json...')));

ipcMain.handle('property:save', async (_event, data, currentPath) => {
  const result = await dialog.showSaveDialog(mainWindow, {
    title: t('Export property.json...'),
    defaultPath: currentPath || 'property.json',
    filters: [{ name: 'JSON', extensions: ['json'] }, { name: t('All files'), extensions: ['*'] }],
  });
  if (result.canceled || !result.filePath) return null;
  fs.writeFileSync(result.filePath, JSON.stringify(data, null, 4), 'utf8');
  return { filePath: result.filePath };
});

ipcMain.handle('property:save-to-path', async (_event, data, filePath) => {
  if (!filePath) return null;
  fs.writeFileSync(filePath, JSON.stringify(data, null, 4), 'utf8');
  return { filePath };
});

ipcMain.handle('temp:write', async (_event, payload) => {
  const dir = path.join(app.getPath('userData'), 'language-editor-temp');
  fs.mkdirSync(dir, { recursive: true });
  const filePath = path.join(dir, 'property.temp.json');
  fs.writeFileSync(filePath, JSON.stringify(payload, null, 2) + '\n', 'utf8');
  const historyPath = path.join(dir, `property.${new Date().toISOString().replace(/[:.]/g, '-')}.temp.json`);
  fs.writeFileSync(historyPath, JSON.stringify(payload, null, 2) + '\n', 'utf8');
  const history = fs.readdirSync(dir).filter(name => /^property\..*\.temp\.json$/.test(name)).sort();
  while (history.length > 30) fs.rmSync(path.join(dir, history.shift()), { force: true });
  return { filePath };
});


// ROM, patch, and segment tools.
ipcMain.handle('rom:open', async (_event, titleText) => {
  const result = await dialog.showOpenDialog(mainWindow, {
    title: titleText || 'Select ROM',
    filters: [
      { name: 'N64 ROM', extensions: ['z64', 'n64', 'v64', 'rom', 'bin'] },
      { name: t('All files'), extensions: ['*'] },
    ],
    properties: ['openFile'],
  });
  if (result.canceled || !result.filePaths.length) return null;
  return { filePath: result.filePaths[0] };
});

ipcMain.handle('dir:open', async (_event, titleText) => {
  const result = await dialog.showOpenDialog(mainWindow, {
    title: titleText || 'Select folder',
    properties: ['openDirectory', 'createDirectory'],
  });
  if (result.canceled || !result.filePaths.length) return null;
  return { filePath: result.filePaths[0] };
});

ipcMain.handle('patch:ranges', () => DEFAULT_BIN_PATCH_RANGES);

ipcMain.handle('patch:generate', async (_event, payload) => {
  const originalPath = normalizeRomPath(payload?.originalPath);
  const modifiedPath = normalizeRomPath(payload?.modifiedPath);
  const outputDir = normalizeRomPath(payload?.outputDir);
  const items = Array.isArray(payload?.items) ? payload.items : [];
  if (!originalPath || !modifiedPath || !outputDir) throw new Error('Original ROM, modified ROM, and output folder are required.');
  fs.mkdirSync(outputDir, { recursive: true });
  const written = [];
  for (const item of items) {
    const key = String(item.key || '').trim();
    const filename = String(item.filename || key).trim();
    if (!key || !filename) continue;
    const range = DEFAULT_BIN_PATCH_RANGES[key];
    if (!range) throw new Error(`Unknown bin_patch key: ${key}`);
    const diff = xorCompressedDiff(originalPath, modifiedPath, range);
    const outPath = path.isAbsolute(filename) ? filename : path.join(outputDir, filename);
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, diff);
    written.push(outPath);
  }
  return { written };
});


ipcMain.handle('segment:export-many', async (_event, payload) => {
  const originalPath = normalizeRomPath(payload?.originalPath);
  const outputDir = normalizeRomPath(payload?.outputDir);
  const items = Array.isArray(payload?.items) ? payload.items : [];
  if (!originalPath || !outputDir) throw new Error('ROM and output folder are required.');
  if (!items.length) throw new Error('No raw segment presets are selected.');
  fs.mkdirSync(outputDir, { recursive: true });
  const written = [];
  for (const item of items) {
    const filename = String(item?.filename || item?.key || 'segment.bin').trim();
    const start = typeof item?.start === 'string' ? parseInt(item.start, 0) : Number(item?.start || 0);
    const size = typeof item?.size === 'string' ? parseInt(item.size, 0) : Number(item?.size || 0);
    if (!filename) continue;
    const outPath = path.isAbsolute(filename) ? filename : path.join(outputDir, filename);
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, rawSegment(originalPath, start, size));
    written.push(outPath);
  }
  return { written };
});

ipcMain.handle('segment:export', async (_event, payload) => {
  const originalPath = normalizeRomPath(payload?.originalPath);
  const outputDir = normalizeRomPath(payload?.outputDir);
  const filename = String(payload?.filename || 'segment.bin').trim();
  const start = typeof payload?.start === 'string' ? parseInt(payload.start, 0) : Number(payload?.start || 0);
  const size = typeof payload?.size === 'string' ? parseInt(payload.size, 0) : Number(payload?.size || 0);
  if (!originalPath || !outputDir || !filename) throw new Error('ROM, output folder, and filename are required.');
  fs.mkdirSync(outputDir, { recursive: true });
  const outPath = path.isAbsolute(filename) ? filename : path.join(outputDir, filename);
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, rawSegment(originalPath, start, size));
  return { filePath: outPath };
});


ipcMain.handle('rom:extract-plain-texts', async (_event, payload) => extractPlainTextsFromRom(payload));

// Work-file persistence.
ipcMain.handle('work:open', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    title: t('Open work file...'),
    filters: [
      { name: 'OOTR language editor work file', extensions: ['ootr-lang-work.json', 'json'] },
      { name: t('All files'), extensions: ['*'] },
    ],
    properties: ['openFile'],
  });
  if (result.canceled || !result.filePaths.length) return null;
  const filePath = result.filePaths[0];
  const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  return { filePath, data };
});

ipcMain.handle('work:save', async (_event, payload, currentPath) => {
  const result = await dialog.showSaveDialog(mainWindow, {
    title: t('Save work file...'),
    defaultPath: currentPath || 'language-editor.ootr-lang-work.json',
    filters: [
      { name: 'OOTR language editor work file', extensions: ['ootr-lang-work.json', 'json'] },
      { name: t('All files'), extensions: ['*'] },
    ],
  });
  if (result.canceled || !result.filePath) return null;
  fs.writeFileSync(result.filePath, JSON.stringify(payload, null, 2) + '\n', 'utf8');
  return { filePath: result.filePath };
});

// Application startup.
app.whenReady().then(() => {
  if (process.platform === 'darwin' && typeof app.setAccessibilitySupportEnabled === 'function') {
    app.setAccessibilitySupportEnabled(false);
  }
  loadUiData();
  loadWorkspaceDefinition();
  loadThemeData();
  loadDefaultProperty();
  buildMenu();
  createWindow();
});

app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
