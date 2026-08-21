# Make fingerprints portable and redact local paths

Status: completed
Feature: coverage-integrity
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Handoff ID: 20260821144634-gviiisen-60f90c607e
Session ID: 20260821144634-gviiisen-60f90c607e
Actor: gviiisen
Branch: agent/v0.5.8-portable-fingerprints-path-redaction
Started: 2026-08-21T14:46:34+08:00
Completed: 2026-08-21T15:06:31+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 5892ff462b3970d3e86555ac79d3cf304571c172
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/coverage-integrity.md, docs/specs/task-session-integrity.md
Spec exception: none

## Intent

发布 v0.5.8 的跨平台指纹与本机路径隐私修复。验收结果是：同一 UTF-8 文本在 LF/CRLF checkout 下通过 `check --strict`，真实文本或二进制变化仍报告 stale；任何新旧 verification checks 在进入 completed change 前都不含仓库、Codex、临时目录或用户目录的真实绝对路径。

## Changed behavior

Before: Context Pack 对 working-tree 原始字节直接执行 SHA-256，Windows CRLF checkout 会把未改动的逻辑文本误判为 stale。成功验证末行与旧草稿中的 JSON 双反斜杠路径可以把本机目录写进正式 change。

After: 指纹先遵守 Git `text/eol` 属性，再对未声明的 UTF-8 非 NUL 文本把 CRLF 规范为 LF；`-text`、NUL 与非 UTF-8 文件保持逐字节哈希。`verify` 和 `finish` 以稳定占位符净化普通、slash 与 JSON-escaped 路径，当前可见的 5 处旧绝对路径也已纠正。

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::file_digest` | 生成 Context Pack tracked-file 指纹。 | 增加 Git 属性判定与可移植文本换行规范化，同时保持 binary 字节敏感。 |
| `skills/repo-context-ledger/scripts/ledger.py::redact_local_paths` | 清理将持久化的 verification 文本。 | 按最长根优先替换 `<REPO_ROOT>`、`<CODEX_HOME>`、`<TEMP_DIR>` 和 `<USER_HOME>`，覆盖 JSON 双反斜杠形式。 |
| `skills/repo-context-ledger/scripts/ledger.py::redact_record_local_paths` | 守住 completed change 的原子发布边界。 | 在 `finish` 和中断恢复时重新净化整个 managed checks 区块。 |
| `.context-ledger/ledger.py` | 仓库自举运行时镜像。 | 与 Skill canonical runtime 同步为 v0.5.8 且保持 byte-identical。 |
| `tests/test_ledger.py` | 公开 CLI 行为回归测试。 | 覆盖 LF/CRLF、真实文本变化、NUL/`-text` binary、成功/失败 evidence 与旧草稿 finish 净化。 |

## Boundaries and risks

- Invariant: 既有 LF `sha256:` 指纹保持兼容；真实文本变化和 binary 字节变化必须继续让 Pack stale；原始日志仍不进入 Git。
- Failure / recovery: 非法或 stale 的 session 继续保留私有草稿；升级前已存在的 checks 在 `finish` 或幂等恢复时重新脱敏，验证失败不会发布半成品记录。
- Not changed: 不改变三层文档模型、session 并发隔离、Coverage 关联规则、Git 历史对象或既有 Release/tag；当前 head 的隐私纠正不会声称清除旧提交历史。

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -m unittest tests.test_ledger.LedgerFlowTests.<redacted-token> -v`
  - Status: failed
  - Exit code: 1
  - Duration: 0.09s
  - Recorded: 2026-08-21T14:48:04+08:00
  - Output evidence: sha256:d2a446c95bbe93aa8aba93d7f59dbd2b71eeae74412bdf608101d284063b4677 (729 characters captured; content not persisted; failure=test_ledger (unittest.loader._FailedTest.test_ledger) ... ERROR | ERROR: test_ledger (unittest.loader._FailedTest.test_ledger) | ImportError: Failed to import test module: test_ledger | Traceback (most recent call last): | ModuleNotFoundError: No module named 'tests.test_ledger' | FAILED (errors=1))
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: failed
  - Exit code: 1
  - Duration: 1.36s
  - Recorded: 2026-08-21T14:48:15+08:00
  - Output evidence: sha256:184cac1b3926ae6e95c556ae806f315f3362cacebe65dfda630c89580c6da406 (1068 characters captured; content not persisted; failure=<redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) ... FAIL | FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.fail( | AssertionError: command returned 2, expected 0 | ERROR: docs/ai/context-packs/authentication.md: Context pack is stale; tracked file changed: src/auth.py | FAILED (failures=1))
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: passed
  - Exit code: 0
  - Duration: 1.45s
  - Recorded: 2026-08-21T14:49:30+08:00
  - Output evidence: sha256:18dcafec7eeadd5b6ec9899b014eeb4aadaa65ff5b9466e2fa2114a00a4b7422 (264 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: failed
  - Exit code: 1
  - Duration: 4.36s
  - Recorded: 2026-08-21T14:50:31+08:00
  - Output evidence: sha256:30077680e140aaf7868415976db000ac7a9b0ee5244f01e54a6e1c947fca5cb6 (1119 characters captured; content not persisted; failure=<redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) ... FAIL | FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.fail( | AssertionError: command returned 2, expected 0 | Finish preflight failed; the private draft remains active. | FAILED (failures=1))
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: failed
  - Exit code: 1
  - Duration: 4.55s
  - Recorded: 2026-08-21T14:51:04+08:00
  - Output evidence: sha256:7c415f4ba6b5b241c5ec49fd9c9fa2425adca68388bf3af0cc26be716a654a44 (3890 characters captured; content not persisted; failure=<redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) ... FAIL | FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.assertNotIn(str(home).replace("\\", "\\\\"), text) | AssertionError: 'C:\\\\Users\\\\Administrator' unexpectedly found in '# Redact verification paths\n\nStatus: completed\nFeature: service\nQuality profile: evidence-v1\nLanguage: en\nDetail: standard\nHandoff ID: 20260821145101-alice-1767974aef\nSession ID: 20260821145101-alice-1767974aef\nActor: Alice\nBranch: main\nStarted: 2026-08-21T14:51:01+08:00\nCompleted: 2026-08-21T14:51:04+08:00\nPaused:\nResumed:\nCheckpointed:\nCheckpoint actor:\nBase commit: <redacted-token>\nDirty paths: none\nResume summary:\nNext step:\nSpecs: docs/specs/service.md\nSpec…)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: failed
  - Exit code: 1
  - Duration: 4.83s
  - Recorded: 2026-08-21T14:52:11+08:00
  - Output evidence: sha256:0f9ca9869f775a0c57201f1bf3f66f158862a41a9e439d2f7c193edeb1de32ed (3822 characters captured; content not persisted; failure=<redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) ... FAIL | FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.assertIn("<REPO_ROOT>", text) | AssertionError: '<REPO_ROOT>' not found in '# Redact verification paths\n\nStatus: completed\nFeature: service\nQuality profile: evidence-v1\nLanguage: en\nDetail: standard\nHandoff ID: 20260821145207-alice-dafa1051f9\nSession ID: 20260821145207-alice-dafa1051f9\nActor: Alice\nBranch: main\nStarted: 2026-08-21T14:52:07+08:00\nCompleted: 2026-08-21T14:52:10+08:00\nPaused:\nResumed:\nCheckpointed:\nCheckpoint actor:\nBase commit: <redacted-token>\nDirty paths: none\nResume summary:\nNext step:\nSpecs: docs/specs/service.md\nSpec exception: none\n\n## Intent\n\nDeliver the re…)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: failed
  - Exit code: 1
  - Duration: 4.62s
  - Recorded: 2026-08-21T14:52:46+08:00
  - Output evidence: sha256:75fd1f4ac61ed0162cd62e0758be739861cf1c4c79ad997cc4fae4109a691fcb (3741 characters captured; content not persisted; failure=<redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) ... FAIL | FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.assertIn("<REPO_ROOT>", text) | AssertionError: '<REPO_ROOT>' not found in '# Redact verification paths\n\nStatus: completed\nFeature: service\nQuality profile: evidence-v1\nLanguage: en\nDetail: standard\nHandoff ID: 20260821145243-alice-4a9628e68e\nSession ID: 20260821145243-alice-4a9628e68e\nActor: Alice\nBranch: main\nStarted: 2026-08-21T14:52:43+08:00\nCompleted: 2026-08-21T14:52:46+08:00\nPaused:\nResumed:\nCheckpointed:\nCheckpoint actor:\nBase commit: <redacted-token>\nDirty paths: none\nResume summary:\nNext step:\nSpecs: docs/specs/service.md\nSpec exception: none\n\n## Intent\n\nDeliver the re…)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: passed
  - Exit code: 0
  - Duration: 4.58s
  - Recorded: 2026-08-21T14:53:48+08:00
  - Output evidence: sha256:776548d9719d405bb5b797dd24e89a05c79189e40a4313241e9e9e3ccc37081d (266 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: passed
  - Exit code: 0
  - Duration: 1.22s
  - Recorded: 2026-08-21T14:53:55+08:00
  - Output evidence: sha256:b4d56d87fc0514e91800fd88618321e4dfaf86a6a0d619e524b3baa01801abc7 (254 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: failed
  - Exit code: 1
  - Duration: 2.08s
  - Recorded: 2026-08-21T14:54:43+08:00
  - Output evidence: sha256:4c288f1bd03ab4e2f321ce607b26fc1ce972cdd533871cbc078aee7a1943ffc4 (1064 characters captured; content not persisted; failure=<redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) ... FAIL | FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.fail( | AssertionError: command returned 0, expected 2 | FAILED (failures=1))
- Command: `python -m unittest discover -s tests -p test_ledger.py -k fingerprints -v`
  - Status: passed
  - Exit code: 0
  - Duration: 4.75s
  - Recorded: 2026-08-21T14:55:20+08:00
  - Output evidence: sha256:79ec709db9fee93a546fdc6724bba289e4058b9d5a4041c95e829952f36b1efe (581 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k verification -v`
  - Status: passed
  - Exit code: 0
  - Duration: 18.97s
  - Recorded: 2026-08-21T14:56:50+08:00
  - Output evidence: sha256:f88cb70752b4d5a56ba00f283b3fff7eab93bcce0c9dae7744a8a6b6eff2575e (1101 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -v`
  - Status: passed
  - Exit code: 0
  - Duration: 108.77s
  - Recorded: 2026-08-21T15:00:37+08:00
  - Output evidence: sha256:e81a0250dd9ee98a95e649831f9621da0020905854e56d531ad3bbc51780404a (8693 characters captured; content not persisted; last=OK)
- Command: `python <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py skills\repo-context-ledger`
  - Status: failed
  - Exit code: 1
  - Duration: 0.14s
  - Recorded: 2026-08-21T15:00:58+08:00
  - Output evidence: sha256:eda70640c6b815c404cd1ee7b4b0b4ee3fbd413d311bc39ed613a72875d50f4d (694 characters captured; content not persisted; failure=Traceback (most recent call last): | UnicodeDecodeError: 'gbk' codec can't decode byte 0x92 in position 2037: illegal multibyte sequence)
- Command: `python -m py_compile skills\repo-context-ledger\scripts\ledger.py .context-ledger\ledger.py`
  - Status: passed
  - Exit code: 0
  - Duration: 0.16s
  - Recorded: 2026-08-21T15:00:59+08:00
  - Output evidence: No output.
- Command: `python -X utf8 <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py skills\repo-context-ledger`
  - Status: passed
  - Exit code: 0
  - Duration: 0.06s
  - Recorded: 2026-08-21T15:01:06+08:00
  - Output evidence: sha256:db349825903d66adffea3ecf1bd8e1803043e8a71cf1a051235dabc5371f5bb0 (16 characters captured; content not persisted; last=Skill is valid!)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: failed
  - Exit code: 1
  - Duration: 5.33s
  - Recorded: 2026-08-21T15:02:37+08:00
  - Output evidence: sha256:a93724d2d1d9644b11e873dce0158966725337b499c5a9fe310a3584f85b7e71 (3822 characters captured; content not persisted; failure=<redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) ... FAIL | FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.assertNotIn(str(home).replace("\\", "\\\\"), text) | AssertionError: 'C:\\\\Users\\\\Administrator' unexpectedly found in '# Redact verification paths\n\nStatus: completed\nFeature: service\nQuality profile: evidence-v1\nLanguage: en\nDetail: standard\nHandoff ID: 20260821150233-alice-79af66d0d6\nSession ID: 20260821150233-alice-79af66d0d6\nActor: Alice\nBranch: main\nStarted: 2026-08-21T15:02:33+08:00\nCompleted: 2026-08-21T15:02:37+08:00\nPaused:\nResumed:\nCheckpointed:\nCheckpoint actor:\nBase commit: <redacted-token>\nDirty paths: none\nResume summary:\nNext step:\nSpecs: docs/specs/service.md\nSpec…)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: passed
  - Exit code: 0
  - Duration: 5.16s
  - Recorded: 2026-08-21T15:03:14+08:00
  - Output evidence: sha256:59fc5312599fc7c7010ceca8a64a9467300ab7b26adebaaef4c8f06ccdb5b451 (266 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -v`
  - Status: passed
  - Exit code: 0
  - Duration: 103.09s
  - Recorded: 2026-08-21T15:06:15+08:00
  - Output evidence: sha256:24b46e04cf4fc732468f9d0a1cff2894011e27baaa434add7a44ad11992b80c4 (8693 characters captured; content not persisted; last=OK)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`, `README.zh-CN.md`, `skills/repo-context-ledger/SKILL.md`, `docs/specs/coverage-integrity.md`, `docs/specs/task-session-integrity.md`, `docs/ai/context-packs/coverage-integrity.md`, `docs/ai/context-packs/task-session-integrity.md`, `docs/ai/context-packs/native-context-bridge.md`, and five corrected records under `docs/changes/2026/08/`.

Reason: 双语发布说明、稳定行为契约、最小加载路线和当前公开历史都需要反映跨平台指纹与绝对路径脱敏边界。

## Open questions

None. Git 历史中的旧 blob 保持不变；Release 说明会明确这是前向保护与当前 head 纠正，而不是历史重写。

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `5892ff462b3970d3e86555ac79d3cf304571c172`
- Current commit: `5892ff462b3970d3e86555ac79d3cf304571c172`
- Changed paths:
  - `docs/ai/context-packs/coverage-integrity.md`
  - `docs/ai/context-packs/native-context-bridge.md`
  - `docs/ai/context-packs/task-session-integrity.md`
  - `docs/changes/2026/08/20260811211310-gviiisen-5a44822643-implement-native-context-bridge.md`
  - `docs/changes/2026/08/20260812025946-gviiisen-ec71978b50-change.md`
  - `docs/changes/2026/08/20260812034448-gviiisen-6c5673170f-handoff.md`
  - `docs/changes/2026/08/20260812041915-gviiisen-c1688f4523-evidence-finish.md`
  - `docs/changes/2026/08/20260815153145-gviiisen-c108737ed0-implement-init-dry-run-planning.md`
  - `docs/specs/coverage-integrity.md`
  - `docs/specs/task-session-integrity.md`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `tests/test_ledger.py`
<!-- repo-context-ledger:evidence:end -->
