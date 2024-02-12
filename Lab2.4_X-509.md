### Implement X509 client certificates 
* Navigate to the certificates folder
``` bash
cd /root/k8-certificates
```
* Creating Certificate for the user sam
``` bash
openssl genrsa -out sam.key 4098
openssl req -new -key sam.key -subj "/CN=sam/O=developers" -out sam.csr
openssl x509 -req -in sam.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out sam.crt -days 500
```
* Open kube-apiservice file and and Set ClientCA flag
``` bash
vi /etc/systemd/system/kube-apiserver.service
```
``` bash
--client-ca-file /root/k8-certificates/ca.crt
```
* Restart the kube-apiserver
``` bash
systemctl daemon-reload
systemctl restart kube-apiserver
systemctl status kube-apiserver
```
* Verify the access to sam user
``` bash
kubectl get secret --server=https://127.0.0.1:6443 --client-certificate /root/k8-certificates/sam.crt --certificate-authority /root/k8-certificates/ca.crt --client-key /root/k8-certificates/sam.key
```

