.PHONY: fmt
fmt:
	poetry run black custom_components
	poetry run isort --profile black custom_components

.PHONY: lint
lint: fmt
	poetry run pylint custom_components