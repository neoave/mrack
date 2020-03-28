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
)
