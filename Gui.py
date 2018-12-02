#!/usr/bin/env python3
import json
import re
import os
import tkinter as tk
import webbrowser

from tkinter import ttk, colorchooser

from GuiUtils import ToolTips, set_icon, BackgroundTask, BackgroundTaskProgress, Dialog, ValidatingEntry, SearchBox
from Main import main, from_patch_file
from Utils import is_bundled, local_path, data_path, default_output_path, open_file, check_version
from Settings import Settings
from SettingsList import setting_infos
from version import __version__ as ESVersion
import WorldFile
from LocationList import location_table

def settings_to_guivars(settings, guivars):
    for info in setting_infos:
        name = info.name
        if name not in guivars:
            continue
        guivar = guivars[name]
        value = settings.__dict__[name]
        # Checkbox
        if info.type == bool:
            guivar.set(int(value))
        # Dropdown/radiobox
        if info.type == str:
            if value is None:
                guivar.set("")
            else:
                if info.gui_params and 'options' in info.gui_params:
                    if 'Custom Color' in info.gui_params['options'] and re.match(r'^[A-Fa-f0-9]{6}$', value):
                        guivar.set('Custom (#' + value + ')')
                    else:
                        for gui_text,gui_value in info.gui_params['options'].items():
                            if gui_value == value:
                                guivar.set(gui_text)
                else:
                    guivar.set(value)
        # Text field for a number...
        if info.type == int:
            if value is None:
                guivar.set(str(1))
            else:
                guivar.set(str(value))
        if info.type == list:
            guivars[info.name] = list(value)


def guivars_to_settings(guivars):
    result = {}
    for info in setting_infos:
        name = info.name
        if name not in guivars:
            result[name] = None
            continue
        guivar = guivars[name]
        # Checkbox
        if info.type == bool:
            result[name] = bool(guivar.get())
        # Dropdown/radiobox
        if info.type == str:
            # Set guivar to hexcode if custom color
            if re.match(r'^Custom \(#[A-Fa-f0-9]{6}\)$', guivar.get()):
                result[name] = re.findall(r'[A-Fa-f0-9]{6}', guivar.get())[0]
            elif info.gui_params and 'options' in info.gui_params:
                result[name] = info.gui_params['options'][guivar.get()]
            else:
                result[name] = guivar.get()
        # Text field for a number...
        if info.type == int:
            try:
                result[name] = int(guivar.get())
            except ValueError:
                result[name] = 0
        if info.type == list:
            result[name] = list(guivars[name])

    if result['seed'] == "":
        result['seed'] = None
    if result['count'] == 1:
        result['count'] = None

    return Settings(result)

def guiMain(settings=None):
    mainWindow = tk.Tk()
    mainWindow.wm_title("OoT Randomizer %s" % ESVersion)
    mainWindow.resizable(False, False)
    set_icon(mainWindow)
    notebook = ttk.Notebook(mainWindow)
    tab_labels = {
            'rom_tab':       'ROM Options',
            'rules_tab':     'Main Rules',
            'logic_tab':     'Detailed Logic',
            'other_tab':     'Other',
            'aesthetic_tab': 'Cosmetics',
            }

    frames = {}
    for frame, name in tab_labels.items():
        frames[frame] = ttk.Frame(notebook)
        notebook.add(frames[frame], text=name)

    frames['aesthetic_tab_left']  = tk.Frame(frames['aesthetic_tab'])
    frames['aesthetic_tab_right'] = tk.Frame(frames['aesthetic_tab'])

    #######################
    # Randomizer controls #
    #######################

    # Hold the results of the user's decisions here
    guivars      = {}
    widgets      = {}
    dependencies = {}
    presets      = {}

    frame_hierarchy = {
            'rules_tab': {
                'world':             'World',
                'open':              'Open',
                'logic':             'Shuffle',
                },
            'logic_tab': {
                'rewards':           'Remove Specific Locations',
                'tricks':            'Specific Expected Tricks',
                },
            'other_tab': {
                'convenience':       'Speedups',
                'other':             'Misc',
                },
            'aesthetic_tab': {
                'cosmetics':         'General',
                },
            'aesthetic_tab_left': {
                'tunic_color':       'Tunic Color',
                'lowhp':             'Low HP SFX',
                },
            'aesthetic_tab_right': {
                'navi_color':        'Navi Color',
                'navihint':          'Navi SFX',
                },
            }

    for tab in frame_hierarchy:
        for frame, label in frame_hierarchy[tab].items():
            frames[frame] = tk.LabelFrame(frames[tab], text=label, labelanchor=tk.NW)


    # Shared
    def toggle_widget(widget, enabled):
        widget_type = widget.winfo_class()
        if widget_type == 'Frame' or widget_type == 'TFrame' or widget_type == 'Labelframe':
            if widget_type == 'Labelframe':
                widget.configure(fg='Black'if enabled else 'Grey')
            for child in widget.winfo_children():
                toggle_widget(child, enabled)
        else:
            if widget_type == 'TCombobox':
                widget.configure(state= 'readonly' if enabled else 'disabled')
            else:
                widget.configure(state= 'normal' if enabled else 'disabled')

            if widget_type == 'Scale':
                widget.configure(fg='Black'if enabled else 'Grey')


    def check_dependency(name):
        setting_state = {}
        for key in list(guivars.keys()):
            # This breaks with types other than string, int, double, or bool.
            # We'll have to rework dependency handling if we need to allow for
            # checking lists. Until then we shall just skip them.
            if not (isinstance(guivars[key], list)):
                setting_state[key] = guivars[key].get()

        if name in dependencies:
            return dependencies[name](setting_state)
        else:
            return True


    def show_settings(*event):
        settings = guivars_to_settings(guivars)
        settings_string_var.set(settings.get_settings_string())

        # Update any dependencies
        for info in setting_infos:
            dep_met = check_dependency(info.name)

            if info.name in widgets:
                toggle_widget(widgets[info.name], dep_met)

            if info.type == list:
                widgets[info.name].delete(0, tk.END)
                widgets[info.name].insert(0, *guivars[info.name])

            if info.type != list and info.name in guivars and guivars[info.name].get() == 'Custom Color':
                color = colorchooser.askcolor()
                if color == (None, None):
                    color = ((0,0,0),'#000000')
                guivars[info.name].set('Custom (' + color[1] + ')')
        update_generation_type()


    def update_logic_tricks_children():
        for info in setting_infos:
            if info.gui_params \
            and info.gui_params.get('widget') == 'Checkbutton' \
            and info.gui_params['group'] == 'tricks':
                if guivars['all_logic_tricks'].get():
                    widgets[info.name].select()
                else:
                    widgets[info.name].deselect()
        settings = guivars_to_settings(guivars)
        settings_string_var.set(settings.get_settings_string())


    def update_logic_tricks_parent():
        are_all_enabled = True
        for info in setting_infos:
            if info.gui_params \
            and info.gui_params.get('widget') == 'Checkbutton' \
            and info.gui_params['group'] == 'tricks':
                if guivars[info.name].get() == False:
                    are_all_enabled = False
        if are_all_enabled:
            widgets['all_logic_tricks'].select()
        else:
            widgets['all_logic_tricks'].deselect()
        settings = guivars_to_settings(guivars)
        settings_string_var.set(settings.get_settings_string())


    fileDialogFrame = tk.Frame(frames['rom_tab'])

    romDialogFrame = tk.Frame(fileDialogFrame)
    baseRomLabel = tk.Label(romDialogFrame, text='Base ROM')
    guivars['rom'] = tk.StringVar(value='')
    romEntry = tk.Entry(romDialogFrame, textvariable=guivars['rom'], width=40)

    def RomSelect():
        rom = tk.filedialog.askopenfilename(filetypes=[("ROM Files", (".z64", ".n64")), ("All Files", "*")])
        if rom != '':
            guivars['rom'].set(rom)
    romSelectButton = tk.Button(romDialogFrame, text='Select ROM', command=RomSelect, width=10)

    baseRomLabel.pack(side=tk.LEFT, padx=(38,0))
    romEntry.pack(side=tk.LEFT, padx=3)
    romSelectButton.pack(side=tk.LEFT)

    romDialogFrame.pack()

    fileDialogFrame.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=(5,1))

    def output_dir_select():
        rom = tk.filedialog.askdirectory(initialdir = default_output_path(guivars['output_dir'].get()))
        if rom != '':
            guivars['output_dir'].set(rom)

    outputDialogFrame = tk.Frame(frames['rom_tab'])
    outputDirLabel = tk.Label(outputDialogFrame, text='Output Directory')
    guivars['output_dir'] = tk.StringVar(value='')
    outputDirEntry = tk.Entry(outputDialogFrame, textvariable=guivars['output_dir'], width=40)
    outputDirButton = tk.Button(outputDialogFrame, text='Select Dir', command=output_dir_select, width=10)
    outputDirLabel.pack(side=tk.LEFT, padx=(3,0))
    outputDirEntry.pack(side=tk.LEFT, padx=3)
    outputDirButton.pack(side=tk.LEFT)
    outputDialogFrame.pack(side=tk.TOP, anchor=tk.W, pady=3)

    countDialogFrame = tk.Frame(frames['rom_tab'])
    countLabel = tk.Label(countDialogFrame, text='Generation Count')
    guivars['count'] = tk.StringVar()
    widgets['count'] = tk.Spinbox(countDialogFrame, from_=1, to=100, textvariable=guivars['count'], width=3)

    if os.path.exists(local_path('README.html')):
        def open_readme():
            open_file(local_path('README.html'))
        openReadmeButton = tk.Button(countDialogFrame, text='Open Documentation', command=open_readme)
        openReadmeButton.pack(side=tk.RIGHT, padx=5)

    countLabel.pack(side=tk.LEFT)
    widgets['count'].pack(side=tk.LEFT, padx=2)
    countDialogFrame.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=(1,1))

    # Build gui
    ############

    # Add special checkbox to toggle all logic tricks
    guivars['all_logic_tricks'] = tk.IntVar(value=0)
    widgets['all_logic_tricks'] = tk.Checkbutton(
            frames['tricks'],
            text="Enable All Tricks",
            variable=guivars['all_logic_tricks'],
            justify=tk.LEFT,
            wraplength=190,
            command=update_logic_tricks_children)
    widgets['all_logic_tricks'].pack(expand=False, anchor=tk.W)


    location_names = [name for name, (type, scene, default, hint, addresses) in location_table.items() if
        scene is not None and default is not None]
    widgets['disabled_location_entry'] = SearchBox(frames['rewards'], location_names, width=30)
    widgets['disabled_location_entry'].pack(expand=False, side=tk.TOP, anchor=tk.W, padx=3, pady=3)

    location_frame = tk.Frame(frames['rewards'])
    scrollbar = tk.Scrollbar(location_frame, orient=tk.VERTICAL)
    widgets['disabled_locations'] = tk.Listbox(location_frame, width=30, yscrollcommand=scrollbar.set)
    guivars['disabled_locations'] = []
    scrollbar.config(command=widgets['disabled_locations'].yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    widgets['disabled_locations'].pack(side=tk.LEFT)
    location_frame.pack(expand=False, side=tk.TOP, anchor=tk.W, padx=3, pady=3)

    def add_disabled_location():
        new_location = widgets['disabled_location_entry'].get()
        if new_location in widgets['disabled_location_entry'].options \
                and new_location not in widgets['disabled_locations'].get(0, tk.END):
            widgets['disabled_locations'].insert(tk.END, new_location)
            guivars['disabled_locations'].append(new_location)
        show_settings()

    def remove_disabled_location():
        location = widgets['disabled_locations'].get(tk.ACTIVE)
        widgets['disabled_locations'].delete(tk.ACTIVE)
        guivars['disabled_locations'].remove(location)
        show_settings()

    location_button_frame = tk.Frame(frames['rewards'])
    widgets['disabled_location_add'] = tk.Button(location_button_frame, text='Add', command=add_disabled_location)
    widgets['disabled_location_add'].pack(side=tk.LEFT, anchor=tk.N, padx=3, pady=3)
    widgets['disabled_location_remove'] = tk.Button(location_button_frame, text='Remove', command=remove_disabled_location)
    widgets['disabled_location_remove'].pack(side=tk.LEFT, anchor=tk.N, padx=3, pady=3)
    location_button_frame.pack(expand=False, side=tk.TOP, padx=3, pady=3)

    disabled_location_tooltip = '''
        Prevent locations from being required. Major
        items can still appear there, however they
        will never be required to beat the game.

        Most dungeon locations have a MQ alternative.
        If the location does not exist because of MQ
        then it will be ignored. So make sure to
        disable both versions if that is the intent.
    '''

    ToolTips.register(widgets['disabled_location_entry'], disabled_location_tooltip)
    ToolTips.register(location_frame, disabled_location_tooltip)

    for info in setting_infos:
        if info.dependency is not None:
            dependencies[info.name] = info.dependency

        if info.gui_params and 'group' in info.gui_params:
            if info.gui_params['widget'] == 'Checkbutton':
                default_value = 1 if info.gui_params['default'] == "checked" else 0
                # Link a variable to the widget's state
                guivars[info.name] = tk.IntVar(value=default_value)
                if info.gui_params['group'] == 'tricks':
                    c = update_logic_tricks_parent
                else:
                    c = show_settings

                widgets[info.name] = tk.Checkbutton(
                        frames[info.gui_params['group']],
                        text=info.gui_params['text'],
                        variable=guivars[info.name],
                        justify=tk.LEFT,
                        wraplength=190,
                        command=c)
                widgets[info.name].pack(expand=False, anchor=tk.W)

            elif info.gui_params['widget'] == 'Combobox':
                # Link a variable to the widget's state
                guivars[info.name] = tk.StringVar(value=info.gui_params['default'])
                # Create the option menu
                widgets[info.name] = tk.Frame(frames[info.gui_params['group']])
                if isinstance(info.gui_params['options'], list):
                    info.gui_params['options'] = dict(zip(
                        info.gui_params['options'],
                        info.gui_params['options']))

                dropdown = ttk.Combobox(
                        widgets[info.name],
                        textvariable=guivars[info.name],
                        values=list(info.gui_params['options'].keys()),
                        state='readonly',
                        width=30)
                dropdown.bind("<<ComboboxSelected>>", show_settings)
                dropdown.pack(side=tk.BOTTOM, anchor=tk.W)

                if 'text' in info.gui_params:
                    label = tk.Label(widgets[info.name], text=info.gui_params['text'])
                    label.pack(side=tk.LEFT, anchor=tk.W, padx=5)

                widgets[info.name].pack(expand=False, side=tk.TOP, anchor=tk.W, padx=3, pady=3)

            elif info.gui_params['widget'] == 'Radiobutton':
                # Link a variable to the widget's state
                guivars[info.name] = tk.StringVar(value=info.gui_params['default'])
                # Create the option menu
                widgets[info.name] = tk.LabelFrame(
                        frames[info.gui_params['group']],
                        text=info.gui_params['text'],
                        labelanchor=tk.NW)
                if isinstance(info.gui_params['options'], list):
                    info.gui_params['options'] = dict(zip(
                        info.gui_params['options'],
                        info.gui_params['options']))

                # Set up orientation
                side = tk.TOP
                anchor = tk.W
                if "horizontal" in info.gui_params and info.gui_params["horizontal"]:
                    side = tk.LEFT
                    anchor = tk.N

                for option in info.gui_params["options"]:
                    radio_button = tk.Radiobutton(
                            widgets[info.name],
                            text=option,
                            value=option,
                            variable=guivars[info.name],
                            justify=tk.LEFT,
                            wraplength=190,
                            indicatoron=False,
                            command=show_settings)
                    radio_button.pack(expand=True, side=side, anchor=anchor)

                widgets[info.name].pack(expand=False, side=tk.TOP, anchor=tk.W, padx=3, pady=3)

            elif info.gui_params['widget'] == 'Scale':
                # Link a variable to the widget's state
                guivars[info.name] = tk.IntVar(value=info.gui_params['default'])
                # Create the option menu
                widgets[info.name] = tk.Frame(frames[info.gui_params['group']])
                minval  = 'min'  in info.gui_params and info.gui_params['min']  or 0
                maxval  = 'max'  in info.gui_params and info.gui_params['max']  or 100
                stepval = 'step' in info.gui_params and info.gui_params['step'] or 1
                scale   = tk.Scale(
                        widgets[info.name],
                        variable=guivars[info.name],
                        from_=minval,
                        to=maxval,
                        tickinterval=stepval,
                        resolution=stepval,
                        showvalue=0,
                        orient=tk.HORIZONTAL,
                        sliderlength=15,
                        length=200,
                        command=show_settings)
                scale.pack(side=tk.BOTTOM, anchor=tk.W)

                if 'text' in info.gui_params:
                    label = tk.Label(widgets[info.name], text=info.gui_params['text'])
                    label.pack(side=tk.LEFT, anchor=tk.W, padx=5)

                widgets[info.name].pack(expand=False, side=tk.TOP, anchor=tk.W, padx=3, pady=3)

            elif info.gui_params['widget'] == 'Entry':
                # Link a variable to the widget's state
                guivars[info.name] = tk.StringVar(value=info.gui_params['default'])
                # Create the option menu
                widgets[info.name] = tk.Frame(frames[info.gui_params['group']])

                if 'validate' in info.gui_params:
                    entry = ValidatingEntry(
                            widgets[info.name],
                            command=show_settings,
                            validate=info.gui_params['validate'],
                            textvariable=guivars[info.name],
                            width=30)
                else:
                    entry = tk.Entry(widgets[info.name],
                            textvariable=guivars[info.name],
                            width=30)

                entry.pack(side=tk.BOTTOM, anchor=tk.W)

                if 'text' in info.gui_params:
                    label = tk.Label(widgets[info.name], text=info.gui_params['text'])
                    label.pack(side=tk.LEFT, anchor=tk.W, padx=5)

                widgets[info.name].pack(expand=False, side=tk.TOP, anchor=tk.W, padx=3, pady=3)

            if 'tooltip' in info.gui_params:
                ToolTips.register(widgets[info.name], info.gui_params['tooltip'])


    # Pack the hierarchy

    frames['logic'].pack(               fill=tk.BOTH, expand=True, anchor=tk.N, side=tk.RIGHT,  pady=(5,1))
    frames['open'].pack(                fill=tk.BOTH, expand=True, anchor=tk.W, side=tk.TOP,    pady=(5,1))
    frames['world'].pack(               fill=tk.BOTH, expand=True, anchor=tk.W, side=tk.BOTTOM, pady=(5,1))

    # Logic tab
    frames['rewards'].pack(             fill=tk.BOTH, expand=True, anchor=tk.N, side=tk.LEFT,   pady=(5,1))
    frames['tricks'].pack(              fill=tk.BOTH, expand=True, anchor=tk.N, side=tk.LEFT,   pady=(5,1))

    # Other tab
    frames['convenience'].pack(         fill=tk.BOTH, expand=True, anchor=tk.N, side=tk.LEFT,   pady=(5,1))
    frames['other'].pack(               fill=tk.BOTH, expand=True, anchor=tk.N, side=tk.LEFT,   pady=(5,1))

    # Aesthetics tab
    frames['cosmetics'].pack(           fill=tk.BOTH, expand=True, anchor=tk.W, side=tk.TOP)
    frames['aesthetic_tab_left'].pack(  fill=tk.BOTH, expand=True, anchor=tk.W, side=tk.LEFT)
    frames['aesthetic_tab_right'].pack( fill=tk.BOTH, expand=True, anchor=tk.W, side=tk.RIGHT)

    # Aesthetics tab - Left Side
    frames['tunic_color'].pack(         fill=tk.BOTH, expand=True, anchor=tk.W, side=tk.TOP,    pady=(5,1))
    frames['lowhp'].pack(               fill=tk.BOTH, expand=True, anchor=tk.W, side=tk.TOP,    pady=(5,1))

    # Aesthetics tab - Right Side
    frames['navi_color'].pack(          fill=tk.BOTH, expand=True, anchor=tk.W, side=tk.TOP,    pady=(5,1))
    frames['navihint'].pack(            fill=tk.BOTH, expand=True, anchor=tk.W, side=tk.TOP,    pady=(5,1))

    notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


    # Multi-World
    widgets['multiworld'] = tk.LabelFrame(frames['rom_tab'], text='Multi-World Generation')
    countLabel = tk.Label(widgets['multiworld'], wraplength=350, justify=tk.LEFT, text='This is used for co-op generations. Increasing Player Count will drastically increase the generation time. For more information see:')
    hyperLabel = tk.Label(widgets['multiworld'], wraplength=350, justify=tk.LEFT, text='https://github.com/TestRunnerSRL/bizhawk-co-op', fg='blue', cursor='hand2')
    hyperLabel.bind("<Button-1>", lambda event: webbrowser.open_new(r"https://github.com/TestRunnerSRL/bizhawk-co-op"))
    countLabel.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=0)
    hyperLabel.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=0)

    worldCountFrame = tk.Frame(widgets['multiworld'])
    countLabel = tk.Label(worldCountFrame, text='Player Count')
    guivars['world_count'] = tk.StringVar()
    widgets['world_count'] = tk.Spinbox(worldCountFrame, from_=1, to=31, textvariable=guivars['world_count'], width=3)
    guivars['world_count'].trace('w', show_settings)
    countLabel.pack(side=tk.LEFT)
    widgets['world_count'].pack(side=tk.LEFT, padx=2)
    worldCountFrame.pack(side=tk.LEFT, anchor=tk.N, padx=10, pady=(1,5))

    playerNumFrame = tk.Frame(widgets['multiworld'])
    countLabel = tk.Label(playerNumFrame, text='Player ID')
    guivars['player_num'] = tk.StringVar()
    widgets['player_num'] = tk.Spinbox(playerNumFrame, from_=1, to=31, textvariable=guivars['player_num'], width=3)
    countLabel.pack(side=tk.LEFT)
    widgets['player_num'].pack(side=tk.LEFT, padx=2)
    ToolTips.register(widgets['player_num'], 'Generate for specific Player.')
    playerNumFrame.pack(side=tk.LEFT, anchor=tk.N, padx=10, pady=(1,5))

    widgets['multiworld'].pack(side=tk.TOP, anchor=tk.W, padx=5, pady=(1,1))


    # Settings Presets Functions
    def import_setting_preset():
        if guivars['settings_preset'].get() == '[New Preset]':
            tk.messagebox.showerror("Invalid Preset", "You must select an existing preset!")
            return

        # Get cosmetic settings
        old_settings = guivars_to_settings(guivars)
        new_settings = {setting.name: old_settings.__dict__[setting.name] for setting in
                            filter(lambda s: not (s.shared and s.bitwidth > 0), setting_infos)}

        preset = presets[guivars['settings_preset'].get()]
        new_settings.update(preset)

        settings = Settings(new_settings)
        settings.seed = guivars['seed'].get()

        settings_to_guivars(settings, guivars)
        show_settings()


    def add_settings_preset():
        preset_name = guivars['settings_preset'].get()
        if preset_name == '[New Preset]':
            preset_name = tk.simpledialog.askstring("New Preset", "Enter a new preset name:")
            if not preset_name or preset_name in presets or preset_name == '[New Preset]':
                tk.messagebox.showerror("Invalid Preset", "You must enter a new preset name!")
                return
        elif presets[preset_name].get('locked', False):
            tk.messagebox.showerror("Invalid Preset", "You cannot modify a locked preset!")
            return

        settings = guivars_to_settings(guivars)
        preset = {setting.name: settings.__dict__[setting.name] for setting in
            filter(lambda s: s.shared and s.bitwidth > 0, setting_infos)}

        presets[preset_name] = preset
        guivars['settings_preset'].set(preset_name)
        update_preset_dropdown()


    def remove_setting_preset():
        preset_name = guivars['settings_preset'].get()
        if preset_name == '[New Preset]':
            tk.messagebox.showerror("Invalid Preset", "You must select an existing preset!")
            return
        elif presets[preset_name].get('locked', False):
            tk.messagebox.showerror("Invalid Preset", "You cannot modify a locked preset!")
            return

        confirm = tk.messagebox.askquestion('Remove Setting Preset', 'Are you sure you want to remove the setting preset "%s"?' % preset_name)
        if confirm != 'yes':
            return

        del presets[preset_name]
        guivars['settings_preset'].set('[New Preset]')
        update_preset_dropdown()


    def update_preset_dropdown():
        widgets['settings_preset']['values'] = ['[New Preset]'] + list(presets.keys())


    # Settings Presets
    widgets['settings_presets'] = tk.LabelFrame(frames['rom_tab'], text='Settings Presets')
    countLabel = tk.Label(widgets['settings_presets'], wraplength=350, justify=tk.LEFT, \
            text='Presets are settings that can be saved and loaded from. Loading a preset will overwrite all settings that affect the seed.')
    countLabel.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=0)

    selectPresetFrame = tk.Frame(widgets['settings_presets'])
    guivars['settings_preset'] = tk.StringVar(value='[New Preset]')
    widgets['settings_preset'] = ttk.Combobox(selectPresetFrame, textvariable=guivars['settings_preset'], values=['[New Preset]'], state='readonly', width=35)
    widgets['settings_preset'].pack(side=tk.BOTTOM, anchor=tk.W)
    ToolTips.register(widgets['settings_preset'], 'Select a setting preset to apply.')
    widgets['settings_preset'].pack(side=tk.LEFT, padx=(5, 0))
    selectPresetFrame.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=(1,5))

    buttonPresetFrame = tk.Frame(widgets['settings_presets'])
    importPresetButton = tk.Button(buttonPresetFrame, text='Load Preset', command=import_setting_preset)
    addPresetButton = tk.Button(buttonPresetFrame, text='Save Preset', command=add_settings_preset)
    removePresetButton = tk.Button(buttonPresetFrame, text='Remove Preset', command=remove_setting_preset)
    importPresetButton.pack(side=tk.LEFT, anchor=tk.W, padx=5)
    addPresetButton.pack(side=tk.LEFT, anchor=tk.W, padx=5)
    removePresetButton.pack(side=tk.LEFT, anchor=tk.W, padx=5)
    buttonPresetFrame.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=(1,5))

    widgets['settings_presets'].pack(side=tk.TOP, anchor=tk.W, padx=5, pady=(1,1))


    # Create the generation menu
    def update_generation_type(event=None):
        if generation_notebook.tab(generation_notebook.select())['text'] == 'Generate From Seed':
            notebook.tab(1, state="normal")
            if guivars['logic_rules'].get() == 'Glitchless':
                notebook.tab(2, state="normal")
            else:
                notebook.tab(2, state="disabled")
            notebook.tab(3, state="normal")
            toggle_widget(widgets['world_count'], check_dependency('world_count'))
            toggle_widget(widgets['create_spoiler'], check_dependency('create_spoiler'))
            toggle_widget(widgets['count'], check_dependency('count'))
        else:
            notebook.tab(1, state="disabled")
            notebook.tab(2, state="disabled")
            notebook.tab(3, state="disabled")
            toggle_widget(widgets['world_count'], False)
            toggle_widget(widgets['create_spoiler'], False)
            toggle_widget(widgets['count'], False)



    generation_notebook = ttk.Notebook(mainWindow)
    frames['gen_from_seed'] = ttk.Frame(generation_notebook)
    frames['gen_from_file'] = ttk.Frame(generation_notebook)
    generation_notebook.add(frames['gen_from_seed'], text='Generate From Seed')
    generation_notebook.add(frames['gen_from_file'], text='Generate From File')
    generation_notebook.bind("<<NotebookTabChanged>>", show_settings)

    # From seed tab
    def import_settings(event=None):
        try:
            settings = guivars_to_settings(guivars)
            text = settings_string_var.get().upper()
            settings.seed = guivars['seed'].get()
            settings.update_with_settings_string(text)
            settings_to_guivars(settings, guivars)
            show_settings()
        except Exception as e:
            tk.messagebox.showerror(title="Error", message="Invalid settings string")

    settingsFrame = tk.Frame(frames['gen_from_seed'])
    settings_string_var = tk.StringVar()
    widgets['setting_string'] = tk.Entry(settingsFrame, textvariable=settings_string_var, width=32)

    label = tk.Label(settingsFrame, text="Settings String")
    widgets['import_settings'] = tk.Button(settingsFrame, text='Import Settings String', command=import_settings)
    label.pack(side=tk.LEFT, anchor=tk.W, padx=5)
    widgets['setting_string'].pack(side=tk.LEFT, anchor=tk.W)
    widgets['import_settings'].pack(side=tk.LEFT, anchor=tk.W, padx=5)

    settingsFrame.pack(fill=tk.BOTH, anchor=tk.W, padx=5, pady=(10,0))

    def multiple_run(settings, window):
        orig_seed = settings.seed
        for i in range(settings.count):
            settings.update_seed(orig_seed + '-' + str(i))
            window.update_title("Generating Seed %s...%d/%d" % (settings.seed, i+1, settings.count))
            main(settings, window)

    def generateRom():
        settings = guivars_to_settings(guivars)
        if settings.count:
            BackgroundTaskProgress(mainWindow, "Generating Seed %s..." % settings.seed, multiple_run, settings)
        else:
            BackgroundTaskProgress(mainWindow, "Generating Seed %s..." % settings.seed, main, settings)

    generateSeedFrame = tk.Frame(frames['gen_from_seed'])
    generateButton = tk.Button(generateSeedFrame, text='Generate Patched ROM', command=generateRom)

    seedLabel = tk.Label(generateSeedFrame, text='Seed')
    guivars['seed'] = tk.StringVar()
    widgets['seed'] = tk.Entry(generateSeedFrame, textvariable=guivars['seed'], width=32)
    seedLabel.pack(side=tk.LEFT, padx=(55, 5))
    widgets['seed'].pack(side=tk.LEFT)
    generateButton.pack(side=tk.LEFT, padx=(5, 0))

    generateSeedFrame.pack(side=tk.BOTTOM, anchor=tk.W, padx=5, pady=10)

    # From file tab
    patchDialogFrame = tk.Frame(frames['gen_from_file'])

    patchFileLabel = tk.Label(patchDialogFrame, text='Patch File')
    guivars['patch_file'] = tk.StringVar(value='')
    patchEntry = tk.Entry(patchDialogFrame, textvariable=guivars['patch_file'], width=45)

    def PatchSelect():
        patch_file = tk.filedialog.askopenfilename(filetypes=[("Patch File Archive", "*.zpfz *.zpf"), ("All Files", "*")])
        if patch_file != '':
            guivars['patch_file'].set(patch_file)
    patchSelectButton = tk.Button(patchDialogFrame, text='Select File', command=PatchSelect, width=10)

    patchFileLabel.pack(side=tk.LEFT, padx=(5,0))
    patchEntry.pack(side=tk.LEFT, padx=3)
    patchSelectButton.pack(side=tk.LEFT)

    patchDialogFrame.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=(10,5))

    def generateFromFile():
        settings = guivars_to_settings(guivars)
        BackgroundTaskProgress(mainWindow, "Generating From File %s..." % os.path.basename(settings.patch_file), from_patch_file, settings)

    generateFileButton = tk.Button(frames['gen_from_file'], text='Generate Patched ROM', command=generateFromFile)
    generateFileButton.pack(side=tk.BOTTOM, anchor=tk.E, pady=(0,10), padx=(0, 10))

    generation_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


    guivars['checked_version'] = tk.StringVar()

    if settings is not None:
        # Load values from commandline args
        settings_to_guivars(settings, guivars)
    else:
        # Try to load saved settings
        settingsFile = local_path('settings.sav')
        try:
            with open(settingsFile) as f:
                settings = Settings(json.load(f))
        except:
            settings = Settings({})
        settings.update_seed("")
        settings_to_guivars(settings, guivars)

        presets = {}
        for file in [data_path('presets_default.json')] \
                  + [local_path(f) for f in os.listdir(local_path()) if f.startswith('presets_') and f.endswith('.sav')] \
                  + [local_path('presets.sav')]:
            try:
                with open(file) as f:
                    presets_temp = json.load(f)
                    if file != local_path('presets.sav'):
                        for preset in presets_temp.values():
                            preset['locked'] = True
                    presets.update(presets_temp)
            except:
                pass
        update_preset_dropdown()

    show_settings()

    def gui_check_version():
        task = BackgroundTask(mainWindow, check_version, guivars['checked_version'].get())
        while task.running:
            mainWindow.update()

        if task.status:
            dialog = Dialog(mainWindow, title="Version Error", question=task.status, oktext='Don\'t show again', canceltext='OK')
            if dialog.result:
                guivars['checked_version'].set(ESVersion)

    mainWindow.after(1000, gui_check_version)
    mainWindow.mainloop()

    # Save settings on close
    settings_file = local_path('settings.sav')
    with open(settings_file, 'w') as outfile:
        settings = guivars_to_settings(guivars)
        del settings.__dict__["seed"]
        del settings.__dict__["numeric_seed"]
        del settings.__dict__["check_version"]
        if "locked" in settings.__dict__:
            del settings.__dict__["locked"]
        json.dump(settings.__dict__, outfile, indent=4)

    presets_file = local_path('presets.sav')
    with open(presets_file, 'w') as outfile:
        preset_json = {name: preset for name,preset in presets.items() if not preset.get('locked')}
        json.dump(preset_json, outfile, indent=4)

if __name__ == '__main__':
    guiMain()
