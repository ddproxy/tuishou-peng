# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Automatic dev pre-releases after CI succeeds on `main`, with commit-count tags, shared release workflow, and pruning to the ten newest dev pre-releases.
- `scripts/set-release-version.py` and tests: stable tags must match the `Cargo.toml` version, while dev tags rewrite only the release checkout.
- Workflow policy checks for the dev release path, and script tests in CI.

## [0.1.0] - 2026-11-22

### Added

- Minimal Rust library skeleton with a documented `VERSION` constant and a unit test.
- CI, Audit, CodeQL, Scorecard, dependency review, and source-only Release workflows.
- Dependency policy, security policy, and workflow pin validation script.
- README badges for CI, CodeQL, OpenSSF Scorecard, the latest release, and the MIT licence.

[Unreleased]: https://github.com/ddproxy/tuishou-peng/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ddproxy/tuishou-peng/releases/tag/v0.1.0
