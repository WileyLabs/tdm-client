# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Changed

- Minimum `requests` version is now 2.34.2.

## [1.2.0] - 2026-07-02

### Added

- **SICI DOI support** — DOIs containing semicolons (including [SICI](https://en.wikipedia.org/wiki/Serial_Item_and_Contribution_Identifier) identifiers) can now be downloaded via the TDM API. This addresses a long-standing community request. See Example 4 (`examples/example4.py`).

## [1.1.0] - 2026-05-20

### Changed

- Minimum supported Python version is now 3.10 (Python 3.9 is no longer supported).
- Minimum `requests` version is now 2.33.1.
- PyPI package metadata updated (Production/Stable, project URLs).
- README expanded with configuration options, known limitations, and troubleshooting (including rate limiting and access denied).

## [1.0.0] - 2025-06-02
### Added
- Initial release
- PDF downloading
- DOI validation
- API handling
- Reporting
- Cross platform support
- Example scripts
