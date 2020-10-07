#api.py
import requests
import json

#function the poll mimir and return status code and body in json format
def poll_mimir(url, json_body):
   r = requests.get(url=url, data=json.dumps(json_body)) 
   return r.status_code, r.json()