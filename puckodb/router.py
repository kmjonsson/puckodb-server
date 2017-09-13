
import json

class PuckoDbRouter():
    def setPuckoDb(self,puckodb):
        self.puckodb = puckodb

    def parse(self,client,message):
        print "Parse:",client.address,message
        incomming = json.loads(message)
        if not 'type' in incomming:
            j = json.dumps({
                'type': u'error',
                'error': u"Missing type in incomming message"
            })
            client.sendIt(j)
            return
        print "Type: " + incomming['type']
        if incomming['type'] == 'auth':
            client.setUser(incomming['user'])
            j = json.dumps({
                'type': u'ok',
            })
            client.sendIt(j)
            return
        if incomming['type'] == 'create':
            id = self.puckodb.create()
            self.puckodb.update(id,incomming['data'])
            print "Created: ",id
            return

        client.sendMessage(json.dumps({
            'type': 'error',
            'error': "Invalid type in incomming message"
        }))

