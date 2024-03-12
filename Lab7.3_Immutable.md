``` bash
vi immutable.yaml
```
``` bash
apiVersion: v1
kind: Pod
metadata:
  name: immutable-pod
spec:
  containers:
  - name: ubuntu
    image: ubuntu
    command: ["sleep","3600"]
    securityContext:
      readOnlyRootFilesystem: true
```
``` bash
kubectl exec -it immutable-pod -- bash
touch file.txt
```