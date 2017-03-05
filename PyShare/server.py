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
import time
import socket
import errno
import select
import traceback
import logging

# Project imports
from utils import config
from utils.stockings.server import ServerStocking
from utils.message import CryptoMessage
from utils.cache import ServerCache
from utils.crypto.rsa_aes import RSA_AES

if not hasattr(select, 'poll'):
    raise Exception("CryptoServer must be run on a system with poll capabilities (typically linux systems).")

logging.basicConfig(filename='CryptoServer.log',level=logging.INFO)

class CryptoServer(object):
    """ Class which accepts connections and handles redistributing messages from clients to other clients. """

    # hconf.Config object containing configuration directives
    config = None
    # Server socket to handle communication with clients
    serverSocket = None
    # Address to bind the server to
    addr = None
    # Password clients must provide in order to connect to the server
    password = None
    # select.poll object to manage connections
    poller = None
    # ServerCache object to maintain information about connected clients
    cache = None
    # Counter to prevent userID/roomID conflicts
    uniqueIDIncrementor = 1

    def __init__(self):
        self.config = config.server()

        self.addr = (self.config.server_ip, self.config.server_port)
        self.poller = select.poll()

        self.cache = ServerCache()

        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setblocking(0)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind(self.addr)
        self.serverSocket.listen(5)
        self.poller.register(self.serverSocket, select.POLLIN)
        logging.info("Server starting on %s:%s" % self.addr)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _getUniqueID(self):
        uniqueID = self.uniqueIDIncrementor
        self.uniqueIDIncrementor += 1
        return uniqueID

    def close(self):
        logging.info("Server shutting down!")

        self.serverSocket.close()
        for session in self.cache.authenticated.values() + self.cache.unauthenticated.values():
            session.close()

    def sendRoomMessage(self, message):
        """
        Sends a message posted to a room.

        Inputs: message - An instance of utils.message.CryptoMessage containing the data to send.
        """

        for session in self.cache.usersInRoom(message.recipient_id):
            session.write(**dict(message))

    def sendUserMessage(self, message):
        """
        Sends a private message from one user to another.

        Inputs: message - An instance of utils.message.CryptoMessage containing the data to send.
        """

        if message.recipient_id in self.cache.authenticated:
            session = self.cache.authenticated[message.recipient_id]
            session.write(**dict(message))

    def broadcast(self, fromUserID, action=CryptoMessage.MESSAGE, msg=None, flags=CryptoMessage.MOD_PRINT):
        """
        Sends a message to all authenticated users.

        Inputs: fromUserID - The userID of the user who sent the message.
                action     - The action flag to associate with the message.
                msg        - The contents of the message.
                flags      - The flags to associate with the message.
        """

        for session in self.cache.authenticated.values():
            session.write(
                sender_id=fromUserID,
                recipient_id=session.userID,
                send_time=int(time.time()),
                action=action,
                data=msg,
                flags=flags
            )

    def disconnect(self, session):
        """ Disconnects a connected session. """

        logging.info("Disconnecting %s:%s" % session.addr)

        # Remove the session from our cache
        self.cache.removeUser(session.userID)

        # Inform other clients that this client has disconnected
        self.broadcast(session.userID, CryptoMessage.LOGOUT)

    def createNewSessions(self):
        """ Spawns new ServerStocking instances from our server socket. """

        try:
            # Accept each waiting connection
            while True:
                conn, addr = self.serverSocket.accept()

                # If this address has already connected, remove it from our sessions
                for session in self.cache.userDict.values():
                    if session.addr == addr:
                        self.disconnect(session)
                        logging.info("Disconnecting %s:%s due to address conflict." % addr)

                # Connect the new session, and add to self.handshaking
                userID = self._getUniqueID()
                session = ServerStocking(conn, userID, RSA_AES())
                self.cache.newUser(session)

                logging.info("%s:%s Has connected." % addr)

        except socket.error as e:
            # Only mask EAGAIN errors
            if e.errno != errno.EAGAIN:
                raise

    def removeInactiveConnections(self):
        """ Removes inactive unauthenticated connections. """

        for session in self.cache.unauthenticated.values():
            if int(time.time()) - session.connectionTime > self.config.inactive_disconnect_period or not session.active:
                self.cache.removeUser(session.userID)

        disconnected = False

        for session in self.cache.authenticated.values():
            if not session.active:
                disconnected = True
                self.disconnect(session)

        if disconnected:
            self.pushCacheUpdates()

    def authenticateConnections(self):
        """ Authenticates connections which have successfully logged in. """

        newSession = False

        for session in self.cache.unauthenticated.values():
            if session.handshakeComplete:
                newSession = True
                self.cache.authenticate(session.userID)
                self.poller.register(session.sock.fileno(), select.POLLHUP)
                self.poller.register(session.fileno(), select.POLLIN)

        if newSession:
            self.pushCacheUpdates()

    def pushCacheUpdates(self):
        """ Refreshes all clients local caches. """

        data = self.cache.toString()

        for session in self.cache.authenticated.values():
            session.write(
                action = CryptoMessage.CACHE_REFRESH,
                data = data,
                flags = 0
            )

    def processMessage(self, session, message):
        """
        Processes a message sent from a client.

        Inputs: session - The ServerStocking object that the message originated from.
                message - A utils.message.CryptoMessage instance containing the contents of the message.
        """

        # Assign sender_id automatically
        message.sender_id = session.userID

        # Handle logouts
        if message.action == message.ERROR:
            self.disconnect(session)

        # Handle distribution of messages
        elif message.action == message.MESSAGE:
            # Find the recipient of this message
            if message.recipient_id in self.cache.roomDict:
                self.sendRoomMessage(message)
            elif message.recipient_id in self.cache.authenticated:
                self.sendUserMessage(message)

        # Handle new room creation
        elif message.action == message.CREATE_ROOM:
            roomID = self._getUniqueID()
            self.cache.newRoom(roomID, message.data)
            self.cache.joinRoom(message.sender_id, roomID)

        # Handle a user joining a room
        elif message.action == message.JOIN_ROOM:
            self.cache.joinRoom(message.sender_id, roomID)
            self.sendRoomMessage(message)

        # Handle a user leaving a room
        elif message.action == message.LEAVE_ROOM:
            self.cache.leaveRoom(message.sender_id, roomID)
            self.sendRoomMessage(message)

        # If someone entered/left/created a room, the clients will need to have their local caches updated
        if message.action in (message.CREATE_ROOM, message.JOIN_ROOM, message.LEAVE_ROOM):
            self.pushCacheUpdates()


    def loop(self):
        """ Main handler. """

        try:
            while True:
                for fd, eventMask in self.poller.poll(3):
                    logging.debug("Event (%s): %s" % (fd, eventMask))

                    # If a connection has disconnected, disconnect it
                    if eventMask & select.POLLHUP:
                        # If this connection is not in the cache, ignore this input
                        session = self.cache.sockDict.get(fd, None)
                        if not session:
                            logging.debug("Cannot disconnect %s; unknown connection" % fd)
                            continue
                        self.disconnect(session)

                    # If we have input to process
                    elif eventMask & select.POLLIN:
                        # If the fd is our serverSocket, accept new connections
                        if fd == self.serverSocket.fileno():
                            self.createNewSessions()

                        # Otherwise it is from one of our sessions

                        # Ensure we have a corresponding session
                        elif fd not in self.cache.sessionDict:
                            self.poller.unregister(fd)
                            logging.error("%s is not in server cache!! Unregistered from poller." % fd)

                        # Otherwise process any messages this session's sent
                        else:
                            try:
                                session = self.cache.sessionDict[fd]
                                self.processMessage(session, session.read())

                            except:
                                logging.error(traceback.format_exc())

                # Remove inactive connections
                self.removeInactiveConnections()

                # Authenticate connections finished handshaking
                self.authenticateConnections()

                # Process connections waiting to authenticate
                for session in self.cache.unauthenticated.values():
                    logging.debug("Checking if %s has finished authenticating" % session)
                    if session.handshakeComplete:
                        self.cache.authenticate(session)

        except KeyboardInterrupt:
            logging.info("Interrupt caught. Exiting...")

        finally:
            self.close()



if __name__ == '__main__':
    try:
        with CryptoServer() as server:
            server.loop()
    except:
        traceback.print_exc()
        logging.error(traceback.format_exc())
    finally:
        logging.info("CryptoServer has successfully shut down.")
