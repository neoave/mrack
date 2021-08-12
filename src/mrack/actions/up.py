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

from mrack.errors import MetadataError, ProvisioningError
from mrack.providers import providers
from mrack.transformers import transformers
from mrack.utils import global_context, validate_dict_attrs

PROVIDER_NAME_INDEX = 1

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

        provisioning_results = await asyncio.gather(*prov_aws, return_exceptions=True)

        success_hosts = []
        failed_providers = []
        for results in provisioning_results:
            if isinstance(results, ProvisioningError):
                # in this case some of any provider fails to provision
                # we need to cleanup all the remaining resources
                # even when provisioned successfully
                failed_providers.append(results.args[PROVIDER_NAME_INDEX])
                continue

            if isinstance(results, Exception):
                logger.error("An unexpected exception occurred while provisioning")
                raise results

            success_hosts.extend(results)

        if failed_providers and success_hosts:
            # if there is successfully provisioned resource do a cleanup
            logger.info(
                "Issuing deletion of all successfully provisioned resources "
                " due to provisioning error"
            )
            cleanup = [h.delete() for h in success_hosts]
            cleanup_res = await asyncio.gather(*cleanup)
            if all(cleanup_res):
                logger.info(
                    "All successfully provisioned resources issued to be deleted"
                )
            else:
                logger.error(
                    "Failed to destroy some of provisioned resources, "
                    "manual destroy of resources might be needed"
                )

        if failed_providers:
            failed_prov = ", ".join(failed_providers)
            raise ProvisioningError(
                f"Provider(s) {failed_prov} failed to provision resources"
            )

        self._db_driver.add_hosts(success_hosts)
        logger.info("Provisioning done")
        return success_hosts
