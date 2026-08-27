# Coverage Integrity

Status: current
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Last reviewed: 2026-08-27

## Purpose and behavior

Coverage Integrity 将 Git 变更分成生产实现、测试、CI、配置、生成文件、Ledger 受管文件与显式忽略路径。全仓 `check --coverage` 只对生产实现要求行为记录，并确保每个生产路径都有实际跟踪它且在本次变更中刷新的 Context Pack，避免用无关 Pack 绕过门禁。单个 task session 的 `finish` 只核验其显式 evidence、明确 spec 与相关 Pack 指纹，不因其他 session 的 dirty path 或 stale Pack 失败。

## Entry points and code map

| Path / symbol | Ownership and role |
| --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::normalize_coverage_globs` | 校验并规范化仓库相对 Coverage glob。 |
| `skills/repo-context-ledger/scripts/ledger.py::coverage_path_kind` | 按固定优先级为 Git 路径分类。 |
| `skills/repo-context-ledger/scripts/ledger.py::file_digest` | 对逻辑文本执行可移植换行规范化，同时让 Git binary 属性与真实二进制保持逐字节敏感。 |
| `skills/repo-context-ledger/scripts/ledger.py::tracked_context_packs`, `related_context_documents` | 一次建立生产路径到 current Pack 的反向关联，并展开本次 delta 直接关联的 Pack/spec。 |
| `skills/repo-context-ledger/scripts/ledger.py::coverage_validation_errors` | 校验 handoff evidence、稳定 spec 及相关 Context Pack 是否覆盖生产变更。 |
| `skills/repo-context-ledger/scripts/ledger.py::changed_scope_paths`, `check_changed_repo` | 从 merge base 构建 PR delta，只严格校验本次改变的语义文档、链接、adapter 与 Pack 指纹。 |
| `skills/repo-context-ledger/scripts/ledger.py::task_session_finish_errors` | 对当前 session 的显式 evidence 执行局部、fail-closed 的完成门禁。 |
| `.context-ledger/config.json::coverage` | 保存项目可覆盖的路径分类规则。 |

## Data flow and contracts

- Input: 全仓集成检查或 `--changed-since <base-ref>` 读取 Git merge base 到 HEAD 的已提交路径与当前工作区路径；session 完成门禁读取该 session 已记录的显式 evidence paths；Coverage 只纳入 evidence 与本次生产实现路径相交的 active/paused 私有 session，不能借用无关 session 的 spec exception。
- Flow: `finish` 只校验当前 session。`check --strict --changed-since` 读取 delta 中的语义文档，并通过 current Pack 反向映射展开被修改源码直接关联的 Pack/spec。普通实现路径继续要求 current Pack 精确跟踪；rename 则保留 transition，在 merge base 读取旧路径的 Pack 所有权，在当前工作区读取新路径的 Pack 所有权，并要求两端 feature 一致且相关 Pack 已刷新。无关旧文档债务不进入阻塞错误。指纹对 UTF-8 文本把 CRLF 规范为 LF；Git `-text`、NUL 内容和非 UTF-8 内容保持原始字节。
- Persistence / dependencies: 默认分类由标准库运行时提供；`init` 将规范化后的配置写入 `.context-ledger/config.json`。关联关系来自 Git 中的 Context Pack 指纹块，不依赖 Agent 私有 Memory。
- Output: 增量检查报告 base、实际检查路径数和只属于当前 delta 的确定性错误；全仓检查继续报告全部结构/链接/过期债务；session 门禁只报告当前 evidence 不真实、明确 spec 未记录、遗漏已有相关 Pack 或当前路径指纹过期。测试、CI、配置和生成文件不会单独触发行为 Coverage。

## Boundaries and failure modes

- Invariants: `implementation_globs` 至少包含一个规则；glob 必须为非空仓库相对路径且不能包含 `..`；无关 Context Pack 或无关私有 session 不能满足生产路径覆盖；production rename 的旧路径必须由 base Pack 覆盖，新路径必须由同一 feature 的 current Pack 覆盖，且 source/current Pack 迁移必须进入本次 delta；增量检查不能掩盖当前问题，也不能因范围外旧债务失败；LF/CRLF 逻辑等价文本共享既有 `sha256:` 指纹。
- Permissions / concurrency: Coverage 只读取 Git diff、配置和语义文档；并行 session 必须显式选择自己的 evidence paths。共享 worktree 的全局 dirty 集合不属于任何单个任务，也不构成联系、暂停或修改另一个任务的授权。
- Failure / recovery: session 完成失败时保留其私有草稿，修正当前 evidence 或相关 Pack 后重试；PR 增量检查失败时只修复本次 delta，不得顺手重写无关历史。其他 session 或旧版本的 stale Pack 留给其所有者或定时全仓审计。base ref 不存在、配置非法或本次新断链会明确失败。
- Non-goals: 本功能不判断 Before/After 的完整业务语义，不增加 Light Mode，不使用 LLM 作为强制门禁，也不改变单文件运行时分发方式。

## Verification

运行 `python -m unittest discover -s tests -p "test_ledger.py" -v` 验证默认分类、配置兼容、相关 Pack、LF/CRLF、Git binary 属性、显式 session evidence，以及增量检查“忽略旧债务但拒绝新断链/新 stale Pack”的边界。PR 使用 `check --strict --coverage --changed-since origin/main`；定时或 Release 全仓审计使用 `check --strict --coverage`。

<!-- repo-context-ledger:changes:start -->
## Related changes

- [Address PR 25 review blockers](../changes/2026/08/20260827214039-gviiisen-c84859e7d8-address-pr-25-review-blockers.md)
- [Bound context loading and delta validation](../changes/2026/08/20260821154209-gviiisen-25df54aeac-bound-context-loading-and-delta-validation.md)
- [Make fingerprints portable and redact local paths](../changes/2026/08/20260821144634-gviiisen-60f90c607e-make-fingerprints-portable-and-redact-local-path.md)
- [隔离并发任务的 evidence 与 finish 校验](../changes/2026/08/20260812041915-gviiisen-c1688f4523-evidence-finish.md)
- [修正受管 README 路径分类](../changes/2026/08/20260812003845-gviiisen-5857b9529e-readme.md)
- [修正 Coverage 分类与 Context Pack 关联](../changes/2026/08/20260812002950-gviiisen-495d91c753-coverage-context-pack.md)
<!-- repo-context-ledger:changes:end -->
