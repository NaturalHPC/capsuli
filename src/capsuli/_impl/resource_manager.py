from capsuli._impl.resources import OnNodeResources


class ResourceManager:
    """Receives and holds a description of available resources."""

    def __init__(self) -> None:
        """Create a ResourceManager."""
        # TODO: implementation

    def report_resources(self, resources: OnNodeResources) -> None:
        """Receive and set available resources.

        Called by ACPServer from a server thread.
        """
        # TODO: implementation
