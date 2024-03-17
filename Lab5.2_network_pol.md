### Implementing network polices
* Verify the Verify Calico installation in your cluster
``` bash
kubectl get pods -n calico-system
* You should see a result similar to the below
```
``` bash
NAME                                       READY   STATUS    RESTARTS   AGE
calico-kube-controllers-76fdffb7c5-2456v   1/1     Running   0          118m
calico-node-kjmz5                          1/1     Running   0          118m
calico-typha-868d94c88b-vs9f8              1/1     Running   0          118m
csi-node-driver-4fw88                      2/2     Running   0          118m
```
* More on Network policies: https://kubernetes.io/docs/concepts/services-networking/network-policies/
* Create two pods in the default namespace
``` bash
kubectl run nw-pod1 --image=praqma/network-multitool
kubectl run nw-pod2 --image=praqma/network-multitool
```
* Create a namespace external
``` bash
kubectl create namespace external
```
* Create a pod in the external namespace
``` bash
kubectl run nw-pod3 --image=praqma/network-multitool -n external
```
* Find the IP address of the pods
``` bash
kubectl get pods -o wide
```
``` bash
NAME    READY   STATUS    RESTARTS   AGE    IP              NODE           NOMINATED NODE   READINESS GATES
nw-pod-1   1/1     Running   0          117m   10.244.63.136   amazon-linux   <none>           <none>
nw-pod-2   1/1     Running   0          117m   10.244.63.137   amazon-linux   <none>           <none>
```
``` bash
kubectl get pods -o wide -n external
```
``` bash
NAME    READY   STATUS    RESTARTS   AGE    IP              NODE           NOMINATED NODE   READINESS GATES
nw-pod-3   1/1     Running   0          117m   10.244.63.138   amazon-linux   <none>           <none>
```
* List the network policies in the default namespace. No policy will be available
``` bash
kubectl get netpol
```
* Test the connectivity form nw-pod1 to nw-pod2, nw-pod3 and internet
``` bash
kubectl exec -it nw-pod1 -- ping -c 3 <nw-pod2 IP> 
kubectl exec -it nw-pod1 -- ping -c 3 <nw-pod3 IP> 
kubectl exec -it nw-pod1 -- ping -c 3 sc.com
```
#### Examine Default deny ingress 
* You can create a "default" ingress isolation policy for a namespace by creating a NetworkPolicy that selects all pods but does not allow any ingress traffic to those pods.
* create a nw-policy directory and navigate into that 
``` bash
mkdir /root/nw-policy; cd /root/nw-policy
```
* create a file vi default.yml
``` bash
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
spec:
  podSelector: {}
  policyTypes:
  - Ingress
```
``` bash
kubectl apply -f default.yml 
```
* List the network policy 
``` bash
kubectl get netpol
```
``` bash
NAME                   POD-SELECTOR   AGE
default-deny-ingress   <none>         114s
```
* Ping the nw-pod-2
``` bash
kubectl exec -it nw-pod-1 -- ping -c 3 10.244.63.137
```
* Try to ping nw-pod-3 
``` bash
kubectl exec -it nw-pod-1 -- ping -c 3 10.244.63.138
kubectl exec -it nw-pod-1 -- ping -c 3 sc.com

```
* Note: The default deny ploicy applied default namespace. Pinging with pod in other namesapce is working and to the internet
