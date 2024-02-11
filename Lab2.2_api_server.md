### Running API server in secure mode
* Navigate to the certificate folder 
``` bash
cd /root/k8-certificates/
```
* Generate client (etcd) certificate for api server 
``` bash
[root@k8security k8-certificates]# openssl genrsa -out apiserver.key 4098
[root@k8security k8-certificates]# openssl req -new -key apiserver.key -subj "/CN=kube-apiserver" -out apiserver.csr
[root@k8security k8-certificates]# openssl x509 -req -in apiserver.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out apiserver.crt -extensions v3_req  -days 500 
```
* Create Service Account Certificates
``` bash
[root@k8security k8-certificates]# openssl genrsa -out service-account.key 4098
[root@k8security k8-certificates]# openssl req -new -key service-account.key -subj "/CN=service-accounts" -out service-account.csr
[root@k8security k8-certificates]# openssl x509 -req -in service-account.csr -CA ca.crt -CAkey ca.key -CAcreateserial  -out service-account.crt -days 500
```
* Start API server with certificates
``` bash
kube-apiserver --advertise-address=159.65.147.161 --etcd-cafile=/root/k8-certificates/ca.crt --etcd-certfile=/root/k8-certificates/apiserver.crt --etcd-keyfile=/root/k8-certificates/apiserver.key --service-cluster-ip-range 10.0.0.0/24 --service-account-issuer=https://127.0.0.1:6443 --service-account-key-file=/root/k8-certificates/service-account.crt --service-account-signing-key-file=/root/k8-certificates/service-account.key --etcd-servers=https://127.0.0.1:2379
```
