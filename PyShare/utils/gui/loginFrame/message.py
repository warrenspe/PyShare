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
from .. import CryptoWidgetABC

class Message(CryptoWidgetABC):
    """
    Class which encapsulates logic relating to displaying login messages to the user.
    """

    controlVariableClass = Tkinter.StringVar
    controlVariableOptionName = 'textvariable'
    widgetClass = Tkinter.Label
    options = {
        'foreground': 'black'
    }

    def position(self):
        self.widget.grid(column=0, row=1, columnspan=3, sticky=Tkinter.E+Tkinter.W+Tkinter.N)

    def redraw(self):
        pass

    def clearMessage(self):
        self.controlVariable.set("")

    def setMessage(self, message, autoClear=True, color="black"):
        self.widget.configure(foreground=color)
        self.controlVariable.set(message)
        if autoClear:
            self.widget.after(4000, self.clearMessage)
