# Native Context Bridge context pack

Status: current
Feature: native-context-bridge
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Source commit: da095bc00c8acfa6f0fd60c88ba9b8f117ce0e98
Base branch: main
Base commit: da095bc00c8acfa6f0fd60c88ba9b8f117ce0e98
Last refreshed: 2026-08-12T04:32:28+08:00

## Purpose

Native Context Bridge 将不同编码 Agent 的仓库入口连接到同一份 Git 原生上下文，而不尝试读取各工具的私有 Memory。运行时负责生成适配器、路由最小上下文、保存按 task session 隔离的私有 draft/checkpoint，并只在完成时发布验证记录；同时禁止 Agent 在未经用户授权时主动联系、引导或中断另一个用户任务。

## Load order

- Read first: `skills/repo-context-ledger/scripts/ledger.py`、`skills/repo-context-ledger/SKILL.md` 与 `docs/specs/native-context-bridge.md`。
- Read if needed: 修改 CLI 行为或兼容迁移时读取 `tests/test_ledger.py` 和 `skills/repo-context-ledger/references/document-model.md`。
- Do not load by default: 不加载无关 Agent 的私有会话、加密 Memory 或仓库外缓存。

## Entry points and code map

| Path / symbol | Role |
| --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py` / `init_repo` | 生成仓库内运行时、统一配置和 Agent 适配器。 |
| `skills/repo-context-ledger/scripts/ledger.py` / CLI commands | 构建 Manifest、创建 checkpoint，以显式路径记录当前 session evidence，并分别执行 session 完成门禁与全仓集成门禁。 |
| `skills/repo-context-ledger/SKILL.md` | 规定 Agent 在实现、切换和完成任务时自主调用桥接流程。 |

## Contracts and boundaries

- Invariants and contracts: Git 内的 spec、change 与 Context Pack 是跨 Agent 共享事实；工具专用入口仅作薄适配器，且只修改受管区块；共享 worktree 不构成跨任务协调授权。并行 session 必须显式记录自己拥有的 evidence paths，不能把共享 worktree 的完整 dirty 集合吸收到当前草稿。
- Failure / recovery: 当前 session 的证据或相关 Pack 不一致时 `finish` 必须失败并保留私有草稿；其他 session 的 dirty path、stale Pack 或全仓集成检查失败不能触发跨任务消息、暂停或修复。adapter 漂移与全仓 Coverage 由所有任务稳定后的集成检查处理。
- Non-goals: 不解密、导入或同步 Codex、Cursor、Claude、Copilot 等工具的私有 Memory，也不保存完整聊天记录。

## Verification

运行 `python -m unittest discover -s tests -v` 验证运行时、迁移与桥接行为；运行 Skill Creator 的 `quick_validate.py` 验证 Skill 元数据和目录结构。

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Native Context Bridge](../../specs/native-context-bridge.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:2d4136d86425071f84ab14ba2ab0728cca333a6b268fd9ca49f39c855c1c121c`
- `skills/repo-context-ledger/SKILL.md` — `sha256:4fd67632b217fbc6ad5ccfa6f42802993fbdcd37b54d4bed91385af48907b411`
- `skills/repo-context-ledger/agents/openai.yaml` — `sha256:dc78c15dba0364f25f59f2c5ace283f1c64e200f3f88c4b03feedfe99b64c329`
- `skills/repo-context-ledger/assets/handoff-template.md` — `sha256:cfb76dcea9238ffc40384e8118608d3bd89891ef42de622a8aad69478acdf945`
- `skills/repo-context-ledger/references/document-model.md` — `sha256:5358e84f5033a0f4108384793bc686c7703f0fd8a7eb14ac6f2d40b1d4bca916`
- `tests/test_ledger.py` — `sha256:94f86ee1e59fb06859ba1c7df49aa7acf9a9f8f9caf0cea061a2485bddd5a7e3`
<!-- repo-context-ledger:pack-files:end -->
