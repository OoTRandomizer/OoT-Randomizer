import os
import sys
import datetime
import json
import random
import RandomSettingsConditionals as conds
from SettingsList import get_settings_from_tab, get_settings_from_section, get_setting_info
from StartingItems import inventory, songs, equipment


def load_weights_file(weights_fname):
    """ Given a weights filename, open it up. If the file does not exist, make it with even weights """
    fpath = os.path.join(os.path.dirname(__file__), "data/Weights",  weights_fname + ".json")
    if os.path.isfile(fpath):
        with open(fpath) as fin:
            datain = json.load(fin)
    else:
        raise Exception("No weights file found at {}".format(fpath))

    weight_options = datain["options"] if "options" in datain else None
    weight_multiselect = datain["multiselect"] if "multiselect" in datain else None
    weight_dict = datain["weights"]

    return weight_options, weight_multiselect, weight_dict


def generate_balanced_weights(fname="default_weights.json"):
    """ Generate a file with even weights for each setting. """
    settings_to_randomize = list(get_settings_from_tab("main_tab"))[1:] + \
                list(get_settings_from_tab("detailed_tab")) + \
                list(get_settings_from_tab("other_tab")) + \
                list(get_settings_from_tab("starting_tab"))

    exclude_from_weights = ["bridge_tokens", "ganon_bosskey_tokens", "bridge_hearts", "ganon_bosskey_hearts",
                            "triforce_goal_per_world", "triforce_count_per_world", "disabled_locations",
                            "allowed_tricks", "starting_equipment", "starting_items", "starting_songs"]
    weight_dict = {}
    for name in settings_to_randomize:
        if name not in exclude_from_weights:
            opts = list(get_setting_info(name).choices.keys())
            optsdict = {o: 100./len(opts) for o in opts}
            weight_dict[name] = optsdict

    if fname is not None:
        with open(fname, 'w') as fp:
            json.dump(weight_dict, fp, indent=4)

    return weight_dict


def geometric_weights(N, startat=0, rtype="list"):
    """ Compute weights according to a geometric distribution """
    if rtype == "list":
        return [50.0/2**i for i in range(N)]
    elif rtype == "dict":
        return {str(startat+i): 50.0/2**i for i in range(N)}


def draw_starting_item_pool(random_settings, start_with):
    """ Select starting items, songs, and equipment. """
    random_settings["starting_items"] = draw_choices_from_pool(inventory)
    random_settings["starting_songs"] = draw_choices_from_pool(songs)
    random_settings["starting_equipment"] = draw_choices_from_pool(equipment)

    for key, val in start_with.items():
        for thing in val:
            if thing not in random_settings[key]:
                random_settings[key] += [thing]


def draw_choices_from_pool(itempool):
    N = random.choices(range(len(itempool)), weights=geometric_weights(len(itempool)))[0]
    return random.sample(list(itempool.keys()), N)


def remove_plando_if_random(random_settings):
    """ For settings that have a _random option, remove the specific plando if _random is true """
    settings_to_check = ["trials", "chicken_count", "big_poe_count"]
    for setting in settings_to_check:
        if random_settings[setting+'_random'] == "true":
            random_settings.pop(setting)


def remove_redundant_settings(random_settings):
    """ Disable settings that the randomizer expects to be disabled.
    The randomizer will reject plandos with disabled settings set to non-default values.
    Settings are considered disabled if they are disabled in the randomizer GUI by another setting.
    """
    settings_list = list(random_settings.keys())
    for setting in settings_list:
        # As we're iterating, the setting may already have been deleted/disabled by a previous setting
        if setting in random_settings.keys():
            info = get_setting_info(setting)
            choice = random_settings[setting]
            if info.disable != None:
                for option, disabling in info.disable.items():
                    negative = False
                    if isinstance(option, str) and option[0] == '!':
                        negative = True
                        option = option[1:]
                    if (choice == option) != negative:
                        for other_setting in disabling.get('settings', []):
                            remove_disabled_setting(random_settings, other_setting)
                        for section in disabling.get('sections', []):
                            for other_setting in get_settings_from_section(section):
                                remove_disabled_setting(random_settings, other_setting)
                        for tab in disabling.get('tabs', []):
                            for other_setting in get_settings_from_tab(tab):
                                remove_disabled_setting(random_settings, other_setting)


def remove_disabled_setting(random_settings, other_setting):
    if other_setting in random_settings.keys():
        random_settings.pop(other_setting)

def resolve_multiselect_weights(setting, options):
    """ Given a multiselect weights block, resolve into the plando options. 
    A multiselect block should contain the following elements in addition to individual weights

    global_enable_percentage [0,100] - the chance at rolling any on in the first place
    geometric [true/false] - If true, ignore individual weights and chose a random number
    to enable according to the geometric distribution
    """
    if random.random()*100 > options["global_enable_percentage"]:
        return []
    
    if "geometric" in options.keys() and options["geometric"]:
        nopts = len(get_setting_info(setting).choices)
        N = random.choices(range(nopts+1), weights=geometric_weights(nopts+1))[0]
        return random.sample(list(get_setting_info(setting).choices.keys()), N)

    # Randomly draw which multiselects should be enabled
    if not "opt_percentage" in options.keys():
        return []
    return [msopt for msopt, perc in options["opt_percentage"].items() if random.random()*100 < perc]


def draw_dungeon_shortcuts(random_settings):
    """ Decide how many dungeon shortcuts to enable and randomly select them """
    N = random.choices(range(8), weights=geometric_weights(8))[0]
    dungeon_shortcuts_opts = ['deku_tree', 'dodongos_cavern', 'jabu_jabus_belly', 'forest_temple', 'fire_temple', 'shadow_temple', 'spirit_temple']
    random_settings["dungeon_shortcuts"] = random.sample(dungeon_shortcuts_opts, N)


def generate_weights_override(override_weights_fname):
    weight_options, weight_multiselect, weight_dict = load_weights_file(override_weights_fname)


    # If an override_weights file name is provided, load it
    start_with = {"starting_items":[], "starting_songs":[], "starting_equipment":[]}
    if override_weights_fname is not None:
        print(f"RSL GENERATOR: LOADING OVERRIDE WEIGHTS from {override_weights_fname}")
        override_options, override_multiselect, override_weights = load_weights_file(override_weights_fname)
        # Check for starting items, songs and equipment
        for key in start_with.keys():
            if key in override_weights.keys():
                start_with[key] = override_weights[key]
                override_weights.pop(key)

        # Replace the options
        if override_options is not None:
            for key, value in override_options.items():
                # Handling overwrite
                if not (key.startswith("extra_") or key.startswith("remove_")):
                    weight_options[key] = value
                    continue

                # Handling extras
                if key.startswith("extra_"):
                    option = key.split("extra_")[1]
                    if option not in weight_options:
                        weight_options[option] = value
                    else: # Both existing options and extra options
                        if isinstance(weight_options[option], dict):
                            weight_options[option].update(value)
                        else:
                            weight_options[option] += value
                            weight_options[option] = list(set(weight_options[option]))

                # Handling removes
                if key.startswith("remove_"):
                    option = key.split("remove_")[1]
                    if option in weight_options:
                        for item in value:
                            if item in weight_options[option]:
                                weight_options[option].remove(item)

        # Replace the weights
        for key, value in override_weights.items():
            weight_dict[key] = value

        # Replace the multiselects
        if override_multiselect is not None:
            for key, value in override_multiselect.items():
                weight_multiselect[key] = value
    
    return weight_options, weight_multiselect, weight_dict, start_with


def generate_plando(override_weights_fname):
    weight_options, weight_multiselect, weight_dict, start_with = generate_weights_override(override_weights_fname)

    ####################################################################################
    # Make a new function that parses the weights file that does this stuff
    ####################################################################################
    # Generate even weights for tokens, hearts, and triforce pieces given the max value (Maybe put this into the step that loads the weights)
    for nset in ["bridge_tokens", "ganon_bosskey_tokens", "bridge_hearts", "ganon_bosskey_hearts", "triforce_goal_per_world", "triforce_count_per_world"]:
        kwx = nset + "_max"
        kwn = nset + "_min"
        nmax = weight_options[kwx] if kwx in weight_options else 100
        nmin = weight_options[kwn] if kwn in weight_options else 1
        weight_dict[nset] = {i: 100./(nmax - nmin + 1) for i in range(nmin, nmax + 1)}
        if kwx in weight_dict:
            weight_dict.pop(kwx)
        if kwn in weight_dict:
            weight_dict.pop(kwn)
    ####################################################################################

    # Draw the random settings
    random_settings = {}
    for setting, options in weight_dict.items():
        random_settings[setting] = random.choices(list(options.keys()), weights=list(options.values()))[0]

    # Draw the multiselects
    if weight_multiselect is not None:
        for setting, options in weight_multiselect.items():
            random_settings[setting] = resolve_multiselect_weights(setting, options)

    # Add starting items, conditionals, tricks and excluded locations
    if weight_options is not None:
        if "conditionals" in weight_options:
            conds.parse_conditionals(weight_options["conditionals"], weight_dict, random_settings, start_with)
        if "tricks" in weight_options:
            random_settings["allowed_tricks"] = weight_options["tricks"]
        if "disabled_locations" in weight_options:
            random_settings["disabled_locations"] = weight_options["disabled_locations"]
        if "starting_items" in weight_options and weight_options["starting_items"] == True:
            draw_starting_item_pool(random_settings, start_with)
        
    # Remove plando setting if a _random setting is true
    remove_plando_if_random(random_settings)

    # Format numbers and bools to not be strings
    for setting, value in random_settings.items():
        setting_type = get_setting_info(setting).type
        if setting_type is bool:
            if value == "true":
                value = True
            elif value == "false":
                value = False
            else:
                raise TypeError(f'Value for setting {setting!r} must be "true" or "false"')
        elif setting_type is int:
            value = int(value)
        elif setting_type is not str and setting not in ["allowed_tricks", "disabled_locations", "starting_items", "starting_songs", "starting_equipment", "hint_dist_user", "dungeon_shortcuts"] + list(weight_multiselect.keys()):
            raise NotImplementedError(f'{setting} has an unsupported setting type: {setting_type!r}')
        random_settings[setting] = value

    # Remove conflicting "dead" settings since rando won't ignore them anymore
    remove_redundant_settings(random_settings)

    # Add the RSL Script version to the plando
    random_settings['user_message'] = f'RSL Script embedded in OoT Randomizer Generator'

    # Save the output plando
    output = { "settings": random_settings }

    return output