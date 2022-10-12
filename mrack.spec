# Created by pyp2rpm-3.3.5
Name:           mrack
Version:        1.9.0
Release:        1%{?dist}
Summary:        Multicloud use-case based multihost async provisioner for CIs and testing during development

License:        Apache License 2.0
URL:            https://github.com/neoave/mrack
Source0:        https://github.com/neoave/mrack/releases/download/v%{version}/%{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-click
BuildRequires:  python3-pyyaml
BuildRequires:  python3-setuptools

# coma separated list of provider plugins
%global provider_plugins aws,beaker,openstack,podman,virt

Requires:       %{name}-cli == %{version}-%{release}
Requires:       python3-%{name}lib == %{version}-%{release}
Requires:       python3-%{name}-aws == %{version}-%{release}
Requires:       python3-%{name}-beaker == %{version}-%{release}
Requires:       python3-%{name}-openstack == %{version}-%{release}
Requires:       python3-%{name}-podman == %{version}-%{release}
Requires:       python3-%{name}-virt == %{version}-%{release}

# We filter out the asyncopenstackclient dependency of this package
# so it is not forcing installation of missing dependencies in Fedora
# Once python3-AsyncOpenStackClient is in fedora we can drop this line
%global __requires_exclude asyncopenstackclient

%description
mrack is a provisioning tool and a library for CI and local multi-host testing supporting
multiple provisioning providers (e.g. AWS, Beaker, Openstack). But in comparison to other
multi-cloud libraries, the aim is to be able to describe host from application perspective.

%{?python_provide:%python_provide %{name}}

%package        cli
Summary:        mrack command
Requires:       python3-%{name}lib == %{version}-%{release}

%package -n     python3-%{name}lib
Summary:        Core mrack libraries
Requires:       python3-click
Requires:       python3-pyyaml
Requires:       sshpass

%package -n     python3-%{name}-aws
Summary:        AWS provider plugin for mrack
Requires:       python3-%{name}lib == %{version}-%{release}
Requires:       python3-boto3
Requires:       python3-botocore

%package -n     python3-%{name}-beaker
Summary:        Beaker provider plugin for mrack
Requires:       python3-%{name}lib == %{version}-%{release}
Requires:       beaker-client

%package -n     python3-%{name}-openstack
Summary:        Openstack provider plugin for mrack
Requires:       python3-%{name}lib == %{version}-%{release}
Recommends:     python3-AsyncOpenStackClient

%package -n     python3-%{name}-podman
Summary:        Podman provider plugin for mrack
Requires:       python3-%{name}lib == %{version}-%{release}
Requires:       podman

%package -n     python3-%{name}-virt
Summary:        Virtualization provider plugin for mrack using testcloud
Requires:       python3-%{name}lib == %{version}-%{release}
Requires:       testcloud

%description        cli
%{name}-cli contains mrack command which functionality can be extended by installing mrack plugins

%description -n     python3-%{name}lib
python3-%{name}lib contains core mrack functionalities and static provider which can be used as a library

%description -n     python3-%{name}-aws
%{name}-aws is an additional plugin with AWS provisioning library extending mrack package

%description -n     python3-%{name}-beaker
%{name}-beaker is an additional plugin with Beaker provisioning library extending mrack package

%description -n     python3-%{name}-openstack
%{name}-openstack is an additional plugin with OpenStack provisioning library extending mrack package

%description -n     python3-%{name}-podman
%{name}-podman is an additional plugin with Podman provisioning library extending mrack package

%description -n     python3-%{name}-virt
%{name}-virt is an additional plugin with Virualization provisioning library extending mrack package using testcloud

%prep
%autosetup -p1 -n %{name}-%{version}
# Remove bundled egg-info
rm -rf %{name}.egg-info

%build
%py3_build

%install
%py3_install

%files
%license LICENSE
%doc README.md

%files cli
%license LICENSE
%doc README.md
%{_bindir}/%{name}

%files -n python3-%{name}lib
%license LICENSE
%doc README.md
%{python3_sitelib}/%{name}
%{python3_sitelib}/%{name}-%{version}-py%{python3_version}.egg-info
%exclude %{python3_sitelib}/%{name}/providers/utils/{,__pycache__/}osapi.py
%exclude %{python3_sitelib}/%{name}/providers/{,__pycache__/}{%{provider_plugins}}.*
%exclude %{python3_sitelib}/%{name}/transformers/{,__pycache__/}{%{provider_plugins}}.*

%files -n python3-%{name}-aws
%{python3_sitelib}/%{name}/providers/{,__pycache__/}aws.*
%{python3_sitelib}/%{name}/transformers/{,__pycache__/}aws.*

%files -n python3-%{name}-beaker
%{python3_sitelib}/%{name}/providers/{,__pycache__/}beaker.*
%{python3_sitelib}/%{name}/transformers/{,__pycache__/}beaker.*

%files -n python3-%{name}-openstack
%{python3_sitelib}/%{name}/providers/utils/{,__pycache__/}osapi.py
%{python3_sitelib}/%{name}/providers/{,__pycache__/}openstack.*
%{python3_sitelib}/%{name}/transformers/{,__pycache__/}openstack.*

%files -n python3-%{name}-podman
%{python3_sitelib}/%{name}/providers/{,__pycache__/}podman.*
%{python3_sitelib}/%{name}/transformers/{,__pycache__/}podman.*

%files -n python3-%{name}-virt
%{python3_sitelib}/%{name}/providers/{,__pycache__/}virt.*
%{python3_sitelib}/%{name}/transformers/{,__pycache__/}virt.*

%changelog
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
