
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
                c.sendObj({'type':'object', uuid: d})
        return True

    def sendObjs(self,client,objs):
        for k,v in objs.items():
            d = self.filterObj.filterIt(client.getUsers(),v)
            if '.tid' in d:
                client.sendObj({'type':'object', k: d })
        return True

    def parse(self,client,message):
        print "Parse:",client.address,message
        incomming = json.loads(message)
        if not 'type' in incomming:
            return client.error('error',"no 'type' in message")

        if not 'id' in incomming:
            return client.error('error',"no 'id' in message")

        id = incomming['id']
        type = incomming['type']

        print "Type: %s, Id: %s" % (type,id)

        # AUTH
        if type == 'auth':
            if incomming['password'] == 'correct':
                client.setUser(incomming['user'])
                return client.ok(id,'Login successful')
            else:
                return client.error(id,'Login failed')

        if type == 'connected':
            return client.ok(id,'Connected')

        # Replay
        if type == 'replay':
            fromTid = incomming['from']
            client.ok(id,'replay successful')
            objs = self.puckodb.getFrom(fromTid)
            return self.sendObjs(client,objs)

        # CREATE
        if type == 'create':
            if not self.filterObj.canCreate(client.getUsers()):
                return client.error(id,"Not allowed to create object")

            uuid = self.puckodb.create()
            self.puckodb.update(uuid,incomming)
            client.ok(id,'created',{ 'uuid': uuid })
            return self.sendUpdate(uuid)

        if not 'uuid' in incomming:
            return client.error(id,"no 'uuid' in message")

        # get UUID from message
        uuid = incomming['uuid']
        current = self.puckodb.get(uuid)
        if not current:
            return client.error(id,"Object %s does not exist" % uuid)

        # UPDATE
        if type == 'update':
            if 'set' in incomming and not self.filterObj.canUpdate(client.getUsers(),current,incomming):
                return client.error(id,"Not allowed to update object %s" % uuid)

            if 'delete' in incomming and not self.filterObj.canUpdate(client.getUsers(),current,incomming):
                return client.error(id,"Not allowed to delete in object %s" % uuid)

            self.puckodb.update(uuid,incomming)
            client.ok(id,'updated',{'uuid':uuid})
            return self.sendUpdate(uuid)

        # DELETE
        if type == 'delete':
            if not self.filterObj.canDelete(client.getUsers()):
                return client.error(id,"Not allowed to delete object %s" % uuid)

            self.puckodb.delete(uuid)
            client.ok(id,'deleted',{'uuid':uuid})
            return self.sendUpdate(uuid)

        return client.error(id,"Invalid 'type' in message")
