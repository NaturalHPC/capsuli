from collections.abc import Generator
from pathlib import Path
from typing import cast
from unittest.mock import MagicMock
from unittest.mock import patch
import msgpack
import pytest
from capsuli._impl.agent.acp_client import ACPClient
from capsuli._impl.agent.agent_commands import CancelAllCommand
from capsuli._impl.agent.agent_commands import ShutdownCommand
from capsuli._impl.agent.agent_commands import StartCommand
from capsuli._impl.resources import Core
from capsuli._impl.resources import CoreSet
from capsuli._impl.resources import OnNodeResources


@pytest.fixture
def mock_transport_client() -> Generator[MagicMock, None, None]:
    with patch("capsuli._impl.agent.acp_client.TcpTransportClient") as mock:
        yield mock.return_value


@pytest.fixture
def client(mock_transport_client: MagicMock) -> Generator[ACPClient, None, None]:
    client = ACPClient("node001", "tcp:location:9009")
    assert client._transport_client == mock_transport_client
    yield client
    client.close()


def test_create_client(mock_transport_client: MagicMock, client: ACPClient) -> None:
    assert client._node_name == "node001"
    assert client._transport_client == mock_transport_client


def test_report_resources(mock_transport_client: MagicMock, client: ACPClient) -> None:
    mock_transport_client.call.return_value = b"\0"
    core_set = CoreSet([Core(0, {0, 1}), Core(1, {2, 3})])
    resources = OnNodeResources("node001", core_set)
    client.report_resources(resources)
    mock_transport_client.call.assert_called_once()
    sent = cast(
        "list", msgpack.unpackb(mock_transport_client.call.call_args[0][0], raw=False)
    )
    assert sent[0] == 1
    assert sent[1] == "node001"
    assert sent[2]["cpu"][0] == [0, 0, 1]
    assert sent[2]["cpu"][1] == [1, 2, 3]


def test_get_start_command(mock_transport_client: MagicMock, client: ACPClient) -> None:
    command = [
        1,
        "my_program",
        "/work",
        ["echo", "-e"],
        {"ENVVAR": "test"},
        "/work/stdout",
        "/work/stderr",
    ]
    response = [0, msgpack.packb(command, use_bin_type=True)]
    response_bytes = msgpack.packb(response, use_bin_type=True)
    mock_transport_client.call.return_value = response_bytes

    command = client.get_command()
    assert isinstance(command, StartCommand)
    assert command.name == "my_program"
    assert command.work_dir == Path("/work")
    assert command.args == ["echo", "-e"]
    assert command.env == {"ENVVAR": "test"}
    assert command.stdout == Path("/work/stdout")
    assert command.stderr == Path("/work/stderr")


def test_get_cancel_all_command(
    mock_transport_client: MagicMock, client: ACPClient
) -> None:
    command = [2]
    response = [0, msgpack.packb(command, use_bin_type=True)]
    response_bytes = msgpack.packb(response, use_bin_type=True)
    mock_transport_client.call.return_value = response_bytes

    command = client.get_command()
    assert isinstance(command, CancelAllCommand)


def test_get_shutdown_command(
    mock_transport_client: MagicMock, client: ACPClient
) -> None:
    command = [3]
    response = [0, msgpack.packb(command, use_bin_type=True)]
    response_bytes = msgpack.packb(response, use_bin_type=True)
    mock_transport_client.call.return_value = response_bytes

    command = client.get_command()
    assert isinstance(command, ShutdownCommand)


def test_report_result(mock_transport_client: MagicMock, client: ACPClient) -> None:
    mock_transport_client.call.return_value = b"\0"
    client.report_result([("my_program1", 0), ("my_program2", -9)])

    mock_transport_client.call.assert_called_once()
    sent = cast(
        "list", msgpack.unpackb(mock_transport_client.call.call_args[0][0], raw=False)
    )
    assert sent[0] == 3
    assert sent[1] == [["my_program1", 0], ["my_program2", -9]]
