#!/bin/bash

HOST_NAME="$1"
MASTER_NODE_IP="$2"
NODE_IP="$3"
MASTER_USER="$4"
KEYPAIR="$5"

if [ -z "$HOST_NAME" ]; then
    echo "❌ Error: Missing HOST_NAME argument."
    echo "Usage: $0 <HOST_NAME> <MASTER_IP> <NODE_IP> <MASTER_USER> [KEYPAIR_FILE]"
    exit 1
fi

if [ -z "$MASTER_NODE_IP" ]; then
    echo "❌ Error: Missing MASTER_IP argument."
    echo "Usage: $0 <HOST_NAME> <MASTER_IP> <NODE_IP> <MASTER_USER> [KEYPAIR_FILE]"
    exit 1
fi

if [ -z "$NODE_IP" ]; then
    echo "❌ Error: Missing NODE_IP argument."
    echo "Usage: $0 <HOST_NAME> <MASTER_IP> <NODE_IP> <MASTER_USER> [KEYPAIR_FILE]"
    exit 1
fi

if [ -z "$MASTER_USER" ]; then
    echo "❌ Error: Missing MASTER_USER argument."
    echo "Usage: $0 <HOST_NAME> <MASTER_IP> <NODE_IP> <MASTER_USER> [KEYPAIR_FILE]"
    exit 1
fi

if [ -z "$KEYPAIR" ]; then
    echo "KEYPAIR VALUE IS NOT SPECIFIED. USING PASSWORD AUTHENTICATION FOR MASTER SSH CONNECTION."
fi

echo "✅ Arguments successfully provided:"
echo "   Host Name: $HOST_NAME"
echo "   Master IP: $MASTER_NODE_IP"
echo "   Host IP:   $NODE_IP"
echo "   Master user:   $MASTER_USER"
echo "   Keypair:   $KEYPAIR"

# Ask for confirmation
echo -n "Do you wish to proceed with these settings? (yes/no): "
read PROCEED

# Check user input
if [[ "$PROCEED" =~ ^[Yy][Ee]?[Ss]?$ ]]; then
    echo "👍 User confirmed. Continuing script execution..."
else
    echo "🛑 Operation cancelled by user."
    # Exit here to stop the script if the user cancels
    exit 0
fi

# Set hostname
sudo hostnamectl hostname ${HOST_NAME}

# disable swap
sudo swapoff -a
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab

# disable firewall
sudo ufw disable
sudo systemctl stop ufw
sudo systemctl disable ufw

# enable kernel modules
sudo cp ./kernel_modules.conf /etc/modules-load.d/k8s.conf
sudo modprobe overlay
sudo modprobe br_netfilter

# enable network config
sudo cp ./network.conf /etc/sysctl.d/k8s.conf
sudo sysctl --system

# install ssh
sudo apt update
sudo apt install -y openssh-server
sudo systemctl start ssh
sudo systemctl enable ssh

# Install containerd
sudo apt-get update && sudo apt-get install -y containerd

# config containerd
sudo mkdir -p /etc/containerd
sudo containerd config default | sudo tee /etc/containerd/config.toml
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/g' /etc/containerd/config.toml
sudo sed -i 's/pause:3.8/pause:3.10.1/g' /etc/containerd/config.toml
sudo systemctl restart containerd 
sudo systemctl enable containerd

# Install tools
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg

# Add k8s repo
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.34/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.34/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list

# Install k8s tools & images
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

# specify correct IP of current node
sudo sed -i 's/KUBELET_EXTRA_ARGS=/KUBELET_EXTRA_ARGS="--node-ip='"${NODE_IP}"'"/g' /etc/default/kubelet
sudo systemctl daemon-reload
sudo systemctl restart kubelet

# JOIN NODE
if [ -z "$KEYPAIR" ]; then
    # missing keypair
    scp ${MASTER_USER}@${MASTER_NODE_IP}:/home/${MASTER_USER}/k8s_local_installation/k8s/token.sh ./token.sh
else
    # has keypair
    chmod 400 ${KEYPAIR}
    scp -i ${KEYPAIR} ${MASTER_USER}@${MASTER_NODE_IP}:/home/${MASTER_USER}/k8s_local_installation/k8s/token.sh ./token.sh
fi

sudo sed -i 's/kubeadm/sudo kubeadm/g' token.sh
chmod +x token.sh
./token.sh
