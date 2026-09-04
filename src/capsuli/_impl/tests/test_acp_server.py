from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch
import pytest
from capsuli._impl.acp_server import ACPServer
from capsuli._impl.agent.agent_commands import StartCommand


@pytest.fixture
def mock_post_office() -> Generator[MagicMock, None, None]:
    with patch("capsuli._impl.acp_server.PostOffice") as mock:
        yield mock.return_value


@pytest.fixture
def server(mock_post_office: MagicMock) -> Generator[ACPServer, None, None]:
    server = ACPServer(MagicMock(), MagicMock())
    yield server
    server.stop()


def test_create_server(server: ACPServer) -> None:
    assert server.get_location().startswith("tcp:")
    assert server.get_location().endswith("9009")


def test_deposit_command(
    tmp_path: Path, mock_post_office: MagicMock, server: ACPServer
) -> None:
    command = StartCommand(
        "my_program",
        tmp_path,
        ["--help"],
        {"ENVVAR": "testing"},
        tmp_path / "stdout",
        tmp_path / "stderr",
    )
    server.deposit_command("node001", command)

    mock_post_office.deposit.assert_called_once()
    assert mock_post_office.deposit.call_args[0][0] == "node001"
