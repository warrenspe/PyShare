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
import hconf

# Client configs
_CLIENT = (

)

# Server configs
_SERVER = (
    # Socket & Authentication configuration directices
    {
        'name': 'server_name',
        'required': True,
        'description': 'IP address/DNS hostname where the server is located.'
    },
    {
        'name': 'server_port',
        'required': True,
        'default': 16482,
        'cast': int,
        'description': 'Port the server is bound to.'
    }
    {
        'name': 'server_password',
        'required': True,
        'description': 'Password to require clients to provide in order to authenticate with the server',
        'default': '',
    },

    # File/Directory configuration directives
    {
        'name': 'upload_dir',
        'required': False,
        'description': 'Path to the directory to store uploaded files at. If not given, uploads will not be permitted.',
    },
    {
        'name': 'file_ledger_path',
        'required': True,
        'description': 'Path to the file ledger, containing a listing of all the files which can be served to peers.',
    },
)

_SERVER_CONFIG = None
_CLIENT_CONFIG = None

def server():
    global _SERVER_CONFIG

    if not _SERVER_CONFIG:
        configMgr = hconf.ConfigManager(*_SERVER)
        configMgr.registerParser(hconf.Subparsers.Cmdline("CryptoChat Server"))
        _SERVER_CONFIG = configMgr.parse()

    return _SERVER_CONFIG


def client():
    global _CLIENT_CONFIG

    if not _CLIENT_CONFIG:
        configMgr = hconf.ConfigManager(*_CLIENT)
        configMgr.registerParser(hconf.Subparsers.Cmdline("CryptoChat Client"))
        _CLIENT_CONFIG = configMgr.parse()

    return _CLIENT_CONFIG
