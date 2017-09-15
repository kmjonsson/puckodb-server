
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from puckodb.storage import PuckoDbStorage
from puckodb.puckodb import PuckoDb
from puckodb.router import PuckoDbRouter
from puckodb.filter import Filter
import json

import sys, traceback

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

    def sendAll(self,message):
        for client in self.clients:
            client.sendIt(message)

# Server client instance
class PuckoDbServer(WebSocket):
    def error(self,message,extra={}):
        r = {
            'type': u'error',
            'message': message
        }
        for k,v in extra.items():
            r[k] = v
        self.sendIt(json.dumps(r))

    def ok(self,message,extra={}):
        r = {
            'type': u'ok',
            'message': message
        }
        for k,v in extra.items():
            r[k] = v
        self.sendIt(json.dumps(r))

    def setUser(self,user):
        self.users = [u'__public__']
        if user and len(user):
            self.users.extend([u'__users__',user])
        print "setUser",self.address,self.users

    def getUsers(self):
        return self.users

    def sendAll(self,message):
        print(self.address, 'sendAll', unicode(message))
        self.server.sendAll(message)

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
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60           

    def handleConnected(self):
       print(self.address, 'connected')
       self.setUser('')
       self.server.addClient(self)
       self.server.router.parse(self,'{"type":"connected"}')

    def handleClose(self):
       self.server.removeClient(self)
       #self.server.router.parse(self,'{"type":"disconnected"}')
       print(self.address, 'closed')

router = PuckoDbRouter()
router.setFilter(Filter({
            '__public__': {
                '.tid': { 'read': True },
                'foo': { 'read': True },
                'auth': { 'allowIf': '__users__' },
            },
            '__users__': {
                '.tid': { 'read': True },
                'foo': { 'read': True },
                'bar': { 'read': True },
                'auth': { 'allowIf': '__users__', 'read': False },
            },
            'magnus': {
                '__admin__': True
            }
}))
router.setPuckoDb(PuckoDb(PuckoDbStorage('/tmp/pucko')))
server = PuckoWebSocketServer('', 9999, PuckoDbServer)
router.setServer(server)
server.setRouter(router)
server.serveforever()
