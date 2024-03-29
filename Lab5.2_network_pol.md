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
kubectl exec -it nw-pod-1 -- ping -c 3 <pod-2 ip>
```
* Try to ping nw-pod-3 
``` bash
kubectl exec -it nw-pod-1 -- ping -c 3 <Pod-3 ip>
kubectl exec -it nw-pod-1 -- ping -c 3 sc.com

```
* Note: The default deny ploicy applied default namespace. Pinging with pod in other namesapce is working and to the internet
### Examine defult deny Egress
* Open the default.yml file in the nw-policy directory and remove its contents and add the following configuration
``` bash
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-egress
spec:
  podSelector: {}
  policyTypes:
  - Egress
```
``` bash
kubectl apply -f default.yml 
```
* List the pods
``` bash
kubectl get pods -o wide
NAME    READY   STATUS    RESTARTS       AGE   IP              NODE           NOMINATED NODE   READINESS GATES
nw-pod-1   1/1     Running   1 (114m ago)   11d   10.244.63.147   amazon-linux   <none>           <none>
nw-pod-2   1/1     Running   1 (114m ago)   11d   10.244.63.144   amazon-linux   <none>           <none>

kubectl get pods -o wide -n external
NAME    READY   STATUS    RESTARTS       AGE   IP              NODE           NOMINATED NODE   READINESS GATES
nw-pod-3   1/1     Running   1 (114m ago)   11d   10.244.63.146   amazon-linux   <none>           <none>
```
* Ping from pod-2 to internet
``` bash
kubectl exec -it nw-pod-2 -- ping -c 3 sc.com
ping: sc.com: Try again
command terminated with exit code 2
```
* Note: Because of the default Egress policy it is not working
* ping form the pod-3
``` bash
kubectl exec -it -n external nw-pod-3 -- ping -c 3 sc.com
```
* Note: Ping is working because the network policy is applied to the default namespace
### Pod Selector policy
* Open the default.yml file in the nw-policy directory and remove its contents and add the following configuration
``` bash 
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: podselector-suspicous
spec:
  podSelector:
    matchLabels:
      role: untrusted
  policyTypes:
  - Ingress
  - Egress
```
``` bash
kubectl apply -f default.yml 
```
* 
``` bash
* Add the untrusted label to the nw-pod-1
kubectl label pod nw-pod-1 role=untrusted
AME    READY   STATUS    RESTARTS       AGE   LABELS
nw-pod-1   1/1     Running   1 (128m ago)   11d   role=untrusted,run=pod-1
```
* Print the added labels
``` bash
kubectl get pods nw-pod-1 --show-labels
```
* Try to ping the pod from pod-2
``` bash
kubectl exec -it pod-2 -- ping -c 3 pod-1
ping: pod-1: Try again
command terminated with exit code 2
```
* Try to ping some webpage form pod-1
``` bash
kubectl exec -it pod-1 -- ping -c 3 sc.com
ping: sc.com: Try again
command terminated with exit code 2
```
* Remove the label and verify the connectivity
``` bash
kubectl label pod nw-pod-1 role-
```
* Note: You can notice that now the ingress and egress is unblocked
* delete the network policies
``` bash
kubectl delete netpol default-deny-egress default-deny-ingress
```
### ingress - from selector
* Create a ingress from policy. In the default.yml under nw-policy folder add the following config
``` bash
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ingress-from-ips
spec:
  podSelector:
    matchLabels:
      role: backend
  ingress:
  - from:
     - ipBlock:
        cidr: 10.244.0.0/16
        except:
        - <add your pod-2 ip here>/32 # example 10.244.63.144/32
  policyTypes:
  - Ingress
```
``` bash
kubectl apply -f default.yml
```
* Ping pod1 from pod3
``` bash
kubectl exec -it -n external nw-pod-3 -- ping -c 3 <pod-1 ip>
```
* Try to ping pod 1 from pod2
``` bash
kubectl exec -it  nw-pod-2 -- ping -c 3 <pod-1 ip>
```
* Note: the connection works here eventhough the policy is created to block it. Let us try to indentify the issue
* List the network policies
``` bash
kubectl get netpol
```
* Fetch the running congifuration of the network policy 
``` bash
kubectl get netpol -o yaml
```
``` bash
apiVersion: v1
items:
- apiVersion: networking.k8s.io/v1
  kind: NetworkPolicy
  metadata:
    annotations:
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"networking.k8s.io/v1","kind":"NetworkPolicy","metadata":{"annotations":{},"name":"ingress-from-ips","namespace":"default"},"spec":{"ingress":[{"from":[{"ipBlock":{"cidr":"10.244.0.0/16","except":["10.244.63.144/32"]}}]}],"podSelector":{"matchLabels":{"role":"backend"}},"policyTypes":["Ingress"]}}
    creationTimestamp: "2024-03-29T12:18:45Z"
    generation: 1
    name: ingress-from-ips
    namespace: default
    resourceVersion: "100800"
    uid: 0c81cf6c-0a07-41f1-9864-d83c5b35c455
  spec:
    ingress:
    - from:
      - ipBlock:
          cidr: 10.244.0.0/16
          except:
          - 10.244.63.144/32
    podSelector:
      matchLabels:
        role: backend
    policyTypes:
    - Ingress
  status: {}
kind: List
metadata:
  resourceVersion: ""
```
* Note: Observe the pod selector label it is mentioned as backend. First fetch the labels of pod1
``` bash
kubectl get pods nw-pod-1 --show-labels

AME    READY   STATUS    RESTARTS        AGE   LABELS
nw-pod-1   1/1     Running   1 (7h15m ago)   12d   run=pod-1
```
* Note: notice that the backend label is not set. Now set the label to the pod
```
kubectl label pod nw-pod-1 role=backend
```
* Now, try to ping from pod2 to pod1
``` bash
kubectl exec -it  pod-2 -- ping -c 3 10.244.63.147
PING 10.244.63.147 (10.244.63.147) 56(84) bytes of data.

--- 10.244.63.147 ping statistics ---
3 packets transmitted, 0 received, 100% packet loss, time 2030ms

command terminated with exit code 1
```
* Hope you understood how a from selector works
* Delete the network policy and label from pod1
``` bash
kubectl delete netpol ingress-from-ips
kubectl label pod nw-pod-1 role-
```

### Egress to selector
* Create a egress to selector policy 
``` bash
nano netpol.yaml
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: egress-to-ips
spec:
  podSelector:
    matchLabels:
      role: db
  egress:
  - to:
     - ipBlock:
        cidr: <add the ip of your pod 2 here>/32 # For example 10.244.63.144/32
  policyTypes:
  - Egress
```
* Add db label to pod-1
``` bash
kubectl label pod nw-pod-1 role=db
```
* Try to ping with pod-2 (it is considered as db pod)
``` bash
kubectl exec -it pod-1 -- ping -c 3 <pod-2 ip>
```
* Try try ping  to the internet and pod-3 from pod-1 the traffic flow will be denied
* Delete the network policy and label from pod1
``` bash
kubectl delete netpol egress-to-ips
kubectl label pod pod-1 role-
```

### Namespace selector
* Allow connection based on a namespace
* Create a namespace selector network policy
``` bash
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: namespace-selector
spec:
  podSelector:
    matchLabels:
      role: database
  ingress:
  - from:
     - namespaceSelector:
        matchLabels:
          role: app
       podSelector:
         matchLabels:
           role: frontend
  policyTypes:
  - Ingress
```
``` bash
kubectl apply -f default.yml
```
* Add a label to pod 1
``` bash
kubectl label pod pod-1 role=database
```
* Try to connect with pod-1 from pod-2 and pod-3
``` bash
kubectl exec -it nw-pod-2 -- ping -c 3 <pod-1 ip>
kubectl exec -n external -it nw-pod-3 -- ping -c 3 <pod-1 ip>
```
* Both the ping will not work 
* Add a label "frontend" to pod-3
``` bash
kubectl label pod pod-3 role=frontend -n external
```
* Now, try to ping pod-1 from pod-3
``` bash
kubectl exec -n external -it nw-pod-3 -- ping -c 3 <pod-1 ip>
```
* Still this will not happen because we have not added approiate label to the namespace external
* list the labels associated with the namespace external
``` bash
kubectl get namespace external --show-labels
```
* Add label app to the external namespace
``` bash
kubectl label namespace external role=app
```
* List the labels of the external namespace
``` bash
kubectl get namespace external --show-labels
```
* Try to connect to the pod-1 from pod-3
``` bash
kubectl exec -n external -it pod-3 -- ping -c 3 <pod-1 ip>

ING 10.244.63.147 (10.244.63.147) 56(84) bytes of data.
64 bytes from 10.244.63.147: icmp_seq=1 ttl=254 time=0.121 ms
64 bytes from 10.244.63.147: icmp_seq=2 ttl=254 time=0.132 ms
64 bytes from 10.244.63.147: icmp_seq=3 ttl=254 time=0.159 ms
```
* Note: It worked now beacuse correct labels are added. 
* More details refer here https://kubernetes.io/docs/concepts/services-networking/network-policies/




