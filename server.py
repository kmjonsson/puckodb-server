
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from puckodb.storage import PuckoDbStorage
from puckodb.puckodb import PuckoDb
from puckodb.router import PuckoDbRouter
import json

# Server Listener
class PuckoWebSocketServer(SimpleWebSocketServer):
    clients = []

    def setRouter(self, router):
        print "PuckoWebSocketServer: setRouter = ", router
        self.router = router

    def addClient(self, client):
        self.clients.append(client)

    def removeClient(self, client):
        self.clients.remove(client)

    def getClients(self):
        return self.clients

# Server client instance
class PuckoDbServer(WebSocket):
    def setUser(self,user):
        self.user = user

    def sendIt(self,message):
        print(self.address, 'sendIt', unicode(message))
        self.sendMessage(unicode(message))

    def handleMessage(self):
        print(self.address, 'message', self.data)
        try:
            self.server.router.parse(self,unicode(self.data))
        except Exception as inst:
            print type(inst)     # the exception instance
            print inst.args      # arguments stored in .args
            print inst           

    def handleConnected(self):
       print(self.address, 'connected')
       self.server.addClient(self)
       self.server.router.parse(self,'{"type":"connected"}')

    def handleClose(self):
       self.server.removeClient(self)
       self.server.router.parse(self,'{"type":"disconnected"}')
       print(self.address, 'closed')

router = PuckoDbRouter()
router.setPuckoDb(PuckoDb(PuckoDbStorage('/tmp/pucko')))
server = PuckoWebSocketServer('', 9999, PuckoDbServer)
server.setRouter(router)
server.serveforever()
