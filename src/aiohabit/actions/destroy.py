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
from ..host import STATUS_DELETED


class Destroy:
    """Destroy action.

    Destroy all still active provisioned host. Save the state to DB.
    """

    def __init__(self, config, metadata, db_driver):
        """Initialize the destroy action."""
        self._config = config
        self._metadata = metadata
        self._db_driver = db_driver

    async def destroy(self):
        """Execute the destroy action."""
        hosts = self._db_driver.hosts
        results_aws = []
        for host in hosts.values():
            if host.status == STATUS_DELETED:
                continue
            aw = host.delete()
            results_aws.append(aw)
        delete_results = await asyncio.gather(*results_aws)
        success = all(delete_results)
        self._db_driver.update_hosts(hosts)
        return success
