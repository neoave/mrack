import os
import shutil
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
