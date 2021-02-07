<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module scrapli_netconf.driver.async_driver

scrapli_netconf.driver.async_driver

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""scrapli_netconf.driver.async_driver"""
from typing import Any, Callable, Dict, List, Optional, Union
from warnings import warn

from scrapli import AsyncDriver
from scrapli_netconf.channel.async_channel import AsyncNetconfChannel
from scrapli_netconf.channel.base_channel import NetconfBaseChannelArgs
from scrapli_netconf.constants import NetconfVersion
from scrapli_netconf.driver.base_driver import NetconfBaseDriver
from scrapli_netconf.response import NetconfResponse


class AsyncNetconfDriver(AsyncDriver, NetconfBaseDriver):
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
        comms_ansi: bool = False,
        ssh_config_file: Union[str, bool] = False,
        ssh_known_hosts_file: Union[str, bool] = False,
        on_init: Optional[Callable[..., Any]] = None,
        on_open: Optional[Callable[..., Any]] = None,
        on_close: Optional[Callable[..., Any]] = None,
        transport: str = "system",
        transport_options: Optional[Dict[str, Any]] = None,
        channel_log: Union[str, bool] = False,
        channel_lock: bool = False,
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
            comms_ansi=comms_ansi,
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
        self._netconf_base_channel_args = NetconfBaseChannelArgs(
            netconf_version=NetconfVersion.UNKNOWN
        )
        self.channel = AsyncNetconfChannel(
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

    async def open(self) -> None:
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

        await self.transport.open_netconf()
        await self.channel.open_netconf()

        self._build_readable_datastores()
        self._build_writeable_datastores()

        self._post_open_closing_log(closing=False)

    async def get(self, filter_: str, filter_type: str = "subtree") -> NetconfResponse:
        """
        Netconf get operation

        Args:
            filter_: string filter to apply to the get
            filter_type: type of filter; subtree|xpath

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_get(filter_=filter_, filter_type=filter_type)
        raw_response = await self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    async def get_config(
        self,
        source: str = "running",
        filters: Optional[Union[str, List[str]]] = None,
        filter_type: str = "subtree",
    ) -> NetconfResponse:
        """
        Netconf get-config operation

        Args:
            source: configuration source to get; typically one of running|startup|candidate
            filters: string or list of strings of filters to apply to configuration
            filter_type: type of filter; subtree|xpath

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_get_config(source=source, filters=filters, filter_type=filter_type)
        raw_response = await self.channel.send_input_netconf(response.channel_input)

        response.record_response(raw_response)
        return response

    async def edit_config(self, config: str, target: str = "running") -> NetconfResponse:
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
        raw_response = await self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    async def delete_config(self, target: str = "candidate") -> NetconfResponse:
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
        raw_response = await self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    async def commit(self) -> NetconfResponse:
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
        raw_response = await self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    async def discard(self) -> NetconfResponse:
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
        raw_response = await self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    async def lock(self, target: str) -> NetconfResponse:
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
        raw_response = await self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    async def unlock(self, target: str) -> NetconfResponse:
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
        raw_response = await self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    async def rpc(self, filter_: str) -> NetconfResponse:
        """
        Netconf "rpc" operation; typically only used with juniper devices

        You can also use this to build send your own payload in a more manual fashion

        Args:
            filter_: filter/rpc to execute

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_rpc(filter_=filter_)
        raw_response = await self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    async def validate(self, source: str) -> NetconfResponse:
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
        raw_response = await self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response


# remove in future releases, retaining this to not break end user scripts for now
class AsyncNetconfScrape(AsyncNetconfDriver):
    warning = (
        "`NetconfScrape` has been renamed `NetconfDriver`, `NetconfScrape` will be deprecated in "
        "future releases!"
    )

    def __init_subclass__(cls) -> None:
        """Deprecate AsyncNetconfScrape"""
        warn(cls.warning, DeprecationWarning, 2)

    def __new__(cls, *args, **kwargs) -> "AsyncNetconfDriver":  # type: ignore
        warn(cls.warning, DeprecationWarning, 2)
        return AsyncNetconfDriver(*args, **kwargs)
        </code>
    </pre>
</details>



## Classes

### AsyncNetconfDriver


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
    comms_ansi: True/False strip comms_ansi characters from output, generally the default
        value of False should be fine
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
class AsyncNetconfDriver(AsyncDriver, NetconfBaseDriver):
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
        comms_ansi: bool = False,
        ssh_config_file: Union[str, bool] = False,
        ssh_known_hosts_file: Union[str, bool] = False,
        on_init: Optional[Callable[..., Any]] = None,
        on_open: Optional[Callable[..., Any]] = None,
        on_close: Optional[Callable[..., Any]] = None,
        transport: str = "system",
        transport_options: Optional[Dict[str, Any]] = None,
        channel_log: Union[str, bool] = False,
        channel_lock: bool = False,
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
            comms_ansi=comms_ansi,
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
        self._netconf_base_channel_args = NetconfBaseChannelArgs(
            netconf_version=NetconfVersion.UNKNOWN
        )
        self.channel = AsyncNetconfChannel(
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

    async def open(self) -> None:
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

        await self.transport.open_netconf()
        await self.channel.open_netconf()

        self._build_readable_datastores()
        self._build_writeable_datastores()

        self._post_open_closing_log(closing=False)

    async def get(self, filter_: str, filter_type: str = "subtree") -> NetconfResponse:
        """
        Netconf get operation

        Args:
            filter_: string filter to apply to the get
            filter_type: type of filter; subtree|xpath

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_get(filter_=filter_, filter_type=filter_type)
        raw_response = await self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    async def get_config(
        self,
        source: str = "running",
        filters: Optional[Union[str, List[str]]] = None,
        filter_type: str = "subtree",
    ) -> NetconfResponse:
        """
        Netconf get-config operation

        Args:
            source: configuration source to get; typically one of running|startup|candidate
            filters: string or list of strings of filters to apply to configuration
            filter_type: type of filter; subtree|xpath

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_get_config(source=source, filters=filters, filter_type=filter_type)
        raw_response = await self.channel.send_input_netconf(response.channel_input)

        response.record_response(raw_response)
        return response

    async def edit_config(self, config: str, target: str = "running") -> NetconfResponse:
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
        raw_response = await self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    async def delete_config(self, target: str = "candidate") -> NetconfResponse:
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
        raw_response = await self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    async def commit(self) -> NetconfResponse:
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
        raw_response = await self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    async def discard(self) -> NetconfResponse:
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
        raw_response = await self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    async def lock(self, target: str) -> NetconfResponse:
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
        raw_response = await self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    async def unlock(self, target: str) -> NetconfResponse:
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
        raw_response = await self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    async def rpc(self, filter_: str) -> NetconfResponse:
        """
        Netconf "rpc" operation; typically only used with juniper devices

        You can also use this to build send your own payload in a more manual fashion

        Args:
            filter_: filter/rpc to execute

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_rpc(filter_=filter_)
        raw_response = await self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    async def validate(self, source: str) -> NetconfResponse:
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
        raw_response = await self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli.driver.base.async_driver.AsyncDriver
- scrapli_netconf.driver.base_driver.NetconfBaseDriver
- scrapli.driver.base.base_driver.BaseDriver
#### Descendants
- scrapli_netconf.driver.async_driver.AsyncNetconfScrape
#### Class variables

    
`host: str`




    
`readable_datastores: List[str]`




    
`strict_datastores: bool`




    
`strip_namespaces: bool`




    
`writeable_datastores: List[str]`



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
    filter_: string filter to apply to the get
    filter_type: type of filter; subtree|xpath

Returns:
    NetconfResponse: scrapli_netconf NetconfResponse object

Raises:
    N/A
```



    

##### get_config
`get_config(self, source: str = 'running', filters: Union[str, List[str], NoneType] = None, filter_type: str = 'subtree') ‑> scrapli_netconf.response.NetconfResponse`

```text
Netconf get-config operation

Args:
    source: configuration source to get; typically one of running|startup|candidate
    filters: string or list of strings of filters to apply to configuration
    filter_type: type of filter; subtree|xpath

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
`open(self) ‑> NoneType`

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
`rpc(self, filter_: str) ‑> scrapli_netconf.response.NetconfResponse`

```text
Netconf "rpc" operation; typically only used with juniper devices

You can also use this to build send your own payload in a more manual fashion

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





### AsyncNetconfScrape


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
    comms_ansi: True/False strip comms_ansi characters from output, generally the default
        value of False should be fine
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
class AsyncNetconfScrape(AsyncNetconfDriver):
    warning = (
        "`NetconfScrape` has been renamed `NetconfDriver`, `NetconfScrape` will be deprecated in "
        "future releases!"
    )

    def __init_subclass__(cls) -> None:
        """Deprecate AsyncNetconfScrape"""
        warn(cls.warning, DeprecationWarning, 2)

    def __new__(cls, *args, **kwargs) -> "AsyncNetconfDriver":  # type: ignore
        warn(cls.warning, DeprecationWarning, 2)
        return AsyncNetconfDriver(*args, **kwargs)
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli_netconf.driver.async_driver.AsyncNetconfDriver
- scrapli.driver.base.async_driver.AsyncDriver
- scrapli_netconf.driver.base_driver.NetconfBaseDriver
- scrapli.driver.base.base_driver.BaseDriver
#### Class variables

    
`host: str`




    
`readable_datastores: List[str]`




    
`strict_datastores: bool`




    
`strip_namespaces: bool`




    
`warning`




    
`writeable_datastores: List[str]`