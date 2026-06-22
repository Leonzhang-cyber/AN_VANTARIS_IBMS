# Time and Timestamp Standard v1

## Baseline

- UTC ISO-8601 is mandatory for all timestamp fields.
- Timestamps must include timezone indicator (`Z` for UTC).

## Standard fields

- `sourceTimestamp`: time at source emission.
- `observedTimestamp`: time observed by ingestion boundary.
- `createdAt`: object creation time.
- `receivedAt`: transport receive time.
- `processedAt`: completion/processing milestone time.
- `signedAt`: signature generation time.

## Clock skew tolerance

- Recommended tolerance: up to +/- 300 seconds for distributed edge environments.
- Out-of-range timestamps should be flagged for validation/monitoring review.

## Timezone handling

- Persist and transmit timestamps in UTC only.
- UI localization is presentation-layer concern and must not alter authority payload values.
- Do not mix local time and UTC inside authority contract payloads.
