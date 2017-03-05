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
from .. import CryptoFrameABC
from .username import Username
from .password import Password
from .submit import Submit
from .message import Message

class LoginFrame(CryptoFrameABC):
    """
    Class which encapsulates the login interface displayed to the user.
    """

    childClasses = {
        'username': Username,
        'password': Password,
        'submit': Submit,
        'message': Message,
    }

    def position(self):
        self.widget.grid(sticky=Tkinter.N+Tkinter.E+Tkinter.S+Tkinter.W)

        # Initialize grid layout
        self.widget.grid_columnconfigure(0, weight=1)
        self.widget.grid_columnconfigure(1, weight=0)
        self.widget.grid_columnconfigure(2, weight=1)
        self.widget.grid_rowconfigure(0, weight=1)
        self.widget.grid_rowconfigure(1, weight=1)

    def afterFrameInit(self):
        self.children['username'].children['usernameEntry'].widget.focus_set()

    def submitCredentials(self):
        username = self.children['username'].getUsername()
        password = self.children['password'].getPassword()

        self.setButtonState(Tkinter.DISABLED)
        self.serverComm.authenticate(username, password)

    def showMessage(self, *args, **kwargs):
        """ Simple wrapper for our Message widget's setMessage function. """

        self.children['message'].setMessage(*args, **kwargs)

    def setButtonState(self, state):
        """
        Simple wrapper for setting the state of our Submit button widget.

        state - A Tkinter state depicting what state we should set the button to.
                (Tkinter.NORMAL, Tkinter.DISABLED)
        """

        self.children['submit'].widget.configure(state=state)
