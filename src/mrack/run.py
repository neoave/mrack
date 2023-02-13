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

"""mrack default app."""
#  pylint: disable=no-name-in-module
import logging
import sys
from typing import Set, Tuple, Type

import click

from mrack.actions.destroy import Destroy
from mrack.actions.etchosts import EtcHostsUpdate
from mrack.actions.list import List
from mrack.actions.output import Output
from mrack.actions.ssh import SSH
from mrack.actions.up import Up
from mrack.context import GlobalContext, global_context
from mrack.errors import ApplicationError, MrackError
from mrack.providers import providers
from mrack.providers.provider import Provider
from mrack.utils import async_run
from mrack.version import VERSION

PROVIDER_NAME = 0
PROVIDER_CLASS = 1
installed_providers: Set[Tuple[str, Type[Provider]]] = set()
logger = logging.getLogger(__name__)
IMPORT_ERR_TEMPLATE = "Provider '%s' not installed, skipping provider registration"


try:
    from mrack.providers.aws import PROVISIONER_KEY as AWS
    from mrack.providers.aws import AWSProvider

    installed_providers.add((AWS, AWSProvider))
except ModuleNotFoundError as err:
    logger.debug(IMPORT_ERR_TEMPLATE, err.name)

try:
    from mrack.providers.beaker import PROVISIONER_KEY as BEAKER
    from mrack.providers.beaker import BeakerProvider

    installed_providers.add((BEAKER, BeakerProvider))
except ModuleNotFoundError as err:
    logger.debug(IMPORT_ERR_TEMPLATE, err.name)

try:
    from mrack.providers.openstack import PROVISIONER_KEY as OPENSTACK
    from mrack.providers.openstack import OpenStackProvider

    installed_providers.add((OPENSTACK, OpenStackProvider))
except ModuleNotFoundError as err:
    logger.debug(IMPORT_ERR_TEMPLATE, err.name)

try:
    from mrack.providers.podman import PROVISIONER_KEY as PODMAN
    from mrack.providers.podman import PodmanProvider

    installed_providers.add((PODMAN, PodmanProvider))
except ModuleNotFoundError as err:
    logger.debug(IMPORT_ERR_TEMPLATE, err.name)

try:
    from mrack.providers.static import PROVISIONER_KEY as STATIC
    from mrack.providers.static import StaticProvider

    installed_providers.add((STATIC, StaticProvider))
except ModuleNotFoundError as err:
    logger.debug(IMPORT_ERR_TEMPLATE, err.name)

try:
    from mrack.providers.virt import PROVISIONER_KEY as VIRT
    from mrack.providers.virt import VirtProvider

    installed_providers.add((VIRT, VirtProvider))
except ModuleNotFoundError as err:
    logger.debug(IMPORT_ERR_TEMPLATE, err.name)


def init_providers():
    """Register all providers usable in this session."""
    if not installed_providers:
        raise ApplicationError("FATAL: mrack did not find any installed providers")

    for installed_provider in installed_providers:
        providers.register(
            installed_provider[PROVIDER_NAME],
            installed_provider[PROVIDER_CLASS],
        )

    logger.info(f"Installed providers: {', '.join(providers.names)}")


async def generate_outputs(ctx):
    """Init and run output action."""
    config = ctx.obj.CONFIG
    output_action = Output(
        ctx.obj.PROV_CONFIG,
        ctx.obj.METADATA,
        ctx.obj.DB,
        config.ansible_inventory_path(),
        config.pytest_multihost_path(),
        config.pytest_mh_path(),
    )
    await output_action.generate_outputs()


@click.group()
@click.option("-c", "--mrack-config", type=click.Path(exists=True))
@click.option("-p", "--provisioning-config", type=click.Path(exists=True))
@click.option("-d", "--db", "db_file")  # db file may not exist
@click.option("--debug", default=False, is_flag=True)
@click.version_option(version=VERSION)
@click.pass_context
def mrackcli(ctx, mrack_config, provisioning_config, db_file, debug):
    """Multihost human friendly provisioner."""
    if debug:
        logging.getLogger("mrack").setLevel(logging.DEBUG)

    init_providers()
    ctx.ensure_object(GlobalContext)
    global_context.init(mrack_config, provisioning_config, db_file)
    ctx.obj = global_context


@mrackcli.command()
@click.pass_context
@click.option("-m", "--metadata", type=click.Path(exists=True))
@click.option("-p", "--provider", default="openstack")
@async_run
async def up(ctx, metadata, provider):  # pylint: disable=invalid-name
    """Provision hosts.

    Based on provided job metadata file and provisioning configuration.
    """
    ctx.obj.init_metadata(metadata)

    up_action = Up(ctx.obj.PROV_CONFIG, ctx.obj.METADATA, ctx.obj.DB)
    await up_action.init(provider)
    await up_action.provision()

    await generate_outputs(ctx)


@mrackcli.command()
@click.pass_context
@click.option("-m", "--metadata", type=click.Path(exists=True))
@async_run
async def destroy(ctx, metadata):
    """Destroy provisioned hosts."""
    ctx.obj.init_metadata(metadata)
    destroy_action = Destroy(ctx.obj.PROV_CONFIG, ctx.obj.METADATA, ctx.obj.DB)
    await destroy_action.destroy()


@mrackcli.command()
@click.pass_context
@click.option("-m", "--metadata", type=click.Path(exists=True))
@async_run
async def output(ctx, metadata):
    """Create outputs - such as Ansible inventory."""
    ctx.obj.init_metadata(metadata)
    await generate_outputs(ctx)


@mrackcli.command()
@click.pass_context
@async_run
async def list(ctx):  # pylint: disable=redefined-builtin
    """List host tracked by."""
    list_action = List(ctx.obj.DB)
    list_action.list()


@mrackcli.command()
@click.pass_context
@click.argument("hostname", required=False)
@click.option("-m", "--metadata", type=click.Path(exists=True))
@async_run
async def ssh(ctx, hostname, metadata):
    """SSH to host."""
    ctx.obj.init_metadata(metadata)
    ssh_action = SSH(ctx.obj.PROV_CONFIG, ctx.obj.METADATA, ctx.obj.DB)
    return ssh_action.ssh(hostname)


@mrackcli.group()
def eh():  # pylint: disable=invalid-name
    """Commands to update /etc/hosts file."""


@eh.command()
@click.pass_context
def add(ctx):
    """Add active hosts to /etc/hosts file."""
    eh_action = EtcHostsUpdate(ctx.obj.DB)
    eh_action.update()


@eh.command()
@click.pass_context
def clear(ctx):
    """Remove all mrack hosts from /etc/hosts file."""
    eh_action = EtcHostsUpdate(ctx.obj.DB)
    eh_action.clear()


def exception_handler(func):
    """
    Top level exception handler.

    For showing nice output to users if exception bubbles up to the top.
    """

    def handle(*args, **kwargs):
        """Handle exceptions."""
        ret_code = 1  # assuming error
        try:
            ret_code = func(*args, **kwargs)
        except (
            FileNotFoundError,
            MrackError,
        ) as known_error:
            logger.error(known_error)
            sys.exit(1)
        except Exception as exc:
            logger.exception(exc)
            raise exc

        return ret_code

    return handle


@exception_handler
def run():
    """Run the app."""
    logger.debug(f"mrack version: {VERSION}")
    mrackcli(obj={})  # pylint: disable=no-value-for-parameter,unexpected-keyword-arg


if __name__ == "__main__":
    run()
