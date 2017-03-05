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
import socket
import time
import kimchi

# Project imports
from . import _Stocking
from .. import config


class ClientStocking(_Stocking):
    """ Class which subclasses a Stocking to send and recv messages to and from a PyShare Server. """

    # Password of the server we're connecting to
    password = None
    # Time the connection was established
    connectionTime = None
    # Human readable string of the status of the authentication, used to keep the user informed of its status
    authStr = "Setting up connection"

    def __init__(self, password, encryptor, conn=None):
        self.password = password
        self.connectionTime = int(time.time())

        conf = config.client()

        if conn is None:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((conf.server_ip, conf.server_port))

        super(self.__class__, self).__init__(conn, encryptor)

    def handshake(self):
        """ Authenticates with the CryptoServer, setting up encryption and giving it our credentials. """

        phase = 1

        while self.active:
            # Phase 1: Create a public key to send to the server
            if phase == 1:
                self.authStr = "Generating Private/Public Key"
                publicKey = self.encryptor.generateClientPublicKey()
                self._write(publicKey)
                phase += 1

            # Phase 2: Decrypt the server's symmetric key
            elif phase == 2:
                self.authStr = "Decrypting Server Key"
                symmKey = self._read()
                if symmKey is not None:
                    self.encryptor.registerEncryptedSymmKey(symmKey)
                    phase += 1

            # Phase 3: Send the server a salt and the hash of the password salted with the salt
            elif phase == 3:
                self.authStr = "Authenticating with the server"
                salt = self.encryptor.randomBytes(64)
                hashed = self.encryptor.hash(self.password, salt)
                self._write(kimchi.dumps((salt, hashed)))
                phase += 1

            # Phase 4: Receive and verify the hash of the password salted with the salt + 1
            elif phase == 4:
                self.authStr = "Verifying the server's identity"
                hashed = self._read()
                if hashed:
                    salt = salt[:-1] + chr((ord(salt[-1]) + 1) % 256)
                    hashed2 = self.encryptor.hash(self.password, salt)
                    if hashed != hashed2:
                        return False

                    phase += 1

            else:
                return True

            time.sleep(self.HANDSHAKE_SLEEP_TIME)

        return False
