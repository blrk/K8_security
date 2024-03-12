### EXplore auditing in detail
* install jq
``` bash
yum install jq -y 
```
* In Terminal 1, navigate into the follwoing directory
``` bash
cd /etc/kubernetes/
```
* Create a log directory 
``` bash
mkdir -p /var/log/k8s/audit
```
* make a copy file
``` bash
cp manifests/kube-apiserver.yaml manifests/kube-apiserver.yaml.bak
```
* Mount the directory as HostPath Volumes in kube-apiserver
* open the kube-apiserver manifest file and add the following config
``` bash
manifests/kube-apiserver.yaml
```
``` bash
- hostPath:
      path: /var/log/k8s/audit
      type: DirectoryOrCreate
  name: auditing
```
``` bash
- mountPath: /var/log/k8s/audit
  name: auditing
```
* open the kube-apiserver manifest file and add the following config
``` bash
- --audit-policy-file=/var/log/k8s/audit/audit-policy.yaml
- --audit-log-path=/var/log/k8s/audit/audit.log
```
``` bash
apiVersion: audit.k8s.io/v1
kind: Policy
omitStages:
  - "RequestReceived"

rules:

  - level: None
    resources:
    - group: ""
      resources: ["secrets"]
    namespaces: ["kube-system"]

  - level: None
    users: ["system:kube-controller-manager"]
    resources:
    - group: ""
      resources: ["secrets"]

  - level: RequestResponse
    resources:
    - group: ""
      resources: ["secrets"]
```
* View the logs
``` bash
cat /var/log/k8s/audit/audit.log | jq
```
