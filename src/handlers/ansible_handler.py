import tempfile
import src.handlers.ansible_executor as ansible_executor
import yaml
import random
import shelve
import logging

from src.grpc_connector.client_pb2 import ResourceGroupProto, Auth, Network, VDU, Key
supported_modules_aws = ['ec2', 'ec2_instance', 'ec2_subnet']
supported_modules_openstack = ['os_server', 'os_floating_ip', 'os_keypair', 'os_network', 'os_subnet', 'os_user']

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
    logging.info(play_as_dict)
    if auth['type'] == 'aws':
        for task in play_as_dict['tasks']:
            for module in task:
                if module in supported_modules_aws:
                    task[module]['aws_access_key'] = auth['aws_access_key']
                    task[module]['aws_secret_key'] = auth['aws_secret_key']
                    task[module]['region'] = auth['region']
                else:
                    logging.warn('%s either does not require or is not officially supported for authentification'%module)
    elif auth['type'] == 'openstack':
        for task in play_as_dict['tasks']:
            for module in task:
                if module in supported_modules_openstack:
                    task[module]['auth'] = {}
                    task[module]['auth']['username'] = auth['username']
                    task[module]['auth']['password'] = auth['password']
                    task[module]['auth']['auth_url'] = auth['auth_url']
                    task[module]['auth']['project_name'] = auth['project_name']
                else:
                    logging.warn('%s either does not require or is not officially supported for authentification'%module)
    logging.info(play_as_dict)
    try:
        rg_name = play_as_dict["name"]
    except:
        rg_name = str(random.randint(100, 999))

    response = ansible_executor.execute_play(play_as_dict, with_metadata=True)

    pops = []
    vdus = []
    ssh_key = Key(key=key.read())
    logging.debug("-----------------------------------------------------------------")
    #logging.debug(response)
    for r in response:
        if "os_server" in play_as_dict["tasks"][0]: #if we have been deploying on openstack
            if r.has_key("openstack"):       
                compute_id = r["openstack"]["id"]
                name = r["openstack"]["name"]
                imageName = r["openstack"]["image"]["name"]
                net = r["invocation"]["module_args"]["network"]
                ip = r["openstack"]["interface_ip"]
                vdu = VDU(name=name, imageName=imageName, netName=net, computeId=compute_id, ip=ip, key=ssh_key,
                                        metadata=[])   
                vdus.append(vdu)  
                
        else: #if we are deploying on aws
            imageName = play_as_dict["tasks"][0]["ec2"]["image"]
            if not r.has_key("instances"):
                continue
            for instance in r["instances"]:           
                compute_id = instance["id"]
                name = instance["id"]
                ip = instance["public_ip"]
                net_name = r["invocation"]["module_args"]["vpc_subnet_id"]
                vdu = VDU(name=name, imageName=imageName, netName=net_name, computeId=compute_id, ip=ip, key=ssh_key,
                                    metadata=[])   
                vdus.append(vdu)    

    networks = prepare_networks(play_as_dict)

    rg = ResourceGroupProto(name=rg_name, pops=pops, networks=networks, vdus=vdus)
    return rg



def prepare_networks(play_as_dict):
    nets = []
    for task in play_as_dict["tasks"]:
        for module in task:
            if module == "ec2":
                net = Network(name=task[module]["vpc_subnet_id"], cidr="", poPName="ansible-aws", networkId="id")               
                if list(filter((lambda x: x.name == task[module]["vpc_subnet_id"]), nets)) == []:             
                    nets.append(net)
            elif module == "os_server":
                net = Network(name=task[module]["network"], cidr="", poPName="ansible-openstack", networkId="id")
                if list(filter(lambda x: x.name == task[module]["network"], nets)) == []:
                    nets.append(net)
    return nets


