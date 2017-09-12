
import uuid

from storage import PuckoDbStorage

class PuckoDb():
    data = {}
    def __init__(self, storage):
        self.storage = storage
        self.data = self.storage.load()
        self.tid = 0
        for uuid in self.data.keys():
            if self.data[uuid]['.tid'] > self.tid:
                self.tid = self.data[uuid]['.tid']

    def _getUUID(self):
        return str(uuid.uuid1())

    def _getTid(self):
        self.tid = self.tid + 1
        return self.tid

    # return current tid 
    def tid(self):
        return self.tid

    # create object returns UUID
    def create(self):
        uuid = self._getUUID()
        tid  = self._getTid()
        self.data[uuid] = { ".tid": tid }
        self.storage.save({uuid:self.data[uuid]})
        return uuid

    def delete(self,uuid):
        # Can only update object that exists
        if not uuid in self.data:
            return

        # can only work on objects that are not deleted
        if '.deleted' in self.data[uuid]:
            return
        
        tid  = self._getTid()
        self.data[uuid] = { ".tid": tid, ".deleted": True }
        self.storage.save({uuid:self.data[uuid]})
        return uuid

    def update(self,uuid,data):
        # Can only update object that exists
        if not uuid in self.data:
            return

        # can only work on objects that are not deleted
        if '.deleted' in self.data[uuid]:
            return

        if 'set' in data:
            for k in data['set'].keys():
                self.data[uuid][k] = data['set'][k]

        if 'delete' in data:
            for k in data['delete']:
                if k in self.data[uuid]:
                    del self.data[uuid][k]

        tid  = self._getTid()
        self.data[uuid]['.tid'] = tid
        self.storage.save({uuid:self.data[uuid]})

    def checkpoint(self):
        tid  = self._getTid()
        self.storage.checkpoint(tid,self.data)

class FakeClient():
    def sendMessage(self, string):
        print "FakeClient: ", string

if __name__ == "__main__":
    c = FakeClient()
    p = PuckoDb(PuckoDbStorage("/tmp/pucko"))
    u = p.create()
    p.update(u,{
        'set': { 'fnu':'foo' },
        'delete': ['apa']
    })
    p.update(u,{
        'delete': ['fnu']
    })
#    p.delete(u)
    p.checkpoint()