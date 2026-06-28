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
      README.md
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

When a file is loaded, missing known sections and known language metadata fields can be filled from the embedded default template. Exported JSON keeps a stable top-level section order where possible.

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

### `language_specific_replace_table`

This section is edited as a replacement table.

```text
from text => to text
```

Use it for language-specific cleanup, contraction, spacing, or replacement rules that should be applied consistently.

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

When an entry with an `id` is pasted, the tool can assign a new ID to avoid direct duplication.

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
Ctrl/Cmd+Shift+C            Copy entry
Ctrl/Cmd+Shift+V            Paste entry
Ctrl/Cmd+Backspace/Delete   Delete entry
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
