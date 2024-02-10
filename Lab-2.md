## Create Self signed certificate
* Creating a private key for Certificate Authority
``` bash
  mkdir /root/k8-certificates
  cd /root/k8-certificates/
```
  
* Create key
``` bash
  openssl genrsa -out ca.key 4098
```
  
``` bash
  [root@k8security k8-certificates]# ls
  ca.key
```

* Create CSR
``` bash
  openssl req -new -key ca.key -subj "/CN=K8s-CA" -out ca.csr
```

```bash
  [root@k8security k8-certificates]# ll
  total 8
  -rw-r--r--. 1 root root 1582 Feb  9 15:44 ca.csr
  -rw-------. 1 root root 3272 Feb  9 15:40 ca.key
```
* Self-sign the CSR

``` bash
openssl x509 -req -in ca.csr -signkey ca.key -CAcreateserial  -out ca.crt -days 500

Certificate request self-signature ok
subject=CN = K8s-CA
```
### In Transit encryption etcd
* In Terminal 1: start the etcd server
``` bash
etcd
```
* In terminal 2: Fetch the tcp dump from port 2379
``` bash
etcdctl put axess "k8-lab"
etcdctl get axess
```
### Securing communication to etcd server
* Install net-tools and tcp dump
``` bash
yum install net-tools tcpdump -y
```
* In Terminal 1: start the etcd server
``` bash
etcd
```
* Check the etcd  server is listing on port 2379
``` bash
[root@k8security ~]# netstat -ntlp
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      731/sshd: /usr/sbin 
tcp        0      0 127.0.0.1:2380          0.0.0.0:*               LISTEN      1570/etcd           
tcp        0      0 127.0.0.1:2379          0.0.0.0:*               LISTEN      1570/etcd           
tcp6       0      0 :::22                   :::*                    LISTEN      731/sshd: /usr/sbin
```
* In terminal 2: Run the tcp dump command
``` bash
tcpdump -i lo -X  port 2379
```
* I Terminal 3: run the following commands
``` bash
etcdctl put axess "k8-lab"
etcdctl get axess
```
* Move to the terminal 2 and press ctrl + c and verify the tcp dump by scrolling up; you will be able to see the "k8-lab"
``` bash
17:32:38.615227 IP localhost.etcd-client > localhost.33446: Flags [P.], seq 61:184, ack 195, win 512, options [nop,nop,TS val 3582313186 ecr 3582313186], length 123
	0x0000:  4500 00af 2bf3 4000 4006 1054 7f00 0001  E...+.@.@..T....
	0x0010:  7f00 0001 094b 82a6 597f faa6 f8cd c577  .....K..Y......w
	0x0020:  8018 0200 fea3 0000 0101 080a d585 c2e2  ................
	0x0030:  d585 c2e2 0000 0e01 0400 0000 0188 5f8b  .............._.
	0x0040:  1d75 d062 0d26 3d4c 4d65 6400 003a 0000  .u.b.&=LMed..:..
	0x0050:  0000 0001 0000 0000 350a 1a08 b298 eaf1  ........5.......
	0x0060:  9483 86fc cd01 10cd d291 8bd2 b881 cf8e  ................
	0x0070:  0118 0620 0512 150a 0561 7865 7373 1003  .........axess..
	0x0080:  1806 2004 2a06 6b38 2d6c 6162 2001 0000  ....*.k8-lab....
	0x0090:  1801 0500 0000 0140 889a cac8 b212 34da  .......@......4.
	0x00a0:  8f01 3040 899a cac8 b525 4207 317f 00    ..0@.....%B.1..
17:32:38.617612 IP localhost.33446 > localhost.etcd-client: Flags [F.], seq 195, ack 184, win 512, options [nop,nop,TS val 3582313189 ecr 3582313186], length 0
	0x0000:  4500 0034 3e33 4000 4006 fe8e 7f00 0001  E..4>3@.@.......
	0x0010:  7f00 0001 82a6 094b f8cd c577 597f fb21  .......K...wY..!
	0x0020:  8011 0200 fe28 0000 0101 080a d585 c2e5  .....(..........
	0x0030:  d585 c2e2                                ....
```
  


  

