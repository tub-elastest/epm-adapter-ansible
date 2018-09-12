import tempfile
import src.handlers.ansible_executor as ansible_executor
import yaml
import random
import shelve
import logging

from src.grpc_connector.client_pb2 import ResourceGroupProto, Auth, Network, VDU


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

   

    pops = []
    vdus = []
    networks = []
    imageName = ""
    compute_id = ""
    net = None
    nets = []
    ip = ""
    if "os_server" in play_as_dict["tasks"][0]: #if we have been deploying on openstack
        if not r.has_key("openstack"):
            logging.error("It was either not possible to execute the play or it was not an openstack play. Please check if everything " +
                " specified in the play is already in the OpenStack instance and that the auth credentials are correct.")
            raise ValueError("Could not instantiate VM!")


        net_name = play_as_dict["tasks"][0]["os_server"]["network"]
        net = Network(name=net_name, cidr="", poPName="ansible", networkId="id")
        compute_id = r["openstack"]["id"]
        name = r["openstack"]["name"]
        imageName = r["openstack"]["image"]["name"]
        nets = r["openstack"]["addresses"]

        ip = r["openstack"]["interface_ip"]
        save_to_db(compute_id, auth, "auth")
    else: #if we are deploying on aws
        logging.debug("-----------------------------------------------------------------")
        logging.debug(r)
        pops = []
        vdus = []
        networks = []
        net_name = play_as_dict["tasks"][0]["ec2"]["vpc_subnet_id"]
        imageName = play_as_dict["tasks"][0]["ec2"]["image"]
        net = Network(name=net_name, cidr="", poPName="ansible-aws", networkId=net_name)
        for instance in r["instances"]:           
            compute_id = instance["id"]
            name = instance["id"]
            ip = instance["public_ip"]    
            vdu = VDU(name=name, imageName=imageName, netName=net_name, computeId=compute_id, ip=ip,
                                 metadata=[])   
            vdus.append(vdu)    
            save_to_db(compute_id, play_as_dict["tasks"][0]["ec2"], "auth")
    
    
    if key is not None:
        save_to_db(ip, key.read(), "key")
    elif keypath is not None:
        save_to_db(ip, keypath, "keypath")

    vdu = VDU(name=name, imageName=imageName, netName=net_name, computeId=compute_id, ip=ip,
                                 metadata=[])

    networks.append(net)
    

    rg = ResourceGroupProto(name=rg_name, pops=pops, networks=networks, vdus=vdus)
    return rg


def save_to_db(name, value, type):
    db = shelve.open('auths.db')
    db[str(name) + "_" + type] = value
    db.close()
