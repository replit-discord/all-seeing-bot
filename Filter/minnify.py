import json


dat = open('conv.json').read()

dat = json.loads(dat)

open('conv.json', 'w').write(json.dumps(dat))