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

"""Destroy action module."""

import logging

from mrack.context import global_context
from mrack.errors import MetadataError
from mrack.transformers import transformers

logger = logging.getLogger(__name__)


class Action:
    """Base Action."""

    def __init__(self, config=None, metadata=None, db_driver=None):
        """Initialize the action."""
        self._config = config or global_context.PROV_CONFIG
        self._metadata = metadata or global_context.METADATA
        self._db_driver = db_driver or global_context.DB
        self._transformers = {}

    async def _get_transformer(self, provider_name):
        """Get a transformer by name, initialize a new one if not yet done."""
        transformer = self._transformers.get(provider_name)
        if not transformer:
            transformer = transformers.get(provider_name)
            await transformer.init(self._config, self._metadata)
            if not transformer:
                raise MetadataError(f"Invalid provider: {provider_name}")
            self._transformers[provider_name] = transformer
        return transformer


class DBAction:
    """Base Action."""

    def __init__(
        self,
        db_driver=None,
    ):
        """Initialize the database action."""
        self._db_driver = db_driver or global_context.DB
