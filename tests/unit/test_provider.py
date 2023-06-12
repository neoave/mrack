# Copyright 2023 Red Hat Inc.
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

import os
from unittest import mock
from unittest.mock import Mock, patch

import pytest

from mrack.context import global_context
from mrack.errors import ProviderNotExists
from mrack.providers.provider import Provider


def init_global_context(mrack_conf="mrack.conf"):
    try:
        global_context.init(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                f"conf/{mrack_conf}",
            ),
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "conf/provisioning-config.yaml",
            ),
        )
    except ProviderNotExists:
        assert global_context.CONFIG is not None


def AsyncMock(*args, **kwargs):
    m = mock.MagicMock(*args, **kwargs)

    async def mock_coro(*args, **kwargs):
        return m(*args, **kwargs)

    mock_coro.mock = m
    return mock_coro


class TestProvider:
    def setup_method(self):
        init_global_context()

    @pytest.mark.asyncio
    @patch.object(Provider, "_get_max_utilization", return_value=60)
    async def test_strategy_retry(self, get_max_utilization_mock):
        # Mock hosts with different results
        host1 = Mock(name="host1", error={})
        host2 = Mock(name="host2", error={})
        host3 = Mock(name="host3", error={})
        hostA_500 = Mock(name="hostA_500", error={"code": 500})
        hostB_500 = Mock(name="hostB_500", error={"code": 500})
        host1.name = "host1"
        host2.name = "host2"
        host3.name = "host3"
        hostA_500.name = "hostA_500"
        hostB_500.name = "hostB_500"

        provider = Provider()
        provider.max_retry = 3

        async def subtest_500_error():
            """Test reprovisioning and output when provisioning results in 500 error."""
            dummy_reqs = [
                {"name": "host1", "vcpus": 2, "memory": 4096},
                {"name": "hostA_500", "vcpus": 2, "memory": 4096},
                {"name": "hostB_500", "vcpus": 2, "memory": 4096},
            ]
            missing_dummy_reqs = [
                {"name": "hostA_500", "vcpus": 2, "memory": 4096},
                {"name": "hostB_500", "vcpus": 2, "memory": 4096},
            ]

            with patch.object(
                provider,
                "_provision_base",
                new_callable=AsyncMock,
                side_effect=lambda *args, **kwargs: (
                    [host1],
                    [hostA_500, hostB_500],
                    missing_dummy_reqs,
                ),
            ), patch.object(
                provider, "utilization", new_callable=AsyncMock, return_value=20
            ), patch.object(
                provider, "delete_hosts", new_callable=AsyncMock
            ) as mock_delete_hosts, patch(
                "asyncio.sleep", new_callable=AsyncMock
            ) as mock_sleep:
                (
                    success_hosts,
                    error_hosts,
                    missing_reqs,
                ) = await provider.strategy_retry(dummy_reqs)

                assert len(success_hosts) == 1
                assert len(error_hosts) == 2
                assert len(missing_reqs) == 2
                assert mock_sleep.mock.call_count == 3
                assert mock_delete_hosts.mock.call_count == 3
                # Assert that delete_hosts is called to delete all the hosts
                for call in mock_delete_hosts.mock.call_args_list:
                    called_error_hosts = call[0][0]
                    # error_hosts argument contains all hosts
                    assert len(called_error_hosts) == 3

        async def subtest_high_utilization():
            """Test reprovisioning and output when provisioning fails due to high
            provider utilization.
            """
            dummy_reqs = [
                {"name": "host1", "vcpus": 2, "memory": 4096},
                {"name": "host2", "vcpus": 2, "memory": 4096},
                {"name": "host3", "vcpus": 2, "memory": 4096},
            ]
            missing_dummy_reqs = [
                {"name": "host2", "vcpus": 2, "memory": 4096},
                {"name": "host3", "vcpus": 2, "memory": 4096},
            ]

            with patch.object(
                provider,
                "_provision_base",
                new_callable=AsyncMock,
                side_effect=lambda *args, **kwargs: (
                    [host1],
                    [hostA_500, hostB_500],
                    missing_dummy_reqs,
                ),
            ), patch.object(
                provider, "utilization", new_callable=AsyncMock, return_value=100
            ), patch.object(
                provider, "delete_hosts", new_callable=AsyncMock
            ) as mock_delete_hosts, patch(
                "asyncio.sleep", new_callable=AsyncMock
            ) as mock_sleep:
                (
                    success_hosts,
                    error_hosts,
                    missing_reqs,
                ) = await provider.strategy_retry(dummy_reqs)

                assert len(success_hosts) == 1
                assert len(error_hosts) == 2
                assert len(missing_reqs) == 2
                assert mock_sleep.mock.call_count == 3
                assert mock_delete_hosts.mock.call_count == 3
                # Assert that delete_hosts is called to delete all the hosts
                for call in mock_delete_hosts.mock.call_args_list:
                    called_error_hosts = call[0][0]
                    # error_hosts argument contains all hosts
                    assert len(called_error_hosts) == 3

        async def subtest_success():
            """Test successful provisioning output (no retry)"""
            dummy_reqs = [
                {"name": "host1", "vcpus": 2, "memory": 4096},
                {"name": "host2", "vcpus": 2, "memory": 4096},
                {"name": "host3", "vcpus": 2, "memory": 4096},
            ]

            with patch.object(
                provider,
                "_provision_base",
                new_callable=AsyncMock,
                return_value=([host1, host2, host3], [], []),
            ), patch.object(
                provider, "utilization", new_callable=AsyncMock, return_value=20
            ), patch.object(
                provider, "delete_hosts", new_callable=AsyncMock
            ) as mock_delete_hosts, patch(
                "asyncio.sleep", new_callable=AsyncMock
            ) as mock_sleep:
                (
                    success_hosts,
                    error_hosts,
                    missing_reqs,
                ) = await provider.strategy_retry(dummy_reqs)

                assert len(success_hosts) == 3
                assert not error_hosts
                assert not missing_reqs
                assert mock_sleep.mock.call_count == 0
                assert mock_delete_hosts.mock.call_count == 0

        async def subtest_reprovision_missing_one_by_one_error():
            """Test reprovisioning when provisioning fails."""
            dummy_reqs = [
                {"name": "host1", "vcpus": 2, "memory": 4096},
                {"name": "host2", "vcpus": 2, "memory": 4096},
                {"name": "host3", "vcpus": 2, "memory": 4096},
            ]
            missing_dummy_reqs = [
                {"name": "host3", "vcpus": 2, "memory": 4096},
            ]

            call_counts = [0]  # Initialize a list to store the call counts

            def provision_side_effect(*args, **kwargs):
                call_counts[0] += 1  # Increment the call count
                side_effects = {
                    1: ([host1], [host2, host3], dummy_reqs),
                    2: ([host1, host2], [host3], missing_dummy_reqs),
                    3: ([host3], [], []),
                }

                # return value based on call count simulate reprovision
                # to pass for only one host at the time
                return side_effects[call_counts[0]]

            with patch.object(
                provider,
                "_provision_base",
                new_callable=AsyncMock,
                side_effect=provision_side_effect,
            ), patch.object(
                provider, "utilization", new_callable=AsyncMock, return_value=50
            ), patch.object(
                provider, "delete_hosts", new_callable=AsyncMock
            ) as mock_delete_hosts, patch(
                "asyncio.sleep", new_callable=AsyncMock
            ) as mock_sleep:
                (
                    success_hosts,
                    error_hosts,
                    missing_reqs,
                ) = await provider.strategy_retry(dummy_reqs)

                assert len(success_hosts) == 3
                assert len(error_hosts) == 0
                assert len(missing_reqs) == 0
                assert mock_sleep.mock.call_count == 2
                assert mock_delete_hosts.mock.call_count == 2
                # Assert that delete_hosts is called
                # to delete all the hosts first for 3 hosts then for one
                assert [
                    len(c[0][0]) for c in mock_delete_hosts.mock.call_args_list
                ] == [3, 1]

        await subtest_500_error()
        await subtest_high_utilization()
        await subtest_success()
        await subtest_reprovision_missing_one_by_one_error()
