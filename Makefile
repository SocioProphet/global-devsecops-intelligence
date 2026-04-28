.PHONY: validate test

validate:
	python3 tools/validate_service_desk_metrics.py

test:
	python3 -m pytest -q tools/tests
