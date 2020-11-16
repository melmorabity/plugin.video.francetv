# coding: utf-8
#
# Copyright © 2020 melmorabity
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

from __future__ import unicode_literals
import logging

try:
    from typing import Any
    from typing import Dict
    from typing import List
    from typing import Optional
    from typing import Text
    from typing import Tuple
    from typing import Union

    Item = Dict[Text, Any]
    Collection = List[Item]
    # pylint: disable=unsubscriptable-object
    CollectionId = List[Tuple[Text, Union[int, Text]]]
except ImportError:
    pass

from unittest import TestCase

from resources.lib.api import FranceTV


class WalkthroughTest(TestCase):

    _API = FranceTV()

    def _scan_collection(
        self,
        path,  # type: Text
        level,  # type: Optional[int]
        _buffer,  # type: List[Tuple[Text, Optional[int]]]
    ):
        # type: (...) -> None

        if not _buffer:
            _buffer = []

        if (path, level) in _buffer:
            return

        _buffer.append((path, level))

        for item in self._API.get_collection(path, level):
            logging.debug("item = %s", item)

            self.assertTrue(item)
            self.assertTrue(item.label)
            self.assertTrue(item.url)

            mode = item.url.get("mode")
            self.assertTrue(mode, ["watch", "collection"])

            if mode != "watch":
                new_path = item.url.get("path")
                self.assertTrue(new_path)

                if item.url.get("level") is not None:
                    self.assertTrue(isinstance(item.url["level"], int))
                    new_level = int(item.url["level"])  # type: Optional[int]
                else:
                    new_level = None

                self._scan_collection(
                    new_path,  # type: ignore
                    new_level,
                    _buffer,
                )

    def test_walthrough(self):
        # type: () -> None

        _buffer = []  # type: List[Tuple[Text, Optional[int]]]

        self._scan_collection("apps/page/_", None, _buffer)
        self._scan_collection("generic/directs", None, _buffer)
        self._scan_collection("generic/channels", None, _buffer)
        self._scan_collection("generic/categories", None, _buffer)
