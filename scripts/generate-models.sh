#!/usr/bin/env bash
# Generates Pydantic v2 models from the SDK OpenAPI snapshot.
# Usage: scripts/generate-models.sh <openapi.json> <models.py>
# Pinned generator (0.40.0: last line tested that still targets Python 3.9) + fixed header so `pnpm sdk:check` output is byte-stable.
set -euo pipefail

input="${1:?usage: generate-models.sh <openapi.json> <models.py>}"
output="${2:?usage: generate-models.sh <openapi.json> <models.py>}"

uvx --from datamodel-code-generator==0.40.0 datamodel-codegen \
  --input "$input" \
  --input-file-type openapi \
  --output "$output" \
  --output-model-type pydantic_v2.BaseModel \
  --target-python-version 3.9 \
  --use-standard-collections \
  --use-schema-description \
  --use-field-description \
  --field-constraints \
  --enum-field-as-literal all \
  --use-double-quotes \
  --type-mappings "string+uuid=string" \
  --strict-nullable \
  --disable-timestamp \
  --custom-file-header "# Generated from packages/sdk-spec/openapi.json by scripts/generate-models.sh — do not edit."
