lint:
	python -m isort -rc -y scrapli_netconf/
	python -m black scrapli_netconf/
	python -m pylama scrapli_netconf/
	python -m pydocstyle scrapli_netconf/
	python -m mypy scrapli_netconf/

.PHONY: docs
docs:
	rm -rf docs/scrapli_netconf
	python -m pdoc \
	--html \
	--output-dir docs \
	scrapli_netconf \
	--force