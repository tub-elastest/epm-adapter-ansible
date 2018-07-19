import grpc
import src.grpc_connector.client_pb2_grpc as client_pb2_grpc
import src.grpc_connector.client_pb2 as client_pb2
import time
import yaml
import os
import logging

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
            return identifier.resource_id
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


def check_package_pop(play, auth):
    print(auth)
    if len(auth) < 4 :
        # Check if play has cloud / auth specified
        play_as_dict = yaml.load(play)[0]
        if not "auth" in play_as_dict["tasks"][0]["os_server"] and not "cloud" in play_as_dict["tasks"][0]:
            logging.error("No PoP specified neither in the package nor in the ansible play!")
            return {}
        else:
            return play_as_dict["tasks"][0]["os_server"]["auth"]
    else:
        #Export variables
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