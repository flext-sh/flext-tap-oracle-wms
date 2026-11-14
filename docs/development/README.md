# Development Documentation

<!-- TOC START -->

- [Overview](#overview)
- [Command Surface](#command-surface)
- [Tests](#tests)
- [Topic Guides](#topic-guides)

<!-- TOC END -->

## Overview

This directory collects the development notes of FLEXT Tap Oracle WMS. The binding
engineering law is the workspace
[`AGENTS.md`](https://github.com/flext-sh/flext/blob/0.12.0-dev/AGENTS.md); this page
only routes to it and to the project's own command surface.

## Command Surface

Every build, repair, validation and test action runs through the project's Make
verbs, from the repository root. `make help` prints the current interface.

```bash
make setup
make fix
make fmt
make check
make tests
```

## Tests

Tests live under `tests/unit`, `tests/integration`, `tests/e2e` and
`tests/performance`. They exercise the public tap without mocks. Tests that need a
reachable Oracle WMS environment depend on the `real_config` or `real_tap_instance`
fixtures and are skipped when no local `.env` configures that environment.

## Topic Guides

- [Development workflow](development-workflow.md)
- [Testing strategy](testing-strategy.md)
- [Test architecture](test-architecture.md)
- [Quality gates](quality-gates.md)
- [Code standards](code-standards.md)
- [Security standards](security-standards.md)
- [Singer compliance](singer-compliance.md)
- [Debugging guide](debugging-guide.md)
- [Architecture](../architecture.md)
