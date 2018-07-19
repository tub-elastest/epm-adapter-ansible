import os
import sys
from collections import namedtuple
import logging

from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager

from ansible.plugins.callback import CallbackBase
import json
import time


class ResultCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin
    """

    def __init__(self):
        self.done = False
        self.metadata = {}

    def v2_runner_on_ok(self, result, **kwargs):
        """Print a json representation of the result

        This method could store the result in an instance attribute for retrieval later
        """
        logging.debug("TASK " + result.task_name + " HAS FAILED: " + str(result.is_failed()))
        logging.debug("TASK " + result.task_name + " RESULT: " + str(result._result))
        host = result._host
        self.metadata = result._result
        self.done = True


def execute_playbook(playbook_path):
    loader = DataLoader()

    inventory = InventoryManager(loader=loader, sources=["localhost"])
    variable_manager = VariableManager(loader=loader, inventory=inventory)

    if not os.path.exists(playbook_path):
        logging.debug('[INFO] The playbook does not exist')
        sys.exit()

    Options = namedtuple('Options',
                         ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection', 'module_path', 'forks',
                          'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args',
                          'sftp_extra_args', 'scp_extra_args', 'become', 'become_method', 'become_user',
                          'verbosity', 'check', 'diff'])

    options = Options(listtags=False, listtasks=False, listhosts=False, syntax=False, connection='local',
                      module_path=None,
                      forks=100, remote_user='root', private_key_file=None, ssh_common_args=None,
                      ssh_extra_args=None,
                      sftp_extra_args=None, scp_extra_args=None, become=False, become_method=None, become_user='root',
                      verbosity=None, check=False, diff=False)

    variable_manager.extra_vars = {'hosts': 'localhost'}  # This can accomodate various other command line arguments.`

    passwords = {}

    pbex = PlaybookExecutor(playbooks=[playbook_path], inventory=inventory, variable_manager=variable_manager,
                            loader=loader,
                            options=options, passwords=passwords)
    results = pbex.run()
    return results


def execute_play(play_source, with_metadata=False):
    loader = DataLoader()

    inventory = InventoryManager(loader=loader, sources=["localhost"])
    variable_manager = VariableManager(loader=loader, inventory=inventory)

    Options = namedtuple('Options',
                         ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection', 'module_path', 'forks',
                          'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args',
                          'sftp_extra_args', 'scp_extra_args', 'become', 'become_method', 'become_user',
                          'verbosity', 'check', 'diff'])

    options = Options(listtags=False, listtasks=False, listhosts=False, syntax=False, connection='local',
                      module_path=None,
                      forks=100, remote_user='root', private_key_file=None, ssh_common_args=None,
                      ssh_extra_args=None,
                      sftp_extra_args=None, scp_extra_args=None, become=False, become_method=None, become_user='root',
                      verbosity=None, check=False, diff=False)

    variable_manager.extra_vars = {'hosts': 'localhost'}

    passwords = {}
    # Instantiate our ResultCallback for handling results as they come in
    if (with_metadata):
        results_callback = ResultCallback()
    else:
        results_callback = None

    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

    # actually run it
    tqm = None
    try:
        tqm = TaskQueueManager(
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            options=options,
            passwords=passwords,
            stdout_callback=results_callback,  # Use our custom callback instead of the ``default`` callback plugin
        )
        result = tqm.run(play)

        if with_metadata:
            while (not results_callback.done):
                time.sleep(1)
                logging.debug("continue")
            result = results_callback.metadata

        return result

    finally:
        if tqm is not None:
            tqm.cleanup()
