# Native Context Bridge context pack

Status: current
Feature: native-context-bridge
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Source commit: ba915523eb59aa27ad01f9299dca19b0c5bdf723
Base branch: main
Base commit: ba915523eb59aa27ad01f9299dca19b0c5bdf723
Last refreshed: 2026-08-21T16:25:21+08:00

## Purpose

Native Context Bridge 将不同编码 Agent 的仓库入口连接到同一份 Git 原生上下文，而不尝试读取各工具的私有 Memory。运行时生成有文件数/字符上限的 Context Plan，只把一个主 Pack、预算内 spec 和近期 Change 元数据交给 Agent；Change 正文保持冷历史。它还保存按 task session 隔离的私有 draft/checkpoint，并禁止 Agent 在未经用户授权时主动联系、引导或中断另一个用户任务。

## Load order

- Read first: `docs/specs/native-context-bridge.md`，再读 `skills/repo-context-ledger/scripts/ledger.py` 中的 `context_search` 与 `manifest_change_summaries`。
- Read if needed: 修改 Agent 读取政策时读取 `skills/repo-context-ledger/SKILL.md` 和 `references/production-workflow.md`；修改 CLI/迁移时读取相关 `tests/test_ledger.py`。
- Do not load by default: 不加载 completed Change 正文、无关 Pack/spec、其他 Agent 的私有会话、加密 Memory 或仓库外缓存。

## Entry points and code map

| Path / symbol | Role |
| --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py` / `build_init_plan`, `init_repo` | 用同一份内存文件计划预览或生成仓库内运行时、统一配置和 Agent 适配器。 |
| `skills/repo-context-ledger/scripts/ledger.py` / `load_live_context_packs`, `context_search`, `manifest_change_summaries` | 排除非 current Pack，选一个主路线，按配置生成有界 Required reads，并只读取 Manifest 的完整近期 Change 元数据。 |
| `skills/repo-context-ledger/scripts/ledger.py` / CLI commands | 输出 text/JSON Context Plan，构建 Manifest、创建 checkpoint，并分别执行 session、PR delta 与全仓门禁。 |
| `skills/repo-context-ledger/SKILL.md`, `references/production-workflow.md` | 规定先读 Required reads、禁止递归加载 Ledger 文档，并区分 PR 增量检查与定时全仓审计。 |

## Contracts and boundaries

- Invariants and contracts: Git 内的 spec、change 与 Context Pack 是跨 Agent 共享事实；初始 Context Plan 只能包含一个 current 主 Pack，并受 Required 文件数、关联 spec 数和字符数硬预算约束；superseded/archived Pack 不可路由，Change 元数据摘要不能成为正文 Required read。四类工具入口使用同一读取边界；`init --dry-run` 与真实 `init` 使用同一计划；共享 worktree 不构成跨任务协调授权。
- Failure / recovery: 当前 session 的证据或相关 Pack 不一致时 `finish` 必须失败并保留私有草稿；失败验证只保留有上限的 Failure Capsule，并在命令与输出两侧脱敏常见的等号、冒号、JSON 与空格分隔凭据。其他 session 的 dirty path、stale Pack 或全仓集成检查失败不能触发跨任务消息、暂停或修复。adapter 漂移与全仓 Coverage 由所有任务稳定后的集成检查处理。
- Non-goals: 不解密、导入或同步 Codex、Cursor、Claude、Copilot 等工具的私有 Memory，也不保存完整聊天记录。

## Verification

运行 `python -m unittest discover -s tests -v` 验证运行时、100 Pack/1,000 Change 规模边界、四类 Adapter、迁移与桥接行为；运行 Skill Creator 的 `quick_validate.py` 验证 Skill 元数据和目录结构。

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Native Context Bridge](../../specs/native-context-bridge.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:23ffe775a57678c4b72794fac84ae79a76dd2e5d4441f6a75d332e05cb7df5eb`
- `skills/repo-context-ledger/SKILL.md` — `sha256:54d50e230f5c4387b39a8ea9f857be68087f74ea169c01359468a0a5ccfdcaf9`
- `skills/repo-context-ledger/agents/openai.yaml` — `sha256:77d4dcdebd3300bd9b7920fe8c4eaea5116129dc56f29d993ad8f463da7171a7`
- `skills/repo-context-ledger/assets/handoff-template.md` — `sha256:cfb76dcea9238ffc40384e8118608d3bd89891ef42de622a8aad69478acdf945`
- `skills/repo-context-ledger/references/document-model.md` — `sha256:c8dbb02a474a1fd218adbc6cc0567a4c9c52321dfedf33cd8630bb8417763568`
- `skills/repo-context-ledger/references/production-workflow.md` — `sha256:b4815921a714ee27109e4c772d41b9f3693c81b30a3e315f462d6310efcc7c2c`
- `tests/test_ledger.py` — `sha256:13d01293b2209fac70dcefd9235cd58f574a741c8e32f1fbf76c5d3c17ff2802`
<!-- repo-context-ledger:pack-files:end -->
