lint:
	python -m isort .
	python -m black .
	python -m pylama .
	python -m pydocstyle .
	python -m mypy --strict scrapli_netconf/

darglint:
	find scrapli_cfg -type f \( -iname "*.py"\) | xargs darglint -x

test:
	python -m pytest \
	tests/

cov:
	python -m pytest \
	--cov=scrapli_netconf \
	--cov-report html \
	--cov-report term \
	tests/

test_unit:
	python -m pytest \
	tests/unit/

cov_unit:
	python -m pytest \
	--cov=scrapli_netconf \
	--cov-report html \
	--cov-report term \
	tests/unit/

test_functional:
	python -m pytest \
	tests/functional/

cov_functional:
	python -m pytest \
	--cov=scrapli_netconf \
	--cov-report html \
	--cov-report term \
	tests/functional/

.PHONY: docs
docs:
	python docs/generate/generate_docs.py

deploy_docs:
	mkdocs gh-deploy
