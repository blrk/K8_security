### Install kubeadm cluster
#### Install containerd
* Add containerd network configuration
``` sh
cat <<EOF | sudo tee /etc/modules-load.d/containerd.conf
overlay
br_netfilter
EOF
```
``` sh
modprobe overlay
modprobe br_netfilter
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
apt-get install -y containerd
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
systemctl status containerd
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
apt-get update
apt-get install -y apt-transport-https ca-certificates curl
curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-archive-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list

apt-get update
apt-cache madison kubeadm
apt-get install -y kubelet=1.24.2-00 kubeadm=1.24.2-00 kubectl=1.24.2-00 cri-tools=1.24.2-00
apt-mark hold kubelet kubeadm kubectl
```
* Initialize cluster with kubeadm (master node only)
``` bash
kubeadm init --pod-network-cidr=10.244.0.0/16 --kubernetes-version=1.24.2
```
* copy the kube config
``` bash
mkdir -p $HOME/.kub
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
chown $(id -u):$(id -g) $HOME/.kube/config
```
* install a network addon flannal on (master node)
``` bash
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```
* List the manifest files
``` bash
ls -l /etc/kubernetes/manifests
```
* Verify the k8s components status
``` bash
root@kubeadm:~# netstat -ntlp
```
``` bash
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      706/sshd: /usr/sbin 
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN      641/systemd-resolve 
tcp        0      0 127.0.0.1:2381          0.0.0.0:*               LISTEN      4222/etcd           
tcp        0      0 127.0.0.1:2379          0.0.0.0:*               LISTEN      4222/etcd           
tcp        0      0 127.0.0.1:10259         0.0.0.0:*               LISTEN      4211/kube-scheduler 
tcp        0      0 127.0.0.1:10257         0.0.0.0:*               LISTEN      4139/kube-controlle 
tcp        0      0 127.0.0.1:10249         0.0.0.0:*               LISTEN      4439/kube-proxy     
tcp        0      0 127.0.0.1:10248         0.0.0.0:*               LISTEN      4317/kubelet        
tcp        0      0 192.168.122.87:2380     0.0.0.0:*               LISTEN      4222/etcd           
tcp        0      0 192.168.122.87:2379     0.0.0.0:*               LISTEN      4222/etcd           
tcp        0      0 127.0.0.1:44071         0.0.0.0:*               LISTEN      2328/containerd     
tcp6       0      0 :::10250                :::*                    LISTEN      4317/kubelet        
tcp6       0      0 :::10256                :::*                    LISTEN      4439/kube-proxy     
tcp6       0      0 :::22                   :::*                    LISTEN      706/sshd: /usr/sbin 
tcp6       0      0 :::6443                 :::*                    LISTEN      4169/kube-apiserver 
```
##### Documentation Link:

https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/

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
### Install kubeadm cluster in Amazon Linux 2
* In terminal 1 login as root user
``` bash
sudo su -
```
* Download the installation script file
``` bash
wget https://raw.githubusercontent.com/blrk/K8-Practitioner/main/day2/install.sh
```
* Set executable permission
``` bash
chmod +x install.sh 
```
* Execute the install.sh script to install kubeadm cluster
``` bash
./install.sh 
```
* Initialise the kubeadm cluster
``` bash
kubeadm init --pod-network-cidr=192.168.0.0/16 --kubernetes-version=1.24.2
```
* copy the kubecofig file
``` bash
mkdir -p $HOME/.kube
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
chown $(id -u):$(id -g) $HOME/.kube/config
```
* Verify the k8s components status
``` bash
netstat -ntlp
```
``` bash
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      706/sshd: /usr/sbin 
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN      641/systemd-resolve 
tcp        0      0 127.0.0.1:2381          0.0.0.0:*               LISTEN      4222/etcd           
tcp        0      0 127.0.0.1:2379          0.0.0.0:*               LISTEN      4222/etcd           
tcp        0      0 127.0.0.1:10259         0.0.0.0:*               LISTEN      4211/kube-scheduler 
tcp        0      0 127.0.0.1:10257         0.0.0.0:*               LISTEN      4139/kube-controlle 
tcp        0      0 127.0.0.1:10249         0.0.0.0:*               LISTEN      4439/kube-proxy     
tcp        0      0 127.0.0.1:10248         0.0.0.0:*               LISTEN      4317/kubelet        
tcp        0      0 192.168.122.87:2380     0.0.0.0:*               LISTEN      4222/etcd           
tcp        0      0 192.168.122.87:2379     0.0.0.0:*               LISTEN      4222/etcd           
tcp        0      0 127.0.0.1:44071         0.0.0.0:*               LISTEN      2328/containerd     
tcp6       0      0 :::10250                :::*                    LISTEN      4317/kubelet        
tcp6       0      0 :::10256                :::*                    LISTEN      4439/kube-proxy     
tcp6       0      0 :::22                   :::*                    LISTEN      706/sshd: /usr/sbin 
tcp6       0      0 :::6443                 :::*                    LISTEN      4169/kube-apiserver 
```

* Install Calico network addon
``` bash
kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.26.4/manifests/tigera-operator.yaml
kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.26.4/manifests/custom-resources.yaml
```
##### Documentation Link:

* https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/

