# Elastest Platform Manager Ansible adapter

The Ansible adapter compliant with ElasTest Platform Manager is used to launch OpenStack instances using ansible.
The ansible play file is passed along with an additional Metadata file in a package. 

The package has to be a **tar** file and has to have the following structure:
```bash
- Metadata.yaml #Simple metadata file that should include the name of the package
- play.yml #The play file
- key # Required if you want to communicate with the machine after instantiation is done
```

This is an example **Metadata** file:
```yaml
name: example-name
type: <openstack or aws>
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

```bash
pip install -r requirements.txt &&
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


At the moment the adapter supports launching OpenStack and Amazon Plays with these modules: ec2 and os_server. Other modules can still be used but only if they do not require authorisation or the authorisation should be provdied inside the play. 

In order to use the adapter the pop must be registered to EPM:

Example for AWS

```json
{
  "name": "aws", 
  "interfaceEndpoint": "amazon", 
  "interfaceInfo" : [
    {"key": "type", "value": "aws"},  
    {"key": "aws_access_key", "value": "<value>"}, 
    {"key": "aws_secret_key", "value": "<value>"},
    {"key":"region", "value":"<value>"}
  ], 
  "status": "active"
}
```
Example for Openstack

```json
{
  "name": "openstack-1", 
  "interfaceEndpoint": "openstack", 
  "interfaceInfo" : [
    {"key": "type", "value": "openstack"},  
    {"key": "username", "value": "<value>"}, 
    {"key": "password", "value": "<value>"}, 
    {"key": "project_name", "value": "<value>"}, 
    {"key": "auth_url", "value": "<value>"}
  ], 
  "status": "active"
}
```
The PoP should be sent via POST to http://ip-of-the-epm:8180/api/v1/pop

If you include any authorisation data inside play, as ansible allows to do, the authorisation data in supported modules described above will be updated to the one you have added as PoP

Here is an example of such a plays with one task, multiple tasks are supported but should all be executre on one PoP (AWS or Openstack):


```yaml
- name: launch
  hosts: localhost
  tasks:
    - name: launch an instance
      os_server:
        state: present
        name: vm1
        image: ubuntu-14.04-server-cloudimg-amd64-disk1
        key_name: key
        timeout: 200
        flavor: m1.small
        security_groups: default
        auto_ip: yes
        network: mgmt
```
```yaml
- name: launch
  hosts: localhost
  tasks:
    - name: launch an instance
      ec2:
        group: default
        instance_type: t2.micro
        image: ami-8a392060
        wait: true
        vpc_subnet_id: <subnet-id>
        assign_public_ip: yes
        key_name: <REQUIRED key provided in package as file named "key", should be generated in aws>
      register: ec2
```

It will launch an Ubuntu Virtual Machine in OpenStack or AWS and then perform the full set of runtime operations on it.
