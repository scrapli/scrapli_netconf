lint:
	python -m isort -rc -y scrapli_netconf/
	python -m isort -rc -y tests/
	python -m black scrapli_netconf/
	python -m black tests/
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

cov:
	python -m pytest \
	--cov=scrapli_netconf \
	--cov-report html \
	--cov-report term \
	tests/

cov_unit:
	python -m pytest \
	--cov=scrapli_netconf \
	--cov-report html \
	--cov-report term \
	tests/unit/

test:
	python -m pytest tests/

test_unit:
	python -m pytest tests/unit/

test_functional:
	python -m pytest tests/functional/
