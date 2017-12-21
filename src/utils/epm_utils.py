import json
import requests
import time

max_timeout = 10


def register_pop(ip, adapter_ip):
    i = 0
    while i < 10:
        pop_ansible = {"name": "ansible",
                       "interfaceEndpoint": adapter_ip,
                       "interfaceInfo":
                           [{"key": "type",
                             "value": "ansible"}]}

        headers = {"accept": "application/json",
                   "content-type": "application/json"}
        try:
            r = requests.post('http://' + ip + ':8180/v1/pop', data=json.dumps(pop_ansible), headers=headers)
            print(str(r.status_code) + " " + r.reason)
            break
        except requests.ConnectionError:
            print("Still not connected")
        time.sleep(11)
        i += 1
