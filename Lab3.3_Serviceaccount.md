### Create and manage service accounts (SA)
#### Pod using Service account
Note: Perform the following 
* List all the existing service accouts
``` bash
kubectl get sa --all-namespaces
```
* connect to the running pod
``` bash
kubectl exec -it service-backend-pod -- bash
```
* Navigate into the service account folder
``` bash
cd /var/run/secrets/kubernetes.io/serviceaccount/
```
* list the files
``` bash
ls    
ca.crt	namespace  token
```
* print the contents of token
``` bash
cat token
```
* Store the token in a variable
``` bash
token=$(cat token)
cat $token
```
* Print the cluster info (Perform this step in terminal 2) and copy the control plane URL.
``` bash
kubectl cluster-info
```
* In the container run the following command
``` bash
curl -k -H "Authorization: Bearer $token" https://192.168.122.87:6443/api/v1 
```
* exit from the container
``` bash
exit
```
#### Service accounts and namespaces
* Note: Every namspace has a default service account, to list it use the following command 
``` bash
kubectl get sa
```
* List the service accounts from the namespace kube-system. Notice that deafult service account is also listed. 
``` bash
kubectl get sa -n kube-system
```
* Create a namespace and verify the defauklt service account creation 
``` bash
kubectl create namespace axess-academy
kubectl get sa -n axess-academy
```
* Note : The default service accounts get no permissions except API discovery
#### Assigning pods to service accounts
* Create a pod in the axess-academy namespace and describe it and notice it uses the dafult SA
``` bash
kubectl run nginx-pod -n axess-academy --image=nginx
kubectl get pods -n axess-academy
kubectl describe pod nginx-pod -n axess-academy
```
#### Configure Service Accounts for Pods
* DOC link https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/
* 
``` bash
kubectl exec -it -n axess-academy nginx-pod -- bash
```
``` bash
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
echo $TOKEN
```
``` bash
curl -k -H "Authorization: Bearer $TOKEN" https://192.168.122.87:6443/api/v1 
curl -k -H "Authorization: Bearer $TOKEN" https://192.168.122.87:6443/api/v1/namespaces
```
* Exit from the pod
``` bash
exit
```
* List the SA
``` bash
kubectl get sa -n axess-academy
```
* edit the SA and add "automountServiceAccountToken: false" below the kind:
``` bash
k edit sa default -n axess-academy
```
* Verify the effect by creating another pod 
``` bash
kubectl run nginx-pod-2 --image=nginx -n axess-academy
```
``` bash
 kubectl exec -it nginx-pod-2 -n axess-academy -- bash
```
``` bash
ls /run/
```
* Note: No service account related files
* Disable service from the pod level
``` bash
vi pod1.yml
```
``` bash
apiVersion: v1
kind: Pod
metadata:
  name: pod-1
spec:
  automountServiceAccountToken: false
  containers:
  - image: nginx
    name: demo-pod
```
``` bash
kubectl create -f pod1.yml 
```
``` bash
kubectl exec -it pod-1 -- bash
```
``` bash
ls /run/
```
#### Verify the Automounting removed in SA level enabled in pod level
* Create a pod in axess-acdemy namespace
``` bash
vi pod3.yml
```
``` bash
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod-3
  namespace: axess-academy
spec:
  automountServiceAccountToken: false
  containers:
  - image: nginx
    name: nginx-pod-3-container
```
``` bash 
kubectl create -f pod3.yml
```
``` bash
kubectl get pods -n axess-academy
```
``` bash
kubectl exec -it -n axess-academy nginx-pod-3 -- bash
```
``` bash
ls /run/secrets/kubernetes.io/serviceaccount/
```
