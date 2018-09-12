import grpc
import src.grpc_connector.client_pb2_grpc as client_pb2_grpc
import src.grpc_connector.client_pb2 as client_pb2
import time
import yaml
import os
import logging
import requests
import json

max_timeout = 10

pop_ansible = {"name": "aws", "interfaceEndpoint": "amazon", "interfaceInfo" : [{"key": "type", "value": "aws"},  {"key": "aws_access_key", "value": "AKIAJRRMWNVCLD4JOVMA"}, {"key": "aws_secret_key", "value": "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"}], "status": "active"}
headers = {"accept": "application/json","content-type": "application/json"}
def register_adapter(ip, ansible_ip):
    channel = grpc.insecure_channel(ip + ":50050")
    stub = client_pb2_grpc.AdapterHandlerStub(channel)
    endpoint = ansible_ip + ":50052"
    adapter = client_pb2.AdapterProto(type="ansible", endpoint=endpoint)

    i = 0
    while i < 10:
        try:
            identifier = stub.RegisterAdapter(adapter)
            logging.info("Adapter registered")
            break
        except:
            logging.info("Still not connected")
        time.sleep(11)
        i += 1
    
    logging.info("Register pop")
    r = requests.post('http://' + ip + ':8180/v1/pop', data=json.dumps(pop_ansible), headers=headers)
    logging.info("Pop registered")
    logging.debug(str(r.status_code) + " " + r.reason)
    logging.debug(r.json())
    return ""


def unregister_adapter(ip, id):
    channel = grpc.insecure_channel(ip + ":50050")
    stub = client_pb2_grpc.AdapterHandlerStub(channel)
    identifier = client_pb2.ResourceIdentifier(resource_id=id)
    stub.DeleteAdapter(identifier)


def check_package_pop(auth):
    print(auth)
    if len(auth) < 4 :
       raise Exception("No authorisation for the PoP provided")
    else:
        #Export variables
        if auth.type == "openstack":
            out = {}
            for var in auth:
                if var.key == "username":
                    os.environ['OS_USERNAME'] = var.value
                    out["username"] = var.value
                if var.key == "password":
                    os.environ['OS_PASSWORD'] = var.value
                    out["password"] = var.value
                if var.key == "project_name":
                    os.environ['OS_PROJECT_NAME'] = var.value
                    out["project_name"] = var.value
                if var.key == "auth_url":
                    os.environ['OS_AUTH_URL'] = var.value
                    out["auth_url"] = var.value
            return out
        elif auth.type == "aws":
            for var in auth:
                if var.key.lower() == "aws_secret_key":
                    os.environ['AWS_SECRET_KEY'] = var.value
                    out["aws_secret_key"] = var.value
                if var.key.lower() == "aws_access_key":
                    os.environ['AWS_ACCESS_KEY'] = var.value
                    out["aws_access_key"] = var.value
            return out