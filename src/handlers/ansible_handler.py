import tempfile
import src.handlers.ansible_executor as ansible_executor
import yaml
import random
import shelve

from src.grpc_connector.client_pb2 import ResourceGroupProto, Auth


def launch_playbook(playbook_contents):
    f = tempfile.NamedTemporaryFile("w")
    f.write(playbook_contents)
    f.seek(0)

    r = ansible_executor.execute_playbook(f.name)
    return r


def launch_play(play_contents, auth, key=None, keypath=None):

    if key is None and keypath is None:
        raise Exception("You have to include the private key (for doing runtime operations on the launched instances)! "+
                        "You can either add it in the package with the name 'key' or set a 'keypath' in the metadata " +
                        "where the adapater the adapter can find it.")

    play_as_dict = yaml.load(play_contents)[0]

    try:
        rg_name = play_as_dict["name"]
    except:
        rg_name = str(random.randint(100, 999))

    r = ansible_executor.execute_play(play_as_dict, with_metadata=True)

    if not r.has_key("openstack"):
        print("It was either not possible to execute the play or it was not an openstack play. Please check if everything " +
              " specified in the play is already in the OpenStack instance and that the auth credentials are correct.")
        raise ValueError("Could not instantiate VM!")

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

    save_to_db(name, auth, "auth")

    if key is not None:
        save_to_db(ip, key.read(), "key")
    elif keypath is not None:
        save_to_db(ip, keypath, "keypath")

    vdu = ResourceGroupProto.VDU(name=name, imageName=imageName, netName=net_name, computeId=compute_id, ip=ip,
                                 metadata=[])

    networks.append(net)
    vdus.append(vdu)

    rg = ResourceGroupProto(name=rg_name, pops=pops, networks=networks, vdus=vdus)
    return rg


def save_to_db(name, value, type):
    db = shelve.open('auths.db')
    db[str(name) + "_" + type] = value
    db.close()
