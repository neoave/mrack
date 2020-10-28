.. mrack documentation master file, created by
   sphinx-quickstart on Fri Mar 13 21:47:46 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

mrack introduction
===================

mrack is a provisioning library for CI and local multi-host testing supporting
multiple provisioning providers e.g. OpenStack, libvirt, containers,
Beaker).

But in comparison to multi-cloud libraries, the aim is to be able to
describe host from application perspective. E.g.:

.. code:: yaml

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

This is then combined with provisioning configuration where each
provider has defined meaning for ``role``, ``group``, ``os`` params
which e.g. translates to flavors, images, …

.. code:: yaml

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

So then user can quickly change provisioning location just by changing
provider name without a need to redefine the provider/cloud specifics.
This is especially useful for a lot of jobs sharing the same app
specific provisioner configuration.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   self
   guides/index.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
