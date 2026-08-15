# Native Context Bridge context pack

Status: current
Feature: native-context-bridge
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Source commit: 650c18896bea6c287caae74a5b431cd68fa15cae
Base branch: main
Base commit: bd61e06cff7a1374cf842d8850604b1ab9567107
Last refreshed: 2026-08-15T15:56:30+08:00

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

- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:702a0569ffe0731b9fbffb07a84b26d96e827f11ab27274d9a759f57d5e5f7d1`
- `skills/repo-context-ledger/SKILL.md` — `sha256:87b83e43decd4db8a3ed5f002a3a31a15bd37f1a7584827983708956ee35b448`
- `skills/repo-context-ledger/agents/openai.yaml` — `sha256:dc78c15dba0364f25f59f2c5ace283f1c64e200f3f88c4b03feedfe99b64c329`
- `skills/repo-context-ledger/assets/handoff-template.md` — `sha256:f0acc36162fd1e36a8dee438fd7160ad03845df4da6739c1811994b366271ec1`
- `skills/repo-context-ledger/references/document-model.md` — `sha256:35752cc0cae464c9b0d5bbda84eaef1770ff12515f0cf66fa0b597cb4c6c011b`
- `tests/test_ledger.py` — `sha256:0bbbbf7d6b5494aa5d7288e503343d9c1740eb9bdce38dd5db484063a6604650`
<!-- repo-context-ledger:pack-files:end -->
