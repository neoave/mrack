import json
import os
import shutil
import tempfile


def test_dir_path():
    return os.path.dirname(os.path.realpath(__file__))


def get_data(name, data_dir="data"):
    path = os.path.join(test_dir_path(), data_dir, name)
    with open(os.path.expanduser(path), "r") as file_data:
        data = json.load(file_data)
    return data


def copy_as_temp(data_path, text=True):
    """
    Makes a temporary copy of file relative to test dir and return it file path.
    """
    source_path = os.path.join(test_dir_path(), data_path)
    temp_fp, temp_path = tempfile.mkstemp(text=text)
    shutil.copy(source_path, temp_path)
    return temp_path
