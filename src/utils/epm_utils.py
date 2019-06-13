import grpc
import src.grpc_connector.client_pb2_grpc as client_pb2_grpc
import src.grpc_connector.client_pb2 as client_pb2
import time
import yaml
import os
import logging
import requests
import json
import subprocess

max_timeout = 10



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
    return ""


def unregister_adapter(ip, id):
    channel = grpc.insecure_channel(ip + ":50050")
    stub = client_pb2_grpc.AdapterHandlerStub(channel)
    identifier = client_pb2.ResourceIdentifier(resource_id=id)
    stub.DeleteAdapter(identifier)


def check_package_pop(auth):
        #Export variables
    type = list(filter((lambda x: x.key == "type"), auth))
    out = {}
    if type[0].value == "openstack":
     
        for var in auth:
            os.environ['OS_' + var.key.upper()] = var.value
            out[var.key] = var.value
        out['type'] = 'openstack'
        return out
    elif type[0].value == "aws":
        for var in auth:
            if var.key.lower() == "aws_secret_key":
                out["aws_secret_key"] = var.value
            if var.key.lower() == "aws_access_key":
                out["aws_access_key"] = var.value
            if var.key.lower() == "region":
                out["region"] = var.value
        out['type'] = 'aws' 
        return out