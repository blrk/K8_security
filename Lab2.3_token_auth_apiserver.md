### Implementing token authentication for kube-apiserver
* Create a token directory and navigate into that
``` bash
mkdir /root/tokens
cd /root/tokens
```
* Create a token file and add the following data
``` bash
echo Myp@ssw0rd#,sam,01,admins > /root/tokens/token.csv
```
* Add the token auth flag in the kube-apiserver service file
``` bash
vi /etc/systemd/system/kube-apiserver.service
```
``` bash
--token-auth-file /root/tokens/token.csv
```
``` bash
[Service]
ExecStart=/usr/local/bin/kube-apiserver --advertise-address=192.168.122.108 --token-auth-file /root/tokens/token.csv --etcd-cafile=/root/k8-certificates/ca.crt --etcd-certfile=/root/k8-certificates/apiserver.crt --etcd-keyfile=/root/k8-certificates/apiserver.key --etcd-servers=https://127.0.0.1:2379 --service-account-key-file=/root/k8-certificates/service-account.crt --service-cluster-ip-range=10.0.0.0/24 --service-account-signing-key-file=/root/k8-certificates/service-account.key --service-account-issuer=https://127.0.0.1:6443 --tls-cert-file=/root/k8-certificates/kube-api.crt --tls-private-key-file=/root/k8-certificates/kube-api.key 
```
* Restart the service
``` bash
systemctl daemon-reload
systemctl restart kube-apiserver
systemctl status kube-apiserver
```
* Verify the authentication
``` bash
curl -k --header "Authorization: Bearer Myp@ssw0rd#" https://localhost:6443
```
``` bash
{
  "paths": [
    "/.well-known/openid-configuration",
    "/api",
    "/api/v1",
    "/apis",
    "/apis/",
    "/apis/admissionregistration.k8s.io",
    "/apis/admissionregistration.k8s.io/v1",
    "/apis/apiextensions.k8s.io",
    "/apis/apiextensions.k8s.io/v1",
    "/apis/apiregistration.k8s.io",
    "/apis/apiregistration.k8s.io/v1",
    "/apis/apps",
    "/apis/apps/v1",
    "/apis/authentication.k8s.io",
    "/apis/authentication.k8s.io/v1",
    "/apis/authorization.k8s.io",
    "/apis/authorization.k8s.io/v1",
    "/apis/autoscaling",
    "/apis/autoscaling/v1",
    "/apis/autoscaling/v2",
    "/apis/autoscaling/v2beta1",
    "/apis/autoscaling/v2beta2",
    "/apis/batch",

```
* Try to access a secret resource which does not exist using static token 
``` bash
kubectl get secret --server=https://localhost:6443 --token Myp@ssw0rd# --insecure-skip-tls-verify
```
* Create and delete a secret using static token 
``` bash
kubectl create secret generic my-secret --server=https://localhost:6443 --token Myp@ssw0rd# --insecure-skip-tls-verify
kubectl delete secret my-secret --server=https://localhost:6443 --token Myp@ssw0rd# --insecure-skip-tls-verify
```
#### Evaluate the disadvanatge of token based authentication
* add a new user token into the csv file 
* delete the user sam 
* delete the user entry sam 
* Try to create a secret using the token of user sam
* restart the kube-apiserver
* try to create a secret using the token of user sam
* Open the api-server service file and remove the "--token-auth-file" entry
* Restart the service