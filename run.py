import os
import sys
import tarfile
import tempfile
import time
import yaml
import shelve

import grpc
import src.grpc_connector.client_pb2_grpc as client_pb2_grpc
from concurrent import futures

import src.grpc_connector.client_pb2 as client_pb2
from src.utils import epm_utils as utils
from src.handlers import ansible_executor, ssh_client, ansible_handler
from src.handlers.plays import *

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class Runner(client_pb2_grpc.OperationHandlerServicer):
    def Create(self, request, context):

        temp = tempfile.NamedTemporaryFile(delete=True)
        temp.write(request.file)
        package = tarfile.open(temp.name, "r")

        metadata = yaml.load(package.extractfile("metadata.yaml").read())
        package_name = metadata.get("name")
        print(package_name)

        play = package.extractfile("play.yaml").read()

        rg = ansible_handler.launch_play(play)
        package.close()
        temp.close()

        return rg

    ''' TODO:
    def CheckIfContainerExists(self, request, context):

        compose_id = request.resource_id
        result = str(docker_handler.check_container_exists(compose_id, True))
        return client_pb2.StringResponse(response=result)

    def CheckIfContainerRunning(self, request, context):

        compose_id = request.resource_id
        result = str(docker_handler.check_container_exists(compose_id, False))
        return client_pb2.StringResponse(response=result)

    '''

    def Remove(self, request, context):
        instance_id = request.resource_id

        db = shelve.open('auths.db')
        auth = db[str(instance_id)]
        db.close()

        ansible_executor.execute_play(
            delete_instance_play(instance_id, auth["auth_url"], auth["username"], auth["password"], auth["project_name"]))
        return client_pb2.Empty()


    def StartContainer(self, request, context):
        instance_id = request.resource_id
        db = shelve.open('auths.db')
        auth = db[str(instance_id)]
        db.close()
        print("Starting instance " + instance_id)
        ansible_executor.execute_play(
            start_instance_play(instance_id, auth["auth_url"], auth["username"], auth["password"], auth["project_name"]))
        return client_pb2.Empty()

    def StopContainer(self, request, context):
        instance_id = request.resource_id
        db = shelve.open('auths.db')
        auth = db[str(instance_id)]
        db.close()

        print("Stoping instance " + instance_id)
        ansible_executor.execute_play(
            stop_instance_play(instance_id, auth["auth_url"], auth["username"], auth["password"], auth["project_name"]))
        return client_pb2.Empty()

    def ExecuteCommand(self, request, context):
        instance_id = request.resource_id
        command = request.property[0]
        key = request.property[1]
        user = request.property[2]
        password = request.property[3]
        ssh_exec = ssh_client.SSHExecutor(instance_id, user, password=password, key_file_path=key)

        print("Executing command " + command)
        output = ssh_exec.execute_command(command)
        return client_pb2.StringResponse(response=output)

    def DownloadFile(self, request, context):
        instance_id = request.resource_id
        key = request.property[1]
        user = request.property[2]
        password = request.property[3]
        ssh_exec = ssh_client.SSHExecutor(instance_id, user, password=password, key_file_path=key)
        path = request.property[0]
        print("Downloading file " + path)
        output = ssh_exec.download_file_from_container(path)
        return client_pb2.FileMessage(file=output)

    def UploadFile(self, request, context):

        instance_id = request.resource_id
        key = request.property[1]
        user = request.property[2]
        password = request.property[3]
        ssh_exec = ssh_client.SSHExecutor(instance_id, user, password=password, key_file_path=key)
        type = request.property[0]
        if(type == "withPath"):
            remotePath = request.property[5]
            hostPath = request.property[4]
            print("Uploading a file " + hostPath + " to " + remotePath)
            ssh_exec.upload_file_from_path(hostPath=hostPath, remotePath=remotePath)
            return client_pb2.Empty()
        else:
            path = request.property[0]
            print("Uploading a file to " + path)
            file = request.file
            ssh_exec.upload_file(path, file)
            return client_pb2.Empty()


def serve(port="50052", register=False, ip="elastest-epm", adapter_ip="elastest-epm-adapter-ansible"):
    print("Starting server...")
    print("Listening on port: " + port)

    if register:
        print("Trying to register pop to EPM instance...")
        utils.register_pop(ip, adapter_ip)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    client_pb2_grpc.add_OperationHandlerServicer_to_server(
        Runner(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    if "--register-pop" in sys.argv:
        if len(sys.argv) == 4:
            serve(register=True, ip=sys.argv[2], adapter_ip=sys.argv[3])
        else:
            serve(register=True)
    else:
        serve()
