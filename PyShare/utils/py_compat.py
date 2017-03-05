"""
    Copyright (C) 2016 Warren Spencer warrenspencer27@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    Author: Warren Spencer
    Email:  warrenspencer27@gmail.com
"""

# Standard imports
import sys

if sys.version_info.major == 2:
    UNICODE = unicode

else:
    UNICODE = str


def toBytes(s):
    """
    Converts a Py2 unicode/Py3 string object to bytes using the utf8 codec.
    If a Py2 string/Py3 bytes object is given this function performs no operation.
    """

    if isinstance(s, UNICODE):
        return s.decode('utf8')

    elif isinstance(s, bytes):
        return s

    raise Exception("Cannot convert non-unicode/bytes object to bytes.")
