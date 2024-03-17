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
pod-1   1/1     Running   0          117m   10.244.63.136   amazon-linux   <none>           <none>
pod-2   1/1     Running   0          117m   10.244.63.137   amazon-linux   <none>           <none>
```
``` bash
kubectl get pods -o wide -n external
```
``` bash
NAME    READY   STATUS    RESTARTS   AGE    IP              NODE           NOMINATED NODE   READINESS GATES
pod-3   1/1     Running   0          117m   10.244.63.138   amazon-linux   <none>           <none>
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

