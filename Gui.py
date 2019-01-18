#!/usr/bin/env python3
from argparse import Namespace
from glob import glob
import json
import random
import re
import os
import shutil
from tkinter import Scale, Checkbutton, OptionMenu, Toplevel, LabelFrame, \
        Radiobutton, PhotoImage, Tk, BOTH, LEFT, RIGHT, BOTTOM, TOP, \
        StringVar, IntVar, Frame, Label, W, E, X, N, S, NW, Entry, Spinbox, \
        Button, filedialog, messagebox, simpledialog, ttk, HORIZONTAL, Toplevel, \
        colorchooser, Listbox, ACTIVE, END, Scrollbar, VERTICAL, Y
from urllib.parse import urlparse
from urllib.request import urlopen

from GuiUtils import ToolTips, set_icon, BackgroundTask, BackgroundTaskProgress, Dialog, ValidatingEntry, SearchBox
from Main import main, from_patch_file
from Utils import is_bundled, local_path, data_path, default_output_path, open_file, check_version, check_python_version
from Settings import Settings
from SettingsList import setting_infos
from version import __version__ as ESVersion
import webbrowser
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
            guivar.set( int(value) )
        # Dropdown/radiobox
        if info.type == str:
            if value is None:
                guivar.set( "" )
            else:
                if info.gui_params and 'options' in info.gui_params:
                    if 'Custom Color' in info.gui_params['options'] and re.match(r'^[A-Fa-f0-9]{6}$', value):
                        guivar.set('Custom (#' + value + ')')
                    else:
                        for gui_text,gui_value in info.gui_params['options'].items():
                            if gui_value == value:
                                guivar.set( gui_text )
                else:
                    guivar.set( value )
        # Text field for a number...
        if info.type == int:
            if value is None:
                guivar.set( str(1) )
            else:
                guivar.set( str(value) )
        if info.type == list:
            guivars[name] = []
            if value:
                for item in value:
                    if info.gui_params and 'options' in info.gui_params:
                        for gui_text,gui_value in info.gui_params['options'].items():
                            if gui_value == item:
                                guivars[name].append(gui_text)
                    else:
                        guivars[name].append(item)


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
                result[name] = int( guivar.get() )
            except ValueError:
                result[name] = 0
        if info.type == list:
            result[name] = []
            for item in guivar:
                if info.gui_params and 'options' in info.gui_params:
                    result[name].append(info.gui_params['options'][item])
                else:
                    result[name].append(item)

    if result['seed'] == "":
        result['seed'] = None
    if result['count'] == 1:
        result['count'] = None

    return Settings(result)


def guiMain(settings=None):
    frames = {}

    mainWindow = Tk()
    mainWindow.wm_title("OoT Randomizer %s" % ESVersion)
    mainWindow.resizable(False, False)

    set_icon(mainWindow)

    notebook = ttk.Notebook(mainWindow)
    frames['rom_tab'] = ttk.Frame(notebook)
    frames['rules_tab'] = ttk.Frame(notebook)
    frames['logic_tab'] = ttk.Frame(notebook)
    frames['other_tab'] = ttk.Frame(notebook)
    frames['cosmetic_tab'] = ttk.Frame(notebook)
    frames['SFX_tab'] = ttk.Frame(notebook)
    frames['cosmetic_tab_left'] = Frame(frames['cosmetic_tab'])
    frames['cosmetic_tab_right'] = Frame(frames['cosmetic_tab'])
    notebook.add(frames['rom_tab'], text='ROM Options')
    notebook.add(frames['rules_tab'], text='Main Rules')
    notebook.add(frames['logic_tab'], text='Detailed Logic')
    notebook.add(frames['other_tab'], text='Other')
    notebook.add(frames['cosmetic_tab'], text='Cosmetic')
    notebook.add(frames['SFX_tab'], text='SFX')

    #######################
    # Randomizer controls #
    #######################

    # Hold the results of the user's decisions here
    guivars = {}
    widgets = {}
    presets = {}

    # Hierarchy
    ############

    #Rules Tab
    frames['open']        = LabelFrame(frames['rules_tab'],          text='Open',              labelanchor=NW)
    frames['world']       = LabelFrame(frames['rules_tab'],          text='World',             labelanchor=NW)
    frames['shuffle']     = LabelFrame(frames['rules_tab'],          text='Shuffle',           labelanchor=NW)

    # Logic tab
    frames['checks']      = LabelFrame(frames['logic_tab'],          text='Adult Trade Sequence', labelanchor=NW)
    frames['tricks']      = LabelFrame(frames['logic_tab'],          text='Lens of Truth',     labelanchor=NW)

    #Other Tab
    frames['convenience'] = LabelFrame(frames['other_tab'],          text='Timesavers',        labelanchor=NW)
    frames['other']       = LabelFrame(frames['other_tab'],          text='Misc',              labelanchor=NW)

    #Cosmetic tab
    frames['cosmetic']    = LabelFrame(frames['cosmetic_tab_left'],  text='General',           labelanchor=NW)
    frames['sword_trails']= LabelFrame(frames['cosmetic_tab_left'],  text='Sword Trail Colors',labelanchor=NW)
    frames['gauntlet_colors']= LabelFrame(frames['cosmetic_tab_left'], text='Gauntlet Colors', labelanchor=NW)
    frames['tunic_colors']= LabelFrame(frames['cosmetic_tab_right'], text='Tunics',            labelanchor=NW)
    frames['navi_colors'] = LabelFrame(frames['cosmetic_tab_right'], text='Navi Colors',       labelanchor=NW)

    #Cosmetic tab
    frames['sfx']         = LabelFrame(frames['SFX_tab'],            text='General',           labelanchor=NW)
    frames['menu_sfx']    = LabelFrame(frames['SFX_tab'],            text='Menu',              labelanchor=NW)
    frames['npc_sfx']     = LabelFrame(frames['SFX_tab'],            text='NPC',               labelanchor=NW)


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

    def show_settings(*event):
        settings = guivars_to_settings(guivars)
        settings_string_var.set( settings.get_settings_string() )

        # Update any dependencies
        for info in setting_infos:
            dep_met = settings.check_dependency(info.name)

            if info.name in widgets:
                toggle_widget(widgets[info.name], dep_met)

            if info.type == list:
                widgets[info.name].delete(0, END)
                widgets[info.name].insert(0, *guivars[info.name])

            if info.type != list and info.name in guivars and guivars[info.name].get() == 'Custom Color':
                color = colorchooser.askcolor()
                if color == (None, None):
                    color = ((0,0,0),'#000000')
                guivars[info.name].set('Custom (' + color[1] + ')')
        update_generation_type()


    versionCheckFrame = Frame(frames['rom_tab'])
    versionCheckFrame.pack(side=BOTTOM, anchor=NW, fill=X)

    fileDialogFrame = Frame(frames['rom_tab'])

    romDialogFrame = Frame(fileDialogFrame)
    baseRomLabel = Label(romDialogFrame, text='Base ROM')
    guivars['rom'] = StringVar(value='')
    romEntry = Entry(romDialogFrame, textvariable=guivars['rom'], width=46)

    def RomSelect():
        rom = filedialog.askopenfilename(filetypes=[("ROM Files", (".z64", ".n64")), ("All Files", "*")])
        if rom != '':
            guivars['rom'].set(rom)
    romSelectButton = Button(romDialogFrame, text='Browse', command=RomSelect, width=10)

    baseRomLabel.pack(side=LEFT, padx=(40,0))
    romEntry.pack(side=LEFT, padx=3)
    romSelectButton.pack(side=LEFT)

    romDialogFrame.pack()

    fileDialogFrame.pack(side=TOP, anchor=W, padx=5, pady=(5,1))

    def output_dir_select():
        rom = filedialog.askdirectory(initialdir = default_output_path(guivars['output_dir'].get()))
        if rom != '':
            guivars['output_dir'].set(rom)

    outputDialogFrame = Frame(frames['rom_tab'])
    outputDirLabel = Label(outputDialogFrame, text='Output Directory')
    guivars['output_dir'] = StringVar(value='')
    outputDirEntry = Entry(outputDialogFrame, textvariable=guivars['output_dir'], width=46)
    outputDirButton = Button(outputDialogFrame, text='Browse', command=output_dir_select, width=10)
    outputDirLabel.pack(side=LEFT, padx=(3,0))
    outputDirEntry.pack(side=LEFT, padx=3)
    outputDirButton.pack(side=LEFT)
    outputDialogFrame.pack(side=TOP, anchor=W, pady=3)

    countDialogFrame = Frame(frames['rom_tab'])
    countLabel = Label(countDialogFrame, text='Generation Count')
    guivars['count'] = StringVar()
    widgets['count'] = Spinbox(countDialogFrame, from_=1, to=100, textvariable=guivars['count'], width=3)

    if os.path.exists(local_path('README.html')):
        def open_readme():
            open_file(local_path('README.html'))
        openReadmeButton = Button(countDialogFrame, text='Open Documentation', command=open_readme)
        openReadmeButton.pack(side=RIGHT, padx=5)

    countLabel.pack(side=LEFT)
    widgets['count'].pack(side=LEFT, padx=2)
    countDialogFrame.pack(side=TOP, anchor=W, padx=5, pady=(1,1))

    # Build gui
    ############

    for info in setting_infos:
        if info.gui_params and 'group' in info.gui_params:
            if info.gui_params['widget'] == 'Checkbutton':
                # Determine the initial value of the checkbox
                default_value = 1 if info.gui_params['default'] == "checked" else 0
                # Create a variable to access the box's state
                guivars[info.name] = IntVar(value=default_value)
                # Create the checkbox
                widgets[info.name] = Checkbutton(frames[info.gui_params['group']], text=info.gui_params['text'], variable=guivars[info.name], justify=LEFT, wraplength=220, command=show_settings)
                widgets[info.name].pack(expand=False, anchor=W)
            elif info.gui_params['widget'] == 'Combobox':
                # Create the variable to store the user's decision
                guivars[info.name] = StringVar(value=info.gui_params['default'])
                # Create the option menu
                widgets[info.name] = Frame(frames[info.gui_params['group']])
                if isinstance(info.gui_params['options'], list):
                    info.gui_params['options'] = dict(zip(info.gui_params['options'], info.gui_params['options']))
                dropdown = ttk.Combobox(widgets[info.name], textvariable=guivars[info.name], values=list(info.gui_params['options'].keys()), state='readonly', width=36)
                dropdown.bind("<<ComboboxSelected>>", show_settings)
                dropdown.pack(side=BOTTOM, anchor=W)
                # Label the option
                if 'text' in info.gui_params:
                    label = Label(widgets[info.name], text=info.gui_params['text'])
                    label.pack(side=LEFT, anchor=W, padx=5)
                # Pack the frame
                widgets[info.name].pack(expand=False, side=TOP, anchor=W, padx=3, pady=3)
            elif info.gui_params['widget'] == 'Radiobutton':
                # Create the variable to store the user's decision
                guivars[info.name] = StringVar(value=info.gui_params['default'])
                # Create the option menu
                widgets[info.name] = LabelFrame(frames[info.gui_params['group']], text=info.gui_params['text'] if 'text' in info.gui_params else info["name"], labelanchor=NW)
                if isinstance(info.gui_params['options'], list):
                    info.gui_params['options'] = dict(zip(info.gui_params['options'], info.gui_params['options']))
                # Setup orientation
                side = TOP
                anchor = W
                if "horizontal" in info.gui_params and info.gui_params["horizontal"]:
                    side = LEFT
                    anchor = N
                # Add the radio buttons
                for option in info.gui_params["options"]:
                    radio_button = Radiobutton(widgets[info.name], text=option, value=option, variable=guivars[info.name], justify=LEFT, wraplength=220, indicatoron=False, command=show_settings)
                    radio_button.pack(expand=True, side=side, anchor=anchor)
                # Pack the frame
                widgets[info.name].pack(expand=False, side=TOP, anchor=W, padx=3, pady=3)
            elif info.gui_params['widget'] == 'Scale':
                # Create the variable to store the user's decision
                guivars[info.name] = IntVar(value=info.gui_params['default'])
                # Create the option menu
                widgets[info.name] = Frame(frames[info.gui_params['group']])
                minval = 'min' in info.gui_params and info.gui_params['min'] or 0
                maxval = 'max' in info.gui_params and info.gui_params['max'] or 100
                stepval = 'step' in info.gui_params and info.gui_params['step'] or 1
                scale = Scale(widgets[info.name], variable=guivars[info.name], from_=minval, to=maxval, tickinterval=stepval, resolution=stepval, showvalue=0, orient=HORIZONTAL, sliderlength=15, length=235, command=show_settings)
                scale.pack(side=BOTTOM, anchor=W)
                # Label the option
                if 'text' in info.gui_params:
                    label = Label(widgets[info.name], text=info.gui_params['text'])
                    label.pack(side=LEFT, anchor=W, padx=5)
                # Pack the frame
                widgets[info.name].pack(expand=False, side=TOP, anchor=W, padx=3, pady=3)
            elif info.gui_params['widget'] == 'Entry':
                # Create the variable to store the user's decision
                guivars[info.name] = StringVar(value=info.gui_params['default'])
                # Create the option menu
                widgets[info.name] = Frame(frames[info.gui_params['group']])

                if 'validate' in info.gui_params:
                    entry = ValidatingEntry(widgets[info.name], command=show_settings, validate=info.gui_params['validate'], textvariable=guivars[info.name], width=35)
                else:
                    entry = Entry(widgets[info.name], textvariable=guivars[info.name], width=36)
                entry.pack(side=BOTTOM, anchor=W)
                # Label the option
                if 'text' in info.gui_params:
                    label = Label(widgets[info.name], text=info.gui_params['text'])
                    label.pack(side=LEFT, anchor=W, padx=5)
                # Pack the frame
                widgets[info.name].pack(expand=False, side=TOP, anchor=W, padx=3, pady=3)
            elif info.gui_params['widget'] == 'SearchBox':
                search_frame = LabelFrame(frames[info.gui_params['group']], text=info.gui_params['text'] if 'text' in info.gui_params else info["name"], labelanchor=NW)
                if isinstance(info.gui_params['options'], list):
                    info.gui_params['options'] = dict(zip(info.gui_params['options'], info.gui_params['options']))

                widgets[info.name + '_entry'] = SearchBox(search_frame, list(info.gui_params['options'].keys()), width=78)
                widgets[info.name + '_entry'].pack(expand=False, side=TOP, anchor=W, padx=3, pady=3)

                list_frame = Frame(search_frame)
                scrollbar = Scrollbar(list_frame, orient=VERTICAL)
                widgets[info.name] = Listbox(list_frame, width=78, height=7, yscrollcommand=scrollbar.set)
                guivars[info.name] = []
                scrollbar.config(command=widgets[info.name].yview)
                scrollbar.pack(side=RIGHT, fill=Y)
                widgets[info.name].pack(side=LEFT)
                list_frame.pack(expand=False, side=TOP, anchor=W, padx=3, pady=3)

                if 'entry_tooltip' in info.gui_params:
                    ToolTips.register(widgets[info.name + '_entry'], info.gui_params['entry_tooltip'])
                if 'list_tooltip' in info.gui_params:
                    ToolTips.register(widgets[info.name], info.gui_params['list_tooltip'])

                def get_lambda(function, *args):
                    return lambda: function(*args)

                def add_list_selected(name):
                    new_location = widgets[name +'_entry'].get()
                    if new_location in widgets[name +'_entry'].options and new_location not in widgets[name].get(0, END):
                        widgets[name].insert(END, new_location)
                        guivars[name].append(new_location)
                    show_settings()

                def remove_list_selected(name):
                    location = widgets[name].get(ACTIVE)
                    widgets[name].delete(ACTIVE)
                    guivars[name].remove(location)
                    show_settings()

                def add_list_all(name):
                    widgets[name].delete(0, END)
                    widgets[name].insert(0, *widgets[name +'_entry'].options)
                    guivars[name] = list(widgets[name +'_entry'].options)
                    show_settings()

                def remove_list_all(name):
                    widgets[name].delete(0, END)
                    guivars[name] = []
                    show_settings()

                list_button_frame = Frame(search_frame)
                list_add = Button(list_button_frame, width=10, text='Add', command=get_lambda(add_list_selected, info.name))
                list_add.pack(side=LEFT, anchor=N, padx=3, pady=3)
                list_remove = Button(list_button_frame, width=10, text='Remove', command=get_lambda(remove_list_selected, info.name))
                list_remove.pack(side=LEFT, anchor=N, padx=3, pady=3)

                list_add = Button(list_button_frame, width=10, text='All', command=get_lambda(add_list_all, info.name))
                list_add.pack(side=LEFT, anchor=N, padx=3, pady=3)
                list_remove = Button(list_button_frame, width=10, text='None', command=get_lambda(remove_list_all, info.name))
                list_remove.pack(side=LEFT, anchor=N, padx=3, pady=3)

                list_button_frame.pack(expand=False, side=TOP, padx=3, pady=3)

                # pack the frame
                search_frame.pack(expand=False, side=TOP, anchor=W, padx=3, pady=3)


            if 'tooltip' in info.gui_params:
                ToolTips.register(widgets[info.name], info.gui_params['tooltip'])


    # Pack the hierarchy
    frames['shuffle'].pack(fill=BOTH,  expand=True, anchor=N, side=RIGHT,  pady=(5,1))
    frames['open'].pack(   fill=BOTH,  expand=True, anchor=W, side=TOP,    pady=(5,1))
    frames['world'].pack(  fill=BOTH,  expand=True, anchor=W, side=BOTTOM, pady=(5,1))

    # Logic tab
    frames['checks'].pack(fill=BOTH, expand=True, anchor=N, side=LEFT, pady=(5,1))
    frames['tricks'].pack(fill=BOTH, expand=True, anchor=N, side=LEFT, pady=(5,1))

    # Other Tab
    frames['convenience'].pack(fill=BOTH, expand=True, anchor=N, side=LEFT, pady=(5,1))
    frames['other'].pack(      fill=BOTH, expand=True, anchor=N, side=LEFT, pady=(5,1))

    # Cosmetics tab
    frames['cosmetic'].pack(          fill=BOTH, expand=True, anchor=W, side=TOP)
    frames['cosmetic_tab_left'].pack( fill=BOTH, expand=True, anchor=W, side=LEFT)
    frames['cosmetic_tab_right'].pack(fill=BOTH, expand=True, anchor=W, side=RIGHT)

    # Cosmetics tab - Left Side
    frames['sword_trails'].pack(fill=BOTH, expand=True, anchor=W, side=TOP, pady=(5,1))
    frames['gauntlet_colors'].pack(fill=BOTH, expand=True, anchor=W, side=BOTTOM, pady=(5,1))

    # Cosmetics tab - Right Side
    frames['tunic_colors'].pack(fill=BOTH, expand=True, anchor=N, side=TOP)
    frames['navi_colors'].pack(fill=BOTH, expand=True, anchor=W, side=TOP, pady=(5,1))

    #SFX tab
    frames['sfx'].pack(          fill=BOTH, expand=True, anchor=N, side=LEFT, pady=(5,1))
    frames['menu_sfx'].pack( fill=BOTH, expand=False, anchor=W, side=TOP, pady=(5,1))
    frames['npc_sfx'].pack(fill=BOTH, expand=True, anchor=W, side=BOTTOM, pady=(5,1))

    notebook.pack(fill=BOTH, expand=True, padx=5, pady=5)


    #Multi-World
    widgets['multiworld'] = LabelFrame(frames['rom_tab'], text='Multi-World Generation')
    countLabel = Label(
            widgets['multiworld'],
            wraplength=250,
            justify=LEFT,
            text='''This is used for co-op generations. \
                    Increasing Player Count will drastically \
                    increase the generation time. \
                    \nFor more information, see: \
                 '''
            )
    hyperLabel = Label(widgets['multiworld'], wraplength=250, justify=LEFT, text='https://github.com/TestRunnerSRL/\nbizhawk-co-op\n', fg='blue', cursor='hand2')
    hyperLabel.bind("<Button-1>", lambda event: webbrowser.open_new(r"https://github.com/TestRunnerSRL/bizhawk-co-op"))
    countLabel.pack(side=TOP, anchor=W, padx=5, pady=0)
    hyperLabel.pack(side=TOP, anchor=W, padx=5, pady=0)

    worldCountFrame = Frame(widgets['multiworld'])
    countLabel = Label(worldCountFrame, text='Player Count')
    guivars['world_count'] = StringVar()
    widgets['world_count'] = Spinbox(worldCountFrame, from_=1, to=255, textvariable=guivars['world_count'], width=3)
    guivars['world_count'].trace('w', show_settings)
    countLabel.pack(side=LEFT)
    widgets['world_count'].pack(side=LEFT, padx=2)
    worldCountFrame.pack(side=LEFT, anchor=N, padx=10, pady=(1,5))

    playerNumFrame = Frame(widgets['multiworld'])
    countLabel = Label(playerNumFrame, text='Player ID')
    guivars['player_num'] = StringVar()
    widgets['player_num'] = Spinbox(playerNumFrame, from_=1, to=255, textvariable=guivars['player_num'], width=3)
    countLabel.pack(side=LEFT)
    widgets['player_num'].pack(side=LEFT, padx=2)
    ToolTips.register(widgets['player_num'], 'Generate for specific Player.')
    playerNumFrame.pack(side=LEFT, anchor=N, padx=10, pady=(1,5))

    widgets['multiworld'].pack(side=LEFT, fill=BOTH, anchor=NW, padx=5, pady=5)


    # Settings Presets Functions
    def import_setting_preset():
        if guivars['settings_preset'].get() == '[New Preset]':
            messagebox.showerror("Invalid Preset", "You must select an existing preset!")
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
            preset_name = simpledialog.askstring("New Preset", "Enter a new preset name:")
            if not preset_name or preset_name in presets or preset_name == '[New Preset]':
                messagebox.showerror("Invalid Preset", "You must enter a new preset name!")
                return
        elif presets[preset_name].get('locked', False):
            messagebox.showerror("Invalid Preset", "You cannot modify a locked preset!")
            return
        else:
            if messagebox.askquestion("Overwrite Preset", 'Are you sure you want to overwrite the "%s" preset?' % preset_name) != 'yes':
                return

        settings = guivars_to_settings(guivars)
        preset = {setting.name: settings.__dict__[setting.name] for setting in
            filter(lambda s: s.shared and s.bitwidth > 0, setting_infos)}

        presets[preset_name] = preset
        guivars['settings_preset'].set(preset_name)
        update_preset_dropdown()
        save_presets()


    def remove_setting_preset():
        preset_name = guivars['settings_preset'].get()
        if preset_name == '[New Preset]':
            messagebox.showerror("Invalid Preset", "You must select an existing preset!")
            return
        elif presets[preset_name].get('locked', False):
            messagebox.showerror("Invalid Preset", "You cannot modify a locked preset!")
            return

        confirm = messagebox.askquestion('Remove Setting Preset', 'Are you sure you want to remove the setting preset "%s"?' % preset_name)
        if confirm != 'yes':
            return

        del presets[preset_name]
        guivars['settings_preset'].set('[New Preset]')
        update_preset_dropdown()
        save_presets()


    def update_preset_dropdown():
        widgets['settings_preset']['values'] = ['[New Preset]'] + list(presets.keys())


    def save_presets():
        presets_file = local_path('presets.sav')
        with open(presets_file, 'w') as outfile:
            preset_json = {name: preset for name,preset in presets.items() if not preset.get('locked')}
            json.dump(preset_json, outfile, indent=4)


    # Settings Presets
    widgets['settings_presets'] = LabelFrame(frames['rom_tab'], text='Settings Presets')
    countLabel = Label(
            widgets['settings_presets'],
            wraplength=250,
            justify=LEFT,
            text='''Presets are settings that can be saved\
                    and loaded from. Loading a preset\
                    will overwrite all settings that affect\
                    the seed.\
                    \n\
                 '''
            )
    countLabel.pack(side=TOP, anchor=W, padx=5, pady=0)

    selectPresetFrame = Frame(widgets['settings_presets'])
    guivars['settings_preset'] = StringVar(value='[New Preset]')
    widgets['settings_preset'] = ttk.Combobox(selectPresetFrame, textvariable=guivars['settings_preset'], values=['[New Preset]'], state='readonly', width=33)
    widgets['settings_preset'].pack(side=BOTTOM, anchor=W)
    ToolTips.register(widgets['settings_preset'], 'Select a setting preset to apply.')
    widgets['settings_preset'].pack(side=LEFT, padx=(5, 0))
    selectPresetFrame.pack(side=TOP, anchor=W, padx=5, pady=(1,5))

    buttonPresetFrame = Frame(widgets['settings_presets'])
    importPresetButton = Button(buttonPresetFrame, text='Load', width=9, command=import_setting_preset)
    addPresetButton = Button(buttonPresetFrame, text='Save', width=9, command=add_settings_preset)
    removePresetButton = Button(buttonPresetFrame, text='Remove', width=9, command=remove_setting_preset)
    importPresetButton.pack(side=LEFT, anchor=W, padx=2)
    addPresetButton.pack(side=LEFT, anchor=W, padx=2)
    removePresetButton.pack(side=LEFT, anchor=W, padx=2)
    buttonPresetFrame.pack(side=TOP, anchor=W, padx=5, pady=(1,5))

    widgets['settings_presets'].pack(side=RIGHT, fill=BOTH, anchor=NW, padx=5, pady=5)


    # Create the generation menu
    def update_generation_type(event=None):
        if generation_notebook.tab(generation_notebook.select())['text'] == 'Generate From Seed':
            notebook.tab(1, state="normal")
            if guivars['logic_rules'].get() == 'Glitchless':
                notebook.tab(2, state="normal")
            else:
                notebook.tab(2, state="disabled")
            notebook.tab(3, state="normal")

            settings = guivars_to_settings(guivars)
            toggle_widget(widgets['world_count'], settings.check_dependency('world_count'))
            toggle_widget(widgets['create_spoiler'], settings.check_dependency('create_spoiler'))
            toggle_widget(widgets['count'], settings.check_dependency('count'))
            toggle_widget(widgets['settings_presets'], True)
        else:
            notebook.tab(1, state="disabled")
            notebook.tab(2, state="disabled")
            notebook.tab(3, state="disabled")
            toggle_widget(widgets['world_count'], False)
            toggle_widget(widgets['create_spoiler'], False)
            toggle_widget(widgets['count'], False)
            toggle_widget(widgets['settings_presets'], False)



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
            messagebox.showerror(title="Error", message="Invalid settings string")

    def copy_settings(event=None):
        mainWindow.clipboard_clear()
        new_clip = settings_string_var.get().upper()
        mainWindow.clipboard_append(new_clip)
        mainWindow.update()

    settingsFrame = Frame(frames['gen_from_seed'])
    settings_string_var = StringVar()
    widgets['setting_string'] = Entry(settingsFrame, textvariable=settings_string_var, width=44)

    label = Label(settingsFrame, text="Settings String", width=13, anchor=E)
    widgets['copy_settings'] = Button(settingsFrame, text='Copy', width=5, command=copy_settings)
    widgets['import_settings'] = Button(settingsFrame, text='Import', width=7, command=import_settings)
    label.pack(side=LEFT, anchor=W, padx=5)
    widgets['setting_string'].pack(side=LEFT, anchor=W)
    widgets['copy_settings'].pack(side=LEFT, anchor=W, padx=(5, 0))
    widgets['import_settings'].pack(side=LEFT, anchor=W)

    settingsFrame.pack(fill=BOTH, anchor=W, padx=5, pady=(10,0))

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

    generateSeedFrame = Frame(frames['gen_from_seed'])
    seedLabel = Label(generateSeedFrame, text='Seed', width=13, anchor=E)
    generateButton = Button(generateSeedFrame, text='Generate!', width=14, command=generateRom)
    guivars['seed'] = StringVar()
    widgets['seed'] = Entry(generateSeedFrame, textvariable=guivars['seed'], width=44)
    seedLabel.pack(side=LEFT, padx=5)
    widgets['seed'].pack(side=LEFT)
    generateButton.pack(side=LEFT, padx=(5, 0))

    generateSeedFrame.pack(side=BOTTOM, anchor=W, padx=5, pady=10)

    # From file tab
    patchDialogFrame = Frame(frames['gen_from_file'])

    patchFileLabel = Label(patchDialogFrame, text='Patch File')
    guivars['patch_file'] = StringVar(value='')
    patchEntry = Entry(patchDialogFrame, textvariable=guivars['patch_file'], width=45)

    def PatchSelect():
        patch_file = filedialog.askopenfilename(filetypes=[("Patch File Archive", "*.zpfz *.zpf"), ("All Files", "*")])
        if patch_file != '':
            guivars['patch_file'].set(patch_file)
    patchSelectButton = Button(patchDialogFrame, text='Select File', command=PatchSelect, width=10)

    patchFileLabel.pack(side=LEFT, padx=(5,0))
    patchEntry.pack(side=LEFT, padx=3)
    patchSelectButton.pack(side=LEFT)

    patchDialogFrame.pack(side=TOP, anchor=W, padx=5, pady=(10,5))

    def generateFromFile():
        settings = guivars_to_settings(guivars)
        BackgroundTaskProgress(mainWindow, "Generating From File %s..." % os.path.basename(settings.patch_file), from_patch_file, settings)

    generateFileButton = Button(frames['gen_from_file'], text='Generate Patched ROM', command=generateFromFile)
    generateFileButton.pack(side=BOTTOM, anchor=E, pady=(0,10), padx=(0, 10))

    generation_notebook.pack(fill=BOTH, expand=True, padx=5, pady=5)


    guivars['checked_version'] = StringVar()
    guivars['cosmetics_only'] = IntVar()

    if settings is not None:
        # Load values from commandline args
        settings_to_guivars(settings, guivars)
    else:
        # Try to load saved settings
        settingsFile = local_path('settings.sav')
        try:
            with open(settingsFile) as f:
                settings = Settings( json.load(f) )
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
            versionCheckLabel = LabelFrame(versionCheckFrame, text="New Version Available!")
            versionCheckText = Label(versionCheckLabel, justify=LEFT, text=task.status[(task.status.find(' ')+1):])
            versionCheckLink = Label(versionCheckLabel, justify=LEFT, text='Click here and download the current version.', fg='blue', cursor='hand2')
            versionCheckLink.bind("<Button-1>", lambda event: webbrowser.open_new(r"https://github.com/TestRunnerSRL/OoT-Randomizer/tree/Dev"))
            versionCheckText.pack(anchor=NW, padx=5, pady=0)
            versionCheckLink.pack(anchor=NW, padx=5, pady=0)
            versionCheckLabel.pack(anchor=NW, fill=X, expand="yes", padx=5, pady=5)

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
    
    save_presets()


if __name__ == '__main__':
    try:
        check_python_version()
    except Exception as ex:
        messagebox.showerror(title="Unsupported Python Version", message=str(ex))
        exit()
    guiMain()

