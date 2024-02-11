# Install the following packages in the server/VM
### Create a packages directory to hold the packages and navigate into that 
``` bash
mkdir /root/packages
cd /root/packages
```
### Install etcd server
* install wget if it is not available by default
``` bash
yum install wget -y
```
* Download the etcd Binaries
``` bash
wget https://github.com/etcd-io/etcd/releases/download/v3.5.4/etcd-v3.5.4-linux-amd64.tar.gz
tar -xzvf etcd-v3.5.4-linux-amd64.tar.gz
cd etcd-v3.5.4-linux-amd64
cp etcd etcdctl /usr/local/bin/
```
* Extract the binaries using tar command
``` bash
tar -xzvf etcd-v3.5.4-linux-amd64.tar.gz
```
* Navigate into the binaries directory
``` bash
cd etcd-v3.5.4-linux-amd64
```
* copy the binaries into /usr/local/bin/
``` bash
cp etcd etcdctl /usr/local/bin/
```
### Install api server
* Downlaod the package
``` bash
wget https://dl.k8s.io/v1.24.2/kubernetes-server-linux-amd64.tar.gz
```
* Extract the binaries using tar command
``` bash
tar -xzvf kubernetes-server-linux-amd64.tar.gz
```
* Navigate into the binaries directory
``` bash
cd /root/packages/kubernetes/server/bin
```
* copy the binaries into /usr/local/bin/
``` bash
cp kube-apiserver kubectl /usr/local/bin/
```



