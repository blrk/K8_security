### Understanding the system hardening
#### Learn apparmor
* Check the status of apparmor
``` bash
systemctl status apparmor
```
* Print the currently loaded app armor policy 
``` bash
aa-status
```
* Create a directory and navigate into that
``` bash
mkdir /root/learn-apparmor; cd root/learn-apparmor
```
* Create a script file and add the following script 
``` bash
vi script1.sh
```
``` bash
#!/bin/bash
touch /tmp/file.txt
echo "New File created"

rm -f /tmp/file.txt
echo "New file removed"
```
* Set an execution bit
``` bash
chmod +x script1.sh
```
* install apparmor utility 
``` bash
apt install apparmor-utils -y
```
* Generate apparmor profile for the script file
``` bash
aa-genprof ./scrript1.sh
```
* In Terminal -2 execute the script 
``` bash
./script1.sh
```
* Move to the first tab and press s to scan 
``` bash
Profile:  /root/learn-apparmor/script1.sh
Execute:  /usr/bin/touch
Severity: 3

(I)nherit / (C)hild / (N)amed / (X) ix On / (D)eny / Abo(r)t / (F)inish
```
* Press I to inherit
* Press A to allow
* Press S to save
* Press F for finish
* Run the foillowing command to print the apparmor profile. Notice that your script file is loaded 
``` bash
aa-status
```
* list the files in apparmor.d directory 
``` bash
ls /etc/apparmor.d/
abi           force-complain  nvidia_modprobe                 tunables         usr.lib.snapd.snap-confine.real
abstractions  local           root.learn-apparmor.script1.sh  usr.bin.man      usr.sbin.rsyslogd
disable       lsb_release     sbin.dhclient                   usr.bin.tcpdump
```
* print the contents of the root.learn-apparmor.script1.sh 
``` bash
cat root.learn-apparmor.script1.sh 
at /etc/apparmor.d/root.learn-apparmor.script1.sh 
# Last Modified: Sat Mar  9 13:36:46 2024
abi <abi/3.0>,

include <tunables/global>

/root/learn-apparmor/script1.sh {
  include <abstractions/base>
  include <abstractions/bash>
  include <abstractions/consoles>
  include <abstractions/user-tmp>

  /root/learn-apparmor/script1.sh r,
  /usr/bin/bash ix,
  /usr/bin/rm mrix,
  /usr/bin/touch mrix,
  owner /etc/ld.so.cache r,

}
```
* In Terminal -2 execute the script 
``` bash
./script1.sh
```
* Edit the script and add the following line
``` bash
cat /etc/password
```
* Execute the script 
``` bash
./script1.sh 
New File created
New file removed
./script1.sh: line 8: /usr/bin/cat: Permission denied
```
* stop the apparmor service
``` bash
systemctl stop apparmor.service 
```
* Execute the script once again
``` bash
./script1.sh 
New File created
New file removed
./script1.sh: line 8: /usr/bin/cat: Permission denied
```
* Disable the apparmor profile
``` bash
ln -s /etc/apparmor.d/root.learn-apparmor.script1.sh /etc/apparmor.d/disable
apparmor_parser -R /etc/apparmor.d/root.learn-apparmor.script1.sh 
```
* Note: Enforce mode - enforce the policy and complain mode - only logs

#### Integerate apparmor with K8s
* Create a deny write apparmor profile
``` bash
apparmor_parser -q <<EOF
#include <tunables/global>

profile k8s-apparmor-deny-write-profile flags=(attach_disconnected) {
  #include <abstractions/base>

  file,

  # Deny all file writes.
  deny /** w,
}
EOF
```
* Verify the status of the profile
``` bash
aa-status
```
* Create a apparmor YAML profile for container
``` bash
vi demopod-apparmor.yml
```
``` bash
apiVersion: v1
kind: Pod
metadata:
  name: demopod-apparmor
  annotations:
    container.apparmor.security.beta.kubernetes.io/apparmor-container: localhost/k8s-apparmor-deny-write-profile
spec:
  containers:
  - name: apparmor-container
    image: busybox
    command: [ "sh", "-c", "echo 'Hello AppArmor!' && sleep 1h" ]
```
``` bash
kubectl apply -f demopod-apparmor.yml
```
* Verify the write access by connecting to the container 
``` bash
kubectl exec -it demopod-apparmor -- sh
/ # echo "hello" > file1.txt
sh: can't create file1.txt: Permission denied
```
* Exit the container
``` bash
exit
```
#### Seccomp profiles
``` bash
cat <<EOF | tee /var/lib/kubelet/seccomp/profiles/ping-seccomp.json
{
  "defaultAction": "SCMP_ACT_ALLOW",
  "architectures": [
    "SCMP_ARCH_X86_64",
    "SCMP_ARCH_X86",
    "SCMP_ARCH_X32"
  ],
  "syscalls": [
    {
      "name": "socket",
      "action": "SCMP_ACT_ERRNO",
      "args": [
        {
          "index": 0,
          "value": 2,
          "op": "SCMP_CMP_EQ"
        },
        {
          "index": 1,
          "value": 1,
          "op": "SCMP_CMP_EQ"
        },
        {
          "index": 2,
          "value": 0,
          "op": "SCMP_CMP_EQ"
        }
      ]
    }
  ]
}
EOF
```
``` bash
apiVersion: v1
kind: Pod
metadata:
  name: ping-blocked-pod
spec:
  containers:
  - name: ping-blocked-container
    image: praqma/network-multitool
    securityContext:
      seccompProfile:
        type: "Local"
        localhostProfile: "ping-seccomp.json"
```
``` bash
apiVersion: v1
kind: Pod
metadata:
  name: ping-blocked-pod
  labels:
    app: ping-blocked-pod
spec:
  securityContext:
    seccompProfile:
      type: Localhost
      localhostProfile: profiles/ping-seccomp.json
  containers:
  - name: ping-blocked-container
    image: praqma/network-multitool    
    securityContext:
      allowPrivilegeEscalation: false
```
``` bash
apiVersion: v1
kind: Pod
metadata:
  name: ping-blocked-pod
  labels:
    app: ping-blocked-pod
spec:
  securityContext:
    seccompProfile:
      type: Localhost
      localhostProfile: profiles/pblock.json
  containers:
  - name: ping-blocked-container
    image: hashicorp/http-echo:1.0
    args:
    - "-text=just made some syscalls!"
    securityContext:
      allowPrivilegeEscalation: false
```
====
new test

``` bash
{
  "defaultAction": "SCMP_ACT_ALLOW",
  "architectures": [
    "SCMP_ARCH_X86_64",
    "SCMP_ARCH_X86",
    "SCMP_ARCH_X32"
  ],
  "syscalls": [
    {
      "name": "NET_RAW",
      "action": "SCMP_ACT_ERRNO"
    }
  ]
}

```
