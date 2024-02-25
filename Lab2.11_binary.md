  ### Verify Binaries

  https://github.com/kubernetes/kubernetes/releases

  * Download Binaries:
  ```sh
 wget https://dl.k8s.io/v1.29.2/kubernetes-server-linux-amd64.tar.gz
  ```
* if sha512sum is not here install it
```sh
  apt install hashalot
  ```
  * Verify the Message Digest
  ``` bash
sha512sum kubernetes-server-linux-amd64.tar.gz 
d5575da7f28a5284d4ffb40ca1b597213e03c381e161c1ec2bdadd7fe0532d62f41c758443ecefed70f484fb770e0bac53218f0a429587ac983469a39e56979b  kubernetes-server-linux-amd64.tar.gz

  ```