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

"""Provisioning transformers.

Transformers take job definitions, combine it with provisioning configuration
and returns provisioning requirements (input for provisioners).
"""

import logging
from typing import Set, Tuple, Type

from mrack.errors import ProviderNotExists
from mrack.transformers.transformer import Transformer

NAME = 0
CLASS = 1
installed_transformers: Set[Tuple[str, Type[Transformer]]] = set()
IMPORT_ERR_TEMPLATE = "Transformer '%s' not installed, skipping registration"
logger = logging.getLogger(__name__)

try:
    from mrack.transformers.aws import CONFIG_KEY as AWS_KEY
    from mrack.transformers.aws import AWSTransformer

    installed_transformers.add((AWS_KEY, AWSTransformer))
except ModuleNotFoundError as import_err:
    logger.debug(IMPORT_ERR_TEMPLATE, import_err.name)

try:
    from mrack.transformers.beaker import CONFIG_KEY as BEAKER_KEY
    from mrack.transformers.beaker import BeakerTransformer

    installed_transformers.add((BEAKER_KEY, BeakerTransformer))
except ModuleNotFoundError as import_err:
    logger.debug(IMPORT_ERR_TEMPLATE, import_err.name)

try:
    from mrack.transformers.openstack import CONFIG_KEY as OPENSTACK_KEY
    from mrack.transformers.openstack import OpenStackTransformer

    installed_transformers.add((OPENSTACK_KEY, OpenStackTransformer))
except ModuleNotFoundError as import_err:
    logger.debug(IMPORT_ERR_TEMPLATE, import_err.name)

try:
    from mrack.transformers.podman import CONFIG_KEY as PODMAN_KEY
    from mrack.transformers.podman import PodmanTransformer

    installed_transformers.add((PODMAN_KEY, PodmanTransformer))
except ModuleNotFoundError as import_err:
    logger.debug(IMPORT_ERR_TEMPLATE, import_err.name)

try:
    from mrack.transformers.static import CONFIG_KEY as STATIC_KEY
    from mrack.transformers.static import StaticTransformer

    installed_transformers.add((STATIC_KEY, StaticTransformer))
except ModuleNotFoundError as import_err:
    logger.debug(IMPORT_ERR_TEMPLATE, import_err.name)

try:
    from mrack.transformers.virt import CONFIG_KEY as VIRT_KEY
    from mrack.transformers.virt import VirtTransformer

    installed_transformers.add((VIRT_KEY, VirtTransformer))
except ModuleNotFoundError as import_err:
    logger.debug(IMPORT_ERR_TEMPLATE, import_err.name)


class Registry:
    """Transformers registry."""

    def __init__(self):
        """Initialize transformer registry."""
        self._transformer_cls = {}
        self._transformers = {}

    def register(self, name, transformer_cls):
        """Register new tranformer class."""
        self._transformer_cls[name] = transformer_cls

    def get(self, name):
        """Get Transformer instance by name.

        Initialize the the transformer if not done yet.
        """
        trans_cls = self._transformer_cls.get(name)
        if not trans_cls:
            raise ProviderNotExists(f"Transformer '{name}' doesn't exist")
        transformer = self._transformers.get(name)
        if not transformer:
            transformer = trans_cls()
            self._transformers[name] = transformer
        return transformer

    @property
    def names(self):
        """Get all registered transformer names."""
        return self._transformer_cls.keys()


transformers = Registry()

for installed_transformer in installed_transformers:
    transformers.register(
        installed_transformer[NAME],
        installed_transformer[CLASS],
    )
