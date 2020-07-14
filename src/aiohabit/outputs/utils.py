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

import socket
from socket import error as socket_error


def resolve_hostname(ip):
    """Resolve IP address to hostname."""
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket_error:
        return None


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
