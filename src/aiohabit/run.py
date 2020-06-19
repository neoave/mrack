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

"""aiohabit default app."""

import asyncio
import click
import sys

from .dbdrivers.file import FileDBDriver
from .utils import load_yaml, print_obj, no_such_file_config_handler
from .config import ProvisioningConfig
from .actions.destroy import Destroy
from .actions.up import Up
from .providers import providers
from .providers.openstack import OpenStackProvider, KEY as OPENSTACK_KEY
from .errors import ConfigError, MetadataError, ValidationError, ProviderError


def init_providers():
    """Register all providers usable in this session."""
    providers.register(OPENSTACK_KEY, OpenStackProvider)


def init_db(path):
    """Initialize file database."""
    db = FileDBDriver(path)
    return db


@no_such_file_config_handler(error="Provisioning config file not found: {path}")
def init_config(path):
    """Load and initialize provisioning configuration."""
    config_data = load_yaml(path)
    config = ProvisioningConfig(config_data)
    return config


@no_such_file_config_handler(error="Job metadata file not found: {path}")
def init_metadata(path):
    """Load and initialize job metadata."""
    metadata_data = load_yaml(path)
    return metadata_data


DB = "db"
CONFIG = "config"
META = "metadata"


@click.group()
@click.option("-c", "--config", default="./provisioning-config.yaml")
@click.option("-d", "--db", default="./.aiohabitdb.json")
@click.pass_context
def aiohabitcli(ctx, config, db):
    """Multihost human friendly provisioner."""
    init_providers()
    ctx.ensure_object(dict)
    ctx.obj[DB] = init_db(db)
    ctx.obj[CONFIG] = init_config(config)


@aiohabitcli.command()
@click.pass_context
@click.argument("metadata")
@click.option("-p", "--provider", default="openstack")
async def up(ctx, metadata, provider):
    """Provision hosts.

    Based on provided job metadata file and provisioning configuration.
    """
    ctx[META] = init_metadata(metadata)
    up_action = Up(ctx[CONFIG], ctx[META], provider, ctx[DB])
    hosts = await up_action.provision()
    print_obj(hosts)


@aiohabitcli.command()
@click.pass_context
async def destroy(ctx):
    """Destroy provisioned hosts."""
    destroy_action = Destroy(ctx[CONFIG], ctx[DB])
    result = await destroy_action.destroy()
    print_obj(result)


def exception_handler(func):
    """
    Top level exception handler.

    For showing nice output to users if exception bubbles up to the top.
    """

    def handle(*args, **kwargs):
        """Handle exceptions."""
        rc = 1  # assuming error
        try:
            rc = func(*args, **kwargs)
        except (
            FileNotFoundError,
            ConfigError,
            MetadataError,
            ValidationError,
            ProviderError,
        ) as e:
            print(e, file=sys.stderr)
        except Exception as e:
            raise e
            # TODO: when logging support added: logger.error(e, exc_info=True)

        return rc

    return handle


@exception_handler
def run():
    """Run the app."""
    asyncio.run(aiohabitcli(obj={}))


if __name__ == "__main__":
    run()
