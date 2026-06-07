# Migration Guide

Migration is conservative by default.

1. Run `workspace-manager audit`.
2. Run `workspace-manager migrate --dry-run`.
3. Review the generated migration plan.
4. Run `workspace-manager migrate --apply` only after explicit approval.

Rules:

- Do not delete business files.
- Do not overwrite targets.
- Use `_v2`, `_v3`, etc. for conflicts.
- Put ambiguous files in `unclassified`.
- Put ambiguous Skills in `experimental`.
