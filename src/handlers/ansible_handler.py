import tempfile
import src.handlers.ansible_executor as ansible_executor
import yaml

from src.grpc_connector.client_pb2 import ResourceGroupCompose

def launch_playbook(playbook_contents):

    f = tempfile.NamedTemporaryFile("w")
    f.write(playbook_contents)
    f.seek(0)

    r = ansible_executor.execute_playbook(f.name)
    return r

def launch_play(play_contents):

    play_as_dict = yaml.load(play_contents)[0]
    r = ansible_executor.execute_play(play_as_dict, with_metadata=True)
    return r

def convert_to_resource_group(r):

    print(dict(r))

    pops = []
    vdus = []
    networks = []

    net = ResourceGroupCompose.NetworkCompose(name="mgmt", cidr="", poPName="ansible", networkId="id")

    compute_id = r["openstack"]["id"]
    name = r["openstack"]["name"]
    imageName = r["openstack"]["image"]["name"]

    nets = r["openstack"]["addresses"]
    net_name = "mgmt"

    ip = r["openstack"]["interface_ip"]

    vdu = ResourceGroupCompose.VDUCompose(name=name, imageName=imageName, netName=net_name, computeId=compute_id, ip=ip,
                                          metadata=[])

    networks.append(net)
    vdus.append(vdu)

    rg = ResourceGroupCompose(name="rg", pops=pops, networks=networks, vdus=vdus)
    return rg