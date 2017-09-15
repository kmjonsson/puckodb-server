import json

class Filter():
    def __init__(self,rules={}):
        self.rules = rules

    def setRules(self,rules):
        self.rules = rules

    def filterIt(self,users,show_data):
        allow = False
        result = {}
        admin = False

        for user in users:
            if user in self.rules and '__admin__' in self.rules[user]:
                admin = True

        for key,data in show_data.items():
            read = False
            write = False
            for user in filter(lambda u: u in self.rules,users):
                if not key in self.rules[user]:
                    continue
                rule = self.rules[user][key]
                if 'read' in rule:
                    read = rule['read']
                if 'write' in rule:
                    write = rule['write']
                if 'allowIf' in rule and type(data) is list and rule['allowIf'] in data:
                    allow = True
                if 'allowIf' in rule and not type(data) is list and rule['allowIf'] == data:
                    allow = True
                if 'denyIf' in rule and type(data) is list and rule['denyIf'] in data:
                    allow = False
                if 'denyIf' in rule and not type(data) is list and rule['denyIf'] == data:
                    allow = False

            if read or admin:
                result[key] = data

        if not allow and not admin:
            return {} 

        return result
            
    def canWrite(self,users,original_data,new_data):
        allow = True
        admin = False

        for u in users:
            if u in self.rules and '__admin__' in self.rules[u]:
                admin = True

        for key,data in original_data.items():
            for user in filter(lambda u: u in self.rules,users):
                if not key in self.rules[user]:
                    continue
                rule = self.rules[user][key]
                if 'denyIf' in rule and rule['denyIf'] in data:
                    allow = False

        for key,data in new_data.items():
            write = False
            for user in filter(lambda u: u in self.rules,users):
                if not key in self.rules[user]:
                    continue
                rule = self.rules[user][key]
                if 'write' in rule and rule['write']:
                    write = True
                if 'denyIf' in rule and rule['denyIf'] in data:
                    allow = False

            if not write:
                allow = False
            
        return admin or allow


if __name__ == "__main__":
    f = Filter({
            '__users__': {
                'hej': { 'read': True },
                'hopp': { 'write': True },
                'auth': { 'allowIf': '__users__' },
            },
            'magnus': {
                '__admin__': True,
                'auth': { 'allowIf': 'magnus' }
            }
        })
        
    print json.dumps(f.canWrite(['__users__','magnus'],{
            'hej':'hopp',
            'gnu':'apa',
            'hopp': '',
            'auth': ['public','magnus']
        },{
            'hej':'groda'
        }), indent= 4, sort_keys= True)
        
    print json.dumps(f.canWrite(['__users__'],{
            'hej':'hopp',
            'gnu':'apa',
            'hopp': '',
            'auth': ['public','magnus']
        },{
            'hej':'groda'
        }), indent= 4, sort_keys= True)
        
    print json.dumps(f.canWrite(['__users__'],{
            'hej':'hopp',
            'gnu':'apa',
            'hopp': '',
            'auth': ['__users__','magnus']
        },{
            'hopp':'groda'
        }), indent= 4, sort_keys= True)

    print json.dumps(f.filterIt(['__users__','magnus'],{
        'hej':'hopp',
        'gnu':'apa',
        'hopp': '',
        'auth': ['public','magnus']
    }), indent= 4, sort_keys= True)

    print json.dumps(f.filterIt(['__users__','magnu'],{
        'hej':'hopp',
        'gnu':'apa',
        'hopp': '',
        'auth': ['__users__']
    }), indent= 4, sort_keys= True)
