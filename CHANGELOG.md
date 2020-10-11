CHANGELOG
=========

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
