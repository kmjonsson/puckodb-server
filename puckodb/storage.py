import json
import os
from os import listdir
from os.path import isfile, join

class PuckoDbStorage():
    def __init__(self,path):
        self.path = path
        pass
        
    def _makePath(self,tid,ext):
        return "%s/%d%s" % (self.path,tid,ext)

    # Save event
    def save(self, data):
        print "PuckoDbStorage: save", data
        for k in data.keys():
            path = self._makePath(data[k]['.tid'],".json")
            f = open("%s.t" % path,"w")
            f.write(json.dumps({k:data[k]}, sort_keys=True, indent=4))
            f.close()
            os.rename("%s.t" % path,path)

    # load everything (once?)
    def load(self):
        print "PuckoDbStorage: load"
        initfiles = [f for f in listdir(self.path) if isfile(join(self.path, f)) and f.endswith(".init")]
        initfiles.sort(key=lambda f: int(f.split(".")[0]))
        data = {}
        initnr = 0
        if initfiles and len(initfiles):
            initfile = initfiles.pop()
            print "initfile: ", initfile
            f = open(join(self.path,initfile))
            data = json.load(f)
            f.close()
            initnr = int(initfile.split(".")[0])

        jsonfiles = [f for f in listdir(self.path) if isfile(join(self.path, f)) and 
                                                        f.endswith(".json") and 
                                                        int(f.split(".")[0]) >= initnr]
        jsonfiles.sort(key=lambda f: int(f.split(".")[0]))
        for file in jsonfiles:
            print "jsonfile: ", file
            f = open(join(self.path,file))
            delta = json.load(f)
            f.close()
            for k in delta.keys():
                data[k] = delta[k]
                
        return data

    # create checkpoint @ current state
    # every hour? on close? on???
    def checkpoint(self,tid,data):
        print "PuckoDbStorage: checkpoint", tid, data
        path = self._makePath(tid,".init")
        f = open("%s.t" % path,"w")
        f.write(json.dumps(data, sort_keys=True, indent=4))
        f.close()
        os.rename("%s.t" % path,path)
