from enum import Enum


class RequestType(Enum):
    """Identifier for different types of request.

    This provides a means to encode requests types for the Agent Control Protocol.
    """

    REPORT_RESOURCES = 1
    GET_COMMAND = 2
    REPORT_RESULT = 3


class ResponseType(Enum):
    """Identifier for different types of response.

    Identifiers for different kinds of responses to requests.
    """

    # TODO: check which are used here
    SUCCESS = 0
    ERROR = 1
    PENDING = 2


class AgentCommandType(Enum):
    """Identifier for different types of commands.

    These are requested from the manager by the agent, and tell it what to do. Part
    of the Agent Control Protocol, used in the response to RequestType.GET_COMMAND.
    """

    START = 1
    CANCEL_ALL = 2
    SHUTDOWN = 3
