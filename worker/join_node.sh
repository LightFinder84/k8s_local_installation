MASTER_ADDRESS=$1
scp truong@${MASTER_ADDRESS}:/home/truong/setup/token.sh ./token.sh
sudo sed -i 's/kubeadm/sudo kubeadm/g' token.sh
chmod +x token.sh
./token.sh