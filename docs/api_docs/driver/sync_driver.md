<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module scrapli_netconf.driver.sync_driver

scrapli_netconf.driver.sync_driver

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""scrapli_netconf.driver.sync_driver"""
from typing import Any, Callable, Dict, List, Optional, Union

from lxml.etree import _Element

from scrapli import Driver
from scrapli_netconf.channel.base_channel import NetconfBaseChannelArgs
from scrapli_netconf.channel.sync_channel import NetconfChannel
from scrapli_netconf.driver.base_driver import NetconfBaseDriver
from scrapli_netconf.response import NetconfResponse


class NetconfDriver(Driver, NetconfBaseDriver):
    # kinda hate this but need to tell mypy that channel in netconf land is in fact a channel of
    # type `NetconfChannel`
    channel: NetconfChannel

    def __init__(
        self,
        host: str,
        port: int = 830,
        strip_namespaces: bool = False,
        strict_datastores: bool = False,
        auth_username: str = "",
        auth_password: str = "",
        auth_private_key: str = "",
        auth_private_key_passphrase: str = "",
        auth_strict_key: bool = True,
        auth_bypass: bool = False,
        timeout_socket: float = 15.0,
        timeout_transport: float = 30.0,
        timeout_ops: float = 30.0,
        comms_prompt_pattern: str = r"^[a-z0-9.\-@()/:]{1,48}[#>$]\s*$",
        comms_return_char: str = "\n",
        ssh_config_file: Union[str, bool] = False,
        ssh_known_hosts_file: Union[str, bool] = False,
        on_init: Optional[Callable[..., Any]] = None,
        on_open: Optional[Callable[..., Any]] = None,
        on_close: Optional[Callable[..., Any]] = None,
        transport: str = "system",
        transport_options: Optional[Dict[str, Any]] = None,
        channel_log: Union[str, bool] = False,
        channel_lock: bool = False,
        preferred_netconf_version: Optional[str] = None,
        use_compressed_parser: bool = True,
    ) -> None:
        super().__init__(
            host=host,
            port=port,
            auth_username=auth_username,
            auth_password=auth_password,
            auth_private_key=auth_private_key,
            auth_private_key_passphrase=auth_private_key_passphrase,
            auth_strict_key=auth_strict_key,
            auth_bypass=auth_bypass,
            timeout_socket=timeout_socket,
            timeout_transport=timeout_transport,
            timeout_ops=timeout_ops,
            comms_prompt_pattern=comms_prompt_pattern,
            comms_return_char=comms_return_char,
            ssh_config_file=ssh_config_file,
            ssh_known_hosts_file=ssh_known_hosts_file,
            on_init=on_init,
            on_open=on_open,
            on_close=on_close,
            transport=transport,
            transport_options=transport_options,
            channel_log=channel_log,
            channel_lock=channel_lock,
        )

        _preferred_netconf_version = self._determine_preferred_netconf_version(
            preferred_netconf_version=preferred_netconf_version
        )
        _preferred_xml_parser = self._determine_preferred_xml_parser(
            use_compressed_parser=use_compressed_parser
        )
        self._netconf_base_channel_args = NetconfBaseChannelArgs(
            netconf_version=_preferred_netconf_version, xml_parser=_preferred_xml_parser
        )

        self.channel = NetconfChannel(
            transport=self.transport,
            base_channel_args=self._base_channel_args,
            netconf_base_channel_args=self._netconf_base_channel_args,
        )

        self.strip_namespaces = strip_namespaces
        self.strict_datastores = strict_datastores
        self.server_capabilities: List[str] = []
        self.readable_datastores: List[str] = []
        self.writeable_datastores: List[str] = []
        self.message_id = 101

    def open(self) -> None:
        """
        Open netconf connection to server

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        self._pre_open_closing_log(closing=False)

        self.transport.open_netconf()

        # in the future this and scrapli core should just have a class attribute of the transports
        # that require this "in channel" auth so we can dynamically figure that out rather than
        # just look at the name of the transport
        if "system" in self.transport_name:
            self.channel.channel_authenticate_netconf(
                auth_password=self.auth_password,
                auth_private_key_passphrase=self.auth_private_key_passphrase,
            )

        self.channel.open_netconf()

        self._build_readable_datastores()
        self._build_writeable_datastores()

        self._post_open_closing_log(closing=False)

    def get(self, filter_: str, filter_type: str = "subtree") -> NetconfResponse:
        """
        Netconf get operation

        Args:
            filter_: filter to apply to the get
            filter_type: type of filter; subtree|xpath

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_get(filter_=filter_, filter_type=filter_type)
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def get_config(
        self,
        source: str = "running",
        filter_: Optional[str] = None,
        filter_type: str = "subtree",
        default_type: Optional[str] = None,
    ) -> NetconfResponse:
        """
        Netconf get-config operation

        Args:
            source: configuration source to get; typically one of running|startup|candidate
            filter_: string of filter(s) to apply to configuration
            filter_type: type of filter; subtree|xpath
            default_type: string of with-default mode to apply when retrieving configuration

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_get_config(
            source=source, filter_=filter_, filter_type=filter_type, default_type=default_type
        )
        raw_response = self.channel.send_input_netconf(response.channel_input)

        response.record_response(raw_response)
        return response

    def edit_config(self, config: str, target: str = "running") -> NetconfResponse:
        """
        Netconf get-config operation

        Args:
            config: configuration to send to device
            target: configuration source to target; running|startup|candidate

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_edit_config(config=config, target=target)
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def delete_config(self, target: str = "candidate") -> NetconfResponse:
        """
        Netconf delete-config operation

        Args:
            target: configuration source to target; startup|candidate

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_delete_config(target=target)
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def commit(self) -> NetconfResponse:
        """
        Netconf commit config operation

        Args:
            N/A

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_commit()
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def discard(self) -> NetconfResponse:
        """
        Netconf discard config operation

        Args:
            N/A

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_discard()
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def lock(self, target: str) -> NetconfResponse:
        """
        Netconf lock operation

        Args:
            target: configuration source to target; running|startup|candidate

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_lock(target=target)
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def unlock(self, target: str) -> NetconfResponse:
        """
        Netconf unlock operation

        Args:
            target: configuration source to target; running|startup|candidate

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_unlock(target=target)
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def rpc(self, filter_: Union[str, _Element]) -> NetconfResponse:
        """
        Netconf "rpc" operation

        Typically used with juniper devices or if you want to build/send your own payload in a more
        manual fashion. You can provide a string that will be loaded as an lxml element, or you can
        provide an lxml element yourself.

        Args:
            filter_: filter/rpc to execute

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_rpc(filter_=filter_)
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def validate(self, source: str) -> NetconfResponse:
        """
        Netconf "validate" operation

        Args:
            source: configuration source to validate; typically one of running|startup|candidate

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_validate(source=source)
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def copy_config(self, source: str, target: str) -> NetconfResponse:
        """
        Netconf "copy-config" operation

        Args:
            source: configuration, url, or datastore to copy into the target datastore
            target: destination to copy the source to

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_copy_config(source=source, target=target)
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response
        </code>
    </pre>
</details>




## Classes

### NetconfDriver


```text
BaseDriver Object

BaseDriver is the root for all Scrapli driver classes. The synchronous and asyncio driver
base driver classes can be used to provide a semi-pexpect like experience over top of
whatever transport a user prefers. Generally, however, the base driver classes should not be
used directly. It is best to use the GenericDriver (or AsyncGenericDriver) or NetworkDriver
(or AsyncNetworkDriver) sub-classes of the base drivers.

Args:
    host: host ip/name to connect to
    port: port to connect to
    auth_username: username for authentication
    auth_private_key: path to private key for authentication
    auth_private_key_passphrase: passphrase for decrypting ssh key if necessary
    auth_password: password for authentication
    auth_strict_key: strict host checking or not
    auth_bypass: bypass "in channel" authentication -- only supported with telnet,
        asynctelnet, and system transport plugins
    timeout_socket: timeout for establishing socket/initial connection in seconds
    timeout_transport: timeout for ssh|telnet transport in seconds
    timeout_ops: timeout for ssh channel operations
    comms_prompt_pattern: raw string regex pattern -- preferably use `^` and `$` anchors!
        this is the single most important attribute here! if this does not match a prompt,
        scrapli will not work!
        IMPORTANT: regex search uses multi-line + case insensitive flags. multi-line allows
        for highly reliably matching for prompts however we do NOT strip trailing whitespace
        for each line, so be sure to add '\\s?' or similar if your device needs that. This
        should be mostly sorted for you if using network drivers (i.e. `IOSXEDriver`).
        Lastly, the case insensitive is just a convenience factor so i can be lazy.
    comms_return_char: character to use to send returns to host
    ssh_config_file: string to path for ssh config file, True to use default ssh config file
        or False to ignore default ssh config file
    ssh_known_hosts_file: string to path for ssh known hosts file, True to use default known
        file locations. Only applicable/needed if `auth_strict_key` is set to True
    on_init: callable that accepts the class instance as its only argument. this callable,
        if provided, is executed as the last step of object instantiation -- its purpose is
        primarily to provide a mechanism for scrapli community platforms to have an easy way
        to modify initialization arguments/object attributes without needing to create a
        class that extends the driver, instead allowing the community platforms to simply
        build from the GenericDriver or NetworkDriver classes, and pass this callable to do
        things such as appending to a username (looking at you RouterOS!!). Note that this
        is *always* a synchronous function (even for asyncio drivers)!
    on_open: callable that accepts the class instance as its only argument. this callable,
        if provided, is executed immediately after authentication is completed. Common use
        cases for this callable would be to disable paging or accept any kind of banner
        message that prompts a user upon connection
    on_close: callable that accepts the class instance as its only argument. this callable,
        if provided, is executed immediately prior to closing the underlying transport.
        Common use cases for this callable would be to save configurations prior to exiting,
        or to logout properly to free up vtys or similar
    transport: name of the transport plugin to use for the actual telnet/ssh/netconf
        connection. Available "core" transports are:
            - system
            - telnet
            - asynctelnet
            - ssh2
            - paramiko
            - asyncssh
        Please see relevant transport plugin section for details. Additionally third party
        transport plugins may be available.
    transport_options: dictionary of options to pass to selected transport class; see
        docs for given transport class for details of what to pass here
    channel_lock: True/False to lock the channel (threading.Lock/asyncio.Lock) during
        any channel operations, defaults to False
    channel_log: True/False or a string path to a file of where to write out channel logs --
        these are not "logs" in the normal logging module sense, but only the output that is
        read from the channel. In other words, the output of the channel log should look
        similar to what you would see as a human connecting to a device
    channel_log_mode: "write"|"append", all other values will raise ValueError,
        does what it sounds like it should by setting the channel log to the provided mode
    logging_uid: unique identifier (string) to associate to log messages; useful if you have
        multiple connections to the same device (i.e. one console, one ssh, or one to each
        supervisor module, etc.)

Returns:
    None

Raises:
    N/A
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class NetconfDriver(Driver, NetconfBaseDriver):
    # kinda hate this but need to tell mypy that channel in netconf land is in fact a channel of
    # type `NetconfChannel`
    channel: NetconfChannel

    def __init__(
        self,
        host: str,
        port: int = 830,
        strip_namespaces: bool = False,
        strict_datastores: bool = False,
        auth_username: str = "",
        auth_password: str = "",
        auth_private_key: str = "",
        auth_private_key_passphrase: str = "",
        auth_strict_key: bool = True,
        auth_bypass: bool = False,
        timeout_socket: float = 15.0,
        timeout_transport: float = 30.0,
        timeout_ops: float = 30.0,
        comms_prompt_pattern: str = r"^[a-z0-9.\-@()/:]{1,48}[#>$]\s*$",
        comms_return_char: str = "\n",
        ssh_config_file: Union[str, bool] = False,
        ssh_known_hosts_file: Union[str, bool] = False,
        on_init: Optional[Callable[..., Any]] = None,
        on_open: Optional[Callable[..., Any]] = None,
        on_close: Optional[Callable[..., Any]] = None,
        transport: str = "system",
        transport_options: Optional[Dict[str, Any]] = None,
        channel_log: Union[str, bool] = False,
        channel_lock: bool = False,
        preferred_netconf_version: Optional[str] = None,
        use_compressed_parser: bool = True,
    ) -> None:
        super().__init__(
            host=host,
            port=port,
            auth_username=auth_username,
            auth_password=auth_password,
            auth_private_key=auth_private_key,
            auth_private_key_passphrase=auth_private_key_passphrase,
            auth_strict_key=auth_strict_key,
            auth_bypass=auth_bypass,
            timeout_socket=timeout_socket,
            timeout_transport=timeout_transport,
            timeout_ops=timeout_ops,
            comms_prompt_pattern=comms_prompt_pattern,
            comms_return_char=comms_return_char,
            ssh_config_file=ssh_config_file,
            ssh_known_hosts_file=ssh_known_hosts_file,
            on_init=on_init,
            on_open=on_open,
            on_close=on_close,
            transport=transport,
            transport_options=transport_options,
            channel_log=channel_log,
            channel_lock=channel_lock,
        )

        _preferred_netconf_version = self._determine_preferred_netconf_version(
            preferred_netconf_version=preferred_netconf_version
        )
        _preferred_xml_parser = self._determine_preferred_xml_parser(
            use_compressed_parser=use_compressed_parser
        )
        self._netconf_base_channel_args = NetconfBaseChannelArgs(
            netconf_version=_preferred_netconf_version, xml_parser=_preferred_xml_parser
        )

        self.channel = NetconfChannel(
            transport=self.transport,
            base_channel_args=self._base_channel_args,
            netconf_base_channel_args=self._netconf_base_channel_args,
        )

        self.strip_namespaces = strip_namespaces
        self.strict_datastores = strict_datastores
        self.server_capabilities: List[str] = []
        self.readable_datastores: List[str] = []
        self.writeable_datastores: List[str] = []
        self.message_id = 101

    def open(self) -> None:
        """
        Open netconf connection to server

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        self._pre_open_closing_log(closing=False)

        self.transport.open_netconf()

        # in the future this and scrapli core should just have a class attribute of the transports
        # that require this "in channel" auth so we can dynamically figure that out rather than
        # just look at the name of the transport
        if "system" in self.transport_name:
            self.channel.channel_authenticate_netconf(
                auth_password=self.auth_password,
                auth_private_key_passphrase=self.auth_private_key_passphrase,
            )

        self.channel.open_netconf()

        self._build_readable_datastores()
        self._build_writeable_datastores()

        self._post_open_closing_log(closing=False)

    def get(self, filter_: str, filter_type: str = "subtree") -> NetconfResponse:
        """
        Netconf get operation

        Args:
            filter_: filter to apply to the get
            filter_type: type of filter; subtree|xpath

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_get(filter_=filter_, filter_type=filter_type)
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def get_config(
        self,
        source: str = "running",
        filter_: Optional[str] = None,
        filter_type: str = "subtree",
        default_type: Optional[str] = None,
    ) -> NetconfResponse:
        """
        Netconf get-config operation

        Args:
            source: configuration source to get; typically one of running|startup|candidate
            filter_: string of filter(s) to apply to configuration
            filter_type: type of filter; subtree|xpath
            default_type: string of with-default mode to apply when retrieving configuration

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_get_config(
            source=source, filter_=filter_, filter_type=filter_type, default_type=default_type
        )
        raw_response = self.channel.send_input_netconf(response.channel_input)

        response.record_response(raw_response)
        return response

    def edit_config(self, config: str, target: str = "running") -> NetconfResponse:
        """
        Netconf get-config operation

        Args:
            config: configuration to send to device
            target: configuration source to target; running|startup|candidate

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_edit_config(config=config, target=target)
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def delete_config(self, target: str = "candidate") -> NetconfResponse:
        """
        Netconf delete-config operation

        Args:
            target: configuration source to target; startup|candidate

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_delete_config(target=target)
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def commit(self) -> NetconfResponse:
        """
        Netconf commit config operation

        Args:
            N/A

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_commit()
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def discard(self) -> NetconfResponse:
        """
        Netconf discard config operation

        Args:
            N/A

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_discard()
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def lock(self, target: str) -> NetconfResponse:
        """
        Netconf lock operation

        Args:
            target: configuration source to target; running|startup|candidate

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_lock(target=target)
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def unlock(self, target: str) -> NetconfResponse:
        """
        Netconf unlock operation

        Args:
            target: configuration source to target; running|startup|candidate

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_unlock(target=target)
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def rpc(self, filter_: Union[str, _Element]) -> NetconfResponse:
        """
        Netconf "rpc" operation

        Typically used with juniper devices or if you want to build/send your own payload in a more
        manual fashion. You can provide a string that will be loaded as an lxml element, or you can
        provide an lxml element yourself.

        Args:
            filter_: filter/rpc to execute

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_rpc(filter_=filter_)
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def validate(self, source: str) -> NetconfResponse:
        """
        Netconf "validate" operation

        Args:
            source: configuration source to validate; typically one of running|startup|candidate

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_validate(source=source)
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def copy_config(self, source: str, target: str) -> NetconfResponse:
        """
        Netconf "copy-config" operation

        Args:
            source: configuration, url, or datastore to copy into the target datastore
            target: destination to copy the source to

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_copy_config(source=source, target=target)
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli.driver.base.sync_driver.Driver
- scrapli_netconf.driver.base_driver.NetconfBaseDriver
- scrapli.driver.base.base_driver.BaseDriver
#### Class variables

    
`channel: scrapli_netconf.channel.sync_channel.NetconfChannel`



#### Methods

    

##### commit
`commit(self) ‑> scrapli_netconf.response.NetconfResponse`

```text
Netconf commit config operation

Args:
    N/A

Returns:
    NetconfResponse: scrapli_netconf NetconfResponse object

Raises:
    N/A
```



    

##### copy_config
`copy_config(self, source: str, target: str) ‑> scrapli_netconf.response.NetconfResponse`

```text
Netconf "copy-config" operation

Args:
    source: configuration, url, or datastore to copy into the target datastore
    target: destination to copy the source to

Returns:
    NetconfResponse: scrapli_netconf NetconfResponse object

Raises:
    N/A
```



    

##### delete_config
`delete_config(self, target: str = 'candidate') ‑> scrapli_netconf.response.NetconfResponse`

```text
Netconf delete-config operation

Args:
    target: configuration source to target; startup|candidate

Returns:
    NetconfResponse: scrapli_netconf NetconfResponse object

Raises:
    N/A
```



    

##### discard
`discard(self) ‑> scrapli_netconf.response.NetconfResponse`

```text
Netconf discard config operation

Args:
    N/A

Returns:
    NetconfResponse: scrapli_netconf NetconfResponse object

Raises:
    N/A
```



    

##### edit_config
`edit_config(self, config: str, target: str = 'running') ‑> scrapli_netconf.response.NetconfResponse`

```text
Netconf get-config operation

Args:
    config: configuration to send to device
    target: configuration source to target; running|startup|candidate

Returns:
    NetconfResponse: scrapli_netconf NetconfResponse object

Raises:
    N/A
```



    

##### get
`get(self, filter_: str, filter_type: str = 'subtree') ‑> scrapli_netconf.response.NetconfResponse`

```text
Netconf get operation

Args:
    filter_: filter to apply to the get
    filter_type: type of filter; subtree|xpath

Returns:
    NetconfResponse: scrapli_netconf NetconfResponse object

Raises:
    N/A
```



    

##### get_config
`get_config(self, source: str = 'running', filter_: Optional[str] = None, filter_type: str = 'subtree', default_type: Optional[str] = None) ‑> scrapli_netconf.response.NetconfResponse`

```text
Netconf get-config operation

Args:
    source: configuration source to get; typically one of running|startup|candidate
    filter_: string of filter(s) to apply to configuration
    filter_type: type of filter; subtree|xpath
    default_type: string of with-default mode to apply when retrieving configuration

Returns:
    NetconfResponse: scrapli_netconf NetconfResponse object

Raises:
    N/A
```



    

##### lock
`lock(self, target: str) ‑> scrapli_netconf.response.NetconfResponse`

```text
Netconf lock operation

Args:
    target: configuration source to target; running|startup|candidate

Returns:
    NetconfResponse: scrapli_netconf NetconfResponse object

Raises:
    N/A
```



    

##### open
`open(self) ‑> None`

```text
Open netconf connection to server

Args:
    N/A

Returns:
    None

Raises:
    N/A
```



    

##### rpc
`rpc(self, filter_: Union[str, lxml.etree._Element]) ‑> scrapli_netconf.response.NetconfResponse`

```text
Netconf "rpc" operation

Typically used with juniper devices or if you want to build/send your own payload in a more
manual fashion. You can provide a string that will be loaded as an lxml element, or you can
provide an lxml element yourself.

Args:
    filter_: filter/rpc to execute

Returns:
    NetconfResponse: scrapli_netconf NetconfResponse object

Raises:
    N/A
```



    

##### unlock
`unlock(self, target: str) ‑> scrapli_netconf.response.NetconfResponse`

```text
Netconf unlock operation

Args:
    target: configuration source to target; running|startup|candidate

Returns:
    NetconfResponse: scrapli_netconf NetconfResponse object

Raises:
    N/A
```



    

##### validate
`validate(self, source: str) ‑> scrapli_netconf.response.NetconfResponse`

```text
Netconf "validate" operation

Args:
    source: configuration source to validate; typically one of running|startup|candidate

Returns:
    NetconfResponse: scrapli_netconf NetconfResponse object

Raises:
    N/A
```