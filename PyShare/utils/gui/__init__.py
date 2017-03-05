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
import abc

class CryptoWidgetABC(object):
    """ Base class for CryptoChat GUI Widgets. """

    __metaclass__ = abc.ABCMeta

    # Parent of this widget
    parent = None
    # Widget of the parent of this widget
    parentWidget = None
    # The type of widget to initialize
    widgetClass = None
    # The widget itself
    widget = None
    # Any options to set on the widget on initialization
    options = dict()
    # A controlvariable to set on the widget
    controlVariableClass = None
    # The name of the option to set the control variable as
    controlVariableOptionName = None
    # The controlVariable set on the widget, if controlvariableClass is not None
    controlVariable = None
    # A client.ServerComm object which is capable of interacting with the server.
    serverComm = None
    # A ClientConfig object containing configuration directives
    config = None
    # A utils.cache.ClientCache object used to record data sent from the server
    cache = None

    def __init__(self, parent):
        self.parent = parent
        self.parentWidget = self.parent.widget
        self.serverComm = self.parent.serverComm
        self.config = self.parent.config
        self.cache = self.parent.cache

        if self.controlVariableClass:
            self.controlVariable = self.controlVariableClass()
            self.options[self.controlVariableOptionName] = self.controlVariable

        self.before()

        self.widget = self.widgetClass(self.parentWidget, **self.options)

        self.position()

        self.after()

    @abc.abstractmethod
    def position(self):
        """ Positions the widget in the parent frame using the grid method. """

        raise NotImplementedError()

    def redraw(self):
        """ Redraw the element on the screen. """

        pass # TODO?

    def before(self):
        """ Performs any additional setup required before the widget is initialized. """

        pass

    def after(self):
        """ Performs any additional setup required before the widget is initialized. """

        pass

    def destroy(self):
        self.widget.destroy()


class CryptoFrameABC(CryptoWidgetABC):
    """ Base class for CryptoChat GUI Frames, which contain other CryptoWidgets. """

    __metaclass__ = abc.ABCMeta

    widgetClass = Tkinter.Frame

    # A dictionary mapping the names of the child widgets of this frame to the class of the widget.
    # Used to populate children
    childClasses = None
    # A dictionary mapping the names of the child widgets of this frame to the widget itself
    children = None

    def __init__(self, parent):
        super(CryptoFrameABC, self).__init__(parent)

        self.children = {name: childClass(self) for name, childClass in self.childClasses.items()}

        self.redraw()

        self.afterFrameInit()

    def afterFrameInit(self):
        """ Functions to perform after the frame has been initialized. """

        pass

    def redraw(self):
        """ Redraws the frame in its entirety. """

        for child in self.children.values():
            child.redraw()

    def destroy(self):
        for child in self.children.values():
            child.destroy()
        self.widget.destroy()


class CryptoElementList(CryptoFrameABC):
    """ Class which allows for a series of selectable items to be stored within it in a column. """

    childClasses = dict()
    defaultOptions = {
        'justify': Tkinter.CENTER,
    }

    def addEntry(self, entryID, entryText, callback, **options):
        """
        Adds a new entry (Label widget) to this list.

        Inputs: entryID   - The unique ID to associate with the entry
                entryText - The text to display to the user in the entry
                callback  - A callback to be fired when the entry is clicked.
                                Should accept the entry as its first and only parameter.
                options   - Any additional options to pass to the initializer for the new Label widget
        """

        widgetOptions = self.defaultOptions.copy()
        widgetOptions['text'] = entryText
        widgetOptions.update(options)
        entry = Tkinter.Label(self.widget, **widgetOptions)
        entry.bind("<Button-1>", callback)
        entry.entryID = entryID
        key = (max(self.children.values()) if self.children else 0) + 1
        self.children[key] = entry

        entry.grid(column=0, row=len(self.children), sticky=Tkinter.E+Tkinter.W)
