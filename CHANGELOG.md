CHANGELOG
=========

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
