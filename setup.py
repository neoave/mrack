# Copyright 2020 Red Hat Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""mrack setup"""
# -*- coding: utf-8 -*-
import re
import sys

from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

with open("requirements.txt", encoding="utf-8") as req:
    reqs = req.readlines()

with open("src/mrack/version.py", "r", encoding="utf-8") as fd:
    version = re.search(r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE)
    if version is None:
        sys.stderr.write("Could not parse the version string.\n")
        sys.exit(1)

    mrack_version = version.group(1)


MRACK_CONF = "mrack.conf"
PROV_CONF = "provisioning-config.yaml"
SECCOMP_JSON = "seccomp.json"

setup(
    name="mrack",
    version=mrack_version,
    description="Multicloud use-case based multihost async provisioner "
    "for CIs and testing during development",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Petr Vobornik",
    maintainer="Red Hat IdM-Ops team",
    maintainer_email="idmops@redhat.com",
    url="https://github.com/neoave/mrack",
    license="Apache License 2.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=reqs,
    scripts=["scripts/mrack"],
    package_data={
        "mrack": [
            f"data/{datafile}" for datafile in [MRACK_CONF, PROV_CONF, SECCOMP_JSON]
        ]
    },
    extras_require={
        "krb-owner": ["gssapi"],
    },
)
