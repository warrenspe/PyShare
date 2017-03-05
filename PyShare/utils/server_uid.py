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


class ServerUID(object):
    """ Class which contains metadata necessary to connect to a PyShare server. """

    attrs = [
        'name',
        'host',
        'port'
    ]

    def __init__(self, *args):
        for name, val in zip(self.attrs, args):
            setattr(self, name, val)

    def toString(self):
        uid = kimchi.dumps(tuple(getattr(self, name) for name in self.attrs))

        # Strip any trailing equal signs from the digest
        return uid.encode('base64').strip().rstrip(b'=')

    def fromString(self, s):
        # Add any missing equal signs from the digest
        s += '=' * (4 - (len(s) % 4))
        s = s.decode('base64')

        for name, val in zip(self.attrs, kimchi.loads(s)):
            setattr(self, name, val)
