### Implementing Auditing 
* Create the looging config in the certificate directory and add the following configuration
``` bash
vi /root/k8-certificates/logging.yaml
```
``` bash
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: Metadata
```
* Edit the kube apiserver service file add the following line
``` bash
vi /etc/systemd/system/kube-apiserver.service
```
``` bash
--audit-policy-file=/root/k8-certificates/logging.yaml --audit-log-path=/var/log/api-audit.log --audit-log-maxage=30  --audit-log-maxbackup=10  --audit-log-maxsize=100 
```
* Restart the kube apiserver
``` bash
systemctl daemon-reload
systemctl restart kube-apiserver
systemctl status kube-apiserver
```
* Run a query as "rk" user
``` bash
kubectl get secret --server=https://127.0.0.1:6443 --client-certificate /root/k8-certificates/rk.crt --certificate-authority /root/k8-certificates/ca.crt --client-key /root/k8-certificates/rk.key
```
* Verify the logs for the secret access by the user rk
``` bash
grep -i ':"rk' /var/log/api-audit.log
```
* Copy the log data and paste in this following link to read it better. <a href="https://jsonformatter.curiousconcept.com/">https://jsonformatter.curiousconcept.com/</a>
