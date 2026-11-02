# TNG Temporal Pipeline — Foundation Specification

**Status:** implementation specification; no scientific validation claimed  
**Target simulation:** IllustrisTNG TNG100-1  
**Initial target snapshot:** 99  
**Implementation branch:** `research/tng-temporal-pipeline-foundation`

## 1. Purpose and scope

Build a reproducible ingestion layer for individual subhalo main-progenitor histories. The first milestone retrieves and validates source records only. It does not calculate the Cloud-9 Assembly Index, mutual information, statistical significance, or a cosmological detection.

The implementation must keep three outputs distinct:

1. main-progenitor temporal history;
2. secondary progenitor / merger records;
3. derived scientific measurements.

A main-progenitor branch is not a complete merger tree. Merger analysis must remain a separate operation over the documented merger records or full tree.

## 2. Documented API strategy

Use HTTPS and the official IllustrisTNG API.

For the first implementation:

1. Retrieve the target subhalo resource at `/api/TNG100-1/snapshots/99/subhalos/{subhalo_id}/`.
2. Read the documented `trees.sublink` link where present, and request the documented `sublink/simple.json` representation for branch identifiers.
3. Treat the `Main` branch as snapshot/subhalo identifier pairs and `Mergers` as a separate collection.
4. Retrieve the individual subhalo resource for each main-branch pair to obtain the actual catalogue properties and source links.
5. Retrieve snapshot metadata for the corresponding snapshot numbers. Do not infer cosmic time from snapshot number or use a constant time interval.

The exact response payload must be captured from a successful, credential-safe API response and frozen as a clearly labelled fixture before the production parser is implemented. The parser must not guess alternative nested keys or silently accept undocumented shapes.

The official API also exposes SubLink main-progenitor-branch JSON/HDF5 products. They may be evaluated as a later optimization once their response shape, field coverage, and dependency requirements have been tested against the simple-branch implementation.

## 3. Authentication and transport

- Read the API key from `TNG_API_KEY`; send it using the documented `api-key` request header.
- Never hardcode credentials, print headers, include credentials in exception text, or write them to provenance records.
- Require HTTPS and restrict requested URLs to the expected `www.tng-project.org` API host.
- Set explicit connect/read timeouts.
- Retry only transient failures (429 and selected 5xx responses); respect `Retry-After` when supplied and use bounded exponential backoff.
- Do not retry 400, 401, 403, or 404 as if they were transient.
- Distinguish authentication, permission, missing-resource, rate-limit, server, timeout, transport, and parse failures.
- A successful HTTP status is not proof of a valid tree.

## 4. Canonical record contract

Every subhalo observation must retain:

- simulation name;
- snapshot number;
- subhalo ID;
- source endpoint;
- retrieval timestamp in UTC;
- response content hash (computed from the received body);
- available source fields with original units and names;
- record validation status;
- missing-field list and warnings.

Do not silently convert absent, null, non-finite, or malformed values to zero. Preserve an actual measured zero as zero. Keep original source units; any unit conversion must be a separately named, documented derived field.

Cosmological time must come from validated snapshot metadata or a separately tested cosmology calculation using the simulation's documented cosmological parameters. In the first milestone, leave cosmic time unavailable if the source metadata does not provide a validated value. Scale factor may be derived from a verified redshift using a = 1/(1+z).

## 5. History status model

Use explicit statuses:

- `FETCH_FAILED`: no usable source response was retrieved;
- `PARSE_FAILED`: response body or schema could not be interpreted;
- `INCOMPLETE_HISTORY`: some valid observations exist, but required history elements or fields are missing;
- `VALID_HISTORY`: all declared requirements and chronology checks pass.

A branch ending at the documented sentinel is a valid termination condition, not a failed fetch. It does not imply that merger count is zero.

A history with missing physical fields may remain useful for limited purposes, but it must not be promoted to `VALID_HISTORY` for an analysis requiring those fields.

## 6. Chronology and identity validation

- Confirm every returned snapshot/subhalo pair against the corresponding individual subhalo response.
- Main-branch records must be ordered from the target snapshot toward earlier snapshots.
- Allow skipped snapshots: SubLink can legitimately connect across a missing snapshot.
- Flag duplicate snapshot numbers, duplicate pairs, inconsistent IDs, and non-monotonic ordering.
- Do not require consecutive snapshot numbers.
- Do not invent a missing progenitor, mass, redshift, or merger event.
- Record branch termination explicitly.
- Keep secondary merger progenitors out of the main-branch time series unless a later, separately specified merger-analysis step joins them.

## 7. Validation and test requirements

All CI tests must use mocked HTTP responses and synthetic fixtures. No live API key or network access is required.

Required tests:

1. valid target subhalo and valid main-branch pairs;
2. valid branch with skipped snapshots;
3. documented branch termination;
4. duplicate snapshot and duplicate identifier detection;
5. mismatched subhalo ID or snapshot in a fetched record;
6. non-monotonic branch ordering;
7. missing mass/redshift/time remains missing, never zero-filled;
8. malformed JSON and unexpected schema;
9. content type with optional charset parameters;
10. 401, 403, 404, 429, 500/502/503/504, timeout and connection failure;
11. bounded retry count and `Retry-After` handling;
12. credential never appears in logs, exceptions, fixture files, or exported provenance;
13. response hash is stable for identical response bytes and changes when bytes change;
14. output round-trips through JSON without changing missing-value semantics.

The synthetic fixture must be labelled synthetic and must never be described as an actual TNG retrieval.

## 8. KSG and scientific analysis are separate

Do not place a KSG estimator in the ingestion module.

A later `tng_temporal_ksg.py` module must have its own mathematical specification and independent tests against known distributions. It must define the estimator variant, norm, tie handling, neighbour counts, units (nats/bits), finite-sample behavior, and treatment of degenerate inputs.

Before computing a temporal statistic, pre-register:

- the physical variables and units;
- the sampling rule and subhalo selection function;
- the temporal pairing and integration rule;
- treatment of missing snapshots and branch gaps;
- the null ensemble and preserved dependencies;
- uncertainty and multiple-testing procedures.

Do not compare a TNG temporal statistic to the synthetic ensemble's reported value until both pipelines measure the same observable with compatible definitions, sampling, and units.

## 9. Acceptance gate

The ingestion milestone is complete only when the documented response fixture exists, parser and transport tests pass, provenance is reproducible, and a sample history can be independently traced back to its source records.

Passing software tests establishes software behavior only. It does not establish the physical validity of a scientific interpretation.
