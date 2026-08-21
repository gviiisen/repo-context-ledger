# Architecture

Repo Context Ledger separates editable source from the single-file runtime installed into repositories.

## Source and generated artifacts

| Path | Role |
| --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl` | Canonical runtime body and ordered build markers. |
| `src/repo_context_ledger/constants.pyfrag` | Stable version, schema, exit, and runtime constants. |
| `src/repo_context_ledger/errors.pyfrag` | Stable user-facing error type and machine error-code carrier. |
| `src/repo_context_ledger/models.pyfrag` | Typed machine-result contracts such as `CommandResult`. |
| `src/repo_context_ledger/contracts.pyfrag` | Non-built compatibility tombstone that points older contributors to the three ordered fragments. |
| `scripts/build_runtime.py` | Deterministic standard-library builder and drift checker. |
| `.gitattributes` | Pins canonical inputs and generated outputs to LF across Windows and Unix checkouts. |
| `skills/repo-context-ledger/scripts/ledger.py` | Generated standalone artifact shipped with the Skill. |
| `.context-ledger/ledger.py` | Generated dogfood mirror used by this repository. |

The generated files are byte-identical. `init` copies the currently executing standalone runtime into the target repository, so installed projects keep one zero-dependency file and do not import the source package.

## Build contract

The builder reads UTF-8 source, normalizes line endings to LF, injects each ordered fragment through exactly one explicit marker, emits no timestamp or machine path, and writes outputs atomically. Git attributes pin the build inputs and generated outputs to LF so byte comparison remains portable when Windows enables `core.autocrlf`. `--check` compares bytes and never writes. CI runs the check on Windows and Ubuntu with Python 3.10 and 3.12 before tests; release, scheduled, and manual workflows also run on macOS.

Edit source and rebuild with:

```text
python scripts/build_runtime.py
python scripts/build_runtime.py --check
```

Never repair drift by editing a generated output. Change the template/fragment, rebuild both outputs, and review the generated diff.

## Gradual extraction

v0.7.0 deliberately extracts the low-coupling constants, errors, and result models first as separately ordered fragments. Future versions may add fragments for configuration, Git/state access, routing, health, lifecycle, and rendering after their boundaries have focused tests. Every step must preserve the standalone CLI artifact, public JSON schemas, exit classes, `init --dry-run` equivalence, and repository/private-state migrations.

The legacy body remains in one template for now. This avoids a high-risk flag-day rewrite while eliminating the previous requirement to hand-maintain two 5,000-line copies.
