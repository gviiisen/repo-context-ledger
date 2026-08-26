# Coverage Integrity context pack

Status: current
Feature: coverage-integrity
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Source commit: b7e4eb53249faa64881e37401a764093faf476b7
Base branch: main
Base commit: b7e4eb53249faa64881e37401a764093faf476b7
Last refreshed: 2026-08-27T06:50:48+08:00

## Purpose

本功能负责把 Git 变更映射到可审查的 completed change 或当前 worktree 的私有 handoff draft、稳定规格与实际相关的 Context Pack。单个 task session 的 `finish` 使用显式 evidence；PR 的 `--changed-since` 只严格检查 merge-base delta；省略该参数时保留全仓审计。它区分生产代码与测试、CI、配置、文档和生成文件，并防止无关 Context Pack 绕过门禁。

## Load order

- Read first: `skills/repo-context-ledger/scripts/ledger.py` 中的 `check_changed_repo`、`coverage_validation_errors` 与 `task_session_finish_errors`。
- Read if needed: `tests/test_ledger.py` 中的 Coverage 场景，以及 `.context-ledger/config.json` 的迁移兼容行为。
- Do not load by default: Native Context Bridge adapter、README 派生摘要和团队分支冲突检测实现。

## Entry points and code map

| Path / symbol | Role |
| --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::file_digest` | 生成跨 LF/CRLF 稳定、同时尊重 Git binary 属性的 tracked-file 指纹。 |
| `skills/repo-context-ledger/scripts/ledger.py::validate_config` | 校验并补齐 Coverage 分类配置。 |
| `skills/repo-context-ledger/scripts/ledger.py::is_implementation_path` | 判定路径是否属于需要语义记录的生产实现。 |
| `skills/repo-context-ledger/scripts/ledger.py::relevant_private_handoff_texts`, `coverage_validation_errors` | 只采信 evidence 与本次生产实现相交的私有 session，再将变更与 handoff、spec 和 current Pack 对齐。 |
| `skills/repo-context-ledger/scripts/ledger.py::related_context_documents`, `check_changed_repo` | 校验 merge-base delta 及其直接关联 current Pack/spec、链接和 adapter。 |
| `skills/repo-context-ledger/scripts/ledger.py::task_session_finish_errors` | 只核验当前 session 的 evidence、明确 spec 与相关 Pack 指纹。 |
| `tests/test_ledger.py` | 覆盖默认分类、配置覆盖、Pack 关联和绕过防护。 |

## Contracts and boundaries

- Invariants and contracts: 私有 active draft 不进入正式历史或 Manifest；只有 evidence 与当前生产路径相交的 session 才能为 Coverage 提供记录或 spec exception；Context Pack 关联只来自 current Pack 的 tracked file；`--changed-since` 不能因关联范围外旧问题失败，也不能放过 delta 新断链或源码变化造成的关联 Pack stale；无参数的全仓检查语义不变。UTF-8 文本 LF/CRLF 共享指纹，Git `-text` 与真实二进制保持字节敏感。
- Failure / recovery: 当前 session 引用未变更路径、遗漏相关 Pack 或相关 Pack 过期时，`finish` 保留草稿。PR 增量检查只修复当前 delta；旧债务留给所有者或定时全仓审计，不得据此干预另一个任务。base ref 不存在或本次新问题会明确失败。
- Non-goals: 本功能不进行 LLM 语义判断，不引入 Light Mode，也不重构单文件运行时分发模型。

## Verification

`python -m unittest discover -s tests -p "test_ledger.py" -v` 验证分类、可移植指纹、Pack 关联、session 隔离和 changed-scope 边界；PR 运行 `check --strict --coverage --changed-since origin/main`，定时全仓审计运行 `check --strict --coverage`。

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Coverage Integrity](../../specs/coverage-integrity.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `src/repo_context_ledger/constants.pyfrag` — `sha256:5d4b0887372663c0fe37d6a20a2c35c88f49e633725e7ea862f24432164dbe93`
- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:0833437a2238a3fc15cc39d3723d0ddb3642968842d3f905f39699dc6921053a`
- `.context-ledger/config.json` — `sha256:6b7d2b67d36868c59444f9c677a04c9aa0ed993d6d7d421c7666bf3baf61ebaa`
- `tests/test_ledger.py` — `sha256:bc43609d285a1e06069eddfef53660379678122eed0f10c59e6ec6011446f65d`
<!-- repo-context-ledger:pack-files:end -->
