### Monitoring and Logging
### install Faclo and check the basic rules
* Falco Doc: https://falco.org/docs/install-operate/installation/
* Add the falcosecurity GPG key
``` bash
rpm --import https://falco.org/repo/falcosecurity-packages.asc
```
* Configure the yum repository
``` bash
curl -s -o /etc/yum.repos.d/falcosecurity.repo https://falco.org/repo/falcosecurity-rpm.repo
```
* Update the package list
``` bash
yum update -y
```
* Install some required dependencies that are needed to build the kernel module and the eBPF probe
``` bash
yum install -y dkms make && yum install -y kernel-devel-$(uname -r) && yum install -y clang llvm  && yum install -y dialog
```
* Install the Falco package
``` bash
yum install -y falco
```
* In Terminal 1: Start faclo choose eBPF mode
``` bash
falco
```
* In terminal 2: run the following commands
``` bash
kubectl run demo-falco --image=nginx
kubectl exec -it demo-falco -- bash
cat /etc/passwd
```
* Verify the Terminal 1 you can notice an alert
``` bash
20:18:38.806338761: Notice A shell was spawned in a container with an attached terminal (evt_type=execve user=root user_uid=0 user_loginuid=-1 process=bash proc_exepath=/usr/bin/bash parent=containerd-shim command=bash terminal=34816 exe_flags=EXE_WRITABLE container_id=8663dc264469 container_name=nginx)
```
* Open the falco config and search "container"
``` bash
vi /etc/falco/falco_rules.yaml
```
* Note: you can understand how falco rules are written
### Writing custom falco rules
* More about falco rules https://github.com/falcosecurity-retire/profiles/blob/master/rules/rules-nginx.yaml
* Observe the syntax of Falco rules
* Supported Fields for Conditions and Outputs: https://falco.org/docs/reference/rules/supported-fields/
* Write rule for detecting cat usage in a container
``` bash
vi /etc/falco/falco_rules.local.yaml 
```
``` bash
- rule: The "cat" command is ran in a container
  desc: An event will trigger every time you run cat in a container
  condition: evt.type = execve and container.id != host and proc.name = cat
  output: "cat was run inside a container"
  priority: INFO
```
``` bash
kubectl exec -it demo-falco -- bash
cat /etc/passwd
```
* Modify the rule output using field class element
``` bash
output: "cat was run inside a container (user=%user.name container=%container.name image=%container.image proc=%proc.cmdline)"
```
``` bash
kubectl exec -it demo-falco -- bash
cat /etc/passwd
```
* Modify the rule using macros and list
``` bash
- macro: custom_macro
  condition: evt.type = execve and container.id != host

- list: blacklist_binaries
  items: [cat, grep,date]

- rule: The program "cat" is run in a container
  desc: An event will trigger every time you run cat in a container
  condition: custom_macro and proc.name in (blacklist_binaries)
  output: "cat was run inside a container (user=%user.name container=%container.name image=%container.image proc=%proc.cmdline)"
  priority: INFO
```
``` bash
kubectl exec -it demo-falco -- bash
cat /etc/passwd
grep /etc/shadow root
```

