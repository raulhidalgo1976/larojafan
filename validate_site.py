#!/usr/bin/env python3
"""Smoke checks for generated output before publishing."""
from pathlib import Path
p=Path('docs')
for name in ('index.html','players/index.html','tournaments/index.html','about/index.html','privacy/index.html','sitemap.xml','robots.txt'):
    if not (p/name).is_file(): raise SystemExit(f'Missing generated file: {name}')
for name in ('index.html','players/index.html'):
    text=(p/name).read_text()
    if 'rel="canonical"' not in text: raise SystemExit('Missing canonical')
print('Generated site checks passed')

# Confirm configured analytics ID is present in the generated script and privacy draft text is absent.
import json
config=json.loads(Path('config.json').read_text())
js=(p/'analytics.js').read_text()
if config['ga4_measurement_id'] not in js: raise SystemExit('GA4 ID missing from generated analytics script')
if '__GA4_MEASUREMENT_ID__' in js: raise SystemExit('Unresolved GA4 template')
if 'must be reviewed by the site operator' in (p/'privacy/index.html').read_text(): raise SystemExit('Privacy draft text still present')
