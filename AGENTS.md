# AGENTS

## Requirements

- Python 3.12+ (the source uses 3.12 f-string syntax).
- AWS credentials and a deployed stack for the integration tests.

## Setup

```sh
python -m venv venv
venv/bin/pip install -r requirements-lock.txt
```

## Lint

```sh
venv/bin/ruff check
```

## Tests

Offline tests (no AWS access required), run in CI on every pull request:

```sh
venv/bin/pytest tests
```

Full/integration suite. Requires `API_ENDPOINT`, `TABLE_NAME` and `QUEUE_NAME`
pointing at a deployed stack (the `pre-push` hook deploys production first):

```sh
venv/bin/pytest --workers auto
```

## CI

`.github/workflows/ci.yml` runs `ruff check` and the offline test suite on every
pull request. The integration suite runs via `workflow_dispatch` against the
`staging` environment.
