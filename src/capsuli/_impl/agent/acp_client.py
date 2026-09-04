from pathlib import Path
from typing import Any
from typing import cast
import msgpack
from nelambu import TcpTransportClient
from typing_extensions import Buffer
from capsuli._impl.agent.agent_commands import AgentCommand
from capsuli._impl.agent.agent_commands import CancelAllCommand
from capsuli._impl.agent.agent_commands import ShutdownCommand
from capsuli._impl.agent.agent_commands import StartCommand
from capsuli._impl.protocol import AgentCommandType
from capsuli._impl.protocol import RequestType
from capsuli._impl.protocol import ResponseType
from capsuli._impl.resources import OnNodeResources


class ACPClient:
    """The client for the Agent Control Protocol.

    This class connects to the ACPServer and communicates with it.
    """

    def __init__(self, node_name: str, location: str) -> None:
        """Create a MAPClient.

        Args:
            node_name: Name (hostname) of the local node
            location: A connection string of the form hostname:port
        """
        self._node_name = node_name
        self._transport_client = TcpTransportClient(location)

    def close(self) -> None:
        """Close the connection.

        This closes the connection. After this no other member functions can be called.
        """
        self._transport_client.close()

    def report_resources(self, resources: OnNodeResources) -> None:
        """Report local resources.

        Args:
            resources: Description of the resources on this node
        """
        enc_cpu_resources = [[c.cid, *list(c.hwthreads)] for c in resources.cpu_cores]
        request = [
            RequestType.REPORT_RESOURCES.value,
            resources.node_name,
            {"cpu": enc_cpu_resources},
        ]
        self._call_agent_manager(request)

    def get_command(self) -> AgentCommand | None:
        """Get a command from the agent manager.

        Returns:
            A command, or None if there are no commands pending.
        """
        request = [RequestType.GET_COMMAND.value, self._node_name]
        response = self._call_agent_manager(request)

        if response[0] == ResponseType.PENDING.value:
            return None

        command = cast("list", msgpack.unpackb(response[1], raw=False))

        if command[0] == AgentCommandType.START.value:
            name = command[1]
            workdir = Path(command[2])
            args = command[3]
            env = command[4]
            stdout = Path(command[5])
            stderr = Path(command[6])

            return StartCommand(name, workdir, args, env, stdout, stderr)

        if command[0] == AgentCommandType.CANCEL_ALL.value:
            return CancelAllCommand()

        if command[0] == AgentCommandType.SHUTDOWN.value:
            return ShutdownCommand()

        raise Exception("Unknown AgentCommand")

    def report_result(self, names_exit_codes: list[tuple[str, int]]) -> None:
        """Report results of finished processes.

        Args:
            names_exit_codes: A list of names and exit codes of finished processes.
        """
        request = [RequestType.REPORT_RESULT.value, names_exit_codes]
        self._call_agent_manager(request)

    def _call_agent_manager(self, request: Any) -> Any:
        """Call the manager and do en/decoding.

        Args:
            request: The request to encode and send

        Returns:
            The decoded response
        """
        encoded_request = cast("Buffer", msgpack.packb(request, use_bin_type=True))
        response = self._transport_client.call(encoded_request)
        return msgpack.unpackb(response, raw=False)
