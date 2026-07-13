# OoTR language files and Language Editor

Language data lives in `data/lang/<Language>/property.json`. The optional Electron
editor is located at `GUI/devtools/language-editor` and is intended for language
maintainers; it does not replace the main randomizer GUI.

## Start the editor

From the repository root:

```bash
node GUI/devtools/language-editor/run.js
```

The editor uses the repository's existing Electron installation.
So in order to work with it, you need to run `Gui.py` before.

## Reviewable file layout

```text
GUI/devtools/language-editor/
├── index.html              renderer and feature blocks
├── main.js                 Electron windows, menus, file/ROM IPC
├── preload.js              narrow renderer API
├── run.js                  Electron launcher
├── workspace.json          panels, default layout, change view, workspace styles
├── theme.json              developer UI themes
├── language_editor_ui.json complete UI translations
└── charmap.chn.json        Chinese character map data
```

There are no additional JavaScript modules or distributed test files in this
folder. New UI features should first declare their panel/configuration in
`workspace.json`, then add the renderer behavior near the related feature block
in `index.html`, and expose privileged operations through `preload.js` and
`main.js` only when required.

## Language rendering fields

### `lang_property.wide_text_english_metrics`

For `base: "jp"`, uses English-like character scale, line spacing, icon placement,
and choice-cursor placement while retaining JP/wide message encoding.

### `CHAR_WIDTHS`

Overrides character widths.

- Narrow languages may use a visible character, symbolic name, message byte, or
  `index:<n>`.
- Wide languages use Shift-JIS codes such as `0x824F`.
- Values may be one number or a `{default, ntsc, pal}` object.
- Missing narrow entries keep the original width table value.
- Missing wide entries keep width 16.

Examples:

```text
W => 15
index:143 => 14
0x824F => {"default":12,"ntsc":12,"pal":12}
```

### `dpad_menu`

Contains six labels, exactly 15 dungeon names, and exactly 9 boss names. The
complete section falls back to English only when it is absent. A partial section
is rejected so translated and English menu information cannot be mixed.

JP/wide D-pad text is stored as Shift-JIS `u16` glyph codes and rendered through
the wide font loader. Seed-dependent entrance, boss-destination, and reward-area
names come from the selected language's hint-area data.

### `replace_table`

Contains simultaneous language-wide text replacements. Each rule uses `from` and
`to`. Control-code sequences are protected during replacement, and a replacement
result is not processed again by a later rule in the same pass. Legacy
`language_specific_replace_table` remains accepted.

## Editor behavior

- Top-level property keys are sections; nested keys never become other sections.
- Changes can be imported selectively and reviewed in a Git-style view.
- Entries continuously show `A`, `M`, and `D` relative to the last load or
  property export.
- Dock panels can be moved, tabbed, resized, persisted, and reset from View.
- Details shows only Selected section, Selected entry, and Section note.
- Entry editor type is always automatic.
- Memo opens in a separate window and is saved only in work files/local editor
  state, never in `property.json`.
- Closing with unsaved data opens the in-page Save/Don't Save/Cancel dialog.

## Build requirement

Changes to `CHAR_WIDTHS`, wide metrics, or D-pad runtime tables require rebuilding
the ASM payload with the user's own uncompressed base ROM:

```bash
cd ASM
python3 build.py
```

See `Notes/multilingual-implementation.md` for the source review order and exact
generated files.
