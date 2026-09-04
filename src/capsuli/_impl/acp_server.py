import errno
import logging
from typing import Any
from typing import cast
import msgpack
from nelambu import RequestHandler
from nelambu import TcpTransportServer
from typing_extensions import Buffer
from capsuli._impl.agent.agent_commands import AgentCommand
from capsuli._impl.agent.agent_commands import CancelAllCommand
from capsuli._impl.agent.agent_commands import ShutdownCommand
from capsuli._impl.agent.agent_commands import StartCommand
from capsuli._impl.finished_process_manager import FinishedProcessManager
from capsuli._impl.post_office import PostOffice
from capsuli._impl.protocol import AgentCommandType
from capsuli._impl.protocol import RequestType
from capsuli._impl.protocol import ResponseType
from capsuli._impl.resource_manager import ResourceManager
from capsuli._impl.resources import Core
from capsuli._impl.resources import CoreSet
from capsuli._impl.resources import OnNodeResources

_logger = logging.getLogger(__name__)


class ACPRequestHandler(RequestHandler):
    """Handles Agent requests."""

    def __init__(
        self,
        resource_manager: ResourceManager,
        post_office: PostOffice,
        fp_manager: FinishedProcessManager,
    ) -> None:
        """Create a MAPRequestHandler.

        Args:
            resource_manager: The ResourceManager to report resources to
            post_office: The PostOffice to get commands from
            fp_manager: The FinishedProcessManager to report finished processes to
        """
        self._resource_manager = resource_manager
        self._post_office = post_office
        self._fp_manager = fp_manager

    def handle_request(self, request: Buffer) -> Buffer:
        """Handles an agent request.

        Args:
            request: The encoded request

        Returns:
            response: An encoded response
        """
        req_list = cast("list", msgpack.unpackb(request, raw=False))
        req_type = req_list[0]
        req_args = req_list[1:]
        if req_type == RequestType.REPORT_RESOURCES.value:
            response = self._report_resources(*req_args)
        elif req_type == RequestType.GET_COMMAND.value:
            response = self._get_command(*req_args)
        elif req_type == RequestType.REPORT_RESULT.value:
            response = self._report_result(*req_args)

        return cast("Buffer", msgpack.packb(response, use_bin_type=True))

    def _report_resources(self, node_name: str, data: dict[str, Any]) -> Any:
        """Handle a report resources request.

        This is used by the agent to report available resources on its node when
        it starts up.

        Args:
            node_name: Name (hostname) of the node
            data: Resource dictionary, containing a single key 'cpu' which maps to a
                list of cores, where each core is a list of ints, starting with the core
                id at index [0] followed by the hwthread ids of all hwthreads in this
                core.
        """
        cores = CoreSet(Core(ids[0], set(ids[1:])) for ids in data["cpu"])
        node_resources = OnNodeResources(node_name, cores)
        self._resource_manager.report_resources(node_resources)
        return [ResponseType.SUCCESS.value]

    def _get_command(self, node_name: str) -> Any:
        """Handle a get command request.

        This is used by the agent to ask if there's anything we would like it to do.
        Command sounds a bit brusque, but we already have the agent sending requests
        to this handler, so I needed a different word to distinguish them. Requests
        are sent by the agent to the manager (because it's the client in an RPC setup),
        commands are returned by the manager to the agent (because it tells it what to
        do).

        Args:
            node_name: Hostname (name) of the agent's node
        """
        if self._post_office.have_message(node_name):
            next_command = self._post_office.get_message(node_name)
            return [ResponseType.SUCCESS.value, next_command]

        return [ResponseType.PENDING.value]

    def _report_result(self, instances: list[list[Any]]) -> Any:
        """Handle a report result request.

        This is sent by the agent if an instance it launched exited.

        Args:
            instances: List of instance descriptions, comprising an id str and exit
                    code int. Really a list[Tuple[str, int]] but msgpack doesn't know
                    about tuples.
        """
        self._fp_manager.report_result(list(map(tuple, instances)))
        return [ResponseType.SUCCESS.value]


class ACPServer:
    """The Agent Control Protocol server.

    This class accepts connections from the agents and services them using an
    ACPRequestHandler.
    """

    def __init__(
        self, resource_manager: ResourceManager, fp_manager: FinishedProcessManager
    ) -> None:
        """Create an ACPServer.

        This starts a TCP Transport server and connects it to an ACPRequestHandler,
        which uses the given agent manager to service the requests. By default, we
        listen on port 9009, unless it's not available in which case we use a random
        other one.

        Args:
            resource_manager: ResourceManager to report resources to
            fp_manager: FinishedProcessManager to report finished processes to
        """
        self._post_office = PostOffice()
        self._handler = ACPRequestHandler(
            resource_manager, self._post_office, fp_manager
        )
        try:
            self._server = TcpTransportServer(self._handler, 9009)
        except OSError as e:
            if e.errno != errno.EADDRINUSE:
                raise
            self._server = TcpTransportServer(self._handler)

    def get_location(self) -> str:
        """Return this server's network location.

        This is a string of the form tcp:<hostname>:<port>.
        """
        return self._server.get_location()

    def stop(self) -> None:
        """Stop the server.

        This makes the server stop serving requests, and shuts down its
        background threads.
        """
        self._server.close()

    def deposit_command(self, node_name: str, command: AgentCommand) -> None:
        """Deposit a command for the given agent.

        This takes the given command and queues it for the given agent to pick up next
        time it asks us for one.

        Args:
            node_name: Name of the node whose agent should execute the command
            command: The command to send
        """
        if isinstance(command, StartCommand):
            command_obj = [
                AgentCommandType.START.value,
                command.name,
                str(command.work_dir),
                command.args,
                command.env,
                str(command.stdout),
                str(command.stderr),
            ]
        elif isinstance(command, CancelAllCommand):
            command_obj = [AgentCommandType.CANCEL_ALL.value]
        elif isinstance(command, ShutdownCommand):
            command_obj = [AgentCommandType.SHUTDOWN.value]

        encoded_command = cast("bytes", msgpack.packb(command_obj, use_bin_type=True))

        self._post_office.deposit(node_name, encoded_command)
