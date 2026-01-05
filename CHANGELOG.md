# Changelog

## [2.22.0](https://github.com/Flagsmith/edge-proxy/compare/v2.21.2...v2.22.0) (2026-01-05)


### Features

* use-context-evaluation-with-newest-engine-version ([#182](https://github.com/Flagsmith/edge-proxy/issues/182)) ([da33db3](https://github.com/Flagsmith/edge-proxy/commit/da33db33f6b8df6c9361b45733ee278ca1ad469b))

## [2.21.2](https://github.com/Flagsmith/edge-proxy/compare/v2.21.1...v2.21.2) (2025-11-19)


### Dependency Updates

* update flagsmith-flag-engine to 6.1.0 ([70ddbef](https://github.com/Flagsmith/edge-proxy/commit/70ddbefd3e51d1f2b1f94e51211862bf08a0660d))

## [2.21.1](https://github.com/Flagsmith/edge-proxy/compare/v2.21.0...v2.21.1) (2025-09-25)


### Bug Fixes

* Deleted identity overrides not synchronised ([#170](https://github.com/Flagsmith/edge-proxy/issues/170)) ([c105be6](https://github.com/Flagsmith/edge-proxy/commit/c105be67e421655501f8af08191ec9f731d01f8b))


### CI

* Integrate release-please ([#171](https://github.com/Flagsmith/edge-proxy/issues/171)) ([2f7d449](https://github.com/Flagsmith/edge-proxy/commit/2f7d44986a890c5def08f15314e3f0e102c35de7))


### Other

* add root CODEOWNERS ([#166](https://github.com/Flagsmith/edge-proxy/issues/166)) ([615a359](https://github.com/Flagsmith/edge-proxy/commit/615a3594f6b8a53f238ea520fe497b1ce6e2877d))

<a name="v2.21.0"></a>
## [v2.21.0](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.21.0) - 19 Aug 2025

## What's Changed
* chore: bumped-version-and-regenerated-lock-files by [@Zaimwa9](https://github.com/Zaimwa9) in https://github.com/Flagsmith/edge-proxy/pull/163
* fix: enable follow_redirects for httpx client to handle 307 status codes by [@GuyGitzMagen](https://github.com/GuyGitzMagen) in https://github.com/Flagsmith/edge-proxy/pull/164
* [pre-commit.ci] pre-commit autoupdate by [@pre-commit-ci](https://github.com/pre-commit-ci)[bot] in https://github.com/Flagsmith/edge-proxy/pull/162

## New Contributors
* [@Zaimwa9](https://github.com/Zaimwa9) made their first contribution in https://github.com/Flagsmith/edge-proxy/pull/163
* [@GuyGitzMagen](https://github.com/GuyGitzMagen) made their first contribution in https://github.com/Flagsmith/edge-proxy/pull/164

**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.20.0...v2.21.0

[Changes][v2.21.0]


<a name="v2.20.0"></a>
## [v2.20.0](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.20.0) - 18 Jul 2025

## What's Changed
* feat: Add environment document endpoint by [@rolodato](https://github.com/rolodato) in https://github.com/Flagsmith/edge-proxy/pull/150
* [pre-commit.ci] pre-commit autoupdate by [@pre-commit-ci](https://github.com/pre-commit-ci)[bot] in https://github.com/Flagsmith/edge-proxy/pull/158


**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.19.0...v2.20.0

[Changes][v2.20.0]


<a name="v2.19.0"></a>
## [v2.19.0](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.19.0) - 30 Apr 2025

## What's Changed

* feat: Set If-Modified-Since header for environment document requests by [@rolodato](https://github.com/rolodato) in https://github.com/Flagsmith/edge-proxy/pull/159. This requires Flagsmith v2.176.0 or later.


**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.18.0...v2.19.0

[Changes][v2.19.0]


<a name="v2.18.0"></a>
## [v2.18.0](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.18.0) - 08 Apr 2025

## What's Changed

* fix: Do not crash when running with unknown environment variables [@matthewelwell](https://github.com/matthewelwell) in https://github.com/Flagsmith/edge-proxy/pull/141
* fix: Warning when running edge-proxy-render-config by [@rolodato](https://github.com/rolodato) in https://github.com/Flagsmith/edge-proxy/pull/142
* feat: Immediately exit if configuration is missing or invalid by [@rolodato](https://github.com/rolodato) in https://github.com/Flagsmith/edge-proxy/pull/148
* feat: Add liveness and readiness check endpoints. Return 503 instead of 500 when checks fail by [@rolodato](https://github.com/rolodato) in https://github.com/Flagsmith/edge-proxy/pull/151
* feat: Add `server.proxy_headers` option by [@rolodato](https://github.com/rolodato) in https://github.com/Flagsmith/edge-proxy/pull/154


**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.17.0...v2.18.0

[Changes][v2.18.0]


<a name="v2.17.0"></a>
## [v2.17.0](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.17.0) - 19 Dec 2024

## What's Changed
* feat: Add GET /api/v1/identities endpoint by [@rolodato](https://github.com/rolodato) in https://github.com/Flagsmith/edge-proxy/pull/135

## New Contributors
* [@rolodato](https://github.com/rolodato) made their first contribution in https://github.com/Flagsmith/edge-proxy/pull/135

**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.16.0...v2.17.0

[Changes][v2.17.0]


<a name="v2.16.0"></a>
## [v2.16.0](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.16.0) - 20 Nov 2024

## What's Changed
* [pre-commit.ci] pre-commit autoupdate by [@pre-commit-ci](https://github.com/pre-commit-ci) in https://github.com/Flagsmith/edge-proxy/pull/127
* feat: Bypass server-side filtering for server keys by [@MCPx](https://github.com/MCPx) in https://github.com/Flagsmith/edge-proxy/pull/130
* [pre-commit.ci] pre-commit autoupdate by [@pre-commit-ci](https://github.com/pre-commit-ci) in https://github.com/Flagsmith/edge-proxy/pull/131

## New Contributors
* [@MCPx](https://github.com/MCPx) made their first contribution in https://github.com/Flagsmith/edge-proxy/pull/130

**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.15.1...v2.16.0

[Changes][v2.16.0]


<a name="v2.15.1"></a>
## [v2.15.1](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.15.1) - 04 Oct 2024

## What's Changed
* [pre-commit.ci] pre-commit autoupdate by [@pre-commit-ci](https://github.com/pre-commit-ci) in https://github.com/Flagsmith/edge-proxy/pull/124
* ci: use new org-level dockerhub token by [@matthewelwell](https://github.com/matthewelwell) in https://github.com/Flagsmith/edge-proxy/pull/126


**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.15.0...v2.15.1

[Changes][v2.15.1]


<a name="v2.15.0"></a>
## [v2.15.0](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.15.0) - 04 Sep 2024

## What's Changed
* docs: add example docker-compose.yml by [@matthewelwell](https://github.com/matthewelwell) in https://github.com/Flagsmith/edge-proxy/pull/121
* feat: remove unnecessary setting `health_check.count_stale_documents_as_failing` by [@matthewelwell](https://github.com/matthewelwell) in https://github.com/Flagsmith/edge-proxy/pull/123

BREAKING CHANGES

Undocumented settings `health_check.count_stale_documents_as_failing` and `health_check.grace_period_seconds` have been removed. 

**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.14.0...v2.15.0

[Changes][v2.15.0]


<a name="v2.14.0"></a>
## [v2.14.0](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.14.0) - 04 Sep 2024

## What's Changed
* feat: make health check configurable by [@matthewelwell](https://github.com/matthewelwell) in https://github.com/Flagsmith/edge-proxy/pull/122


**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.13.0...v2.14.0

[Changes][v2.14.0]


<a name="v2.13.0"></a>
## [Version 2.13.0 (v2.13.0)](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.13.0) - 18 Jun 2024

## What's Changed
* feat: Add identity overrides support by [@khvn26](https://github.com/khvn26) in https://github.com/Flagsmith/edge-proxy/pull/110
* feat: Customised logging by [@khvn26](https://github.com/khvn26) in https://github.com/Flagsmith/edge-proxy/pull/115
* feat: Use `rye`, overhaul settings by [@khvn26](https://github.com/khvn26) in https://github.com/Flagsmith/edge-proxy/pull/98
* fix: Fix Docker build using incorrect command by [@khvn26](https://github.com/khvn26) in https://github.com/Flagsmith/edge-proxy/pull/105
* fix: Revert API poll settings names by [@khvn26](https://github.com/khvn26) in https://github.com/Flagsmith/edge-proxy/pull/111
* chore: Fix entrypoint in README by [@khvn26](https://github.com/khvn26) in https://github.com/Flagsmith/edge-proxy/pull/106
* chore: Add test for config backwards compatibility by [@matthewelwell](https://github.com/matthewelwell) in https://github.com/Flagsmith/edge-proxy/pull/109
* [pre-commit.ci] pre-commit autoupdate by [@pre-commit-ci](https://github.com/pre-commit-ci) in https://github.com/Flagsmith/edge-proxy/pull/104
* [pre-commit.ci] pre-commit autoupdate by [@pre-commit-ci](https://github.com/pre-commit-ci) in https://github.com/Flagsmith/edge-proxy/pull/107
* [pre-commit.ci] pre-commit autoupdate by [@pre-commit-ci](https://github.com/pre-commit-ci) in https://github.com/Flagsmith/edge-proxy/pull/112


**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.12.0...v2.13.0

[Changes][v2.13.0]


<a name="v2.12.0"></a>
## [Version 2.12.0 (v2.12.0)](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.12.0) - 16 Apr 2024

## What's Changed
* chore(deps): bump idna from 3.4 to 3.7 by [@dependabot](https://github.com/dependabot) in https://github.com/Flagsmith/edge-proxy/pull/99
* [pre-commit.ci] pre-commit autoupdate by [@pre-commit-ci](https://github.com/pre-commit-ci) in https://github.com/Flagsmith/edge-proxy/pull/102
* feat: allow config file to be defined via environment variable by [@abannachGrafana](https://github.com/abannachGrafana) in https://github.com/Flagsmith/edge-proxy/pull/103
* chore(deps): upgrade fastapi and starlette by [@matthewelwell](https://github.com/matthewelwell) in https://github.com/Flagsmith/edge-proxy/pull/101

## New Contributors
* [@pre-commit-ci](https://github.com/pre-commit-ci) made their first contribution in https://github.com/Flagsmith/edge-proxy/pull/102
* [@abannachGrafana](https://github.com/abannachGrafana) made their first contribution in https://github.com/Flagsmith/edge-proxy/pull/103

**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.11.0...v2.12.0

[Changes][v2.12.0]


<a name="v2.11.0"></a>
## [Version 2.11.0 (v2.11.0)](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.11.0) - 08 Apr 2024

## What's Changed
* refac!: Remove sse by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/83
* feat: JSON logging by [@khvn26](https://github.com/khvn26) in https://github.com/Flagsmith/edge-proxy/pull/97
* feat: Switch to Ruff by [@khvn26](https://github.com/khvn26) in https://github.com/Flagsmith/edge-proxy/pull/96
* fix: `Too much data for declared Content-Length` error when endpoint caches enabled by [@matthewelwell](https://github.com/matthewelwell) in https://github.com/Flagsmith/edge-proxy/pull/92
* fix: correct comment about polling by [@dabeeeenster](https://github.com/dabeeeenster) in https://github.com/Flagsmith/edge-proxy/pull/93
* chore(deps): bump orjson from 3.9.7 to 3.9.15 by [@dependabot](https://github.com/dependabot) in https://github.com/Flagsmith/edge-proxy/pull/88
* chore(deps): bump fastapi from 0.103.2 to 0.109.1 by [@dependabot](https://github.com/dependabot) in https://github.com/Flagsmith/edge-proxy/pull/87
* chore: bump github actions by [@dabeeeenster](https://github.com/dabeeeenster) in https://github.com/Flagsmith/edge-proxy/pull/89
* docs: update readme by [@dabeeeenster](https://github.com/dabeeeenster) in https://github.com/Flagsmith/edge-proxy/pull/82
* ci: remove old cache action by [@dabeeeenster](https://github.com/dabeeeenster) in https://github.com/Flagsmith/edge-proxy/pull/95


**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.10.1...v2.11.0

[Changes][v2.11.0]


<a name="v2.10.1"></a>
## [Version 2.10.1 (v2.10.1)](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.10.1) - 29 Feb 2024

## What's Changed
* chore(deps): bump orjson from 3.9.7 to 3.9.15 by [@dependabot](https://github.com/dependabot) in https://github.com/Flagsmith/edge-proxy/pull/88
* chore(deps): bump fastapi from 0.103.2 to 0.109.1 by [@dependabot](https://github.com/dependabot) in https://github.com/Flagsmith/edge-proxy/pull/87
* fix: `Too much data for declared Content-Length` error when endpoint caches enabled by [@matthewelwell](https://github.com/matthewelwell) in https://github.com/Flagsmith/edge-proxy/pull/92

**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.10.0...v2.10.1

[Changes][v2.10.1]


<a name="v2.10.0"></a>
## [Version 2.10.0 (v2.10.0)](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.10.0) - 26 Jan 2024

## What's Changed
* perf: add lru cache by [@matthewelwell](https://github.com/matthewelwell) in https://github.com/Flagsmith/edge-proxy/pull/84
* ci: bump python version in workflow by [@matthewelwell](https://github.com/matthewelwell) in https://github.com/Flagsmith/edge-proxy/pull/86


**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.9.0...v2.10.0

[Changes][v2.10.0]


<a name="v2.9.0"></a>
## [Version 2.9.0 (v2.9.0)](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.9.0) - 26 Jan 2024

## What's Changed
* chore: upgrade to py312 by [@matthewelwell](https://github.com/matthewelwell) in https://github.com/Flagsmith/edge-proxy/pull/85


**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.8.0...v2.9.0

[Changes][v2.9.0]


<a name="v2.8.0"></a>
## [v2.8.0](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.8.0) - 09 Nov 2023

## What's Changed
* Enable gzip-compressing middleware by [@goncalossilva](https://github.com/goncalossilva) in https://github.com/Flagsmith/edge-proxy/pull/80


**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.7.0...v2.8.0

[Changes][v2.8.0]


<a name="v2.7.0"></a>
## [v2.7.0](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.7.0) - 01 Nov 2023

## What's Changed
* chore(deps): bump urllib3 from 2.0.4 to 2.0.6 by [@dependabot](https://github.com/dependabot) in https://github.com/Flagsmith/edge-proxy/pull/78
* Modernize codebase to be fully async by [@goncalossilva](https://github.com/goncalossilva) in https://github.com/Flagsmith/edge-proxy/pull/77


**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.6.0...v2.7.0

[Changes][v2.7.0]


<a name="v2.6.0"></a>
## [v2.6.0](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.6.0) - 29 Sep 2023

## What's Changed
* Return JSONResponse(dict) instead of dict by [@goncalossilva](https://github.com/goncalossilva) in https://github.com/Flagsmith/edge-proxy/pull/75
* Allow time for environments to sync by [@goncalossilva](https://github.com/goncalossilva) in https://github.com/Flagsmith/edge-proxy/pull/73
* Minor logging improvements by [@goncalossilva](https://github.com/goncalossilva) in https://github.com/Flagsmith/edge-proxy/pull/72
* Add missing asserts by [@goncalossilva](https://github.com/goncalossilva) in https://github.com/Flagsmith/edge-proxy/pull/69
* Improve handling of unknown key errors by [@goncalossilva](https://github.com/goncalossilva) in https://github.com/Flagsmith/edge-proxy/pull/74
* Adopt orjson by [@goncalossilva](https://github.com/goncalossilva) in https://github.com/Flagsmith/edge-proxy/pull/76


**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.5.0...v2.6.0

[Changes][v2.6.0]


<a name="v2.5.0"></a>
## [v2.5.0](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.5.0) - 18 Sep 2023

## What's Changed
* chore(deps): bump redis from 4.4.1 to 4.4.4 by [@dependabot](https://github.com/dependabot) in https://github.com/Flagsmith/edge-proxy/pull/62
* chore(deps-dev): bump certifi from 2021.10.8 to 2022.12.7 by [@dependabot](https://github.com/dependabot) in https://github.com/Flagsmith/edge-proxy/pull/64
* chore(deps-dev): bump certifi from 2022.12.7 to 2023.7.22 by [@dependabot](https://github.com/dependabot) in https://github.com/Flagsmith/edge-proxy/pull/66
* chore(deps): bump requests from 2.28.1 to 2.31.0 by [@dependabot](https://github.com/dependabot) in https://github.com/Flagsmith/edge-proxy/pull/63
* feat: bump engine, mapper layer by [@khvn26](https://github.com/khvn26) in https://github.com/Flagsmith/edge-proxy/pull/60
* Update fastapi by [@matthewelwell](https://github.com/matthewelwell) in https://github.com/Flagsmith/edge-proxy/pull/65
* ci: bump pytest by [@dabeeeenster](https://github.com/dabeeeenster) in https://github.com/Flagsmith/edge-proxy/pull/67
* Feature/python 3.11 by [@dabeeeenster](https://github.com/dabeeeenster) in https://github.com/Flagsmith/edge-proxy/pull/71

## New Contributors
* [@dependabot](https://github.com/dependabot) made their first contribution in https://github.com/Flagsmith/edge-proxy/pull/62

**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.4.0...v2.5.0

[Changes][v2.5.0]


<a name="v2.4.0"></a>
## [Version 2.4.0 (v2.4.0)](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.4.0) - 30 Jun 2023

## What's Changed
* improve comment by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/57
* feat: protected features by [@khvn26](https://github.com/khvn26) in https://github.com/Flagsmith/edge-proxy/pull/58
* Upgrade engine version to resolve inconsistent percentage split evaluations by [@matthewelwell](https://github.com/matthewelwell) in https://github.com/Flagsmith/edge-proxy/pull/61

## New Contributors
* [@khvn26](https://github.com/khvn26) made their first contribution in https://github.com/Flagsmith/edge-proxy/pull/58
* [@matthewelwell](https://github.com/matthewelwell) made their first contribution in https://github.com/Flagsmith/edge-proxy/pull/61

**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.3.2...v2.4.0

[Changes][v2.4.0]


<a name="v2.3.2"></a>
## [v2.3.2](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.3.2) - 01 Mar 2023

## What's Changed
* fix prod redis hostname(remove port) by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/56


**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.3.1...v2.3.2

[Changes][v2.3.2]


<a name="v2.3.1"></a>
## [v2.3.1](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.3.1) - 01 Mar 2023

## What's Changed
* fix(sse/prod): Add redis prod cluster by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/54


**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.3.0...v2.3.1

[Changes][v2.3.1]


<a name="v2.3.0"></a>
## [v2.3.0](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.3.0) - 27 Feb 2023

## What's Changed
* feat(stream/environment): Add last_update_at and remove identity events from stream  by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/48
* Drop SQLite(for redis) and identity endpoints by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/50
* sse(stream): fix stream payload and frequency  by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/52


**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.2.3...v2.3.0

[Changes][v2.3.0]


<a name="v2.2.3"></a>
## [v2.2.3](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.2.3) - 19 Oct 2022

## What's Changed
* fix(engine): run in autocommit mode by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/46


**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.2.2...v2.2.3

[Changes][v2.2.3]


<a name="v2.2.2"></a>
## [v2.2.2](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.2.2) - 18 Oct 2022

## What's Changed
* remove --no-access-logs from task definition by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/45


**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.2.1...v2.2.2

[Changes][v2.2.2]


<a name="v2.2.1"></a>
## [v2.2.1](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.2.1) - 18 Oct 2022

## What's Changed
* enable access logs by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/43


**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.2.0...v2.2.1

[Changes][v2.2.1]


<a name="v2.2.0"></a>
## [v2.2.0](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.2.0) - 11 Oct 2022

## What's Changed
* Improvement: Add identity update event and auth by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/27
* improved health check by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/32
* feat(identities-queue-change): Add bulk endpoint by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/36
* infra: Add authentication token as a secret by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/37
* Release v2.2.0 by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/31
* fix(sse/authtoken): update variable name by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/40
* feat(infra/prod): Add sse auth token by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/41


**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.1.2...v2.2.0

[Changes][v2.2.0]


<a name="v2.1.2"></a>
## [v2.1.2](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.1.2) - 21 Sep 2022

## What's Changed
* Fix/warning by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/25
* feature/Arm Docker builds by [@dabeeeenster](https://github.com/dabeeeenster) in https://github.com/Flagsmith/edge-proxy/pull/28
* chore/infra: Add deploy action for production by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/34
* fix: workflow deploy on tag by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/35
* Release v2.1.2 by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/26


**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.1.1...v2.1.2

[Changes][v2.1.2]


<a name="v2.1.1"></a>
## [v2.1.1](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.1.1) - 23 Aug 2022

## What's Changed
* chore: bump flagsmith-flag-engine by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/21
* Release/v2.1.1 by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/22


**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.1.0...v2.1.1

[Changes][v2.1.1]


<a name="v2.1.0"></a>
## [v2.1.0](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.1.0) - 22 Aug 2022

## What's Changed
* Feat/sse by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/17
* Feat/health check by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/19
* Infra add deployment pipeline by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/20
* Release v2.1.0 by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/18


**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v2.0.0...v2.1.0

[Changes][v2.1.0]


<a name="v2.0.0"></a>
## [v2.0.0](https://github.com/Flagsmith/edge-proxy/releases/tag/v2.0.0) - 12 Jul 2022

## What's Changed
* Chore/remove isort use reorder by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/8
* feat(config): use config.json for configuration  by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/7
* Release/v2.0.0 by [@gagantrivedi](https://github.com/gagantrivedi) in https://github.com/Flagsmith/edge-proxy/pull/10


**Full Changelog**: https://github.com/Flagsmith/edge-proxy/compare/v1.0.0...v2.0.0

[Changes][v2.0.0]


<a name="v1.0.0"></a>
## [Version 1.0.0 (v1.0.0)](https://github.com/Flagsmith/edge-proxy/releases/tag/v1.0.0) - 06 Jan 2022

Initial release

[Changes][v1.0.0]


[v2.21.0]: https://github.com/Flagsmith/edge-proxy/compare/v2.20.0...v2.21.0
[v2.20.0]: https://github.com/Flagsmith/edge-proxy/compare/v2.19.0...v2.20.0
[v2.19.0]: https://github.com/Flagsmith/edge-proxy/compare/v2.18.0...v2.19.0
[v2.18.0]: https://github.com/Flagsmith/edge-proxy/compare/v2.17.0...v2.18.0
[v2.17.0]: https://github.com/Flagsmith/edge-proxy/compare/v2.16.0...v2.17.0
[v2.16.0]: https://github.com/Flagsmith/edge-proxy/compare/v2.15.1...v2.16.0
[v2.15.1]: https://github.com/Flagsmith/edge-proxy/compare/v2.15.0...v2.15.1
[v2.15.0]: https://github.com/Flagsmith/edge-proxy/compare/v2.14.0...v2.15.0
[v2.14.0]: https://github.com/Flagsmith/edge-proxy/compare/v2.13.0...v2.14.0
[v2.13.0]: https://github.com/Flagsmith/edge-proxy/compare/v2.12.0...v2.13.0
[v2.12.0]: https://github.com/Flagsmith/edge-proxy/compare/v2.11.0...v2.12.0
[v2.11.0]: https://github.com/Flagsmith/edge-proxy/compare/v2.10.1...v2.11.0
[v2.10.1]: https://github.com/Flagsmith/edge-proxy/compare/v2.10.0...v2.10.1
[v2.10.0]: https://github.com/Flagsmith/edge-proxy/compare/v2.9.0...v2.10.0
[v2.9.0]: https://github.com/Flagsmith/edge-proxy/compare/v2.8.0...v2.9.0
[v2.8.0]: https://github.com/Flagsmith/edge-proxy/compare/v2.7.0...v2.8.0
[v2.7.0]: https://github.com/Flagsmith/edge-proxy/compare/v2.6.0...v2.7.0
[v2.6.0]: https://github.com/Flagsmith/edge-proxy/compare/v2.5.0...v2.6.0
[v2.5.0]: https://github.com/Flagsmith/edge-proxy/compare/v2.4.0...v2.5.0
[v2.4.0]: https://github.com/Flagsmith/edge-proxy/compare/v2.3.2...v2.4.0
[v2.3.2]: https://github.com/Flagsmith/edge-proxy/compare/v2.3.1...v2.3.2
[v2.3.1]: https://github.com/Flagsmith/edge-proxy/compare/v2.3.0...v2.3.1
[v2.3.0]: https://github.com/Flagsmith/edge-proxy/compare/v2.2.3...v2.3.0
[v2.2.3]: https://github.com/Flagsmith/edge-proxy/compare/v2.2.2...v2.2.3
[v2.2.2]: https://github.com/Flagsmith/edge-proxy/compare/v2.2.1...v2.2.2
[v2.2.1]: https://github.com/Flagsmith/edge-proxy/compare/v2.2.0...v2.2.1
[v2.2.0]: https://github.com/Flagsmith/edge-proxy/compare/v2.1.2...v2.2.0
[v2.1.2]: https://github.com/Flagsmith/edge-proxy/compare/v2.1.1...v2.1.2
[v2.1.1]: https://github.com/Flagsmith/edge-proxy/compare/v2.1.0...v2.1.1
[v2.1.0]: https://github.com/Flagsmith/edge-proxy/compare/v2.0.0...v2.1.0
[v2.0.0]: https://github.com/Flagsmith/edge-proxy/compare/v1.0.0...v2.0.0
[v1.0.0]: https://github.com/Flagsmith/edge-proxy/tree/v1.0.0

<!-- Generated by https://github.com/rhysd/changelog-from-release v3.7.2 -->
