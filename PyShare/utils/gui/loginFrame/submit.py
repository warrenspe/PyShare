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

class Submit(CryptoWidgetABC):
    """
    Class which encapsulates logic relating to the login submit button.
    """

    widgetClass = Tkinter.Button
    options = {
        'height': 1,
        'width': 6,
        'text': 'Submit'
    }

    def position(self):
        self.widget.grid(column=2, row=0, sticky=Tkinter.S+Tkinter.W)

    def before(self):
        self.options['command'] = self.submit

    def after(self):
        self.widget.bind("<KP_Enter>", lambda _: self.submit())
        self.widget.bind("<Return>", lambda _: self.submit(), "+")

    def redraw(self):
        pass

    def submit(self):
        """ Submits the user's credentials to the server. """

        self.parent.submitCredentials()
