
import json

class PuckoDbRouter():
    def setPuckoDb(self,puckodb):
        self.puckodb = puckodb

    def setFilter(self,filterObj):
        print "setFilter",filterObj
        self.filterObj = filterObj

    def setServer(self,server):
        print "setServer",server
        self.server = server

    def sendUpdate(self,uuid):
        o = self.puckodb.get(uuid)
        print "sendUpdate (before filter)",uuid,o
        print "sendUpdate (server)", self.server
        for c in self.server.getClients():
            d = self.filterObj.filterIt(c.getUsers(),o)
            print "sendUpdate (after filter)",c.getUsers(),d
            if '.tid' in d:
                c.sendIt({uuid: d})

    def sendObjs(self,client,objs):
        for k,v in objs.items():
            d = self.filterObj.filterIt(client.getUsers(),v)
            if '.tid' in d:
                client.sendIt({ k: d })

    def parse(self,client,message):
        print "Parse:",client.address,message
        incomming = json.loads(message)
        if not 'type' in incomming:
            client.error("no 'type' in message")
            return

        print "Type: " + incomming['type']

        # AUTH
        if incomming['type'] == 'auth':
            client.setUser(incomming['user'])
            client.ok('Login successful')
            return

        if incomming['type'] == 'connected':
            client.ok('Connected')
            return

        # Replay
        if incomming['type'] == 'replay':
            fromTid = incomming['from']
            client.ok('replay successful')
            objs = self.puckodb.getFrom(fromTid)
            self.sendObjs(client,objs)
            return

        # CREATE
        if incomming['type'] == 'create':
            uuid = self.puckodb.create()
            self.puckodb.update(uuid,incomming)
            client.ok('created',{ 'uuid': uuid })
            self.sendUpdate(uuid)
            return

        if not 'uuid' in incomming:
            client.error("no 'uuid' in message")
            return

        # get UUID from message
        uuid = incomming['uuid']

        # UPDATE
        if incomming['type'] == 'update':    
            self.puckodb.update(uuid,incomming)
            client.ok('updated',{'uuid':uuid})
            self.sendUpdate(uuid)
            return

        # DELETE
        if incomming['type'] == 'delete':
            self.puckodb.delete(uuid)
            client.ok('deleted',{'uuid':uuid})
            self.sendUpdate(uuid)
            return

        client.error("Invalid 'type' in message")
