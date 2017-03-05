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
from ...message import CryptoMessage

class Message(CryptoWidgetABC):
    """
    Class which encapsulates logic relating to the message history section.
    """

    widgetClass = Tkinter.Text
    options = {
        'state': 'disabled',
    }

    def position(self):
        self.widget.grid(column=1, row=0, sticky=Tkinter.N+Tkinter.E+Tkinter.S+Tkinter.W)

    def redraw(self):
        pass

    def writeMessages(self, messages):
        """
        Writes a message to the buffer

        Inputs: messages - A sequence of CryptoChat.utils.message.CryptoMessage objects to write to the screen.
        """

        if isinstance(messages, CryptoMessage):
            messages = [messages]

        self.widget.configure(state=Tkinter.NORMAL)
        for message in messages:
            if message.flags & CryptoMessage.MOD_PRINT:
                self.widget.insert(Tkinter.END, message.format(self.cache))
        self.widget.configure(state=Tkinter.DISABLED)
