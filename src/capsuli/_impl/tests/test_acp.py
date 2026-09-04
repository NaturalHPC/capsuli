from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock
import pytest
from capsuli._impl.acp_server import ACPServer
from capsuli._impl.agent.acp_client import ACPClient
from capsuli._impl.agent.agent_commands import CancelAllCommand
from capsuli._impl.agent.agent_commands import ShutdownCommand
from capsuli._impl.agent.agent_commands import StartCommand
from capsuli._impl.resources import Core
from capsuli._impl.resources import CoreSet
from capsuli._impl.resources import OnNodeResources


@pytest.fixture
def mock_resource_manager() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_fp_manager() -> MagicMock:
    return MagicMock()


@pytest.fixture
def real_server(
    mock_resource_manager: MagicMock,
    mock_fp_manager: MagicMock,
) -> Generator[ACPServer, None, None]:
    server = ACPServer(mock_resource_manager, mock_fp_manager)
    yield server
    server.stop()


@pytest.fixture
def connected_client(real_server: ACPServer) -> Generator[ACPClient, None, None]:
    client = ACPClient("node001", real_server.get_location())
    yield client
    client.close()


def test_report_resources(
    mock_resource_manager: MagicMock,
    connected_client: ACPClient,
) -> None:
    resources = OnNodeResources(
        "node001", CoreSet([Core(0, {0, 1, 2}), Core(1, {3, 4, 5})])
    )
    connected_client.report_resources(resources)

    mock_resource_manager.report_resources.assert_called_once()
    rec_res = mock_resource_manager.report_resources.call_args[0][0]
    assert rec_res == resources


def test_get_start_command(
    tmp_path: Path, real_server: ACPServer, connected_client: ACPClient
) -> None:
    sent_cmd = StartCommand(
        "program1",
        tmp_path,
        ["--test"],
        {"ENV": "for testing"},
        tmp_path / "out.txt",
        tmp_path / "err.txt",
    )
    real_server.deposit_command("node001", sent_cmd)
    recv_cmd = connected_client.get_command()

    assert recv_cmd == sent_cmd


def test_get_cancel_all_command(
    real_server: ACPServer, connected_client: ACPClient
) -> None:
    real_server.deposit_command("node001", CancelAllCommand())
    recv_cmd = connected_client.get_command()
    assert isinstance(recv_cmd, CancelAllCommand)


def test_get_shutdown_command(
    real_server: ACPServer, connected_client: ACPClient
) -> None:
    real_server.deposit_command("node001", ShutdownCommand())
    recv_cmd = connected_client.get_command()
    assert isinstance(recv_cmd, ShutdownCommand)


def test_report_result(
    real_server: ACPServer, connected_client: ACPClient, mock_fp_manager: MagicMock
) -> None:
    result = [("program1", 0), ("program2", 2)]
    connected_client.report_result(result)
    mock_fp_manager.report_result.assert_called_once_with(result)
