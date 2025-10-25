HOST_NAME=$1
HOST_IP=$2

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
sudo kubeadm config images pull

# $0: server IP
sudo kubeadm init --apiserver-advertise-address=${HOST_IP} --pod-network-cidr=10.244.0.0/16

# Generate join node token
echo 'sudo ' | sudo tee ./token.sh
sudo kubeadm token create --print-join-command | sudo tee ./token.sh

# config kubectl
mkdir -p $HOME/.kube
sudo cp -v /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# apply cni
kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml