### Understanding Imagepull policy
#### Pre-requsite 
* Install docker
``` bash
apt install apt-transport-https ca-certificates curl software-properties-common -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update -y
apt-cache policy docker-ce
apt install docker-ce -y
systemctl status docker
usermod -aG docker ${USER}
```
``` bash
sudo yum update -y
sudo amazon-linux-extras install docker
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user
```
#### Pre-Requiste create container image using docker build 
* Create a directory microservice and naviage into that
``` bash
mkdir microservice; cd microservice
```
* Create a Dockerfile
``` bash
vi Dockerfile
```
* Add the following config
``` bash
FROM ubuntu:22:04
CMD ["sleep","3600"]
```
* Run the following command to create an image
``` bash
docker build -t myapp:1.0 .
```
* List the images
``` bash
docker images
REPOSITORY   TAG       IMAGE ID       CREATED       SIZE
myapp        1.0       f5a447cb3f8a   10 days ago   77.9MB
```
* Verify the default image pull policy
``` bash
kubectl run myapp1 --image=blrk/nodeapp:1.0
```
``` bash
kubectl logs myapp1
```
``` bash
ctr -n k8s.io containers list | grep nodeapp
```
* Delete the pod and image
``` bash
kubectl delete pod myapp1
```
* delete the image
``` bash
ctr -n k8s.io i rm docker.io/blrk/nodeapp:1.0
```
* Create a pod with imagePullPolicy: IfNotPresent
``` bash
vi myapp1.yml
```
``` bash
apiVersion: v1
kind: Pod
metadata:
  labels:
    run: node-app
  name: myapp1
spec:
  containers:
  - image: blrk/nodeapp:1.0
    name: myapp-container
    imagePullPolicy: IfNotPresent
```
``` bash
kubectl apply -f myapp1.yml 
```
``` bash
kubectl logs myapp1
kubectl describe pod myapp1
```
#### Configure Admission controller for image policy 
* Make a copy of the kube-api server yaml file
``` bash
cp /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/manifests/kube-apiserver.yaml.bak
```
* Open the admission contoller yaml file and search for --enable-admission-plugins
``` bash
vi /etc/kubernetes/manifests/kube-apiserver.yaml 
```
* Add imagePullPolicy as 
``` bash
AlwaysPullImages
```
* After adding it should look like this
``` bash
--enable-admission-plugins=NodeRestriction,AlwaysPullImages
```
* Delete the existing pods
``` bash
kubectl delete pods --all
```
* Create a pod defnition
``` bash
vi myapp2.yml
```
``` bash
apiVersion: v1
kind: Pod
metadata:
  labels:
    run: myapp2
  name: myapp2
spec:
  containers:
  - image: myapp:1.0
    name: myapp2-container
    imagePullPolicy: Always
```
``` bash
 kubectl apply -f myapp2.yml 
```
``` bash
kubectl describe pod myapp2
```
``` bash
kubectl get pod myapp2 -o yaml
```




