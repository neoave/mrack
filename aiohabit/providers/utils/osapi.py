from asyncopenstackclient import NovaClient
from asyncopenstackclient.client import Client


class ExtraNovaClient(NovaClient):
    def __init__(self, session=None, api_url=None):
        super().__init__(session, api_url)
        self.resources.extend(['limits', 'quota', 'usage'])

    async def init_api(self, timeout=60):
        await super().init_api(timeout)
        self.api.limits.actions["show"] = {
            "method": "GET", "url": "limits"
        }
        self.api.quota.actions["show"] = {
            "method": "GET", "url": "os-quota-sets/{}"
        }
        self.api.usage.actions["show"] = {
            "method": "GET", "url": "os-simple-tenant-usage/{}"
        }
        self.api.limits.add_action("show")
        self.api.quota.add_action("show")
        self.api.usage.add_action("show")


class NeutronClient(Client):
    def __init__(self, session=None, api_url=None):
        super().__init__('neutron', ['network', 'ip'], session, api_url)

    async def init_api(self, timeout=60):
        await super().init_api(timeout)
        self.api.network.actions["list"] = {
            "method": "GET", "url": "networks"
        }
        self.api.ip.actions["list"] = {
            "method": "GET", "url": "network-ip-availabilities"
        }
        self.api.network.add_action("list")
        self.api.ip.add_action("list")
