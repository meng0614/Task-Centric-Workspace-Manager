# Contributing

Thanks for helping improve `codex-task-workspace-manager`.

## Development Setup

```bash
python -m pip install -e .
python -m unittest discover -s tests
```

## Principles

- Prefer task ownership over file-type folders.
- Never delete user business files during migration.
- Default to dry-run for operations that move or rename files.
- Mark uncertain ownership as `unclassified` or `experimental`.
- Keep registries short, accurate, and actionable.

## Pull Requests

A good PR includes:

- a clear task-centric use case;
- tests for routing, naming, or registry behavior;
- documentation updates when behavior changes;
- no unrelated workspace churn.
