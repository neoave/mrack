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

"""Provisioning providers.

Providers provisions resources in Clouds or other means based on provisioning
requirements (e.g. host requirements)
"""

from mrack.errors import ProviderNotExists


class Registry:
    """Provider registry."""

    def __init__(self):
        """Initialize Registry."""
        self._provider_cls = {}
        self._providers = {}

    def register(self, name, provider_cls):
        """Register new provider."""
        self._provider_cls[name] = provider_cls

    def get(self, name):
        """Get a provider object by name.

        Instantiate the provider if not done yet.

        Raises: ProviderNotExists
        """
        prov_cls = self._provider_cls.get(name)
        if not prov_cls:
            raise ProviderNotExists(f"Provider '{name}' doesn't exist")
        provider = self._providers.get(name)
        if not provider:
            provider = prov_cls()
            self._providers[name] = provider
        return provider

    @property
    def names(self):
        """Get all registered provider names."""
        return self._provider_cls.keys()


providers = Registry()
# registersing in run.py init_providers()
