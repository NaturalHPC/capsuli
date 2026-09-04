class FinishedProcessManager:
    """Tracks finished processes.

    This is just a little helper class that sits between the ACPServer and Capsuli
    classes. The ACPServer's threads pass it newly finished processes, and Capsuli picks
    those up when requested.
    """

    def __init__(self) -> None:
        """Create a FinishedProcessManager."""
        # TODO: implement

    def report_result(self, names_exit_codes: list[tuple[str, int]]) -> None:
        """Report results of finished processes.

        Called by ACPServer from a server thread.

        Args:
            names_exit_codes: A list of names and exit codes of finished processes.
        """
        # TODO: implement
