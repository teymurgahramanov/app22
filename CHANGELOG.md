# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2025-08-08

### Added
- New MongoDB endpoint `/mongodb` to insert a heartbeat and return recent request documents.
  - Configurable via environment variables: `APP22_MONGO_URI`, `APP22_MONGO_DB`, `APP22_MONGO_COLLECTION`, `APP22_MONGO_SERVER_SELECTION_TIMEOUT_MS`, `APP22_MONGO_CLIENT_OPTIONS`.
  - Added `pymongo` dependency.
- Metrics are now under the "App" tag with a custom registry:
  - GET `/metrics` exposes Prometheus metrics.
  - POST `/metrics/counter` increments a labeled counter.
  - POST `/metrics/gauge` sets/increments/decrements a labeled gauge.
  - POST `/metrics/histogram` records observations.
- Filesystem compatibility endpoint `/cat` to list and preview files under `data/` (used by tests and demos).
- Tests for MongoDB and metrics endpoints.

### Changed
- Renamed SQL endpoint from `/database` to `/sql`.
- Moved metrics endpoint from application root to the App router; removed the old global `/metrics` registration from application startup.
- Updated documentation to reflect endpoint changes and new features.

### Fixed
- Stabilized database route tests for environment-agnostic database URI assertions.
- Improved `/mongodb` implementation to tolerate mocked cursors in tests.

### Notes
- Backward-compatibility: `/database` path is replaced by `/sql`.
- See `README.md` for updated usage examples and configuration.

[1.1.0]: https://github.com/your-org/app22/releases/tag/v1.1.0
