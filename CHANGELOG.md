# CHANGELOG



## v1.23.4 (2025-05-28)

### Chore

* chore: Enable epel-10 builds in Packit

Replace epel-8/9 with epel-all which points to all current releases,
including epel-10

Addresses https://bugzilla.redhat.com/show_bug.cgi?id=2367449

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`75d8c3b`](https://github.com/neoave/mrack/commit/75d8c3beb5f47ad66f9b8535183c1f23f5099756))

### Fix

* fix: Support pass fetch_url to task

Block tmt&#39;s bootc installation on beaker feature:
https://github.com/teemtee/tmt/pull/3728 ([`4a98123`](https://github.com/neoave/mrack/commit/4a98123dbcfdbf699ed26cceac1cf3b39f36c4b9))


## v1.23.3 (2025-04-25)

### Documentation

* docs: Update maintainer email

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`c02cc90`](https://github.com/neoave/mrack/commit/c02cc90a8f01957a9b570fa339aecfab52d64554))

### Fix

* fix: Translate nested or/and constraint properly

Fixes https://github.com/neoave/mrack/issues/310 ([`4da221c`](https://github.com/neoave/mrack/commit/4da221c1e19e4331f6a650e19f89e0bd3d0f0627))

* fix: Make distro_variants working as patterns

Fixes https://github.com/neoave/mrack/issues/309 ([`60275ee`](https://github.com/neoave/mrack/commit/60275ee735fe21c64053fd73da99a1f82350cc4d))

### Unknown

* fix : Not try to login beaker hub unless needed

mrack should not try to login beaker hub unless need talk to remote API.
Blocks tmt tests: https://github.com/teemtee/tmt/pull/3623#issuecomment-2782901674 ([`cee2f5b`](https://github.com/neoave/mrack/commit/cee2f5b72fe217fb1ede94237623efaf77c182a4))


## v1.23.2 (2025-01-09)

### Fix

* fix: Translate host_requires properly ([`600203c`](https://github.com/neoave/mrack/commit/600203caf9037d3d86796408d3094a14bf85288a))


## v1.23.1 (2024-12-16)

### Fix

* fix: Translate job-group properly ([`0cabc75`](https://github.com/neoave/mrack/commit/0cabc75ff768bebb4287391b263fcefefb613f31))

* fix: Return empty list when there is no content in res_ks_list ([`70e07c1`](https://github.com/neoave/mrack/commit/70e07c191e9f148cb774a1aa5dfc35dc79c5106d))


## v1.23.0 (2024-11-05)

### Feature

* feat: Add support for translanting job-owner of kickstart ([`64a84db`](https://github.com/neoave/mrack/commit/64a84db64bd825ec2551b164734eaa354265f6cb))

* feat: Add translantion for kernel_options and kernel_options_post ([`868523c`](https://github.com/neoave/mrack/commit/868523c9f75005b92e5300d4b877c32d9cfe80f6))


## v1.22.0 (2024-10-17)

### Chore

* chore: setup: package seccomp filter

Add seccomp.json to setup mrack package so it is included on pkg install.

Signed-off-by: Alexander Bokovoy &lt;abokovoy@redhat.com&gt; ([`4d0b63c`](https://github.com/neoave/mrack/commit/4d0b63c5e15a0cd90fb7f44b2a1d340704618bd9))

### Documentation

* docs: Update seccomp configuration example

seccomp.json example from FreeIPA Azure CI tests. It works well for both
docker and podman, both root and rootless.

Signed-off-by: Alexander Bokovoy &lt;abokovoy@redhat.com&gt; ([`9b2d980`](https://github.com/neoave/mrack/commit/9b2d98093aaad4a8fdb7f2391aa94a6281590162))

### Feature

* feat: podman: handle custom network configuration

Allow to add custom network configuration to the network bridge
activated via podman provider.

Signed-off-by: Alexander Bokovoy &lt;abokovoy@redhat.com&gt; ([`f3deca1`](https://github.com/neoave/mrack/commit/f3deca12138c1470cf2b399d00baf81875aa1ef2))

### Fix

* fix: podman: set podman connection information for ansible

Ansible connection.podman.podman connection module uses ansible_host as
a container ID to connect to. Use container ID instead of IP address
which cannot be reached in rootless setup anyway.

It makes `ansible -c podman -i metadata-inventory.yaml` usable in
rootless podman setup because one cannot connect over IP addresses to
the containers as the networking bridge is not visible from the host.

Signed-off-by: Alexander Bokovoy &lt;abokovoy@redhat.com&gt; ([`768bba5`](https://github.com/neoave/mrack/commit/768bba5e4a098ad513a1123400aea03a90156e7d))

### Style

* style: Reformat by black ([`f43d20f`](https://github.com/neoave/mrack/commit/f43d20f486352cd21fada90d301173c98cf5dca5))


## v1.21.0 (2024-08-06)

### Feature

* feat: update pytest-mh output to work with latest version ([`b3e0f7d`](https://github.com/neoave/mrack/commit/b3e0f7df1ebbb0748d267172ef315aa22ae3903a))


## v1.20.0 (2024-07-16)

### Chore

* chore: Update deprecated actions

Due to warnings shown in https://github.com/neoave/mrack/actions/runs/9302766806
It updates actions to new version with Node 20

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`236393c`](https://github.com/neoave/mrack/commit/236393ccd2f16e13fec230b62232fb4bd2fc08ea))

### Feature

* feat: Add support for translanting %pre and main body part of kickstart ([`feeae04`](https://github.com/neoave/mrack/commit/feeae04835574655aff2397dd78a5e1522c5156b))


## v1.19.0 (2024-05-30)

### Chore

* chore: bump black in pre-commit

Additionally formating version.py from running make format

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`784d24b`](https://github.com/neoave/mrack/commit/784d24bb2ae2919bd6d3ba922967d6e2616c2769))

* chore(deps): bump black from 22.3.0 to 24.3.0

Bumps [black](https://github.com/psf/black) from 22.3.0 to 24.3.0.
- [Release notes](https://github.com/psf/black/releases)
- [Changelog](https://github.com/psf/black/blob/main/CHANGES.md)
- [Commits](https://github.com/psf/black/compare/22.3.0...24.3.0)

---
updated-dependencies:
- dependency-name: black
  dependency-type: direct:production
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt; ([`f6f9131`](https://github.com/neoave/mrack/commit/f6f9131ac9e3509c01c85adaee29ccc24f776b7f))

### Feature

* feat: handle list value for add_dict_to_node function ([`f4324bf`](https://github.com/neoave/mrack/commit/f4324bf3291e37bf18ccbc2d229630513baf779c))

* feat: Provide beaker log links

Client like tmt may need to fetch the logs and store log contents ([`aa25ff3`](https://github.com/neoave/mrack/commit/aa25ff362022d86520e4a3196636a043f352b990))

### Fix

* fix(beaker): supress 10_avc_check restraint plugin

It has happpened that this plugin sometimes ran after the dummy task, it reported fail
that there was some AVC (probabaly from other thing) which then failed the job and thus
mrack treated this as a provisioning failure.

This patch instructs restraint to not run this plugin and thus avoid this situation.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`587a9c7`](https://github.com/neoave/mrack/commit/587a9c740035aff501d7c35af5e73de4c04e20c8))

* fix: make delete_host function more robust ([`f1e7590`](https://github.com/neoave/mrack/commit/f1e7590c0680849e81d67d40cbc9105a2fd40b2e))

### Test

* test: speed-up tests by mocking gethostbyaddr

Tests that are using mrack outputs are slowed down by
socker.gethostbyaddr for adhoc IP addresses. This resolution mostly
fails and the test is slow (multiple seconds timeout for single IP).

With this, all python tests are executed within 1.5s.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`6f81e37`](https://github.com/neoave/mrack/commit/6f81e377c56370d62664685a42d5f44e445c522c))

* test: Add add_dict_to_node test ([`2c0c2bb`](https://github.com/neoave/mrack/commit/2c0c2bb88f70bed25c432805b43026a4b6bf4b3f))

* test: Add test for _get_recipe_info function ([`a7db867`](https://github.com/neoave/mrack/commit/a7db867ff0fd53b5b6805efb08597b685b65ab24))


## v1.18.0 (2023-11-27)

### Feature

* feat: Add async_timeout dependency

This dependency was observed missing when installing mrack as a dependency in another python project

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`c158474`](https://github.com/neoave/mrack/commit/c158474018ba5d9d5c3b29bc85f6629668081655))


## v1.17.1 (2023-11-03)

### Fix

* fix: curate_auth func changed to non-async

await call for _curate_auth_url missing in session
creation which caused regression.
function _curate_auth_url changed to non-async,
tests updated to reflect the same

Signed-off-by: Kaleemullah Siddiqui &lt;ksiddiqu@redhat.com&gt; ([`583193a`](https://github.com/neoave/mrack/commit/583193a10db04e22d5340975e9a04fe6c3272531))


## v1.17.0 (2023-10-23)

### Chore

* chore(ci): Temporarely remove packit tests

Until secret injection issue into test farm is solved

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`5251d90`](https://github.com/neoave/mrack/commit/5251d9014b65b4106a98495321ab4c2ad3de9874))

* chore(release): Update semantic release action name and version

Updating action to new name and latest version.
This should not affect behaviour.

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`97a5355`](https://github.com/neoave/mrack/commit/97a5355daf112b447847a2f9dded377389593222))

* chore(release): Upload distribution package to release assets

To fix fedora release, broken in https://github.com/neoave/mrack/pull/272

Fixes https://github.com/neoave/mrack/issues/273

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`6d6cdc6`](https://github.com/neoave/mrack/commit/6d6cdc64c4410f99ba1bea4482ead1264b75247c))

### Feature

* feat(openstack): Append API version to auth_url in credentials

This will save a manual step for the users when setting up clouds.yaml file,
as auth_url field is usually generated without specifying the version.

Version specification is needed by asyncopenstackclient libray

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`3a59761`](https://github.com/neoave/mrack/commit/3a597615b9e28e1304ca2af3d1914db549f9f04c))


## v1.16.0 (2023-10-09)

### Chore

* chore(ci): Fix release workflow build step checking out wrong commit

actions/checkout checks out the latest commit at the time of the workflow trigger,
hence any commit done during the workflow is not included.
Fixing this to checkout the actual latest (release) commit.

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`e8e20f1`](https://github.com/neoave/mrack/commit/e8e20f119f988eedd851495c54ff5c04ae60cc52))

* chore: Bump asyncopenstackclient dependency version

This will allow to use the feature that enables application
credentials authentication.
Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`97a7cd0`](https://github.com/neoave/mrack/commit/97a7cd0518682a90d0655853333294290fea76ac))

* chore(release): Add PyPI action &amp; extract copr step

Due to latest changes to python semantic release
PyPI release is no longer supported and the separate
action (https://github.com/pypa/gh-action-pypi-publish)
is recomended to use while releasing to PyPI.
For the trusted publishing we had to set up the PyPI
account owning mrack to trust neoave/mrack repository
which I did and set up the actions jobs to build
the python package and trigger a truster build.
As an addition i have extracted copr to separate job.

Some resources:
https://docs.pypi.org/trusted-publishers/
https://python-semantic-release.readthedocs.io/en/latest/index.html
https://github.com/pypa/gh-action-pypi-publish
https://python-semantic-release.readthedocs.io/en/latest/migrating_from_v7.html

we had to move from v7 to 8 to use PyPI and have
build steps separate as v7 does that inplace.

Signed-off-by: Tibor Dudlák &lt;tibor.dudlak@gmail.com&gt; ([`278d1b1`](https://github.com/neoave/mrack/commit/278d1b121388e28d2b2ffa7d48cb60657a091471))

* chore: Bump python-semantic-release to v7.34.4

Version 7.33.1 of python-semantic-release action is failing in the container build.
Updating action to this version will solve this issue.

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`9bbd987`](https://github.com/neoave/mrack/commit/9bbd98739e600400d580bc6c815d3225c12beac6))

### Documentation

* docs(Beaker): Add hostRequires documentation section to guides

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`de027fa`](https://github.com/neoave/mrack/commit/de027fa278dd52b5874bd017a12a81901e8ad982))

### Feature

* feat: Add new dependecies to mrack.spec file

Add aiofiles and os_client_config dependencies from latest changes
to mrack.spec definition

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`d6b7298`](https://github.com/neoave/mrack/commit/d6b72983a5bd81977b68de2ecf607ad6b5a26eb0))

* feat(OpenStack): Add clouds.yaml as an authentication method

Add clouds.yaml as an alternative to env vars.
Also, user+password and application credentials formats are both allowed.

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`7bbda34`](https://github.com/neoave/mrack/commit/7bbda3442826d7db19eee2e6c0af17e02a9b156e))

* feat(OpenStack): Import publick key on provision

This will save manual steps and error if the public key was not previously imported to
openstack profile.

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`a5b32e3`](https://github.com/neoave/mrack/commit/a5b32e3b47cd454b7481119cb138e41fb23b022a))

### Fix

* fix(Beaker): Exception has been thrown as raise missed argument

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`db74ae0`](https://github.com/neoave/mrack/commit/db74ae0d392b00d950c36aede08b13480165811a))

### Test

* test: fix pylint issues and use isinstance

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`1a29d86`](https://github.com/neoave/mrack/commit/1a29d86e9218eb6bd86a120726aa12a89681521e))


## v1.15.1 (2023-06-13)

### Chore

* chore: Release version 1.15.1

Releasing mrack version 1.15.1 ([`0135d46`](https://github.com/neoave/mrack/commit/0135d4653ea0d77335037f9f5d8a3440100d3f67))

* chore(Packit): Use yaml magic to run same internal tests for PRs and commits to main

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`608c763`](https://github.com/neoave/mrack/commit/608c7635eaf20d1df310c02080ccc06ae3211010))

* chore(Packit): Add internalt tests per pull request

Add internal tests for pre-defined usecases from
internal repository with the specifications.
These tests are switched by using MRACK_TEST_CASE
environment variable with a test that needs to be
specified in internal repository.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`e03793c`](https://github.com/neoave/mrack/commit/e03793c8aee309cfbce69a098db259cabd99bf0f))

* chore(Packit): add missing build job(s) to Packit config

Packit will now additionally require for each test job requiring build
a build job definition to be present in the Packit configuration file. See details
in https://github.com/packit/packit-service/issues/1775. ([`44023eb`](https://github.com/neoave/mrack/commit/44023ebf54f5196b1cdafdd01ba85d6005d99e49))

### Fix

* fix: Do not reprovision all hosts when server error is detected

when 500 code is detected in the error state of the errored VM
mrack would aggressively remove all hosts which have been
already provisioned properly. Changing logic that
if only a certain percentage of errored hosts is reached.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`fd111f5`](https://github.com/neoave/mrack/commit/fd111f56daa271ccc7824ec0805d007ca4c78f8d))

* fix: Use lower cooldown time to not be too slow in re-provisioning

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`6e499f6`](https://github.com/neoave/mrack/commit/6e499f6cb50a3523db199cd37b877558b9896342))

### Refactor

* refactor: more verbose output when (re)provisioning

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`8062a20`](https://github.com/neoave/mrack/commit/8062a20d0e0f801f036f60afc0ccc62d23d3bf47))

### Test

* test(OpenStack): Add reprovision with dynamic result tests

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`19b52f8`](https://github.com/neoave/mrack/commit/19b52f8df036f36183fd18b7ba87ed457c2d8682))


## v1.15.0 (2023-04-18)

### Chore

* chore: Release version 1.15.0

Releasing mrack version 1.15.0 ([`5903fb9`](https://github.com/neoave/mrack/commit/5903fb92b8f97e2b5851bfaeb20b84b834175fb8))

* chore: fix docs dependencies in tox run

Running `make test` or `tox` failed on building docs as the tox
config did not use the docsi/requirements.txt and thus the required
dependency which was recently added was missing.

This path is changing the tox run to use the docs/requirements.txt
and thus is fixing the issue.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`e9d716e`](https://github.com/neoave/mrack/commit/e9d716e580700bcad5aa42a1e67a240f99898d30))

* chore: add Markdown support to docs and add design section

To be able to include the ssh_options.md design and to allow writing
content in markdown which is more known by people than RST.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`6f1943b`](https://github.com/neoave/mrack/commit/6f1943b1a4525d5e33bd32dba7a3eba18ee6179b))

### Documentation

* docs: SSH options design

Adding a design for configuring ssh options for mrack&#39;s ssh connection
check and Ansible inventory output with main purpose to have the Ansible
inventory settings consumable by Ansible calls used in  pytest-ansible.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`88458e1`](https://github.com/neoave/mrack/commit/88458e12754054def3136a7d919f9d8061fd4300))

### Feature

* feat(outputs): preset username and password for windows host in pytest-mh

This implements the same behavior is pytest-multihost output. ([`86393ab`](https://github.com/neoave/mrack/commit/86393abed8e90ca36e71894f60cedf20046bfdac))

* feat(outputs): merge nested dictionary instead of overriding it

pytest-mh configuration may contain nested dictionary, specifying
username or password in pytest_mh section will result in overriding
the host option, i.e.:

```
pytest_mh:
  ssh:
    username: tuser
    password: tuserpassword
```

will generate wrong configuration where ssh/host is not set.

This patch makes sure that the ssh key is merged instead of overwritten. ([`4c26b5f`](https://github.com/neoave/mrack/commit/4c26b5ff7934efc8895eb83b3b89fe01a4d64257))

* feat(utils): add merge_dict

To combined two nested dictionaries. ([`4dde2e5`](https://github.com/neoave/mrack/commit/4dde2e5fb54b352d53048c2e147f63c3cbc79932))

* feat: configurable ssh options

This implements configurable ssh options according to design:

https://mrack.readthedocs.io/en/latest/designs/ssh_options.html

With the idea that those options will be used for SSH connections
check as well as added to generated Ansible inventory so that other
tools can use it.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`a4e5075`](https://github.com/neoave/mrack/commit/a4e50752d2c804b196b1290903ce6e12030fc5d5))

### Fix

* fix: Handle 403 AuthError (out of quota) in openstack provisioning

This modification will cath the Exception, to free all hosts and wait for
quota to be available again

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`e29031b`](https://github.com/neoave/mrack/commit/e29031b6dca037a3a3563c3646ed1f5fcf88c9ac))

### Refactor

* refactor(provider): take max_utilization out to method to ease mocking

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`121c5db`](https://github.com/neoave/mrack/commit/121c5db1e17143737d138327fe620874f9c40b3d))

* refactor: fixes _openstack_gather_responses test warnings and exec time

This refactoring of the method fixes test warning &#34;coroutine was never awaited&#34;.
Additionally mocking async sleep in the test to speed up execution time.

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`5440be1`](https://github.com/neoave/mrack/commit/5440be195cdbba5b872674c6662941a0021f030e))

### Test

* test: Add missing strategy_retry test

This covers the functionality added in https://github.com/neoave/mrack/pull/229
and https://github.com/neoave/mrack/pull/254

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`f9f0e33`](https://github.com/neoave/mrack/commit/f9f0e335e1ce9d7df0a1c0aa999b82730aa99db0))

* test: Add missing tests for fixed code from https://github.com/neoave/mrack/pull/245

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`dc74ced`](https://github.com/neoave/mrack/commit/dc74cedfa0de5061c11bd348d76983cc632953a7))


## v1.14.1 (2023-03-16)

### Chore

* chore: Release version 1.14.1

Releasing mrack version 1.14.1 ([`af38b70`](https://github.com/neoave/mrack/commit/af38b7079f4d8098c543d379bc1648ac6d29b251))

### Fix

* fix: mrack not re-provisioning hosts which were destroyed

Since I have coded a regression when trying to re-provision
mrack is not setting variables for another loop correctly
error_hosts is updated correctly but when keeping success_hosts
not changed to empty list it creates a illusion of hosts
which were deleted because of re-provisioning strategy
that they are still up and running.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`a9c4e62`](https://github.com/neoave/mrack/commit/a9c4e629fa448461bc037c3c9f24c8950bf2b1bb))

* fix: Replace coroutines with tasks to avoid RuntimeError

Fixing code block in _opentack_gather_responses method to avoid
RuntimeError when a coroutine is reused in the loop.

Including a unit test for this method as part of the commit

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`17b45e4`](https://github.com/neoave/mrack/commit/17b45e4c5a6046bae315f885dd4934aba0ed8c8f))


## v1.14.0 (2023-03-08)

### Chore

* chore: Release version 1.14.0

Releasing mrack version 1.14.0 ([`c209923`](https://github.com/neoave/mrack/commit/c209923bf02ef46f1bdbce344bce78485d1c080b))

### Feature

* feat(outputs): allow to overwrite ansible layout

New field in metadata file is added:

```
config:
  ansible:
    layout:
      ...
``` ([`d3da251`](https://github.com/neoave/mrack/commit/d3da25156f91313ea5020bace15f20b7b0b5ce3f))

* feat(outputs): allow to choose which outputs should be generated

Add &#34;outputs&#34; key to the metadata file. E.g.:

```
outputs:
- ansible-inventory
- pytest-multihost
- pytest-mh
domains:
   ...
phases:
   ...
```

Defaults to ansible-inventory and pytest-multihost. ([`d3ac20d`](https://github.com/neoave/mrack/commit/d3ac20d4d3615893f4781c0142f47eb576db30e2))

* feat(outputs): add support for pytest-mh

Add support for generating pytest-mh configuration file, which is
similar to pytest-multihost but can make things more clear with
custom generator.

Add additional options:
- pytest-mh to mrack.conf, default path to the config file
- pytest_mh to host metadata, add additional values to the host config ([`66f2877`](https://github.com/neoave/mrack/commit/66f2877f0b3b33ced341fd6faf307d42414a4742))

* feat(utils): relax condition in get_fqdn

It should return the hostname even if it is part of different domain. ([`db633b7`](https://github.com/neoave/mrack/commit/db633b75a59880e901248b80e38d076468c7c5da))

* feat(utils): add get_os_type ([`b1f5318`](https://github.com/neoave/mrack/commit/b1f5318f7beb0e48b702dc0eafe675c20baf3366))

### Fix

* fix(OpenStack): Add missing await for self._load_limits() method call

Co-authored-by: David Pascual &lt;davherna@redhat.com&gt;
Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`d95e65f`](https://github.com/neoave/mrack/commit/d95e65f70f5c76bb08f25093ed5cafc1af32df6d))

* fix(outputs): remove config section from pytest-multihost ([`13ad3df`](https://github.com/neoave/mrack/commit/13ad3df70f3c6adc5d5d348bb91227235b1e2ff7))

* fix(outputs): add host to correct group in layout

If the group was empty, it returns empty dictionary and the condication
fails resulting in creating a new group instead of adding the host to
an existing one. ([`0735e36`](https://github.com/neoave/mrack/commit/0735e36c16aec74c7920f755bf7367d8ba59c790))

### Refactor

* refactor(AWS): change variable name typo in get_ip_addresses

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`e319b73`](https://github.com/neoave/mrack/commit/e319b73377fcacdb67df11fa7f1aa0291702380f))

* refactor: Update supported providers

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`d0c2d8f`](https://github.com/neoave/mrack/commit/d0c2d8f4d90ec7e2bc6b0e63dd0b5fdc05724947))

* refactor(black): reformat code

tox failed black tests ([`0ab88e6`](https://github.com/neoave/mrack/commit/0ab88e6f79985f26f9b4884e1f2d68274aad0219))


## v1.13.3 (2023-03-01)

### Chore

* chore: Release version 1.13.3

Releasing mrack version 1.13.3 ([`acf943e`](https://github.com/neoave/mrack/commit/acf943e2d6fd53e9376e0e4731abd0f6c1e0d35b))

### Fix

* fix(OpenStack): await loading limits to not break provisioning

Resolves: https://github.com/neoave/mrack/issues/248

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`0f62237`](https://github.com/neoave/mrack/commit/0f622374105abb52adf160fb5dcb9240da7ae013))


## v1.13.2 (2023-03-01)

### Chore

* chore: Release version 1.13.2

Releasing mrack version 1.13.2 ([`13e2635`](https://github.com/neoave/mrack/commit/13e263597f51900a3a8e235c6d6f87e5f8c4057f))

* chore: change back mrack dist release to 1

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`61e515f`](https://github.com/neoave/mrack/commit/61e515fc783d6e4be49b850e95279c7fe314d085))

### Fix

* fix: Use get method when host error object is a dictionary

This makes sure to not throw an exception when host.error
is not a dictionary and we can not use .get() method

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`06f18d1`](https://github.com/neoave/mrack/commit/06f18d19353d021c9bcf0c1a509cdc0867aae2a7))

* fix(Beaker): rerurn common dictionary when validation fails

when Beaker distro/image is not recognized by beakerhub
mrack failed with exception as newer code expects
dictionary error object.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`fd33d68`](https://github.com/neoave/mrack/commit/fd33d68bd7991be61038d2df340720c7ef09b14f))

* fix(OpenStack): Add exception parameter when validation fails

Adding second parameter to ValidationError exception
gets rid of mrack exiting with exception.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`b6c5ef4`](https://github.com/neoave/mrack/commit/b6c5ef4edbcac9ed0902eebbb705a78401345532))

* fix(OpenStack): load limits properly by one method

when creatring utilization method for openstack there
was a problem that limits were read incorrectly.
moving code to private method reused in utilization
and can_provision methods to get rid of copy-paste errors.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`fa2c779`](https://github.com/neoave/mrack/commit/fa2c779840e773958016dd7df37857140c4afaff))


## v1.13.1 (2023-02-21)

### Chore

* chore: Release version 1.13.1

Releasing mrack version 1.13.1 ([`469298d`](https://github.com/neoave/mrack/commit/469298da7d00a6162dea5cffd09b3048536f8e95))

### Fix

* fix(MrackConfig): Fix MrackConfig class properties

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`1421b37`](https://github.com/neoave/mrack/commit/1421b371d1eef6509f9cdc4ef81f57c8a8a37751))


## v1.13.0 (2023-02-17)

### Chore

* chore: Release version 1.13.0

Releasing mrack version 1.13.0 ([`38313f8`](https://github.com/neoave/mrack/commit/38313f84d6eda16ff0d118171dab04011058ebe5))

* chore: set packit to sync changelog as well

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`32a754b`](https://github.com/neoave/mrack/commit/32a754b5d15830dfbdd188e8bc47b9a82259c654))

* chore: sync fedora spec to upstream to maintain changelog history for fedora

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`b0512b4`](https://github.com/neoave/mrack/commit/b0512b4f3a65af6aec265c554c7aafeee53d82e9))

* chore: Generate proper changelog from commit history when releasing

When releasing the package mrack.spec was not enriched
by the history of changes compared to previous release
this is enhancing the workflow to have proper changelog

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`be7b50a`](https://github.com/neoave/mrack/commit/be7b50a03498b7e09b11bf4d976793e8e7cb825f))

* chore: Bump python-semantic-release to latest

Python-semantic-release had problems fetching
the commit&#39;s sha from work directory. This
issue should be fixed in latest release of action.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`98f4035`](https://github.com/neoave/mrack/commit/98f403574740a3c6989b95a8e4ecdbaf066ce498))

* chore: use custom release_suffix for PR testing via packit

Thus making the Release higher than the one in repos and thus tmt
in tf/packit integration will prefer the packages from packit.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`72b9b9c`](https://github.com/neoave/mrack/commit/72b9b9cd241b8ce4d0c9a5b72214b3236af034fc))

* chore: disable pylint pre-commit hook

As it is failing and it needs more time to fix.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`f3f734a`](https://github.com/neoave/mrack/commit/f3f734abecaeedd97dc4dca5babd1ae29c7ac3c2))

* chore(Packit): Add synchronization of tmt plans and tests

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`4aa9b0a`](https://github.com/neoave/mrack/commit/4aa9b0a575c27f49bae5e8b681bef699c8ac7337))

* chore(Packit): Configure users on whose actions packit is allowed to be run

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`02c3e01`](https://github.com/neoave/mrack/commit/02c3e0176d3445aa97910d7e96643129e7e7c61d))

* chore(Packit): Add missing ci.fmf to synced files

Missing ci.fmf sync causes fedora message being not recognized
in dowsntream and thus expected tests to be marked as failed
even when tests might be run and passing.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`cf14ed9`](https://github.com/neoave/mrack/commit/cf14ed9c17e4070059cb47bf5ecd2c226ffea813))

### Feature

* feat(OpenStack): Provide a way to disable network spreading

The network spreading feature has aimed to utilize networks usage
however for some particular products it might be not optimal
to have resources on different networks. This patch is adding
options to mrack.conf which can disable the feature and also
set the acceptable threshold of network utilization for OpenStack.

network-spread = no  # disable the feature
network-spread = force  # force the feature
network-spread = allow  # allow the feature (default)
max-network-utilization = 75 (default=50)

When the request size exceeds max network utilization mrack
falls back to default behavior of spreading the requests to
different networks (Corner case of having too few IPs).

mrack fails if the feature is disabled and request is too big.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`777862f`](https://github.com/neoave/mrack/commit/777862fc917bc1dc436f008f4693c991e101dd0d))

* feat(AWS): Add utilization check method

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`46141dc`](https://github.com/neoave/mrack/commit/46141dc4aa2cf2378aee2f03dc31e6273f5c9ec1))

* feat(OpenStack): Add utilization check method

minor fix: typo _opentack -&gt; _openstack

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`bb80060`](https://github.com/neoave/mrack/commit/bb80060149e5f7228a0f56f2bfacb2ec708d5a34))

* feat: Do not use same sleep for every mrack run

Adding logic to randomize the timeout to basically
set the waiting timeout to vary from 45-75 minutes randomly
and the poll time to 45-75 seconds accordingly
so if there are multiple parallel runs of mrack they wait
different amount time before poll and increase chance to get resources
quicker than other concurrent runs of mrack requests

Add cooldown after error host was found to wait before
another retry and resource check cycle for random time
between one poll sleep and 2* poll sleep (45-75 s is one poll)

Add utilization method template to decide whether to
destroy all machines or to keep them while re-provisioning
to free some resources when there is provided highly utilized.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`55f9c2c`](https://github.com/neoave/mrack/commit/55f9c2c63c1882a0e5b1f99aa9dc94646c9b6068))

* feat(AnsibleInventory): Allow additional global level values

Add support for global level ansible_inventory records
which can be eventually overwritten by domain and host defined values.
Minor fix of logig in pytest multihost code - adding deepcopy.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`a7a896a`](https://github.com/neoave/mrack/commit/a7a896aa8879a8630dc1cfcd6572ea1402c3c7ba))

* feat(AnsibleInventory): Allow additional domain level ansible inventory values

Add support for domain level ansible_inventory records which
can be eventually overwritten by host defined values.
Added unit tests to test this feature.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`91c562c`](https://github.com/neoave/mrack/commit/91c562c1af45eb747ee46de1c08ca352b3370bcb))

### Fix

* fix(OpenStack): fix condition for network to get in interval

In corner case with 2 ip adresses left and requesting
2 ip adresses from mrack there was an issue that mrack
has picked same network for both request which eventually
break the request. Fixing the condition that when counting
weights the mrack will divide two ips like it should.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`ff7331d`](https://github.com/neoave/mrack/commit/ff7331d54069c4b1a264dc12f1bf1f5934762abb))

* fix: fqdn in name is ignored and mrack guesses the name instead #237 ([`943316d`](https://github.com/neoave/mrack/commit/943316d736516b0b5025b10315de6599e491fdd6))

### Refactor

* refactor(OpenStack): make private openstack methods truly private

renaming the openstack private methods to be private
openstack had too many public methods and this seems
to be proper fix, to have public just the needed ones.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`4467cc2`](https://github.com/neoave/mrack/commit/4467cc2a297e64a07baaed5eb2f127c5f74c72aa))

### Test

* test: add extra dnf options when dealing with rhel/epel 8

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`72cc2f3`](https://github.com/neoave/mrack/commit/72cc2f310c68ee90ee4ff6f34d8b1f70d1a198fe))

* test(OpenStack): Fixup the network spread tests

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`a0e76dd`](https://github.com/neoave/mrack/commit/a0e76ddb72ae4a0b8876d9eb2425865bdd04065b))

* test(OpenStack): rewrite network alloaction tests

To use less copy paste and have visible both inputs and outpus in
declarion.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt;
Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`88b9332`](https://github.com/neoave/mrack/commit/88b9332f1c65ba8d4f13799acd60fb2517c207e1))

* test(AnsibleInventory): global level output values override

Add test for the feature to support global level
ansible_inventory records which can be eventually
overwritten by domain and host defined values.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`6ce3927`](https://github.com/neoave/mrack/commit/6ce39273f258b0f371d21426a675f22a0fc6cea1))

* test(OpenStack): Update calls in openststack tests

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`109b03c`](https://github.com/neoave/mrack/commit/109b03c62cc65bf298a4b5d122f131790d8f659f))


## v1.12.3 (2022-12-13)

### Chore

* chore: Release version 1.12.3

Releasing mrack version 1.12.3 ([`6bd9e17`](https://github.com/neoave/mrack/commit/6bd9e17e71c891b99a0f569b383f67da4ad55a13))

* chore(Packit): Enable copr build for commit to main only.

switching copr_build job to commit rule as pull request job
may not need this with tests enabled in Testing Farm per PR.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`52bb87e`](https://github.com/neoave/mrack/commit/52bb87efd6ecee482497c3d3d78a4c1ed8433a75))

* chore(Packit): Enable TF tests job to run on pull request.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`635d008`](https://github.com/neoave/mrack/commit/635d00814a6c2afd73abe54f30818ade95b3b4a0))

* chore(Packit): Add fedora gating.yaml to synced files.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`9c83b5d`](https://github.com/neoave/mrack/commit/9c83b5d8f4d8bb4f399b378acce08b2928319224))

* chore(TestingFarm): Add gating for fedora workflow

Adding basic gating smoke tests for fedora workflows
which are run in Testing Farm using tmt plan.
This workflow should allow us to have some
testing automation downstream (Fedora)
and catch package regressions in future.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`a07785c`](https://github.com/neoave/mrack/commit/a07785c4f845aef008599521537a9e9f478e1d5a))

* chore(Packit): enable epel-8 and epel-9 updates and tests

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`5a726db`](https://github.com/neoave/mrack/commit/5a726db5b753e7b96367ea64f21d3c0341860707))

### Fix

* fix: Add cache decorator for older python versions.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`c4c1a67`](https://github.com/neoave/mrack/commit/c4c1a6701eee9d17df20c66527c062f407d260ae))

* fix(mrack.spec): Missing dependency in c8s for beaker-client

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`aac3ed4`](https://github.com/neoave/mrack/commit/aac3ed4fe89f42be9fb0df85fad5d0decc635607))

* fix(AWS): refactor sources to be py3.6 compatible

When considering mrack to be part of
the tmt which is used even in epel8 and epel9
we might be limited to not use latest python
features which one of them is := opearator.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`cd0335a`](https://github.com/neoave/mrack/commit/cd0335aa8c3115260c83c4f0e84cd5be10a84c0d))


## v1.12.2 (2022-12-02)

### Chore

* chore: Release version 1.12.2

Releasing mrack version 1.12.2 ([`497e95b`](https://github.com/neoave/mrack/commit/497e95b3b81fb0e0ad56d7724c0cc08accdc1a4f))

* chore: Use python 3.10 in GH actions

Using latest python will help us to identify
latest changes and regressions early in upstream PRs.
Bumped repo versions in .pre-commit-config.yaml
to point to latest stable releases per available check.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`3397948`](https://github.com/neoave/mrack/commit/33979481bfa67c5b16c553c1df229dd39e7195be))

* chore(pytest): add missing python_path when using pytest &gt;=7.0.0

Reference: https://docs.pytest.org/en/7.0.x/reference/reference.html#confval-pythonpath

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`9303259`](https://github.com/neoave/mrack/commit/9303259dcc1ca19cb4ba93846d0fbb82396f3d46))

* chore(Packit): Add upstream_tag_template to .packit.yaml

This configuration options sets up the packit tag template
for packit to know what tag format to expect when checking
the release to properly set the variables for the archives.

Resolves: https://github.com/neoave/mrack/issues/220

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`a7bf366`](https://github.com/neoave/mrack/commit/a7bf366261fa5c24dbbd7b8b32e6896276a6957a))

### Fix

* fix: Owner requirement boolean parsing from string

When parsing boolean values from string using bool()
builtin funtion string which is not empty returns True
Writing a util function to convert such strings
to proper boolean values. NOTE: distutil implementation:
from distutils.util import strtobool
will be deprecated and removed in future python releases
thus implementing a funtion ourselves might be
future proof solution at this time.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`592f364`](https://github.com/neoave/mrack/commit/592f364e86d838e630259c0ce91928d15c10d00d))

### Refactor

* refactor: pylint fixes related to Python 3.10

We need to first fix some pylint isses before
changing checks python version to 3.10.
pylint has still some issues with Python 3.11

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`71abf31`](https://github.com/neoave/mrack/commit/71abf31c9bc57410f4809ff7d5247f0d16560775))

### Test

* test: Fix test_utils.py to be included in pytest run

When tests were outside of pytest class the tests
were not run by pytest and thus github actions
were always green. Created TestPytestMrackUtils
class containing all the mrack unit tests.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`6e3563b`](https://github.com/neoave/mrack/commit/6e3563b2074a146f8aa8dfe1ad2e05ee7494c3ed))

* test: Add test for value_to_bool util function

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`de0986f`](https://github.com/neoave/mrack/commit/de0986f4c13b45741cd613345d07f42601c90e46))


## v1.12.1 (2022-11-24)

### Chore

* chore: Release version 1.12.1

Releasing mrack version 1.12.1 ([`cd95a01`](https://github.com/neoave/mrack/commit/cd95a0149730dd7f595508be6daf5dfc08e3ece0))

* chore: Add packit service configuration

This commit is enabling packit service for the mrack
project. see: https://packit.dev/docs/configuration/

To start using Packit we did:
- set up integration on GitHub side and selected free plan
- got approved by mapping FAS identity (tdudlak) to the
  service via: https://github.com/packit/notifications/issues/482
  by linking neoave organization with FAS account
- configured the wanted features via this commit

This commit sets up packit jobs to:
- check build per pull request
- trigger copr build after a release
- create fedora PRs to mrack project with updates
- create koji build per commit merged to fedora&#39;s mrack
- create bodhi updates per each successful koji build

This allows us to forget about backporting pathces
to Fedora repo and automate release workflow per
each supported Fedora release currently not EOL.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`378ec61`](https://github.com/neoave/mrack/commit/378ec61c0914d0446a02e4f6b8ae071168b46671))

* chore: bump commit message checker version

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`80ade20`](https://github.com/neoave/mrack/commit/80ade20788131aee31ed6721590803996c50c027))

* chore: Set persist credentials to false at checkout

This will not force the actions user credentials
to be stored into git config which will later
result in using github_token of release actor.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`e281c32`](https://github.com/neoave/mrack/commit/e281c32d8e691cc83e0e2fcc86d1a5596fd6c3c0))

* chore: Use personal GH token to release mrack

When branch protection is enabled only real
user (not gh-actions as it is bot) can push
to the main branch when there is Pull Request
required and approvals for particular PR.
With exception added to the users which can bypass
the protection rules we should be able to release
with personal GH token generated for the user.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`bd3a08a`](https://github.com/neoave/mrack/commit/bd3a08a03d6a0c0bf74e2c14173766c3929e988a))

### Fix

* fix: make db file and provisioning file optional

When initializing the global context these files
should be passed to the init as optional param
when path is specified in mrack cli tool.
Otherwise mrack should only load the data from
the mrack.conf file records and rely on paths
set there for db and provisioning-config.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`9449082`](https://github.com/neoave/mrack/commit/94490824e8e6d3713328e08b99acb2a8a83623f8))

* fix: Use MrackError in action Up to catch all possible mrack errors at once

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`990224b`](https://github.com/neoave/mrack/commit/990224bd326ee2a70021a558a46596005121159b))

* fix: validate ownership and lifetime only for AWS and OpenStack

Limitin only for certain providers is needed as the owner doesn&#39;t matter for
static (vm already present somewhere, could be owned by completely different
person), podman, libvirst (vm running on current machine, no need for owners).

But it makes sense for any cloud like OpenStack, AWS, Beaker.

Enabled only for AWS, OpenStack as Beaker doesn&#39;t work with ownership
yet.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`111d481`](https://github.com/neoave/mrack/commit/111d481e9bac692854a1b2764a760608b7fc2046))

### Refactor

* refactor: Use MrackError in run.py

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`40345f0`](https://github.com/neoave/mrack/commit/40345f0441e50787b2fd11f8ccf257b0d474f18e))

* refactor: Add MrackError as Parent exception class

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`883dd81`](https://github.com/neoave/mrack/commit/883dd81a95bdf889ab290bd5c245ac6ee3c39e60))

* refactor(OpenStack): raise Validation error when validation fails

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`1b87ce5`](https://github.com/neoave/mrack/commit/1b87ce524593b0f8cfbc336b16da460e8883fa05))

### Test

* test(OpenStack): update test according to new changes in error handling

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`1c9a75e`](https://github.com/neoave/mrack/commit/1c9a75e0d79e2f272bcfee40ad3689691ab875cb))


## v1.12.0 (2022-11-14)

### Chore

* chore: Release version 1.12.0

Releasing mrack version 1.12.0 ([`81db5bf`](https://github.com/neoave/mrack/commit/81db5bf42c6defd8206977fa751e4b88a3002a89))

* chore: include optional dependency of gssapi

gssapi pkg now required for new added mrack
feature to add owner/lifetime info into the
VM

Signed-off-by: ksiddiqu &lt;ksiddiqu@redhat.com&gt; ([`fd4e0db`](https://github.com/neoave/mrack/commit/fd4e0db682d5049718694b2bd077bec5a50ed2a6))

* chore: disable automatic runtime deps discovery for rpm build

As it is adding all dependencies to all rpms and ignoring the individual
nuaces between packages. I.e. without this, we cannot install
python3-mracklib without the rest.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`e11c9a7`](https://github.com/neoave/mrack/commit/e11c9a776061829811c3a96f9f03e1a7df9b510e))

* chore: rpm and clean-rpms targets in Makefile

To make buiding of rpms easier - for adhoc testing/development and sort
of work as a documentation how to do it as it is easily forgotten when
not doing often.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`30f1d5d`](https://github.com/neoave/mrack/commit/30f1d5d662d9023a672c6068f95d323a3639ba64))

### Feature

* feat(aws): Add owner/lifetime info in VM&#39;s metadata

Owner and lifetime info will be added into VM&#39;s metadata
for AWS provider. This info will give info who
owns the VM and what is the lifetime of the VM which will
be used for notifying owners and cleaning up the resources
based on lifetime of the VMs.
If owner info not fetched, user notified with custom error
message for follow up action to take up.

Signed-off-by: ksiddiqu &lt;ksiddiqu@redhat.com&gt; ([`ed9e977`](https://github.com/neoave/mrack/commit/ed9e977f4f56c5cc5cda6f0b4ad0f09cdaab89b9))

* feat(openstack): Add owner/lifetime info in VM&#39;s metadata

Owner and lifetime info will be added into VM&#39;s metadata
for Openstack provider. This info will give info who
owns the VM and what is the lifetime of the VM which will
be used for notifying owners and cleaning up the resources
based on lifetime of the VMs.
If owner info not fetched, user notified with custom error
message for follow up action to take up.

Signed-off-by: ksiddiqu &lt;ksiddiqu@redhat.com&gt; ([`e33038e`](https://github.com/neoave/mrack/commit/e33038e4de2fcca8d58564508b1d6786fbe8d01b))

### Fix

* fix: integration test_actions test fixes

Integration test test_actions.py failing due to
introduction of new option(require-owner) in mrack.conf
as global_context was not set which is now being
set using a fixture in test_actions.py

Signed-off-by: ksiddiqu &lt;ksiddiqu@redhat.com&gt; ([`07682c1`](https://github.com/neoave/mrack/commit/07682c148a7fe7d40b8e5761e9845cdd85972013))

* fix: Do not use deprecated asyncio.coroutine wrapper

Python 3.11.0 completely dropped support for the
asyncio.coroutine. As it was already deprecated
we should use the proper way of decorating the
click functions in the mrack run.py.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`c66fef7`](https://github.com/neoave/mrack/commit/c66fef729754d3f28f8014e901524184bba5e18d))


## v1.11.0 (2022-11-03)

### Chore

* chore: Release version 1.11.0

Releasing mrack version 1.11.0 ([`84e055e`](https://github.com/neoave/mrack/commit/84e055e082daee90293517db16980f9c7c1f610c))

* chore: bump python version in tox.ini

In our automation we rely on python 3.9
setting tox.ini to same version

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`22993be`](https://github.com/neoave/mrack/commit/22993bee3612e928176cd2f8e8e50afae91ee1da))

### Feature

* feat(AWS): Add multiple subnet support &amp; IPs availability check

- Now mrack expects either subnets_id (prioritized) or subnet_id field in the provisioning config file or metadata (provder config) in AWS key field.
  A list of subnets can be specified where host can be provisioned. It is expected that the subnets are in the same VPC.
- mrack checks that the amount IPs available with all the subnets specified are enough to provision all the host concurrently.
  The amount of IPs available for provisioning are the sum of the available IPs in the provided subnets.
  Otherwise provisioning will retried after a wait and/or cancelled.
- Add rule to pylintrc file to allow more local variables in methods.

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`742ed9c`](https://github.com/neoave/mrack/commit/742ed9cf2e6ffe32575584ab405aa034f8049128))

### Fix

* fix(mrack.spec): fix the location for mrack.egg-info

fixing removal of bundled egg-info which is located
in the src directory. removing option &#39;-f&#39; from rm.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`9a998bc`](https://github.com/neoave/mrack/commit/9a998bce750c09aa1bd2d2f0007cc67b729ab8f3))

* fix(mrack.spec): cli package files and deps

Fixing the cli package dependency by adding
the Requires: python3-click and removing
unnecessary file run.py from lib package
and move it to cli package where it belongs

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`f76c31a`](https://github.com/neoave/mrack/commit/f76c31a7fdd297ae121f2001980742783cf62687))

* fix(Podman): Fix action ssh import failing if podman provider not found

When podman provider is not installed as plugin
we should not import it in ssh.
Ignoring the import error will fix tracebacks.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`87c397e`](https://github.com/neoave/mrack/commit/87c397eb0fd1c84384bda7dfe28e446d35158764))

* fix(mrack.spec): remove unecessary statement

the python_provide should be used
for python*- packages only thus removing.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`dbb43f3`](https://github.com/neoave/mrack/commit/dbb43f30a0a978ce8570f1d3d23efb28cfd440a5))

### Refactor

* refactor(Beaker): transformer test to use dictionary

Refactor beaker transformer test to use dictionary instead of multiple
parameters in function call. This increase readability of test. ([`b58f717`](https://github.com/neoave/mrack/commit/b58f717a3df7ee3821413d1218a78c8f890e29ea))

### Test

* test(Beaker): add tests for non-default keys

Add test for non-default requirement keys [retention_tag, tasks, product]
Add more hosts with such values to test metadata topology

Signed-off-by: Erik Belko &lt;ebelko@redhat.com&gt; ([`d00dbe5`](https://github.com/neoave/mrack/commit/d00dbe5011cd23e90aec22f4b9d1028088af2de1))

* test(Beaker): add check for additional keys

Add check for additional keys [tasks, redention_tag, product]
to beaker transformer tests.
Resolve: https://github.com/neoave/mrack/issues/186 ([`9c6869f`](https://github.com/neoave/mrack/commit/9c6869f29f3f8bd4db3a4513ec74797a4ca02a58))


## v1.10.0 (2022-10-26)

### Chore

* chore: Release version 1.10.0

Releasing mrack version 1.10.0 ([`7ff67e2`](https://github.com/neoave/mrack/commit/7ff67e2f413b66ecbc8810f95f1d52df881d7c33))

* chore: bump versions of GitHub actions

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`1ca449d`](https://github.com/neoave/mrack/commit/1ca449d2f08344f44df1b5e890d53dfc524d830d))

### Feature

* feat(OpenStack): Pick from all networks based on load

With this patch OpenStack is able to pick Network from
all of networks based on network load and requirement
got from the metadata. Each of required host gets
its own position, aka weigh in interval &lt;0, 1&gt;
based on the order (index) in metadata. Before that
all of the networks are &#39;normalized&#39; in a way that
the random selection from subset of networks
(or all of network if number of hosts &gt; number of networks)
is divided to effective range (multiple intervals &lt;0, 1&gt;)
for the network based on the relative network weight
compared to full capacity of considered networks.

An example:
- considering 5 host request
- picked 5 networks where availability is &gt; 5%

Host weights:
- host 1 - 0/5 = 0
- host 2 - 1/5 = 0.2
- host 3 - 2/5 = 0.4
- host 4 - 3/5 = 0.6
- host 5 - 4/5 = 0.8

Network availability:
- net 1 - 20 addresses
- net 2 - 100 addresses
- net 3 - 130 addresses
- net 4 - 145 addresses
- net 5 - 105 addresses

Full capacity of these 5 nets: 500

Normalized network range:
net 4 - &lt;0, 0.29&gt;
net 3 - (0,29, 0.55&gt;
net 5 - (0.55, 0.76&gt;
net 2 - (0.76, 0.96&gt;
net 1 - (0.96, 1&gt;

Which will divide networks for hosts:
host 1 =&gt; net 4 (0 falls into net 4 interval)
host 2 =&gt; net 4 (0.2 falls into net 4 interval)
host 3 =&gt; net 3 (0.4 falls into net 3 interval)
host 4 =&gt; net 5 (0.6 falls into net 5 interval)
host 5 =&gt; net 2 (0.8 falls into net 2 interval)

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`317c2ac`](https://github.com/neoave/mrack/commit/317c2ac8c11580b078f306192309a0637522aed5))

### Fix

* fix: Update paths in specfile and python_provide

Fixing the last minor pieces for the upstream BZ:
https://bugzilla.redhat.com/show_bug.cgi?id=2134387
Summary for mrack-cli, Installation of *.pyc files
and adding the python_provide to python3-* subpackaged

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`5262bca`](https://github.com/neoave/mrack/commit/5262bca0782e343927aa0c5ee2be63c10f9c9e0d))

* fix(utils): add encoding to open functions

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`e28e044`](https://github.com/neoave/mrack/commit/e28e044e9398c380d64ef0980eab4239881f98d1))

* fix(Podman): add encoding to open function

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`84cd4dc`](https://github.com/neoave/mrack/commit/84cd4dcf53d5888c6537fdb5f3bd4ec99c83583c))

* fix(Beaker): Add encoding to open when opening ssh key

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`71ef2f1`](https://github.com/neoave/mrack/commit/71ef2f102f8110f84c12914a1bbd2308a5f592b2))

### Refactor

* refactor: create more verbose output when listing reqs

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`887a13e`](https://github.com/neoave/mrack/commit/887a13ec61d7910174ec03d790b204ec192b5e50))

### Test

* test(OpenStack): network picker check

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`e7646b8`](https://github.com/neoave/mrack/commit/e7646b84c577129f22c4c36f8f90f418a9ea99a5))


## v1.9.1 (2022-10-20)

### Chore

* chore: Release version 1.9.1

Releasing mrack version 1.9.1 ([`ab4c1c6`](https://github.com/neoave/mrack/commit/ab4c1c69872c37598343c123bcd6a93960130ad5))

* chore: Use branch main instead of master

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`221ea15`](https://github.com/neoave/mrack/commit/221ea153fba59fc0db6284c99f3a6fd3b85bbe2f))

### Fix

* fix: add CHANGELOG.md to MANIFEST.in

This change is needed to include CHANGELOG.md
file in the tarball of package release in the
github&#39;s pages and sources available upstream.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`64fa546`](https://github.com/neoave/mrack/commit/64fa546e9fc24e30ea655c2ee211f5b348272929))

* fix: Update spec to match fedora community standard

Update the mrack specfile to match fedora packaging
standards and to move this project to official fedora
packages via: https://bugzilla.redhat.com/show_bug.cgi?id=2134387

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`91726d7`](https://github.com/neoave/mrack/commit/91726d786414620b5556165e7a90adc672bfc3d2))

* fix(Beaker): traceback when hub is not accessible at session creation

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`18f6b78`](https://github.com/neoave/mrack/commit/18f6b7898130cf8c5c7e4c392b1d4ad72b15f1ba))

* fix(Beaker): connection to hub timing out

mrack was failing with an exception when
Beaker hub was not replying to requests for
some time. With this we accept the fact that
hub may not respond and we use previous
result and continue the wait for resource.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`9c258d8`](https://github.com/neoave/mrack/commit/9c258d8bf4eea248e8220d0b697ea0126e24b23b))


## v1.9.0 (2022-10-12)

### Chore

* chore: Release version 1.9.0

Releasing mrack version 1.9.0 ([`c42e4e2`](https://github.com/neoave/mrack/commit/c42e4e2bae295799786600d5ca45c74b5a5f4515))

### Documentation

* docs: Update installation steps based on mrack package division

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`48b16f4`](https://github.com/neoave/mrack/commit/48b16f45acf96e9129507037e2fcac1a0abf0045))

### Feature

* feat: Split mrack spec to multiple packages

Splitting mrack to:
- mrack
- mrack-cli
- python3-mracklib
- python3-mrack-aws
- python3-mrack-beaker
- python3-mrack-openstack
- python3-mrack-podman
- python3-mrack-virt

where python3-mracklib contains only static provider and all the
scripts and provisioning base logic.
we can install mrack-{aws,beaker,openstack,podman,virt}
providers in addition to static provider extending
the functionality and create modular solution where only
needed providers can be installed.
Package mrack contains all supported providers.
Package mrack-cli contains mrack command.
We are using Suggests directives for OpenStack dependencies
so in fedora where these are not available build will pass.

Resolving: https://github.com/neoave/mrack/issues/113

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`1709af0`](https://github.com/neoave/mrack/commit/1709af06150c567f91e44584375bddf79b993807))


## v1.8.1 (2022-10-10)

### Chore

* chore: Release version 1.8.1

Releasing mrack version 1.8.1 ([`40cd839`](https://github.com/neoave/mrack/commit/40cd83945a04caa1517ddd56034c1065b861bd48))

### Fix

* fix: add missing split support for transformer

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`d22d360`](https://github.com/neoave/mrack/commit/d22d36071dc922e088ede8df63576988e2c8bd52))

### Refactor

* refactor: fix the typos in aws provider

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`957f8c5`](https://github.com/neoave/mrack/commit/957f8c57368009a49a7ada8d06913a0a87d91bd9))


## v1.8.0 (2022-10-10)

### Chore

* chore: Release version 1.8.0

Releasing mrack version 1.8.0 ([`aaa611d`](https://github.com/neoave/mrack/commit/aaa611d4dba0b92e6a4cebbc6991adb5424440af))

### Feature

* feat: Add support to dynamically load providers

Prepare dynamic loading of mrack providers
for future division of mrack package.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`607c99c`](https://github.com/neoave/mrack/commit/607c99c7cd6aef5fdf10dd4f634fe3c99543ff96))

### Fix

* fix: Use encoding when opening files in setup.py

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`3ef4b92`](https://github.com/neoave/mrack/commit/3ef4b92ac2751cbc2144e86bb12ae56da8833bae))


## v1.7.0 (2022-09-20)

### Chore

* chore: Release version 1.7.0

Releasing mrack version 1.7.0 ([`2e76b4f`](https://github.com/neoave/mrack/commit/2e76b4f606de6ae70cbf8f7acb2d43cb7c6e337a))

* chore: Add ksiddiqu as release actor

Added kaleem as release actor

Signed-off-by: ksiddiqu &lt;ksiddiqu@redhat.com&gt; ([`4852af9`](https://github.com/neoave/mrack/commit/4852af9bac02d206ea9ab9db8809b5828373866f))

### Feature

* feat(Beaker): Specify ks_append per host or config

Now we can specify ks_append per host and defaults
in the provisioning_config.yaml file where if nothing
is set defaults to empty ks_append.
Moves the allow ssh_key to transformer and leverage
ks_append to inject keys into Beaker instance.
Also changed: pubkey is not required anymore.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`59ba489`](https://github.com/neoave/mrack/commit/59ba489e70e7c83fc56d006ca0073d010dd4564f))

* feat(Beaker): support configurable jobxml specs

Moving the translation of requirement to specs
to the beaker transformer and support more options.
Now the beaker specific configurations
can be defined in provisioning config,
host&#39;s beaker section. If nothing is specified
sane defaults are configured.
Allow users to define more pubkeys to be injected
supported values are now string containing path
or a list of paths. This value can be set in
the provisioning config.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`e9b6fa7`](https://github.com/neoave/mrack/commit/e9b6fa7a1c7bd550953d5905f5fe262787559070))

* feat(Beaker): Support custom configurable ks_meta values

get the ks_meta from host configuration, global
provisioning config or default hardcoded in code.
The priority is following:
 - host
 - provisioning-config.yaml
 - default (if nothing set)
https://beaker-project.org/docs/user-guide/customizing-installation.html#kickstart-metadata-ks-meta

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`e167443`](https://github.com/neoave/mrack/commit/e16744346169ca375cea005c9e5989ff30bfc43b))

### Fix

* fix(Beaker): Do not throw an Exception when not authenticated

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`d1b794b`](https://github.com/neoave/mrack/commit/d1b794b9622b27a6c776e9699bb21bb7032db173))

* fix: issue when searching for value when dict_name == attr

When searching for value using find_value_in_config_hierarchy the method
might return the entire dictionary with name according to dict_name when
the search attribute name is the same as dict_name and the dict doesn&#39;t have
a default value nor value according to provided key.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`98255c7`](https://github.com/neoave/mrack/commit/98255c78ec52053c508170238951daff90f4f5c6))

* fix: Beaker log polling to logfile instead of console

Beaker was too chatty in console output so we moved
the messages to the debug level so it is logged in
the mrack.log only. Added debug message to the
function responsible for polling beaker for job status.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`be560d9`](https://github.com/neoave/mrack/commit/be560d9b59fae0f8d142e737db99d7077ee8cf92))

### Refactor

* refactor(beaker): move distro_tags and hostRequires to transformer

From provider as transformer is the component which should work with
provisioning config.

Also remove the mrack_beaker from specs as it is no longer needed.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`7a8bd24`](https://github.com/neoave/mrack/commit/7a8bd2497e5a952de92b89bb93d268ce852d4d24))

* refactor(Beaker): fix the typo in the comment message

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`aa938e3`](https://github.com/neoave/mrack/commit/aa938e37ca92836edd35cf52921e72a57e06cdf1))

### Test

* test(Beaker): check transformation for all supported reqs

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`64cfa3a`](https://github.com/neoave/mrack/commit/64cfa3ace7a528c675bfddc10c2aa00cce2cb749))

* test(Beaker): Do not use pubkey in mocked config

When pubkey is defined in provisioning_config.yaml
test fails with error reading the file.
This requeirement has been removed thus this pubkey
s no longer needed in mocked config.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`0617fdf`](https://github.com/neoave/mrack/commit/0617fdfac67ff84df2f3210493929466be053f29))

* test(Beaker): check the ks_meta translation

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`161a145`](https://github.com/neoave/mrack/commit/161a1450393197668c8c8deb3e25fa823a01789a))

* test(Beaker): Update beaker test to mock global context provisioning config

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`7a690a0`](https://github.com/neoave/mrack/commit/7a690a04a783b74a0216e29660f679b41dcb4759))


## v1.6.0 (2022-07-27)

### Chore

* chore: Release version 1.6.0

Releasing mrack version 1.6.0 ([`9c0b89b`](https://github.com/neoave/mrack/commit/9c0b89b6f647ff38472b32cdacb6a05fc8a8eb8a))

* chore: Use python 3.9 and new python-semantic-release

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`3d97bcc`](https://github.com/neoave/mrack/commit/3d97bcc68c84c166e401163170ef08d1cbfbe348))

### Feature

* feat(pytest-multihost): arbitrary attributes for hosts

Make it possible to add arbitrary attributes per-host via defining them
in pytest_multihost dictionary in host section of job metadata file.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`d0c28f6`](https://github.com/neoave/mrack/commit/d0c28f62dad1cb8cf99704973209102cc0deab2f))

* feat(ansible-inventory): host arbitrary attributes

Adding a possibility to add arbitrary attributes to host part of
generated Ansible inventory via defining them per-host in new dictonary
`ansible_inventory`.

This is useful for creating more complex jobs which are using ansible
playbooks or roles requiring to get vars from hosts.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`65057e7`](https://github.com/neoave/mrack/commit/65057e734db89531d10ee02ec8b763f25578b840))

* feat: copyign meta_ attributes from host to ansible inventory

Make it possible to define arbitratry attributes prefix with meta_
in host section of job metadata file.

All of these attributes are then copied to host part in ansible
inventory output.

It can serve for creation of playbooks which consumes these attributes.

Addtional, but probably rare use case, is to override the meta_ attrs
which are derived from other others by mrack.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`3da517c`](https://github.com/neoave/mrack/commit/3da517c18701999c43638a67835f09938272badc))

### Fix

* fix(pytest-multihost): crash when group is not defined

It should possible to define host groups either via &#34;group&#34; or &#34;groups&#34;
variable. But pytest-multihost output was crashing when it was done via
&#34;groups&#34;.

This fix makes it not to crash if both are missing. It also makes it
possible to use first group from &#34;groups&#34; if groups are defined -
similar as in Ansible inventory output.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`d337a7b`](https://github.com/neoave/mrack/commit/d337a7bbec98f9385fa7f86fb944e032b8b60878))

* fix(pytest-multihost): crash when mhcfg is missing in prov. config

`mhcfg` is not required key in provisinong config, but pytest-multihost
plugin crashes if it is missing. This fix makes it not crash.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`d6e3483`](https://github.com/neoave/mrack/commit/d6e3483f509fb6fe5b5c0759f0d51e0db9bd28b5))


## v1.5.0 (2022-07-08)

### Chore

* chore: Release version 1.5.0

Releasing mrack version 1.5.0 ([`7b7afe2`](https://github.com/neoave/mrack/commit/7b7afe2695d0f57222e0b6ffcf271a47f7b4f1ed))

### Feature

* feat(AWS): Create unique instance name with the tag

Create unique instance Hostname tag which is used
or can be used by lambda functions on AWS to create
dynamic DNS records on the fly.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`b3e31e0`](https://github.com/neoave/mrack/commit/b3e31e0ab614c795ea34ef250e118ffa4905b536))


## v1.4.1 (2022-06-17)

### Chore

* chore: Release version 1.4.1

Releasing mrack version 1.4.1 ([`a0ad3fe`](https://github.com/neoave/mrack/commit/a0ad3fe8995aead942e03568fa7f6d4a26b943ef))

### Fix

* fix: Creating inventory with None host

The code in create_invetory method was looping hostnames from the DB,
which some of them may have already been deleted, which cause a None return
when trying to get their metadata.

This fixes traceback caused by rerunning mrack up with a different host name
without previously deleting mrackdb.json

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`7489240`](https://github.com/neoave/mrack/commit/748924088ab0416d8ff1d9381cb5da5f262a2af9))


## v1.4.0 (2022-05-05)

### Chore

* chore: Release version 1.4.0

Releasing mrack version 1.4.0 ([`6dfe04f`](https://github.com/neoave/mrack/commit/6dfe04f33507815328717876253faf1c42f46236))

### Feature

* feat(AWS): Move tagging into creation request itself

When the creation of the instance is too slow
on the ec2 side we get a traceback that instance
does not exist (yet) and we need would need
to wait a bit in order to tag it.
Move tagging into request itself and do it at instance creation

resolves: https://github.com/neoave/mrack/issues/173

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`b4fae6b`](https://github.com/neoave/mrack/commit/b4fae6bceabfeffa2fe47efae5a3ee87aba6da74))

### Fix

* fix(AWS): return False when ValidationError is raised

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`bb5594b`](https://github.com/neoave/mrack/commit/bb5594b4028bc06e71f5167615acbb9ac3cd7e32))

### Refactor

* refactor: remove collon from error string

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`cedefcb`](https://github.com/neoave/mrack/commit/cedefcbdf8385f2e31d8078328776230b747d3e3))


## v1.3.1 (2022-04-05)

### Chore

* chore: Release version 1.3.1

Releasing mrack version 1.3.1 ([`81a70e7`](https://github.com/neoave/mrack/commit/81a70e75889bccda2272db6a56c3f9035aaaf2bb))

### Documentation

* docs: Update the _get_image() method doc string

when the image is not found in the provisioning
config mapping the _get_image() method defaults
to the host[&#39;os&#39;] value from the input metadata

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`6b88058`](https://github.com/neoave/mrack/commit/6b8805880e2e9bfcb26dca4d9628254e4ad896cf))

### Fix

* fix: image transformer none value in requirements

When OS image in metadata is not found in provisioning
config, there was a traceback causing mrack to fail.
Adding default value solves the problem and prints expected message.

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`cb5290d`](https://github.com/neoave/mrack/commit/cb5290d7c4864dccf94c9c126487e9436fea8682))

### Refactor

* refactor: print used image msg just once

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`9fd3616`](https://github.com/neoave/mrack/commit/9fd36165562aeb03c033c15298f34421835187c5))

### Style

* style: Increase readability of logs by using host

Adding a host name from metadata or host object
where it is possible to increase readability of
the log messages and better debugging with only
using the log content. Before this patch there
were logging messages that were describing the
error but from the log message we could not tell
which host was causing that.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`f31b4ef`](https://github.com/neoave/mrack/commit/f31b4ef1f1f847c3e95567ec012323be65a1e177))


## v1.3.0 (2022-04-01)

### Chore

* chore: Release version 1.3.0

Releasing mrack version 1.3.0 ([`75ce9e6`](https://github.com/neoave/mrack/commit/75ce9e6d18adbc56a6ed6314650afe068ec55638))

* chore: Add asyncio-mode=strict to pytest.ini

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`851dfb8`](https://github.com/neoave/mrack/commit/851dfb8f128907365775f8f7ba94d37dbe77ec75))

* chore: Add dav-pascual release actor

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`7494eea`](https://github.com/neoave/mrack/commit/7494eea7d74217fecdc5cfb3670b95b6ba0ce78d))

* chore: Update Black pre-commit hook version to 22.3.0 to fix issue

Recent release of Click makes current version of Black to break in the pre-commit stage. This issue is solved in newest version of Black 22.3.0
See more about the issue in https://github.com/psf/black/issues/2964

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`b5c6d41`](https://github.com/neoave/mrack/commit/b5c6d41666da31057e875cd568ab915928b90006))

### Documentation

* docs(aws): add missing examples to provisioning config

And config examples for features implemented recently for the aws
provider.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`e00e149`](https://github.com/neoave/mrack/commit/e00e1499364fef1b60a81417d485250817108991))

### Feature

* feat(Beaker): Support distro variant configuration

Before this patch the distro variant could not be configured
and was hardcoded in the source code of the mrack project.
With this patch we support the old way and also a new way
of specifying the distro variants in the provisioning-config.

Updated the example provisioning-config.yaml file with latest
beaker feature examples.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`e568507`](https://github.com/neoave/mrack/commit/e568507ec233fe232109717c68abb4a86b14948d))

* feat(Openstack): printout compose_id when using -latest image pointer

In order to know what image is the latest tag pointing to in Openstack,
meta_compose_id and meta_compose_url fields from image meta information are
printed out in the log and added to ansible inventory output.

Implemented in a way that allows extension for other providers with extra custom fields,
or images that don&#39;t have those fields at all.q

Signed-off-by: David Pascual &lt;davherna@redhat.com&gt; ([`bb91893`](https://github.com/neoave/mrack/commit/bb918931d76b2cb031094398eb5e6970f2ef42ad))

* feat(aws): delete volumes on termination

The behavior is default it can be disabled by setting:
```
  delete_volume_on_termination: false
```

In a config hierarchy of AWS provider.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`d90375e`](https://github.com/neoave/mrack/commit/d90375ebf571efb4f3b3d6cbf34dc741910fa95a))

* feat: possibility to disable host DNS resolution in outputs

Ansible inventory&#39;s `ansible_host` or pytest-multihost&#39;s
`external_hostname` currently by default tries to resolve host&#39;s IP
address and use the DNS name if resolution is successfull.

This change allows to disable this behavior by setting:
  resolve_host: False
Somewhere in the configuration hierarchy (metatadat host, provider
config, or global provisioning config).

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`3fbd133`](https://github.com/neoave/mrack/commit/3fbd133e14f7397ccf261edaf05470664681fc0a))

* feat(aws): request spot instances

Spot instances are a great way how to save money for CI purposes.

https://aws.amazon.com/ec2/spot

This is inital implementation where the only possible option is to
ask for spot instance, but not define SpotOptions - this can be
extended later if wanted.

How to use:
- set `spot: True` in `aws` provider to enable it globally
- set `spot: True` in host section in job metadata file to request
  a spot instance for this particular host.

Additional changes:
- removes stopping instance on destroy as it doesn&#39;t work with
  default behaviour of spot instances + correctly handle exception when
  stopping fails (previous behaviour crashed mrack)
- prepares a parameters dict to be able to control what is passed to
  ec2.create_instances, + partly fixes a possible regression with
  SubNetId

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`25576cb`](https://github.com/neoave/mrack/commit/25576cbb9be0e8e258e8e5fc7209acd17a7e641d))

* feat(aws): defining AMIs by tags

Add a new way to define an AWS EC2 image in a provisiong config in
addition to ami ID.

The following is valid:

```
images:
  fedora-34: ami-0d3c5199abb29a7ae
  fedora-35: { tag: { name: compose, value: mrack-fedora-35-latest } }
```

This allows for a seperate tool to upload new image with the same
purpose and mrack automatically picks the latest one with the given
tag.

Currently only one tag is supported and it search in all images.

Possible improvements:
- more tags
- limiting to private images

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`a04497c`](https://github.com/neoave/mrack/commit/a04497c6003445241d96b19218a775a106db7da5))

### Fix

* fix: use host[&#39;os&#39;] as default value when distro is not found

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`253a380`](https://github.com/neoave/mrack/commit/253a3809887b1024b0ee09c1bc47a40869f35e8c))

* fix(Virt): remove password when provisioning windows

testcloud is capable to inject password to linux
instances but not to windows one when provisioning
thus remove the password from the result when
the instance is identified as windows host.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`e3a976a`](https://github.com/neoave/mrack/commit/e3a976a75a6e13659277936c690a5abec1ae6faa))

### Refactor

* refactor: use hierarchy search for images and distros

It may change some behavior a little but is mostly a refactoring.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`c3a91ad`](https://github.com/neoave/mrack/commit/c3a91ad9c36113ad14d4ebbab8985616a0a1359c))

### Test

* test: Add test for legacy beaker variant transformer

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`c486941`](https://github.com/neoave/mrack/commit/c486941325e56fdb0dbd68eba332ce0d01132515))

* test: Add BeakerTransformer unit test for distro and variant

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`ce5ed46`](https://github.com/neoave/mrack/commit/ce5ed4615f2417a27f46efae6f1616b47d1cafa2))

* test: Update the mock_data for Beaker unit tests

Update the mock provisioning config data
and create new MockedBeakerTransformer

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`07acc21`](https://github.com/neoave/mrack/commit/07acc21f0b47ce4316207c04be1083401ac2d200))


## v1.2.0 (2021-12-15)

### Chore

* chore: Release version 1.2.0

Releasing mrack version 1.2.0 ([`bc658b7`](https://github.com/neoave/mrack/commit/bc658b75e429cebcee09c1a3fb41b0fd2b03bfbf))

### Feature

* feat(aws): support for PrivateIpAddress

When instance is provisioned with VPC which does not have a public
IP address, mrack is not able to get IP and fails. So changing the
behavior to try also Private IP if Public is not present.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`8b7ed70`](https://github.com/neoave/mrack/commit/8b7ed705a58d533b7c5a2115b595d4e4e3e8c2e4))

* feat(aws): subnet support

Adding possibility to define subnet to use for the instances. This
is needed, e.g. when instance needs to use a non-default VPC.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`01c6bf5`](https://github.com/neoave/mrack/commit/01c6bf5a315ce4df73952086645911781516117d))

* feat(aws): multiple security groups

Add support to be able to use multiple security groups and thus be able
to fine tune the inbount and outbound commnucation rules.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`1340813`](https://github.com/neoave/mrack/commit/13408133310b80a4163aef21825ebaa861d9d0dc))

* feat(Openstack): poll openstack load when running can_provision()

Can provision method was using only preloaded limits which caused
provisioning to fail always when resources at begining of the run
were already full. Now we reload limits with every can_provision()
method call and make sure load is refreshed and provisioning continues

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`8ef8312`](https://github.com/neoave/mrack/commit/8ef831297a99c47eb270a6ea4f5e33ed20c8caee))

* feat: search also provider config for username

Cloud images might have a different default user based on privider, e.g.
RHEL has ec2-user but OpenStack image has cloud-user. This allows to
define default user per OS in provider section of provisioning config.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`8419698`](https://github.com/neoave/mrack/commit/84196984b85f7743cab3d148827d8417cefef11f))

* feat: find_value_in_config_hierarchy utility method

For getting a configuration value from the most specific to the
least specific. Design in a way to be usable for multiple of attributes.

E.g. first looking in host object then host definition in metadata then
in provider configuration and then in global provisioning configuration.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`c05ab58`](https://github.com/neoave/mrack/commit/c05ab586ea61cb55b5ff211a7486be0c3ae74761))

### Fix

* fix: SSH action - do not redirect to PIPEs

SSH action was previously redirected to PIPEs and thus it stopped
working from a user perspective as nothing was visible.

This patch is bringing the original behavior back.

Regression was caused by commit: 19d513ba246ef4be02a0ce3d22fbb0faea971ce8

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`8992629`](https://github.com/neoave/mrack/commit/89926294b663c43edddea4a7c92503e407c92447))

* fix: prepare_provisioning now shall return bool value

Based on latest changes method prepare_provisioning
should return boolean value which means succes/fail
ref: a0de8475659153fd3fb39133a34f56729d0e561c

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`7e47c6f`](https://github.com/neoave/mrack/commit/7e47c6fd18015826575b8a844d95086502022e98))

* fix(Virt): Handle traceback when image is not accessible

When image for Virt provider is not accessible we
happen to raise an exception:
TypeError: &#39;TestcloudImageError&#39; object is not iterable
This should fix above exception and also tune behavior
when preparation of resources is failing.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`a0de847`](https://github.com/neoave/mrack/commit/a0de8475659153fd3fb39133a34f56729d0e561c))


## v1.1.1 (2021-11-25)

### Chore

* chore: Release version 1.1.1

Releasing mrack version 1.1.1 ([`65e95ea`](https://github.com/neoave/mrack/commit/65e95eabd2e2bc00bbcb4bcb3679a3f963f14ff9))

### Fix

* fix: add domain name for fqdn if host has short name

Append the meta_domain[&#34;name&#34;] to the hostname
of the resource where name is not fqdn to get one

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`a870f7f`](https://github.com/neoave/mrack/commit/a870f7f0fbe5117d08ffda6f789b09ab53018ece))


## v1.1.0 (2021-11-23)

### Chore

* chore: Release version 1.1.0

Releasing mrack version 1.1.0 ([`dada7e3`](https://github.com/neoave/mrack/commit/dada7e391107e716a31ec26c09923b61117bb6e2))

### Documentation

* docs: Add post-provisioning ssh check docs

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`ef0e339`](https://github.com/neoave/mrack/commit/ef0e339d25eb735d3825493e815376cd5c6f106b))

* docs: fix toctree for guides

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`d9075f9`](https://github.com/neoave/mrack/commit/d9075f91304d1d31491bb37e8cde0a671597b230))

### Feature

* feat: add shortname in Ansible inventory output

It is added in meta_hostname attribute as often shortnames are
referred as hostnames.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`ea76cbc`](https://github.com/neoave/mrack/commit/ea76cbc07750ffb3e324919a4089bbba88470121))

* feat: Add group specific ssh config possibility

With that feature we added group to host object
provisioning config section can be extended:
post_provisioning_check:
    ssh:
	...
        group:
            ipaclient:
                timeout: 309090 # minutes
        ...

This is an extension to post_provisioning_check feature
Now we pass on whole req dictionary as part of
server response with key: mrack_req.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`f0e32d8`](https://github.com/neoave/mrack/commit/f0e32d8aab1e22126b3d5e1b3b82afb0082a5ad6))

* feat: Make post provisioning ssh check configurable

Using post_provisioning_check with ssh default section
in the provisioning config to configure check based on
values in the dictionary:

post_provisioning_check:
    ssh:
        # Default configurations for every host
        enabled: True # True | False
        disabled_providers: [&#34;podman&#34;] # Per provider override to `enabled: True`
        enabled_providers: [] # Would be relevant if &#39;enabled&#39; is &#39;False&#39;
        # port: 22
        # timeout: 10 # minutes

        # Overrides

        # If we want to override based on OS
        os:
            win-2012r2:
                timeout: 15 # minutes
            win-2016:
                timeout: 15 # minutes
            win-2019:
                timeout: 15 # minutes
            fedora-34:
                enabled: False
                timeout: 1
                enabled_providers: [&#34;static&#34;]
                disabled_providers: [&#34;beaker&#34;]

Priority OS &gt; Default

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`c419dc2`](https://github.com/neoave/mrack/commit/c419dc29fdc98ce8aef1dcc13f5ca40f511375a9))

* feat(Beaker): Add parsing of HostRequires to the job

mrack now supports the hostRequires in the host metadata
or default in provisioning config yaml.

NOTE: CASE MATTERS

The hostRequires for the host should look like following:
hostRequires:
  or:
    - hostname:
        _value: foo1.bar.baz.com
        _op: &#34;=&#34;
    - hostname:
        _value: foo2.bar.baz.com
        _op: &#34;=&#34;
  and:
    - system:
        memory:
          _value: 8000
          _op: &#34;&gt;&#34;
    - arch:
        _value: x86_64
        _op: &#34;=&#34;
    - system_type:
        _value: Machine
        _op: &#34;=&#34;
    - key_value:
        _key: HVM
        _value: 1
        _op: &#34;=&#34;
    - disk:
        size:
          _value: 137438953472
          _op: &#34;&gt;&#34;

Which will result into following xml for the job specification:

&lt;hostRequires&gt;
  &lt;or&gt;
    &lt;hostname value=&#34;foo1.bos.redhat.com&#34; op=&#34;=&#34;/&gt;
    &lt;hostname value=&#34;foo2.bos.redhat.com&#34; op=&#34;=&#34;/&gt;
  &lt;/or&gt;
  &lt;and&gt;
    &lt;system&gt;
      &lt;memory value=&#34;8000&#34; op=&#34;&amp;gt;&#34;/&gt;
    &lt;/system&gt;
    &lt;arch value=&#34;x86_64&#34; op=&#34;=&#34;/&gt;
    &lt;system_type value=&#34;Machine&#34; op=&#34;=&#34;/&gt;
    &lt;key_value key=&#34;HVM&#34; value=&#34;1&#34; op=&#34;=&#34;/&gt;
    &lt;disk&gt;
      &lt;size value=&#34;137438953472&#34; op=&#34;&amp;gt;&#34;/&gt;
    &lt;/disk&gt;
  &lt;/and&gt;
&lt;/hostRequires&gt;
and such requirement will be uploaded to the beaker hub
and schedule a job with this requirements.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`e696872`](https://github.com/neoave/mrack/commit/e69687234c26c518de159a082f4bfcb1df328860))

* feat(Podman): Add possibility to run post provisioning commands

Now there is a possibility to specify extra post provisioning
commands with using &#39;extra_commands&#39; section in podman config.
podman:
    extra_commands:
        - &#34;systemctl restart sshd&#34;
Fixed exeption raising where exception needs extra argument
for later usage - the self.dsp_name which is name of provider
caused troubles in provisioning.
Added error log for this message.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`ea488fc`](https://github.com/neoave/mrack/commit/ea488fc5e367b5d33e074585e48197e050c7d0fb))

### Fix

* fix(OpenStack): Do not raise exception when using unavailable network

In some cases when network has an outage or is temporarily
removed etc. mrack would raise an exception when getting
the &#34;id&#34; from network which is set to &#39;None&#39; which is
obvious AttributeError: &#39;NoneType&#39; object has no attribute &#39;get&#39;

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`6c31bb6`](https://github.com/neoave/mrack/commit/6c31bb6f24132051ba7be777a59ec7652cf28f67))

* fix(openstack): use shortnames for Windows vm names

Windows machines get hostname often by Cloudbase-Init. But
windows host support setting only shortnames (domain is added
when the host joins AD domain). OpenStack derives the hostnane
from vm name (until nova version 2.90 where hostname attr is added).
Thus we set shortname to support this also on older OpenStacks.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`d4a1bec`](https://github.com/neoave/mrack/commit/d4a1bec262041d101d555264382f852faf7190c1))

* fix(AWS): Fix provision of non-existing ami

Fixing provisioning error when ami is not available
anymore and boto is not able to tell from ami itself.

ref: https://github.com/boto/boto3/issues/2531

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`0971479`](https://github.com/neoave/mrack/commit/09714792de24877fe1fa59e8d51fbfd01a7c75ec))

* fix(Beaker): Change host status to error when task did not pass

Update slightly format of error message

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`90cd628`](https://github.com/neoave/mrack/commit/90cd6281aba071fe80705dc89adb0dcc721b40d9))

* fix(Podman): Fix the exception handling when container creation is failing

Fixed exception raising for podman subprocess which was causing troubles
when catching an exception and using arguments from the raise.

Fixed use case when container failed to create and there was
no container id to delete.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`6df9605`](https://github.com/neoave/mrack/commit/6df9605c05a1a59bc09715e53edf97126bdb78e0))

* fix(Podman): raise an exception when image failed to pull

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`ed79732`](https://github.com/neoave/mrack/commit/ed79732a12b47e28d3228e14cf0ea725e80360df))

### Refactor

* refactor: use builtin operator to merge dictionary

mhcfg section from provisioning-config is default
and could be extended by user provided mhcfg section
from metadata, thus using this order for `|` operator

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`51f7ceb`](https://github.com/neoave/mrack/commit/51f7ceb84c8acc6283b6e9c94a522522ebcf4b7e))

* refactor: pass req to to_host method

Or in other words, do not loose it/return it from
wait_till_provisioned method.

That way a provider can loose all info about req
- even the host name and to_host will still have this
info accessible.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`f065255`](https://github.com/neoave/mrack/commit/f065255b0e04d0879a4383ff6d9caf8219806cef))

* refactor: Return requirement with server result

Returns server requirements alongside with
provisioning results to be later used.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`cd275e4`](https://github.com/neoave/mrack/commit/cd275e4927883af42b2716696b38ddaf1bb0c3cf))


## v1.0.0 (2021-09-03)

### Breaking

* docs: Add docs about usage mrack as lib

Update README.md to help people use mrack as library
to easily include our code to their automation or scripts.
Add docs/guides/mrack_lib.rst with the content same as
in the README.md

BREAKING CHANGE: Release 1.0.0 candidate

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`2df06d7`](https://github.com/neoave/mrack/commit/2df06d7cdc0b9ce008bc40ad25708adb24564a68))

* feat: Use GlobalContext class in runtime

mrack now uses the GlobalContext object to store
the information for every particular run.
This object is defined in the context.py
And should be initialized for the run.

BREAKING CHANGE: Using GlobalContext class in runtime
allows us to use mrack actions without parameters
Up/Destroy/... which simplify the workflow in scripts
so mrack can be used as library in python automation.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`2c23c97`](https://github.com/neoave/mrack/commit/2c23c9714900e727f845c99ef675b7a8a9ac0147))

### Chore

* chore: Release version 1.0.0

Releasing mrack version 1.0.0 ([`e49d492`](https://github.com/neoave/mrack/commit/e49d492f572570d7a51d673cbf61e657d9ff293f))

* chore: update tests to use latest GlobalContext class changes

Tests needed to be alligned to the usage of GlobalContext
class to catch difference between class init and calling
methods.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`1a8eb88`](https://github.com/neoave/mrack/commit/1a8eb88ef206e3aa4088f0d0d16ddfdfb6ef8603))

### Documentation

* docs: fix title underline too short

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`225cff4`](https://github.com/neoave/mrack/commit/225cff4d0c4c4d745844ef8b591f99628f6d82bc))

* docs: Add documentation to strategy switch

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`5cd1a8a`](https://github.com/neoave/mrack/commit/5cd1a8a6e83a5eb8cef04ac8d88108c533a66f28))

### Feature

* feat: Use global context instead of dictionary as ctx for click

replace ctx object with global context class and use
the class for click context.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`9f38a3c`](https://github.com/neoave/mrack/commit/9f38a3c77cf3874326866247d40ff696a5c24a4b))

* feat: log message when job is not changing state

log message when beaker job is not changing state
and increase poll time so we poll baker hub less

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`9e50f46`](https://github.com/neoave/mrack/commit/9e50f468fd58912a76ec6b19312f87f5c9f46252))

* feat: improve logging for openstack and ssh subprocess

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`7594732`](https://github.com/neoave/mrack/commit/7594732cbbf46c5cc2e4ef07c3fee35c02ee5081))

* feat: do not destroy if there are not success hosts

renaming variable destroy to failed_providers
to reflect what this variable really is.
if there are no success hosts do not run
branch with cleanup.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`84dce71`](https://github.com/neoave/mrack/commit/84dce715bb181adfb5bdc2d285e73c837b18172e))

* feat(Virt): support testcloud v0.6.0 and later

testcloud 0.6.1 now changes the invocation command
add support to use testcloud ssh_path option.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`6403bd6`](https://github.com/neoave/mrack/commit/6403bd64b63a52e187d447ec702e9e6253ef02c8))

* feat(Virt): log the tracebacks for Virt provider

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`d508aff`](https://github.com/neoave/mrack/commit/d508aff342fbbfceb4334e2068ab092d6fe6662d))

* feat: Use max_retry across providers to define retry count

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`d8caab5`](https://github.com/neoave/mrack/commit/d8caab5fa96cb74410193c8c1cc7e927d776c9a9))

* feat(Beaker): use timeout instead of number of retries

using number of retries is being replaced by timeout
to help users to redefine easily using provisioning config
timeout variable should be more user friendly

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`00330ef`](https://github.com/neoave/mrack/commit/00330efa500d1c2d2de796004bde04709ac2ac92))

* feat: add possibility to change strategy per provider in provisioning config

change default openstack behavior to abort

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`ee8cb36`](https://github.com/neoave/mrack/commit/ee8cb36e5e6c0ecd9e3885676d3b16a91f2be140))

### Fix

* fix(AWS): Catch traceback when credentials are missing

When we are missing export for AWS_CONFIG_FILE=...
boto throws an exception which we need to catch and
notify user nice way.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`1dc975e`](https://github.com/neoave/mrack/commit/1dc975e027039d46c8a36e6b7d6f2cd70f9d0340))

* fix(Podman): handle premature deletion

Podman now handles premature deletion and
we fixed missing max_retry arg in init()

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`0353d89`](https://github.com/neoave/mrack/commit/0353d895c83699e6f07af12416b29195d2059a5d))

* fix(Beaker): delete_host handle premature deletion

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`c57ff28`](https://github.com/neoave/mrack/commit/c57ff287ed506d9c4b353f7439230cc4dbdc0b54))

* fix(Virt): Create more readable output and move to debug

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`04d4d4a`](https://github.com/neoave/mrack/commit/04d4d4a3e9ceb9583af980a69df94071e3f2c1eb))

* fix: do not end provisioning if there are no resources

Providers ended provisioning early by throwing an exception
ValidationError which caused mrack to end provisioning
even when retry strategy has been enabled.
Now we create error Host object to continue provisioning with.
Also fixed condition when we need to cleanup the
error hosts for the next retry of the provisioning.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`4cbdc50`](https://github.com/neoave/mrack/commit/4cbdc501085d5f5ae8f819f828a30bcea59d940e))

* fix(OpenStack): Add exception handling to init of provider

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`5ac9eaf`](https://github.com/neoave/mrack/commit/5ac9eafba2e368015a6bffd3d1d5f9e81a3e40aa))

* fix(Beaker): handle Fault exception when contacting hub

Beaker provider may fail with throwing an Fault exception
when contacting beaker hub while creating requests.
We parse this exception string and behave as we can not
provision by creating fault beaker host object.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`02cfd66`](https://github.com/neoave/mrack/commit/02cfd6652ba938df1b9239dd5b84d710867e5ec7))

* fix: attempts should be greater than max_retry

number of attempts should be greater than max_retry
and not greater or equal than max_retry because
other way first attempt to provision will be
considered as first retry and provisioning will end
after reaching count 1 without reprovisioning retry
this was causing retry strategy to abort after
1st attempt even when max_retry was set to 1.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`e29e92d`](https://github.com/neoave/mrack/commit/e29e92d78b6f9bdf7b0dd4fb79e0c98eb921954c))

* fix: add missing &#39;/&#39; to log message while deleting

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`65e4ad0`](https://github.com/neoave/mrack/commit/65e4ad094bcced6434c2e0510354238fc71d8b9c))

* fix: make static provider more verbose

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`9c6b217`](https://github.com/neoave/mrack/commit/9c6b21795b72bb4cf554ccd3929d41cae7dc2d54))

* fix: destroy active VMs after other providers fail

Fixing the use case with multi provider failed run.
In case of at least 2 providers in metadata and one
failing, successfully provisioned hosts were not
destroyed as part of freeing resources.
e.g.:
if:
- Beaker fails
- Openstack succeeds
then
- Beaker cancel jobs
- Openstack resources keeps hanging not destroyed.
Adding block of code to raise an exception when
other than ProvisioningError occurred.

Resolves: https://github.com/neoave/mrack/issues/129

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`7e58e5d`](https://github.com/neoave/mrack/commit/7e58e5d9622e5c714c1e5e6659ffee89680a9b05))

* fix: Add verbosity to virt and podman resource deletion

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`c7653fb`](https://github.com/neoave/mrack/commit/c7653fb22ed37142fb80573b77b24de8ec4f8501))

* fix(Beaker): beaker job link add missing &#39;/&#39; in url

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`4a33072`](https://github.com/neoave/mrack/commit/4a330725d1b6ab410a0610fd8662c0fa86af2f43))

* fix(Virt): Add de-sync state and fix error parsing.

added de-sync state into known states and update error
parsing to use Error: or ERROR: sring to split traceback
message and extract information about failure from it.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`5875883`](https://github.com/neoave/mrack/commit/5875883e89f85484cb3b48dc8bdfae8cc6f6b37c))

* fix: Do not remove error hosts when doing last retry

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`6201042`](https://github.com/neoave/mrack/commit/6201042d34e352ead8ce6369f43a5f8e8622f2b8))

* fix: fail without traceback when job times out

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`5aa156e`](https://github.com/neoave/mrack/commit/5aa156e44fe2a1589879d78ec8cac9a8d7cc5f2e))

* fix: use SPECS and ERROR_OBJ keys to create fault object

use SPECS and ERROR_OBJ keys to create fault object
later used to remove resources from the failed
provisioning and to use as many as possible
values which could help to destroy resources correctly.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`2de1f6f`](https://github.com/neoave/mrack/commit/2de1f6f350decff116f80b519ed4e53cd2b75aaa))

* fix: Unite providers&#39;s create server to return tuple

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`5f9ba63`](https://github.com/neoave/mrack/commit/5f9ba633ef1ddafa07105e6f8a0667f057a09786))

* fix: Do not proceed to ssh check if port is not open

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`ea94a8e`](https://github.com/neoave/mrack/commit/ea94a8e53dd56e306e0131404508476a0929fe67))

### Refactor

* refactor(OpenStack): do not use while true

use actual condition to check retry count
instead of true statement.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`afc896e`](https://github.com/neoave/mrack/commit/afc896e9aff117a88bf634ff0fb2bf8418d56a93))

* refactor(Beaker): Use hub url in messages

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`bf944cf`](https://github.com/neoave/mrack/commit/bf944cf7f141e75240985507eb98408cb750c430))

* refactor(Beaker): fix the typo in message

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`e7c3a6e`](https://github.com/neoave/mrack/commit/e7c3a6e5c5eccbf56fdf17e3c73f0cb2f8be2d59))

* refactor(static): remove method which is inherited

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`1a9436a`](https://github.com/neoave/mrack/commit/1a9436ac331c3f5f7420616215a0fe8c4522a943))


## v0.14.0 (2021-07-01)

### Chore

* chore: Release version 0.14.0

Releasing mrack version 0.14.0 ([`313cd88`](https://github.com/neoave/mrack/commit/313cd888b6b5778ef58a215227002281f07a1f05))

### Feature

* feat(Beaker): Add distro tag from provisioning conf

Add feature which enables adding distro tags specified
in the provisioning config in beaker section like:
```
beaker:
    distro_tags:
        FEDORA-34%:
            - NIGHTLY
```
This allows us to specify distros with custom tags.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`762e88a`](https://github.com/neoave/mrack/commit/762e88a00c79be2c1194a459a7404f2eb3513e19))


## v0.13.0 (2021-06-08)

### Chore

* chore: Release version 0.13.0

Releasing mrack version 0.13.0 ([`c2af397`](https://github.com/neoave/mrack/commit/c2af39735b3789b6bba07c5dd3a0687b258e3b88))

* chore: Add f-trivino as release actor

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`cd5b5d0`](https://github.com/neoave/mrack/commit/cd5b5d084f19117ded595811a55a6b8e62eaac16))

### Feature

* feat: Support size definition in metadata

Enable flavor translation based on size defined
in the metadata file. If the metadata does not
contain the size key for host entry flavor
will be based on host group.

This enables possibility to provision bigger/smaller
instances for specific usecases with keeping
group in place for each host so &#39;roles&#39; of VMs
in the automation remain as expected based on groups.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`b3923ba`](https://github.com/neoave/mrack/commit/b3923baf2b4969946a935536c2509dee349bc27f))

### Fix

* fix: use BaseOS as variant for RHEL9.0 in Beaker

Only BaseOS variant is available for RHEL9.0 in Beaker ([`9908257`](https://github.com/neoave/mrack/commit/9908257f01a417a22e36d3768502530b254c7a0b))


## v0.12.0 (2021-05-13)

### Chore

* chore: Release version 0.12.0

Releasing mrack version 0.12.0 ([`bfe6f46`](https://github.com/neoave/mrack/commit/bfe6f46dd7c78450b1eed89324a366cd016bf9f5))

* chore: Add libvirt-dev distro dep to GH action

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`687c6d9`](https://github.com/neoave/mrack/commit/687c6d9cc85fa724b54eabc26a73c785e1c465cf))

### Documentation

* docs: Update method docsting as it does not Validate hosts anymore

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`46e725c`](https://github.com/neoave/mrack/commit/46e725ca64223da5560948a144a5798f0e8499ed))

### Feature

* feat: gracefully destroy servers after traceback

This allows us to create dummy Host object based
on the ProvisioningError traceback arguments
where we added also requirement which may have
caused the provisioning to fail so the worflow
can continue and remove already provisioned
servers after reprovision / abort strategy is
done so resources that may not be freed
to openstack will be returned.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`ab22410`](https://github.com/neoave/mrack/commit/ab22410cf07785c2e430464a5e933807a6d785dc))

* feat: Wait for provider resources up to hour

Checking resources more than once should help
to provide better results when we are facing
the providers to be overocupied.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`b9612cf`](https://github.com/neoave/mrack/commit/b9612cfaa194fe99a691529b42c5549010a21e03))

* feat(OpenStack): Check openstack response for resources issue

OpenStack may be oversubscribed so even when we do not reach
our quota limit provisioning may fail due to lack of resources.
In such scenario (OpenStack run out of hosts to provision)
we check the response from server and act based on the fact
that OpenStack itself is being fully loaded and does not have
free resources to provide for our server.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`328e0c9`](https://github.com/neoave/mrack/commit/328e0c9262e9a577a11817975218259ddf1ebd91))

* feat(Virt): use generated run IDs for parallel jobs

It may be common use case to run on one host machine two mrack jobs
with job metadata files which share hostnames. This may result in
conflict in testcloud as it identifies the vms by provided name. So
this patch is generating a pseudo unique run ID which is used as a
prefix for testcloud vm names and thus making it whole unique and
conflict resilient.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`60292ea`](https://github.com/neoave/mrack/commit/60292eaca1ff2f83746718c2f6aa2fc25ab0cbdf))

* feat: password authentication in ssh_to_host

ssh_to_host had some code for password authentication but it never
worked so this is basically a new feature.

Password authentication is preferred over sshkey as sshkey is often
defined globally and preffering it would e.g. not work for virt
provider. It is assuming that if a host has a password set then
it should work.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`dd151b5`](https://github.com/neoave/mrack/commit/dd151b524eac0eaecf9faf35d81073a0724f9d1e))

* feat: Virt a local virtual machine provider

PoC implementation which uses testcloud library to do most of the
heavy lifting. The idea is to use cloud images for local provisioning.

First implementation doesn&#39;t do much about image sources and expects
urls of images to be in provisioning config. Later this should be
improved to allow dynamic loading of latest images from the sources
without a need to change them often manually.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`b2f917e`](https://github.com/neoave/mrack/commit/b2f917e3a17802ac238508e2326d0b262f02f6fd))

* feat(OpenStack): move network translation to provider

Moving network translation to provider will help us
to find new network for openstack VM when there
is a problem with network pools (insufficient ips)
that will help to choose another pool within openstack.

Transformer now only informs about network type
provider picks the network at every provision retry.
Touches little bit commit:
b28acca76cd095a5c70e8417ffe9321b8aa671c0
To reword log message and provide more detailed
information about availability of ip addresses.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`5d5146b`](https://github.com/neoave/mrack/commit/5d5146b098c268bed8fe277c1cba30dd0a514317))

* feat: Add capability to disable ssh check

Disable/Enable the ssh check after provisioning with:
post_provisioning_ssh_check: False/True
in provisioning-config.yaml file.
Default: True

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`efc5061`](https://github.com/neoave/mrack/commit/efc5061c93f28510d56ca53d5be53b5f709e3ff8))

* feat(OpenStack): distribute choosing of networks

Currenlty Mrack always chooses a network with the most available IPs.

This is good for a lot of use cases but is problematic when a lot of
jobs are started at the same time. Each of the jobs is doing a
separate network availability check. This can lead to a situation
where almost all jobs pick the same and start provisioning with it.

But this network might not have enough IPs for everything so there
is a increased chance that it will fail. E.g if there is 300 available
IPs and we run 100 jobs which needs 3-4 machines.

Indroducing a new behavior where Mrack is picking a random network from
networks which have at least 50% of IPs as the bests one. Thus spreading
the load and lowering the chance of the issue to happening.

It will not solve the issue completely. This can be improved e.g.
in re-provision logic.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`b28acca`](https://github.com/neoave/mrack/commit/b28acca76cd095a5c70e8417ffe9321b8aa671c0))

### Fix

* fix: remove redundant host validation

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`baa2a06`](https://github.com/neoave/mrack/commit/baa2a06c27ece44302848a9f36fcd24681034e8f))

* fix: Change priority of hardcoding Administrator to Win hosts

Change the priority of hardcoded Administrator user
later used for Windows Hosts and let provisioning-config.yaml
be the firts one to lookup the username.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`3a5f19f`](https://github.com/neoave/mrack/commit/3a5f19ffc0b995814182bec335e002147fe670c2))

* fix: Do not add the config_drive_req to req

Do not add the config_drive_req to req when
the requirement is not needed to behave as older
mrack releases.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`db1f82a`](https://github.com/neoave/mrack/commit/db1f82ae6a108fc8da38961cb0efe6dafede8726))

### Refactor

* refactor: exec_async_subprocess helper method

Move code to execute subprocess asynchronously to a helper method
to be later used e.g. by a virt provider.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`57f7c21`](https://github.com/neoave/mrack/commit/57f7c21b907dde6db70ac47adc81e48a3cdb7b2a))

* refactor: Fix typo in log message

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`0380aae`](https://github.com/neoave/mrack/commit/0380aaebe3895d23d5eb7879251650f3f1a59894))


## v0.11.0 (2021-05-07)

### Chore

* chore: Release version 0.11.0

Releasing mrack version 0.11.0 ([`26c0370`](https://github.com/neoave/mrack/commit/26c0370637422ee39b436e89b510849638ecb87a))

* chore: Update GH workflows pre-commit version

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`3c6c158`](https://github.com/neoave/mrack/commit/3c6c158b3c79708cfa985ee4c7005585cd021f1a))

* chore: Accept code which has 10 or less lines similar

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`4c3bd5d`](https://github.com/neoave/mrack/commit/4c3bd5d8712785092b4e37c86fa9328153897f20))

### Feature

* feat: log mrack version into mrack.log

As debug. For knowing which version is used when investigation
failures.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`8ffa3c6`](https://github.com/neoave/mrack/commit/8ffa3c6610535c7fae8f4fa7d8d7a833bb200cab))

* feat: Add --version option to mrack cli

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`1863b79`](https://github.com/neoave/mrack/commit/1863b79c97ea00bc9277bba0fec1c78d7b42fbf8))

### Fix

* fix: decrease and insanely long timeout

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`2d8ed4e`](https://github.com/neoave/mrack/commit/2d8ed4ec115a9c2ac5ea2f904035b5042dbe570b))

### Refactor

* refactor: version module with version

To have only a single location (not counting docs) with version. It
has it&#39;s own module so that it can be easily imported anywhere else
later.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`cb3c1c0`](https://github.com/neoave/mrack/commit/cb3c1c0e61bdebaebb1d221ecdf935248328e508))


## v0.10.0 (2021-04-30)

### Chore

* chore: Release version 0.10.0

Releasing mrack version 0.10.0 ([`b695a9e`](https://github.com/neoave/mrack/commit/b695a9e7c3b190d77320a6cbcec4c7adf58f1828))

* chore: Add podman as requirement to specfile

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`4e68012`](https://github.com/neoave/mrack/commit/4e680128a40e23670478b47e8aa35d55151a6b37))

* chore: Add Bhavik Bhavsar as Release Actor

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`538fc7d`](https://github.com/neoave/mrack/commit/538fc7d3ac1dc3df5e7f7e01694b4756a9902a8f))

### Documentation

* docs: Add example provisioning config for podman

Adds an example config section for podman to provisioning-config.yaml
Adds an example seccomp.json file which might be used for containers
as a list of allowed syscalls for seccomp filter.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`f54b2e9`](https://github.com/neoave/mrack/commit/f54b2e96d24e91c57c161f1cf8c1f62cde1b7899))

* docs: Fix typo in docstring

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`255032b`](https://github.com/neoave/mrack/commit/255032b9ed38c083250cffae710f6330a543414e))

### Feature

* feat: Create podman networks in preparation

Create podman networks in provisioning preparation
to not block the provisioning or ty to create already
created networks which may cause unexpected errors.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`c6791ce`](https://github.com/neoave/mrack/commit/c6791cedc49148200761f3540778fe6a999110f5))

* feat: Pull podman images in preparation

Pull podman image in provisioning preparation
to not block the provisioning or pull one image
more than once which may cause unexpected errors.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`c19b230`](https://github.com/neoave/mrack/commit/c19b230da6c7fa01ef3200853aecd115ed2badc2))

* feat: check ssh connectivity outside of pares_error_hosts more than once

Move the ssh connectivity check outside of the
pares_error_hosts method to distinguish the functionality
and to be able to gather asynchronous results later.

Retry the ssh connection after if fails to not destroy
slower systems which may not have set up the proper
ssh key into allowed keys.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`ecd5470`](https://github.com/neoave/mrack/commit/ecd5470babfec8868263127d4b1cdf42b7bc52b6))

* feat: Use always root user for provisioned containers

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`311a8a5`](https://github.com/neoave/mrack/commit/311a8a576af821ccd2c49ef615a38521b1a7d67b))

* feat: Use more flexible way of defining podman names

NETWORK: Podman now use network name created by composing
default network from provisioning config and domain name.
PODS: name of the pod derives from the hostname and network
the pod is assigned to.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`a94d922`](https://github.com/neoave/mrack/commit/a94d922fc6aa83e65c538cb09edfd139487caf35))

* feat: Use ssh public key to access container instead of podman id

Use ssh to connect to container provisioned by mrack
instead of ansible connection to prevent some issues
with connection and built in ansible modules so
the container acts like a vm.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`87c1ff0`](https://github.com/neoave/mrack/commit/87c1ff04215d120f90d6e8785d7c2478da92ec13))

* feat: Add capability to use custom podman options

mrack now support advanced podman provisioning
to enable custom way of running pods with podman
we should add podman section to provisioning config
something like:
```
podman:
    images:
        # systemd enabled container images from: https://github.com/Tiboris/snappeas
        fedora-32: tdudlak/snappeas:fedora-32
        fedora-33: tdudlak/snappeas:fedora-33
        fedora-rawhide: tdudlak/snappeas:fedora-rawhide

    pubkey: config/id_rsa.pub

    default_network: mrack-network

    podman_options:
        # Mount a temporary filesystems (tmpfs) into a container
        &#34;--tmpfs&#34;:
            - &#34;/tmp&#34;
        # Use /sys/fs/cgroup in container as read only volume
        &#34;-v&#34;:
            - &#34;/sys/fs/cgroup:/sys/fs/cgroup:ro&#34;
        # Adding ipv6 support to network
        &#34;--network&#34;: &#34;enable_ipv6=true&#34;
```

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`d05a41f`](https://github.com/neoave/mrack/commit/d05a41f542861ff404113af68de52041779f0d72))

### Fix

* fix: The type of duration is not correct

TypeError: unsupported format string passed to datetime.timedelta.__format__
Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`dbdc25c`](https://github.com/neoave/mrack/commit/dbdc25ceae5a5e7985d1ece7eb253f0729b560fa))

* fix: ssh action crashes as it misses global_context

utils.ssh_to_host requires to have global_context initialized but
with introduction of it ssh action was not ammended. Without it
mrack crashed on sshing to a host.

This fix is initializing utils.global_context in ssh_action and
thus fixing the issue.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`a210f6e`](https://github.com/neoave/mrack/commit/a210f6eef895441198706b44697f7c3638630e94))

* fix: Log error when ssh fails after provisioning

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`76af86e`](https://github.com/neoave/mrack/commit/76af86ebe85a1ba500c89fed48fb3bf55cc692bd))

* fix: Do not use compression when trying ssh to machine

The `-C` flag causes the ssh to request compressed data
which may slow down the response time as manual says.
Rename execute to command so it is more clear
what is going to be happened on remote system.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`26d89be`](https://github.com/neoave/mrack/commit/26d89be9e643d7a9b8ea0ca929331b77af165bf9))

* fix: mrack ssh action needs host.host_id for podman

fix the traceback for accessing bad value in host
and fix the traceback when shell has been terminated
by using ctrl+D in terminal (signal 2)

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`c4daabd`](https://github.com/neoave/mrack/commit/c4daabda53bcace5a5d69dbe6e24f9fd62991bf2))

* fix: Use pubkey instead of keypair for beaker

Use pubkey name instead of keypair for beaker
to truly match the meaning of the value expected
to be set in provisioning-config.yaml

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`abc2a84`](https://github.com/neoave/mrack/commit/abc2a843c872a04a32908c931e5302def9879ca0))

* fix: Podman provider logger does not use Podman prefix

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`ef7dd59`](https://github.com/neoave/mrack/commit/ef7dd598d4ba9b86b5ba2037acaf06190e88289e))


## v0.9.0 (2021-04-19)

### Chore

* chore: Release version 0.9.0

Releasing mrack version 0.9.0 ([`539cb1c`](https://github.com/neoave/mrack/commit/539cb1c8b107344c2e34ef661fc9b5cea622e0a8))

### Feature

* feat: Enable config drive in OpenStack

By default Nova&#39;s metadata informatation if retrieved via HTTP, setting
`enable_config_drive` to True in provisioning-config will make metadata
available via a config drive, a special drive that are attached to an
instance when it boots.

This is helpful when connection is not stable during host booting stage,
host would be unreachable because cloud-init is failing to injecting
SSH keys into it.

This reduces the chance of hosts being provisioned but not accessible.

Signed-off-by: Armando Neto &lt;abiagion@redhat.com&gt; ([`3cdb54b`](https://github.com/neoave/mrack/commit/3cdb54b0ce64c97fb884c9d83ba46576fa8bbae7))


## v0.8.0 (2021-04-15)

### Chore

* chore: Release version 0.8.0

Releasing mrack version 0.8.0 ([`b029e2e`](https://github.com/neoave/mrack/commit/b029e2e489c49d26d29f631bbea59c6a3d8199a8))

* chore: Update pylint in pre-commit hook

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`8ba8dc3`](https://github.com/neoave/mrack/commit/8ba8dc347181c609d0a9f9be7d2e8b267bc7be4b))

* chore: Trigger COPR to build rpm

Add action step to trigger COPR after a new release is created.

Signed-off-by: Armando Neto &lt;abiagion@redhat.com&gt; ([`4e7ef91`](https://github.com/neoave/mrack/commit/4e7ef9186017f0d245317e50cabd4bdc91b967c9))

### Documentation

* docs: Add info on how to install on Fedora

Packages available as rpm for Fedora 32+

Signed-off-by: Armando Neto &lt;abiagion@redhat.com&gt; ([`90a52bc`](https://github.com/neoave/mrack/commit/90a52bc2661598da698f40c0a1cd5e730ec65bed))

### Feature

* feat: use ssh to check VM availability after provisioning

After a host in provisioned we do check ssh connectivity
to the host itself and claim it is ready only after ssh
connection is successful. If ssh connection fails we
mark this host as an error host delete it and try to
go with reprovision strategy.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`7af47ec`](https://github.com/neoave/mrack/commit/7af47ec4a161c6b6e7f521d06ea3a23ca859ed51))


## v0.7.1 (2021-03-23)

### Chore

* chore: Release version 0.7.1

Releasing mrack version 0.7.1 ([`cc4f130`](https://github.com/neoave/mrack/commit/cc4f1307df7dbfe3bfd97e8b347b22d56282ae71))

### Documentation

* docs: Add copr build badge and fix some typos

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`f85e236`](https://github.com/neoave/mrack/commit/f85e2366ee3fb5f952a03291bd4768099f298d23))

### Fix

* fix: Update project homepage

Fix URL used by Python Package Index.

Signed-off-by: Armando Neto &lt;abiagion@redhat.com&gt;
Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`1a1a0c2`](https://github.com/neoave/mrack/commit/1a1a0c2082ede76c74a14ccee0a7e364a2cc0a5d))


## v0.7.0 (2021-03-22)

### Chore

* chore: Release version 0.7.0

Releasing mrack version 0.7.0 ([`ad19af0`](https://github.com/neoave/mrack/commit/ad19af042378072a8463851f2364afcb11645cb2))

* chore: Update release action to update specfile changelog

Test &amp; Release action now updates also specfile
using GH secrets with corresponding actor name
and e-mail address to be used in spec&#39;s changelog.
Update action names to be more human friendly
Use latest python-semantic-release version.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`f72b329`](https://github.com/neoave/mrack/commit/f72b32900f9b2d6b05eb4ad88178127e6e581473))

* chore: change boto&#39;s minimum version required

Replace exact versions of boto3 and boto-core with &#34;greater than&#34; and
setting an older version because it&#39;s the latest available for Fedora
32.

It will install latest via pypi, pinned version is not a requirement
anymore because production conflicts with linchpin are not a problem
anymore.

Signed-off-by: Armando Neto &lt;abiagion@redhat.com&gt; ([`8eb56d3`](https://github.com/neoave/mrack/commit/8eb56d36b91d8713558f25eaafc1f6f15cb57306))

* chore: Add pylint to pre-commit-config.yaml

Use pylint in pre-commit-hook and actions as well
to check code for easy to overlook mistakes.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`8c8e99b`](https://github.com/neoave/mrack/commit/8c8e99b2cb299fd0d604bce24064173681624404))

### Feature

* feat: Add RPM spec file

Versioning automated via Github Actions.
Dependencies have no pinned version.

Signed-off-by: Armando Neto &lt;abiagion@redhat.com&gt; ([`17aebbb`](https://github.com/neoave/mrack/commit/17aebbbb41453cace25258695eef795320477869))

* feat: OpenStack: increase polling time based on number of hosts

Increase polling times so that Mrack doesn&#39;t poll very often to
not overload the server when a lot of hosts is provisioned.

Current setting should be approx:

hosts   init_wait   poll_time   After 10mins    After 15mins
    1       15.65        7.22          48.77           69.55
    3       16.95        7.66          46.82           66.41
    7       19.55        8.54          43.67           61.23
   10       21.50        9.20          41.81           58.11
   30       34.50       13.60          35.66           46.69
  100       80.00       29.00          39.34           44.52
  200      145.00       51.00          56.88           59.82

Where &#34;After 10/15mins&#34; is poll_time after the time, but it is not
a precise value (did not want to spend time on calculating it).

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`7558969`](https://github.com/neoave/mrack/commit/755896999e17b4b94336349ec98438a9bd532f3c))

### Fix

* fix: Handle ServerError in all Openstack calls

Handle 503 errors that can be returned by the nova client.

Signed-off-by: Armando Neto &lt;abiagion@redhat.com&gt; ([`585543a`](https://github.com/neoave/mrack/commit/585543a476debfbc9a2106e9fee2ed25014b7c82))

* fix: Handle timeout state and treat it as an error

When machine took too long to provision an exceeds
the timeout it stays in provisioning or other state
which does not fulfil the check for successful provisioning
We switch the logic and ask for the active state.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`a6b9738`](https://github.com/neoave/mrack/commit/a6b9738749d3392fae99d4d1b3df9e19fc118c89))

* fix: podman ansible inventory and status_map

Fixing ansible inventory generation for podman because db_host has no
attribute id.
Fixing AttributeError: &#39;PodmanProvider&#39; object has no attribute &#39;strategy&#39;.
Adding status map to podman

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`503a680`](https://github.com/neoave/mrack/commit/503a6802418bf8ac33cf08c0fd3468b13e7d5b74))

* fix: Fix pylint isssues and reuse existing methods

Fixing pylint iussues in project
Reusing existing methods in static and podman provider
for which pylint forced us to do some serious refactoring.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`788b2ff`](https://github.com/neoave/mrack/commit/788b2ff520f26a7e50601d8c450ad74c2c7a9feb))

* fix: If mrack is run first time db may not exist

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`bd51176`](https://github.com/neoave/mrack/commit/bd51176b025390e32d3012aec26c56e055771be0))

* fix: Require beaker version with support for python 3.9

Python 3.9 has removed the deprecated method &#39;encodestring&#39; from base64 module.
It needs to be replaced by &#39;encodebytes&#39;.
Beaker version 28.1 has the fix in place so require at least this
version.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`6f22bea`](https://github.com/neoave/mrack/commit/6f22bea70c963ad717b8c8ce53bb85f848b0be88))

* fix: OpenStack provider does not crash if no credentials are provided

If OpenStack RC file is not loaded, openstack provider failed with
unhandled TypeError exception which is thrown by asyncopenstackclient
AuthPassword.

This fix catches the exception and writes friendly error message.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`6115c1a`](https://github.com/neoave/mrack/commit/6115c1af4e8a8cb73624c7182259161e797910aa))

* fix: provider: await abort_and_delete

To fix:
```
Retrying to provision these hosts.
Max attempts(5) reached. Aborting.
$somepath/mrack/providers/provider.py:137: RuntimeWarning: coroutine &#39;Provider.abort_and_delete&#39; was never awaited
  self.abort_and_delete(hosts_to_delete, error_hosts)
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
```

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`8f361f5`](https://github.com/neoave/mrack/commit/8f361f5525bbfc9b3fba574825518dbc1ad3c2cd))

### Refactor

* refactor: Correct wait_till_provisioned method signature

To match parent class and to use only what is used.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`3fd3956`](https://github.com/neoave/mrack/commit/3fd3956a9d9e31668a9367a4646a3b9f8d22e5bf))


## v0.6.0 (2021-01-27)

### Feature

* feat: Podman support in SSH action

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`10a43f1`](https://github.com/neoave/mrack/commit/10a43f1bdaa328fad0a4fb2ad4ae57cd7ef41878))

* feat: Podman support in Ansible inventory

Now with only with &#34;podman&#34; connection support - no choice to SSH

Next step: make users configurable per-provider.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`f5dbed9`](https://github.com/neoave/mrack/commit/f5dbed9fc61ab474220fbc655246e1aafe03f73b))

* feat: Add Podman provider

- simple support to run rootless containers

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`ef35545`](https://github.com/neoave/mrack/commit/ef3554547eada23a65f0d40b7ecd9f51cb17eeeb))

### Fix

* fix: Handle ServerError in OpenStack provisioning

If OpenStack server returns e.g. error 503, provider code doesn&#39;t
handle it well and whole Mrack fails. This should catch it with
certain error tolerance/retry - e.g. if it was a fluke.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`46048c0`](https://github.com/neoave/mrack/commit/46048c01f6ae3224e9d49e711e610b28497f63df))

* fix: more verbose print about available networks

So that we can see more details in debugging.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`824b359`](https://github.com/neoave/mrack/commit/824b3594d152b061c36ade3f382b8908272030f9))

### Refactor

* refactor: Fix missing param in README.md file

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`96adff4`](https://github.com/neoave/mrack/commit/96adff43b16bf975046e7b116b19b2b34d5f3f25))

### Unknown

* 0.6.0

Automatically generated by python-semantic-release ([`237cfef`](https://github.com/neoave/mrack/commit/237cfef9fbccc3b1909099a06c9ae436b86328f6))


## v0.5.2 (2020-12-21)

### Chore

* chore: change pinned version from strict to range

While still a good practice to pin the versions of dependencies we found
some issues with conflicting dependencies.

This change tries to install greater than or equal to latest major
version (or minor if versio is 0.X).

It keeps the exact version (`==`) for boto3 and botocore because of a
known conflict in the production environment.

Signed-off-by: Armando Neto &lt;abiagion@redhat.com&gt; ([`f030229`](https://github.com/neoave/mrack/commit/f030229ef34a933f147b3516962db606c525e59d))

### Fix

* fix: mrack eh add no longer complains about coroutine &#39;eh&#39; not awaited

Turns:
```
$ mrack eh add
/usr/lib/python3.9/site-packages/click/core.py:1256: RuntimeWarning: coroutine &#39;eh&#39; was never awaited
  Command.invoke(self, ctx)
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
Adding hosts to /etc/hosts file
Done
```

Into:
```
$ mrack eh add
Adding hosts to /etc/hosts file
Done
```

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`7dbdd6a`](https://github.com/neoave/mrack/commit/7dbdd6a6f54331078907081527c944dd5899ab19))

* fix: Error for non authorized user reading image

There was an issue when reading image.name for image
for which user did not have proper read rights and
is not authorised to use it - ec2.Image() returned
None and resulted into Nonetype has no attribute name

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`a5c355d`](https://github.com/neoave/mrack/commit/a5c355da2a0b7d37e5865fb3a78558c26b163b3f))

* fix: mrack.conf &#39;~&#39; causes no such file or directory

When &#39;~&#39; is used in path for mrack.conf the later
operation open(&#39;~/.mrack/mrackdb.json&#39;, &#39;w&#39;) fails with an
exception FileNotFoundError:
[Errno 2] No such file or directory: &#39;~/.mrack/mrackdb.json&#39;
Use os.path.expanduser() to fix this

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`4b8dee8`](https://github.com/neoave/mrack/commit/4b8dee8d710a9a0d978561733dfcd898d96c2c67))

* fix: load possible missing image specified in metadata

When openstack image was not in provisioning config
it was not loaded to known images.
Now we try to load missing images and store to provider&#39;s
known images if they were specified in metadata but not
in provisioning-config.yaml

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`19103c0`](https://github.com/neoave/mrack/commit/19103c0a44311ba95409560877a48e0585795c01))

### Refactor

* refactor: remove overcomplicate things with join

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`f9a52cc`](https://github.com/neoave/mrack/commit/f9a52ccf5f22c0b64a25c8b5f30e6bb3e780de1a))

### Unknown

* 0.5.2

Automatically generated by python-semantic-release ([`6d62147`](https://github.com/neoave/mrack/commit/6d62147025fc6b0046783fbcabb1429025811afe))


## v0.5.1 (2020-12-14)

### Fix

* fix: Set user for Windows host in pytest-multihost config

Commit 7bb230e170ac0a2373a2316ef23a26bfcb681ad9 removed setting of
users as it did not work &#34;well&#34; for Linux host in our testing. But
it broke assumtion that Windows host have it set. So this is a fix
to be compatible with our previous mechanism.

I&#39;d call it a hotfix as it is needed but not great. It would be
better to have a more general mechanism with a degree of configuration
to make it adjustable for a project.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`e36138c`](https://github.com/neoave/mrack/commit/e36138c8f80e18eb235981ffd7eeb4840cac0855))

### Unknown

* 0.5.1

Automatically generated by python-semantic-release ([`42a4af7`](https://github.com/neoave/mrack/commit/42a4af759364a1c5c95139df1834c37bf8139963))


## v0.5.0 (2020-12-11)

### Feature

* feat: Retry provisioning strategy

Optional (currently aplied only for OpenStack) provisioning strategy
to retry provisioning of host which ended with error in a provisioning
attempt.

This is useful if environment gets into state where the provisioning
is a bit unstable but in general working. I.e. succeeds for some host
and fails for others.

The Retry strategy:
1. tries to provision all hosts
2. if some failed, delete them and retry only for these hosts
3. if they fail more than max_attempts time(default: 5), fail the job

Default strategy:
- do 1.
- if some failed, fail the job

In each job failure case:
- delete all hosts

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`3683d3c`](https://github.com/neoave/mrack/commit/3683d3c20f917f57de7f88d0b3e9e4fea5ff0398))

### Fix

* fix: openstack: log which server is being provisioned

To not see something more useful than:
&#34;&#34;&#34;
OpenStack: Creating server
OpenStack: Creating server
&#34;&#34;&#34;

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`d89aa5d`](https://github.com/neoave/mrack/commit/d89aa5d20192c75560f7bb0beffb3027b0431a47))

* fix: pytest-multihost: handle unresolvable IP into DNS

If host IP was not resolvable into DNS record, external_hostname was
null and thus pytest-multihost could not connect to the host.

This resolves the issue with using IP as a backup.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`56c716e`](https://github.com/neoave/mrack/commit/56c716ec910028604e2ecaf42124e7e1f6061324))

* fix: Fix making ssh_key_filename absolute for default behavior.

The logic was not working as the comment said. The cause was that
`mhcfg` already contained the value from provisioning config. So
we need to check the metadata to detect the situation.

Do the change also pro-actively for Ansible inventory output.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`6b5ea95`](https://github.com/neoave/mrack/commit/6b5ea951f132336fcde50b53a97c7b4338eb0099))

* fix: Remove double status translation in parse_errors

parse_errors works with Host objects which already have the normalized
status so usage of STATUS_MAP is incorrect.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`e5da9cd`](https://github.com/neoave/mrack/commit/e5da9cd6403d67f75d429b3207e11555dd90e437))

### Unknown

* 0.5.0

Automatically generated by python-semantic-release ([`211d24e`](https://github.com/neoave/mrack/commit/211d24e9865fa0e2ae468a09cb2ba8be370ae89a))


## v0.4.0 (2020-12-07)

### Chore

* chore: Add manual release action

In this action:
- pre-commit hook is run
- tox is run for a master
After these check succeedes:
- a new commit with changed version and changelog is pushed to master
- a new tag is added to the commit above with particular release version
- a new mrack package is being release to PyPi
  (prerequisite: secret with PYPI_TOKEN - already set)

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`01ea068`](https://github.com/neoave/mrack/commit/01ea068c51fe59738644b51f0deb2527f31f2990))

* chore: Add check-commits action for commits

Checks the future commit headers to be compatible with
the project python-semantic-release.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`1716abf`](https://github.com/neoave/mrack/commit/1716abf8aacd9cbdb32fb48531bf056b4d4db57e))

* chore: Add pre-commit github action

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`ace1da3`](https://github.com/neoave/mrack/commit/ace1da3555e568500f32535aabca4aebdb192447))

* chore: Add mypy to the .pre-commit-config.yaml

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`6e3319f`](https://github.com/neoave/mrack/commit/6e3319faf2d577928493243e532168cdea6848d6))

* chore: Add pre-commit configuration files

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`7095ee0`](https://github.com/neoave/mrack/commit/7095ee08640a07a5139fba0270cecc3dc8d60679))

### Feature

* feat: Output file paths configurable in mrack config

Adding a possibility to change Ansible inventory and pytest multihost
configuration output file paths in a mrack config file. So that a user
can use directly a custom location.

Example of such config:

```ini
[mrack]
mrackdb = config/mrackdb.json
provisioning-config = config/provisioning-config.yaml
metadata = config/metadata.yaml
ansible-inventory = config/test.inventory.yaml
pytest-multihost = config/pytest-multihost-config.yaml
```

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`1761baf`](https://github.com/neoave/mrack/commit/1761baf1da0c75e8bb86ec423e3b563bdfb18871))

* feat: Simple way to add hosts into /etc/hosts file

This is useful for cases where the fake hostname needs to be used
e.g. when accessing FreeIPA Web UI which is sensitive on used hostname.

It is uncomfortable task to read the values from `mrack list` and add
them manualy to /etc/hosts.

The change introduces two commands to help with this case:

* `$ mrack eh add` to add all active hosts into /etc/hosts
* `$ mrack eh clear` to remove all records added by mrack.

Mrack adds two markers into the /etc/hosts file and adds records
between them. This should work also with multiple runs of mrack in
separate tests. If the section already contains the fake hostname then
this line is overwritten with a new value. This is useful when
provisioning hosts for the same task after they were previously
removed.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`da24ac5`](https://github.com/neoave/mrack/commit/da24ac55a3189512c98884eb30f1b5a6ad4dd46a))

### Fix

* fix: Use meta_ prefix for parent domain

When inventory was created the expected key value
for the parent_domain in host section should be
meta_parent_domain playbook will not fail with:
The error was: &#39;meta_parent_domain&#39; is undefined

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`aaeeb58`](https://github.com/neoave/mrack/commit/aaeeb58c0682dbd7be9db94dcb7469c07e6243eb))

* fix: Add missing annotations for mypy

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`2427b15`](https://github.com/neoave/mrack/commit/2427b15ddd12b4d7813a51b3b276b8affd42259b))

* fix: Remove deprecated flag --recursive from Makefile

Remove deprecated flag --recursive for the isort
Add command to sort setup.py.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`48937f3`](https://github.com/neoave/mrack/commit/48937f38a3b8e2780d39539c513187591b9a953d))

* fix: Move common methods to transfromer.py

Move common methods to transfromer.py
to have less copy pasted code.
Added more debug messages to transformation procedure.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`4ea839e`](https://github.com/neoave/mrack/commit/4ea839e560a3d11662d2b65309993652b4cd44bd))

### Refactor

* refactor: Add Status badges for PyPI and docs

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`2f5e25a`](https://github.com/neoave/mrack/commit/2f5e25a8d6976c763dc0d31f91682595e2ed212c))

* refactor: Refactor setup.py and configure release

Refactor setup.py to use version from src/mrack/__init__
Add configuration values for python semantic release
to the pyproject.toml and set default branch for releases.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`544baf6`](https://github.com/neoave/mrack/commit/544baf67afff1f91be99ff2167915d901501d9ad))

* refactor: Update README.md file

Update README.md file with sections:
where example inventory output is shown
where usage of the mrack is explained

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`127dd03`](https://github.com/neoave/mrack/commit/127dd031068215673196839a85b5260f25774a9a))

* refactor: Update files after make format

Previous commit which updated .isort.cfg file
would cause failures in testing with black
and isort afterwards.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`6ba0bec`](https://github.com/neoave/mrack/commit/6ba0bec908acadb1085d339e881cf97f954e6832))

* refactor: Fixing the pre-commit eof-check failures

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`93ab0ac`](https://github.com/neoave/mrack/commit/93ab0ac6db0a4091e4f8c83763204d2213a6c44c))

* refactor: Update yamls that yamllint was complaining about

Update yamls that yamllint was complaining about
Update python version to 3.9

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`3c08ec4`](https://github.com/neoave/mrack/commit/3c08ec454a3593aaf2e3f69f89f20fc1481b8c62))

* refactor: Add dsp_name to logging messages to display context

Add dsp_name to logging messages to display context
for prioviders and transformers.
Added some debug messages.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`4c13b6f`](https://github.com/neoave/mrack/commit/4c13b6f5d89006f7886182fe2c83dbdecdf1b585))

### Unknown

* 0.4.0

Automatically generated by python-semantic-release ([`4d359ac`](https://github.com/neoave/mrack/commit/4d359acb40aa2852942966140262a6fc1cd2a4e0))

* MrackConfig: alternative approach

This commit implements a MrackConfig which allows to define options
and arguments otherwise needed in a configuration file and thus
save people&#39;s time with writing them in CLI.

Config file looks like:
```
[mrack]
mrackdb = config/mrackdb.yaml
provisioning-config = config/provisioning-config.yaml
metadata = config/metadata.yaml
```

Where each value is optional and existance of the config is also
optional.

Mrack looks for the config on these locations:
- user provided path via -c or --mrack-config global option
- ./mrack.conf
- ~/.mrack/mrack.conf
- /etc/mrack/mrack.conf

It also changes CLI of commands:
- metadata is no longer an argument but an option: -m or --metadata
- provisioning config shortcut changes to global -p

With these changes it is possible to define a config file to allow
just typing:
```
$ mrack up
$ mrack list
$ mrack ssh
$ mrack output
$ mrack destroy
```

The MrackConfig class is also extensible for new use cases.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`84e52a2`](https://github.com/neoave/mrack/commit/84e52a29090a66d5ba06c9ea8d7a5de48001f4c9))

* Add mrack.conf from which we load defaults

Add mrack.conf which contains default enfironment
configuration in ini format for the click options
- `--config=provisioning-config from mrack.conf`
- `--db=mrackdb from mrack.conf`

Load default for options from the mrack.conf file from:
1. use `$(pwd)/mrack.conf` or other way the `./mrack.conf` - actual directory
2. or use user home directory configuration - `~/.mrack/mrack.conf`
3. alternatively directory `/etc/mrack/mrack.conf` as safe fallback.

Add example `mrack.conf` and `provisioning-config.yaml`
to the `data/` directory in repository.

Update setup.py to install required files from `data/` dir. ([`951c08f`](https://github.com/neoave/mrack/commit/951c08fb9e80c3dc099751e08f6ed16594c7362d))

* Update .gitignore for python projects

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`8f9a674`](https://github.com/neoave/mrack/commit/8f9a67435304497132b0f0cc1d0a2c17e76cc4e7))

* Support netbios in windows host definition for the inventory

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`1916058`](https://github.com/neoave/mrack/commit/1916058f57aea85da42f34b4f300866c228403ed))

* Give preference to metadata ssh_key_filename in pytest multihost

If job metadata contains a ssh_key_filename, use it for pytest
multihost configuration. I.e. do no override with key used by mrack.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`a1cad10`](https://github.com/neoave/mrack/commit/a1cad10b33034a8244d1f15fec54e56e96d257f3))

* Do not set username for pytest multihost config

We have actually not used it at it cannot be assumed that
the user used for provisioning should be used for pytest-multihost.

E.g. a lot of tests rely on root - to be able to completely control
the remote machine. That cannot be done, e.g. with default cloud-user.

(Though it can often sudo to root)

Let&#39;s keep there the more simple configuration, where user is the
same for all host and is defined in provisioning config &#39;mhcfg&#39; dir.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`7bb230e`](https://github.com/neoave/mrack/commit/7bb230e170ac0a2373a2316ef23a26bfcb681ad9))

* Fix OpenStack provisioning status translation

It is not needed to use a STATUS_MAP for translation status in
prov_result_to_host_data as it is done also in to_host of parent
class. Double translation doesn&#39;t work and thus everything provisioned
had incorrecly status : &#34;other&#34;.

This has then a negative effect on ssh actione where no host is reported
as active.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`a9d62cc`](https://github.com/neoave/mrack/commit/a9d62ccd9206f594dc4b2abec1020a22607980a2))

* Do not show traceback on ApplicationError

So that, e.g., on ssh action, when there are no active host, user
will not get an exception ending with:

```
raise ApplicationError(&#34;No active host available.&#34;)
```

But only:
```
No active host available.
```

Which is more user friendly.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`99c5ab1`](https://github.com/neoave/mrack/commit/99c5ab1ca747da35576a6300cd54a0cd1230d867))

* Increase OpenStack timeout to 6mins

Trying to make the provider more stable if OpenStack is slow, e.g.
under load.

It&#39;s not very clever method. But might work.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`7854c49`](https://github.com/neoave/mrack/commit/7854c4937742ec5ee0cbe05370c324061b3ebdfd))


## v0.3.0 (2020-11-05)

### Documentation

* docs: set master doc to index

From sphinx doc:
&#34;&#34;&#34;
master_doc

    The document name of the “master” document, that is, the document
    that contains the root toctree directive. Default is &#39;index&#39;.

    Changed in version 2.0: The default is changed to &#39;index&#39; from &#39;contents&#39;.
&#34;&#34;&#34;

Read the docs is using version &lt; 2.0 thus it tries to find &#39;content&#39;s
and it fails.

Also changing theme to default - no real reason, thinking it will be
better.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`c62f345`](https://github.com/neoave/mrack/commit/c62f345121ff1cc7dcb1db7dc3ecf0f222e95e8c))

### Unknown

* Release version 0.3.0

New features:

    Create CODE_OF_CONDUCT.md
    Add basic image validation to AWS and Beaker
    Support restraint_id record in metadata
    Add docs on how to set credentials
    Build and publish html to Azure artifacts storage

Bug Fixing and testing:

    docs: set master doc to index
    Remove missing and unused print_basic_info method
    Fix destroy action because delete host now needs only host.id
    Require specific versions for mrack
    Fix regression in up action with OpenStack provider
    Remove unused values in aws and beaker tranformation

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`145b50a`](https://github.com/neoave/mrack/commit/145b50a1a67b92cfff910ea633cd7b3f8ea4ad37))

* Remove unused values in aws and beaker tranformation

These values are loaded from metadata when generating
inventory so they do not need to be passed to provider.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`6b379e1`](https://github.com/neoave/mrack/commit/6b379e1e83512b42ffaebd979d52238bd766ca90))

* Fix regression in up action with OpenStack provider

Provisioning failed because requirements contained unexpected information.

I.e., the provider should receive only the information it expects or
are valid for OpenStack provisioning.

Removing the culprit lines: meta_image and restraint_id params.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`4cdedd1`](https://github.com/neoave/mrack/commit/4cdedd1d49850eee4229a84c36e1fdf45684be29))

* Require specific versions for mrack

It is always better to require specific versions
of dependencies because pip always installs
the latest and they may break funcionality
or create conflicts when mrack is a dependency.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`2c20866`](https://github.com/neoave/mrack/commit/2c2086664418120a521b03c9a6237bb09fe01d0d))

* Build and publish html to Azure artifacts storage

Signed-off-by: Armando Neto &lt;abiagion@redhat.com&gt; ([`305ebc2`](https://github.com/neoave/mrack/commit/305ebc2a55f2a708879859518a2ad410169bbf2b))

* Add docs on how to set credentials

Quick guide on how set credentials for current supported providers.

Signed-off-by: Armando Neto &lt;abiagion@redhat.com&gt; ([`ef46be9`](https://github.com/neoave/mrack/commit/ef46be9b8411312a9b333abe380411ed21b216fa))

* Fix destroy action because delete host now needs only host.id

Because of delete_host method now needs only host.id,
the Destroy action was broken and it needed to use
the host.id variable not whole object as well.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`abbb80c`](https://github.com/neoave/mrack/commit/abbb80c930c2acb519d583bb82efda8abee55f89))

* Support restraint_id record in metadata

Support restraint_id defined in metadata and later
defined in inventory for the restraint jobs.
For this we pass requirements all the way
for later inventory generation.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`59aa87f`](https://github.com/neoave/mrack/commit/59aa87f97e83c2784f0fe46da1fd22dc61f4f917))

* Remove missing and unused print_basic_info method

Add loger info message to error parsing method.
Move the parse_errors to provider.py file.
Add property error to Host object.
Delete host now needs only host_id.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`c6f8394`](https://github.com/neoave/mrack/commit/c6f8394bdfe421f9275dfb4bd2b802e9edfc9b23))

* Add basic image validation to AWS and Beaker

Added basic image validation to AWS and Beaker provider
When os was not known in provisioning config, null/None
was taken and set as required image even for Openstack.

Value of &#39;os&#39; is passed to req when image is not in place.
Then the &#39;os&#39; value is seen in ValidationError messages
even instead of None/null in Openstack, AWS and Beaker.

Support image/distro definition from metadata.
And flag it with meta_distro/meta_image when used.

For AWS check image availability with boto.
When image is not present raise ValidationError

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`1e3b298`](https://github.com/neoave/mrack/commit/1e3b298b26a7e6f494a7c9c9adfcd6a17ff1abd3))

* Create CODE_OF_CONDUCT.md

https://github.com/neoave/mrack/issues/39 ([`38a7a74`](https://github.com/neoave/mrack/commit/38a7a746c7e7be8cda93faeab1aebac02aa320be))


## v0.2.0 (2020-09-29)

### Unknown

* Release version 0.2.0

Bug fixing and testing:

    Refactor providers to share same code
    Force black version to get rid of test errors
    Remove false warnings produced by isort
    Add missing beaker job status
    ansible-inventory: rework generation of groups

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`e5bc921`](https://github.com/neoave/mrack/commit/e5bc9211bcbfc8a8fe1709186e21c337e20fd55e))

* Force black version to get rid of test errors

When black devels change their opinion too much
we got format errors. Let us try to use versioning here.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`38b3f07`](https://github.com/neoave/mrack/commit/38b3f07292624efb55d3ac55caeb1dca0b4c2496))

* Refactor providers to share same code

Methods provision_hosts, delete_hosts and to_host
were moved to provider.py as they can be easily
shared among the providers.

Added missing methods to provider.py to share
same structure. Not implemented methods will throw
a NotImplementedError() and they are ment to be
implmented per provider.

Removed set poll sleeps based on host count.

For all providers moved STATUS_MAP to class
so from now on it is a class attribute.

Openstack&#39;s wait_till_provisioned now uses
instance and not only id to match inherited method.

Added optional username parameter to to_host method in provider.py

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`b0254b2`](https://github.com/neoave/mrack/commit/b0254b2056fd05b742ba544f167f01cd1b464c89))

* ansible-inventory: rework generation of groups

The Ansible inventory output was not correctly adding hosts into groups. E.g.
group was not added when it was not defined in layout. Nested group was not
correctly found and host added.

This part is completely reworked and changes the behavior to:
- add only a host name reference (no vars) into custom groups
- add missing groups as children of &#39;all&#39; group
- works with both &#34;groups&#34; and &#34;group&#34; defined in metadata
- add all hosts to &#39;all&#39; with also variables. This ensures that the full host
  object is defined only once.

Doc: https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`23cdb21`](https://github.com/neoave/mrack/commit/23cdb21996310b35ea200cba36cec21d41839526))

* Add missing beaker job status

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`f476a12`](https://github.com/neoave/mrack/commit/f476a1277fe9290b380e7acecf63e01d3526b772))

* Remove false warnings produced by isort in make format

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`10bd910`](https://github.com/neoave/mrack/commit/10bd910bdac47f08af4b45ab613ec52f300028ab))


## v0.1.4 (2020-09-11)

### Unknown

* Release version 0.1.4

Bug fixing and testing:

    Fixed username for beaker machines to be root.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`364ab4c`](https://github.com/neoave/mrack/commit/364ab4cb571eb97c609bdaccadc634f3415f02b2))

* Add username=&#39;root&#39; to fix ansible user

Added username=&#39;root&#39; to beaker host object
initialization so inventory is created
using ansible_user: root

Fix initialization of provider in a way
that we do not pass provisioning config
but only needed values.

Add status Queued as provisioning.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`b25a173`](https://github.com/neoave/mrack/commit/b25a173a02474be644b51df513640d64536f425c))


## v0.1.3 (2020-09-10)

### Unknown

* Release version 0.1.3

New features:

    Beaker provider support

Bug fixing and testing:

    Use public AWS addresses
    Remove asserts and replace them with ProvisioningErrors

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`02a9fb6`](https://github.com/neoave/mrack/commit/02a9fb62accea530ac658ec6a23b88f7d126e6f2))

* Use public AWS addresses instead of private ones

Using private addresses will result into unreachable host
without vpn tunnel or mechanism to access AWS network.

Add security group, tags, keypair to init of AWS provider.
They have to be defined in provisioning config.

Remove asserts and replace them with ProvisioningErrors

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`79aa885`](https://github.com/neoave/mrack/commit/79aa8857995fa51599e9adf61c047efc286685a1))

* Add beaker provider

Beaker provider generates jobxml and then schedules
this job to beaker hub. Provider waits until job
is in Reserved state which is success.

Beaker provider requires kerberos credentials.

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`40dcb7f`](https://github.com/neoave/mrack/commit/40dcb7ff972408da74821d63fec92846227d65a2))


## v0.1.2 (2020-08-28)

### Unknown

* Release version 0.1.2

New features:

    mrack now generates output with modules for:
    - ansible-inventory
    - pytest-multihost
    added a static provider to create resources from static VMs
    added list action to print resources from DB
    added ssh action to connect quickly to VMs in DB

Bug fixing and testing:

    added tests for static provider
    added various minor fixes

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`43d7c6c`](https://github.com/neoave/mrack/commit/43d7c6c139366349e9ebb804f9808300c54ebcec))

* Fix style after black update

Latest version of black was complaing about these changes.

Previous version: black-19.10b0
Latest version: black-20.8b1

Signed-off-by: Armando Neto &lt;abiagion@redhat.com&gt; ([`b850639`](https://github.com/neoave/mrack/commit/b8506391e12f3be1c7027109d9b27c17888a504e))

* Set defaults for pytest and remove xunit1 format warning message

So that we can more easily inspect in azure if new tests were run
properly and also be able to see the results.

Mainly it removes warning message about deprecating xunit1 format.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`fc28e66`](https://github.com/neoave/mrack/commit/fc28e664a9d94a568df70312ed693877e56d8aa9))

* Add test scenario for actions with static provider

Testing up, output, list and destroy actions using the Static Provider.

Signed-off-by: Armando Neto &lt;abiagion@redhat.com&gt; ([`50dcc77`](https://github.com/neoave/mrack/commit/50dcc779c26e0e14bfc6069420b9f6bed36ccfb0))

* Handle output action error

Running `mrack output` with an empty database breaks
`python-pytest-multihost` config file. (E.g: Not running `mrack
up` before trying that.)

Signed-off-by: Armando Neto &lt;abiagion@redhat.com&gt; ([`3b71d86`](https://github.com/neoave/mrack/commit/3b71d86c70b339eac4246c7c8b0a452109c5fd2f))

* Print message only

Signed-off-by: Armando Neto &lt;abiagion@redhat.com&gt; ([`089c80c`](https://github.com/neoave/mrack/commit/089c80c1841191a9a0bed63c545c671006963e5e))

* Docs: do not use source/_static directory

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`be8d5fa`](https://github.com/neoave/mrack/commit/be8d5fadf03df53d61f55321314dab45219b867b))

* Load the requirements.txt in setup.py

Load the content of requirements.txt file
instead of having static list in setup.py

Update the test-requirements.txt to contain
all necessary dependencies to test.

Add requirements.txt to tox.ini

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`a20e288`](https://github.com/neoave/mrack/commit/a20e288c819318a884888d9b5a780ce5c34cafc1))

* Normalize all imports

Signed-off-by: Armando Neto &lt;abiagion@redhat.com&gt; ([`e00a77a`](https://github.com/neoave/mrack/commit/e00a77acb25cc3254129141a66df23b006e638b5))

* Enable isort linting

Helper tool to sort the imports for us.

Signed-off-by: Armando Neto &lt;abiagion@redhat.com&gt; ([`e56d267`](https://github.com/neoave/mrack/commit/e56d2678c6e3eafa34d93427f5b42efe81d86059))

* Rename aiohabit project to mrack

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`4b4233f`](https://github.com/neoave/mrack/commit/4b4233f9a6b0e141e744b0ac2ec39d3f557b021d))

* Replace print statements with logging

Adding logging calls to replace print statements.
Rename exception objects to three letters to not mess with pdb.

Signed-off-by: Armando Neto &lt;abiagion@redhat.com&gt; ([`8ec7bf9`](https://github.com/neoave/mrack/commit/8ec7bf98391adb4bc02de381268577f857bbdd0a))

* Add basic logging mechanism

Configure a logger to be used in the whole application.

If user pass `--debug` to aiohabit log level is changed to DEBUG.

Signed-off-by: Armando Neto &lt;abiagion@redhat.com&gt; ([`c41f93b`](https://github.com/neoave/mrack/commit/c41f93b2e3dc736563dce2bce59c1bcb60a9c58a))

* AWS host: Return the right status

Signed-off-by: Armando Neto &lt;abiagion@redhat.com&gt; ([`6c02c34`](https://github.com/neoave/mrack/commit/6c02c347074ff9461a5e332da6d27bb81ca7a605))

* ansible-inventory: fix bug when python interpreter not defined for os

E.g. so that the default python interpreter will be used.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`dfddfaf`](https://github.com/neoave/mrack/commit/dfddfafa714e04d21d1134d16a3a51d5d43a4be5))

* Static provider

Static provider serves for mixing already provisioned hosts (pets)
with dynamically provisioned hosts. Alternatively all hosts can
be static. This can be useful for generating the outputs and using
other features.

Almost all operations are fake given that the hosts exist and cannot
be deleted by static provider. The most important parts is to provide
a name and ip.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`f3bc80b`](https://github.com/neoave/mrack/commit/f3bc80b009be50108109d4f126013aaa40463814))

* Add SSH action

To make it very easy to SSH into a host based on value in various
configuration objects.

It is usually very time-consuming to &#34;cat&#34; e.g. inventory, copy the
real hostname/IP, write all the SSH options including determining
if it should use SSH key and what is its location.

The interactive mode even saves time with writing the fake hostname.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`044de05`](https://github.com/neoave/mrack/commit/044de0569a19138c178c93d747530f50d2e735d2))

* Host: add first IP getter

To avoid copy&amp;paste in SSH action

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`749d666`](https://github.com/neoave/mrack/commit/749d666e0c18c1eacc2ee4a18c576fc9421191a4))

* Common methods to figure out username, password, ssh key for a host

To avoid copy&amp;paste in ssh action.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`22c163f`](https://github.com/neoave/mrack/commit/22c163fd1120b6b0c42091551f79713be49bf7de))

* Add list action

To quickly show content of DB in human readable form

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`a7a6114`](https://github.com/neoave/mrack/commit/a7a611471404e5b2a268056f54c2b0cdda43e623))

* Host: include status in print

So that it is known which hosts are still active.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`b993302`](https://github.com/neoave/mrack/commit/b9933021956e9436ddfd68343d201745929d528d))

* Add Ansible Inventory and pytest-multihost output modules

And enhance &#34;up&#34; action to use them. Add also &#34;output&#34; action which
calls them separately. It can be used for recreation of deleted ones
or testing.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`97f482e`](https://github.com/neoave/mrack/commit/97f482e2e9338c618fdec42bb2f4970057725976))

* hosts: adding missing properties

So that they can be work with in output modules.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`ceb5e93`](https://github.com/neoave/mrack/commit/ceb5e9389981b776cdfd9e28f558ee70415da211))


## v0.1.1 (2020-08-28)

### Unknown

* Add AWS provider

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`173b259`](https://github.com/neoave/mrack/commit/173b259b39a6975f57d9d82b3b78565bf82e4b48))

* Do not use relative imports

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`5f69bdc`](https://github.com/neoave/mrack/commit/5f69bdc53fd54539a3f65a2f1c547707e194539e))


## v0.1.0 (2020-08-28)

### Unknown

* Fix some typos

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`66b4040`](https://github.com/neoave/mrack/commit/66b40400bd2aa87105666362e77caa9a75ff186e))

* make up and destroy action work

Finishing of previous &#34;WIP&#34; architecture commit. With this, provisioning
in OpenStack is working. I.e. machines can be provisioned by up action
and destroyed by destroy action with state saved using File driver.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`11d2439`](https://github.com/neoave/mrack/commit/11d2439bd2fd2f69737989addb2d7ecfe364df41))

* run: gracefully handle exceptions

So that nice error message is shown on expected errors.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`a7a5e04`](https://github.com/neoave/mrack/commit/a7a5e04bcd44ea17dc5af9277b26b434997f6a1b))

* Update ctx obj attribute and add yaml helper functions

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`01cee03`](https://github.com/neoave/mrack/commit/01cee032c5d450ad08ee570b2fa18742389cd9ef))

* Update requirements.txt

Signed-off-by: Tibor Dudlák &lt;tdudlak@redhat.com&gt; ([`1e68b67`](https://github.com/neoave/mrack/commit/1e68b674f9e097b089c7e1a8fc3c565dadd6ecbe))

* WIP: Main app architecture with basic functionality

Adding:
- up action
- destroy action

Introducing concepts:

Trasnsformers: combines metadata together with provisioning config to
get configuration for providers.

Outputs: transform result of providers to various files like ansible
inventory or pytest-multihost config

Drivers: saves results of actions to file so that it can be used
later. E.g. up action result to be used for destroy action.

Adds basic CLI entry point for debugging or standalone usage.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`3fccf92`](https://github.com/neoave/mrack/commit/3fccf92802b942b71706bc31333dbbd607f02629))

* fix Azure pipelines testing

Run the same stuff as in tox

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`b5e8a9e`](https://github.com/neoave/mrack/commit/b5e8a9ede2b3d9a51e4029f384e6b7e5bc4dd1ae))

* Set up CI with Azure Pipelines

[skip ci] ([`3467504`](https://github.com/neoave/mrack/commit/3467504d3f9d2339cfad5d10c91fadc6bce7eb94))

* Add Contribute section to README.md

To set expectations.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`0dbcdcb`](https://github.com/neoave/mrack/commit/0dbcdcb5ccc0ee77a4eea9d3bb25439eb3d40396))

* lint: add pydocstyle checks and adjust/add doc strings

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`7d0867f`](https://github.com/neoave/mrack/commit/7d0867f161963b482e541fc515f541756a589579))

* doc string changes ([`20e938d`](https://github.com/neoave/mrack/commit/20e938d333a327f3d47ccc40661bafb50ec8344a))

* add unit tests for openstack provider

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`152051c`](https://github.com/neoave/mrack/commit/152051cdd7a6c5f5ef1ced18ac3028b9179fc081))

* openstack: add get_ips method to get IP availability for network

So that network availability  can be queried by network name or uuid
in the same way as other objects.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`60189ce`](https://github.com/neoave/mrack/commit/60189ce665cc04865646026090b976427beb6421))

* Move aiohabit package to src directory

Based on good practices in pytest

https://docs.pytest.org/en/latest/goodpractices.html

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`02e2cdd`](https://github.com/neoave/mrack/commit/02e2cddc307452bef25fb8b57927bafad8a1e682))

* Reformat code using python black

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`56c0a5a`](https://github.com/neoave/mrack/commit/56c0a5a2d6f9ca1e84d9d131c44058cbed6f3113))

* Initial .gitignore file

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`09e8959`](https://github.com/neoave/mrack/commit/09e89598f68c2ce960c0e98b50d094e24fe27c06))

* Initial implementation of OpenStack provider

This provider is now capable of:

* loading images, flavors, networks and limits up from during
  initialization
* checking available resources (vCPU, memory) ahead
* provisioning multiple servers in parallel
* waiting for the servers to be ACTIVE
* deleting provisioned servers

TODO: check available IP addresses in networks

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`bb9bf58`](https://github.com/neoave/mrack/commit/bb9bf58d0840329d7b46eb2990f0cfac3c0b43aa))

* Basic highlevel API

this might change completely during development

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`29535a5`](https://github.com/neoave/mrack/commit/29535a5a5a01f957a8a2aef9e77d762dcdd4225a))

* Basic structure for future docs

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`f9ac876`](https://github.com/neoave/mrack/commit/f9ac876580c8d0b31030fc6cc07680e5af6e4730))

* Initial commit.

Describes basic intentions of the project.

Signed-off-by: Petr Vobornik &lt;pvoborni@redhat.com&gt; ([`e9fdb37`](https://github.com/neoave/mrack/commit/e9fdb378abfb0aa5d6d4dc568d655c08f1be4d33))
