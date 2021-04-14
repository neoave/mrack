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

    async def run(
        self,
        image,
        hostname=None,
        network=None,
        extra_options=None,
        remove_at_stop=False,
    ):
        """Run a container."""
        args = ["run", "-dti"]

        for opt in extra_options:
            if isinstance(extra_options[opt], list):
                for item in extra_options[opt]:
                    args.extend([opt, item])
            else:
                args.extend([opt, extra_options[opt]])

        if remove_at_stop:
            args.append("--rm")

        if network:
            args.extend(["--network", network])

        if hostname:
            args.extend(["-h", hostname])
            args.extend(["--name", hostname.split(".")[0]])

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

    async def stop(self, container_id, time=0):
        """Remove a container."""
        args = ["stop"]
        if time:
            args.append("--time")
            args.append(time)

        args.append(container_id)
        _stdout, _stderr, process = await self._run_podman(args, raise_on_err=False)
        return process.returncode == 0

    async def exec_command(self, container_id, command):
        """Execute command in selected container."""
        args = ["exec", container_id, "sh", "-c"]
        args.append(command)
        _stdout, _stderr, process = await self._run_podman(args, raise_on_err=False)
        return process.returncode == 0

    async def network_exists(self, network):
        """Check the existence of podman network on system using inspect command."""
        args = ["network", "inspect", network]
        _stdout, _stderr, inspect = await self._run_podman(args, raise_on_err=False)
        return inspect.returncode == 0

    async def network_create(self, network):
        """Create a podman network if it does not exist."""
        if await self.network_exists(network):
            logger.debug(f"Podman network '{network}' is present")
            return 0

        logger.info(f"Creating podman network {network}")
        args = ["network", "create", network]
        _stdout, _stderr, process = await self._run_podman(args, raise_on_err=False)

        return process.returncode == 0

    async def network_remove(self, network):
        """Remove a podman network if it does exist."""
        if not await self.network_exists(network):
            logger.debug(f"Podman network '{network}' does not exists")
            return 0

        logger.info(f"Removing podman network {network}")
        args = ["network", "remove", network]
        _stdout, _stderr, process = await self._run_podman(args, raise_on_err=False)

        return process.returncode == 0

    async def pull(self, image):
        """Pull a container image."""
        args = ["pull", image]
        _stdout, _stderr, process = await self._run_podman(args, raise_on_err=False)
        return process.returncode == 0

    async def image_exists(self, image):
        """Check if a container image exists in local storage."""
        args = ["image", "exists", image]
        _stdout, _stderr, process = await self._run_podman(args, raise_on_err=False)
        return process.returncode == 0

    def interactive(self, container_id):
        """Create interactive session."""
        args = [self.program, "exec", "-ti", container_id, "bash"]
        subprocess.run(args, text=True, check=True)
