import os
import json

def WeightFiles():
    return [os.path.join(os.path.dirname(__file__), "data/Weights", f) for f in os.listdir(os.path.join(os.path.dirname(__file__), "data/Weights")) if f.endswith(".json")]

def WeightList():
    weights = {}
    for d in WeightFiles():
        with open(d, 'r') as weight_file:
            weight = json.load(weight_file)
        weight_name = weight['name']
        gui_name = weight['gui_name']
        weights.update({ weight_name: gui_name })
    return weights

def WeightTips():
    tips = ""
    first_dist = True
    line_char_limit = 33
    for d in WeightFiles():
        if not first_dist:
            tips = tips + "\n"
        else:
            first_dist = False
        with open(d, 'r') as dist_file:
            dist = json.load(dist_file)
        gui_name = dist['gui_name']
        desc = dist['description']
        i = 0
        end_of_line = False
        tips = tips + "<b>"
        for c in gui_name:
            if c == " " and end_of_line:
                tips = tips + "\n"
                end_of_line = False
            else:
                tips = tips + c
                i = i + 1
                if i > line_char_limit:
                    end_of_line = True
                    i = 0
        tips = tips + "</b>: "
        i = i + 2
        for c in desc:
            if c == " " and end_of_line:
                tips = tips + "\n"
                end_of_line = False
            else:
                tips = tips + c
                i = i + 1
                if i > line_char_limit:
                    end_of_line = True
                    i = 0
        tips = tips + "\n"
    return tips
    