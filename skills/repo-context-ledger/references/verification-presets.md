# Verification presets

Use a verification preset for a stable acceptance goal that multiple Agents or sessions will verify repeatedly. Routine reads, searches, file/configuration generation, and deployment preparation use ordinary tools; they do not each need a Ledger wrapper. A one-off acceptance check can use direct `verify -- <executable> <arguments>`. Record exploratory observations in the draft without inventing managed verification results.

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

## One acceptance goal, one invocation

1. Identify the behavior and safety boundary being accepted. Reuse the current session and existing project checks; do not repeat plan/status/focus merely for the next helper command.
2. Run that acceptance script through verify when it is first needed, not bare first and a second time for logging. Prefer an existing script; only when a small wrapper is justified, adapt `assets/verify-change.py` from this Skill to the project's scripts directory. Its empty CHECKS list deliberately fails until configured with reviewed, named direct argv arrays. It executes serially, stops on failure or timeout, and marks remaining checks not-run.
3. Inspect the aggregate exit code and substep results before continuing. Optional `ledger-step: <short-name> <passed|failed|not-run>` output is retained as a bounded, redacted summary (up to 16 annotations; extra annotations are explicitly counted as omitted). These are script-reported steps, not separate trusted attestations; the managed result still comes from the actual process exit code. Sensitive verification suppresses the step summary with the rest of the output.

For example, a permission-fix acceptance script can check directory access, execution as the service user, and the existing startup guard. File preparation is not a fourth verification goal. Keep required pre-deployment checks before deployment and post-deployment acceptance afterward; never combine across authorization boundaries or replay deployment/trading actions to repair missing logging. An already executed external observation may be documented as an observation, not relabeled as a managed pass. Rerun only a safe check whose result genuinely needs refreshing.

A small fix commonly needs one or two acceptance invocations, but this is not a hard quota. Different safety boundaries or changed inputs can require more. The goal is fewer wrappers and no duplicate execution, not fewer tests or lost failure details.

## Distinguish script time from Ledger time

For a slow invocation, use `--timings verify ...`. The private stderr report keeps `verification_command_ms` for the actual subprocess, adds `verification_prepare_ms` and `verification_record_ms`, and reports total `ledger_overhead_ms` outside the subprocess. `lock_wait_ms` is included within overhead, not additional time to sum again. Python interpreter startup precedes this measurement. Metrics contain no command arguments or repository paths and are not stored in the handoff. Do not infer real deployment speed from a synthetic small-file benchmark.
