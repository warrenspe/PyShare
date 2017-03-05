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
from .. import CryptoWidgetABC, CryptoFrameABC


class _UsernameEntry(CryptoWidgetABC):
    """ Class representing the actual username entry widget. """

    controlVariableClass = Tkinter.StringVar
    controlVariableOptionName = 'textvariable'
    widgetClass = Tkinter.Entry
    options = {
        'width': MAX_USERNAME_LEN
    }

    def before(self):
        def limit(action):
            if len(self.widget.get()) >= MAX_USERNAME_LEN and action == '1':
                self.widget.bell()
                return False
            return True

        limit = (self.parentWidget.register(limit), "%d")
        self.options['validatecommand'] = limit
        self.options['validate'] = 'key'

    def after(self):
        self.widget.bind("<KP_Enter>", lambda _: self.parent.parent.submitCredentials())
        self.widget.bind("<Return>", lambda _: self.parent.parent.submitCredentials(), "+")

    def position(self):
        self.widget.grid(sticky=Tkinter.S+Tkinter.N+Tkinter.E+Tkinter.W)



class Username(CryptoFrameABC):
    """
    Class which encapsulates logic relating to the username box of the login page.
    """

    widgetClass = Tkinter.LabelFrame
    childClasses = {'usernameEntry': _UsernameEntry}
    options = {
        'text': 'Username',
        'borderwidth': 0
    }

    def position(self):
        self.widget.grid(column=0, row=0, sticky=Tkinter.E+Tkinter.S)

    def redraw(self):
        pass

    def getUsername(self):
        """
        Returns the entered username.

        Outputs: A string containing the entered username.
        """

        return self.children['usernameEntry'].controlVariable.get()
