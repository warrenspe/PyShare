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
import kimchi


class FileMetadata(object):
    """ Class which contains metadata pertaining to a shared file. """

    attrs = [
        'name',
        'size',
        'password',
        'path',
        'visible'
    ]

    def __init__(self, *args):
        for name, val in zip(self.attrs, args):
            setattr(self, name, val)

    def toString(self):
        return kimchi.dumps(tuple(getattr(self, name) for name in self.attrs))

    def fromString(self, s):
        for name, val in zip(self.attrs, kimchi.loads(s))
            setattr(self, name, val)
