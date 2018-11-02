import sys
import os
from collections import namedtuple
import yaml
import logging
import tempfile

from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor


def execute_playbook(playbook_path, key_path):
    loader = DataLoader()

    inventory = InventoryManager(loader=loader, sources=["/etc/ansible/hosts"])
    variable_manager = VariableManager(loader=loader, inventory=inventory)

    if not os.path.exists(playbook_path):
        # logging.debug('[INFO] The playbook does not exist')
        sys.exit()

    Options = namedtuple('Options',
                         ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection', 'module_path', 'forks',
                          'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args',
                          'sftp_extra_args', 'scp_extra_args', 'become', 'become_method', 'become_user',
                          'verbosity', 'check', 'diff'])

    options = Options(listtags=False, listtasks=False, listhosts=False, syntax=False, connection='smart',
                      module_path=None,
                      forks=100, remote_user=None, private_key_file=key_path, ssh_common_args=None,
                      ssh_extra_args=None,
                      sftp_extra_args=None, scp_extra_args=None, become=False, become_method='sudo', become_user='root',
                      verbosity=None, check=False, diff=False)

    variable_manager.extra_vars = {}  # This can accomodate various other command line arguments.`

    passwords = {}

    pbex = PlaybookExecutor(playbooks=[playbook_path], inventory=inventory, variable_manager=variable_manager,
                            loader=loader,
                            options=options, passwords=passwords)
    results = pbex.run()
    return results


def modify_vars(playbook_path, master_ip, nodes_ip):
    with open(playbook_path + "group_vars/all.yaml") as f:
        group_vars = yaml.load(f.read())

    group_vars["node_ips"] = list(nodes_ip)
    group_vars["master_ip"] = master_ip

    with open(playbook_path + "group_vars/all.yaml", "w") as f:
        yaml.dump(group_vars, f, default_flow_style=False)


def install(playbooks_path, type, master_ip, nodes_ip, key):
    response = "Nothing installed"
    if type == "kubernetes" :
        logging.debug("Master IP: " + master_ip)
        logging.debug("Nodes IP: " + str(nodes_ip[:]))

        temp = tempfile.NamedTemporaryFile()
        with open(temp.name, 'w') as f:
            f.write(key)

        playbook_path = playbooks_path + "k8s-cluster/"
        modify_vars(playbook_path, master_ip, nodes_ip)

        response = execute_playbook(playbook_path + "site.yaml", temp.name)
        temp.close()
    elif type == "kubernetes-node":
        logging.debug("Master IP: " + master_ip)
        logging.debug("Node IP: " + str(nodes_ip[0]))

        temp = tempfile.NamedTemporaryFile()
        with open(temp.name, 'w') as f:
            f.write(key)

        playbook_path = playbooks_path + "k8s-cluster/"
        modify_vars(playbook_path, master_ip, nodes_ip)

        response = execute_playbook(playbook_path + "add_node.yaml", temp.name)
        temp.close()
    return response
