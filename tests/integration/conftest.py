import os
import shutil
import socket
import tempfile
from pathlib import Path

import pytest
import yaml

from mrack.dbdrivers.file import FileDBDriver


@pytest.fixture
def datadir(request):
    return Path(os.path.dirname(request.module.__file__), "data")


@pytest.fixture()
def provisioning_config(datadir):
    data = (datadir / "provisioning-config.yaml").read_text()
    return yaml.safe_load(data)


@pytest.fixture()
def provisioning_config_file(datadir):
    return os.path.join(datadir, "provisioning-config.yaml")


@pytest.fixture()
def metadata(datadir):
    data = (datadir / "metadata-hosts.yaml").read_text()
    return yaml.safe_load(data)


@pytest.fixture(scope="class")
def database():
    tmpdir = tempfile.mkdtemp()
    return FileDBDriver(os.path.join(tmpdir, ".mrackdb.json"))


@pytest.fixture
def cleandir():
    old_cwd = os.getcwd()
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)
    yield
    os.chdir(old_cwd)
    shutil.rmtree(newpath)


@pytest.fixture
def mock_gethostbyaddr(monkeypatch):
    """
    Mock gethostbyaddr function from socket module.

    It returns only IP address as if the DNS resolution would fail - which it does
    for test data anyway.

    This is to speed up the tests
    """

    def gethostbyaddr(ip_address):
        return [ip_address, [], []]

    monkeypatch.setattr(socket, "gethostbyaddr", gethostbyaddr)
