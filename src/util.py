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

from inspect import getattr_static, isfunction
from typing import Type, Callable, Final, Union, Any

_yes_values: Final[list[str]] = ['true', 'yes', 'y']
_no_values: Final[list[str]] = ['false', 'no', 'n']


def enum_values(clazz: Type) -> list:
    """
    Return enum class fields.

    Returns fields of the enum class if the field
    name does not start with an underscore or is not a method.

    :param clazz: Enum class.
    :return: List of fields.
    """
    result: Final[list] = []

    for name, value in vars(clazz).items():
        static_attr: Any = getattr_static(clazz, name)

        if name.startswith('_') \
                or isfunction(value) \
                or isinstance(static_attr, staticmethod) \
                or isinstance(static_attr, classmethod):
            continue

        result.append(value)

    return result


def limit(val: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> Union[int, float]:
    """
    Limit the number within the minimum and maximum bounds.

    :param val: Number to limit.
    :param min_val: Minimum bound.
    :param max_val: Maximum bound.
    :return: Limited value.
    """
    return max(min(val, max_val), min_val)


def number(val: Union[Callable[[], Union[int, float]], int, float]) -> Union[int, float]:
    """
    Convert a value to a number.

    :param val: Value to be converted.
    :return: Number.
    :raise ValueError: If the type of value after conversion is not int or float.
    """
    r = val

    if isinstance(r, Callable):
        r = val()

    if not (isinstance(r, int) or isinstance(r, float)):
        raise ValueError()

    return r


def boolean(val: Union[bool, str]) -> bool:
    """
    Convert a value to a boolean.

    The conversion is case-independent.

    :param val: Value to be converted.
    :return: Boolean value.
    :raise ValueError: If the value is not of type bool or str or if the value is not
     contained in the list of valid values e.g. ['true', 'yes', 'y'] or ['false', 'no', 'n'].
    """
    if isinstance(val, bool):
        return val

    if isinstance(val, str):
        val = val.lower()

        is_yes: Final[bool] = val in _yes_values
        is_no: Final[bool] = val in _no_values

        if is_yes != is_no:
            return is_yes

    raise ValueError()
