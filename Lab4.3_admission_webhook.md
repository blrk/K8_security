### Admission Controller Webhook
* An Admission Controller in Kubernetes is a component that intercepts API requests before they are persisted in etcd, allowing you to modify or validate requests dynamically.

#### Test the existing imagepull policy
* Create a pod
```bash
kubectl run before-webhook --image=nginx
```
* List the pod
```bash
kubectl  get pods
```
* Describe the pod
```bash
kubectl get pod before-webhook -o yaml | grep imagePull
```

#### Create admisison control webhook
* Create a webhook directory and navigate into that 
```bash
mkdir webhook; cd webhook
```
```bash
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -subj "/CN=admission-ca" -days 365 -out ca.crt
openssl genrsa -out server.key 2048
openssl req -new -key server.key -subj "/CN=imagepolicy-webhook.default.svc" -out server.csr
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365
```
#### Create a Kubernetes Secret for TLS Certificates
* Since Kubernetes requires TLS for admission webhooks, we will store the server.crt and server.key as a Kubernetes Secret.

```bash
kubectl create secret tls imagepolicy-webhook-secret \
  --cert=server.crt \
  --key=server.key \
  -n default
```

#### Deploy the Webhook
* Create deployment.yaml and add the following manifest. 
```bash
apiVersion: apps/v1
kind: Deployment
metadata:
  name: imagepolicy-webhook
  labels:
    app: imagepolicy-webhook
spec:
  replicas: 1
  selector:
    matchLabels:
      app: imagepolicy-webhook
  template:
    metadata:
      labels:
        app: imagepolicy-webhook
    spec:
      volumes:
      - name: tls-certs
        secret:
          secretName: imagepolicy-webhook-secret
      containers:
      - name: webhook
        image: blrk/mut_webhook_img_policy:1.0.0
        ports:
        - containerPort: 443
        volumeMounts:
        - name: tls-certs
          mountPath: "/etc/webhook/certs"
          readOnly: true
---
apiVersion: v1
kind: Service
metadata:
  name: imagepolicy-webhook
  namespace: default
spec:
  selector:
    app: imagepolicy-webhook
  ports:
  - protocol: TCP
    port: 443
    targetPort: 443
```


