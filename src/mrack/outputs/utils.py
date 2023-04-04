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

"""Utility functions for output modules."""

import copy
import socket
from socket import error as socket_error

from mrack.utils import find_value_in_config_hierarchy


def resolve_hostname(ip_addr):
    """Resolve IP address to hostname."""
    try:
        return socket.gethostbyaddr(ip_addr)[0]
    except socket_error:
        return None


def get_external_id(host, meta_host, config):
    """
    Get host's external ID.

    That can be its resolvable DNS name (from IP) or the IP - based on provider or
    host configuration (key: resolve_host, default True).

    IP is used as fallback if the desired is not available.
    """
    resolve_ip = find_value_in_config_hierarchy(
        config, host.provider.name, host, meta_host, "resolve_host", None, None, True
    )

    external_id = host.ip_addr
    if resolve_ip:
        external_id = resolve_hostname(host.ip_addr) or host.ip_addr
    return external_id


def merge_dict(d1, d2):
    """
    Merge two nested dictionaries together.

    Nested dictionaries are not overwritten but combined.
    """
    dest = copy.deepcopy(d1)
    for key, value in d2.items():
        if isinstance(value, dict):
            dest[key] = merge_dict(dest.get(key, {}), value)
            continue

        dest[key] = value

    return dest
