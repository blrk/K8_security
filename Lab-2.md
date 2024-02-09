## Create Self signed certificate
* Creating a private key for Certificate Authority
  ``` bash
  mkdir /root/k8-certificates
  cd /root/k8-certificates/
  ```
  
* Create key
  ``` bash
  openssl genrsa -out ca.key 4098
  ```
  
  ``` bash
  [root@k8security k8-certificates]# ls
  ca.key
  ```

* Create CSR
  ``` bash
  openssl req -new -key ca.key -subj "/CN=K8s-CA" -out ca.csr
  ```

  ```bash
  [root@k8security k8-certificates]# ll
  total 8
  -rw-r--r--. 1 root root 1582 Feb  9 15:44 ca.csr
  -rw-------. 1 root root 3272 Feb  9 15:40 ca.key
  ```
* Self-sign the CSR

``` bash
openssl x509 -req -in ca.csr -signkey ca.key -CAcreateserial  -out ca.crt -days 500

Certificate request self-signature ok
subject=CN = K8s-CA
```
### I-Transit encryption etcd
* Install net-tools and tcp dump
``` bash
yum install net-tools tcpdump -y
```
* In Terminal 1: start the etcd server
``` bash
etcd
```
* In terminal 2: Fetch the tcp dump from port 2379
``` bash
tcpdump -i lo -X  port 2379
```
* In terminal 3: Run etcdctl commands to store and read a value
``` bash
etcdctl put axess "k8-lab"
etcdctl get axess
```


  

