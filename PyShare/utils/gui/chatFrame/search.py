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
import re

# Project imports
from ...constants import MAX_USERNAME_LEN
from .. import CryptoWidgetABC, CryptoFrameABC, CryptoElementList

class _SearchBox(CryptoWidgetABC):
    """ Class which encapsulates logic relating to searching for users/rooms. """

    widgetClass = Tkinter.Entry
    controlVariableOptionName = 'textvariable'
    options = {
        'width': MAX_USERNAME_LEN,
    }

    def position(self):
        self.widget.grid(column=0, row=0, sticky=Tkinter.N+Tkinter.E+Tkinter.S+Tkinter.W)

    def before(self):
        def limit(action):
            if len(self.widget.get()) >= MAX_USERNAME_LEN and action == '1':
                self.widget.bell()
                return False
            return True

        limit = (self.parentWidget.register(limit), "%d")
        self.options['validatecommand'] = limit
        self.options['validate'] = 'key'

        self.controlVariable = Tkinter.StringVar()
        self.options['textvariable'] = self.controlVariable

    def after(self):
        self.widget.bind("<Return>", self.parent.search)
        self.widget.bind("<KP_Enter>", self.parent.search, "+")


class _SearchList(CryptoElementList):
    """
    Class which encapsulates logic relating to the user/group list section searching/selection.

    Is populated when a search query is entered, and displays rooms we are currently participating in when one isn't.
    """

    options = {
        'width': MAX_USERNAME_LEN,
    }

    def position(self):
        self.widget.grid(column=0, row=1, sticky=Tkinter.N+Tkinter.E+Tkinter.S+Tkinter.W)
        self.widget.grid_columnconfigure(0, weight=1)

    def redraw(self):
        pass

    def entryCallback(self, event):
        """
        Callback which is called when one of the room/user entries is clicked on.

        Inputs: entry - An event object containing the entry that was clicked.
        """

        self.parent.parent.switchChat(event.widget.entryID)


class Search(CryptoFrameABC):
    """ Class which encapsulates both the SearchBox and SearchList. """

    childClasses = {
        'searchBox': _SearchBox,
        'searchList': _SearchList
    }

    def position(self):
        self.widget.grid(column=0, row=0, rowspan=2, sticky=Tkinter.N+Tkinter.E+Tkinter.S+Tkinter.W)

        # Initialize grid layout
        self.widget.grid_columnconfigure(0, weight=1)
        self.widget.grid_rowconfigure(1, weight=1)

    def search(self, _):
        """
        Performs a search of the rooms/users that match the given search criteria.  Displays the list in the
        search list.
        """

        query = self.children['searchBox'].controlVariable.get()

        toSearch = []
        for roomID, roomTuple in self.cache.roomDict.items():
            toSearch.append((roomID, roomTuple[0]))
        for userID, userName in self.cache.userDict.items():
            toSearch.append((userID, userName))

        for objID, objName in sorted(toSearch, key=lambda x: x[1]):
            if re.search(query, objName):
                self.children['searchList'].addEntry(objID, objName, self.children['searchList'].entryCallback)
