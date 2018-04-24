FROM python:2.7.12

RUN apt-get update && apt-get install -y build-essential autoconf libtool software-properties-common

RUN pip install grpcio grpcio-tools ansible==2.4.2.0 requests shade

ADD . ansible-client

WORKDIR ansible-client

EXPOSE 50052

ENTRYPOINT python -m run --register-pop
