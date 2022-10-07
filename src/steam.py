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

import asyncio
import os

import re as regx

# noinspection PyPep8Naming
from sre_constants import error as RegexError

from typing import Final, Optional
from string import ascii_lowercase, digits
from aiohttp import ClientSession, ClientTimeout, ClientError
from base import to_base, from_base
from config import Pattern

# noinspection PyPep8Naming
from colorama import Fore as fclr

_base: Final[str] = ascii_lowercase + digits + '-_'
_url_format: Final[str] = 'https://steamcommunity.com/%s/%s'

_default_timeout: Final[ClientTimeout] = ClientTimeout()
_default_pattern: Final[str] = Pattern.ANY
_default_history: Final[bool] = False

gen_list: list[str] = []
check_list: list[str] = []


def bz_gen_urls(min_len: int, max_len: int, pattern: Optional[str] = None, history: Optional[bool] = None) -> None:
    """
    Generate a list of steam vanity URls based on minimum and maximum length and pattern.

    :param min_len: Minimum url length.
    :param max_len: Maximum url length.
    :param pattern: Pattern for comparison with a url.
    :param history: Defines the output of urls.
    :return: None.
    :raise ValueError: If the minimum length is less than 1 or the maximum length is less than the minimum length.
    """
    if min_len < 1 or max_len < min_len:
        raise ValueError()

    if not pattern:
        pattern = _default_pattern

    if not history:
        history = _default_history

    global gen_list
    gen_list.clear()

    left: Final[int] = from_base(_base[0] * min_len, _base)
    right: Final[int] = from_base(_base[-1] * max_len, _base)

    try:
        cmpl_pattern: Final[regx.Pattern] = regx.compile(pattern)
    except RegexError:
        return

    for i in range(left, right):
        url: str = to_base(i, _base)
        if cmpl_pattern.search(url):
            gen_list.append(url)

            if history:
                _print_url(url)


def fp_gen_urls(file_path: str) -> None:
    """
    Generate a list of steam vanity urls from a file.

    Creates a file if it does not exist at the specified path.

    :param file_path: Path to file.
    :return: None.
    """
    if not os.path.isfile(file_path):
        with open(file_path, 'w'):
            pass

    with open(file_path, 'r') as in_file:
        global gen_list
        gen_list = [url for url in in_file.read().split('\n') if url]


def check_urls(endpoint: str, history: Optional[bool] = None) -> None:
    """
    Check all generated steam vanity urls.

    :param endpoint: Endpoint to add a vanity url to.
    :param history: Defines the output of urls.
    :return: None.
    """
    if not gen_list:
        return

    if not history:
        history = _default_history

    check_list.clear()

    async def check_url(session: ClientSession, url: str) -> None:
        """
        Check the specified steam vanity url.

        :param session: Client session.
        :param url: Vanity url itself.
        :return: None.
        """
        async with session.get(_url_format % (endpoint, url)) as response:
            try:
                if history:
                    _print_url(url)

                content: Final[str] = await response.text()

                if content \
                        and '<p class="returnLink">' in content \
                        and 'This group has been removed' not in content:
                    check_list.append(url)
            except (ValueError, ClientError):
                pass

    async def wrapper() -> None:
        async with ClientSession(timeout=_default_timeout) as session:
            await asyncio.gather(*[check_url(session, url) for url in gen_list])

    asyncio.get_event_loop() \
        .run_until_complete(wrapper())


def save_urls(path: str) -> None:
    """
    Save checked urls to the file.

    :param path: Path to the file to save to.

    :return: None.
    """
    with open(path, 'w') as out_file:
        out_file.write('\n'.join(sorted(check_list)))


def _print_url(url: str) -> None:
    """
    Print the steam vanity url with the prefix '@'.

    :param url: Url to be printed.
    :return: None.
    """
    print(f'{fclr.RESET}{" " * 4}{fclr.LIGHTMAGENTA_EX}@ {fclr.LIGHTWHITE_EX}{url}{fclr.RESET}')
