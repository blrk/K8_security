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
useradd -m sam -s /bin/bash

```

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
Error from server (Forbidden): pods is forbidden: User "sam" cannot list resource "pods" in API group "" in the namespace "default"
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
Error from server (Forbidden): pods is forbidden: User "sam" cannot list resource "pods" in API group "" in the namespace "default"
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
* Note: connect without any authtication
* In terminal 2 list the APIs
``` bash
curl localhost:8085
curl localhost:8085/api/v1
```
#### Creating and binding a role
* Create a config directory and navigate into that 
``` bash
mkdir config && cd config/
```
* Create a file read-rbac.yaml
``` bash
vi read-rbac.yaml
```
``` bash
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-read-only
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list","create"]
- apiGroups: [""]
  resources: ["pods/exec"]
  verbs: ["create"]
```
```  bash
kubectl apply -f read-rbac.yaml 
role.rbac.authorization.k8s.io/pod-read-only created
```
``` bash
kubectl get role
NAME            CREATED AT
pod-read-only   2024-02-26T08:54:30Z
```
``` bash
kubectl describe role pod-read-only
Name:         pod-read-only
Labels:       <none>
Annotations:  <none>
PolicyRule:
  Resources  Non-Resource URLs  Resource Names  Verbs
  ---------  -----------------  --------------  -----
  pods/exec  []                 []              [create]
  pods       []                 []              [get watch list create]
```
* Create a role binding 
``` bash
vi rolebinding.yaml
```
``` bash
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: User
  name: sam
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-read-only
  apiGroup: rbac.authorization.k8s.io
```
``` bash
kubectl apply -f rolebinding.yaml
rolebinding.rbac.authorization.k8s.io/read-pods created
```
``` bash
kubectl get rolebinding
NAME        ROLE                 AGE
read-pods   Role/pod-read-only   31s
```
``` bash
kubectl describe rolebinding read-pods
Name:         read-pods
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  Role
  Name:  pod-read-only
Subjects:
  Kind  Name  Namespace
  ----  ----  ---------
  User  sam   
```
#### Login as user sam and verify
``` bash
su - john
```
* List the pods
``` bash
kubectl get pods
No resources found in default namespace.
```
* Create a pod
``` bash
kubectl run pod-sam --image=nginx
```
* Login into the pod
``` bash
kubectl exec -it pod-sam -- bash
```
* Verify the API access
``` bash
kubectl auth can-i create pods
yes
```
``` bash
kubectl auth can-i create deployments
no
```
* Try deleting the pod
``` bash
kubectl delete pods pod-sam
Error from server (Forbidden): pods "pod-sam" is forbidden: User "sam" cannot delete resource "pods" in API group "" in the namespace "default"
```
#### Creating Cluster Role
* In terminal 1 login as root user and navigate into config
``` bash
cd config
```
* Create dev, prod namespaces
``` bash
kubectl create namespace dev
namespace/dev created
kubectl create namespace prod
namespace/prod created
```
* Create cluster role
``` bash
vi clusterrole.yaml
```
``` bash
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list","create"]
- apiGroups: [""]
  resources: ["pods/exec"]
  verbs: ["create"]
```
``` bash
kubectl apply -f clusterrole.yaml 
clusterrole.rbac.authorization.k8s.io/cluster-pod-reader created
```
* Create cluster role binding for user sam 
``` bash
vi clusterrolebinding.yaml
```
``` bash
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: read-pods-global
subjects:
- kind: User
  name: sam
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: cluster-pod-reader
  apiGroup: rbac.authorization.k8s.io
```
``` bash
kubectl apply -f clusterrolebinding.yaml
clusterrolebinding.rbac.authorization.k8s.io/read-pods-global created
```
* Verify the cluster role
* In terminal 2 login as user sam
``` bash
kubectl run pod-sam-dev --image=nginx -n dev
pod/pod-sam-dev created
```
``` bash
kubectl exec -it -n dev pod-sam-dev -- bash
```
* Delete the cluster role
``` bash
kubectl delete -f clusterrolebinding.yaml
clusterrolebinding.rbac.authorization.k8s.io "read-pods-global" deleted
```
* Role binding to cluster role
``` bash
vi rolebind-cluster.yaml
```
``` bash
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: dev-pods
  namespace: dev
subjects:
- kind: User
  name: sam
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: cluster-pod-reader
  apiGroup: rbac.authorization.k8s.io
```
``` bash
kubectl apply -f rolebind-cluster.yaml
```
``` bash
kubectl exec -it -n dev pod-sam-dev -- bash
```

