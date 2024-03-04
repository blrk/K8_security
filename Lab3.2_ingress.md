### Create and manage ingress controller, resource and security
#### Creating ingress controller and ingress resource
* Create a pod
``` bash
kubectl run service-backend-pod --image=nginx -l=app=nginx --port=80
```
* Create a service for the above pod
``` bash
kubectl expose pod/service-backend-pod --port=80 --target-port=80 --name=demo-service
```
``` bash
* List and describe the service
kubectl get svc
kubectl describe svc demo-service
```
* Install ingress controller
``` bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/baremetal/deploy.yaml
```
* List all the ingress resources
``` bash
kubectl get all -n ingress-nginx
```
* Create an ingress resource 
``` bash
cd config
```
``` bash
vi ingress.yaml
```
``` bash
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: demo-ingress
  annotations:
     nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: app1.scb
    http:
      paths:
      - pathType: Prefix
        path: "/"
        backend:
          service:
            name: demo-service
            port:
              number: 80
```
``` bash
kubectl apply -f ingress.yaml
```
* verify the ingress service
``` bash
kubectl get ingress
kubectl describe ingress demo-ingress
```
* List the services in ingress-nginx namespace
``` bash
kubectl get svc -n ingress-nginx
```
``` bash
ingress-nginx-controller             NodePort    10.102.200.122   <none>        80:30492/TCP,443:31108/TCP   3h36m
ingress-nginx-controller-admission   ClusterIP   10.110.118.173   <none>        443/TCP                      3h36m
```
* Try to access the service using curl
``` bash
curl http://192.168.122.87:30492
```
* Note: the page is not found since the host header is not available
* Add the host information to the host file
``` bash
vi /etc/hosts
```
``` bash
192.168.122.87	app1.scb
```
* Access the service using host name
``` bash
curl http://app1.scb:30492
```
Note: http connection to the ingress is not secure
* Try to access the service using https
``` bash
curl https://app1.scb:31108
```
``` bash
curl -kv https://app1.scb:31108
```
Note: (-k) By default, every secure connection curl makes is verified to be secure before the transfer takes place. This option makes curl skip the verification step  and proceed  without  checking.

#### Secure ingress uisng TLS
* Create Self Signed Certificate for app1.scb
``` bash
cd /root/k8_certificates/
```
``` bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ingress.key -out ingress.crt -subj "/CN=app1.scb/O=security"
```
* https://kubernetes.io/docs/concepts/services-networking/ingress/#tls
* Create a TLS secret
``` bash
kubectl create secret tls tls-cert --key ingress.key --cert ingress.crt
```
``` bash
kubectl get secret 
kubectl get secret tls-cert -o yaml
```
* Delete the existing ingress resource
``` bash
kubectl delete ingress demo-ingress
```
* Modify the ingress resource configuration file
``` bash
cd ../config/
```
``` bash
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: demo-ingress
  annotations:
     nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  tls:
  - hosts:
      - app1.scb
    secretName: tls-cert
  rules:
  - host: app1.scb
    http:
      paths:
      - pathType: Prefix
        path: "/"
        backend:
          service:
            name: demo-service
            port:
              number: 80
```
``` bash
kubectl apply -f ingress.yaml 
```
``` bash
kubectl describe ingress
```
* Make a request to the controller
``` bash
kubectl get svc -n ingress-nginx
```
``` bash
curl -kv https://app1.scb:30279
```
* Refer : https://kubernetes.github.io/ingress-nginx/deploy/
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.0/deploy/static/provider/baremetal/deploy.yaml

