## Create Self signed certificate
* Creating a private key for Certificate Authority
  ``` bash
  mkdir /root/k8-certificates
  cd /root/k8-certificates/ ```
* Create key
  ``` bash
  openssl genrsa -out ca.key 4098
  ```
  ``` bash
  [root@k8security k8-certificates]# ls
  ca.key ```
