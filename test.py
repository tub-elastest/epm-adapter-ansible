import sys

import grpc
from src.grpc_connector import client_pb2_grpc
from src.grpc_connector import client_pb2
import time

def full_test(auth_url, password, username="admin",
                           project="admin"):
    ip = "192.168.161.164"
    user = "ubuntu"
    passphrase = ""

    start_time = time.time()
    #START VM
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
    
    # UPLOAD FILES
    f = open("README.md", "rb")
    upld_message_with_path = client_pb2.RuntimeMessage(resource_id=ip,
                                                       property=["README.md", key_path, user, passphrase], file=f.read())
    stub.UploadFile(upld_message_with_path)
    f.close()

    upld_message_with_path = client_pb2.RuntimeMessage(resource_id=ip,
                                                       property=["withPath", key_path, user, passphrase, ".gitignore", ".gitignore"])
    stub.UploadFile(upld_message_with_path)

    # EXECUTE LS
    command = "ls"
    commandMsg = client_pb2.RuntimeMessage(resource_id=ip, property=[command, key_path, user, passphrase], file=None)
    response = stub.ExecuteCommand(commandMsg)
    print(response)

    # DOWNLOAD FILE
    dwnld_message = client_pb2.RuntimeMessage(resource_id=ip, property=[".gitignore", key_path, user, passphrase], file=None)
    output = stub.DownloadFile(dwnld_message)
    print(output)

    # TERMINATE
    auth = client_pb2.Auth(auth_url=auth_url, username=username, password=password,
                           project=project)
    terminate = client_pb2.ResourceIdentifier(resource_id="vm1", auth=auth)
    stub.Remove(terminate)

    print("Test finished in: " + str(time.time() - start_time))


if __name__ == "__main__":
    url = sys.argv[1]
    password = sys.argv[2]

    full_test(auth_url=url, password=password)