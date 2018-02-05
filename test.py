import src.handlers.ansible_executor as ansible_executor
from src.handlers.plays import *


import grpc
from src.grpc_connector import client_pb2_grpc
from src.grpc_connector import client_pb2
import time

def full_test():

    start_time = time.time()

    channel = grpc.insecure_channel("localhost:50052")
    stub = client_pb2_grpc.OperationHandlerStub(channel)

    f = open("tests/ansible-package.tar", "r")
    dc = client_pb2.FileMessage(file=f.read())
    f.close()
    rg = stub.Create(dc)

    print(rg)
    #r = ansible_executor.execute_play(get_data_play("vm1","http://192.168.161.31:5000/v2.0", "admin", "openbaton", "admin"), with_metadata=True)

    # Wait a bit so that the vm has time to init
    time.sleep(5)

    key_path = "/net/u/rvl/mykey"

    ip = "192.168.161.164"
    user = "ubuntu"
    password = ""

    f = open("README.md", "rb")
    upld_message_with_path = client_pb2.RuntimeMessage(resource_id=ip,
                                                       property=["README.md", key_path, user, password], file=f.read())
    stub.UploadFile(upld_message_with_path)
    f.close()

    upld_message_with_path = client_pb2.RuntimeMessage(resource_id=ip,
                                                       property=["withPath", key_path, user, password, "play.yml", "play.yml"])
    stub.UploadFile(upld_message_with_path)

    command = "ls"
    commandMsg = client_pb2.RuntimeMessage(resource_id=ip, property=[command, key_path, user, password], file=None)
    response = stub.ExecuteCommand(commandMsg)
    print(response)

    dwnld_message = client_pb2.RuntimeMessage(resource_id=ip, property=["play.yml", key_path, user, password], file=None)
    output = stub.DownloadFile(dwnld_message)
    print(output)

    ansible_executor.execute_play(delete_instance_play("vm1","http://192.168.161.151:5000/v2.0", "admin", "openbaton", "admin"))

    print("Test finished in: " + str(time.time() - start_time))


if __name__ == "__main__":
    full_test()