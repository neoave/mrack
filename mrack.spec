# Created by pyp2rpm-3.3.5
%global srcname mrack

Name:           %{srcname}
Version:        0.6.0
Release:        1%{?dist}
Summary:        Multicloud use-case based multihost async provisioner for CIs and testing during development

License:        Apache License 2.0
URL:            https://github.com/neoave/mrack
Source0:        https://github.com/neoave/mrack/releases/download/v%{version}/mrack-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-AsyncOpenStackClient
BuildRequires:  beaker-client
BuildRequires:  python3-boto3
BuildRequires:  python3-botocore
BuildRequires:  python3-click
BuildRequires:  python3-pyyaml
BuildRequires:  python3-setuptools

%description
mrack is a provisioning library for CI and local multi-host testing supporting multiple
provisioning providers (e.g. OpenStack, Beaker). But in comparison to other multi-cloud
libraries, the aim is to be able to describe host from application perspective.

%{?python_provide:%python_provide %{srcname}}

Requires:       python3-AsyncOpenStackClient
Requires:       beaker-client
Requires:       python3-boto3
Requires:       python3-botocore
Requires:       python3-click
Requires:       python3-pyyaml

%prep
%autosetup -n %{srcname}-%{version}
# Remove bundled egg-info
rm -rf %{srcname}.egg-info

%build
%py3_build

%install
%py3_install

%files -n %{srcname}
%license LICENSE
%doc README.md
%{_bindir}/mrack
%{python3_sitelib}/%{srcname}
%{python3_sitelib}/%{srcname}-%{version}-py%{python3_version}.egg-info

%changelog
* Thu Feb 04 2021 Armando Neto <abiagion@redhat.com> - 0.6.0-1
- Initial package.
