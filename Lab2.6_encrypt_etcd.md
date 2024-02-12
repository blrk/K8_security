### Implement encryption to the data at rest in etcd
* Create a secret named mydb1 
``` bash
kubectl create secret generic mydb1 -n default --from-literal=user=mydb1password --server=https://127.0.0.1:6443 --client-certificate /root/k8-certificates/rk.crt --certificate-authority /root/k8-certificates/ca.crt --client-key /root/k8-certificates/rk.key
```
* Retrive the secret
``` bash
kubectl get secret --server=https://127.0.0.1:6443 --client-certificate /root/k8-certificates/rk.crt --certificate-authority /root/k8-certificates/ca.crt --client-key /root/k8-certificates/rk.key
```
* Extract the Secret in ETCD which is stored as Plain-Text
``` bash
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 --insecure-skip-tls-verify  --insecure-transport=false --cert /root/k8-certificates/apiserver.crt --key /root/k8-certificates/apiserver.key get /registry/secrets/default/mydb1 | hexdump -C
```
* you can notice the secret from the hexdump 
``` bash
00000000  2f 72 65 67 69 73 74 72  79 2f 73 65 63 72 65 74  |/registry/secret|
00000010  73 2f 64 65 66 61 75 6c  74 2f 6d 79 64 62 31 0a  |s/default/mydb1.|
00000020  6b 38 73 00 0a 0c 0a 02  76 31 12 06 53 65 63 72  |k8s.....v1..Secr|
00000030  65 74 12 de 01 0a ae 01  0a 05 6d 79 64 62 31 12  |et........mydb1.|
00000040  00 1a 07 64 65 66 61 75  6c 74 22 00 2a 24 36 62  |...default".*$6b|
00000050  64 63 61 30 39 65 2d 31  66 30 66 2d 34 61 66 63  |dca09e-1f0f-4afc|
00000060  2d 39 64 66 31 2d 62 31  31 39 31 32 33 36 61 61  |-9df1-b1191236aa|
00000070  63 65 32 00 38 00 42 08  08 e1 84 a7 ae 06 10 00  |ce2.8.B.........|
00000080  7a 00 8a 01 61 0a 0e 6b  75 62 65 63 74 6c 2d 63  |z...a..kubectl-c|
00000090  72 65 61 74 65 12 06 55  70 64 61 74 65 1a 02 76  |reate..Update..v|
000000a0  31 22 08 08 e1 84 a7 ae  06 10 00 32 08 46 69 65  |1".........2.Fie|
000000b0  6c 64 73 56 31 3a 2d 0a  2b 7b 22 66 3a 64 61 74  |ldsV1:-.+{"f:dat|
000000c0  61 22 3a 7b 22 2e 22 3a  7b 7d 2c 22 66 3a 75 73  |a":{".":{},"f:us|
000000d0  65 72 22 3a 7b 7d 7d 2c  22 66 3a 74 79 70 65 22  |er":{}},"f:type"|
000000e0  3a 7b 7d 7d 42 00 12 23  0a 04 75 73 65 72 12 1b  |:{}}B..#..user..|
000000f0  73 65 63 72 65 74 70 61  73 73 77 6f 72 64 6d 79  |myb1password    |
00000100  64 62 31 70 61 73 73 77  6f 72 64 1a 06 4f 70 61  |..Opaque.."..   |
00000110  71 75 65 1a 00 22 00 0a                           |                |
```
* Search the secret stored in disk
``` bash
root@k8-security:~/k8-certificates# cd /var/lib/etcd 
root@k8-security:/var/lib/etcd# grep -R "mydb1" .
grep: ./member/snap/db: binary file matches
grep: ./member/wal/0000000000000000-0000000000000000.wal: binary file matches
```
#### How to secure the secret stored in etcd 
* Create a directory to hold the configuration and navigate into that 
``` bash
mkdir /var/lib/kubernetes
cd /var/lib/kubernetes
```
* Generate an encryption key
``` bash
ENCRYPTION_KEY=$(head -c 32 /dev/urandom | base64)
echo $ENCRYPTION_KEY
```
* Create an encryption config
``` bash
cat > encryption-at-rest.yaml <<EOF
kind: EncryptionConfig
apiVersion: v1
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: ${ENCRYPTION_KEY}
      - identity: {}
EOF
```
* Edit the kube apiserver and service file and add the following configuration at the end of service
``` bash
vi /etc/systemd/system/kube-apiserver.service
```
``` bash
--encryption-provider-config=/var/lib/kubernetes/encryption-at-rest.yaml
```
* Restart the kube api server
``` bash
systemctl daemon-reload
systemctl restart kube-apiserver
systemctl status kube-apiserver
```
* Create a new secret 
``` bash
kubectl create secret generic mydb2 -n default --from-literal=user=mydb2password --server=https://127.0.0.1:6443 --client-certificate /root/k8-certificates/rk.crt --certificate-authority /root/k8-certificates/ca.crt --client-key /root/k8-certificates/rk.key
```
* Retrive the secret
``` bash
kubectl get secret --server=https://127.0.0.1:6443 --client-certificate /root/k8-certificates/rk.crt --certificate-authority /root/k8-certificates/ca.crt --client-key /root/k8-certificates/rk.key
```
* Try to fetch the password from the hexdump
``` bash
cd /root/certificates
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 --insecure-skip-tls-verify  --insecure-transport=false --cert /root/k8-certificates/apiserver.crt --key /root/k8-certificates/apiserver.key get /registry/secrets/default/mydb2 | hexdump -C
```
* Note that we can't find the password from the hexdump
``` bash
00000000  2f 72 65 67 69 73 74 72  79 2f 73 65 63 72 65 74  |/registry/secret|
00000010  73 2f 64 65 66 61 75 6c  74 2f 6d 79 64 62 32 0a  |s/default/mydb2.|
00000020  6b 38 73 3a 65 6e 63 3a  61 65 73 63 62 63 3a 76  |k8s:enc:aescbc:v|
00000030  31 3a 6b 65 79 31 3a 32  29 fd 3d fb 44 35 d9 6e  |1:key1:2).=.D5.n|
00000040  e7 fc 98 ba 44 8c 43 94  9d 0a c9 64 54 8b 1d eb  |....D.C....dT...|
00000050  8f c7 45 a3 ff 31 8d ef  58 6b e5 36 f2 4b e2 a6  |..E..1..Xk.6.K..|
00000060  e2 ea 10 66 2e 86 22 76  49 62 fc 22 93 e4 93 f6  |...f.."vIb."....|
00000070  56 97 73 83 1c aa 20 de  72 8c ee ed 04 13 4d df  |V.s... .r.....M.|
00000080  0c 90 f3 52 2c 5d 0f 36  5c 01 37 cf 02 07 40 06  |...R,].6\.7...@.|
00000090  fd 1d 17 f8 6e fa 46 ed  cf ec 9e 3d 9c 9d 34 b2  |....n.F....=..4.|
000000a0  16 fa 6b 61 65 16 ba e7  3c 42 35 df 4c 72 b0 e4  |..kae...<B5.Lr..|
000000b0  63 92 47 cf 7d 78 d3 3e  a5 91 7c c0 43 d0 61 47  |c.G.}x.>..|.C.aG|
000000c0  7d d9 5a ae ce b5 a0 57  5c 5b 81 28 0a 20 46 48  |}.Z....W\[.(. FH|
000000d0  0a 4c af 5f 52 33 60 5f  ae 72 55 3c 07 a9 b9 76  |.L._R3`_.rU<...v|
000000e0  4b 15 6c 4d 16 67 59 99  b7 3a a3 d5 5a ce 31 34  |K.lM.gY..:..Z.14|
000000f0  6f e7 b3 41 b4 ac 58 fb  5d 00 56 dd d0 83 b0 22  |o..A..X.].V...."|
00000100  30 cc bb 8c 50 fe 69 9d  23 80 18 bb f9 02 0f 96  |0...P.i.#.......|
00000110  55 93 f1 dd b9 4c a8 e0  cc 17 61 81 3e 9e 2f ff  |U....L....a.>./.|
00000120  a5 c6 ab 67 38 a9 34 4a  b3 fa 8d aa 16 ef 96 c4  |...g8.4J........|
00000130  8c 20 95 bd bb 5c 6b 0a                           |. ...\k.|
00000138
```
* Search the secret stored in disk 
``` bash
grep -R "mydb2" .
```
