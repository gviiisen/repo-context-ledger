# Coverage Integrity context pack

Status: current
Feature: coverage-integrity
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Source commit: 5892ff462b3970d3e86555ac79d3cf304571c172
Base branch: main
Base commit: 5892ff462b3970d3e86555ac79d3cf304571c172
Last refreshed: 2026-08-21T15:03:50+08:00

## Purpose

本功能负责在全仓集成检查中把 Git 变更映射到可审查的 completed change 或当前 worktree 的私有 handoff draft、稳定规格与实际相关的 Context Pack。它应区分生产代码与测试、CI、配置、文档和生成文件，并防止修改无关 Context Pack 绕过覆盖检查。单个 task session 的 `finish` 使用其显式 evidence 集合，不消费共享 worktree 的全部 diff。

## Load order

- Read first: `skills/repo-context-ledger/scripts/ledger.py` 中的 `validate_config`、`is_implementation_path` 与 `coverage_validation_errors`。
- Read if needed: `tests/test_ledger.py` 中的 Coverage 场景，以及 `.context-ledger/config.json` 的迁移兼容行为。
- Do not load by default: Native Context Bridge adapter、README 派生摘要和团队分支冲突检测实现。

## Entry points and code map

| Path / symbol | Role |
| --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::file_digest` | 生成跨 LF/CRLF 稳定、同时尊重 Git binary 属性的 tracked-file 指纹。 |
| `skills/repo-context-ledger/scripts/ledger.py::validate_config` | 校验并补齐 Coverage 分类配置。 |
| `skills/repo-context-ledger/scripts/ledger.py::is_implementation_path` | 判定路径是否属于需要语义记录的生产实现。 |
| `skills/repo-context-ledger/scripts/ledger.py::coverage_validation_errors` | 将本次 Git 变更与 handoff、spec 和关联 Context Pack 对齐。 |
| `skills/repo-context-ledger/scripts/ledger.py::task_session_finish_errors` | 只核验当前 session 的 evidence、明确 spec 与相关 Pack 指纹。 |
| `tests/test_ledger.py` | 覆盖默认分类、配置覆盖、Pack 关联和绕过防护。 |

## Contracts and boundaries

- Invariants and contracts: 私有 active draft 可为当前工作区提供 evidence，但不进入正式历史或 Manifest；文档、账本运行时状态和 Agent adapter 不属于生产实现；Context Pack 关联来自其 tracked file，而不是“任意 Pack 已修改”。UTF-8 文本的 LF/CRLF 形式共享指纹，Git `-text` 与真实二进制保持字节敏感。并行 session 的 evidence 必须是当前任务显式声明的真实变更路径。
- Failure / recovery: 当前 session 引用未变更路径、遗漏已有的相关 Pack 或相关 Pack 指纹过期时，`finish` 必须失败并保留草稿。配置非法、生产路径没有关联 Pack、其他任务的未记录路径或其他 Pack 过期由 `check --strict --coverage` 这个全仓集成门禁报告，不得据此干预另一个任务。
- Non-goals: 本功能不进行 LLM 语义判断，不引入 Light Mode，也不重构单文件运行时分发模型。

## Verification

`python -m unittest discover -s tests -p "test_ledger.py" -v` 验证分类、可移植指纹、Git binary 属性、Pack 关联、显式 session evidence 与 foreign-stale 隔离；所有任务稳定后运行 `python .context-ledger/ledger.py check --strict --coverage` 验证仓库整体记录覆盖。

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Coverage Integrity](../../specs/coverage-integrity.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:c35cc09d2be70369bec0255253dc8ad44091af5a04ca0f33bfd329138a3835d2`
- `tests/test_ledger.py` — `sha256:7a7aeea0a0880a31ee5d96801a6d12b88ee5606f67527154cac9a4f16eda45b6`
<!-- repo-context-ledger:pack-files:end -->
