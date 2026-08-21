# Coverage Integrity

Status: current
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Last reviewed: 2026-08-21

## Purpose and behavior

Coverage Integrity 将 Git 变更分成生产实现、测试、CI、配置、生成文件、Ledger 受管文件与显式忽略路径。全仓 `check --coverage` 只对生产实现要求行为记录，并确保每个生产路径都有实际跟踪它且在本次变更中刷新的 Context Pack，避免用无关 Pack 绕过门禁。单个 task session 的 `finish` 只核验其显式 evidence、明确 spec 与相关 Pack 指纹，不因其他 session 的 dirty path 或 stale Pack 失败。

## Entry points and code map

| Path / symbol | Ownership and role |
| --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::normalize_coverage_globs` | 校验并规范化仓库相对 Coverage glob。 |
| `skills/repo-context-ledger/scripts/ledger.py::coverage_path_kind` | 按固定优先级为 Git 路径分类。 |
| `skills/repo-context-ledger/scripts/ledger.py::file_digest` | 对逻辑文本执行可移植换行规范化，同时让 Git binary 属性与真实二进制保持逐字节敏感。 |
| `skills/repo-context-ledger/scripts/ledger.py::tracked_context_packs` | 根据 Context Pack tracked-file 指纹建立生产路径到 Pack 的关联。 |
| `skills/repo-context-ledger/scripts/ledger.py::coverage_validation_errors` | 校验 handoff evidence、稳定 spec 及相关 Context Pack 是否覆盖生产变更。 |
| `skills/repo-context-ledger/scripts/ledger.py::task_session_finish_errors` | 对当前 session 的显式 evidence 执行局部、fail-closed 的完成门禁。 |
| `.context-ledger/config.json::coverage` | 保存项目可覆盖的路径分类规则。 |

## Data flow and contracts

- Input: 全仓集成检查读取 Git merge base 到 HEAD 的已提交路径与当前工作区路径；session 完成门禁读取该 session 已记录的显式 evidence paths；两者共同使用配置中的六类仓库相对 glob。
- Flow: 运行时先排除配置文档目录、根目录翻译版 README、模块 README 与受管 Agent 入口，再依次应用 ignore、generated、test、CI、config 和 implementation 规则；生产路径随后与所有 Context Pack 的精确 tracked file 建立关联。指纹对 UTF-8 文本把 CRLF 规范为 LF；Git `-text`、NUL 内容和非 UTF-8 内容保持原始字节。
- Persistence / dependencies: 默认分类由标准库运行时提供；`init` 将规范化后的配置写入 `.context-ledger/config.json`。关联关系来自 Git 中的 Context Pack 指纹块，不依赖 Agent 私有 Memory。
- Output: 全仓集成检查对未记录的生产路径、没有关联 Pack 的生产路径或未刷新的相关 Pack 产生包含具体路径的确定性错误；session 完成门禁只报告当前 evidence 不真实、明确 spec 未记录、遗漏已有相关 Pack或当前路径指纹过期。测试、CI、配置和生成文件不会单独触发行为 Coverage。

## Boundaries and failure modes

- Invariants: `implementation_globs` 至少包含一个规则；glob 必须为非空仓库相对路径且不能包含 `..`；无关 Context Pack 不能满足生产路径覆盖；LF/CRLF 逻辑等价文本共享既有 `sha256:` 指纹，真实文本变化和二进制字节变化必须 stale。
- Permissions / concurrency: Coverage 只读取 Git diff、配置和语义文档；并行 session 必须显式选择自己的 evidence paths。共享 worktree 的全局 dirty 集合不属于任何单个任务，也不构成联系、暂停或修改另一个任务的授权。
- Failure / recovery: session 完成失败时保留其私有草稿，修正当前 evidence 或相关 Pack 后重试；其他 session 的 stale Pack 留给其所有者或最终集成检查。非法配置会明确失败；路径分类不符合项目约定时，维护者修改 `coverage` glob 后重新运行检查。生产路径缺少 Pack 时，在集成阶段创建或扩充精确 tracked file，再刷新指纹。
- Non-goals: 本功能不判断 Before/After 的完整业务语义，不增加 Light Mode，不使用 LLM 作为强制门禁，也不改变单文件运行时分发方式。

## Verification

运行 `python -m unittest discover -s tests -p "test_ledger.py" -v` 验证默认分类、配置兼容、相关 Pack 检查、LF/CRLF 可移植指纹、Git binary 属性、显式 session evidence、foreign-stale 隔离与当前 session fail-closed；所有任务稳定后运行 `python .context-ledger/ledger.py check --strict --coverage` 验证本仓库整体结构和变更覆盖。

<!-- repo-context-ledger:changes:start -->
## Related changes

- [Make fingerprints portable and redact local paths](../changes/2026/08/20260821144634-gviiisen-60f90c607e-make-fingerprints-portable-and-redact-local-path.md)
- [隔离并发任务的 evidence 与 finish 校验](../changes/2026/08/20260812041915-gviiisen-c1688f4523-evidence-finish.md)
- [修正受管 README 路径分类](../changes/2026/08/20260812003845-gviiisen-5857b9529e-readme.md)
- [修正 Coverage 分类与 Context Pack 关联](../changes/2026/08/20260812002950-gviiisen-495d91c753-coverage-context-pack.md)
<!-- repo-context-ledger:changes:end -->
