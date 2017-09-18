
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
        return True

    def sendObjs(self,client,objs):
        for k,v in objs.items():
            d = self.filterObj.filterIt(client.getUsers(),v)
            if '.tid' in d:
                client.sendIt({ k: d })
        return True

    def parse(self,client,message):
        print "Parse:",client.address,message
        incomming = json.loads(message)
        if not 'type' in incomming:
            return client.error("no 'type' in message")

        print "Type: " + incomming['type']

        # AUTH
        if incomming['type'] == 'auth':
            client.setUser(incomming['user'])
            return client.ok('Login successful')

        if incomming['type'] == 'connected':
            return client.ok('Connected')

        # Replay
        if incomming['type'] == 'replay':
            fromTid = incomming['from']
            client.ok('replay successful')
            objs = self.puckodb.getFrom(fromTid)
            return self.sendObjs(client,objs)

        # CREATE
        if incomming['type'] == 'create':
            if not self.filterObj.canCreate(client.getUsers())
                return client.error("Not allowed to create object %s" % uuid)

            uuid = self.puckodb.create()
            self.puckodb.update(uuid,incomming)
            client.ok('created',{ 'uuid': uuid })
            return self.sendUpdate(uuid)

        if not 'uuid' in incomming:
            return client.error("no 'uuid' in message")

        # get UUID from message
        uuid = incomming['uuid']
        current = self.puckodb.get(uuid)
        if not current:
            return client.error("Object %s does not exist", uuid)

        # UPDATE
        if incomming['type'] == 'update':
            if 'set' in incomming and not self.filterObj.canUpdate(client.getUsers(),current,incomming[set])
                return client.error("Not allowed to update object %s" % uuid)

            if 'delete' in incomming and not self.filterObj.canUpdate(client.getUsers(),current,incomming[delete])
                return client.error("Not allowed to update object %s" % uuid)

            self.puckodb.update(uuid,incomming)
            client.ok('updated',{'uuid':uuid})
            return self.sendUpdate(uuid)

        # DELETE
        if incomming['type'] == 'delete':
            if not self.filterObj.canDelete(client.getUsers())
                return client.error("Not allowed to delete object %s" % uuid)

            self.puckodb.delete(uuid)
            client.ok('deleted',{'uuid':uuid})
            return self.sendUpdate(uuid)

        return client.error("Invalid 'type' in message")
