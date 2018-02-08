FROM python:2.7.12

RUN apt-get update && apt-get install -y build-essential autoconf libtool software-properties-common

RUN pip install grpcio grpcio-tools ansible==2.4.2.0 requests

RUN apt-get install -y ansible

ADD . ansible-client

WORKDIR ansible-client

ENTRYPOINT python -m run
