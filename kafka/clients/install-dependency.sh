#!/bin/bash

sudo apt install -y software-properties-common
sudo apt apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.12 python3.12-venv

python3 -m venv $HOME/venv
source $HOME/venv/bin/activate
pip install --upgrade pip
pip install confluent-kafka