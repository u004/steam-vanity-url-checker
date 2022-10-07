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

from typing import Final, Union


def to_base(num: int, base: str) -> str:
    """
    Convert an integer number to a string based on the specified base.

    The conversion uses a conversion format that does not include zero.

    :param num: Number to be converted.
    :param base: Base of the result.
    :return: Number-string with base of the specified base.
    :raise ValueError: If the number is less than 1.
    """
    if num < 1:
        raise ValueError()

    base_len: Final[int] = len(base)

    r: str = ''
    while num:
        mod: int = (num - 1) % base_len
        r = base[mod] + r
        num = (num - mod) // base_len

    return r


def from_base(num: str, base: str) -> int:
    """
    Convert a number with specified base to an integer with base 10.

    The conversion uses a conversion format that does not include zero.

    :param num: Number to be converted.
    :param base: Base of the number.
    :return: Integer number with base 10.
    """
    base_len: Final[int] = len(base)

    r: int = 0
    for i in num:
        r = r * base_len + base.index(i) + 1

    return r


def swap_base(num: Union[str, int], base: str) -> Union[str, int]:
    """
    Swap the base of the number.

    The conversion uses a conversion format that does not include zero.

    :param num: Number to be converted.
    :param base: Base of the number or result.
    :return: Number-string if the number is of type int otherwise an integer number if the number is of type str.
    :raise ValueError: If the number is not an instance of type int or str.
    """
    if isinstance(num, int):
        return to_base(num, base)

    if isinstance(num, str):
        return from_base(num, base)

    raise ValueError()
