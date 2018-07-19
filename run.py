import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from logging import handlers
import tarfile
import tempfile
import time
import yaml
import shelve
import atexit

import grpc
import src.grpc_connector.client_pb2_grpc as client_pb2_grpc
from concurrent import futures

import src.grpc_connector.client_pb2 as client_pb2
from src.utils import epm_utils as epm_utils
from src.handlers import ansible_executor, ssh_client, ansible_handler
from src.handlers.plays import *
from src.utils import utils

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class Runner(client_pb2_grpc.OperationHandlerServicer):

    def Create(self, request, context):

        temp = tempfile.NamedTemporaryFile(delete=True)
        temp.write(request.file)
        package = tarfile.open(temp.name, "r")

        metadata = utils.extract_metadata(package)
        if metadata is None:
            raise Exception("No metadata found in package!")
        logging.debug("Package metadata: " + str(metadata))

        package_name = metadata.get("name")
        keypath = None
        if metadata.has_key("keypath"):
            keypath = metadata.get("keypath")
        logging.info(package_name)

        play = utils.extract_play(package)
        if play is None:
            raise Exception("No play found in package!")
        logging.debug("Package play: " + str(play))

        key = None
        if "key" in package.getnames():
            key = package.extractfile("key")
        auth = epm_utils.check_package_pop(play, request.auth)

        rg = ansible_handler.launch_play(play, auth, key, keypath)
        package.close()
        temp.close()

        return rg

    def Remove(self, request, context):
        instance_id = request.vdu.computeId

        db = shelve.open('auths.db')
        auth = db[str(instance_id) + "_auth"]
        db.close()

        if auth.has_key("auth_url") and auth.has_key("username") and auth.has_key("password"):
            ansible_executor.execute_play(
                delete_instance_play(instance_id, auth))
        else:
            raise ValueError("No proper auth found!")
        return client_pb2.Empty()

    def Start(self, request, context):
        instance_id = request.resource_id
        db = shelve.open('auths.db')
        auth = db[str(instance_id) + "_auth"]
        db.close()
        logging.info("Starting instance " + instance_id)
        if auth.has_key("auth_url") and auth.has_key("username") and auth.has_key("password"):
            ansible_executor.execute_play(
                start_instance_play(instance_id, auth))
        else:
            raise ValueError("No proper auth found!")
        return client_pb2.Empty()

    def Stop(self, request, context):
        instance_id = request.resource_id
        db = shelve.open('auths.db')
        auth = db[str(instance_id) + "_auth"]
        db.close()

        logging.info("Stoping instance " + instance_id)
        if auth.has_key("auth_url") and auth.has_key("username") and auth.has_key("password"):
            ansible_executor.execute_play(
                stop_instance_play(instance_id, auth))
        else:
            raise ValueError("No proper auth found!")
        return client_pb2.Empty()

    def ExecuteCommand(self, request, context):
        instance_id = request.vdu.ip
        command = request.property[0]
        #TODO: FIX
        user = "ubuntu"
        password = ""
        ssh_exec = ssh_client.SSHExecutor(instance_id, user, password=password)

        logging.info("Executing command " + command)
        output = ssh_exec.execute_command(command)
        return client_pb2.StringResponse(response=output)

    def DownloadFile(self, request, context):
        instance_id = request.vdu.ip
        # TODO: FIX
        user = "ubuntu"
        password = ""
        ssh_exec = ssh_client.SSHExecutor(instance_id, user, password=password)
        path = request.property[0]
        logging.info("Downloading file " + path)
        output = ssh_exec.download_file_from_container(path)
        return client_pb2.FileMessage(file=output)

    def UploadFile(self, request, context):

        instance_id = request.vdu.ip
        # TODO: FIX
        user = "ubuntu"
        password = ""
        ssh_exec = ssh_client.SSHExecutor(instance_id, user, password=password)
        type = request.property[0]
        if (type == "withPath"):
            remotePath = request.property[4]
            hostPath = request.property[3]
            logging.info("Uploading a file " + hostPath + " to " + remotePath)
            ssh_exec.upload_file_from_path(hostPath=hostPath, remotePath=remotePath)
            return client_pb2.Empty()
        else:
            path = request.property[0]
            logging.info("Uploading a file to " + path)
            file = request.file
            ssh_exec.upload_file(path, file)
            return client_pb2.Empty()


def serve(port="50052"):
    logging.info("Starting server...")
    logging.info("Listening on port: " + port)

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


adapter_id = ""
epm_ip = ""


@atexit.register
def stop():
    logging.info("Exiting")
    if adapter_id != "" and epm_ip != "":
        logging.info("DELETING ADAPTER")
        epm_utils.unregister_adapter(epm_ip, adapter_id)


if __name__ == '__main__':
    log = logging.getLogger('')
    log.setLevel(logging.DEBUG)
    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)

    fh = handlers.RotatingFileHandler("epm-adapter-ansible.log", maxBytes=(1048576 * 5), backupCount=7)
    fh.setFormatter(format)
    log.addHandler(fh)
    logging.info("\n")

    if "--register-adapter" in sys.argv:
        if len(sys.argv) == 4:
            logging.info("Trying to register pop to EPM instance...")
            epm_ip = sys.argv[2]
            adapter_ip = sys.argv[3]
            adapter_id = epm_utils.register_adapter(epm_ip, adapter_ip)
            serve()
        else:
            epm_ip = "elastest-epm"
            adapter_ip = "elastest-epm-adapter-ansible"
            adapter_id = epm_utils.register_adapter(epm_ip, adapter_ip)
            serve()
    else:
        serve()
