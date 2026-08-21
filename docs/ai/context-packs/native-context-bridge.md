# Native Context Bridge context pack

Status: current
Feature: native-context-bridge
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Source commit: 5892ff462b3970d3e86555ac79d3cf304571c172
Base branch: main
Base commit: 5892ff462b3970d3e86555ac79d3cf304571c172
Last refreshed: 2026-08-21T15:03:51+08:00

## Purpose

Native Context Bridge 将不同编码 Agent 的仓库入口连接到同一份 Git 原生上下文，而不尝试读取各工具的私有 Memory。运行时负责生成适配器、路由最小上下文、保存按 task session 隔离的私有 draft/checkpoint，并只在完成时发布验证记录；同时禁止 Agent 在未经用户授权时主动联系、引导或中断另一个用户任务。

## Load order

- Read first: `skills/repo-context-ledger/scripts/ledger.py`、`skills/repo-context-ledger/SKILL.md` 与 `docs/specs/native-context-bridge.md`。
- Read if needed: 修改 CLI 行为或兼容迁移时读取 `tests/test_ledger.py` 和 `skills/repo-context-ledger/references/document-model.md`。
- Do not load by default: 不加载无关 Agent 的私有会话、加密 Memory 或仓库外缓存。

## Entry points and code map

| Path / symbol | Role |
| --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py` / `build_init_plan`, `init_repo` | 用同一份内存文件计划预览或生成仓库内运行时、统一配置和 Agent 适配器。 |
| `skills/repo-context-ledger/scripts/ledger.py` / `context_search` | 读取 live Pack 并返回一个主 Pack、关联 spec 和选择原因。 |
| `skills/repo-context-ledger/scripts/ledger.py` / CLI commands | 构建 Manifest、创建 checkpoint，以显式路径记录当前 session evidence，并分别执行 session 完成门禁与全仓集成门禁。 |
| `skills/repo-context-ledger/SKILL.md` | 规定最短路径：只读 context/focus，小修 start→verify→finish，并行才要求 --path。 |

## Contracts and boundaries

- Invariants and contracts: Git 内的 spec、change 与 Context Pack 是跨 Agent 共享事实；工具专用入口仅作薄适配器，且只修改受管区块；`init --dry-run` 与真实 `init` 必须使用同一初始化计划，预览不能获取写锁或写入仓库/私有状态；共享 worktree 不构成跨任务协调授权。并行 session 必须显式记录自己拥有的 evidence paths，不能把共享 worktree 的完整 dirty 集合吸收到当前草稿。
- Failure / recovery: 当前 session 的证据或相关 Pack 不一致时 `finish` 必须失败并保留私有草稿；失败验证只保留有上限的 Failure Capsule，并在命令与输出两侧脱敏常见的等号、冒号、JSON 与空格分隔凭据。其他 session 的 dirty path、stale Pack 或全仓集成检查失败不能触发跨任务消息、暂停或修复。adapter 漂移与全仓 Coverage 由所有任务稳定后的集成检查处理。
- Non-goals: 不解密、导入或同步 Codex、Cursor、Claude、Copilot 等工具的私有 Memory，也不保存完整聊天记录。

## Verification

运行 `python -m unittest discover -s tests -v` 验证运行时、迁移与桥接行为；运行 Skill Creator 的 `quick_validate.py` 验证 Skill 元数据和目录结构。

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Native Context Bridge](../../specs/native-context-bridge.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:c35cc09d2be70369bec0255253dc8ad44091af5a04ca0f33bfd329138a3835d2`
- `skills/repo-context-ledger/SKILL.md` — `sha256:e75be77d0ce3ec5b9e6e2db7f68afef2c3219ecbb4fdd759011f10c40847a66c`
- `skills/repo-context-ledger/agents/openai.yaml` — `sha256:77d4dcdebd3300bd9b7920fe8c4eaea5116129dc56f29d993ad8f463da7171a7`
- `skills/repo-context-ledger/assets/handoff-template.md` — `sha256:cfb76dcea9238ffc40384e8118608d3bd89891ef42de622a8aad69478acdf945`
- `skills/repo-context-ledger/references/document-model.md` — `sha256:9f6858193c4884adc578c887544556b96bcd9da04e6de8ed403aa7696ca2af48`
- `tests/test_ledger.py` — `sha256:7a7aeea0a0880a31ee5d96801a6d12b88ee5606f67527154cac9a4f16eda45b6`
<!-- repo-context-ledger:pack-files:end -->
