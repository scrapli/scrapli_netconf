lint:
	python -m isort scrapli_netconf/
	python -m isort tests/
	python -m black scrapli_netconf/
	python -m black tests/
	python -m pylama scrapli_netconf/
	python -m pydocstyle scrapli_netconf/
	python -m mypy scrapli_netconf/

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

.PHONY: docs
docs:
	python docs/generate/generate_docs.py

deploy_docs:
	mkdocs gh-deploy
