# OoTR Language File
This file contains multiple language files
Language file can be created using following tool

## OoTR Language Property Editor

OoTR Language Property Editor is a small Electron-based support tool for maintaining language `property.json` files for the Ocarina of Time Randomizer project.

It is intended for language maintainers, translators, and developers who need to inspect or edit language property data without using a Python GUI toolkit. It does not replace the main randomizer GUI and is not part of normal seed generation.

## Repository layout

Place the tool in the repository like this:

```text
OoT-Randomizer/
  GUI/
    devtools/
      language-editor/
        run.js
        main.js
        preload.js
        index.html
        language_editor_ui.json
  data/
    lang/
      English/
        property.json
      README.md
  HintList.py
```

The application files live under `GUI/devtools/language-editor/` so the main GUI source remains untouched. This README lives in `data/lang/` so language maintainers can find the tool documentation near the language assets.

## Start the tool

From the repository root:

```bash
node GUI/devtools/language-editor/run.js
```

The tool uses the repository's existing Node/Electron environment. If the GUI dependencies have not been installed yet, install them from the repository's `GUI/` directory first.

## Main purpose

Use this tool to:

- load a completed language `property.json`
- inspect top-level language property sections
- edit message text with readable control-code markup
- edit dictionary-like tables in a compact `source => replacement` form
- edit structured tables such as hint tables, goal tables, dungeon data, and character-width data
- merge missing known defaults into a loaded property file
- export a completed `property.json`
- generate selected language patch files from ROM differences
- export selected raw ROM segments used by language graphics work

## Main window

The window is split into three working areas:

1. **Sections**: choose the top-level property section.
2. **Entries**: choose an entry inside the selected section.
3. **Editor tabs**: edit or inspect the selected value.

The right side uses tabs:

- **Text editor**: friendly editing view for messages, mappings, and structured values.
- **Raw preview**: JSON-style preview of the selected value.
- **Section JSON**: full JSON editor for the current section.
- **Patch maker**: ROM diff and raw segment helper.

The panes are resizable. Drag the splitters between panes to adjust the working area.

## Loading and saving

Use the menu or shortcuts to load and export data:

```text
Ctrl/Cmd+O  Load property.json
Ctrl/Cmd+S  Export property.json
```

When a file is loaded, missing known sections and known language metadata fields can be filled from `data/lang/English/property.json`. The tool does not embed the default property data in JavaScript. Exported JSON keeps a stable top-level section order where possible.

`hintTable` entry ordering is read from the repository `HintList.py` at runtime, so the editor follows the same order used by hint generation without maintaining a copied order list inside the UI code.

## Entry names and numeric display

Entries that contain an `id` are displayed by ID.

```text
0x001C
0x90A7
```

Numeric display rules:

```text
id       -> 0x0000
box_type -> 0x00
```

## Editor types

Each entry can be displayed with an editor type. The default is automatic detection.

Available modes:

- **Auto**: choose a suitable editor automatically.
- **String dictionary**: show string-to-string dictionaries as `source => replacement`.
- **Friendly value**: use section-specific display rules.
- **JSON**: edit raw JSON for the selected value.

For string-to-string dictionaries, the preferred editing form is:

```text
source => replacement
another source => another replacement
```

No double quotes are required in this view.

## Message control-code markup

The Text editor converts common message control codes to readable markup.

Examples:

```text
<line-break>
<box-break>
<color 41>
<icon 2D>
<sound 4802>
<goto 1234>
<wait 20>
<name>
```

Color markers, placeholders, and language-format paths are highlighted in the editor.

Examples:

```text
<color>important text<color>
{color}
[prefix.definite.nominative.masculine]
```

The Raw preview tab shows the selected value in the form that will be written to JSON.

## Section-specific editing

### `lang_property`

Language metadata can be edited through dedicated fields where possible.

Common fields include:

- `display_name`
- `description`
- `base`
- `align_text`
- `wide_text_english_metrics`

`wide_text_english_metrics` is shown as a boolean checkbox.
`align_text` is shown as a fixed-choice field.
`base` is shown as a fixed-choice field.

### `CHAR_WIDTHS`

`CHAR_WIDTHS` is edited as a character-width table.

Examples:

```text
W => 15
í => 8
index:143 => 14
0x824F => {"default":12,"ntsc":12,"pal":12}
```

Values may be numbers or JSON objects.

### `replace_table`

This section stores language-wide text replacement rules. Each rule is saved as an object with `from` and `to` strings. In the editor, each entry is edited as a block:

```text
[from]
source text

[to]
replacement text
```

When creating or editing an entry, you may also paste multiple arrow-style rules. Saving that draft creates multiple `replace_table` entries at once:

```text
a => 0x819F
A => 0x81A0
```

The replacement pass is intended for cleanup, contraction, spacing, or other language-wide text normalization. All rules are applied simultaneously against the original text, so a result produced by one rule is not processed again by another rule in the same pass. For example, `A => B` and `B => C` changes `ABCD` into `BCCD`, not `CCCD`.

Shift-JIS byte tokens are supported in `from` and `to`. A value written as `0xNN`, `0xNNNN`, `sjis:0xNNNN`, or `shift-jis:0xNNNN` is decoded as Shift-JIS bytes before the rule is applied. `replace_table` is plain text replacement data; control codes are not authored or converted inside this section. Text control codes already present in game text are protected during replacement so ordinary character rules do not rewrite control-code bytes or their arguments.

### `hintTable`

`hintTable` entries expose:

- vague hint
- clear hint
- gender

A vague hint may be empty, a single line, or multiple lines. The editor converts it back to the appropriate JSON form on apply/export.

### Goal tables

`BOSS_GOAL_TABLE` and `REWARD_GOAL_TABLE` expose clear and vague goal names.

Color markers can be edited in the friendly text view and checked in the Raw preview.

### `dungeon_list`

`dungeon_list` entries expose:

- name
- gender
- has_map

`has_map` is treated as a boolean value.

## Entry operations

The entry list supports:

- Add entry
- Delete entry
- Copy entry
- Paste entry
- Duplicate entry
- Move entry up/down
- Sort by ID
- Multi-select entries with Shift+Click and Ctrl/Cmd+Click

When entries with IDs are pasted or duplicated, the tool asks for new IDs before insertion. Multiple selected entries can be copied, pasted, duplicated, deleted, moved, or reordered together.

## Shortcuts

General editing:

```text
Ctrl/Cmd+C        Copy selected text
Ctrl/Cmd+V        Paste text
Ctrl/Cmd+X        Cut text
Ctrl/Cmd+A        Select all text
Ctrl/Cmd+Z        Undo
Ctrl/Cmd+Y        Redo
```

Tool actions:

```text
Ctrl/Cmd+O        Load property.json
Ctrl/Cmd+S        Export property.json
Ctrl/Cmd+Enter    Apply editor contents
Ctrl/Cmd+F        Focus section search
Ctrl/Cmd+Shift+F  Focus entry search
```

Entry actions:

```text
Ctrl/Cmd+N                  Add entry
Ctrl/Cmd+Shift+C            Copy selected entry/entries
Ctrl/Cmd+Shift+V            Paste copied entry/entries
Ctrl/Cmd+Shift+D            Duplicate selected entry/entries
Ctrl/Cmd+Shift+A            Select all visible entries
Ctrl/Cmd+Backspace/Delete   Delete selected entry/entries
Ctrl/Cmd+Alt+Up             Move selected entry/entries up
Ctrl/Cmd+Alt+Down           Move selected entry/entries down
Esc                         Reduce multi-selection to the active entry
```

Tabs:

```text
Ctrl/Cmd+1  Text editor
Ctrl/Cmd+2  Raw preview
Ctrl/Cmd+3  Section JSON
Ctrl/Cmd+4  Patch maker
```

Patch maker:

```text
Ctrl/Cmd+Alt+P  Generate checked diff patches
Ctrl/Cmd+Alt+R  Export checked raw segments
```

## Patch maker

The Patch maker tab can create language patch files and export raw ROM segments.

It supports:

- selecting an original ROM
- selecting a modified ROM
- selecting patch ranges
- generating compressed XOR patch files
- exporting raw ROM segments

The raw segment presets focus on the blue-fire item-name graphics:

```text
blue_fire_arrow_item_name_jap.ia4  start 0x883000  size 0x400
blue_fire_arrow_item_name_eng.ia4  start 0x8A1C00  size 0x400
```

Both presets can be selected and exported together.

## UI language

The tool UI uses `language_editor_ui.json`.

The translation system uses exact full-sentence keys instead of partial word replacement. This avoids mixed-language UI strings and makes missing translations easier to find.

Supported UI languages:

- English
- 日本語
- Español
- Français
- Deutsch
- Русский
- 简体中文
- 繁體中文
- 한국어

Use the app menu:

```text
Edit > Language
```

## Notes before committing

Before committing edited language data:

1. Export the completed `property.json`.
2. Review the Raw preview or exported JSON for the edited sections.
3. Run the repository's normal validation, build, or language-generation steps.
4. Confirm that generated ROM text, patch files, and raw segment files behave as expected.

## Scope

This tool is for language maintenance only. It does not generate seeds, does not replace the main GUI, and does not change the repository's normal randomizer workflow.


## Entry save and ID editing

Use **Save entry** to write the current Text editor contents back into the selected entry without exporting the whole property file. ID-based entries show an **Entry ID** field in hexadecimal form. Use **Apply ID** to change that ID after adding, pasting, or duplicating an entry. When an ID-based entry is duplicated or pasted, the tool asks for the new ID before inserting the entry.

Useful shortcuts:

- `Ctrl/Cmd+Shift+S`: Save entry
- `Ctrl/Cmd+Shift+D`: Duplicate entry
- `Ctrl/Cmd+Alt+I`: Apply ID


## Editing safety and validation

The editor includes several safeguards for language maintenance work. Use **Save entry** to commit the current entry text into the in-memory property data before switching entries or exporting. When an edited entry still has an unsaved draft, the tool warns before changing context.

For message-like entries, the **Entry ID** field accepts hexadecimal IDs such as `0x00F3`. Use **Next ID** to fill the next available ID, **Apply ID** to commit it, and **Validate** to check for duplicate IDs or invalid fields. Entry lists can be moved up or down and sorted by ID when every entry in the section has an ID.

The text editor also includes local find and replace controls for the current entry. These only modify the editor draft; use **Save entry** or **Apply editor** after replacing text.

## Editing safety tools

The editor includes additional safeguards for language maintenance:

- Entry copy, paste, and duplication can assign a new unique ID before insertion.
- Entry rows in list-style sections can be reordered by drag and drop. If several rows are selected, dragging one selected row moves the selected group together.
- The bulk text replacement tool can replace text in the current entry, current section, or all text sections while preserving message control codes.
- Language metadata, character widths, and replacement lists are kept separate during editing and export. Top-level sections are removed from nested entries if they appear in the wrong place.
- The UI language menu also includes Simplified Chinese, Traditional Chinese, and Korean.


## Global entry text replacement

Use **Edit > Replace text in all entries...** to open a separate replacement window for all editable entries. Enter the source text and replacement text there, then run the replacement after confirming the detected match count. Control-code bytes are protected during replacement so that color, icon, sound, jump, and other control arguments are not modified as ordinary text. The shortcut is `Ctrl/Cmd + Alt + Shift + R`.


## Language properties panel

`lang_property` is edited in the dedicated Language properties panel above the section list. It is not shown as a normal section because it controls the whole language file.

The panel provides fixed choices for `base` (`en` or `jp`) and `align_text` (`Left`, `Center`, or `Right`), plus fields for `display_name`, `description`, and `wide_text_english_metrics`. These values are still exported under the top-level `lang_property` key in `property.json`.

## macOS stability notes

On macOS, this tool avoids native modal child windows for editor confirmations and global text replacement. Confirmation panels are rendered inside the main editor window so that closing the panels does not create or destroy additional Electron BrowserWindow instances.

The tool also disables renderer accessibility support and hardware acceleration at startup. This is intended to avoid macOS AppKit accessibility cleanup crashes in older Electron runtimes while preserving the editor's normal file loading, saving, and language-editing behavior.


## Language base conversion

When **Language base** is changed between `en` and `jp`, the editor converts only text control codes to the selected base representation. Ordinary text characters are left unchanged.


### Control code color names

The editor normalizes text color control codes to shared names such as `<color red>`, `<color green>`, `<color blue>`, and `<color yellow>`. This avoids differences between English and Japanese internal control-code encodings. Numeric color arguments are accepted only in the `00` to `47` range; values outside that range, such as `BA`, are treated as ordinary text rather than color control arguments.


## Color control codes

The editor displays colors with shared names such as `<color red>`. English text writes color arguments as `0x40` through `0x47`, while Japanese text writes color arguments as `0x00` through `0x07`. Changing the language base converts only the control-code representation; normal text is kept unchanged.


## UI visibility toggles

The editor shows collapse toggles above each major region. They can hide non-essential regions to give the Text editor more space. These toggles only affect the editor layout and do not change `property.json`.

Available toggles:

- Language properties
- Sections
- Entries
- Details / mode hints
- Text editor tools

The workspace also keeps a compact top toggle bar for Sections, Entries, Details, and Text tools, so a hidden region can always be restored from above the workspace. The Language properties toggle remains above the Language properties panel.

## Editor UI notes

- `pronoun_mapping` and `verb_mapping` are treated as strict language-owned mappings. Default English replacement pairs are removed on load, merge, and export unless they were changed into custom values.
- `hintTable` is displayed and exported in the same key order as `HintList.py` so the editor order matches the runtime hint traversal order.
- In the Text editor, typing `[` opens a property-path suggestion list built from the current property data. Closing with `]` hides it. External placeholders inside a path, such as `{position}`, are highlighted because they are supplied at runtime.
- Each major UI region has a local collapse button in its title, shown as `▼ Name` or `▶ Name`, so the Text editor can be given more space without changing `property.json`.
- `IMPORTANT_ITEM_MESSAGES` has a quick preset panel for boss keys, maps, compasses, and generated key/key-ring message series in the runtime message order.


## Developer view preferences

Use **View > Increase UI text size**, **View > Decrease UI text size**, or **View > Reset UI text size** to scale the editor text. The same actions are available with `Ctrl/Cmd + Plus`, `Ctrl/Cmd + Minus`, and `Ctrl/Cmd + 0`.

Use **View > UI theme** to switch between `Light`, `Dark`, `Link`, `Zelda`, `Ganon`, `Triforce`, `Kakariko`, and `OoT`. The default theme is `Dark`. These preferences are stored in local editor settings and are not written to `property.json`.

Theme palettes are defined in `GUI/devtools/language-editor/theme.json`. Edit that file to adjust colors or add a new developer-only theme without touching the main HTML source.

## Smart copy / paste / duplicate

The Entries toolbar is intentionally compact. Only `+`, `−`, `↑`, and `↓` remain visible there; copy, paste, duplicate, sort, and validation actions are available from the menu and shortcuts so the entry list has more room.

`Ctrl/Cmd + C`, `Ctrl/Cmd + V`, and `Ctrl/Cmd + D` operate on the last clicked editor region:

- Last clicked section list: copy, paste, or duplicate the whole section.
- Last clicked entry list: copy, paste, or duplicate the selected entry or selected entry group.
- Last clicked text editor: copy, paste, or duplicate the selected text. If no text is selected, copy uses the whole text field and duplicate duplicates the current line.

Language property Apply and Reset buttons use two-line labels so their full meaning remains visible in narrow layouts.

`CHAR_WIDTHS` is edited as individual key/value entries. The Text editor also accepts multiple `key => width` lines at once, for example `W => 15` and `index:143 => 14`, so character-width rows can be added in batches.

## Additional developer workflow features

### ROM to PLAIN_TEXTS extractor

The Patch maker tab includes a ROM to PLAIN_TEXTS panel. It reads an already-decompressed ROM only. Select the ROM, enter the message table ROM offset, text data ROM offset, and terminator entry ID as hexadecimal values, then choose either Replace PLAIN_TEXTS or Append to PLAIN_TEXTS. The extractor reads until the configured terminator entry ID instead of using a manual count. For a decompressed NTSC 1.0 English ROM, the default addresses are table `0xB849EC`, text `0x92D000`, and terminator `0xFFFF`. For nonstandard or language-patched ROMs, set the terminator ID used by that ROM, such as `0xFFFC` when appropriate.

The extractor reads 8-byte message table records, uses the 24-bit text offset from each record, derives each message length from the next table record, removes the message end code, and writes the result as PLAIN_TEXTS message entries with id, box_type, and text fields.

### Work memo and work files

The Memo panel is a separate floating workspace area for temporary translation or editing notes. Memo text is not exported into property.json. To keep memo text between sessions, use File > Save work file. Work files store the current property data plus the memo in a separate editor-only JSON format.

### Context menus and control-code input

Right-click the section list, entry list, text editor, raw preview, section JSON editor, language properties, patch panel, or memo panel to open a context menu for that area. Each context menu contains common edit actions plus area-specific actions such as section merge/validation, entry add/delete/move, text control-code insertion, section JSON apply, ROM extraction, and memo work-file actions. In the text editor, type `<` to open control-code suggestions. Common shortcuts are also available: Alt+Enter inserts a line break marker, Alt+Shift+Enter inserts a box break marker, and Alt+0 through Alt+7 insert color markers.
