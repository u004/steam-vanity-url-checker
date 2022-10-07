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

import builtins
import os

import asyncio
import cursor

from config import init_cfg, read_cfg
from typing import Final, Callable, Optional
from menu import Menu, ConfigMenu, SteamMenu

from argparse import ArgumentParser, Namespace

import github

_license_path: Final[str] = f'{os.path.dirname(__file__)}/../COPYING'


def _is_gh_args(_args: Namespace) -> bool:
    """
    Determine if the arguments include the '--gh::*' flags.

    :param _args: Command line arguments.
    :return: Boolean.
    """
    for key, val in _args.__dict__.items():
        if key.startswith('gh_') and val:
            return True

    return False


def _init_builtins() -> None:
    """
    Override built-in functions.

    Overrides the input function to
    enable the cursor when entering text.

    :return: None.
    """
    real_input: Final[Callable[[str], str]] = builtins.input

    def new_input(prompt: str = '') -> Optional[str]:
        """
        Input with enabled cursor.

        Enables the cursor when entering text
        and disables it when exiting input.

        :param prompt: Input prefix.
        :return: String or None.
        """
        cursor.show()

        result = None
        try:
            result = real_input(prompt)
        except KeyboardInterrupt:
            print()

        cursor.hide()
        return result

    builtins.input = new_input


if __name__ == '__main__':
    asyncio.set_event_loop(asyncio.new_event_loop())

    arg_parser: Final[ArgumentParser] = ArgumentParser()

    arg_parser.add_argument(
        '--license',
        help='show the project license and exit',
        dest='is_license',
        action='store_true'
    )

    arg_parser.add_argument(
        '--gh::uid-action',
        help='run the github#uid_action',
        dest='gh_uid_action',
        action='store_true'
    )

    args: Final[Namespace] = arg_parser.parse_args()

    if args.is_license:
        with open(_license_path, 'r') as license_file:
            print(license_file.read())

        exit()

    # GitHub Actions
    if _is_gh_args(args):
        if args.gh_uid_action:
            github.uid_action()

        exit()

    _init_builtins()

    init_cfg()
    read_cfg()

    config_menu: Final[Menu] = ConfigMenu()
    steam_menu: Final[Menu] = SteamMenu()

    main_menu: Final[Menu] = Menu('Main')
    main_menu.append([config_menu, steam_menu])
    main_menu.append_exit()

    cursor.hide()

    try:
        main_menu.render()
    except (KeyError, KeyboardInterrupt):
        pass

    os.system('cls')
    cursor.show()
