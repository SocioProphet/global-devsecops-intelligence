.PHONY: validate test manifest-validate manifest-write service-desk-metrics-validate model-fabric-release-readiness-validate github-footprint-itops-validate github-footprint-itops-generated-validate client-runtime-dump-exposure-validate operational-exhaust-fusion-validate resource-contract-telemetry-validate meshrush-events-validate mesh-consume incident-similarity-validate

validate: manifest-validate service-desk-metrics-validate model-fabric-release-readiness-validate github-footprint-itops-validate client-runtime-dump-exposure-validate operational-exhaust-fusion-validate resource-contract-telemetry-validate meshrush-events-validate incident-similarity-validate
	@echo "OK: validate"

manifest-validate:
	python3 tools/validate_manifest.py

manifest-write:
	python3 tools/validate_manifest.py --write

service-desk-metrics-validate:
	python3 tools/validate_service_desk_metrics.py

model-fabric-release-readiness-validate:
	python3 tools/validate_model_fabric_release_readiness.py

github-footprint-itops-generated-validate:
	python3 tools/generate_github_footprint_itops_projection.py

github-footprint-itops-validate: github-footprint-itops-generated-validate
	python3 tools/validate_github_footprint_itops.py

client-runtime-dump-exposure-validate:
	python3 tools/validate_client_runtime_dump_exposure.py

operational-exhaust-fusion-validate:
	python3 tools/validate_operational_exhaust_fusion.py

resource-contract-telemetry-validate:
	python3 tools/validate_resource_contract_telemetry.py

meshrush-events-validate:
	python3 tools/validate_meshrush_events.py

incident-similarity-validate:
	python3 tools/validate_incident_similarity.py


mesh-consume:
	python3 tools/mesh_consume.py

test:
	python3 -m pytest -q tools/tests
