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

"""Up action module."""

import asyncio
import logging

from mrack.errors import MetadataError
from mrack.providers import providers
from mrack.transformers import transformers
from mrack.utils import global_context, validate_dict_attrs

logger = logging.getLogger(__name__)


class Up:
    """
    Up action.

    UP action provision all hosts defined in domain object of provided job
    metadata.

    The provisioning information is created by transformers from metadata
    and provisioning configuration (config).

    Results of provisioning is saved by 'db_driver'.

    Output objects generate the resulting output artifacts, e.g. Ansible
    inventory.
    """

    async def init(self, config, metadata, default_provider, db_driver):
        """Initialize the Up action."""
        self._transformers = {}

        self._config = config
        self._metadata = metadata
        self._db_driver = db_driver
        self._required_domain_attrs = ["name", "hosts"]

        global_context["metadata"] = metadata
        global_context["config"] = config

        self.validate_topology()
        default_provider_name = self._config.get("provider", default_provider)
        default_provider_name = self._metadata.get("provider", default_provider_name)
        for domain in self._metadata["domains"]:
            for host in domain["hosts"]:
                provider_name = host.get("provider", default_provider_name)
                transformer = await self._get_transformer(provider_name)
                transformer.validate_host(host)
                transformer.add_host(host)

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

    def validate_topology(self):
        """Validate topology part of job metadata.

        Raises: MetadataError
        """
        if "domains" not in self._metadata:
            error = (
                "Error: job metadata file doesn't contain required "
                "`domains` definition"
            )
            raise MetadataError(error)
        for domain in self._metadata["domains"]:
            validate_dict_attrs(domain, self._required_domain_attrs, "domain")

    async def provision(self):
        """Execute the up action."""
        logger.info("Provisioning started")
        prov_aws = []
        for provider_name, transformer in self._transformers.items():
            reqs = transformer.create_host_requirements()
            provider = providers.get(provider_name)
            awaitable = provider.provision_hosts(reqs)
            prov_aws.append(awaitable)
        provisioning_results = await asyncio.gather(*prov_aws)
        hosts = []
        for results in provisioning_results:
            hosts.extend(results)

        self._db_driver.add_hosts(hosts)
        logger.info("Provisioning done")
        return hosts
