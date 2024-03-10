### Container security scanning
* Create a docker hub account using your personal email. https://hub.docker.com/signup
* Note: Create an account by entering email username and password
* After creating the account login into the docker hub account 
* Serach for an official version of nginx image
* Login into the docker hub https://labs.play-with-docker.com/
* Add a new instance and in the instance terminal run the following command to check the docker version installed
``` bash
docker --version
```
* Visit the webpage of trivy https://aquasecurity.github.io/trivy/v0.49/getting-started/installation/
* In the instance terminal, install trivy using the script 
``` bash
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin v0.49.1
```
* Scan a nginx image using trivy
``` bash
trivy image nginx:1.25.4
```
* Press Alt + Enter to maximize the screen, scroll up and down to see the vlunerabilities

### Using kube-bench to scan the k8s cluster
* Download kube-bench
* https://github.com/aquasecurity/kube-bench/?tab=readme-ov-file
``` bash
curl -L https://github.com/aquasecurity/kube-bench/releases/download/v0.7.2/kube-bench_0.7.2_linux_arm64.rpm -o kube-bench.rpm
```
``` bash
yum install kube-bench.rpm -y 
```
* Run kube bench
``` bash
kube-bench
```
* https://github.com/aquasecurity/kube-bench/blob/main/docs/running.md#running-kube-bench

### Static Analysis
* Install pip 
``` bash
yum install python3-pip -y
```
* Install checkov https://github.com/bridgecrewio/checkov
``` bash
pip3 install checkov
```
* Create a pod definition 
``` bash
vi pod-def.yaml
```
``` bash
apiVersion: v1
kind: Pod
metadata:
  name: static-analysis
spec:
  containers:
  - image: nginx
    name: sa-container
    securityContext:
      privileged: true
```
* Run checkov scan
``` bash
checkov -f pod-def.yaml 
```