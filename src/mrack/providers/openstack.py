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
from random import random, sample
from urllib.parse import parse_qs, urlparse

import aiofiles  # type: ignore
import os_client_config
from aiohttp import ContentTypeError
from asyncopenstackclient import AuthPassword, GlanceClient
from keystoneauth1.exceptions.auth_plugins import MissingRequiredOptions, OptionError
from simple_rest_client.exceptions import AuthError, NotFoundError, ServerError

from mrack.context import global_context
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
NETWORK_NAME = 0
NETWORK_SIZE = 1


class OpenStackProvider(Provider):
    """
    OpenStack Provider.

    Provisions servers in OpenStack with added logic to check if requested
    resources are available.
    """

    def __init__(self):
        """Object initialization."""
        super().__init__()
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

    async def _openstack_gather_responses(self, *calls):
        """Gather the async result of functions from parameters.

        Returns:
        * list of asyncio.gather results
        """
        error_attempts = 0
        result = []
        while error_attempts < SERVER_ERROR_RETRY:
            coros = [func(*args, **xargs) for (func, args, xargs) in calls]
            try:
                result = await asyncio.gather(*coros)
                break
            except ServerError as exc:
                logger.debug(f"{self.dsp_name} {exc}")
                error_attempts += 1
                if error_attempts <= SERVER_ERROR_RETRY:
                    await asyncio.sleep(SERVER_ERROR_SLEEP)
                    continue  # Try again due to ServerError
        else:
            # now we are past to what we would like to wait fail now
            raise ProvisioningError(
                f"{self.dsp_name} Failed to load environment objects from server",
            )

        return result

    def _curate_auth_url(self, auth_url):
        """Append OpenStack API version if not present."""
        return auth_url if auth_url.endswith("/v3") else auth_url + "/v3"

    async def _create_session(self):
        """
        Create session object using credentials.

        Credentials are retrieved from either enviromental variables or
        clouds.yaml file.
        Both username+password and application credentials formats
        are accepted.

        Returns: Session object.
        """
        try:
            # Create session from environment variables
            return AuthPassword()
        except TypeError:
            # Fallback to create session from clouds.yaml file
            try:
                config = os_client_config.OpenStackConfig()

                # Get the cloud specified in provisioning-config
                # If that fails try to pick the cloud specified in OS_CLOUD envvar
                # or get the only cloud (if there is only one)
                try:
                    cloud = config.get_one_cloud(self.cloud_profile)
                    logger.debug(f"{self.dsp_name} Using profile: {self.cloud_profile}")
                except os_client_config.exceptions.OpenStackConfigException:
                    cloud = config.get_one_cloud()

                auth_info = cloud.config["auth"]

                curated_auth_url = self._curate_auth_url(auth_info["auth_url"])
                logger.debug(f"{self.dsp_name} auth_url: {curated_auth_url}")

                if "username" in auth_info and "password" in auth_info:
                    logger.debug(f"{self.dsp_name} username: {auth_info['username']}")
                    return AuthPassword(
                        auth_url=curated_auth_url,
                        username=auth_info["username"],
                        password=auth_info["password"],
                        project_name=auth_info["project_name"],
                        user_domain_name=auth_info["user_domain_name"],
                    )
                elif (
                    "application_credential_id" in auth_info
                    and "application_credential_secret" in auth_info
                ):
                    logger.debug(
                        f"{self.dsp_name} application_credential_id: "
                        + f"{auth_info['application_credential_id']}"
                    )
                    return AuthPassword(
                        auth_url=curated_auth_url,
                        application_credential_id=auth_info[
                            "application_credential_id"
                        ],
                        application_credential_secret=auth_info[
                            "application_credential_secret"
                        ],
                    )
                else:
                    err_msg = (
                        "Invalid clouds.yaml configuration. " + "Authentication failed."
                    )
                    raise NotAuthenticatedError(err_msg)
            except (
                os_client_config.exceptions.OpenStackConfigException,
                AttributeError,
                TypeError,
                OptionError,
                MissingRequiredOptions,
            ) as terr:
                logger.debug(f"{self.dsp_name} Error during authentication: {terr}")
                err_msg = (
                    "OpenStack credentials not provided or not properly configured. "
                    + "Authentication failed."
                    + "\nIf you have more than one cloud configured, make sure"
                    + " to set OS_CLOUD envvar."
                )
                raise NotAuthenticatedError(err_msg) from terr

    async def _import_public_key(self):
        """Import public key to OpenStack if it does not exist."""
        try:
            await self.nova.keypairs.show(self.keypair)
            logger.debug(f"Keypair {self.keypair} already exists.")
        except NotFoundError:
            async with aiofiles.open(self.pubkey, mode="r") as public_key_file:
                public_key = await public_key_file.read()

            keypair_obj = {"name": self.keypair, "public_key": public_key}
            resp = await self.nova.keypairs.create(keypair=keypair_obj)
            resp_obj = resp["keypair"]
            logger.info(
                f"Keypair {resp_obj.get('name')} imported with fingerprint: "
                + f"{resp_obj.get('fingerprint')}"
            )

    async def init(
        self,
        image_names=None,
        networks=None,
        strategy=STRATEGY_ABORT,
        max_retry=1,
        cloud_profile="",
        keypair="",
        pubkey="",
    ):
        """Initialize provider with data from OpenStack.

        Load:
        * available flavors
        * networks
        * network availabilities (number of available IPs for networks)
        * images which were defined in `images` option
        * account limits (max and current usage of vCPUs, memory, ...)
        """
        logger.info(f"{self.dsp_name} Initializing provider")
        self.strategy = strategy
        self.max_retry = max_retry
        self.cloud_profile = cloud_profile
        self.keypair = keypair
        self.pubkey = pubkey

        # Session expects that credentials will be set via env variables
        # or clouds.yaml file. For the latter, cloud profile should be specified
        # in provisioning-config openstack.profile key or in envvar OS_CLOUD.
        self.session = await self._create_session()

        self.nova = ExtraNovaClient(session=self.session)
        self.glance = GlanceClient(session=self.session)
        self.neutron = NeutronClient(session=self.session)

        login_start = datetime.now()
        try:
            await asyncio.gather(
                self.nova.init_api(self.api_timeout),
                self.glance.init_api(self.api_timeout),
                self.neutron.init_api(self.api_timeout),
            )
        except KeyError as e:
            err_msg = "Authentication to Openstack with provided credentials failed"
            raise NotAuthenticatedError(err_msg) from e
        except ContentTypeError as e:
            err_msg = (
                "Authentication to Openstack with provided credentials failed"
                + "\nTIP: Make sure the parameter 'auth_url' from your credentials"
                + " ends with '/v3'"
            )
            raise NotAuthenticatedError(err_msg) from e
        login_end = datetime.now()
        logger.info(f"{self.dsp_name} Login duration {login_end - login_start}")

        await self._import_public_key()

        self.network_pools = networks
        object_start = datetime.now()

        _, _, self.limits, _, _ = await self._openstack_gather_responses(
            [self._load_flavors, [], {}],
            [self._load_images, [image_names], {}],
            [self.nova.limits.show, [], {}],
            [self._load_networks, [], {}],
            [self._load_ip_availabilities, [], {}],
        )

        object_duration = datetime.now() - object_start
        logger.info(
            f"{self.dsp_name} Environment objects load duration: {object_duration}"
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

    def _pick_network(self, host_name, host_weight, nets_weights):
        """
        Pick network based network type and weight of host.

        This method allows OpenStack to pick Network from
        all of networks based on network load and requirement
        got from the metadata. Each of required host gets
        its own position, aka weigh in interval <0, 1>
        based on the order (index) in metadata. Before that
        all of the networks are 'normalized' with _get_weights_from_usable

        An example:
        - considering 5 host request
        - picked 5 networks where availability is > 5%

        Host weights:
        - host 1 - 0/5 = 0
        - host 2 - 1/5 = 0.2
        - host 3 - 2/5 = 0.4
        - host 4 - 3/5 = 0.6
        - host 5 - 4/5 = 0.8

        Network availability:
        - net 1 - 20 addresses
        - net 2 - 100 addresses
        - net 3 - 130 addresses
        - net 4 - 145 addresses
        - net 5 - 105 addresses

        Full capacity of these 5 nets: 500

        Normalized network range:
        net 4 - <0, 0.29)
        net 3 - <0,29, 0.55)
        net 5 - <0.55, 0.76)
        net 2 - <0.76, 0.96)
        net 1 - <0.96, 1)

        Which will divide networks for hosts:
        host 1 => net 4 (0 falls into net 4 interval)
        host 2 => net 4 (0.2 falls into net 4 interval)
        host 3 => net 3 (0.4 falls into net 3 interval)
        host 4 => net 5 (0.6 falls into net 5 interval)
        host 5 => net 2 (0.8 falls into net 2 interval)

        net 1 will be unused as bigger networks are preferred this way.
        """
        chosen = tuple()
        for index, net in enumerate(nets_weights):
            if host_weight < net[NETWORK_SIZE]:
                chosen = net
                # print details only if there is more one network to be picked from
                if len(nets_weights) > 1:
                    lower_bound = nets_weights[index - 1][NETWORK_SIZE] if index else 0
                    logger.debug(
                        f"{self.dsp_name} [{host_name}] Weight of host "
                        f"{host_weight:.3f} fell into interval: "
                        f"({lower_bound:.3f}, {chosen[NETWORK_SIZE]:.3f}>"
                    )

                break

        if not chosen:
            raise ProviderError(f"{self.dsp_name} Error: No network has been chosen")

        logger.debug(
            f"{self.dsp_name} [{host_name}] Picked network '{chosen[NETWORK_NAME]}'"
        )

        return chosen[NETWORK_NAME]

    def _get_usable_networks(self, network_type, requested_ip_cnt):
        """
        Return list of available networks and ip availability.

        Available networks with most IPs available is picked.
        """
        usable = set()
        low_avail_nets = set()
        total_available = 0
        max_size_net = 0
        threshold = global_context.CONFIG.usable_network_threshold
        spread_option = global_context.CONFIG.network_spread
        big_request = False

        # filter out the None values - the get_network return None if network not found
        for network in list(
            filter(
                None,
                [self._get_network(net) for net in self.network_pools[network_type]],
            )
        ):
            ips = self._get_ips(ref=network.get("id"))

            available = ips["total_ips"] - ips["used_ips"]
            max_size_net = available if available > max_size_net else max_size_net

            logger.debug(
                f"{self.dsp_name} Network: {network['name']}"
                f"{' - unusable (0 IPs left) skipping' if not available else ''}"
            )
            logger.debug(f"  total: {ips['total_ips']}")
            logger.debug(f"  used: {ips['used_ips']}")
            logger.debug(f"  available: {available}")

            if not available:
                continue

            total_available += available

            #  assume network is unusable when usable_threshold is reached
            if ips["used_ips"] / ips["total_ips"] > threshold / 100:
                low_avail_nets.add((network["name"], available))
                continue

            usable.add((network["name"], available))

        if not usable and (total_available >= requested_ip_cnt) and low_avail_nets:
            usable = usable.union(low_avail_nets)

        if not usable:
            raise ValidationError(
                "No available networks for "
                f"{requested_ip_cnt} hosts with {network_type}",
                self.dsp_name,
            )

        if requested_ip_cnt > max_size_net:
            big_request = True
            # if we request more IPs than maximum size net consider the request big
            # adding even small networks to the usable set to spread the load
            usable = usable.union(low_avail_nets)

        logger.debug(
            f"{self.dsp_name} Default mrack behavior is to 'allow' spread"
            " the load to all available networks, to disable this feature set"
            " the 'network-spread' option in the mrack.conf file to 'no'"
        )
        logger.debug(
            f"{self.dsp_name} 'network-spread' option is set to '{spread_option}'"
        )
        logger.debug(
            f"{self.dsp_name} Considering this request "
            f"{'big' if big_request else 'small'} - requesting {requested_ip_cnt} "
            f"IP(s) from total available {total_available} IP(s)"
        )

        size_for_spread = (
            len(usable) if len(usable) <= requested_ip_cnt else requested_ip_cnt
        )

        # number of networks which we will consider to pass to picking algorithm
        network_subset_size = 0

        if spread_option == "force":
            network_subset_size = size_for_spread
        elif spread_option == "no":
            if not big_request:
                network_subset_size = 1
        else:  # spread option is allow or some unknown string -> fallback to default
            if usable.intersection(low_avail_nets) or big_request:
                network_subset_size = size_for_spread
            else:
                network_subset_size = 1

        if network_subset_size:
            return sorted(
                set(sample(sorted(usable), network_subset_size)),
                key=lambda u: u[NETWORK_SIZE],
                reverse=True,
            )
        # If the above return does not happened because there is 0 usable networks
        # we will raise a ValidationError
        raise ValidationError(
            f"Can not satisfy request for {requested_ip_cnt} hosts ({network_type}) "
            "Change the 'network-spread' in mrack.conf or try provisioning again later",
            self.dsp_name,
        )

    def _get_weights_from_usable(self, usable_networks):
        """
        Define map of network type and weight of usable_networks.

        All of the networks are 'normalized' in a way that the random
        selection from subset of networks (networks_weights parameter)
        (or all of network if number of hosts >= number of networks)
        is divided to effective range (multiple intervals in <0, 1>)
        for the network based on the relative network weight
        compared to full capacity of considered networks.

        e.g.:
        - usable_networks = [('net_1', 11), ('net_3', 10)]
        - weights = [('net_1', 0.5238095238095238), ('net_3', 1.0)]

        """
        total_weight = sum(net[NETWORK_SIZE] for net in usable_networks)
        weights = [
            (net[NETWORK_NAME], net[NETWORK_SIZE] / total_weight)
            for net in usable_networks
        ]
        if len(weights) == 1:
            return weights

        for w_index in range(1, len(weights)):
            weights[w_index] = (
                weights[w_index][NETWORK_NAME],
                weights[w_index - 1][NETWORK_SIZE] + weights[w_index][NETWORK_SIZE],
            )

        return weights

    def _translate_network_types(self, hosts):
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
            # count is crucial
            nt_map[network_type] = self._get_usable_networks(network_type, count)

        weight_map = {}
        for network_type, usable_networks in nt_map.items():
            weight_map[network_type] = self._get_weights_from_usable(
                usable_networks,
            )

        for net_type, netw_weights in weight_map.items():
            logger.debug(
                f"{self.dsp_name} Considered networks "
                f"for {net_type} (network_name, weight_interval):"
            )
            for net in netw_weights:
                logger.debug(f"  {net}")

        for host in hosts:
            # skip hosts which have low-level network names defined
            names = host.get("networks")
            if names:
                continue

            network_type = host.get("network")

            # skip if network_type is not network type
            if not self.network_pools.get(network_type):
                continue

            networks_weights = weight_map[network_type]

            host["network"] = self._pick_network(
                host_name=host["name"],
                host_weight=hosts.index(host) / len(hosts),
                nets_weights=networks_weights,
            )

    def _set_networks(self, networks):
        """Extend provider configuration with list of networks."""
        for network in networks:
            self.networks[network["name"]] = network
            self.networks_by_ref[network["id"]] = network

    def _get_flavor(self, name=None, ref=None):
        """Get flavor by name or UUID."""
        flavor = self.flavors.get(name)
        if not flavor:
            flavor = self.flavors_by_ref.get(ref)
        return flavor

    def _get_image(self, name=None, ref=None):
        """Get image by name or UUID."""
        image = self.images.get(name)
        if not image:
            image = self.images_by_ref.get(ref)
        return image

    def _get_network(self, name=None, ref=None):
        """Get network by name or UUID."""
        network = self.networks.get(name)
        if not network:
            network = self.networks_by_ref.get(ref)

        if not network:
            net_id = name or ref
            logger.debug(
                f"{self.dsp_name} Failed to load network with name: '{net_id}'"
            )

        return network

    def _get_ips(self, name=None, ref=None):
        """Get network availability by network name or network UUID."""
        aval = self.ips.get(name)
        if not aval:
            aval = self.ips_by_ref.get(ref)
        return aval

    async def _load_flavors(self):
        """Extend provider configuration by loading all flavors from OpenStack."""
        resp = await self.nova.flavors.list()
        flavors = resp["flavors"]
        self._set_flavors(flavors)
        return flavors

    async def _load_images(self, image_names=None):
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

    async def _load_networks(self):
        """Extend provider configuration by loading all networks from OpenStack."""
        resp = await self.neutron.network.list()
        networks = resp["networks"]
        self._set_networks(networks)
        return networks

    async def _load_ip_availabilities(self):
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
            flavor = self._get_flavor(ref=flavor_ref)
        if flavor_spec:
            flavor = self._get_flavor(flavor_spec, flavor_spec)

        if not flavor:
            specs = f"flavor: {flavor_spec}, ref: {flavor_ref}"
            raise ValidationError(f"Flavor not found: {specs}", self.dsp_name)
        return flavor

    def _translate_image(self, req):
        image_spec = req.get("image")
        image_ref = req.get("imageRef")
        image = None
        if image_ref:
            image = self._get_image(ref=image_ref)
        if image_spec:
            image = self._get_image(image_spec, image_spec)
        if not image:
            specs = f"image: {image_spec}, ref: {image_ref}"
            raise ValidationError(f"Image not found {specs}", self.dsp_name)
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
            network = self._get_network(ref=uuid)
            if not network:
                raise ValidationError(
                    f"Network not found: {network_spec}", self.dsp_name
                )
            networks.append(network)
        if network_req:
            network = self._get_network(name=network_req, ref=network_req)
            if not network:
                raise ValidationError(
                    f"Network not found: {network_req}", self.dsp_name
                )

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
            logger.debug(f"{self.dsp_name} Loading image info for: '{im_list}'")
            await self._load_images(list(prepare_images))
            logger.debug(f"{self.dsp_name} Loading images info done.")

        self._set_poll_sleep_times(reqs)
        return True

    async def validate_hosts(self, reqs):
        """Validate that all hosts requirements contains existing required objects."""
        # translate network type to actual network and check network availabilities
        self._translate_network_types(reqs)

        for req in reqs:
            logger.info(f"{self.dsp_name} Validating host: {object2json(req)}")
            self.validate_host(req)
            logger.info(f"{self.dsp_name} [{req['name']}] OK")

    def get_host_requirements(self, req):
        """Get vCPU and memory requirements for host requirement."""
        flavor_spec = req.get("flavor")
        flavor_ref = req.get("flavorRef")
        flavor = None
        if flavor_ref:
            flavor = self._get_flavor(ref=flavor_ref)
        if flavor_spec:
            flavor = self._get_flavor(flavor_spec, flavor_spec)

        try:
            res = {"ram": flavor["ram"], "vcpus": flavor["vcpus"]}
        except TypeError as flavor_none:
            # func does not load flavor so None is used as result
            raise ValidationError(
                f"Could not load the flavor for requirement: {req}", self.dsp_name
            ) from flavor_none

        return res

    async def _load_limits(self):
        limits_await = await self._openstack_gather_responses(
            [self.nova.limits.show, [], {}],
        )
        self.limits = limits_await[0]  # gather returns list

        limits = self.limits["limits"]["absolute"]
        used_vcpus = limits["totalCoresUsed"]
        used_memory = limits["totalRAMUsed"]
        limit_vcpus = limits["maxTotalCores"]
        limit_memory = limits["maxTotalRAMSize"]

        return used_vcpus, used_memory, limit_vcpus, limit_memory

    async def can_provision(self, hosts):  # pylint: disable=arguments-differ
        """Check that all host can be provisioned.

        Checks:
        * available vCPUs and memory based on account limits
        * that all host contain available flavors, images, networks
        """
        vcpus = 0
        ram = 0

        for req in hosts:
            needs = self.get_host_requirements(req)
            vcpus += needs["vcpus"]
            ram += needs["ram"]

        # poll the actual openstack load
        logger.debug(f"{self.dsp_name} Loading nova limits")

        used_vcpus, used_memory, limit_vcpus, limit_memory = await self._load_limits()

        req_vcpus = used_vcpus + vcpus
        req_memory = used_memory + ram

        logger.info(
            f"{self.dsp_name} Required vcpus: {vcpus}, "
            f"used: {used_vcpus}, max: {limit_vcpus}"
        )

        logger.info(
            f"{self.dsp_name} Required ram: {ram}, "
            f"used: {used_memory}, max: {limit_memory}"
        )

        return req_vcpus <= limit_vcpus and req_memory <= limit_memory

    async def utilization(self):
        """Check utilization of provider."""
        used_vcpus, used_memory, limit_vcpus, limit_memory = await self._load_limits()
        cpu_util = used_vcpus / limit_vcpus * 100
        memory_util = used_memory / limit_memory * 100
        return cpu_util if memory_util <= cpu_util else memory_util

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
        log_msg_start = f"{self.dsp_name} [{name}]"
        logger.info(f"{log_msg_start} Creating server")
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
        if image.get("meta_compose_id") and image.get("meta_compose_url"):
            logger.info(
                f"{log_msg_start} Image meta_compose_id: {image['meta_compose_id']}"
                f"\n{log_msg_start} Image meta_compose_url:"
                f" {image['meta_compose_url']}"
            )

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
                logger.debug(f"{log_msg_start} {exc}")
                error_attempts += 1
                if error_attempts <= SERVER_ERROR_RETRY:
                    await asyncio.sleep(SERVER_ERROR_SLEEP)
                    continue  # Try again due to ServerError
            except AuthError as exc:
                raise ProvisioningError(
                    f"{log_msg_start} Failed to create server: {exc}",
                    req,
                )

            fault = response["server"].get("fault", {})

            if fault.get("code") == 500:
                # In such scenario OpenStack might run out of hosts to provision
                # This is not related to reaching OpenStack quota but to OpenStack
                # itself being fully loaded and without free resources to provide
                logger.info(
                    f"{log_msg_start} Unable to allocate resources for the required "
                    f"server (all available resources busy)"
                )
                error_attempts += 1
                logger.info(
                    f"{log_msg_start} Retrying request in {SERVER_RES_SLEEP} minutes"
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
                f"{log_msg_start} Failed to create server",
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
                    f"{self.dsp_name} Server with ID '{uuid}' not found, "
                    "probably already deleted"
                )
                break

    async def wait_till_provisioned(self, resource):  # pylint: disable=too-many-locals
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
        log_msg_start = f"{self.dsp_name} [{req.get('name')}]"
        uuid = resource.get("id")

        poll_sleep_initial = self.poll_sleep_initial + self.poll_init_adj
        poll_sleep_initial = (
            poll_sleep_initial / 2 + poll_sleep_initial * random() * 1.5
        )
        poll_sleep = self.poll_sleep + self.poll_adj

        start = datetime.now()
        timeout_time = start + timedelta(minutes=self.timeout)

        # do not check the state immediately, it will take some time
        logger.debug(
            f"{log_msg_start} ID {uuid}: sleeping for {poll_sleep_initial:.1f} seconds"
        )
        await asyncio.sleep(poll_sleep_initial)

        resp = {}
        logger.debug(f"{log_msg_start} ID {uuid}: Waiting for host creation")
        error_attempts = 0
        while datetime.now() < timeout_time:
            try:
                resp = await self.nova.servers.get(uuid)
            except NotFoundError as nf_err:
                raise ServerNotFoundError(uuid) from nf_err
            except ServerError as err:
                logger.debug(f"{log_msg_start} {err}")
                error_attempts += 1
                if error_attempts > SERVER_ERROR_RETRY:
                    raise ProvisioningError(uuid) from err

            server = resp["server"]
            if server["status"] in ["ACTIVE", "ERROR"]:
                break

            poll_sleep += 0.5  # increase delays to check the longer it takes
            logger.debug(
                f"{log_msg_start} ID {uuid}: sleeping for {poll_sleep:.1f} seconds"
            )
            await asyncio.sleep(poll_sleep)

        done_time = datetime.now()
        prov_duration = (done_time - start).total_seconds()

        if datetime.now() >= timeout_time:
            logger.warning(
                f"{log_msg_start} ID {uuid}: host was not provisioned "
                f"within a timeout of {self.timeout} mins"
            )
        else:
            logger.info(
                f"{log_msg_start} ID {uuid}: host "
                f"was provisioned in {prov_duration:.1f}s"
            )

        server.update({"mrack_req": req})

        return server, req

    async def delete_host(self, host_id, host_name):
        """Issue deletion of host(server) from OpenStack."""
        log_msg_start = f"{self.dsp_name} [{host_name}]"
        logger.info(f"{log_msg_start} Deleting host with ID {host_id}")
        await self.delete_server(host_id)
        return True

    def prov_result_to_host_data(self, prov_result, req):
        """Get needed host information from openstack provisioning result."""
        result = {}
        meta_extra = {}
        image = self._translate_image(req)
        # Check if these fields exists, not all images have them
        if image.get("meta_compose_id"):
            meta_extra["meta_compose_id"] = image.get("meta_compose_id")
        if image.get("meta_compose_url"):
            meta_extra["meta_compose_url"] = image.get("meta_compose_url")

        result["id"] = prov_result.get("id")
        result["name"] = req.get("name")
        networks = prov_result.get("addresses", {})
        result["addresses"] = [ip.get("addr") for n in networks.values() for ip in n]
        result["fault"] = prov_result.get("fault")
        result["status"] = prov_result.get("status")
        result["os"] = prov_result.get("mrack_req").get("os")
        result["group"] = prov_result.get("mrack_req").get("group")
        result["meta_extra"] = meta_extra

        return result
