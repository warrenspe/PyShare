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

# Project imports
from ...constants import MAX_USERNAME_LEN
from .. import CryptoElementList

class Users(CryptoElementList): # TODO either dont display us, or dont allow us to talk to ourselves
    """ Class which encapsulates logic relating to displaying the list of users in a room. """

    def entryCallback(self, entry):
        """
        Callback which is called when one of the user entries is clicked on.

        In this case, we want to load up any pre-existing, or create a new chat with that user.

        Inputs: entry - The Label widget object that was clicked on.
        """

        pass # TODO

    def _addUser(self, userID):
        """ Adds a user to the list. """

        if userID not in self.parent.cache.userDict:
            return

        userName = self.parent.cache.userDict[userID]

        self.addEntry(userID, userName, self.entryCallback, **{
            'width': MAX_USERNAME_LEN
        })

    def redraw(self):
        # Get the current room number
        room = self.parent.room

        # Generate the list of users
        if room not in self.parent.cache.roomDict:
            self.hide()
            return

        self.position()
        for user in self.parent.cache.roomDict[room][1]:
            self._addUser(user)

    def hide(self):
        self.widget.grid_forget()

    def position(self):
        self.widget.grid(column=2, row=0, sticky=Tkinter.N+Tkinter.E+Tkinter.S+Tkinter.W)
