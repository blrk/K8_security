### Implementing RBAC
#### User creation 
* Create a directory for certificates
``` bash
root@kubeadm:~# mkdir /root/k8_certificates
root@kubeadm:~# cd /root/k8_certificates/
```
* Create certificates for user sam
``` bash
openssl genrsa -out sam.key 4098
openssl req -new -key sam.key -subj "/CN=sam/O=developers" -out sam.csr
```
* Create Certificate signing request
* More info on certificate singing https://kubernetes.io/docs/reference/access-authn-authz/certificate-signing-requests/
``` bash
cat <<EOF | kubectl apply -f -
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: sam
spec:
  groups:
  - system:authenticated
  request: $(cat sam.csr | base64 | tr -d '\n')
  signerName: kubernetes.io/kube-apiserver-client
  usages:
  - client auth
EOF
```
* List the csr
``` bash
kubectl get csr
```
* Describe and view the csr
``` bash
kubectl describe csr sam
```
* Approve the certificate sigining Request 
``` bash
kubectl certificate approve sam
```
* Get the approved certificate 
``` bash
kubectl get csr sam -o jsonpath='{.status.certificate}' | base64 --decode > sam.crt
```
* Create user sam  
``` bash
useradd -m sam -s /bin/bash```

* Move the certificates to the home directory of the user "sam"
``` bash
cp sam.crt sam.key /home/sam && cp /etc/kubernetes/pki/ca.crt /home/sam
```
* Change the ownership of the certificates to john
``` bash
chown -R sam.sam /home/sam
```
* Switch user sam
``` bash
su - sam 
```
* List the pods 
``` bash
kubectl get pods --server=https://<ip_address>:6443 --client-certificate /home/sam/sam.crt --certificate-authority /home/sam/ca.crt --client-key /home/sam/sam.key
```
* Note: Replace the <ip_address> with the ip address of the ethernet interface
* You will see the following error
``` bash
Error from server (Forbidden): pods is forbidden: User "john" cannot list resource "pods" in API group "" in the namespace "default"
```
#### Create .kubeconfig file for the user
* Store the server ip in an environment variable 
``` bash
export SERVER_IP=<ip_address> For example -- 192.168.122.87
```
* Execute the following commands one by one 
``` bash
kubectl config set-cluster kubeadm \
    --certificate-authority=/home/sam/ca.crt \
    --embed-certs=true \
    --server=https://${SERVER_IP}:6443 \
    --kubeconfig=sam.kubeconfig

kubectl config set-credentials sam \
    --client-certificate=sam.crt \
    --client-key=sam.key \
    --embed-certs=true \
    --kubeconfig=sam.kubeconfig

kubectl config set-context default \
    --cluster=kubeadm \
    --user=sam \
    --kubeconfig=sam.kubeconfig
```
* set the default context
``` bash
kubectl config use-context default --kubeconfig=sam.kubeconfig
```
* List the pods
``` bash
kubectl get pods --kubeconfig=sam.kubeconfig
The connection to the server localhost:8080 was refused - did you specify the right host or port?
```
* Copy the kubeconfig file
``` bash
cp sam.kubeconfig ~/.kube/config
```
* List the pods
``` bash
kubectl get pods
```

#### Navigating the K8s API groups
* In Terminal 1 run the following command
``` bash
kubectl proxy --port 8085
```
* In terminal 2 list the APIs
``` bash
curl localhost:8085
curl localhost:8085/api/v1
```
#### Creating and binding a role








* Cluster role and cluster role binding
* Creating ingress controller and ingress resource
* Ingress security
* Create a service account and secure it