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

class _PasswordEntry(CryptoWidgetABC):
    """ Class representing the actual password entry widget. """

    controlVariableClass = Tkinter.StringVar
    controlVariableOptionName = 'textvariable'
    widgetClass = Tkinter.Entry
    options = {
        'width': MAX_USERNAME_LEN,
        'show': '*'
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

        self.controlVariable = Tkinter.StringVar()
        self.options['textvariable'] = self.controlVariable

    def after(self):
        self.widget.bind("<KP_Enter>", lambda _: self.parent.parent.submitCredentials())
        self.widget.bind("<Return>", lambda _: self.parent.parent.submitCredentials(), "+")

    def position(self):
        self.widget.grid(sticky=Tkinter.S+Tkinter.N+Tkinter.E+Tkinter.W)


class Password(CryptoFrameABC):
    """ Class representing the label and password entry widgets. """

    widgetClass = Tkinter.LabelFrame
    childClasses = {'passwordEntry': _PasswordEntry}
    options = {
        'text': 'Password',
        'borderwidth': 0
    }

    def position(self):
        self.widget.grid(column=1, row=0, sticky=Tkinter.S, padx=4)

    def redraw(self):
        pass

    def getPassword(self):
        """
        Returns the entered password.

        Outputs: A string containing the entered password.
        """

        return self.children['passwordEntry'].controlVariable.get()
