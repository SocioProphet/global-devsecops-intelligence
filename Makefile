.PHONY: validate test service-desk-metrics-validate model-fabric-release-readiness-validate

validate: service-desk-metrics-validate model-fabric-release-readiness-validate
	@echo "OK: validate"

service-desk-metrics-validate:
	python3 tools/validate_service_desk_metrics.py

model-fabric-release-readiness-validate:
	python3 tools/validate_model_fabric_release_readiness.py

test:
	python3 -m pytest -q tools/tests
