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

"""OpenStack provider."""

import asyncio
import logging
from copy import deepcopy
from datetime import datetime, timedelta
from random import choice, random
from urllib.parse import parse_qs, urlparse

from asyncopenstackclient import AuthPassword, GlanceClient
from simple_rest_client.exceptions import NotFoundError, ServerError

from mrack.errors import (
    NotAuthenticatedError,
    ProviderError,
    ProvisioningError,
    ServerNotFoundError,
    ValidationError,
)
from mrack.host import STATUS_ACTIVE, STATUS_DELETED, STATUS_ERROR, STATUS_PROVISIONING
from mrack.providers.provider import STRATEGY_ABORT, Provider
from mrack.providers.utils.osapi import ExtraNovaClient, NeutronClient
from mrack.utils import get_shortname, is_windows_host, object2json

logger = logging.getLogger(__name__)

# Docs
# https://github.com/DreamLab/AsyncOpenStackClient
# https://docs.openstack.org/queens/api/


PROVISIONER_KEY = "openstack"
SERVER_ERROR_RETRY = 5  # number of times to retry server creation
SERVER_ERROR_SLEEP = 10  # seconds
SERVER_RES_SLEEP = 10  # minutes


class OpenStackProvider(Provider):
    """
    OpenStack Provider.

    Provisions servers in OpenStack with added logic to check if requested
    resources are available.
    """

    def __init__(self):
        """Object initialization."""
        self._name = PROVISIONER_KEY
        self.dsp_name = "OpenStack"
        self.max_retry = 1  # provisioning retries
        self.flavors = {}
        self.flavors_by_ref = {}
        self.images = {}
        self.images_by_ref = {}
        self.limits = {}
        self.networks = {}
        self.networks_by_ref = {}
        self.ips = {}
        self.ips_by_ref = {}
        self.api_timeout = 6 * 60  # timeout for request to OpenStack
        self.timeout = 60  # minutes
        self.poll_sleep_initial = 15  # seconds
        self.poll_sleep = 7  # seconds
        self.poll_init_adj = 0  # set based on # of hosts to provisions
        self.poll_adj = 0  # set based on # of hosts to provisions
        self.status_map = {
            "ACTIVE": STATUS_ACTIVE,
            "BUILD": STATUS_PROVISIONING,
            "DELETED": STATUS_DELETED,
            "ERROR": STATUS_ERROR,
            # there is much more we can treat it as STATUS_OTHER, see:
            # https://docs.openstack.org/api-guide/compute/server_concepts.html
        }

    async def init(
        self, image_names=None, networks=None, strategy=STRATEGY_ABORT, max_retry=1
    ):
        """Initialize provider with data from OpenStack.

        Load:
        * available flavors
        * networks
        * network availabilities (number of available IPs for networks)
        * images which were defined in `images` option
        * account limits (max and current usage of vCPUs, memory, ...)
        """
        # session expects that credentials will be set via env variables
        logger.info(f"{self.dsp_name}: Initializing provider")
        self.strategy = strategy
        self.max_retry = max_retry
        try:
            self.session = AuthPassword()
        except TypeError as terr:
            err = (
                "OpenStack credentials not provided. Load OpenStack RC file with valid "
                "credentials and try again. E.g.: $ source PROJECT-openrc.sh"
            )
            raise NotAuthenticatedError(err) from terr

        self.nova = ExtraNovaClient(session=self.session)
        self.glance = GlanceClient(session=self.session)
        self.neutron = NeutronClient(session=self.session)

        login_start = datetime.now()
        await asyncio.gather(
            self.nova.init_api(self.api_timeout),
            self.glance.init_api(self.api_timeout),
            self.neutron.init_api(self.api_timeout),
        )
        login_end = datetime.now()
        logger.info(f"{self.dsp_name}: Login duration {login_end - login_start}")

        self.network_pools = networks
        object_start = datetime.now()

        error_attempts = 0
        while error_attempts < SERVER_ERROR_RETRY:
            try:
                _, _, self.limits, _, _ = await asyncio.gather(
                    self.load_flavors(),
                    self.load_images(image_names),
                    self.nova.limits.show(),
                    self.load_networks(),
                    self.load_ip_availabilities(),
                )
                break
            except ServerError as exc:
                logger.debug(f"{self.dsp_name}: {exc}")
                error_attempts += 1
                if error_attempts <= SERVER_ERROR_RETRY:
                    await asyncio.sleep(SERVER_ERROR_SLEEP)
                    continue  # Try again due to ServerError

        else:
            # now we are past to what we would like to wait fail now
            raise ProvisioningError(
                f"{self.dsp_name}: Failed to load environment objects from server",
            )

        object_duration = datetime.now() - object_start
        logger.info(
            f"{self.dsp_name}: Environment objects load duration: {object_duration}"
        )

    def _set_flavors(self, flavors):
        """Extend provider configuration with list of flavors."""
        for flavor in flavors:
            self.flavors[flavor["name"]] = flavor
            self.flavors_by_ref[flavor["id"]] = flavor

    def _set_images(self, images):
        """Extend provider configuration with list of images."""
        for image in images:
            self.images[image["name"]] = image
            self.images_by_ref[image["id"]] = image

    def _is_network_type(self, name):
        """Check if name is a configured network type in provisioning config."""
        network_type = self.network_pools.get(name)
        return bool(network_type)

    def _aggregate_networks(self, hosts):
        """
        Get how many host require each used network type.

        Returns: dict where keys are network types and values are total count.
        """
        network_types = {}
        for host in hosts:
            # skip hosts which have low-level network names defined
            # this can be extended to pick network type based on the network name
            names = host.get("networks")
            if names:
                continue
            network_type = host.get("network")
            if not self._is_network_type(network_type):
                continue

            count = network_types.get(network_type, 0)
            count += 1
            network_types[network_type] = count

        return network_types

    def _pick_network(self, network_type, count):
        """
        Pick network based network type and needed amount.

        Usable network with most IPs available is picked.
        """
        possible_networks = self.network_pools[network_type]
        networks = [self.get_network(net) for net in possible_networks]
        usable = []
        for network in networks:
            if not network:
                continue

            ips = self.get_ips(ref=network.get("id"))

            available = ips["total_ips"] - ips["used_ips"]
            logger.debug(f"Network: {network['name']}")
            logger.debug(f"  total: {ips['total_ips']}")
            logger.debug(f"  used: {ips['used_ips']}")
            logger.debug(f"  available: {available}")
            if available > count:
                usable.append((network["name"], available))
        if not usable:
            logger.error(
                f"{self.dsp_name}: Error: no usable network"
                f" for {count} hosts with {network_type}"
            )
            return None

        # sort networks by number of available IPs
        usable = sorted(usable, key=lambda u: u[1])
        logger.debug(f"{self.dsp_name}: Listing usable networks: {usable}")

        # Do not always pick the best, but randomize from good ones to spread
        # load for high number of parallel jobs. E.g. if running mrack 100 times
        # where each needs 3-4 hosts and best network has 250 IPs then we risk
        # to pass the check intially but later fail as the check was not done
        # with all the others on mind (race-condition).

        # Good == has at least 50% of IPs as the best.
        best_pool = usable[-1]
        satisfying = [n for n in usable if n[1] / best_pool[1] > 0.5]
        logger.debug(
            f"{self.dsp_name}: Picking randomly from network pools which satisfy "
            f"requirement (size_of_pool/size_of_biggest > 0.5): {satisfying}"
        )
        chosen = choice(satisfying)
        logger.debug(
            f"{self.dsp_name}: Network picked: {chosen[0]} with {chosen[1]} addresses"
        )
        return chosen[0]

    def translate_network_types(self, hosts):
        """Pick the right OpenStack networks for all hosts.

        Pick the network based on network type, networks configured for the
        type and the available IP addresses. Process all hosts to
        be able to pick the network which have enough addresses for all hosts.

        All hosts will have either "networks" attribute or "network"
        host attribute set with OpenStack network name or ID.
        """
        nt_requirements = self._aggregate_networks(hosts)
        nt_map = {}
        for network_type, count in nt_requirements.items():
            network_name = self._pick_network(network_type, count)
            nt_map[network_type] = network_name

        for host in hosts:
            # skip hosts which have low-level network names defined
            names = host.get("networks")
            if names:
                continue

            network_type = host.get("network")

            # skip if network_type is not network type
            if not self.network_pools.get(network_type):
                continue

            network_name = nt_map[network_type]
            host["network"] = network_name

    def _set_networks(self, networks):
        """Extend provider configuration with list of networks."""
        for network in networks:
            self.networks[network["name"]] = network
            self.networks_by_ref[network["id"]] = network

    def get_flavor(self, name=None, ref=None):
        """Get flavor by name or UUID."""
        flavor = self.flavors.get(name)
        if not flavor:
            flavor = self.flavors_by_ref.get(ref)
        return flavor

    def get_image(self, name=None, ref=None):
        """Get image by name or UUID."""
        image = self.images.get(name)
        if not image:
            image = self.images_by_ref.get(ref)
        return image

    def get_network(self, name=None, ref=None):
        """Get network by name or UUID."""
        network = self.networks.get(name)
        if not network:
            network = self.networks_by_ref.get(ref)

        if not network:
            net_id = name or ref
            logger.debug(
                f"{self.dsp_name}: Failed to load network with name: '{net_id}'"
            )

        return network

    def get_ips(self, name=None, ref=None):
        """Get network availability by network name or network UUID."""
        aval = self.ips.get(name)
        if not aval:
            aval = self.ips_by_ref.get(ref)
        return aval

    async def load_flavors(self):
        """Extend provider configuration by loading all flavors from OpenStack."""
        resp = await self.nova.flavors.list()
        flavors = resp["flavors"]
        self._set_flavors(flavors)
        return flavors

    async def load_images(self, image_names=None):
        """
        Extend provider configuration by loading information about images.

        Load everything if image_names list is not specified.

        Specifying list of images to load might improve performance if the
        OpenStack instance contains a lot of images.
        """
        params = {"limit": 1000}

        if image_names:
            image_filter = ",".join(image_names)
            image_filter = "in:" + image_filter
            params["name"] = image_filter

        images = []
        response = await self.glance.images.list(**params)
        images.extend(response["images"])

        while response.get("next"):
            p_result = urlparse(response.get("next"))
            query = p_result.query
            next_params = parse_qs(query)
            for key, val in next_params.items():
                if isinstance(val, list) and val:
                    next_params[key] = val[0]
            response = await self.glance.images.list(**next_params)
            images.extend(response["images"])

        self._set_images(images)

        return images

    async def load_networks(self):
        """Extend provider configuration by loading all networks from OpenStack."""
        resp = await self.neutron.network.list()
        networks = resp["networks"]
        self._set_networks(networks)
        return networks

    async def load_ip_availabilities(self):
        """Extend provider configuration by loading networks availabilities."""
        resp = await self.neutron.ip.list()
        availabilities = resp["network_ip_availabilities"]
        for availability in availabilities:
            self.ips[availability["network_name"]] = availability
            self.ips_by_ref[availability["network_id"]] = availability
        return availabilities

    def _translate_flavor(self, req):
        flavor_spec = req.get("flavor")
        flavor_ref = req.get("flavorRef")
        flavor = None
        if flavor_ref:
            flavor = self.get_flavor(ref=flavor_ref)
        if flavor_spec:
            flavor = self.get_flavor(flavor_spec, flavor_spec)

        if not flavor:
            specs = f"flavor: {flavor_spec}, ref: {flavor_ref}"
            raise ValidationError(f"Flavor not found: {specs}")
        return flavor

    def _translate_image(self, req):
        image_spec = req.get("image")
        image_ref = req.get("imageRef")
        image = None
        if image_ref:
            image = self.get_image(ref=image_ref)
        if image_spec:
            image = self.get_image(image_spec, image_spec)
        if not image:
            specs = f"image: {image_spec}, ref: {image_ref}"
            raise ValidationError(f"Image not found {specs}")
        return image

    def _translate_networks(self, req, spec=False):
        network_req = req.get("network")
        network_specs = req.get("networks", [])
        network_specs = deepcopy(network_specs)
        networks = []
        if not isinstance(network_specs, list):
            network_specs = []
        for network_spec in network_specs:
            uuid = network_spec.get("uuid")
            network = self.get_network(ref=uuid)
            if not network:
                raise ValidationError(f"Network not found: {network_spec}")
            networks.append(network)
        if network_req:
            network = self.get_network(name=network_req, ref=network_req)
            if not network:
                raise ValidationError(f"Network not found: {network_req}")

            network_specs.append({"uuid": network["id"]})
            networks.append(network)

        if spec:
            return network_specs
        return networks

    def validate_host(self, req):
        """Validate that host requirements contains existing required objects."""
        self._translate_flavor(req)
        self._translate_image(req)
        self._translate_networks(req)

        return True

    def _set_poll_sleep_times(self, reqs):
        """
        Compute polling sleep times based on number of hosts.

        So that we don't create unnecessary load on server while still checking returns
        (initial_sleep, sleep)
        """
        count = len(reqs)

        # initial poll is the biggest performance saver it should be around
        # time when more than half of host is in ACTIVE state
        self.poll_init_adj = 0.65 * count

        # poll time should ask often enough, to not create unnecessary delays
        # while not that many to not load the server much
        self.poll_adj = 0.22 * count

    async def prepare_provisioning(self, reqs):
        """
        Prepare provisioning.

        Load missing images if they are not in provisioning-config.yaml
        """
        prepare_images = list(
            {req["image"] for req in reqs if req["image"] not in self.images}
        )

        if prepare_images:
            im_list = ", ".join(prepare_images)
            logger.debug(f"{self.dsp_name}: Loading image info for: '{im_list}'")
            await self.load_images(list(prepare_images))
            logger.debug(f"{self.dsp_name}: Loading images info done.")

        self._set_poll_sleep_times(reqs)

    async def validate_hosts(self, reqs):
        """Validate that all hosts requirements contains existing required objects."""
        # translate network type to actual network and check network availabilities
        self.translate_network_types(reqs)

        for req in reqs:
            logger.info(f"{self.dsp_name}: Validating host: {object2json(req)}")
            self.validate_host(req)
            logger.info(f"{self.dsp_name}: {req['name']} - OK")

    def get_host_requirements(self, req):
        """Get vCPU and memory requirements for host requirement."""
        flavor_spec = req.get("flavor")
        flavor_ref = req.get("flavorRef")
        flavor = None
        if flavor_ref:
            flavor = self.get_flavor(ref=flavor_ref)
        if flavor_spec:
            flavor = self.get_flavor(flavor_spec, flavor_spec)

        try:
            res = {"ram": flavor["ram"], "vcpus": flavor["vcpus"]}
        except TypeError as flavor_none:
            # func does not load flavor so None is used as result
            raise ValidationError(
                f"Could not load the flavor for requirement: {req}"
            ) from flavor_none

        return res

    async def can_provision(self, reqs):  # pylint: disable=arguments-differ
        """Check that all host can be provisioned.

        Checks:
        * available vCPUs and memory based on account limits
        * that all host contain available flavors, images, networks
        """
        vcpus = 0
        ram = 0

        for req in reqs:
            needs = self.get_host_requirements(req)
            vcpus += needs["vcpus"]
            ram += needs["ram"]

        limits = self.limits["limits"]["absolute"]
        used_vcpus = limits["totalCoresUsed"]
        used_memory = limits["totalRAMUsed"]
        limit_vcpus = limits["maxTotalCores"]
        limit_memory = limits["maxTotalRAMSize"]

        req_vcpus = used_vcpus + vcpus
        req_memory = used_memory + ram

        logger.info(
            f"{self.dsp_name}: Required vcpus: {vcpus}, "
            f"used: {used_vcpus}, max: {limit_vcpus}"
        )

        logger.info(
            f"{self.dsp_name}: Required ram: {ram}, "
            f"used: {used_memory}, max: {limit_memory}"
        )

        return req_vcpus <= limit_vcpus and req_memory <= limit_memory

    async def create_server(self, req):
        """Issue creation of a server.

        req - dict of server requirements - can contains values defined in
              POST /servers official OpenStack API
              https://docs.openstack.org/api-ref/compute/?expanded=create-server-detail#create-server

        The req object can contain following additional attributes:
        * 'flavor': uuid or name of flavor to use
        * 'network': uuid or name of network to use. Will be added to networks
                     list if present
        """
        name = req.get("name")
        logger.info(f"{self.dsp_name}: Creating server {name}")
        specs = deepcopy(req)  # work with own copy, do not modify the input
        del specs["os"]  # do not pass this to openstack

        if is_windows_host(req):
            # Windows support only shortnames for Cloudbase-Init - it is
            # derived from openstack vm name.
            specs["name"] = get_shortname(name)

        flavor = self._translate_flavor(req)
        specs["flavorRef"] = flavor["id"]
        if specs.get("flavor"):
            del specs["flavor"]

        image = self._translate_image(req)
        specs["imageRef"] = image["id"]
        if specs.get("image"):
            del specs["image"]

        network_specs = self._translate_networks(req, spec=True)
        specs["networks"] = network_specs
        if specs.get("network"):
            del specs["network"]

        if specs.get("group"):
            del specs["group"]

        error_attempts = 0
        while error_attempts < SERVER_ERROR_RETRY:
            try:
                response = await self.nova.servers.create(server=specs)
            except ServerError as exc:
                logger.debug(f"{self.dsp_name}: {exc}")
                error_attempts += 1
                if error_attempts <= SERVER_ERROR_RETRY:
                    await asyncio.sleep(SERVER_ERROR_SLEEP)
                    continue  # Try again due to ServerError

            fault = response["server"].get("fault", {})

            if fault.get("code") == 500:
                # In such scenario OpenStack might run out of hosts to provision
                # This is not related to reaching OpenStack quota but to OpenStack
                # itself being fully loaded and without free resources to provide
                logger.info(
                    f"{self.dsp_name}: Unable to allocate resources for the required "
                    f"server (all available resources busy)"
                )
                error_attempts += 1
                logger.info(
                    f"{self.dsp_name}: Retrying request in {SERVER_RES_SLEEP} minutes"
                )
                # We should wait for OpenStack for reasonable time to try to reprovision
                # This sleep time should be longer for higher probability for Openstack
                # having freed some resources for us even when we are not reaching quota
                await asyncio.sleep(SERVER_RES_SLEEP * 60)  # * 60 - sleep for minutes
            else:
                # provisioning seems to pass correctly break to return result
                break

        else:
            # now we are past to what we would like to wait fail now
            raise ProvisioningError(
                f"{self.dsp_name}: Failed to create server {req['name']}",
                req,  # add the requirement dictionary to traceback for later
            )

        return (response.get("server"), req)

    async def delete_server(self, uuid):
        """Issue deletion of server.

        Doesn't wait for the deletion to happen.
        """
        error_attempts = 0
        while True:
            try:
                await self.nova.servers.force_delete(uuid)
            except ServerError as exc:
                logger.debug(exc)
                error_attempts += 1
                if error_attempts > SERVER_ERROR_RETRY:
                    raise ProviderError(uuid) from exc
                await asyncio.sleep(SERVER_ERROR_SLEEP)
            except NotFoundError:
                logger.warning(
                    f"{self.dsp_name}: Server '{uuid}' not found, probably already "
                    "deleted"
                )
                break

    async def wait_till_provisioned(self, resource):
        """
        Wait till server is provisioned.

        Provisioned means that server is in ACTIVE or ERROR state

        State is checked by polling. Polling can be controller via `poll_sleep` and
        `poll_sleep_initial` options. This is useful when provisioning a lot of
        machines as it is better to increase initial poll to not ask to often as
        provisioning resources takes some time.

        Waits till timeout happens. Timeout can be either specified or default provider
        timeout is used.

        Return information about provisioned server.
        """
        resource, req = resource
        uuid = resource.get("id")

        poll_sleep_initial = self.poll_sleep_initial + self.poll_init_adj
        poll_sleep_initial = (
            poll_sleep_initial / 2 + poll_sleep_initial * random() * 1.5
        )
        poll_sleep = self.poll_sleep + self.poll_adj

        start = datetime.now()
        timeout_time = start + timedelta(minutes=self.timeout)

        # do not check the state immediately, it will take some time
        logger.debug(f"{uuid}: sleeping for {poll_sleep_initial:.1f} seconds")
        await asyncio.sleep(poll_sleep_initial)

        resp = {}
        logger.debug(f"Waiting for '{req['name']}': {uuid}")
        error_attempts = 0
        while datetime.now() < timeout_time:
            try:
                resp = await self.nova.servers.get(uuid)
            except NotFoundError as nf_err:
                raise ServerNotFoundError(uuid) from nf_err
            except ServerError as err:
                logger.debug(f"{self.dsp_name}: {err}")
                error_attempts += 1
                if error_attempts > SERVER_ERROR_RETRY:
                    raise ProvisioningError(uuid) from err

            server = resp["server"]
            if server["status"] in ["ACTIVE", "ERROR"]:
                break

            poll_sleep += 0.5  # increase delays to check the longer it takes
            logger.debug(f"{uuid}: sleeping for {poll_sleep:.1f} seconds")
            await asyncio.sleep(poll_sleep)

        done_time = datetime.now()
        prov_duration = (done_time - start).total_seconds()

        if datetime.now() >= timeout_time:
            logger.warning(
                f"{self.dsp_name}: Host {uuid} was not provisioned "
                f"within a timeout of {self.timeout} mins"
            )
        else:
            logger.info(
                f"{self.dsp_name}: Host {uuid} was provisioned in {prov_duration:.1f}s"
            )

        server.update({"mrack_req": req})

        return server, req

    async def delete_host(self, host_id):
        """Issue deletion of host(server) from OpenStack."""
        logger.info(f"{self.dsp_name}: Deleting host {host_id}")
        await self.delete_server(host_id)
        return True

    def prov_result_to_host_data(self, prov_result, req):
        """Get needed host information from openstack provisioning result."""
        result = {}

        result["id"] = prov_result.get("id")
        result["name"] = req.get("name")
        networks = prov_result.get("addresses", {})
        result["addresses"] = [ip.get("addr") for n in networks.values() for ip in n]
        result["fault"] = prov_result.get("fault")
        result["status"] = prov_result.get("status")
        result["os"] = prov_result.get("mrack_req").get("os")
        result["group"] = prov_result.get("mrack_req").get("group")

        return result
