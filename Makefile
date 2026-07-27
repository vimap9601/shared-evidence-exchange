PYTHON ?= python

.PHONY: test demo validate

test:
	$(PYTHON) -m unittest discover -s tests -v

demo:
	$(PYTHON) scripts/initialize_project.py ./AI_EXCHANGE

validate:
	$(PYTHON) scripts/validate_exchange.py ./examples/technical-audit
