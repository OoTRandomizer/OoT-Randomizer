from __future__ import annotations
import math
import operator
from typing import Optional, Any

from Utils import powerset


# holds the info for a single setting
class SettingInfo:
    def __init__(self, setting_type: type, gui_text: Optional[str], gui_type: Optional[str], shared: bool,
                 choices: Optional[dict | list] = None, default: Any = None, disabled_default: Any = None,
                 disable: Optional[dict] = None, gui_tooltip: Optional[str] = None, gui_params: Optional[dict] = None,
                 cosmetic: bool = False) -> None:
        self.type: type = setting_type  # type of the setting's value, used to properly convert types to setting strings
        self.shared: bool = shared  # whether the setting is one that should be shared, used in converting settings to a string
        self.cosmetic: bool = cosmetic  # whether the setting should be included in the cosmetic log
        self.gui_text: Optional[str] = gui_text
        self.gui_type: Optional[str] = gui_type
        self.gui_tooltip: Optional[str] = "" if gui_tooltip is None else gui_tooltip
        self.gui_params: dict[str, Any] = {} if gui_params is None else gui_params  # additional parameters that the randomizer uses for the gui
        self.disable: Optional[dict] = disable  # dictionary of settings this setting disabled
        self.dependency = None  # lambda that determines if this is disabled. Generated later

        # dictionary of options to their text names
        choices = {} if choices is None else choices
        if isinstance(choices, list):
            self.choices: dict = {k: k for k in choices}
            self.choice_list: list = list(choices)
        else:
            self.choices: dict = dict(choices)
            self.choice_list: list = list(choices.keys())
        self.reverse_choices: dict = {v: k for k, v in self.choices.items()}

        # number of bits needed to store the setting, used in converting settings to a string
        if shared:
            if self.gui_params.get('min') and self.gui_params.get('max') and not choices:
                self.bitwidth = math.ceil(math.log(self.gui_params.get('max') - self.gui_params.get('min') + 1, 2))
            else:
                self.bitwidth = self.calc_bitwidth(choices)
        else:
            self.bitwidth = 0

        # default value if undefined/unset
        self.default = default
        if self.default is None:
            if self.type == bool:
                self.default = False
            elif self.type == str:
                self.default = ""
            elif self.type == int:
                self.default = 0
            elif self.type == list:
                self.default = []
            elif self.type == dict:
                self.default = {}

        # default value if disabled
        self.disabled_default = self.default if disabled_default is None else disabled_default

        # used to when random options are set for this setting
        if 'distribution' not in self.gui_params and 'randomize_key' in self.gui_params:
            if self.gui_type == 'MultipleSelect':
                self.gui_params['distribution'] = [(list(choice), 1) for choice in powerset(self.choice_list)]
            else:
                self.gui_params['distribution'] = [(choice, 1) for choice in self.choice_list]

    def __set_name__(self, owner, name: str) -> None:
        self.name = name

    def __get__(self, obj, obj_type=None) -> Any:
        value = obj.settings_dict.get(self.name, self.default)
        if value is None:
            return self.default
        return value

    def __set__(self, obj, value: Any) -> None:
        obj.settings_dict[self.name] = value

    def __delete__(self, obj) -> None:
        del obj.settings_dict[self.name]

    def calc_bitwidth(self, choices) -> int:
        count = len(choices)
        if count > 0:
            if self.type == list:
                # Need two special values for terminating additive and subtractive lists
                count = count + 2
            return math.ceil(math.log(count, 2))
        return 0

    def create_dependency(self, disabling_setting: 'SettingInfo', option, negative: bool = False) -> None:
        op = operator.__ne__ if negative else operator.__eq__
        if self.dependency is None:
            self.dependency = lambda settings: op(getattr(settings, disabling_setting.name), option)
        else:
            old_dependency = self.dependency
            self.dependency = lambda settings: op(getattr(settings, disabling_setting.name), option) or old_dependency(settings)


class SettingInfoNone(SettingInfo):
    def __init__(self, gui_text: Optional[str], gui_type: Optional[str], gui_tooltip: Optional[str] = None,
                 gui_params: Optional[dict] = None) -> None:
        super().__init__(setting_type=type(None), gui_text=gui_text, gui_type=gui_type, shared=False, choices=None,
                         default=None, disabled_default=None, disable=None, gui_tooltip=gui_tooltip,
                         gui_params=gui_params, cosmetic=False)

    def __get__(self, obj, obj_type=None) -> None:
        raise Exception(f"{self.name} is not a setting and cannot be retrieved.")

    def __set__(self, obj, value: str) -> None:
        raise Exception(f"{self.name} is not a setting and cannot be set.")


class SettingInfoBool(SettingInfo):
    def __init__(self, gui_text: Optional[str], gui_type: Optional[str], shared: bool, default: Optional[bool] = None,
                 disabled_default: Optional[bool] = None, disable: Optional[dict] = None, gui_tooltip: Optional[str] = None,
                 gui_params: Optional[dict] = None, cosmetic: bool = False) -> None:
        choices = {
            True:  'checked',
            False: 'unchecked',
        }

        super().__init__(setting_type=bool, gui_text=gui_text, gui_type=gui_type, shared=shared, choices=choices,
                         default=default, disabled_default=disabled_default, disable=disable, gui_tooltip=gui_tooltip,
                         gui_params=gui_params, cosmetic=cosmetic)

    def __get__(self, obj, obj_type=None) -> bool:
        value = super().__get__(obj, obj_type)
        if not isinstance(value, bool):
            value = bool(value)
        return value

    def __set__(self, obj, value: bool) -> None:
        if not isinstance(value, bool):
            value = bool(value)
        super().__set__(obj, value)


class SettingInfoStr(SettingInfo):
    def __init__(self, gui_text: Optional[str], gui_type: Optional[str], shared: bool = False,
                 choices: Optional[dict | list] = None, default: Optional[str] = None,
                 disabled_default: Optional[str] = None, disable: Optional[dict] = None,
                 gui_tooltip: Optional[str] = None, gui_params: Optional[dict] = None, cosmetic: bool = False) -> None:
        super().__init__(setting_type=str, gui_text=gui_text, gui_type=gui_type, shared=shared, choices=choices,
                         default=default, disabled_default=disabled_default, disable=disable, gui_tooltip=gui_tooltip,
                         gui_params=gui_params, cosmetic=cosmetic)

    def __get__(self, obj, obj_type=None) -> str:
        value = super().__get__(obj, obj_type)
        if not isinstance(value, str):
            value = str(value)
        return value

    def __set__(self, obj, value: str) -> None:
        if not isinstance(value, str):
            value = str(value)
        super().__set__(obj, value)


class SettingInfoInt(SettingInfo):
    def __init__(self, gui_text: Optional[str], gui_type: Optional[str], shared: bool,
                 choices: Optional[dict | list] = None, default: Optional[int] = None,
                 disabled_default: Optional[int] = None, disable: Optional[dict] = None,
                 gui_tooltip: Optional[str] = None, gui_params: Optional[dict] = None, cosmetic: bool = False) -> None:
        super().__init__(setting_type=int, gui_text=gui_text, gui_type=gui_type, shared=shared, choices=choices,
                         default=default, disabled_default=disabled_default, disable=disable, gui_tooltip=gui_tooltip,
                         gui_params=gui_params, cosmetic=cosmetic)

    def __get__(self, obj, obj_type=None) -> int:
        value = super().__get__(obj, obj_type)
        if not isinstance(value, int):
            value = int(value)
        return value

    def __set__(self, obj, value: int) -> None:
        if not isinstance(value, int):
            value = int(value)
        super().__set__(obj, value)


class SettingInfoList(SettingInfo):
    def __init__(self, gui_text: Optional[str], gui_type: Optional[str], shared: bool,
                 choices: Optional[dict | list] = None, default: Optional[list] = None,
                 disabled_default: Optional[list] = None, disable: Optional[dict] = None,
                 gui_tooltip: Optional[str] = None, gui_params: Optional[dict] = None, cosmetic: bool = False) -> None:
        super().__init__(setting_type=list, gui_text=gui_text, gui_type=gui_type, shared=shared, choices=choices,
                         default=default, disabled_default=disabled_default, disable=disable, gui_tooltip=gui_tooltip,
                         gui_params=gui_params, cosmetic=cosmetic)

    def __get__(self, obj, obj_type=None) -> list:
        value = super().__get__(obj, obj_type)
        if not isinstance(value, list):
            value = list(value)
        return value

    def __set__(self, obj, value: list) -> None:
        if not isinstance(value, list):
            value = list(value)
        super().__set__(obj, value)


class SettingInfoDict(SettingInfo):
    def __init__(self, gui_text: Optional[str], gui_type: Optional[str], shared: bool,
                 choices: Optional[dict | list] = None, default: Optional[dict] = None,
                 disabled_default: Optional[dict] = None, disable: Optional[dict] = None,
                 gui_tooltip: Optional[str] = None, gui_params: Optional[dict] = None, cosmetic: bool = False) -> None:
        super().__init__(setting_type=dict, gui_text=gui_text, gui_type=gui_type, shared=shared, choices=choices,
                         default=default, disabled_default=disabled_default, disable=disable, gui_tooltip=gui_tooltip,
                         gui_params=gui_params, cosmetic=cosmetic)

    def __get__(self, obj, obj_type=None) -> dict:
        value = super().__get__(obj, obj_type)
        if not isinstance(value, dict):
            value = dict(value)
        return value

    def __set__(self, obj, value: dict) -> None:
        if not isinstance(value, dict):
            value = dict(value)
        super().__set__(obj, value)


class Button(SettingInfoNone):
    def __init__(self, gui_text: Optional[str], gui_tooltip: Optional[str] = None,
                 gui_params: Optional[dict] = None) -> None:
        super().__init__(gui_text=gui_text, gui_type="Button", gui_tooltip=gui_tooltip, gui_params=gui_params)


class Textbox(SettingInfoNone):
    def __init__(self, gui_text: Optional[str], gui_tooltip: Optional[str] = None,
                 gui_params: Optional[dict] = None) -> None:
        super().__init__(gui_text=gui_text, gui_type="Textbox", gui_tooltip=gui_tooltip, gui_params=gui_params)


class Checkbutton(SettingInfoBool):
    def __init__(self, gui_text: Optional[str], gui_tooltip: Optional[str] = None, disable: Optional[dict] = None,
                 disabled_default: Optional[bool] = None, default: bool = False, shared: bool = False,
                 gui_params: Optional[dict] = None, cosmetic: bool = False):
        super().__init__(gui_text=gui_text, gui_type='Checkbutton', shared=shared, default=default,
                         disabled_default=disabled_default, disable=disable, gui_tooltip=gui_tooltip,
                         gui_params=gui_params, cosmetic=cosmetic)


class Combobox(SettingInfoStr):
    def __init__(self, gui_text: Optional[str], choices: Optional[dict | list], default: Optional[str],
                 gui_tooltip: Optional[str] = None, disable: Optional[dict] = None, disabled_default: Optional[str] = None,
                 shared: bool = False, gui_params: Optional[dict] = None, cosmetic: bool = False) -> None:
        super().__init__(gui_text=gui_text, gui_type='Combobox', shared=shared, choices=choices, default=default,
                         disabled_default=disabled_default, disable=disable, gui_tooltip=gui_tooltip,
                         gui_params=gui_params, cosmetic=cosmetic)


class Radiobutton(SettingInfoStr):
    def __init__(self, gui_text: Optional[str], choices: Optional[dict | list], default: Optional[str],
                 gui_tooltip: Optional[str] = None, disable: Optional[dict] = None, disabled_default: Optional[str] = None,
                 shared: bool = False, gui_params: Optional[dict] = None, cosmetic: bool = False) -> None:
        super().__init__(gui_text=gui_text, gui_type='Radiobutton', shared=shared, choices=choices, default=default,
                         disabled_default=disabled_default, disable=disable, gui_tooltip=gui_tooltip,
                         gui_params=gui_params, cosmetic=cosmetic)


class Fileinput(SettingInfoStr):
    def __init__(self, gui_text: Optional[str], choices: Optional[dict | list] = None, default: Optional[str] = None,
                 gui_tooltip: Optional[str] = None, disable: Optional[dict] = None, disabled_default: Optional[str] = None,
                 shared: bool = False, gui_params: Optional[dict] = None, cosmetic: bool = False) -> None:
        super().__init__(gui_text=gui_text, gui_type='Fileinput', shared=shared, choices=choices, default=default,
                         disabled_default=disabled_default, disable=disable, gui_tooltip=gui_tooltip,
                         gui_params=gui_params, cosmetic=cosmetic)


class Directoryinput(SettingInfoStr):
    def __init__(self, gui_text: Optional[str], choices: Optional[dict | list] = None, default: Optional[str] = None,
                 gui_tooltip: Optional[str] = None, disable: Optional[dict] = None, disabled_default: Optional[str] = None,
                 shared: bool = False, gui_params: Optional[dict] = None, cosmetic: bool = False) -> None:
        super().__init__(gui_text=gui_text, gui_type='Directoryinput', shared=shared, choices=choices, default=default,
                         disabled_default=disabled_default, disable=disable, gui_tooltip=gui_tooltip,
                         gui_params=gui_params, cosmetic=cosmetic)


class Textinput(SettingInfoStr):
    def __init__(self, gui_text: Optional[str], choices: Optional[dict | list] = None, default: Optional[str] = None,
                 gui_tooltip: Optional[str] = None, disable: Optional[dict] = None, disabled_default: Optional[str] = None,
                 shared: bool = False, gui_params: Optional[dict] = None, cosmetic: bool = False) -> None:
        super().__init__(gui_text=gui_text, gui_type='Textinput', shared=shared, choices=choices, default=default,
                         disabled_default=disabled_default, disable=disable, gui_tooltip=gui_tooltip,
                         gui_params=gui_params, cosmetic=cosmetic)


class ComboboxInt(SettingInfoInt):
    def __init__(self, gui_text: Optional[str], choices: Optional[dict | list], default: Optional[int],
                 gui_tooltip: Optional[str] = None, disable: Optional[dict] = None, disabled_default: Optional[int] = None,
                 shared: bool = False, gui_params: Optional[dict] = None, cosmetic: bool = False) -> None:
        super().__init__(gui_text=gui_text, gui_type='Combobox', shared=shared, choices=choices, default=default,
                         disabled_default=disabled_default, disable=disable, gui_tooltip=gui_tooltip,
                         gui_params=gui_params, cosmetic=cosmetic)


class Scale(SettingInfoInt):
    def __init__(self, gui_text: Optional[str], default: Optional[int], minimum: int, maximum: int, step: int = 1,
                 gui_tooltip: Optional[str] = None, disable: Optional[dict] = None, disabled_default: Optional[int] = None,
                 shared: bool = False, gui_params: Optional[dict] = None, cosmetic: bool = False) -> None:
        choices = {
            i: str(i) for i in range(minimum, maximum+1, step)
        }

        if gui_params is None:
            gui_params = {}
        gui_params['min'] = minimum
        gui_params['max'] = maximum
        gui_params['step'] = step

        super().__init__(gui_text=gui_text, gui_type='Scale', shared=shared, choices=choices, default=default,
                         disabled_default=disabled_default, disable=disable, gui_tooltip=gui_tooltip,
                         gui_params=gui_params, cosmetic=cosmetic)


class Numberinput(SettingInfoInt):
    def __init__(self, gui_text: Optional[str], default: Optional[int], minimum: Optional[int] = None,
                 maximum: Optional[int] = None, gui_tooltip: Optional[str] = None, disable: Optional[dict] = None,
                 disabled_default: Optional[int] = None, shared: bool = False, gui_params: Optional[dict] = None,
                 cosmetic: bool = False) -> None:
        if gui_params is None:
            gui_params = {}
        if minimum is not None:
            gui_params['min'] = minimum
        if maximum is not None:
            gui_params['max'] = maximum

        super().__init__(gui_text=gui_text, gui_type='Numberinput', shared=shared, choices=None, default=default,
                         disabled_default=disabled_default, disable=disable, gui_tooltip=gui_tooltip,
                         gui_params=gui_params, cosmetic=cosmetic)


class MultipleSelect(SettingInfoList):
    def __init__(self, gui_text: Optional[str], choices: Optional[dict | list], default: Optional[list],
                 gui_tooltip: Optional[str] = None, disable: Optional[dict] = None, disabled_default: Optional[list] = None,
                 shared: bool = False, gui_params: Optional[dict] = None, cosmetic: bool = False) -> None:
        super().__init__(gui_text=gui_text, gui_type='MultipleSelect', shared=shared, choices=choices, default=default,
                         disabled_default=disabled_default, disable=disable, gui_tooltip=gui_tooltip,
                         gui_params=gui_params, cosmetic=cosmetic)


class SearchBox(SettingInfoList):
    def __init__(self, gui_text: Optional[str], choices: Optional[dict | list], default: Optional[list],
                 gui_tooltip: Optional[str] = None, disable: Optional[dict] = None, disabled_default: Optional[list] = None,
                 shared: bool = False, gui_params: Optional[dict] = None, cosmetic: bool = False) -> None:
        super().__init__(gui_text=gui_text, gui_type='SearchBox', shared=shared, choices=choices, default=default,
                         disabled_default=disabled_default, disable=disable, gui_tooltip=gui_tooltip,
                         gui_params=gui_params, cosmetic=cosmetic)
