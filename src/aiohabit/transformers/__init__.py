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

from aiohabit.errors import ProviderNotExists
from aiohabit.transformers.openstack import (
    OpenStackTransformer,
    CONFIG_KEY as OPENSTACK_KEY,
)
from aiohabit.transformers.aws import AWSTransformer, CONFIG_KEY as AWS_KEY
from aiohabit.transformers.static import StaticTransformer, CONFIG_KEY as STATIC_KEY


class Registry:
    """Transformers registry."""

    def __init__(self):
        """Initialize transformer registry."""
        self._transformer_cls = dict()
        self._transformers = dict()

    def register(self, name, transformer_cls):
        """Register new tranformer class."""
        self._transformer_cls[name] = transformer_cls

    def get(self, name):
        """Get Transformer instance by name.

        Initialize the the transformer if not done yet.
        """
        trans_cls = self._transformer_cls.get(name)
        if not trans_cls:
            raise ProviderNotExists(name)
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
transformers.register(OPENSTACK_KEY, OpenStackTransformer)
transformers.register(AWS_KEY, AWSTransformer)
transformers.register(STATIC_KEY, StaticTransformer)
