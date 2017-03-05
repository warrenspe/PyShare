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
import Tkinter
import time
import socket
import traceback
import logging

# Project imports
from utils.gui.loginFrame import LoginFrame
from utils.gui.chatFrame import ChatFrame
from utils.cache import ClientCache
from utils import config
from utils import constants
from utils.stockings.client import ClientStocking
from utils.crypto.rsa_aes import RSA_AES

class ServerComm(object):
    """ Manages communication with the server. """

    # A stocking to use to communicate with the server
    conn = None
    crypto = None
    handlers = None
    fMgr = None
    authenticating = False

    def __init__(self, fMgr):
        self.crypto = RSA_AES()
        self.handlers = dict()
        self.fMgr = fMgr

    def sendServerMessage(self, **kwargs):
        """
        Sends the server a message.

        Inputs: kwargs - Keyword arguments corresponding to __init__ parameters of utils.message.CryptoMessage.
        """

        self.conn.write(**kwargs)

    def handleServerMessage(self, message):
        """
        Dispatches a server message to an appropriate handler.

        Inputs: message - The CryptoMessage object received from the server.
        """

        if message.action in self.handlers:
            self.handlers[message.action](message)

        else:
            logging.debug("Message with unknown action received: %s" % message.action)

    def registerHandler(self, action, callback):
        """
        Registers a function to be called when a message from the server is received.

        Inputs: action   - The CryptoMessage action of the server's message.
                callback - The callback to call when a message having this action is received.  The callback function
                           should accept a single parameter, being the CryptoMessage that was received.
        """

        self.handlers[action] = callback

    def authenticate(self, username, password):
        """
        Attempts to authenticate with the server.

        Inputs: username - The username we'd like to register with
                password - The password of the server.

        Outputs: A boolean indicating if authentication was successful.
        """

        def _authenticateInner(startTime):
            """
            Callback function which repeatedly calls itself until either we authenticate with the server, fail to
            authenticate with the server, or run out of time authenticating with the server.

            Inputs: startTime - A unix timestamp of when we started authenticating with the server.
            """

            if self.conn.handshakeComplete:
                self.fMgr.showChat()

            else:
                if not self.conn.active:
                    errorMsg = "Invalid Credentials"

                elif (time.time() - startTime) > constants.MAX_CLIENT_AUTH_WAIT_TIME:
                    errorMsg = "Authentication timeout."

                else:
                    count = (int(time.time()) % 3) + 1
                    messageStr = "%s%s %s" % (" " * count, self.conn.phaseStr, "." * count)
                    self.fMgr.currentFrame.showMessage(messageStr, False)
                    self.fMgr.widget.after(constants.CLIENT_POLL_FREQ, _authenticateInner, startTime)
                    return

                self.fMgr.currentFrame.showMessage(errorMsg, color="red")
                self.fMgr.currentFrame.setButtonState(Tkinter.NORMAL)

            self.authenticating = False

        # Dont double up on authentication attempts - only do them one at a time
        if self.authenticating:
            return

        try:
            self.authenticating = True
            self.conn = ClientStocking(username, password, self.crypto)

        except socket.error:
            error = "Unable to reach server at: %s:%s" % (self.fMgr.config.server_ip, self.fMgr.config.server_port)
            self.fMgr.currentFrame.showMessage(error, color="red")
            self.fMgr.currentFrame.setButtonState(Tkinter.NORMAL)
            self.authenticating = False
            return False

        _authenticateInner(int(time.time()))

    def beginPolling(self):
        """ Begins a recurring function loop which checks if we have received any messages from the server. """

        message = self.conn.read()
        if message:
            try:
                self.handleServerMessage(message)
            except:
                logging.debug(traceback.format_exc())

        self.fMgr.widget.after(constants.CLIENT_POLL_FREQ, self.beginPolling)


class FrameManager(object):
    """ Class which controls which frames are shown when. """

    widget = None
    currentFrame = None
    serverComm = None
    config = None

    def __init__(self, root):
        self.widget = root
        self.serverComm = ServerComm(self)
        self.config = config.client()
        self.cache = ClientCache()

        # Create the initial login frame, which will take care of the rest
        self.showLogin()

        self.widget.mainloop()

    def showLogin(self):
        self.currentFrame = LoginFrame(self)

    def showChat(self):
        self.currentFrame.destroy()

        self.currentFrame = ChatFrame(self)


def main():
    try:
        root = Tkinter.Tk()

        # Always expand the root window as the window grows and shrinks
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(0, weight=1)
        root.minsize(width=500, height=200)
        root.wm_title("CryptoChat")

        fMgr = FrameManager(root)

    finally:
        try:
            root.destroy()

        except:
            pass

if __name__ == '__main__':
    main()
