### Implement kubelet security
* List the services and their port numbers
``` bash
netstat -ntlp
```
* Make a request to kubelt API  using curl
``` bash
curl -k -X GET https://localhost:10250/pods
```
* Check the status of the kubelet service
``` bash
systemctl status kubelet
```
* navigate to the location of kubelet config files
``` bash
cd /var/lib/kubelet/
```
* Make a backup of config.yaml
``` bash
cp config.yaml config.yaml.bak
```
* Make the following chnages to the config.yml to make a insecure connection
* Set anonymous authentication to true
``` bash
authentication:
  anonymous:
    enabled: true
```
* Change the Authorization Mode to AlwaysAllow
``` bash
authorization:
  mode: AlwaysAllow
```
* Restart the service
``` bash
systemctl restart kubelet
systemctl status kubelet
```
* Install kubeletctl from this link https://github.com/cyberark/kubeletctl
``` bash
curl -LO https://github.com/cyberark/kubeletctl/releases/download/v1.6/kubeletctl_linux_amd64 && chmod a+x ./kubeletctl_linux_amd64 && mv ./kubeletctl_linux_amd64 /usr/local/bin/kubeletctl
```
* list the pods using kubeletctl
``` bash
kubeletctl pods -i
```
``` bash
kubeletctl run "whoami" --all-pods -i
```
* Verify the certificate of the kubelet for node authorizer group
``` bash
openssl x509 -in  /var/lib/kubelet/pki/kubelet-client-current.pem -text -noout
```
