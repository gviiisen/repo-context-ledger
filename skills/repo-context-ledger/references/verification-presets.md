# Verification presets

Use a verification preset for a stable project check that multiple Agents or sessions will run repeatedly. Keep one-off diagnostics as direct `verify -- <executable> <arguments>` commands.

## Configuration

Presets live in the Git-tracked `.context-ledger/config.json` and are never executed automatically:

```json
{
  "verification": {
    "presets": {
      "python-unit": {
        "argv": ["python", "-B", "-m", "unittest", "discover", "-s", "tests"],
        "cwd": ".",
        "timeout": 600,
        "sensitive": false,
        "platforms": ["windows", "linux", "darwin"]
      },
      "go-announcement-worker": {
        "argv": ["go", "test", "./..."],
        "cwd": "services/announcement-worker",
        "timeout": 900,
        "sensitive": false,
        "platforms": ["windows", "linux", "darwin"]
      },
      "windows-worker-script": {
        "argv": ["powershell.exe", "-NoProfile", "-NonInteractive", "-File", "scripts/verify-worker.ps1"],
        "cwd": ".",
        "timeout": 900,
        "sensitive": false,
        "platforms": ["windows"]
      }
    }
  }
}
```

Run one explicitly. The first attempt stops before execution and prints the preset's normalized digest:

```text
python .context-ledger/ledger.py verify --session <id> --preset python-unit
ERROR: ... repeat with --trust-digest sha256:<digest>
python .context-ledger/ledger.py verify --session <id> --preset python-unit --trust-digest sha256:<digest>
```

An explicit `--timeout` overrides the preset timeout. An explicit `--sensitive` can strengthen a non-sensitive preset; it cannot make a preset configured as sensitive persist its command or output.

## Safety and portability

- `argv` is passed directly to `subprocess.run(..., shell=False)`. Each JSON element is one argument, so spaces do not require shell escaping.
- `cwd` is relative to the repository and cannot escape it. The directory must exist when the preset runs.
- `platforms` contains one or more of `windows`, `linux`, and `darwin`; a mismatched machine fails before execution.
- PowerShell presets must use `-File` with a reviewed script. `-Command`, encoded command strings, `cmd.exe`, and shell `-c` strings are rejected.
- Do not store secrets, tokens, local absolute paths, or environment-specific values in a preset. `sensitive: true` protects verification evidence, not the Git-tracked configuration itself.
- Review a preset after cloning, pulling, changing branches, or receiving configuration changes. Trust requires the exact digest printed by the runtime, is scoped to the current local principal, and is stored outside Git. A changed preset has a new digest and stops again before execution. Initialization, context routing, and `finish` never auto-run it.
- Prefer checked-in Python, PowerShell, Bash, or project-native scripts when a check needs pipes, conditionals, environment setup, or several commands.

## Agent behavior

Before assembling a repeated verification command, check whether a preset exactly represents the required test. Do not substitute a narrower preset for a broader claimed check, invent a preset merely to avoid understanding the project, or run every configured preset by default. Independent presets may run concurrently only when they do not share mutable services, ports, databases, generated directories, or fixtures.
