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

"""Module for working with podman."""

import asyncio
import json
import logging
import subprocess

from mrack.errors import ProvisioningError

logger = logging.getLogger(__name__)


class Podman:
    """Async wrapper supporting most basic podman calls."""

    def __init__(self, program="podman"):
        """Init the instance."""
        self.program = program

    async def _run_podman(self, args, raise_on_err=True):
        """Util method to execute podman process."""
        process = await asyncio.create_subprocess_exec(
            self.program,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if stdout:
            stdout = stdout.decode()
        if stdout is None:
            stdout = ""
        if stderr:
            stderr = stderr.decode()
        if stdout is None:
            stderr = ""
        if process.returncode != 0 and raise_on_err:
            raise ProvisioningError(stderr)
        return stdout, stderr, process

    async def run(self, image, hostname=None, network=None):
        """Run a container."""
        args = ["run", "-dti"]
        if hostname:
            args.extend(["-h", hostname])
        if network:
            args.extend(["--network", network])
        args.append(image)

        stdout, _stderr, _process = await self._run_podman(args)
        container_id = stdout.strip()
        return container_id

    async def inspect(self, container_id):
        """Inspects a container returns data loaded from JSON structure."""
        args = ["inspect", container_id]
        stdout, _stderr, _process = await self._run_podman(args)
        inspect_data = json.loads(stdout)
        return inspect_data

    async def rm(self, container_id, force=False):  # pylint: disable=invalid-name
        """Remove a container."""
        args = ["rm"]
        if force:
            args.append("-f")
        args.append(container_id)
        _stdout, _stderr, process = await self._run_podman(args, raise_on_err=False)
        return process.returncode == 0

    def interactive(self, container_id):
        """Create interactive session."""
        args = [self.program, "exec", "-ti", container_id, "bash"]
        subprocess.run(args, text=True, check=True)
