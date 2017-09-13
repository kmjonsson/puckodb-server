
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
            j = json.dumps({
                'type': u'ok',
                'error': u"Got IT :-)" + message
            })
            client.sendIt(j)
            return
        if incomming['type'] == 'create':
            #self.puckodb.create
            return

        client.sendMessage(json.dumps({
            'type': 'error',
            'error': "Invalid type in incomming message"
        }))

