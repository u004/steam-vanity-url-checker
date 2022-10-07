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

from configparser import ConfigParser
from typing import Final, Union


class Section:
    """
    Defines section names of the config file.

    :cvar DEFAULT: Default section name.
    :cvar USER: User section name.
    """
    DEFAULT: Final[str] = 'Default'
    USER: Final[str] = 'User'


class Property:
    """
    Defines property names of the config file.

    :cvar OUTPUT_FILE_NAME: Output file property name.
    :cvar INPUT_FILE_NAME: Input file property name.
    :cvar ENDPOINT: Endpoint property name.
    :cvar PATTERN: Pattern property name.
    :cvar URL_MIN_LEN: Url minimum length property name.
    :cvar URL_MAX_LEN: Url maximum length property name.
    :cvar MENU_HISTORY: Menu history property name.
    :cvar URL_HISTORY: Url history property name.
    """
    OUTPUT_FILE_NAME: Final[str] = 'Out. File Name'
    INPUT_FILE_NAME: Final[str] = 'In. File Name'
    ENDPOINT: Final[str] = 'Endpoint'
    PATTERN: Final[str] = 'Pattern'
    URL_MIN_LEN: Final[str] = 'Url Min. Length'
    URL_MAX_LEN: Final[str] = 'Url Max. Length'
    MENU_HISTORY: Final[str] = 'Menu History'
    URL_HISTORY: Final[str] = 'Url History'


class Pattern:
    """
    Defines several default patterns.

    :cvar ANY: Any pattern value.
    :cvar ONLY_DIGITS: Only digits pattern value.
    :cvar ONLY_LETTERS: Only letters pattern value.
    """
    ANY: Final[str] = '.*'
    ONLY_DIGITS: Final[str] = '^[0-9]+$'
    ONLY_LETTERS: Final[str] = '^[a-z]+$'


class Endpoint:
    """
    Defines several default endpoints.

    :cvar ID: /id/ endpoint value.
    :cvar GROUPS: /groups/ endpoint value.
    """
    ID: Final[str] = 'id'
    GROUPS: Final[str] = 'groups'


data_path: Final[str] = 'data/'

_config_path: Final[str] = data_path + 'config.ini'
_default_params: Final[dict[str, Union[str, int, bool]]] = {
    Property.OUTPUT_FILE_NAME: 'Available.txt',
    Property.INPUT_FILE_NAME: 'Checkable.txt',
    Property.ENDPOINT: Endpoint.ID,
    Property.PATTERN: Pattern.ANY,
    Property.URL_MIN_LEN: 3,
    Property.URL_MAX_LEN: 3,
    Property.MENU_HISTORY: False,
    Property.URL_HISTORY: True
}

config: Final[ConfigParser] = ConfigParser()


def init_cfg() -> None:
    """
    Initialize config.

    Creates missing ./data/ directory.

    :return: None.
    """
    if not os.path.isdir(data_path):
        os.mkdir(data_path)


def save_cfg() -> None:
    """
    Save config to the file.

    Creates and saves config to a
    file at the path "./data/config.ini"

    :return: None.
    """
    with open(_config_path, 'w') as cfg_file:
        config.write(cfg_file)


def read_cfg() -> None:
    """
    Read config file to the global config variable.

    Reads a config file or assigns a global
    config variable with default parameters.

    :return: None.
    """
    if os.path.isfile(_config_path):
        config.read(_config_path)
    else:
        config[Section.DEFAULT] = \
            config[Section.USER] = _default_params


def reset_cfg() -> None:
    """
    Reset user config section.

    Assigns user config section with default config section.

    :return: None.
    """
    config[Section.USER] = config[Section.DEFAULT]
