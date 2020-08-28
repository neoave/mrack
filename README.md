# mrack

**Important**: most of the described below is not implemented yet

Provisioning library for CI and local multi-host testing supporting multiple
provisioning providers e.g. OpenStack, libvirt, containers, Beaker).

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
TODO: example
```

## Installation

```
pip install mrack
```

## Run

Atm there is no CLI and it is implemented as Python library

```python
import mrack
# TODO
```

## Contribute

Projects is using [black](https://github.com/psf/black) formater to keep consistent
formatting, [flake8](https://flake8.pycqa.org/en/latest/) and
[pydocstyle](http://pycodestyle.pycqa.org/en/latest/intro.html) to ensure following
Python good practices.

Contributions (Pull Requests) are welcome. It is expected that they will pass tox tests
and include unit tests for new code.

### Black formatting
Expected formatting can be achived by running:
```
$ make format
```

Look into [black](https://github.com/psf/black) documentation for possible integration
in editors/IDEs.

### Testing
Just run tox to execute all tests and linters

```
$ tox
```