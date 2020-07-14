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

"""Output action."""

from aiohabit.outputs.ansible_inventory import AnsibleInventoryOutput
from aiohabit.outputs.pytest_multihost import PytestMultihostOutput


class Output:
    """
    Output action.

    Test action to run output modules from data in database.
    """

    async def init(self, config, metadata, db_driver):
        """Initialize the Output action."""
        self._config = config
        self._metadata = metadata
        self._db_driver = db_driver

    async def generate_outputs(self):
        """Generate outputs."""
        ansible_o = AnsibleInventoryOutput(
            self._config, self._db_driver, self._metadata
        )
        multihost_o = PytestMultihostOutput(
            self._config, self._db_driver, self._metadata
        )

        ansible_o.create_output()
        multihost_o.create_output()

        print("Output generation done")
        return True
