import tempfile
import src.handlers.ansible_executor as ansible_executor
import yaml
import random

from src.grpc_connector.client_pb2 import ResourceGroupProto, Auth

def launch_playbook(playbook_contents):

    f = tempfile.NamedTemporaryFile("w")
    f.write(playbook_contents)
    f.seek(0)

    r = ansible_executor.execute_playbook(f.name)
    return r

def launch_play(play_contents):

    play_as_dict = yaml.load(play_contents)[0]

    try:
        rg_name = play_as_dict["name"]
    except:
        rg_name = str(random.randint(100,999))

    auth = play_as_dict["tasks"][0]["os_server"]["auth"]

    rg_auth = Auth(auth_url=auth["auth_url"], username=auth["username"], password=auth["password"], project=auth["project_name"])

    r = ansible_executor.execute_play(play_as_dict, with_metadata=True)

    pops = []
    vdus = []
    networks = []
    net_name = play_as_dict["tasks"][0]["os_server"]["network"]

    net = ResourceGroupProto.Network(name=net_name, cidr="", poPName="ansible", networkId="id")

    compute_id = r["openstack"]["id"]
    name = r["openstack"]["name"]
    imageName = r["openstack"]["image"]["name"]

    nets = r["openstack"]["addresses"]

    ip = r["openstack"]["interface_ip"]

    vdu = ResourceGroupProto.VDU(name=name, imageName=imageName, netName=net_name, computeId=compute_id, ip=ip,
                                          metadata=[])

    networks.append(net)
    vdus.append(vdu)

    rg = ResourceGroupProto(name=rg_name, pops=pops, networks=networks, vdus=vdus, auth=rg_auth)
    return rg