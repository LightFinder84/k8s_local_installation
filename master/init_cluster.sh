# $0: server IP
sudo kubeadm init --apiserver-advertise-address=$1 --pod-network-cidr=10.244.0.0/16

# Generate join node token
echo 'sudo ' | sudo tee ./token.sh
sudo kubeadm token create --print-join-command | sudo tee ./token.sh

# config kubectl
mkdir -p $HOME/.kube
sudo cp -v /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# apply cni
kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml