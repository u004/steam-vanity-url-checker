#  Steam Vanity Url Checker
#
#  Copyright (C) 2022  u004
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import util
import steam

from typing import Callable, Final, Union, Optional, Any, Type
from PyInquirer import prompt, Separator
from config import config, save_cfg, read_cfg, reset_cfg, data_path, Section, Property, Pattern, Endpoint

separator: Final[Separator] = Separator(' ')


class MenuElement:
    """
    Defines the basic menu element.
    """

    def __init__(self, message: str, select_call: Optional[Callable] = None, parent: Optional = None) -> None:
        # noinspection PyUnresolvedReferences
        """
        Initialize a MenuElement instance.

        :param message: Message to print. Mostly used as a name.
        :param select_call: Callback for a menu element when selecting.
        :param parent: Parent.
        :type parent: Menu
        :return: None.
        :raise ValueError: If parent is not None and parent is not an instance of Menu.
        """
        self._message: Final[str] = message

        if parent and not isinstance(parent, Menu):
            raise ValueError()

        self._parent: Final[Optional[Menu]] = parent

        self.__select_call: Final[Optional[Callable]] = select_call

    def select(self):
        """
        Call select callback and return parent.

        :return: Parent or None.
        """
        if self.__select_call:
            self.__select_call()

        return self._parent


class ExitMenuElement(MenuElement):
    """
    Defines exit menu element.

    When selected, exits the program.
    """

    def __init__(self, name: str = 'Exit') -> None:
        """
        Initialize an ExitMenuElement instance.

        :param name: Name to render.
        :return: None.
        """
        super().__init__(name, self.__exit)

    @staticmethod
    def __exit() -> None:
        """
        Exit the program.

        :return: None.
        """
        raise KeyError


class BackMenuElement(MenuElement):
    """
    Defines back menu element.

    When selected, returns to the parent.
    """

    def __init__(self, parent, name: str = 'Back') -> None:
        """
        Initialize a BackMenuElement instance.

        :param parent: Parent to return to.
        :param name: Name to render.
        :return: None.
        """
        super().__init__(name, parent=parent)


class Menu(MenuElement):
    """
    Defines the basic menu.

    :cvar __exit_element: Final static reference to an ExitMenuElement instance.
    """
    __exit_element: Final[MenuElement] = ExitMenuElement()

    def __init__(self, name: str, message: Optional[str] = None) -> None:
        """
        Initialize a Menu instance.

        :param name: Menu name. Used as a key.
        :param message: Message to render. Mostly used name parameter instead.
        :return: None.
        """
        if not message:
            message = name

        super().__init__(message)

        self.__name: Final[str] = name
        self.__elements: Final[dict[str, MenuElement]] = {}
        self.__choices: Final[list[Union[str, Separator]]] = []

        self.__questions: Final[dict[str, Any]] = {
            'type': 'list',
            'name': self.__name,
            'message': self._message,
            'choices': self.__choices,
        }

    def append(self, element: Optional, use_exit: bool = True) -> None:
        """
        Append element.

        Appends list of elements, MenuElement, Menu, or Separator.

        :param element: Element to append.
        :param use_exit: Used to append an exit element if the element parameter is an instance of the Menu.
        :return: None.
        """
        if not element:
            return

        if isinstance(element, list):
            self.__multi_append(element)

        if isinstance(element, MenuElement):
            self.__elements[element._message] = element
            self.__choices.append(element._message)

            if isinstance(element, Menu) and use_exit:
                element.append_exit(self)
        elif isinstance(element, Separator):
            self.__choices.append(element)

    def __multi_append(self, elements: list) -> None:
        """
        Call self.append for each element in elements.

        self.__multi_append is a wrapper for self.append
        to avoid some gaps for the listed elements.

        :param elements: List of elements.
        :return: None.
        """
        for element in elements:
            self.append(element)

    def append_exit(self, parent: Optional = None, use_sep: bool = True) -> None:
        """
        Append exit or back element to the Menu.

        :param parent: Parent to exit to.
        :param use_sep: Appends blank line before exit or back element.
        :return: None.
        """
        if use_sep:
            self.append(separator)

        self.append(BackMenuElement(parent) if parent else self.__exit_element)

    def select(self) -> MenuElement:
        """
        Return selected MenuElement.

        :return: Selected MenuElement.
        """
        return self.__elements[prompt([self.__questions], keyboard_interrupt_msg='')[self.__name]]

    def render(self) -> None:
        """
        Render the whole Menu.

        :return: None.
        """
        prev_element: MenuElement = self
        curr_element: MenuElement = prev_element

        while True:
            if not config.getboolean(Section.USER, Property.MENU_HISTORY):
                os.system('cls')

            next_element: Optional[MenuElement] = curr_element.select()

            if next_element:
                prev_element = curr_element
                curr_element = next_element
            else:
                curr_element = prev_element


class GenUrlsElement(MenuElement):
    """
    Defines a MenuElement wrapper for steam.bz_gen_urls & steam.fp_gen_urls.
    """

    def __init__(self, name: str, use_file: bool, parent: Optional[Menu] = None) -> None:
        """
        Initialize a GenUrlsElement instance.

        :param name: Name to render.
        :param use_file: Type of the generation. True for file based generation. False for base based generation.
        :param parent: Parent.
        :return: None.
        """
        super().__init__(name, self.__gen_urls, parent)

        self.__use_file: Final[bool] = use_file

    def __gen_urls(self) -> None:
        """
        Wrap self.__bz_gen_urls & self.__fp_gen_urls static methods.

        :return: None.
        """
        try:
            if self.__use_file:
                self.__fp_gen_urls()
            else:
                self.__bz_gen_urls()
        except KeyboardInterrupt:
            pass

    @staticmethod
    def __bz_gen_urls() -> None:
        """
        Wrap steam.bz_gen_urls function.

        :return: None.
        """
        steam.bz_gen_urls(
            config.getint(Section.USER, Property.URL_MIN_LEN),
            config.getint(Section.USER, Property.URL_MAX_LEN),

            config[Section.USER][Property.PATTERN],

            config.getboolean(Section.USER, Property.URL_HISTORY)
        )

    @staticmethod
    def __fp_gen_urls() -> None:
        """
        Wrap steam.fp_gen_urls function.

        :return: None.
        """
        steam.fp_gen_urls(data_path + config[Section.USER][Property.INPUT_FILE_NAME])


class CheckUrlsElement(MenuElement):
    """
    Defines a MenuElement wrapper for steam.check_urls.
    """

    def __init__(self, name: str = 'Check', parent: Optional[Menu] = None) -> None:
        """
        Initialize a CheckUrlsElement instance.

        :param name: Name to render.
        :param parent: Parent.
        """
        super().__init__(name, self.__check_urls, parent)

    @staticmethod
    def __check_urls() -> None:
        """
        Wrap steam.check_urls with async execution.

        Writes all successfully checked urls to the file.

        :return: None.
        """
        try:
            steam.check_urls(
                config[Section.USER][Property.ENDPOINT],
                config.getboolean(Section.USER, Property.URL_HISTORY)
            )
        except KeyboardInterrupt:
            pass

        steam.save_urls(data_path + config[Section.USER][Property.OUTPUT_FILE_NAME])


class SteamMenu(Menu):
    """
    Defines a default steam menu that includes
    GenUrlsElement & CheckUrlsElement elements.
    """

    def __init__(self, name: str = 'Steam') -> None:
        """
        Initialize a SteamMenu instance.

        :param name: Name to render.
        :return: None.
        """
        super().__init__(name)

        gen_menu: Final[Menu] = Menu('Generate')

        gen_menu.append([
            GenUrlsElement('From Base', False, self),
            GenUrlsElement('From File', True, self)
        ])

        self.append([gen_menu, CheckUrlsElement()])


class ConfigElement(MenuElement):
    """
    Defines a MenuElement that can
    update a config property value.
    """

    def __init__(self, token: str, name: str, val_call: Callable, parent: Optional[Menu] = None) -> None:
        """
        Initialize a ConfigElement instance.

        :param token: Config property key.
        :param name: Name to render.
        :param val_call: Callback for self.__upd_param.
        :param parent: Parent.
        :return: None.
        """
        super().__init__(name, self.__upd_param, parent)

        self._token: Final[str] = token
        self.__val_call: Final[Callable] = val_call

    def __upd_param(self) -> None:
        """
        Update the config property with a new value.

        :return: None.
        """
        config[Section.USER][self._token] = str(self.__val_call())


class RawConfigElement(ConfigElement):
    """
    Wraps the ConfigElement and
    overrides self.__upd_param with
    raw lambda that returns value.
    """

    def __init__(self, token: str, name: str, value, parent: Optional[Menu] = None) -> None:
        """
        Initialize a RawConfigElement instance.

        :param token: Key to the config property.
        :param name: Name to render.
        :param value: Value to wrap with lambda.
        :param parent: Parent.
        :return: None.
        """
        super().__init__(token, name, lambda: value, parent)


class CustomConfigElement(ConfigElement):
    """
    Adds a feature for custom input
    to define a new property value.
    """

    def __init__(self, token: str, name: Optional[str] = None, prompt_message: str = '> ') -> None:
        """
        Initialize a CustomConfigElement instance.

        :param token: Key to the config property.
        :param name: Name to render.
        :param prompt_message: Prompt message for the custom input. Used as a prefix before input.
        :return: None.
        """
        super().__init__(token, name if name else token, self._input_param)

        self._prompt_message: Final[str] = prompt_message

    def _input_param(self) -> str:
        """
        Wrap built-in input function.

        :return: String result of the input function or the value from the config if the input failed.
        """
        result: Optional[str] = input(self._prompt_message)
        print()

        return result if result else config[Section.USER][self._token]


class RangeCustomConfigElement(CustomConfigElement):
    """
    Adds a feature for custom input
    to define a range of properties.
    """

    def __init__(self, token: str,
                 min_val: Union[Callable[[], Union[int, float]], str, int, float],
                 max_val: Union[Callable[[], Union[int, float]], str, int, float],
                 cast_call: Callable[[Union], Union[int, float]] = int,
                 prompt_message: str = '> ') -> None:
        """
        Initialize a RangeCustomConfigElement instance.

        The boundaries of the range can be defined as strings, then
        the config property will be used to limit the boundaries.

        :param token: Key to the config property.
        :param min_val: Minimum range bound value.
        :param max_val: Maximum range bound value.
        :param cast_call: Casting function.
        :param prompt_message: Prompt message for the custom input. Used as a prefix before input.
        :return: None.
        """
        super().__init__(token, prompt_message=prompt_message)

        self.__min_val: Final[Union[Callable[[], Union[int, float]], str, int, float]] = min_val
        self.__max_val: Final[Union[Callable[[], Union[int, float]], str, int, float]] = max_val
        self.__cast_call: Final[Callable[[Union], Union[int, float]]] = cast_call

    def _input_param(self) -> str:
        """
        Override _input_param method.

        Limits the result of calling the super()._input_param
        method using the util.limit function.

        :return: Limited number-string or config property value if raised ValueError.
        """
        try:
            min_val: Union[int, float] = self.__number(self.__min_val)
            max_val: Union[int, float] = self.__number(self.__max_val)
            val: Union[int, float] = self.__cast_call(super()._input_param())

            return str(util.limit(val, min_val, max_val))
        except ValueError:
            return config[Section.USER][self._token]

    def __number(self, val: Union[str, Callable[[], Union[int, float]], int, float]) -> Union[int, float]:
        """
        Convert value to number.

        Used for range boundaries conversion.
        If value is an instance of str config
        then property value returned.

        :param val: Value to be converted.
        :return: Number.
        """
        return self.__cast_call(config[Section.USER][val] if isinstance(val, str) else util.number(val))


class BooleanConfigMenu(Menu):
    """
    Defines Yes/No (Type.ANSWER) or
    Enable/Disable (Type.SWITCH) menu.

    :cvar __type_names: Table of rows with selection names.
    """

    class Type:
        """
        Enum class.

        :cvar ANSWER: Yes/No.
        :cvar SWITCH: Enable/Disable.
        """
        ANSWER: Final[int] = 0
        SWITCH: Final[int] = 1

    __type_names: Final[list[list[str]]] = [
        ['Yes', 'No'],
        ['Enable', 'Disable']
    ]

    def __init__(self, token: str, name_type: int) -> None:
        """
        Initialize a BooleanConfigMenu instance.

        :param token: Key to the config property.
        :param name_type: Type of names.
        :return: None.
        """
        super().__init__(token)

        type_names: Final[list[str]] = self.__type_names[name_type]

        self.append([
            RawConfigElement(token, type_names[0], True),
            RawConfigElement(token, type_names[1], False)
        ])


class EnumConfigMenu(Menu):
    """
    Defines config menu for the enum classes.
    """

    def __init__(self, token: str, clazz: Type, customizable: bool) -> None:
        """
        Initialize an EnumConfigMenu instance.

        :param token: Key to the config property.
        :param clazz: Enum class.
        :param customizable: Defines whenever the property
         can accept custom values.
        :return: None.
        """
        super().__init__(token)

        self.append([
            RawConfigElement(token, str(val), val, self)
            for val in util.enum_values(clazz)
        ])

        if customizable:
            self.append([
                separator,
                CustomConfigElement(token, 'Custom')
            ])


class ConfigMenu(Menu):
    """
    Defines a default config menu.

    :cvar __save_cfg_element: Final static reference to a MenuElement instance that
     saves current config.
    :cvar __read_cfg_element: Final static reference to a MenuElement instance that
     reads current config.
    :cvar __reset_cfg_element: Final static reference to a MenuElement instance that
     resets current config.
    :cvar __out_file_name_element: Final static reference to a CustomConfigElement instance that
     updates output file name property value.
    :cvar __in_file_name_element: Final static reference to a CustomConfigElement instance that
     updates input file name property value.
    :cvar __pattern_enum_menu: Final static reference to an EnumConfigMenu instance that
     updates pattern property value.
    :cvar __endpoint_enum_menu: Final static reference to an EnumConfigMenu instance that
     updates endpoint property value.
    :cvar __url_min_len_element: Final static reference to a RangeCustomConfigElement instance that
     updates url minimum length property value.
    :cvar __url_max_len_element: Final static reference to a RangeCustomConfigElement instance that
     updates url maximum length property value.
    :cvar __menu_history_menu: Final static reference to a BooleanConfigMenu instance that
     updates menu history property value.
    :cvar __url_history_menu: Final static reference to a BooleanConfigMenu instance that
     updates url history property value.
    """
    __save_cfg_element: Final[MenuElement] = MenuElement('Save', save_cfg)
    __read_cfg_element: Final[MenuElement] = MenuElement('Read', read_cfg)
    __reset_cfg_element: Final[MenuElement] = MenuElement('Reset', reset_cfg)

    __out_file_name_element: Final[MenuElement] = CustomConfigElement(Property.OUTPUT_FILE_NAME)
    __in_file_name_element: Final[MenuElement] = CustomConfigElement(Property.INPUT_FILE_NAME)

    __pattern_enum_menu: Final[Menu] = EnumConfigMenu(Property.PATTERN, Pattern, True)
    __endpoint_enum_menu: Final[Menu] = EnumConfigMenu(Property.ENDPOINT, Endpoint, True)

    __url_min_len_element: Final[MenuElement] = RangeCustomConfigElement(Property.URL_MIN_LEN, 2, Property.URL_MAX_LEN)
    __url_max_len_element: Final[MenuElement] = RangeCustomConfigElement(Property.URL_MAX_LEN, Property.URL_MIN_LEN, 4)

    __menu_history_menu: Final[Menu] = BooleanConfigMenu(Property.MENU_HISTORY, BooleanConfigMenu.Type.SWITCH)
    __url_history_menu: Final[Menu] = BooleanConfigMenu(Property.URL_HISTORY, BooleanConfigMenu.Type.SWITCH)

    def __init__(self, name: str = 'Config') -> None:
        """
        Initialize a ConfigMenu instance.

        :param name: Name to render.
        :return: None.
        """
        super().__init__(name)

        self.append([
            self.__out_file_name_element,
            self.__in_file_name_element,

            separator,

            self.__pattern_enum_menu,
            self.__endpoint_enum_menu,

            self.__url_min_len_element,
            self.__url_max_len_element,

            separator,

            self.__menu_history_menu,
            self.__url_history_menu,

            separator,

            self.__save_cfg_element,
            self.__read_cfg_element,
            self.__reset_cfg_element
        ])
