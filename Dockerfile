FROM python:2.7.16-stretch

RUN apt-get update && apt-get install -y build-essential autoconf libtool software-properties-common

RUN pip install grpcio grpcio-tools openstacksdk==0.13.0 ansible==2.5.5 requests shade==1.25.0 boto==2.49

ADD . ansible-client

WORKDIR ansible-client

EXPOSE 50052

ENTRYPOINT python -m run --register-adapter $EPM_IP $ADAPTER_IP --register-namespace $NAMESPACE
