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

"""Provisioning errors."""


class MrackError(Exception):
    """Base mrack error."""

    pass


class ConfigError(MrackError):
    """Error in configuration."""

    pass


class ApplicationError(MrackError):
    """General application error."""

    pass


class MetadataError(MrackError):
    """Error in job metadata."""

    pass


class ProviderNotExists(ConfigError):
    """Request provider does not exist."""

    def __init__(self, name):
        """Init the error with provider name."""
        self._provider_name = name


class ProvisioningConfigError(ConfigError):
    """Error in provisioning configuration."""

    pass


class JobConfigError(ConfigError):
    """Error in job configuration."""

    pass


class ValidationError(MrackError):
    """Error found in validation of values."""

    pass


class ProviderError(MrackError):
    """General provider error."""

    pass


class ServerNotFoundError(ProviderError):
    """Provider doesn't know the specified server."""

    pass


class ProvisioningError(ProviderError):
    """Error happened during provisioning of resources."""

    pass


class NotAuthenticatedError(ProviderError):
    """Provided is not authenticated."""

    pass
