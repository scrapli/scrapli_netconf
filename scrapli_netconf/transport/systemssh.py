"""scrapli_netconf.transport.systemssh"""
import re
from typing import Any

from scrapli.decorators import OperationTimeout
from scrapli.exceptions import ScrapliAuthenticationFailed
from scrapli.transport import SystemSSHTransport
from scrapli.transport.ptyprocess import PtyProcess

HELLO_MATCH = re.compile(pattern=rb"<(\w+\:){0,1}hello", flags=re.I)


class NetconfSystemSSHTransport(SystemSSHTransport):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def _build_open_cmd(self) -> None:
        super()._build_open_cmd()
        self.open_cmd.extend(["-s", "netconf"])

    def open_netconf(self) -> bytes:
        """
        Netconf open method

        Several of the base SystemSSHTransport methods must be overridden in order to capture output
        of server capabilities that must be parsed.

        Args:
            N/A

        Returns:
            bytes: bytes output from server captured while opening the connection

        Raises:
            N/A

        """
        login_bytes = self._open_netconf_pty()
        return login_bytes

    def _open_netconf_pty(self) -> bytes:
        """
        Private method to open session with PtyProcess

        Args:
            N/A

        Returns:
            bytes: any output captured during login/authentication; needed to build server
                capabilities

        Raises:
            N/A

        """
        self.session = PtyProcess.spawn(self.open_cmd)
        self.logger.debug(f"Session to host {self.host} spawned")
        login_bytes: bytes = self._authenticate()
        self.logger.debug(f"Authenticated to host {self.host} successfully")
        return login_bytes

    @staticmethod
    def _authenticate_check_hello(output: bytes) -> bool:
        """
        Check if "hello" message is in output

        Args:
            output: bytes output from the channel

        Returns:
            bool: true if hello message is seen, otherwise false

        Raises:
            N/A

        """
        hello_match = re.search(pattern=HELLO_MATCH, string=output)
        if hello_match:
            return True
        return False

    @OperationTimeout("_timeout_ops", "Timed out looking for SSH login password prompt")
    def _authenticate(self) -> bytes:
        """
        Private method to check initial authentication when using pty_session

        Args:
            N/A

        Returns:
            N/A  # noqa: DAR202

        Raises:
            ScrapliAuthenticationFailed: if we see a password prompt more than once, or we got an
                unhandled EOF message

        """
        output = b""
        password_count = 0

        while True:
            try:
                new_output = self.session.read()
                output += new_output
                self.logger.debug(f"Attempting to authenticate. Read: {repr(new_output)}")
            except EOFError as exc:
                self._ssh_message_handler(output=output)
                # if _ssh_message_handler didn't raise any exception, we can raise the standard
                # -- did you disable strict key message/exception
                msg = (
                    f"Failed to open connection to host {self.host}. Do you need to disable "
                    "`auth_strict_key`?"
                )
                self.logger.critical(msg)
                raise ScrapliAuthenticationFailed(msg) from exc
            if b"password:" in output.lower():
                # if password is seen in the output, reset output and enter the password
                # count the times password occurs to have a decent idea if auth failed
                password_count += 1
                output = b""
                self.logger.info("Found password prompt, sending password")
                self.session.write(self.auth_password.encode())
                self.session.write(self._comms_return_char.encode())
            if password_count > 1:
                msg = (
                    "`password` seen multiple times during session establishment, "
                    "likely failed authentication"
                )
                raise ScrapliAuthenticationFailed(msg)
            if self._authenticate_check_hello(output=output):
                self.logger.info("Found start of server capabilities, authentication successful")
                self._isauthenticated = True
                return output
