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

from .dbdrivers.file import FileDBDriver
from .utils import load_json, print_obj
from .config import ProvisioningConfig
from .actions.destroy import Destroy
from .actions.up import Up
from .providers import providers
from .providers.openstack import OpenStackProvider, KEY as OPENSTACK_KEY


def init_providers():
    """Register all providers usable in this session."""
    providers.register(OPENSTACK_KEY, OpenStackProvider)


def init_db(path):
    """Initialize file database."""
    db = FileDBDriver(path)
    return db


def init_config(path):
    """Load and initialize provisioning configuration."""
    config_data = load_json(path)
    config = ProvisioningConfig(config_data)
    return config


def init_metadata(path):
    """Load and initialize job metadata."""
    metadata_data = load_json(path)
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
    ctx[DB] = init_db(db)
    ctx[CONFIG] = init_config(config)


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


def run():
    """Run the app."""
    asyncio.run(aiohabitcli(obj={}))


if __name__ == "__main__":
    run()
