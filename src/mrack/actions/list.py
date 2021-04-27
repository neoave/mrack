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

"""List action module."""
import logging

from mrack.actions.action import DBAction

logger = logging.getLogger(__name__)


class List(DBAction):
    """List action.

    List hosts from DB.
    """

    def list(self):
        """Execute the List action."""
        hosts = self._db_driver.hosts.values()

        for host in hosts:
            logger.info(host)
