# mrack

![pypi_badge](https://img.shields.io/pypi/v/mrack?label=PyPI&logo=pypi) ![readthedocs_badge](https://img.shields.io/readthedocs/mrack?label=Read%20the%20Docs&logo=read-the-docs) ![badge](https://copr.fedorainfracloud.org/coprs/g/freeipa/neoave/package/mrack/status_image/last_build.png)

Provisioning library for CI and local multi-host testing supporting multiple
provisioning providers (OpenStack, AWS, libvirt, podman containers, Beaker).

But in  comparison to multi-cloud libraries, the aim is to be able to describe
host from application perspective. E.g.:

```yaml
network: IPv4
hosts:
- name: master.testdomain.test
  role: master
  group: ipaserver
  os: fedora-31
- name: client.testdomain.test
  role: client
  group: ipaclient
  os: fedora-30
```

This is then combined with provisioning configuration where each provider has
defined meaning for `role`, `group`, `os` params which e.g. translates to
flavors, images, ...

```yaml
provider: openstack  # default provider
openstack:
  images:
    fedora-30: Fedora-Cloud-Base-30-compose-latest
    fedora-31: Fedora-Cloud-Base-31
  flavors:
    ipaserver: ci.m1.medium
    ipaclient: ci.m1.micro
  networks:
    IPv4: net_ci_4
    IPv6: net_ipv6_only
    dual: net_cci_4_6
  keypair: ipa_key
beaker:
  distros:
    fedora-30: FEDORA-30%
    fodora-31: FEDORA-31%
```

So then user can quickly change provisioning location just by changing provider
name without needing to redefine the provider/cloud specifics. This is
especially useful for a lot of jobs sharing the same app specific provisioner
configuration.

```yaml
provider: beaker
```

Or each host can use a different provider:

```yaml
hosts:
- name: master.testdomain.test
  role: master
  group: ipaserver
  os: fedora-31
  provider: openstack
  network: dual
- name: client.testdomain.test
  role: client
  group: ipaclient
  os: fedora-30
  provider: beaker
```

The output is then Ansible inventory with correct group mapping and information
which allows to SSH to the machines.

```yaml
all:
  children:
    ipaserver:
      hosts:
        f30-1.mrack.test: {}
        f33-2.mrack.test: {}
  hosts:
    f30-1.mrack.test:
      ansible_host: 10.0.154.21
      ansible_python_interpreter: /usr/bin/python3
      ansible_ssh_private_key_file: config/id_rsa
      ansible_user: fedora
      meta_dc_record: DC=mrack,DC=test
      meta_domain: mrack.test
      meta_fqdn: f30-1.mrack.test
      meta_ip: 10.0.154.21
      meta_os: fedora-30
      meta_provider_id: 7c3c28f9-4674-4f7f-b413-00bc0b00d711
      meta_restraint_id: 9
      meta_role: master
    f33-2.mrack.test:
      ansible_host: ec2-13-15-16-1.eu-central-1.compute.amazonaws.com
      ansible_python_interpreter: /usr/bin/python3
      ansible_ssh_private_key_file: config/id_rsa
      ansible_user: fedora
      meta_dc_record: DC=mrack,DC=test
      meta_domain: mrack.test
      meta_fqdn: f33-2.mrack.test
      meta_ip: 13.15.16.1
      meta_os: fedora-33
      meta_provider_id: i-08c0d4a86c4b7f7ef
      meta_restraint_id: 1
      meta_role: master
```

## Installation

mrack can be installed via pip, from [PyPI](https://pypi.org/project/mrack/):

```
pip install mrack
```

It is also available for Fedora 32+ via [COPR](https://copr.fedorainfracloud.org/coprs/g/freeipa/neoave/package/mrack/):

```
# enable the copr at your system
sudo dnf copr enable @freeipa/neoave

# install mrack package with all supported providers and cli
sudo dnf install mrack

# install mrack command and e.g. AWS provider
sudo dnf install mrack-cli python3-mrack-aws

# install mrack library to be later used as an import with support of OpenStack provider:
sudo dnf install python3-mrack-openstack

```
---
**NOTE**

Above command will install `mrack` package which depends on (contains) following packages:
- mrack-cli
- python3-mracklib
- python3-mrack-aws
- python3-mrack-beaker
- python3-mrack-openstack
- python3-mrack-podman
- python3-mrack-virt

The `python3-mracklib` is mandatory as it contains core mrack library.
To install only some of `mrack` providers you should install `python3-mrack-{provider_name}`.
To install mrack command a package `mrack-cli` is required.

---

## Run mrack

In order to use the mrack utility a mrack.conf (e.g. [mrack.conf] from the repository(repo/blob/main/src/mrack/data/mrack.conf)) is needed.

mrack looks for the config file in following order:
- `./` actual directory
- `~/.mrack/` home directory
- `/etc/mrack/` system directory

Values from the configuration file could be overriden using mrack utility
options `--mrack-config` `--provisioning-config` `--db` (for more see `mrack --help`).
```
Usage: mrack [OPTIONS] COMMAND [ARGS]...

  Multihost human friendly provisioner.

Options:
  -c, --mrack-config PATH
  -p, --provisioning-config PATH
  -d, --db PATH
  --debug
  --help                          Show this message and exit.

Commands:
  destroy  Destroy provisioned hosts.
  list     List host tracked by.
  output   Create outputs - such as Ansible inventory.
  ssh      SSH to host.
  up       Provision hosts.
```

### Provisioning with mrack

To provision system from the metadata.yaml either run:
```
mrack up
```
or use `up` command's option `--metadata`/`-m` to override path to the metadata file.
```
mrack up --metadata other-metadata.yaml
```

To return resources using mrack run:
```
mrack destroy
```
or use `destroy` command's option `--metadata`/`-m` to override path to the metadata file.
```
mrack destroy --metadata other-metadata.yaml
```

### mrack as python library

```python
# first set up authentication for each provider
# $ export AWS_CONFIG_FILE=`readlink -f ./aws.key`
from mrack.providers import providers
# import all supported providers:
from mrack.providers.aws import PROVISIONER_KEY as AWS
from mrack.providers.aws import AWSProvider
from mrack.providers.beaker import PROVISIONER_KEY as BEAKER
from mrack.providers.beaker import BeakerProvider
from mrack.providers.openstack import PROVISIONER_KEY as OPENSTACK
from mrack.providers.openstack import OpenStackProvider
from mrack.providers.podman import PROVISIONER_KEY as PODMAN
from mrack.providers.podman import PodmanProvider
from mrack.providers.static import PROVISIONER_KEY as STATIC
from mrack.providers.static import StaticProvider
from mrack.providers.virt import PROVISIONER_KEY as VIRT
from mrack.providers.virt import VirtProvider

# register all supported providers:
providers.register(AWS, AWSProvider)
providers.register(OPENSTACK, OpenStackProvider)
providers.register(BEAKER, BeakerProvider)
providers.register(PODMAN, PodmanProvider)
providers.register(STATIC, StaticProvider)
providers.register(VIRT, VirtProvider)


# use global context class
import mrack
global_context = mrack.context.global_context

# init global context with paths to files
mrack_config = "mrack.conf"
provisioning_config = "provisioning-config.yaml"
db_file = "mrackdb.json"
global_context.init(mrack_config, provisioning_config, db_file)

# load the metadata to global_context
metadata = "./metadata-f34.yaml"
global_context.init_metadata(metadata)

# pick default provider:
provider = "aws"

# create Up action

from mrack.actions.up import Up

up_action = Up()
await up_action.init(provider)

# provision machines:
await up_action.provision()

# store the output to db or just use the db later on
from mrack.actions.output import Output
output_action = Output()
await output_action.generate_outputs()

# work with machines...

# cleanup the machines:
from mrack.actions.destroy import Destroy
destroy_action = Destroy()
await destroy_action.destroy()
```

## Contribute

Projects is using [black](https://github.com/psf/black) formater and [isort](https://github.com/PyCQA/isort) to keep consistent
formatting, [flake8](https://flake8.pycqa.org/en/latest/) and
[pydocstyle](http://pycodestyle.pycqa.org/en/latest/intro.html) to ensure following
Python good practices.

Contributions (Pull Requests) are welcome. It is expected that they will pass tox tests and code checkers.
Inclusion of the unit tests for the new code is recommended.
Because of that we have configured [pre-commit](https://pre-commit.com/) hook.
Please enable the feature on your local system and use it before sending a patch.
It could save us lot of re-pushing to the PR.

### Black formatting and isort
Expected formatting can be achieved by running:
```
$ make format
```

Look into [black](https://github.com/psf/black) documentation for possible integration
in editors/IDEs.

### Testing
Just run tox to execute all tests and linters

```
$ tox
# or use make
$ make test
```
