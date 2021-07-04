CHANGELOG
=========

## (in development) 2021.07.30

- Force system transport ssh connections to allocate a tty (-tt); fixes issue that would prevent system transport 
  from sending any command > 1024 chars.
- Added `use_compressed_parser` argument to the driver constructor -- defaults to `True` which means we "squish" all 
  the whitespace out of any input we get from the user before sending it to the netconf server, generally this is no 
  problem, but some devices (looking at you NX-OS!) lock up and stop reading at some character counts (4096 in NX-OS 
  it seems) causing the connection to timeout and die. By *not* "squishing" whitespace out this does not happen.
- Fixed some typing issues and pinned to scrapli pre-release to take advantage of updated typing/packaging setup  
- Deprecate `filters` argument on `get_config` -- will be supported (by decorator) until 2022.01.30 (and 
  pre-releases). This was done to make the arguments consistent for `get`, `get_config`, and `rpc`.
- Better handling of multiple filter elements in a filter string
- Smarter message building -- previously most of the final bytes payload that we send to the servers got built in 
  the base driver class, and then some more (1.1 encoding) got added in the channel base class -- silly! Fixed this, 
  so it is all done in the driver which eliminated a bunch of duplication (yay!).
- Deprecating `comms_ansi` -- see also scrapli changelog for this release (2021.07.30) for more details. This was 
  never used here in scrapli_netconf so should be a non issue, but will not be fully deprecated until 2022.01.30.
- Re-fix #10... see #68 -- now there is a test with a comment so I don't break this again :)
- Added `copy_config` method, thanks to Roman Dodin for adding this in scrapligo first!
- Added handling/warning about `use_compressed_parser` if we catch a timeout exception when looking for prompt after 
  writing inputs -- since I don't know (can't know?) which platforms may require this flag set to False this seems 
  like a reasonable way to let users know and point them in the right direction to get things working!
- Reswizzled the echo check to be like the scrapligo version -- much simpler/less moving parts, so should be good!


# 2021.01.30

- Big overhaul in line with the scrapli core overhaul... mostly this was about reconciliation of the channel and 
  transport things and putting stuff where it should have been in the first place... see the changelog at scrapli 
  core for much more details
- *FUTURE BREAKING CHANGE* -- `NetconfScrape` and `AsyncNetconfScrape` have been renamed to `NetconfDriver` and 
  `AsyncNetconfDriver` -- there are alias classes so you can continue to use `NetconfScrape` and 
  `AsyncNetconfScrape` but there is a warning, and these will be removed at some point in the future!


# 2021.01.17

- Support for future "vrouter" setup for testing
- Flatten all channel inputs (no pretty printed xml) -- seems to behave much more nicely across the board!
- Updated test to match some recent scrapli core updates (multipl easync transports)


# 2020.11.15

- Support namespaces in hello messages -- primarily to support "rfc-compliant" mode in JunOS -- thank you 
 [Gary Napier](https://github.com/napierg) for finding this and coming up with the fix!
- Another fixup to chunk checker -- think that the itty bitty chunk issues have now been solved :)


# 2020.10.24

- Improve the "echo" checker -- and add this for sync as well, because...
- SSH2 and Paramiko are now supported transports!
- As part of the "improved echo checker" sync channel now also overrides the read_until_input method like the async
 channel does -- again, for the same reasons.
- All transports minus system are now optional extras -- this means that asyncssh is no longer an install requirement
- As expected with above point -- added optional extras install options in setup.py as well as a "full" option just
 like scrapli core
- MAYBE BREAKING CHANGE: shouldn't be an issue for 99.9999% of people, however, the asyncssh transport is no longer
 imported and available in the transport package
- Add `error_messages` attribute to response object -- initialized as an empty list and the text of any `rpc-error/error
-message` fields are placed into this list if there are any in the response from the server
- Improve netconf 1.1 chunk matching regex to not ignore/chop off Nokia error messages that contained `#` symbols


# 2020.10.10

- Handle netconf 1.1 devices that have chunk sizes of 1
- Ensure results are "pretty printed"
- Above two items were worked out with thanks to Hugo Tinoco! PS - this has been tested on Nokia devices now too!
- Hopefully improved asyncssh "echo checker" (see _check_echo) method in async_channel for details
- Update CI to use 3.9 instead of 3.9-dev (and update deprecated set-env)
- Remove transport session locks


# 2020.09.23

- Strip server capabilities so we don't save capabilities with newlines/whitespace
- Add `validate` and `delete_config` methods


# 2020.09.18

- Fix some pins for dev requirements
- Add 3.9-dev to actions
- Fix `scrapli-asycnssh` not in setup.py `install_requires`
- Retest everything! In general, just get this updated/ready for `nornir-scrapli`!


# 2020.07.26

- Update to match scrapli core -- moved to updated timeout decorator, fixed a test to match a better exception message


# 2020.07.12

- Minor improvements to response recording (should be a tick faster)
- Update decorators for async things to use the improved `async_operation_timeout` in scrapli 2020.07.12
- Set `strip_namespaces` to `False` for `AsyncNetconfScrape` for consistency/sanity
- Update a few dev pins, update required pins to ensure no major lxml updates break things


# 2020.07.04

- First real release??? :)


# 2020.04.19

- Initial pypi release... very beta still
