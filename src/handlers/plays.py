def launch_instance_play(os_auth_url, os_username, os_password, os_project):
    return dict(name="create",
                hosts='localhost',
                gather_facts='no',
                tasks=[
                    dict(os_server=dict(state='present', auth=dict(auth_url=os_auth_url, username=os_username,
                                                                   password=os_password, project_name=os_project),
                                        name="vm1", timeout="200", image="ubuntu-14.04-server-cloudimg-amd64-disk1",
                                        key_name="rvl", flavor="m1.small",
                                        security_groups="default", auto_ip="yes", network="private", wait='yes'),
                         register='shell_out')
                ])


# start server
def stop_instance_play(name, os_auth_url, os_username, os_password, os_project):
    return dict(
        name="stop",
        hosts='localhost',
        gather_facts='no',
        tasks=[
            dict(os_server_action=dict(action='stop', auth=dict(auth_url=os_auth_url, username=os_username,
                                                                password=os_password, project_name=os_project),
                                       server=name, timeout="200", wait="yes"), register='shell_out')
        ]
    )


def start_instance_play(name, os_auth_url, os_username, os_password, os_project):
    return dict(
        name="start",
        hosts='localhost',
        gather_facts='no',
        tasks=[
            dict(os_server_action=dict(action='start', auth=dict(auth_url=os_auth_url, username=os_username,
                                                                 password=os_password, project_name=os_project),
                                       server=name, timeout="200", wait="yes"), register='shell_out')
        ]
    )


def get_data_play(name, os_auth_url, os_username, os_password, os_project):
    return dict(
        name="get metadata",
        hosts='localhost',
        gather_facts='no',
        tasks=[
            dict(os_server_facts=dict(auth=dict(auth_url=os_auth_url, username=os_username,
                                                password=os_password, project_name=os_project),
                                      server=name, timeout="200", wait="yes")),
            dict(debug=dict(var="openstack_servers"))
        ]
    )


def delete_instance_play(name, os_auth_url, os_username, os_password, os_project):
    return dict(name="create",
                hosts='localhost',
                gather_facts='no',
                tasks=[
                    dict(os_server=dict(state='absent', auth=dict(auth_url=os_auth_url, username=os_username,
                                                                  password=os_password, project_name=os_project),
                                        name=name, timeout="200", wait='yes'), register='shell_out')
                ])
