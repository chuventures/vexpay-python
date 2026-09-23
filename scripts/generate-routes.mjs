// Emits src/vexpay/_generated/routes.py — operationId → (method, path) and the
// success response model — from the SDK OpenAPI snapshot.
//
// Usage: node scripts/generate-routes.mjs <openapi.json> <routes.py>
import { readFileSync, writeFileSync } from 'node:fs';

const [input, output] = process.argv.slice(2);
if (!input || !output) {
  console.error('usage: generate-routes.mjs <openapi.json> <routes.py>');
  process.exit(2);
}

const METHODS = ['get', 'put', 'post', 'patch', 'delete'];
const doc = JSON.parse(readFileSync(input, 'utf8'));
const rows = [];
for (const [path, item] of Object.entries(doc.paths)) {
  for (const method of METHODS) {
    const op = item[method];
    if (!op?.operationId) continue;
    const success = Object.entries(op.responses ?? {})
      .filter(([code]) => /^2\d\d$/.test(code))
      .map(([, response]) => response.content?.['application/json']?.schema?.$ref)
      .find(Boolean);
    const model = success ? success.split('/').pop() : null;
    rows.push([op.operationId, method.toUpperCase(), path, model]);
  }
}
rows.sort(([a], [b]) => a.localeCompare(b));

const routes = rows.map(([id, method, path]) => `    "${id}": ("${method}", "${path}"),`).join('\n');
const models = rows
  .map(([id, , , model]) => `    "${id}": ${model ? `"${model}"` : 'None'},`)
  .join('\n');

writeFileSync(
  output,
  `# Generated from packages/sdk-spec/openapi.json by scripts/generate-routes.mjs — do not edit.
from __future__ import annotations

from typing import Optional

ROUTES: dict[str, tuple[str, str]] = {
${routes}
}

#: Success response schema per operation (None: inline or empty body).
RESPONSE_MODELS: dict[str, Optional[str]] = {
${models}
}
`,
  'utf8',
);
