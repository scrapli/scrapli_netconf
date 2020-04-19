"""scrapli_netconf.transport.netconf"""
from logging import getLogger
from subprocess import Popen
from typing import TYPE_CHECKING, Any

from scrapli.decorators import operation_timeout
from scrapli.exceptions import ScrapliAuthenticationFailed
from scrapli.transport import SystemSSHTransport
from scrapli.transport.ptyprocess import PtyProcess

if TYPE_CHECKING:
    PopenBytes = Popen[bytes]  # pylint: disable=E1136

LOG = getLogger("transport")


class NetconfTransport(SystemSSHTransport):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def _build_open_cmd(self) -> None:
        super()._build_open_cmd()
        self.open_cmd.extend(["-s", "netconf"])

    def open_netconf(self) -> bytes:
        """
        Netconf open method

        Netconf seems to always force a pty which means that scrapli cannot use its preferred
        `open_pipes` method of connecting to the server. This means that we always force the open
        method to open via pty, and due to this several of the base SystemSSHTransport methods must
        be overridden in order to properly authenticate via password or key, as well as to capture
        output of server capabilities that must be parsed.

        Args:
            N/A

        Returns:
            login_bytes: bytes output from server captured while opening the connection

        Raises:
            N/A

        """
        self.session_lock.acquire()

        login_bytes = self._open_netconf_pty()

        if self.keepalive:
            self._session_keepalive()

        return login_bytes

    def _open_netconf_pty(self) -> bytes:
        """
        Private method to open session with PtyProcess

        Args:
            N/A

        Returns:
            bool: True/False session was opened and authenticated

        Raises:
            N/A

        """
        self.session = PtyProcess.spawn(self.open_cmd)
        LOG.debug(f"Session to host {self.host} spawned")
        self.session_lock.release()
        login_bytes: bytes = self._pty_authenticate(self.session)
        LOG.debug(f"Authenticated to host {self.host} successfully")
        return login_bytes

    @operation_timeout("_timeout_ops", "Timed out looking for SSH login password prompt")
    def _pty_authenticate(self, pty_session: PtyProcess) -> bytes:
        """
        Private method to check initial authentication when using pty_session

        Args:
            pty_session: PtyProcess session object

        Returns:
            N/A  # noqa: DAR202

        Raises:
            ScrapliAuthenticationFailed: if we receive an EOFError -- this usually indicates that
                host key checking is enabled and failed.

        """
        self.session_lock.acquire()
        output = b""
        password_count = 0
        while True:
            try:
                new_output = pty_session.read()
                output += new_output
                LOG.debug(f"Attempting to authenticate. Read: {repr(new_output)}")
            except EOFError:
                msg = f"Failed to open connection to host {self.host}"
                if b"Host key verification failed" in output:
                    msg = f"Host key verification failed for host {self.host}"
                elif b"Operation timed out" in output:
                    msg = f"Timed out connecting to host {self.host}"
                LOG.critical(msg)
                raise ScrapliAuthenticationFailed(msg)
            if b"password:" in output.lower():
                # if password is seen in the output, reset output and enter the password
                # count the times password occurs to have a decent idea if auth failed
                password_count += 1
                output = b""
                LOG.info("Found password prompt, sending password")
                pty_session.write(self.auth_password.encode())
                pty_session.write(self._comms_return_char.encode())
            if password_count > 1:
                msg = (
                    "`password` seen multiple times during session establishment, "
                    "likely failed authentication"
                )
                raise ScrapliAuthenticationFailed(msg)
            if b"<hello" in output.lower():
                LOG.info("Found start of server capabilities, authentication successful")
                self.session_lock.release()
                return output

    def _keepalive_network(self) -> None:
        """
        Override _keepalive_network from scrapli; not supported with netconf

        Args:
            N/A

        Returns:
            N/A  # noqa: DAR202

        Raises:
            N/A

        """

    def _keepalive_standard(self) -> None:
        """
        Send "out of band" (protocol level) keepalives to devices.

        Args:
            N/A

        Returns:
            N/A  # noqa: DAR202

        Raises:
            N/A

        """
