import uuid


def mock_subnet_ip_availability(name, version, total_ips, used_ips):
    subnet = {
        "cidr": "10.0.10.0/22",  # this won't probably match total_ips now
        "ip_version": version,
        "subnet_id": str(uuid.uuid4()),
        "subnet_name": name,
        "total_ips": total_ips,
        "used_ips": used_ips,
    }
    if version == 6:
        subnet["cidr"] = "2828:60:0:80::/64"
    return subnet


def mock_network_availability(name, total_ips, used_ips, version, project, tenant):
    return {
        "network_id": str(uuid.uuid4()),
        "network_name": name,
        "project_id": project,
        "subnet_ip_availability": [
            mock_subnet_ip_availability(f"subnet_{name}", version, total_ips, used_ips),
        ],
        "tenant_id": tenant,
        "total_ips": total_ips,
        "used_ips": used_ips,
    }


def mock_network_ip_availabilities(availabilities_data):
    """
    Create mock object simulating OpenStack network availability call.

    Expected input format:
      List of dict with keys
        network: str,
        total: int,
        used: int,
        version: int - 4 or 6,

    E.g.
      [{"name": "net1", "total": 255, "used": 25, "version": 4},]

    Returns:
    """
    availabilities = []
    project = str(uuid.uuid4())
    tenant = str(uuid.uuid4())
    for data in availabilities_data:
        av = mock_network_availability(
            data["network"],
            data["total"],
            data["used"],
            data["version"],
            project,
            tenant,
        )
        availabilities.append(av)
    return {
        "network_ip_availabilities": availabilities,
    }


def mock_networks_from_availabilities(availabilities):
    """
    Mock networks call, create from availabilities data.
    """
    networks = []

    for availability in availabilities["network_ip_availabilities"]:
        subnets = [
            subnet["subnet_id"] for subnet in availability["subnet_ip_availability"]
        ]
        network = {
            "admin_state_up": True,
            "availability_zone_hints": [],
            "availability_zones": ["nova"],
            "created_at": "2019-08-19T07:54:27Z",
            "description": "",
            "id": availability["network_id"],
            "ipv4_address_scope": None,
            "ipv6_address_scope": None,
            "is_default": False,
            "l2_adjacency": True,
            "mtu": 1500,
            "name": availability["network_name"],
            "port_security_enabled": True,
            "project_id": availability["project_id"],
            "qos_policy_id": None,
            "revision_number": 12,
            "router:external": True,
            "shared": True,
            "status": "ACTIVE",
            "subnets": subnets,
            "tags": [],
            "tenant_id": availability["tenant_id"],
            "updated_at": "2019-08-27T12:43:31Z",
        }
        networks.append(network)
    return {
        "networks": networks,
    }


def mock_pools(availabilities):
    ip4 = []
    ip6 = []
    dual = []

    for availability in availabilities["network_ip_availabilities"]:
        is_4 = False
        is_6 = False

        for subnet in availability["subnet_ip_availability"]:
            if subnet["ip_version"] == 4:
                is_4 = True
            if subnet["ip_version"] == 6:
                is_6 = True

        name = availability["network_name"]
        if is_4:
            ip4.append(name)
        if is_6:
            ip6.append(name)
        if is_4 and is_6:
            dual.append(name)

    return {
        "IPv4": ip4,
        "IPv6": ip6,
        "dual": dual,
    }
