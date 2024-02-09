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
  openssl req -new -key ca.key -subj "/CN=K8s-CA" -out ca.csr ```

  ```bash
  [root@k8security k8-certificates]# ll
  total 8
  -rw-r--r--. 1 root root 1582 Feb  9 15:44 ca.csr
  -rw-------. 1 root root 3272 Feb  9 15:40 ca.key
  ```

  

