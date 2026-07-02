# Release Process

> **Note:** This document is intended for project administrators or maintainers who have the necessary permissions to create releases and manage workflows. Contributors should refer to the [CONTRIBUTING](CONTRIBUTING.md) guidelines.

This document outlines the steps to create and publish releases for the `wiley-tdm` project. Follow these instructions to ensure a smooth release process.

## Steps to Create a Release

This will be automated/improved in the future

1. **Update version references:**
    - [pyproject.toml](pyproject.toml): Project version
    - [CHANGELOG](CHANGELOG.md): Release details
    - [`__init__.py`](src/wiley_tdm/__init__.py): `__version__`
    - [tdm_client.py](src/wiley_tdm/tdm_client.py): API_USER_AGENT

2. **Commit changes locally:**
    ```bash
    git commit -m "Prepare for release 1.2.0: update version references in pyproject.toml, CHANGELOG.md, __init__.py, and tdm_client.py"
    ```

3. **Push the version bump so [CI](https://github.com/WileyLabs/tdm-client/actions/workflows/ci.yml) runs:**

    ```bash
    git push origin main
    ```

4. **Confirm build success**
    - [Check CI](https://github.com/WileyLabs/tdm-client/actions/workflows/ci.yml) for the commit you just pushed (or use **Run workflow** on `workflow_dispatch` if you need a manual run).

5. **Tag repository** (after CI is green):

    ```bash
    git tag -a v1.2.0 -m "Release version 1.2.0"
    git push origin v1.2.0
    ```

6. **Publish to TestPyPI:**
    - Manually run [Publish-Test](https://github.com/WileyLabs/tdm-client/actions/workflows/publish-test.yml) workflow
        - Select tag: v1.2.0
    - Confirm success
    - Check [TestPyPI](https://test.pypi.org/project/wiley-tdm/)

7. **Publish to PyPI:**
    - Create a new GitHub [Release](https://github.com/WileyLabs/tdm-client/releases)
        - Select tag: v1.2.0
        - Select target: main
        - Title: Release v1.2.0
        - Description: See [CHANGELOG](CHANGELOG.md)
        - Publish release
    - Check [Publish](https://github.com/WileyLabs/tdm-client/actions/workflows/publish.yml) workflow (automatically triggered)
    - Confirm success
    - Check [PyPI](https://pypi.org/project/wiley-tdm/)

## Pre-Releases

Pre-releases (e.g., `1.2.0-rc1`) are used for testing purposes and are only published to TestPyPI. Follow steps 1–6 above for pre-releases, but do not proceed to step 7 (publishing to PyPI).
