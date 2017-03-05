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
from .. import CryptoWidgetABC, CryptoFrameABC

class _ComposerBox(CryptoWidgetABC):
    """ Class which encapsulates logic relating to the composer section. """

    widgetClass = Tkinter.Text
    options = {
        'height': 6,
    }

    def position(self):
        self.widget.grid(column=0, row=0, sticky=Tkinter.N+Tkinter.E+Tkinter.S+Tkinter.W)

    def redraw(self):
        pass

    def popMessage(self):
        """
        Clears the message box returning the input message.

        Outputs: The string which was previously entered into the composer.
        """

        text = self.widget.get("1.0", Tkinter.END)
        self.widget.delete("1.0", Tkinter.END)
        return text


class _Send(CryptoWidgetABC):
    """ Class which encapsulates logic relating to the send message button. """

    widgetClass = Tkinter.Button
    options = {
        'text': 'Send',
    }

    def position(self):
        self.widget.grid(column=1, row=0, sticky=Tkinter.N+Tkinter.E+Tkinter.S+Tkinter.W)

    def before(self):
        self.options['command'] = self.parent.sendMessage


class Composer(CryptoFrameABC):
    """ Class which encapsulates both the SearchBox and SearchList. """

    childClasses = {
        'composer': _ComposerBox,
        'send': _Send
    }

    def position(self):
        self.widget.grid(column=1, row=1, columnspan=2, sticky=Tkinter.N+Tkinter.E+Tkinter.S+Tkinter.W)

        # Initialize grid layout
        self.widget.grid_columnconfigure(0, weight=1)
        self.widget.grid_rowconfigure(1, weight=1)

    def sendMessage(self):
        """ Sends a message to the server. """

        message = self.children['composer'].popMessage().rstrip('\n')
        if message:
            self.parent.sendMessage(message)
