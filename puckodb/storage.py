import json
import os

class PuckoDbStorage():
    def __init__(self,path):
        self.path = path
        pass
        
    def _makePath(self,tid,ext):
        return "%s/%d%s" % (self.path,tid,ext)

    # Save event
    def save(self, data):
        print "PuckoDbStorage: save", data
        path = self._makePath(data['.tid'],".json")
        f = open("%s.t" % path,"w")
        f.write(json.dumps(data, sort_keys=True))
        f.close()
        os.rename("%s.t" % path,path)

    # load everything (once?)
    def load(self):
        print "PuckoDbStorage: load"
        return { 'gnutt': {'.tid':4, '.deleted':True} }

    # create checkpoint @ current state
    # every hour? on close? on???
    def checkpoint(self,tid,data):
        print "PuckoDbStorage: checkpoint", tid, data
        path = self._makePath(tid,".init")
        f = open("%s.t" % path,"w")
        f.write(json.dumps(data, sort_keys=True))
        f.close()
        os.rename("%s.t" % path,path)
