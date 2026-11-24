# tuishou-peng

[![CI](https://github.com/ddproxy/tuishou-peng/actions/workflows/ci.yml/badge.svg)](https://github.com/ddproxy/tuishou-peng/actions/workflows/ci.yml)
[![CodeQL](https://github.com/ddproxy/tuishou-peng/actions/workflows/codeql.yml/badge.svg)](https://github.com/ddproxy/tuishou-peng/actions/workflows/codeql.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/ddproxy/tuishou-peng/badge)](https://api.securityscorecards.dev/projects/github.com/ddproxy/tuishou-peng)
[![Latest release](https://img.shields.io/github/v/release/ddproxy/tuishou-peng)](https://github.com/ddproxy/tuishou-peng/releases/latest)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Peng (shared capacity and limits code), part of [Tuishou](https://github.com/ddproxy/tuishou).

Status: The code moves here from the Lu repository (`ddproxy/lu`) when it has its own release cadence. This repository currently holds a minimal Rust library skeleton so the required checks can pass.

## Releases

Stable releases come from `vX.Y.Z` tags. The tag must equal the `version` in `Cargo.toml`; the release workflow does not rewrite a stable checkout.

When CI succeeds on a push to `main`, a dev tag `vX.Y.(Z+1)-dev.<commits since the last stable tag>.g<short hash>` is created and published as a pre-release through the same release workflow. `X.Y.Z` is the version in `Cargo.toml` at that commit, and the tag uses the next patch number. The dev version is written only into the release checkout, so the tagged commit keeps its stable `Cargo.toml`.

Dev builds are skipped when the change since the previous dev tag (or the last stable tag if there is none) is documentation only (`*.md`, `docs/`, `LICENSE`), when `main` has moved past the CI commit, or when the computed tag already exists. The ten newest dev pre-releases are kept; older dev releases and their tags are removed.

Dev and stable releases share the source archive, CycloneDX SBOM, checksum, and build-provenance attestation layout.

## License

Licensed under the [MIT License](LICENSE).
