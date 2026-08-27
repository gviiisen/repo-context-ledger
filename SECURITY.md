# Security policy

Repo Context Ledger is a local, zero-dependency repository tool. It reads Git state, writes managed documentation, stores private task state below Git metadata, and can run an explicitly selected verification command. It does not contact a hosted service or execute a verification preset during initialization, routing, checking, or finishing.

## Supported releases

Security fixes are applied to the latest published release. Reports should include the affected version, operating system, a minimal synthetic repository, the command used, and the observed result. Do not include production source, credentials, private session drafts, or raw sensitive verification output.

## Reporting a vulnerability

Use GitHub's private security-advisory reporting flow when it is enabled for the repository. If private reporting is unavailable, open a minimal public issue asking for a private contact channel without disclosing exploit details. Ordinary correctness bugs can use the public issue tracker.

## Local trust rules

- Treat a cloned repository and its Git-tracked `.context-ledger/config.json` as untrusted until reviewed.
- Verification presets are inert data until `verify --preset` is requested. On first use, or after the preset changes, the runtime prints its exact SHA-256 digest and refuses to execute it. After reviewing the preset, pass that digest with `--trust-digest`; trust is stored per local principal outside Git.
- A sensitive verification hides command arguments and output from evidence. It does not make secrets safe to commit in configuration or scripts.
- `doctor` is read-only. It can identify live, stale, malformed, or unsafe write-lock paths, but never deletes a lock.
- Never remove a live writer's lock. A stale lock should be removed only after confirming that the recorded process no longer exists.

## Out of scope

The runtime does not sandbox project test commands, replace operating-system access control, validate the semantics of arbitrary project scripts, secure a compromised host, or make another user's private Agent memory portable. See [THREAT_MODEL.md](THREAT_MODEL.md) for the detailed boundary.
