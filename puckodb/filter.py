import json

class Filter():
    

    def __init__(self,rules={}):
        self.rules = rules

    def setRules(self,rules):
        self.rules = rules

    def filter(self,user,data):
        allow = False
        result = {}
        for k in data:
            read = False
            write = False
            for u in ['__users__',user]:
                if u in self.rules and k in self.rules[u]:
                    if 'read' in self.rules[u][k] and self.rules[u][k]['read']:
                        read = True
                    if 'read' in self.rules[u][k] and not self.rules[u][k]['read']:
                        read = False
                    if 'write' in self.rules[u][k] and self.rules[u][k]['write']:
                        write = True
                    if 'write' in self.rules[u][k] and not self.rules[u][k]['write']:
                        write = False
                    if 'allowIf' in self.rules[u][k] and self.rules[u][k]['allowIf'] in data[k]:
                        allow = True
                    if 'denyIf' in self.rules[u][k] and self.rules[u][k]['allowIf'] in data[k]:
                        allow = False
            
            if read or write:
                result[k] = data[k]

        if not allow:
            return {} 

        return result
            


if __name__ == "__main__":
    f = Filter({
            '__users__': {
                'hej': { 'read': True },
                'hopp': { 'write': True },
                'auth': { 'allowIf': 'public' },
            },
            'magnus': {
                'auth': { 'allowIf': 'magnus' }
            }
        })
        
    print json.dumps(f.filter('magnus',{
        'hej':'hopp',
        'gnu':'apa',
        'hopp': '',
        'auth': ['public','magnus']
    }), indent= 4, sort_keys= True)

    print json.dumps(f.filter('magnus',{
        'hej':'hopp',
        'gnu':'apa',
        'hopp': '',
    }), indent= 4, sort_keys= True)