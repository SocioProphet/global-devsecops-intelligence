# Changelog

All notable changes to `global-devsecops-intelligence` are tracked here.

## Unreleased

- Added IBM ITOPS external seed metadata and curated GLO profile excerpt.
- Added GitHub-footprint / website-surface ITOPS alignment profile and sample instance pack.
- Added operational-exhaust and trader-agent fusion profile.
- Added service-desk metrics and model-fabric release-readiness validators.
- Added GitHub-footprint ITOPS smoke checks and validator.
- Regenerated `MANIFEST.txt` from the tracked file list and documented its inclusion rule in the file itself.
- Added `tools/validate_manifest.py` plus `manifest-validate` / `manifest-write` targets so manifest drift fails `make validate` in both directions.
- Added `.gitignore` for Python bytecode and pytest caches so local test runs cannot be swept into the tracked tree or the manifest.
