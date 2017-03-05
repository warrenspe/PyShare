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
from Cryptodome.PublicKey import RSA
from Cryptodome.PublicKey import pss
from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.Hash import SHA512

# Project imports
import kimchi

class RSA_AES(object):
    """
    Class encapsulating an encryption/verification protocol which takes place over three phases:
        1. Key exchange - Both endpoints exchange a public key with the other in order to validate each others identity
                          and set up symmetric encryption between them.
        2. Authentication - Both endpoints sign a shared secret to validate each other's identity.
        3. Setup Symmetric Crypto - Both endpoints encrypt and share a symmetric key using the other side's public key.
        3. AES Encrypted Communication - Both sides use the symmetric key to initialize a block cipher in OCB mode to
                                         communicate.

    Example:
        >>> alice=pk.PK() TODO
        >>> bob=pk.PK()
        >>> publicKey = alice.generatePublicKey()
        >>> symmetricKey = bob.registerPublicKey(publicKey)
        >>> alice.registerEncryptedSymmKey(symmetricKey)
        >>> cipherText = alice.encrypt('...')
        >>> bob.decrypt(cipherText)
    """

    # Private key used to decrypt messages and sign hashes
    priv = None
    # Public key counterpart of our private key
    pub = None
    # Remote's public key used to encrypt messages and verify hash signatures
    remotePub = None
    # Our symmetric key, used to encrypt messages sent to the remote
    symm = None
    # The remote's symmetric key, used to decrypt messages sent by the remote
    remoteSymm = None
    # nonce used to initialize the cipher.  Must not repeat.
    nonce = 0

    # Maximum number of bits that can be transferred with this cipher before it begins to lose its security
    BYTE_TRANSFER_LIMIT = 2**52 # TODO

    ###
    # Handshake functions
    ###
    def generatePublicPrivateKeys(self):
        """
        Generates an RSA private key which can be used to sign messages and decrypt messages encrypted with its
        public key.  Also generates the private key's public key counterpart.
        """

        self.priv = RSA.generate(1024) # TODO 3072
        self.pub = self.priv.publickey()

    def exportPublicKey(self):
        """
        Returns this connection's public key in a binary format which can be used by the remote endpoint.

        Outputs: A string containing this connections public key in DER format.
        """

        return self.pub.exportKey(format="DER")

    def registerPublicKey(self, key):
        """
        Registers the remote endpoint's public key so it can be used to encrypt messages to it/verify signatures.

        Inputs: key - A string containing the remote endopint's public key.
        """

        self.remotePub = RSA.import_key(key)

    def generateSymmetricKey(self):
        """ Generates a symmetric key which can be used with a block cipher. """

        self.symm = self.randomBytes(32)

    def exportSymmetricKey(self):
        """
        Returns our symmetric key, encrypted using the endpoint's public key.

        Outputs: A string containing our symmetric key encrypted using the remote's public key.
        """

        cipher = PKCS1_OAEP.new(self.remotePub)
        return cipher.encrypt(self.symm)

    def generateAuthenticationToken(self, pwd):
        """
        Generates a token which can be used by the remote endpoint to verify that the endpoint it is communicating with
        is the same endpoint that it has the public key for.  Also validates that both endpoints know the same secret
        password.  This is immune to man in the middle attacks, because for a MITM attack to be successfully carried
        out both sides would have to be connected to it, but since it doesn't know either side's private key it will be
        unable to sign the password which it does not know.

        Inputs: pwd - The password to sign using our private key.

        Outputs: A string containing the signature and salt of the hashed password.
        """

        salt = self.randomBytes(32)
        hashed = self.hash(pwd, salt)
        signature = pss.new(self.priv).sign(hashed)

        return kimchi.dumps((signature, salt))

    def validateAuthenticationToken(self, pwd, token):
        """
        Validates an authentication token from the remote endpoint.  This ensures that the host whose public key we
        have is the same host that knows the shared password.

        Inputs: pwd -   The shared password to validate.
                token - The authentication token, generated by the remote.

        Outputs: A boolean indicating whether or not the given token is authentic and valid.
        """

        try:
            signature, salt = kimchi.loads(token)
            hashed = self.hash(pwd, salt)
            pss.new(self.remotePub).verify(hashed, signature)

            return True

        except (ValueError, TypeError, OverflowError):
            return False

    ###
    # Crypto functions
    ###
    def encrypt(self, plaintext):
        """
        Encrypts a given plaintext.

        Inputs: The plaintext to encrypt.  Should be a string.

        Outputs: A string which can be passed to the remote endpoint to be decrypted.

        Notes: This function can raise a ReAuthenticateException indicating that authentication should be renegotiated
               This is because after a certain number of bytes have been transferred the cipher loses its security.
        """

        self.nonce += 2
        cipher = AES.new(self.symm, AES.MODE_OCB, nonce=str(self.nonce))
        ciphertext, mac = cipher.encrypt_and_digest(plaintext)
        return kimchi.dumps((ciphertext, mac, str(self.nonce)))

    def decrypt(self, cipherPacket):
        """
        Decrypts a given kimchi-bundled cipher packet.

        Inputs: cipherPacket - A kimchi dumped tuple containing the ciphertext, mac, and nonce to use for decryption.

        Outputs: The decrypted message.

        Notes: This function can raise a ValueError or OverflowError if the ciphertext is invalid.
               This function can also raise a ReAuthenticateexception if we need to re-authenticate with the endpoint.
        """

        ciphertext, mac, nonce = kimchi.loads(cipherPacket)
        cipher = AES.new(self.symm, AES.MODE_OCB, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, mac)

    def hash(self, plaintext, salt):
        """
        Hashes the plaintext using the given salt.

        Inputs: plaintext - The text to hash.
                salt      - The salt to use in the hash.

        Outputs: The hashed value of the plaintext.
        """

        hashObj = SHA512.new()
        hashObj.update(plaintext)
        hashObj.update(salt)
        return hashObj.digest()

    def randomBytes(self, numBytes):
        """
        Returns a string containing the number of random bytes specified.

        Inputs: numBytes - An integer specifying how many bytes should be contained in the random number generated.

        Outputs: The random number generated.
        """

        return get_random_bytes(numBytes)
