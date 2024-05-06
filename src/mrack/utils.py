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


"""Module with utility and helper functions."""

import asyncio
import base64
import contextlib
import datetime
import json
import logging
import os
import subprocess
import sys
from functools import wraps
from xml.dom.minidom import Document as xml_doc

import yaml

from mrack.errors import ConfigError, ProvisioningError

logger = logging.getLogger(__name__)

DEFAULT_SSH_OPTIONS = {
    "StrictHostKeyChecking": "no",
    "UserKnownHostsFile": "/dev/null",
}


def value_to_bool(value):
    """Convert Python variable value to boolean."""
    _false_set = {"no", "false", "f", "n", "0"}
    _true_set = {"yes", "true", "t", "y", "1"}
    if isinstance(value, str):
        if value.lower() in _true_set:
            return True

        if value.lower() in _false_set:
            return False

        raise ValueError(
            f"Invalid input string for boolean conversion '{value}',"
            "supported values are:\n"
            f"False:\t{_true_set}\n"
            f"True:\t{_false_set}"
        )

    return bool(value)


def get_config_value(config_dict, key, default=None):
    """Get configuration value or default value from dictionary.

    Usable for dictionaries which can also contain attribute 'default'

    Order of preference:
    * attribute value
    * value of 'default' attribute
    * value of provided default param
    """
    val = config_dict.get(key)
    if val is None:
        val = config_dict.get("default", default)
    return val


def get_value_or_dict_value(config_dict, attr, dict_name, key):
    """
    Look for a value in configuration dictionary.

    Order of preference:
    * dictionary 'dict_name' with key 'key'
    * attribute: 'attr'
    * None
    """
    if config_dict is None:
        return None

    value = None
    if dict_name and key:
        value_dict = config_dict.get(dict_name)
        if value_dict:
            value = get_config_value(value_dict, key)
            if value:
                return value
        # avoid to return the whole value_dict if dict name is the same as attr
        if attr == dict_name:
            return None

    value = config_dict.get(attr)
    return value


def find_value_in_config_hierarchy(
    provisioning_config,
    provider_key,
    host,
    meta_host,
    attr,
    dict_name,
    key,
    default=None,
):
    """
    Look for first value in configuration hierarchy.

    Order of preference:
    * host value (attribute: attr)
    * host metadata value (attribute: 'attr')
    * provider config value (dictionary 'dict_name' with key 'key')
    * provider default value (attribute: 'attr')
    * global config value (dictionary 'dict_name' with key 'key')
    * global default value (attribute: 'attr')
    * value of provided default param
    """
    value = None
    if host is not None:
        if hasattr(host, attr):
            value = getattr(host, attr)

    if value is None and isinstance(meta_host, dict):
        value = meta_host.get(attr)

    if value is None and provider_key is not None:
        provider_config = provisioning_config.get(provider_key)
        value = get_value_or_dict_value(provider_config, attr, dict_name, key)

    if value is None:
        value = get_value_or_dict_value(provisioning_config, attr, dict_name, key)
    if value is None:
        value = default

    return value


def validate_dict_attrs(dct, attr_list, dct_name):
    """Validate that dictionary contains all attributes.

    Based on provided attribute list.
    """
    missing = [a for a in attr_list if a not in dct]
    if missing:
        error = f"""
        '{dct_name} definition:'
        {dct}
        'Is missing required attributes: {missing}'
        """
        raise ConfigError(error)


def add_dict_to_node(node, input_dict):
    """Convert dict object to XML elements."""
    # Recursively create xml from dict
    if isinstance(input_dict, dict):
        for key, value in input_dict.items():
            if isinstance(value, list):
                child_node = node.appendChild(xml_doc().createElement(key))
                for child_value in value:
                    for k, v in child_value.items():
                        child_node.appendChild(
                            add_dict_to_node(xml_doc().createElement(k), v)
                        )
            else:
                if key.startswith("_"):
                    node.setAttribute(key[1:], str(value))
                else:
                    node.appendChild(
                        add_dict_to_node(xml_doc().createElement(key), value)
                    )

    return node


def json_convertor(obj):
    """Convert object to be useable for json serialization.

    To be used in json.dumps as value for default= so that given object
    is serializable
    """
    if "Binary" in str(obj.__class__):
        return base64.b64encode(obj.data).decode("utf-8")

    if "DateTime" in str(obj.__class__):
        date = datetime.datetime.strptime(str(obj), "%Y%m%dT%H:%M:%S")
        return date.isoformat() + "Z"

    if "Decimal" in str(obj.__class__):
        return str(obj)

    # use string as default
    return str(obj)


def load_json(path):
    """Load JSON file into Python object."""
    with open(os.path.expanduser(path), "r", encoding="utf-8") as file_data:
        data = json.load(file_data)
    return data


def load_yaml(path):
    """Load YAML file into Python object."""
    with open(os.path.expanduser(path), "r", encoding="utf-8") as file_data:
        data = yaml.safe_load(file_data)
    return data


def save_to_json(path, data):
    """Serialize object into JSON file."""
    try:
        with open(os.path.expanduser(path), "w", encoding="utf-8") as output:
            json.dump(data, output, default=json_convertor, indent=2, sort_keys=True)
    except IOError as exc:
        logger.exception(exc)
        sys.exit(1)


@contextlib.contextmanager
def fd_open(filename=None):
    """Use file or stout as output file descriptor."""
    if filename:
        file_d = open(os.path.expanduser(filename), "w", encoding="utf-8")
    else:
        file_d = sys.stdout

    try:
        yield file_d
    finally:
        if file_d is not sys.stdout:
            file_d.close()


def save_yaml(path, yaml_data, **kwargs):
    """
    Write yaml data with file.write(yaml.dump()) to file specified by path.

    If path is not specified use stdout.
    """
    with fd_open(path) as yaml_file:
        yaml_file.write(yaml.dump(yaml_data, default_flow_style=False, **kwargs))


def object2json(obj):
    """Convert object to JSON string."""
    return json.dumps(obj, default=json_convertor, sort_keys=True, indent=4)


def print_obj(obj):
    """Print object as JSON."""
    logger.info(object2json(obj))


def get_host_from_metadata(metadata, name):
    """
    Get host definition from job metadata base on name.

    Returns:
    (host, domain)
    """
    domains = metadata.get("domains", [])
    for domain in domains:
        for host in domain.get("hosts", []):
            if host["name"] == name:
                return host, domain

    return None, None


def is_windows_host(meta_host):
    """
    Return if host is Windows host based on host metadata info.

    Host is windows host if:
    * os starts with 'win' or
    * os_type is 'windows'
    """
    return (
        meta_host.get("os", "").startswith("win")
        or meta_host.get("os_type", "") == "windows"
    )


def get_os_type(meta_host):
    """Get os type from ``os_type`` or infer it from ``os``."""
    os_type = meta_host.get("os_type")
    if not os_type:
        os_type = "linux" if not is_windows_host(meta_host) else "windows"

    return os_type


def get_shortname(hostname):
    """
    Get shortname part of fqdn.

    Return the same string if it is not fqdn.
    """
    return hostname.split(".")[0]


def get_fqdn(hostname, domain):
    """
    Get fqdn from hostname and domain.

    Return the hostname if it is fqdn otherwise append domain.
    """
    if "." in hostname:
        return hostname

    return f"{hostname}.{domain}"


def get_username(host, meta_host, config):
    """Find username from sources db/metadata/config."""
    provider = host.provider.name
    dict_key = meta_host["os"]
    default_user = None
    if is_windows_host(meta_host):
        default_user = "Administrator"
    username = find_value_in_config_hierarchy(
        config, provider, host, meta_host, "username", "users", dict_key, default_user
    )

    return username


def get_password(host, meta_host, config):
    """Find password from sources db/metadata/config."""
    password = host.password or meta_host.get("password")
    multihost_config = config.get("mhcfg")
    if is_windows_host(meta_host) and multihost_config:
        password = password or multihost_config.get("ad_admin_password")
    return password


def get_ssh_key(host, meta_host, config):
    """Find ssh_key path from sources: db/metadata/config."""
    ssh_key_attr = "ssh_key_filename"
    provider_config = config.get(host.provider.name, {})

    ssh_key = meta_host.get(ssh_key_attr)
    ssh_key = ssh_key or provider_config.get(ssh_key_attr)
    ssh_key = ssh_key or config.get(ssh_key_attr)
    return ssh_key


def get_username_pass_and_ssh_key(host, context):
    """Return username password and ssh_key to be later used for ssh connections."""
    meta_host, _domain = get_host_from_metadata(context.METADATA, host.name)
    username = get_username(host, meta_host, context.PROV_CONFIG)
    ssh_key = get_ssh_key(host, meta_host, context.PROV_CONFIG)
    password = None if ssh_key else get_password(host, meta_host, context.PROV_CONFIG)
    return username, password, ssh_key


def get_ssh_options(host, metadata, provisioning_config):
    """Get dictionary of SSH options and their values from configuration."""
    # try to get ssh dict
    meta_host = get_host_from_metadata(metadata, host.name)
    ssh = find_value_in_config_hierarchy(
        provisioning_config, host.provider, host, meta_host, "ssh", None, None, {}
    )

    options = ssh.get("options", DEFAULT_SSH_OPTIONS)

    return options


def ssh_options_to_cli(options):
    """Covert dictionary of SSH options into list of SSH CLI options."""
    cmd = []
    for option, value in options.items():
        cmd.extend(["-o", f"'{option}={value}'"])
    return cmd


def ssh_to_host(
    host,
    username=None,
    password=None,
    ssh_key=None,
    command=None,
    interactive=False,
    ssh_options={},
):
    """SSH to the selected host."""
    psw = host.password or password

    run_args = {
        "env": os.environ.copy(),
        "shell": True,
    }
    if not interactive:
        run_args.update(
            {
                "stdout": subprocess.PIPE,
                "stderr": subprocess.PIPE,
            }
        )

    cmd = ["ssh"]
    cmd.extend(ssh_options_to_cli(ssh_options))

    if psw:
        cmd.extend(["-o", "'PasswordAuthentication=yes'"])
        cmd = ["sshpass", "-p", psw] + cmd
    elif ssh_key:
        cmd.extend(["-o", "'PasswordAuthentication=no'"])
        cmd.extend(["-i", ssh_key])

    if username:
        cmd.extend(["-l", username])

    cmd.append(host.ip_addr)  # Destination

    if command:
        cmd.append(command)

    cmd = " ".join(cmd)

    logger.debug(f"Running: {cmd}")
    with subprocess.Popen(cmd, **run_args) as process:
        std_out, std_err = process.communicate()

    if not interactive:
        for o_line in std_out.decode().splitlines():
            logger.debug(f"stdout: {o_line}")

        for e_line in std_err.decode().splitlines():
            logger.debug(f"stderr: {e_line}")

    return process.returncode == 0


async def exec_async_subprocess(program, args, raise_on_err=True):
    """Util method to execute subprocess asynchronously."""
    process = await asyncio.create_subprocess_exec(
        program,
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if stdout:
        stdout = stdout.decode()
    if stdout is None:
        stdout = ""
    if stderr:
        stderr = stderr.decode()
    if stdout is None:
        stderr = ""
    if process.returncode != 0 and raise_on_err:
        raise ProvisioningError(stderr)
    return stdout, stderr, process


def async_run(func):
    """Decorate click actions to run as async."""

    @wraps(func)
    def update_wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return update_wrapper


class NoSuchFileHandler:
    """
    Decorator which change error into ConfigError with custom message.

    error string can contain {path} template.
    """

    def __init__(self, error):
        """Initialize decorator."""
        self.error = error

    def __call__(self, func):
        """Transform FileNotFoundError into ConfigError."""

        def wrapped_f(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except FileNotFoundError as file_error:
                raise ConfigError(
                    self.error.format(path=file_error.filename)
                ) from file_error

        return wrapped_f
