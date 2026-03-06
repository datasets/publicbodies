# FRESHNESS_CHECK

- Repo: `publicbodies`
- Checked on: `2026-03-02`

## Located Files
- README: `README.md`
- Datapackage: `data/datapackage.json`
- Auto-update scripts: `scripts/deploy/prepare_build.py; scripts/import/br/import_br.py; scripts/import/it/import_it.py; scripts/maintenance/domain_to_url.py; scripts/maintenance/se/generate_ids.py; scripts/maintenance/se/simpleslugger.py; scripts/migrate/process.py`

## Dataset Description
- A database of public bodies (or organizations) around the world, such as government departments, ministries etc.

## Steps Taken
- 1. Read README and datapackage (when present) to identify dataset purpose and source references.
- 2. Inspected update scripts to locate automatic refresh pipelines and hardcoded source URLs.
- 3. Scanned local data files for max date/year values.
- 4. Probed upstream source URLs and extracted latest available date from payload or Last-Modified header.
- 5. Compared local latest vs upstream latest and recorded staleness verdict.

## Source Probes
- URL: `https://datahub.io/core/publicbodies` | relevant: `false` | reachable: `true` | status: `200` | latest inferred: `unknown` | reason: `ok`
- URL: `https://badgen.net/badge/icon/View%20on%20datahub.io/orange?icon=https://datahub.io/datahub-cube-badge-icon.svg&label&scale=1.25` | relevant: `false` | reachable: `true` | status: `200` | latest inferred: `2000-12-31` | reason: `ok`
- URL: `https://github.com/okfn/publicbodies/actions/workflows/frictionless.yaml/badge.svg` | relevant: `false` | reachable: `true` | status: `200` | latest inferred: `2000-12-31` | reason: `ok`
- URL: `https://repository.frictionlessdata.io/report?user=okfn&repo=publicbodies&flow=publicbodies` | relevant: `false` | reachable: `false` | status: `404` | latest inferred: `unknown` | reason: `HTTP 404`
- URL: `https://publicbodies.org/` | relevant: `false` | reachable: `false` | status: `404` | latest inferred: `unknown` | reason: `HTTP 404`
- URL: `https://github.com/okfn/publicbodies/issues` | relevant: `false` | reachable: `true` | status: `200` | latest inferred: `unknown` | reason: `ok`
- URL: `https://specs.frictionlessdata.io/` | relevant: `false` | reachable: `true` | status: `200` | latest inferred: `2024-06-26` | reason: `ok`
- URL: `https://docs.docker.com/get-docker/` | relevant: `false` | reachable: `true` | status: `200` | latest inferred: `2026-03-02` | reason: `ok`
- URL: `https://github.com/okfn/publicbodies` | relevant: `false` | reachable: `true` | status: `200` | latest inferred: `unknown` | reason: `ok`
- URL: `https://dados.gov.br/dataset/siorg` | relevant: `true` | reachable: `true` | status: `200` | latest inferred: `2026-02-18` | reason: `ok`
- URL: `https://www.asktheeu.org/` | relevant: `false` | reachable: `false` | status: `429` | latest inferred: `unknown` | reason: `HTTP 429`
- URL: `https://indicepa.gov.it/ipa-dati/dataset/amministrazioni` | relevant: `true` | reachable: `true` | status: `200` | latest inferred: `unknown` | reason: `ok`

## Freshness Result
- Latest local date: `unknown`
- Latest upstream date: `2026-02-18`
- Assessment: No local date detected, while upstream has data through 2026-02-18
