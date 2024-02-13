### Install kubeadm cluster
#### Install containerd
* Add containerd network configuration
``` bash
cat <<EOF | sudo tee /etc/modules-load.d/containerd.conf
overlay
br_netfilter
EOF
```
* Enable ip forward settings 
``` bash
cat <<EOF | sudo tee /etc/sysctl.d/99-kubernetes-cri.conf
net.bridge.bridge-nf-call-iptables  = 1
net.ipv4.ip_forward                 = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF
```
* Upadte the kernal parameters 
``` bash
sysctl --system
```
* Install containerd
``` bash
apt install -y containerd
```
* Create a directory to store the containerd configuration
``` bash
mkdir -p /etc/containerd
```
* Copy the default config to the continerd directory
``` bash
containerd config default > /etc/containerd/config.toml
```
* edit the config file and search for "SystemdCgroup" and set it as "true"
``` bash
vi /etc/containerd/config.toml
```
* restart the containerd service
``` bash
systemctl restart containerd
```
* Add the following kernal parameterer configuration
``` bash
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF
```
* Upadte the kernal parameters 
``` bash
sysctl --system
```
### Install kubeadm cluster. Run the steps one by one
* Switch off the swap
``` bash
swapoff -a
```
* Configure the repo
``` bash
apt update
apt install -y apt-transport-https ca-certificates curl
curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-archive-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list

apt update
apt-cache madison kubeadm
apt install -y kubelet=1.24.2-00 kubeadm=1.24.2-00 kubectl=1.24.2-00 cri-tools=1.24.2-00
apt-mark hold kubelet kubeadm kubectl
```
* Initialize cluster with kubeadm (master node only)
``` bash
kubeadm init --pod-network-cidr=10.244.0.0/16 --kubernetes-version=1.24.2
```
* Note: Suppose if you receive the following error run the error fix step
``` bash
error execution phase preflight: [preflight] Some fatal errors occurred:
	[ERROR FileContent--proc-sys-net-bridge-bridge-nf-call-iptables]: /proc/sys/net/bridge/bridge-nf-call-iptables does not exist
```
* Error fixing step
``` bash
modprobe br_netfilter
sysctl -p /etc/sysctl.conf
```
``` bash
sysctl --system
```
* Run the kubeadm init command 
``` bash
kubeadm init --pod-network-cidr=10.244.0.0/16 --kubernetes-version=1.24.2
```
* copy the kube config
``` bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```
* install a network addon flannal on (master node)
``` bash
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```
* List the manifest files
``` bash
ls -l /etc/kubernetes/manifests
```
