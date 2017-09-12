
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from puckodb.storage import PuckoDbStorage
from puckodb.puckodb import PuckoDb
import json

class PuckoWebSocketServer(SimpleWebSocketServer):
    clients = []

    def setPuckoDb(self, puckodb):
        self.puckodb = puckodb

    def addClient(self, client):
        self.clients.append(client)

    def removeClient(self, client):
        self.clients.remove(client)

    def getClients(self):
        return self.clients

class PuckoDbServer(WebSocket):
    def handleMessage(self):
        print(self.address, 'message', self.data)
        self.server.puckodb.parse(self,self.data)

    def handleConnected(self):
       print(self.address, 'connected')
       self.server.addClient(self)

    def handleClose(self):
       self.server.removeClient(self)
       print(self.address, 'closed')

server = PuckoWebSocketServer('', 9999, PuckoDbServer)
server.setPuckoDb(PuckoDb(PuckoDbStorage()))
server.serveforever()