CHANGELOG
=========

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
