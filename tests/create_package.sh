#!/bin/bash

rm ansible-package.tar
tar -cvf ansible-package.tar key metadata.yaml play.yaml 
