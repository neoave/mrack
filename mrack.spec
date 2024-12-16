Name:           mrack
Version:        1.23.1
Release:        1%{?dist}
Summary:        Multicloud use-case based multihost async provisioner

License:        Apache-2.0
URL:            https://github.com/neoave/mrack
Source0:        %{URL}/releases/download/v%{version}/%{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-click
BuildRequires:  python3-pyyaml
BuildRequires:  python3-setuptools

# coma separated list of provider plugins
%global provider_plugins aws,beaker,openstack,podman,virt

Requires:       %{name}-cli = %{version}-%{release}
Requires:       python3-%{name}lib = %{version}-%{release}
Requires:       python3-%{name}-aws = %{version}-%{release}
Requires:       python3-%{name}-beaker = %{version}-%{release}
Requires:       python3-%{name}-openstack = %{version}-%{release}
Requires:       python3-%{name}-podman = %{version}-%{release}
Requires:       python3-%{name}-virt = %{version}-%{release}

# We filter out the asyncopenstackclient dependency of this package
# so it is not forcing installation of missing dependencies in Fedora
# Once python3-AsyncOpenStackClient is in fedora we can drop this line
%global __requires_exclude asyncopenstackclient
%{?python_disable_dependency_generator}

%description
mrack is a provisioning tool and a library for CI and local multi-host
testing supporting multiple provisioning providers (e.g. AWS, Beaker,
Openstack). But in comparison to other multi-cloud libraries,
the aim is to be able to describe host from application perspective.

%package        cli
Summary:        Command line interface for mrack
Requires:       python3-%{name}lib = %{version}-%{release}
Requires:       python3-click

%package -n     python3-%{name}lib
Summary:        Core mrack libraries
Requires:       python3-pyyaml
Recommends:     python3-gssapi
Requires:       sshpass

%{?python_provide:%python_provide python3-%{name}lib}

%package -n     python3-%{name}-aws
Summary:        AWS provider plugin for mrack
Requires:       python3-%{name}lib = %{version}-%{release}
Requires:       python3-boto3
Requires:       python3-botocore

%{?python_provide:%python_provide python3-%{name}-aws}


%package -n     python3-%{name}-beaker
Summary:        Beaker provider plugin for mrack
Requires:       python3-%{name}lib = %{version}-%{release}
%if 0%{?rhel} == 8
# c8s has missing beaker-client package
Recommends:     beaker-client
%else
Requires:       beaker-client
%endif

%{?python_provide:%python_provide python3-%{name}-beaker}


%package -n     python3-%{name}-openstack
Summary:        Openstack provider plugin for mrack
Requires:       python3-%{name}lib = %{version}-%{release}
Recommends:       python3-aiofiles
Recommends:       python3-os-client-config
Recommends:     python3-AsyncOpenStackClient
Recommends:     python3-async-timeout

%{?python_provide:%python_provide python3-%{name}-openstack}


%package -n     python3-%{name}-podman
Summary:        Podman provider plugin for mrack
Requires:       python3-%{name}lib = %{version}-%{release}
Requires:       podman

%{?python_provide:%python_provide python3-%{name}-podman}

%package -n     python3-%{name}-virt
Summary:        Virtualization provider plugin for mrack using testcloud
Requires:       python3-%{name}lib = %{version}-%{release}
Requires:       testcloud

%{?python_provide:%python_provide python3-%{name}-virt}

%description        cli
%{name}-cli contains mrack command which functionality
can be extended by installing mrack plugins

%description -n     python3-%{name}lib
python3-%{name}lib contains core mrack functionalities
and static provider which can be used as a library

%description -n     python3-%{name}-aws
%{name}-aws is an additional plugin with AWS provisioning
library extending mrack package

%description -n     python3-%{name}-beaker
%{name}-beaker is an additional plugin with Beaker provisioning
library extending mrack package

%description -n     python3-%{name}-openstack
%{name}-openstack is an additional plugin with OpenStack provisioning
library extending mrack package

%description -n     python3-%{name}-podman
%{name}-podman is an additional plugin with Podman provisioning
library extending mrack package

%description -n     python3-%{name}-virt
%{name}-virt is an additional plugin with Virualization provisioning
library extending mrack package using testcloud

%prep
%autosetup -p1 -n %{name}-%{version}
# Remove bundled egg-info
rm -r src/%{name}.egg-info

%build
%py3_build

%install
%py3_install

%files
%license LICENSE
%doc README.md
%doc CHANGELOG.md

%files cli
# the mrack man page RFE: https://github.com/neoave/mrack/issues/197
%license LICENSE
%doc README.md
%doc CHANGELOG.md
%{_bindir}/%{name}
%{python3_sitelib}/%{name}/{,__pycache__/}run.*

%files -n python3-%{name}lib
%license LICENSE
%doc README.md
%doc CHANGELOG.md
%{python3_sitelib}/%{name}
%{python3_sitelib}/%{name}-%{version}-py%{python3_version}.egg-info
%exclude %{python3_sitelib}/%{name}/{,__pycache__/}run.*
%exclude %{python3_sitelib}/%{name}/providers/utils/{,__pycache__/}osapi.*
%exclude %{python3_sitelib}/%{name}/providers/utils/{,__pycache__/}testcloud.*
%exclude %{python3_sitelib}/%{name}/providers/utils/{,__pycache__/}podman.*
%exclude %{python3_sitelib}/%{name}/providers/{,__pycache__/}{%{provider_plugins}}.*
%exclude %{python3_sitelib}/%{name}/transformers/{,__pycache__/}{%{provider_plugins}}.*

%files -n python3-%{name}-aws
%{python3_sitelib}/%{name}/transformers/{,__pycache__/}aws.*
%{python3_sitelib}/%{name}/providers/{,__pycache__/}aws.*

%files -n python3-%{name}-beaker
%{python3_sitelib}/%{name}/transformers/{,__pycache__/}beaker.*
%{python3_sitelib}/%{name}/providers/{,__pycache__/}beaker.*

%files -n python3-%{name}-openstack
%{python3_sitelib}/%{name}/transformers/{,__pycache__/}openstack.*
%{python3_sitelib}/%{name}/providers/{,__pycache__/}openstack.*
%{python3_sitelib}/%{name}/providers/utils/{,__pycache__/}osapi.*

%files -n python3-%{name}-podman
%{python3_sitelib}/%{name}/transformers/{,__pycache__/}podman.*
%{python3_sitelib}/%{name}/providers/{,__pycache__/}podman.*
%{python3_sitelib}/%{name}/providers/utils/{,__pycache__/}podman.*

%files -n python3-%{name}-virt
%{python3_sitelib}/%{name}/transformers/{,__pycache__/}virt.*
%{python3_sitelib}/%{name}/providers/{,__pycache__/}virt.*
%{python3_sitelib}/%{name}/providers/utils/{,__pycache__/}testcloud.*

%changelog
* Mon Dec 16 2024 David Pascual Hernandez <davherna@redhat.com> - 1.23.1-1
- 0cabc75 fix: Translate job-group properly (David Pascual)
- 70e07c1 fix: Return empty list when there is no content in res_ks_list (David Pascual)

* Tue Nov 05 2024 David Pascual Hernandez <davherna@redhat.com> - 1.23.0-1
- 64a84db feat: Add support for translanting job-owner of kickstart (David Pascual)
- 868523c feat: Add translantion for kernel_options and kernel_options_post (David Pascual)

* Thu Oct 17 2024 David Pascual Hernandez <davherna@redhat.com> - 1.22.0-1
- f43d20f style: Reformat by black (David Pascual)
- 768bba5 fix: podman: set podman connection information for ansible (David Pascual)
- 4d0b63c chore: setup: package seccomp filter (David Pascual)
- 9b2d980 docs: Update seccomp configuration example (David Pascual)
- f3deca1 feat: podman: handle custom network configuration (David Pascual)

* Tue Aug 06 2024 Kaleemullah Siddiqui  <kaleem.amu@gmail.com> - 1.21.0-1
- b3e0f7d feat: update pytest-mh output to work with latest version (Kaleemullah Siddiqui)

* Tue Jul 16 2024 David Pascual Hernandez <davherna@redhat.com> - 1.20.0-1
- feeae04 feat: Add support for translanting %pre and main body part of kickstart (David Pascual)
- 236393c chore: Update deprecated actions (David Pascual)

* Thu May 30 2024 David Pascual Hernandez <davherna@redhat.com> - 1.19.0-1
- 6f81e37 test: speed-up tests by mocking gethostbyaddr (Petr Vobornik)
- 587a9c7 fix(beaker): supress 10_avc_check restraint plugin (Petr Vobornik)
- 2c0c2bb test: Add add_dict_to_node test (Petr Vobornik)
- f4324bf feat: handle list value for add_dict_to_node function (Petr Vobornik)
- f1e7590 fix: make delete_host function more robust (Petr Vobornik)
- 784d24b chore: bump black in pre-commit (David Pascual)
- f6f9131 chore(deps): bump black from 22.3.0 to 24.3.0 (David Pascual)
- a7db867 test: Add test for _get_recipe_info function (Petr Vobornik)
- aa25ff3 feat: Provide beaker log links (Petr Vobornik)

* Mon Nov 27 2023 David Pascual Hernandez <davherna@redhat.com> - 1.18.0-1
- c158474 feat: Add async_timeout dependency (David Pascual)

* Fri Nov 03 2023 David Pascual Hernandez <davherna@redhat.com> - 1.17.1-1
- 583193a fix: curate_auth func changed to non-async (Kaleemullah Siddiqui)

* Mon Oct 23 2023 David Pascual Hernandez <davherna@redhat.com> - 1.17.0-1
- 5251d90 chore(ci): Temporarely remove packit tests (David Pascual)
- 3a59761 feat(openstack): Append API version to auth_url in credentials (David Pascual)
- 97a5355 chore(release): Update semantic release action name and version (David Pascual)
- 6d6cdc6 chore(release): Upload distribution package to release assets (David Pascual)

* Mon Oct 09 2023 David Pascual Hernandez <davherna@redhat.com> - 1.16.0-1
- e8e20f1 chore(ci): Fix release workflow build step checking out wrong commit (David Pascual)
- 97a7cd0 chore: Bump asyncopenstackclient dependency version (David Pascual)
- 41b12e7 chore: Release version 1.16.0 (github-actions)
- 278d1b1 chore(release): Add PyPI action & extract copr step (Tibor Dudlák)
- 9bbd987 chore: Bump python-semantic-release to v7.34.4 (Tibor Dudlák)
- d6b7298 feat: Add new dependecies to mrack.spec file (David Pascual)
- 7bbda34 feat(OpenStack): Add clouds.yaml as an authentication method (David Pascual)
- a5b32e3 feat(OpenStack): Import publick key on provision (David Pascual)
- 1a29d86 test: fix pylint issues and use isinstance (Tibor Dudlák)
- db74ae0 fix(Beaker): Exception has been thrown as raise missed argument (Tibor Dudlák)
- de027fa docs(Beaker): Add hostRequires documentation section to guides (David Pascual)

* Tue Sep 19 2023 Tibor Dudlák <tdudlak@redhat.com> - 1.16.0-1
- 278d1b1 chore(release): Add PyPI action & extract copr step (Tibor Dudlák)
- 9bbd987 chore: Bump python-semantic-release to v7.34.4 (Tibor Dudlák)
- d6b7298 feat: Add new dependecies to mrack.spec file (David Pascual)
- 7bbda34 feat(OpenStack): Add clouds.yaml as an authentication method (David Pascual)
- a5b32e3 feat(OpenStack): Import publick key on provision (David Pascual)
- 1a29d86 test: fix pylint issues and use isinstance (Tibor Dudlák)
- db74ae0 fix(Beaker): Exception has been thrown as raise missed argument (Tibor Dudlák)
- de027fa docs(Beaker): Add hostRequires documentation section to guides (David Pascual)

* Tue Jun 13 2023 Tibor Dudlák <tdudlak@redhat.com> - 1.15.1-1
- 608c763 chore(Packit): Use yaml magic to run same internal tests for PRs and commits to main (Tibor Dudlák)
- 8062a20 refactor: more verbose output when (re)provisioning (Tibor Dudlák)
- 19b52f8 test(OpenStack): Add reprovision with dynamic result tests (Tibor Dudlák)
- fd111f5 fix: Do not reprovision all hosts when server error is detected (Tibor Dudlák)
- 6e499f6 fix: Use lower cooldown time to not be too slow in re-provisioning (Tibor Dudlák)
- e03793c chore(Packit): Add internalt tests per pull request (Tibor Dudlák)
- 44023eb chore(Packit): add missing build job(s) to Packit config (Tibor Dudlák)

* Tue Apr 18 2023 Tibor Dudlák <tdudlak@redhat.com> - 1.15.0-1
- f9f0e33 test: Add missing strategy_retry test (Tibor Dudlák)
- 121c5db refactor(provider): take max_utilization out to method to ease mocking (Tibor Dudlák)
- dc74ced test: Add missing tests for fixed code from https://github.com/neoave/mrack/pull/245 (Tibor Dudlák)
- 86393ab feat(outputs): preset username and password for windows host in pytest-mh (Tibor Dudlák)
- 4c26b5f feat(outputs): merge nested dictionary instead of overriding it (Tibor Dudlák)
- 4dde2e5 feat(utils): add merge_dict (Tibor Dudlák)
- 5440be1 refactor: fixes _openstack_gather_responses test warnings and exec time (David Pascual)
- e29031b fix: Handle 403 AuthError (out of quota) in openstack provisioning (David Pascual)
- a4e5075 feat: configurable ssh options (Petr Vobornik)
- e9d716e chore: fix docs dependencies in tox run (Petr Vobornik)
- 6f1943b chore: add Markdown support to docs and add design section (Petr Vobornik)
- 88458e1 docs: SSH options design (Petr Vobornik)

* Thu Mar 16 2023 Tibor Dudlák <tdudlak@redhat.com> - 1.14.1-1
- a9c4e62 fix: mrack not re-provisioning hosts which were destroyed (Tibor Dudlák)
- 17b45e4 fix: Replace coroutines with tasks to avoid RuntimeError (David Pascual)

* Wed Mar 08 2023 Tibor Dudlák <tdudlak@redhat.com> - 1.14.0-1
- e319b73 refactor(AWS): change variable name typo in get_ip_addresses (Tibor Dudlák)
- d95e65f fix(OpenStack): Add missing await for self._load_limits() method call (Tibor Dudlák)
- d0c2d8f refactor: Update supported providers (Tibor Dudlák)
- 13ad3df fix(outputs): remove config section from pytest-multihost (Tibor Dudlák)
- d3da251 feat(outputs): allow to overwrite ansible layout (Tibor Dudlák)
- d3ac20d feat(outputs): allow to choose which outputs should be generated (Tibor Dudlák)
- 66f2877 feat(outputs): add support for pytest-mh (Tibor Dudlák)
- db633b7 feat(utils): relax condition in get_fqdn (Tibor Dudlák)
- 0735e36 fix(outputs): add host to correct group in layout (Tibor Dudlák)
- b1f5318 feat(utils): add get_os_type (Tibor Dudlák)
- 0ab88e6 refactor(black): reformat code (Tibor Dudlák)

* Wed Mar 01 2023 Tibor Dudlák <tdudlak@redhat.com> - 1.13.3-1
- 0f62237 fix(OpenStack): await loading limits to not break provisioning (Tibor Dudlák)

* Wed Mar 01 2023 Tibor Dudlák <tdudlak@redhat.com> - 1.13.2-1
- 06f18d1 fix: Use get method when host error object is a dictionary (Tibor Dudlák)
- fd33d68 fix(Beaker): rerurn common dictionary when validation fails (Tibor Dudlák)
- b6c5ef4 fix(OpenStack): Add exception parameter when validation fails (Tibor Dudlák)
- fa2c779 fix(OpenStack): load limits properly by one method (Tibor Dudlák)
- 61e515f chore: change back mrack dist release to 1 (Tibor Dudlák)

* Tue Feb 21 2023 Tibor Dudlák <tdudlak@redhat.com> - 1.13.1-1
- 1421b37 fix(MrackConfig): Fix MrackConfig class properties (Tibor Dudlák)

* Fri Feb 17 2023 Tibor Dudlák <tdudlak@redhat.com> - 1.13.0-1
- 72cc2f3 test: add extra dnf options when dealing with rhel/epel 8 (Tibor Dudlák)
- 32a754b chore: set packit to sync changelog as well (Tibor Dudlák)
- b0512b4 chore: sync fedora spec to upstream to maintain changelog history for fedora (Tibor Dudlák)
- be7b50a chore: Generate proper changelog from commit history when releasing (Tibor Dudlák)
- 98f4035 chore: Bump python-semantic-release to latest (Tibor Dudlák)
- a0e76dd test(OpenStack): Fixup the network spread tests (Tibor Dudlák)
- 88b9332 test(OpenStack): rewrite network alloaction tests (Tibor Dudlák)
- 777862f feat(OpenStack): Provide a way to disable network spreading (Tibor Dudlák)
- ff7331d fix(OpenStack): fix condition for network to get in interval (Tibor Dudlák)
- 943316d fix: fqdn in name is ignored and mrack guesses the name instead #237 (Tibor Dudlák)
- 46141dc feat(AWS): Add utilization check method (Tibor Dudlák)
- bb80060 feat(OpenStack): Add utilization check method (Tibor Dudlák)
- 55f9c2c feat: Do not use same sleep for every mrack run (Tibor Dudlák)
- 6ce3927 test(AnsibleInventory): global level output values override (Tibor Dudlák)
- a7a896a feat(AnsibleInventory): Allow additional global level values (Tibor Dudlák)
- 91c562c feat(AnsibleInventory): Allow additional domain level ansible inventory values (Tibor Dudlák)
- 109b03c test(OpenStack): Update calls in openststack tests (Tibor Dudlák)
- 4467cc2 refactor(OpenStack): make private openstack methods truly private (Tibor Dudlák)
- 72b9b9c chore: use custom release_suffix for PR testing via packit (Petr Vobornik)
- f3f734a chore: disable pylint pre-commit hook (Petr Vobornik)
- 4aa9b0a chore(Packit): Add synchronization of tmt plans and tests (Tibor Dudlák)
- 02c3e01 chore(Packit): Configure users on whose actions packit is allowed to be run (Tibor Dudlák)
- cf14ed9 chore(Packit): Add missing ci.fmf to synced files (Tibor Dudlák)

* Tue Dec 13 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.12.3-4
- chore: Add add tmt tests and plans and add them to sync (Tibor Dudlák)

* Tue Dec 13 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.12.3-3
- chore: Add fmf/version and allowed users to run packit (Tibor Dudlák)

* Tue Dec 13 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.12.3-2
- chore: Add ci.fmf to the repo (Tibor Dudlák)

* Tue Dec 13 2022 Packit <hello@packit.dev> - 1.12.3-1
- chore: Release version 1.12.3 (github-actions)
- chore(Packit): Enable copr build for commit to main only. (Tibor Dudlák)
- chore(Packit): Enable TF tests job to run on pull request. (Tibor Dudlák)
- chore(Packit): Add fedora gating.yaml to synced files. (Tibor Dudlák)
- chore(TestingFarm): Add gating for fedora workflow (Tibor Dudlák)
- fix: Add cache decorator for older python versions. (Tibor Dudlák)
- fix(mrack.spec): Missing dependency in c8s for beaker-client (Tibor Dudlák)
- chore(Packit): enable epel-8 and epel-9 updates and tests (Tibor Dudlák)
- fix(AWS): refactor sources to be py3.6 compatible (Tibor Dudlák)

* Fri Dec 02 2022 Packit <hello@packit.dev> - 1.12.2-1
- chore: Release version 1.12.2 (github-actions)
- chore: Use python 3.10 in GH actions (Tibor Dudlák)
- refactor: pylint fixes related to Python 3.10 (Tibor Dudlák)
- test: Fix test_utils.py to be included in pytest run (Tibor Dudlák)
- chore(pytest): add missing python_path when using pytest >=7.0.0 (Tibor Dudlák)
- test: Add test for value_to_bool util function (Tibor Dudlák)
- fix: Owner requirement boolean parsing from string (Tibor Dudlák)
- chore(Packit): Add upstream_tag_template to .packit.yaml (Tibor Dudlák)

* Thu Nov 24 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.12.1-1
- Released upstream version 1.12.1

* Mon Nov 14 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.12.0-1
- Released upstream version 1.12.0

* Thu Nov 03 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.11.0-1
- Released upstream version 1.11.0

* Wed Oct 26 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.10.0-1
- Released upstream version 1.10.0

* Thu Oct 20 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.9.1-1
- Released upstream version 1.9.1

* Wed Oct 12 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.9.0-1
- Released upstream version 1.9.0

* Mon Oct 10 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.8.1-1
- Released upstream version 1.8.1

* Mon Oct 10 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.8.0-1
- Released upstream version 1.8.0

* Tue Sep 20 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.7.0-1
- Released upstream version 1.7.0

* Wed Jul 27 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.6.0-1
- Released upstream version 1.6.0

* Fri Jul 08 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.5.0-1
- Released upstream version 1.5.0

* Fri Jun 17 2022 David Pascual Hernandez <davherna@redhat.com> - 1.4.1-1
- Released upstream version 1.4.1

* Thu May 05 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.4.0-1
- Released upstream version 1.4.0

* Tue Apr 05 2022 Tibor Dudlák <tdudlak@redhat.com> - 1.3.1-1
- Released upstream version 1.3.1

* Fri Apr 01 2022 David Pascual Hernandez <davherna@redhat.com> - 1.3.0-1
- Released upstream version 1.3.0

* Wed Dec 15 2021 Tibor Dudlák <tdudlak@redhat.com> - 1.2.0-1
- Released upstream version 1.2.0

* Thu Nov 25 2021 Tibor Dudlák <tdudlak@redhat.com> - 1.1.1-1
- Released upstream version 1.1.1

* Tue Nov 23 2021 Tibor Dudlák <tdudlak@redhat.com> - 1.1.0-1
- Released upstream version 1.1.0

* Fri Sep 03 2021 Tibor Dudlák <tdudlak@redhat.com> - 1.0.0-1
- Released upstream version 1.0.0

* Thu Jul 01 2021 Tibor Dudlák <tdudlak@redhat.com> - 0.14.0-1
- Released upstream version 0.14.0

* Tue Jun 08 2021 Francisco Triviño <ftrivino@redhat.com> - 0.13.0-1
- Released upstream version 0.13.0

* Thu May 13 2021 Tibor Dudlák <tdudlak@redhat.com> - 0.12.0-1
- Released upstream version 0.12.0

* Fri May 07 2021 Tibor Dudlák <tdudlak@redhat.com> - 0.11.0-1
- Released upstream version 0.11.0

* Fri Apr 30 2021 Bhavik Bhavsar <bbhavsar@redhat.com> - 0.10.0-1
- Released upstream version 0.10.0

* Mon Apr 19 2021 Armando Neto <abiagion@redhat.com> - 0.9.0-1
- Released upstream version 0.9.0

* Thu Apr 15 2021 Armando Neto <abiagion@redhat.com> - 0.8.0-1
- Released upstream version 0.8.0

* Tue Mar 23 2021 Armando Neto <abiagion@redhat.com> - 0.7.1-1
- Released upstream version 0.7.1

* Mon Mar 22 2021 Tibor Dudlák <tdudlak@redhat.com> - 0.7.0-1
- Released upstream version 0.7.0

* Thu Feb 04 2021 Armando Neto <abiagion@redhat.com> - 0.6.0-1
- Initial package.
