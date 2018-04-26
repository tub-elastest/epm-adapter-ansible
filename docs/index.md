# Elastest Platform Manager Ansible adapter

The Ansible adapter compliant with ElasTest Platform Manager is used to launch OpenStack instances using ansible.
The ansible play file is passed along with an additional Metadata file in a package. 

The package has to be a **tar** file and has to have the following structure:
```bash
- Metadata.yaml #Simple metadata file that should include the name of the package
- play.yml #The play file
- key # Optional to specify the
```

This is an example **Metadata** file:
```yaml
name: example-name
type: ansible
```

You have to include the private key for doing runtime operations on the launched instances. It should correspond to the 
key specified in the play. You can either add it in the package with the name 'key' or set a 'keypath' in the metadata
where the adapter can find it.

The adapter is implemented using **python2.7** and the Ansible and gRPC libraries.

## Launching the adapter

The adapter has to be started using the **run.py** file. The default port of the adapter is 50052.

```bash
python -m run
```

If the EPM is already running you can make the adapter register itself on the EPM automatically. In this case the PoP
is not specified, because it is part of the play.

```yaml
python -m run --register-adapter <epm-ip> <compose-adapter-ip>
```

## Launching the adapter in a docker container

To start the adapter in a docker container run this command:
```bash
docker run -p 50052:50052 --expose 50052 -i -t elastest/epm-adapter-ansible
```

## Launching the adapter and the EPM with Docker-Compose

If you want to start both the Elastest Platform Manager and the Ansible adapter you can use this [docker-compose](https://github.com/elastest/elastest-platform-manager/blob/master/docker-compose-epm.yml).

## Usage

**Note:** The ansible adapter is still in development and therefore provides only a limited number of use cases
 (considering the number of Virtual Environments supported by ansible). 
 
At the moment the adapter only fully supports launching OpenStack Plays. Here is an example of such a play:

```yaml
- name: launch
  hosts: localhost
  tasks:
    - name: launch an instance
      os_server:
        state: present
        auth:
          auth_url: <REPLACE>
          username: admin
          password: <REPLACE>
          project_name: admin
        name: vm1
        image: ubuntu-14.04-server-cloudimg-amd64-disk1
        key_name: key
        timeout: 200
        flavor: m1.small
        security_groups: default
        auto_ip: yes
        network: mgmt
```

It will launch an Ubuntu 14.04 Virtual Machine in OpenStack and then perform the full set of runtime operations on it.