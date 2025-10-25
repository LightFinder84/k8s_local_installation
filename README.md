# Installation scripts for Kuberntes

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)

## About <a name = "about"></a>

This is the scripts for Kubernetes local installation (local network).

## Getting Started <a name = "getting_started"></a>

These instructions will get you setup a simple kubernetes cluster on your local network for development and learning purposes.

### Prerequisites

- Git

## Usage <a name = "usage"></a>

### For Control-plane node
- Clone this source code on your cluster's node.
```bash
git clone https://github.com/LightFinder84/k8s_local_installation.git
```
- Run the commands below:
```bash
cd k8s_local_installation
./master_setup.sh hostname ip
```
> hostname: your desired hostname for the control-plane node. Eg: master

> ip: IP address of the current node. Eg: 192.168.3.7

### For Worker node
> The control-plane node must be up and running at this step.
- Clone this source code on your cluster's node.
```bash
git clone https://github.com/LightFinder84/k8s_local_installation.git
```
- Run the commands below:
```bash
cd k8s_local_installation
./worker_setup.sh hostname ip
```
> hostname: your desired hostname for the worker node. Eg: worker01

> ip: the IP address of the control-plane node


### Check the result
At your control-plane node, run the command below:
```bash
kubectl get nodes
```
A list of your nodes will be displayed.
