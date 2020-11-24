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

import asyncio
import logging

from mrack.errors import MetadataError
from mrack.host import STATUS_DELETED
from mrack.transformers import transformers

logger = logging.getLogger(__name__)


class Destroy:
    """Destroy action.

    Destroy all still active provisioned host. Save the state to DB.
    """

    async def init(self, config, metadata, db_driver):
        """Initialize the destroy action."""
        self._config = config
        self._metadata = metadata
        self._db_driver = db_driver
        self._transformers = {}

    async def destroy(self):
        """Execute the destroy action."""
        hosts = self._db_driver.hosts.values()
        to_del = [host for host in hosts if host.status != STATUS_DELETED]
        names = [host.name for host in to_del]
        names = ", ".join(names)
        logger.info(f"Hosts to delete: {names}")

        await self.init_providers(to_del)
        results_aws = []

        for host in to_del:
            logger.info(f"Deleting host: {host}")
            awaitable = host.delete()
            results_aws.append(awaitable)
        delete_results = await asyncio.gather(*results_aws)
        success = all(delete_results)
        self._db_driver.update_hosts(hosts)
        logger.info("Destroy done")
        return success

    async def init_providers(self, hosts):
        """Initialize providers for hosts to delete."""
        providers = [host.provider.name for host in hosts]
        providers = set(providers)
        aws = [self._get_transformer(provider) for provider in providers]
        await asyncio.gather(*aws)

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
