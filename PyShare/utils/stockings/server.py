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
import kimchi

# Project imports
from . import _Stocking
from .. import config


class ServerStocking(_Stocking):
    """ Class which subclasses a Stocking to send and recv messages to and from PyShare Clients. """

    # Username of the user who's authenticating
    username = None
    # Server password
    password = None
    # Address of the client
    addr = None
    # Unique identifier of this session
    userID = None
    # File descriptor of the connection
    sockFileno = None
    # Time the connection was established
    connectionTime = None

    def __init__(self, conn, userID, encryptor):
        conf = config.server()

        self.connectionTime = int(time.time())
        self.sockFileno = conn.fileno()
        self.userID = userID
        self.addr = conn.getpeername()
        self.username = "%s:%s" % self.addr # Updated later, when we receive the actual username
        self.password = conf.server_password

        super(self.__class__, self).__init__(conn, encryptor)

    def handshake(self): # TODO cmdline args with _, break
        """ Authenticates a CryptoConnection, setting up encryption and receiving its credentials. """

        phase = 1

        while self.active:
            # Phase 1: Receive the clients public key
            if phase == 1:
                pubKey = self._read()
                if pubKey:
                    encryptedSymmKey = self.encryptor.registerClientPublicKey(pubKey)
                    phase += 1

            # Phase 2: Send the client our encrypted symmetric key
            elif phase == 2:
                self._write(encryptedSymmKey)
                phase += 1

            # Phase 3: Receive and verify the clients salt and hashed password
            elif phase == 3:
                creds = self._read()
                if creds:
                    salt, hashed = kimchi.loads(creds)
                    if self.encryptor.hash(self.password, salt) != hashed:
                        return False
                    phase += 1

            # Phase 4: Send the user the hashed password salted with salt + 1
            elif phase == 4:
                salt = salt[:-1] + chr((ord(salt[-1]) + 1) % 256)
                hashed = self.encryptor.hash(self.password, salt)
                self._write(hashed)
                phase += 1

            else:
                return True

            time.sleep(self.HANDSHAKE_SLEEP_TIME)

        return False

