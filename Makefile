PYTHON ?= python

.PHONY: test demo validate coverage

test:
	$(PYTHON) -m unittest discover -s tests -v

demo:
	$(PYTHON) scripts/initialize_project.py ./AI_EXCHANGE

validate:
	$(PYTHON) scripts/validate_exchange.py ./examples/technical-audit

coverage:
	$(PYTHON) scripts/check_evidence_coverage.py ./examples/technical-audit/01_GOVERNING_STATE/EVIDENCE_MANIFEST.json
