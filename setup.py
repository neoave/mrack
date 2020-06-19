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

# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="aiohabit",
    version="0.1.0",
    description="Multicloud use-case based multihost async provisioner "
    "for CIs and testing during development",
    long_description=readme,
    author="Petr Vobornik",
    author_email="pvoborni@redhat.com",
    url="https://github.com/pvoborni/aiohabit",
    license=license,
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=["asyncopenstackclient"],
    scripts=["scripts/aiohabit"],
)