### Running API server in secure mode
* Navigate to the certificate folder 
``` bash
cd /root/k8-certificates/
```
* Generate client (etcd) certificate for api server 
``` bash
[root@k8security k8-certificates]# openssl genrsa -out apiserver.key 4098
[root@k8security k8-certificates]# openssl req -new -key apiserver.key -subj "/CN=kube-apiserver" -out apiserver.csr
[root@k8security k8-certificates]# openssl x509 -req -in apiserver.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out apiserver.crt -extensions v3_req  -days 500 
```
* Create Service Account Certificates
``` bash
[root@k8security k8-certificates]# openssl genrsa -out service-account.key 4098
[root@k8security k8-certificates]# openssl req -new -key service-account.key -subj "/CN=service-accounts" -out service-account.csr
[root@k8security k8-certificates]# openssl x509 -req -in service-account.csr -CA ca.crt -CAkey ca.key -CAcreateserial  -out service-account.crt -days 500
```
* Find the ip address of your host (eth0)
``` bash
root@k8-security:/home/blrk# ip a s
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
2: enp1s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 52:54:00:d9:d8:f6 brd ff:ff:ff:ff:ff:ff
    inet 192.168.122.108/24 metric 100 brd 192.168.122.255 scope global dynamic enp1s0
       valid_lft 2768sec preferred_lft 2768sec
    inet6 fe80::5054:ff:fed9:d8f6/64 scope link 
       valid_lft forever preferred_lft forever

```
* Start API server with certificates
* Note: chnage the --advertise-address
``` bash
kube-apiserver --advertise-address=192.168.122.108 --etcd-cafile=/root/k8-certificates/ca.crt --etcd-certfile=/root/k8-certificates/apiserver.crt --etcd-keyfile=/root/k8-certificates/apiserver.key --service-cluster-ip-range 10.0.0.0/24 --service-account-issuer=https://127.0.0.1:6443 --service-account-key-file=/root/k8-certificates/service-account.crt --service-account-signing-key-file=/root/k8-certificates/service-account.key --etcd-servers=https://127.0.0.1:2379
```
* Verify that API service is running using netstat command 
``` bash
root@k8-security:/home/blrk# netstat -ntlp
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      1368/sshd: /usr/sbi 
tcp        0      0 127.0.0.1:2380          0.0.0.0:*               LISTEN      1984/etcd           
tcp        0      0 127.0.0.1:2379          0.0.0.0:*               LISTEN      1984/etcd           
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN      624/systemd-resolve 
tcp6       0      0 :::6443                 :::*                    LISTEN      2032/kube-apiserver 
tcp6       0      0 :::22                   :::*                    LISTEN      1368/sshd: /usr/sbi 
```

``` bash
root@k8-security:/home/blrk# curl -k https://localhost:6443
{
  "kind": "Status",
  "apiVersion": "v1",
  "metadata": {},
  "status": "Failure",
  "message": "Unauthorized",
  "reason": "Unauthorized",
  "code": 401
}
```
### Configure systemd to run API server
* Note change the -advertise-address
``` bash
cat <<EOF | sudo tee /etc/systemd/system/kube-apiserver.service
[Unit]
Description=Kubernetes API Server
Documentation=https://github.com/kubernetes/kubernetes

[Service]
ExecStart=/usr/local/bin/kube-apiserver \
--advertise-address=192.168.122.108 \
--etcd-cafile=/root/k8-certificates/ca.crt \
--etcd-certfile=/root/k8-certificates/apiserver.crt \
--etcd-keyfile=/root/k8-certificates/apiserver.key \
--etcd-servers=https://127.0.0.1:2379 \
--service-account-key-file=/root/k8-certificates/service-account.crt \
--service-cluster-ip-range=10.0.0.0/24 \
--service-account-signing-key-file=/root/k8-certificates/service-account.key \
--service-account-issuer=https://127.0.0.1:6443 

[Install]
WantedBy=multi-user.target
EOF
```
### Enable in-transit encryption for API-server 
* Verify client certificate details
``` bash
openssl s_client -showcerts -connect localhost:6443 2>/dev/null | openssl x509 -inform pem -noout -text
```
* Navigate to the certificates directory 
``` bash
cd /root/k8-certificates/
```
* Create config file for certificate creation
``` bash
cat <<EOF | sudo tee api.conf
[req]
req_extensions = v3_req
distinguished_name = req_distinguished_name
[req_distinguished_name]
[ v3_req ]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names
[alt_names]
DNS.1 = kubernetes
DNS.2 = kubernetes.default
DNS.3 = kubernetes.default.svc
DNS.4 = kubernetes.default.svc.cluster.local
IP.1 = 127.0.0.1
IP.2 = 192.168.122.108
IP.3 = 10.0.0.1
EOF
```
* Create Certificates for API Server
``` bash
root@k8-security:~/k8-certificates# openssl genrsa -out kube-api.key 4098
root@k8-security:~/k8-certificates# openssl req -new -key kube-api.key -subj "/CN=kube-apiserver" -out kube-api.csr -config api.conf
root@k8-security:~/k8-certificates# openssl x509 -req -in kube-api.csr -CA ca.crt -CAkey ca.key -CAcreateserial  -out kube-api.crt -extensions v3_req -extfile api.conf -days 500
```
* Add the following glages in the kube-apiserver service fikle and restart the service
``` bash
vi /etc/systemd/system/kube-apiserver.service
```
``` bash
--tls-cert-file=/root/k8-certificates/kube-api.crt 
--tls-private-key-file=/root/k8-certificates/kube-api.key 
```
* Restart the kube-apiserver 
``` bash
systemctl daemon-reload
systemctl restart kube-apiserver
systemctl status kube-apiserver
```
* Verify the Certificate details
``` bash
openssl s_client -showcerts -connect localhost:6443 2>/dev/null | openssl x509 -inform pem -noout -text
```
``` bash
curl -k https://localhost:6443
```
