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
import time
import Stockings

# Project imports
from .. import py_compat


class _Stocking(Stockings.Stocking):
    """ Class which subclasses a Stocking to send and recv messages to and from a remote endpoint. """

    # Crypto module used to partake in encrpyted communication with the other endpoint
    encryptor = None
    CryptoMessage = CryptoMessage

    HANDSHAKE_SLEEP_TIME = .3


    def __init__(self, conn, encryptor):
        self.connectionTime = int(time.time())
        self.encryptor = encryptor

        super(Stockings.Stocking, self).__init__(conn)

    def preWrite(self, s):
        """ Encrypts a string before it is sent to the endpoint. """

        return self.encryptor.encrypt(s)

    def postRead(self, s):
        """ Decrypts a string received from the endpoint. """

        return CryptoMessage(self.encryptor.decrypt(s))
