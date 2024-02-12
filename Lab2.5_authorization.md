### Implement Authorization modes
* Enable always deny auth mode
* open the api-server service file
``` bash
vi /etc/systemd/system/kube-apiserver.service
```
* add the following line
``` bash
--authorization-mode=AlwaysDeny 
```
* Restart the kube-apiserver
``` bash
systemctl daemon-reload
systemctl restart kube-apiserver
systemctl status kube-apiserver
```
``` bash
* Try to access a secret resource from the cluster
kubectl get secret --server=https://127.0.0.1:6443 --client-certificate /root/k8-certificates/sam.crt --certificate-authority /root/k8-certificates/ca.crt --client-key /root/k8-certificates/sam.key
```
``` bash
Error from server (Forbidden): secrets is forbidden: User "system:anonymous" cannot list resource "secrets" in API group "" in the namespace "default": Everything is forbidden.
```
* Note: Now everything is forbiden because of always deny
### Enabling RBAC authentication
* open the api-server service file
``` bash
vi /etc/systemd/system/kube-apiserver.service
```
* Modify the authorization mode as RBAC
``` bash
--authorization-mode=RBAC
```
* Restart the kube-apiserver
``` bash
systemctl daemon-reload
systemctl restart kube-apiserver
systemctl status kube-apiserver
```
* Try to access a secret resource from the cluster
``` bash 
kubectl get secret --server=https://127.0.0.1:6443 --client-certificate /root/k8-certificates/sam.crt --certificate-authority /root/k8-certificates/ca.crt --client-key /root/k8-certificates/sam.key
```
``` bash
Error from server (Forbidden): secrets is forbidden: User "system:anonymous" cannot list resource "secrets" in API group "" in the namespace "default"
```
* Note: this time we received a different error because the right access is not mentioned for the user sam
#### Create admin/Super User
* Navigate to the certificates directory 
``` bash
cd /root/k8-certificates/
```
* Create the certificates for the admin user
``` bash
openssl genrsa -out rk.key 4098
openssl req -new -key rk.key -subj "/CN=rk/O=system:masters" -out rk.csr
openssl x509 -req -in rk.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out rk.crt -extensions v3_req  -days 500
```
* Verify the access
``` bash
kubectl get secret --server=https://127.0.0.1:6443 --client-certificate /root/k8-certificates/rk.crt --certificate-authority /root/k8-certificates/ca.crt --client-key /root/k8-certificates/rk.key
```


