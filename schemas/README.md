# Public JSON protocols

These Draft 2020-12 schemas describe the stable command envelopes and nested Resume Capsule emitted by Repo Context Ledger 1.x. They are compatibility documents for integrations, not runtime dependencies: the shipped `ledger.py` remains Python-standard-library only and does not load these files.

Minor releases may add optional fields. Consumers must ignore unknown fields. Removing a field, changing its meaning incompatibly, or changing a documented exit class requires a new schema name and a major project version. `next_action.argv` is data and must never be treated as a shell string.

The schemas intentionally keep extension objects open while pinning stable required fields, scalar types, arrays, enums, and selected nested structures. Golden fixtures and real CLI tests verify successful, no-match, and error reports against these declarations on Windows and Ubuntu.
