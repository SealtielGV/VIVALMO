
import requests
import json
import sys
import pprint
pp = pprint.PrettyPrinter(indent=4)

access_token = False
if len(sys.argv)<2:
    print("Need at least one argument, run like this: python3 testocapi.py https://www.mysite.com producteca")

baseurl = sys.argv[1]
connector = sys.argv[2]
_url = baseurl+"/ocapi/"+connector

#################################################################
access_token = "cd563257307e9f6f0f880f68cf0a32dbf8d1d091452c108840aa8e110cababa29c1a8e6bd36e5082c41041dfe59a6e9ba11a6c88fd5a4f8e4f312736d9899ed1"

import json
data = []
with open('saleml4.json') as json_file:
    data = json.load(json_file)

pp.pprint(data)

params = {
    'params': {
        'sales': [data],
        'access_token': access_token
    }
}
url = _url+"/sales"
print(url)
print(params)

r = requests.post(url=url, json=dict(params))
print(r.content)

rjson = r.json()
#print(rjson)
pp.pprint(rjson)
