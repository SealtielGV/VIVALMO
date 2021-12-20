
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
access_token = "a2347dae065f25ead039e2b3723484e7f2110373b56a0c24229b5632f055cd0d9a7a2ff9cb03ba0ccee4bdff4c45f8f4312194ad61b0dbda3c360325e67fa7c8"

params = {
    'params': {
        'access_token': access_token,
    }
}
url = _url+"/catalog"
print(url)
print(params)

r = requests.post(url=url, json=dict(params))
print(r.content)

rjson = r.json()
#print(rjson)
pp.pprint(rjson)

exit(0)
#################################################################

params = {
    'params': {
        'access_token': access_token,
    }
}
url = _url+"/pricestock"
print(url)
print(params)

r = requests.post(url=url, json=dict(params))
print(r.content)

rjson = r.json()
#print(rjson)
pp.pprint(rjson)

#################################################################

params = {
    'params': {
        'access_token': access_token,
    }
}
url = _url+"/pricelist"
print(url)
print(params)

r = requests.post(url=url, json=dict(params))
print(r.content)

rjson = r.json()
#print(rjson)
pp.pprint(rjson)

#################################################################

params = {
    'params': {
        'access_token': access_token,
    }
}
url = _url+"/stock"
print(url)
print(params)

r = requests.post(url=url, json=dict(params))
print(r.content)

rjson = r.json()
#print(rjson)
pp.pprint(rjson)

#################################################################
import json
data = []
with open('sale.json') as json_file:
    data = json.load(json_file)

pp.pprint(data)

params = {
    'params': {
        'access_token': access_token,
        'sales': [data],
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
