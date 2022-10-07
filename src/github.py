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

import steam

from config import Endpoint


def uid_action() -> None:
    """
    Call this function for the .github/workflows/uid-action.yml workflow.

    :return: None.
    """
    def wrapper(min_len: int, max_len: int, endpoint: str) -> None:
        """
        Generate, check, and save steam vanity urls.

        Saves urls to a file with the prefix - 'gh#u-'.

        :param min_len: Minimum url length.
        :param max_len: Maximum url length.
        :param endpoint: Endpoint to add a vanity url to.
        :return: None.
        """
        steam.bz_gen_urls(min_len, max_len)
        steam.check_urls(endpoint)
        steam.save_urls(f'gh#u-{endpoint}.txt')

    try:
        wrapper(3, 3, Endpoint.ID)
        wrapper(2, 3, Endpoint.GROUPS)
    except KeyboardInterrupt:
        pass
