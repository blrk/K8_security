### Examine Taint and Tolerations
* Note: For this experiments use the kubeadm cluster
* List the pods running 
``` bash
kubectl get pods

No resources found in default namespace.
```
* create a pod 
``` bash
kubectl run nginx-pod --image=nginx
```
* List the pod resources
``` bash
kubectl get pods
NAME        READY   STATUS    RESTARTS   AGE
nginx-pod   0/1     Pending   0          5s
```
* Note: pod state is pending here. Let us understand why this is happening 
``` bash
kubectl describe pods nginx-pod
Name:         nginx-pod
Namespace:    default
Priority:     0
Node:         <none>
Labels:       run=nginx-pod
Annotations:  <none>
Status:       Pending
IP:           
IPs:          <none>
Containers:
  nginx-pod:
    Image:        nginx
    Port:         <none>
    Host Port:    <none>
    Environment:  <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-qscjx (ro)
Conditions:
  Type           Status
  PodScheduled   False 
Volumes:
  kube-api-access-qscjx:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    ConfigMapOptional:       <nil>
    DownwardAPI:             true
QoS Class:                   BestEffort
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  84s   default-scheduler  0/1 nodes are available: 1 node(s) had untolerated taint {node-role.kubernetes.io/master: }. preemption: 0/1 nodes are available: 1 Preemption is not helpful for scheduling.
```
* By default, user can't create a pod in master node
* List the nodes
``` bash
kubectl get nodes
NAME      STATUS   ROLES           AGE   VERSION
kubeadm   Ready    control-plane   97m   v1.24.2
```
* List the taint details in the master node
``` bash
kubectl describe node kubeadm

Name:               kubeadm
Roles:              control-plane
Labels:             beta.kubernetes.io/arch=amd64
                    beta.kubernetes.io/os=linux
                    kubernetes.io/arch=amd64
                    kubernetes.io/hostname=kubeadm
                    kubernetes.io/os=linux
                    node-role.kubernetes.io/control-plane=
                    node.kubernetes.io/exclude-from-external-load-balancers=
Annotations:        flannel.alpha.coreos.com/backend-data: {"VNI":1,"VtepMAC":"8e:5b:a7:5b:d1:5b"}
                    flannel.alpha.coreos.com/backend-type: vxlan
                    flannel.alpha.coreos.com/kube-subnet-manager: true
                    flannel.alpha.coreos.com/public-ip: 192.168.122.213
                    kubeadm.alpha.kubernetes.io/cri-socket: unix:///var/run/containerd/containerd.sock
                    node.alpha.kubernetes.io/ttl: 0
                    volumes.kubernetes.io/controller-managed-attach-detach: true
CreationTimestamp:  Tue, 13 Feb 2024 02:18:21 +0000
Taints:             node-role.kubernetes.io/control-plane:NoSchedule
                    node-role.kubernetes.io/master:NoSchedule
Unschedulable:      false
Lease:
  HolderIdentity:  kubeadm
  AcquireTime:     <unset>
  RenewTime:       Tue, 13 Feb 2024 03:56:57 +0000
Conditions:
  Type                 Status  LastHeartbeatTime                 LastTransitionTime                Reason                       Message
  ----                 ------  -----------------                 ------------------                ------                       -------
  NetworkUnavailable   False   Tue, 13 Feb 2024 02:20:20 +0000   Tue, 13 Feb 2024 02:20:20 +0000   FlannelIsUp                  Flannel is running on this node
  MemoryPressure       False   Tue, 13 Feb 2024 03:52:35 +0000   Tue, 13 Feb 2024 02:18:18 +0000   KubeletHasSufficientMemory   kubelet has sufficient memory available
  DiskPressure         False   Tue, 13 Feb 2024 03:52:35 +0000   Tue, 13 Feb 2024 02:18:18 +0000   KubeletHasNoDiskPressure     kubelet has no disk pressure
  PIDPressure          False   Tue, 13 Feb 2024 03:52:35 +0000   Tue, 13 Feb 2024 02:18:18 +0000   KubeletHasSufficientPID      kubelet has sufficient PID available
  Ready                True    Tue, 13 Feb 2024 03:52:35 +0000   Tue, 13 Feb 2024 02:20:28 +0000   KubeletReady                 kubelet is posting ready status. AppArmor enabled
Addresses:
  InternalIP:  192.168.122.213
  Hostname:    kubeadm
Capacity:
  cpu:                2
  ephemeral-storage:  10218772Ki
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             4005904Ki
  pods:               110
Allocatable:
  cpu:                2
  ephemeral-storage:  9417620260
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             3903504Ki
  pods:               110
System Info:
  Machine ID:                 9c9caa291342406d8da4014b56daa069
  System UUID:                9c9caa29-1342-406d-8da4-014b56daa069
  Boot ID:                    1146bd7e-4b0f-4525-a7a1-720ac53af43e
  Kernel Version:             5.15.0-94-generic
  OS Image:                   Ubuntu 22.04.3 LTS
  Operating System:           linux
  Architecture:               amd64
  Container Runtime Version:  containerd://1.7.2
  Kubelet Version:            v1.24.2
  Kube-Proxy Version:         v1.24.2
PodCIDR:                      10.244.0.0/24
PodCIDRs:                     10.244.0.0/24
Non-terminated Pods:          (8 in total)
  Namespace                   Name                               CPU Requests  CPU Limits  Memory Requests  Memory Limits  Age
  ---------                   ----                               ------------  ----------  ---------------  -------------  ---
  kube-flannel                kube-flannel-ds-m9c9q              100m (5%)     0 (0%)      50Mi (1%)        0 (0%)         96m
  kube-system                 coredns-6d4b75cb6d-8hxjh           100m (5%)     0 (0%)      70Mi (1%)        170Mi (4%)     98m
  kube-system                 coredns-6d4b75cb6d-z6v5w           100m (5%)     0 (0%)      70Mi (1%)        170Mi (4%)     98m
  kube-system                 etcd-kubeadm                       100m (5%)     0 (0%)      100Mi (2%)       0 (0%)         98m
  kube-system                 kube-apiserver-kubeadm             250m (12%)    0 (0%)      0 (0%)           0 (0%)         98m
  kube-system                 kube-controller-manager-kubeadm    200m (10%)    0 (0%)      0 (0%)           0 (0%)         98m
  kube-system                 kube-proxy-4q77x                   0 (0%)        0 (0%)      0 (0%)           0 (0%)         98m
  kube-system                 kube-scheduler-kubeadm             100m (5%)     0 (0%)      0 (0%)           0 (0%)         98m
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource           Requests    Limits
  --------           --------    ------
  cpu                950m (47%)  0 (0%)
  memory             290Mi (7%)  340Mi (8%)
  ephemeral-storage  0 (0%)      0 (0%)
  hugepages-1Gi      0 (0%)      0 (0%)
  hugepages-2Mi      0 (0%)      0 (0%)
Events:            <none>
```
* The following is the list of tains that do not allow the master node to schedule a pod 
``` sh
Taints:             node-role.kubernetes.io/control-plane:NoSchedule
                    node-role.kubernetes.io/master:NoSchedule
```
* Remove the taint from the master node
``` bash
kubectl taint node kubeadm node-role.kubernetes.io/master-
node/kubeadm untainted
```
``` bash
kubectl taint node kubeadm node-role.kubernetes.io/control-plane-
node/kubeadm untainted
```
* Verify the the removal of taints by creating a pod
``` bash 
kubectl run demo-pod --image=nginx
```
* Cehck the status of the pods
``` bash
root@kubeadm:~# kubectl get pods
NAME         READY   STATUS    RESTARTS   AGE
nginx-pod    1/1     Running   0          38m
nginx-pod1   1/1     Running   0          37m
```

