import src.handlers.ansible_executor as ansible_executor
import src.handlers.ssh_client as ssh_client
import src.handlers.ansible_handler as ansible_handler
from src.handlers.plays import  *


import grpc
from src.grpc_connector import client_pb2_grpc
from src.grpc_connector import client_pb2
import time

def full_test():

    start_time = time.time()

    #ansible_executor.execute_play(launch_instance_play("http://192.168.161.31:5000/v2.0", "admin", "openbaton", "admin"))

    channel = grpc.insecure_channel("localhost:50052")
    stub = client_pb2_grpc.ComposeHandlerStub(channel)

    f = open("tests/ansible-package.tar", "r")
    dc = client_pb2.FileMessage(file=f.read())
    f.close()
    rg = stub.UpCompose(dc)

    print(rg)

    '''
    #playbook = open("/home/rvl/projects/elastest/epm-adapter-ansible/playbooks/openstack_create.yml", "r")
    #r = ansible_handler.launch_playbook(playbook.read())

    play = open("/home/rvl/projects/elastest/epm-adapter-ansible/plays/play.yml", "r")
    r = ansible_handler.launch_play(play.read())
    print(r)

    #ansible_executor.execute_play(stop_instance_play("http://192.168.161.31:5000/v2.0", "admin", "openbaton", "admin"))

    #ansible_executor.execute_play(start_instance_play("http://192.168.161.31:5000/v2.0", "admin", "openbaton", "admin"))

    r = ansible_executor.execute_play(get_data_play("vm1","http://192.168.161.31:5000/v2.0", "admin", "openbaton", "admin"), with_metadata=True)
    #print(r)

    # Wait a bit so that the vm has time to init
    time.sleep(5)

    key_path = "/net/u/rvl/keys/rvl.key"
    ssh_exec = ssh_client.SSHExecutor("192.168.161.42", "ubuntu", password="test1", key_file_path=key_path)
    ssh_exec.execute_command("ls /")
    
    example_file="/home/rvl/projects/elastest/compose-package/metadata.yaml"
    ssh_exec.upload_file_from_path(hostPath=example_file, remotePath="metadata.yaml")
    
    f = open(example_file, "rb")
    ssh_exec.upload_file("docker-compose.yml", f.read())
    
    print("Downloaded file\n" + str(ssh_exec.download_file_from_container("metadata.yaml")))
    
    ssh_exec.execute_command("ls")
    '''

    ansible_executor.execute_play(delete_instance_play("vm1","http://192.168.161.31:5000/v2.0", "admin", "openbaton", "admin"))

    print("Test finished in: " + str(time.time() - start_time))


if __name__ == "__main__":
    full_test()