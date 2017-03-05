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

# Project imports
from .. import CryptoFrameABC
from .composer import Composer
from .search import Search
from .message import Message
from .users import Users

from ...message import CryptoMessage
from ... import constants

class ChatFrame(CryptoFrameABC):
    """
    Class which encapsulates the chatting interface displayed to the user.
    """

    # ID of the room we're currently viewing
    room = None

    childClasses = {
        'composer': Composer,
        'search': Search,
        'message': Message,
        'users': Users
    }

    def position(self):
        self.widget.grid(sticky=Tkinter.N+Tkinter.E+Tkinter.S+Tkinter.W)

        # Initialize grid layout
        self.widget.grid_columnconfigure(1, weight=1)
        self.widget.grid_rowconfigure(0, weight=8)
        self.widget.grid_rowconfigure(1, weight=1)

    def afterFrameInit(self):
        self.serverComm.registerHandler(CryptoMessage.MESSAGE, self.children['message'].writeMessages)
        self.serverComm.registerHandler(CryptoMessage.ERROR, self.children['message'].writeMessages) #TODO - add err stuff
        self.serverComm.registerHandler(CryptoMessage.CACHE_REFRESH, self.updateCache)
        self.serverComm.registerHandler(CryptoMessage.LOGOUT, self.handleLogout)
        self.serverComm.beginPolling()

    def updateCache(self, message):
        """
        Updates the cache object initialized from the server.

        Inputs: message - The CryptoMessage object received from the server containing the data to refresh the cache.
        """

        self.cache.fromString(message.data)

        self.children['users'].redraw()

    def handleLogout(self, message):
        """
        Updates the cache object and sends a message to each chat room including that user we have open.

        Inputs: message - The CryptoMessage object received from the server containing the user who logged out.
        """

        pass # TODO

    def sendMessage(self, message):
        """
        Sends a message to the server from the current room.

        Inputs: message - The contents of the message to send.
        """

        if self.room:
            self.serverComm.sendServerMessage(
                recipient_id=self.room,
                send_time=int(time.time()),
                action=CryptoMessage.MESSAGE,
                data=message,
                flags=CryptoMessage.MOD_PRINT
            )

    def switchChat(self, chatID):
        """ Opens the user/room chat specified by chatID. """

        if chatID in self.cache.roomDict:
            self.room = chatID # TODO
        elif chatID in self.cache.userDict:
            self.room = chatID # TODO
