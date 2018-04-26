[![License badge](https://img.shields.io/badge/license-Apache2-orange.svg)](http://www.apache.org/licenses/LICENSE-2.0)
[![Docker badge](https://img.shields.io/docker/pulls/elastest/epm-adapter-anislbe.svg)](https://hub.docker.com/r/elastest/epm-adapter-ansible/)

<!-- Elastest logo -->
[![][ElasTest Logo]][ElasTest]

Copyright © 2017-2019 [ElasTest]. Licensed under [Apache 2.0 License].

elastest/epm-adapter-ansible
==============================

What is epm-adapter-ansible?
==============================

The ansible adapter compliant to the EPM is used to launch OpenStack instances using ansible. The ansible play file is passed along with an additional Metadata file in a package. 

# Supported tags and respective `Dockerfile` links

# Quick reference

-	**Where to get help**:  
	[the ElastTest mailing list][ElasTest Public Mailing List], [the Elastest Slack][ElasTest Slack], or [Stack Overflow][StackOverflow]

-	**Where to file issues**:  
	Issues and bug reports should be posted to the [GitHub ElasTest Bugtracker].

-	**Maintained by**:  
	[the ElasTest community](https://github.com/elastest)

-	**Published image artifact details**:
	(image metadata, transfer size, etc).

-	**Source of this description**:  
	[docs repo's `template/` directory](https://github.com/mpauls/epm-adapter-ansible/blob/master/docs/Docker-epm-adapter-ansible.md) ([history](https://github.com/mpauls/epm-adapter-ansible/commits/master/docs/Docker-epm-adapter-ansible.md))

-	**Supported Docker versions**:  
	[the latest release](https://github.com/docker/docker/releases/latest) (down to 17.03.1 on a best-effort basis)

# What's on this image?


The adapter is implemented using **python2.7** and the ansible and gRPC libraries.


# How to use this image


To start the adapter in a docker container run this command:
```bash
docker run -p 50052:50052 --expose 50052 -i -t epm-adapter-ansible
```

If you want to start both the Elastest Platform Manager and the Ansible adapter you can use this [docker-compose](https://github.com/elastest/elastest-platform-manager/blob/master/docker-compose-epm.yml).



This will create the docker container for both the adapter and the EPM and will also automatically register the adapter to the EPM, so you can start using them straight away.


The package has to be a **tar** file and has to have the following structure:

```bash
- metadata.yaml #Simple metadata file that should include the name of the package
- docker-compose.yml #The docker-compose file
```

This is an example **Metadata** file:
```yaml
name: example-name
type: ansible
```

## Dependencies (other containers or tools)


none


## Integration with other containers or tools)


none

[Apache 2.0 License]: http://www.apache.org/licenses/LICENSE-2.0
[ElasTest]: http://elastest.io/
[ElasTest Logo]: http://elastest.io/images/logos_elastest/elastest-logo-gray-small.png
[ElasTest Twitter]: https://twitter.com/elastestio
[GitHub ElasTest Group]: https://github.com/elastest
[GitHub ElasTest Bugtracker]: https://github.com/elastest/bugtracker
[ElasTest Public Mailing List]: https://groups.google.com/forum/#!forum/elastest-users
[StackOverflow]: http://stackoverflow.com/questions/tagged/elastest
[ElasTest Slack]: elastest.slack.com
