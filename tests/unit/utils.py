import json
import os


def test_dir_path():
    return os.path.dirname(os.path.realpath(__file__))


def get_data(name, data_dir="data"):
    path = os.path.join(test_dir_path(), data_dir, name)
    with open(path, "r") as file_data:
        data = json.load(file_data)
    return data
