.PHONY: validate test service-desk-metrics-validate model-fabric-release-readiness-validate github-footprint-itops-validate client-runtime-dump-exposure-validate

validate: service-desk-metrics-validate model-fabric-release-readiness-validate github-footprint-itops-validate client-runtime-dump-exposure-validate
	@echo "OK: validate"

service-desk-metrics-validate:
	python3 tools/validate_service_desk_metrics.py

model-fabric-release-readiness-validate:
	python3 tools/validate_model_fabric_release_readiness.py

github-footprint-itops-validate:
	python3 tools/validate_github_footprint_itops.py

client-runtime-dump-exposure-validate:
	python3 tools/validate_client_runtime_dump_exposure.py

test:
	python3 -m pytest -q tools/tests
