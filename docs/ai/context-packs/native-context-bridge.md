# Native Context Bridge context pack

Status: current
Feature: native-context-bridge
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Source commit: 7655bcccc6bb3b07aab23fdd86f16c048178535b
Base branch: main
Base commit: 7655bcccc6bb3b07aab23fdd86f16c048178535b
Last refreshed: 2026-08-21T19:46:07+08:00

## Purpose

Native Context Bridge 将不同编码 Agent 的仓库入口连接到同一份 Git 原生上下文，而不尝试读取各工具的私有 Memory。运行时生成有文件数/字符上限的 `context-bundle-v1`，只把一个主 Pack、预算内 spec、冷 Change 元数据、可选 PR baseline 和可选的私有 Resume Capsule 交给 Agent。Capsule 按需生成，不保存聊天；Required reads 只是首轮路线，不限制行为相关代码边界的继续核验。

## Load order

- Read first: `docs/specs/native-context-bridge.md`，再读 `skills/repo-context-ledger/scripts/ledger.py` 中的 `context_search`、`route_resume_sessions` 与 `build_resume_capsule`。
- Read if needed: 修改 Agent 读取政策时读取 `skills/repo-context-ledger/SKILL.md` 和 `references/production-workflow.md`；修改 CLI/迁移时读取相关 `tests/test_ledger.py`。
- Do not load by default: 不加载 completed Change 正文、无关 Pack/spec、其他 Agent 的私有会话、加密 Memory 或仓库外缓存。

## Entry points and code map

| Path / symbol | Role |
| --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py` / `build_init_plan`, `init_repo` | 用同一份内存文件计划预览或生成仓库内运行时、统一配置和 Agent 适配器。 |
| `skills/repo-context-ledger/scripts/ledger.py` / `load_live_context_packs`, `context_search`, `route_resume_sessions` | 排除非 current Pack，选一个主路线，按配置生成有界 Required reads，并为当前 principal 路由私有 session。 |
| `skills/repo-context-ledger/scripts/ledger.py` / `resume_change`, `share_session` | 在同一 session 上轮换 continuation epoch/tool，并执行显式跨 principal 授权。 |
| `skills/repo-context-ledger/scripts/ledger.py` / CLI commands | 输出 text/JSON Context Bundle，构建 Manifest、创建 checkpoint，并分别执行 session、PR delta 与全仓门禁。 |
| `skills/repo-context-ledger/SKILL.md`, `references/production-workflow.md` | 规定先读 Required reads、按未决问题扩大代码边界、禁止递归加载 Ledger 文档，并区分 PR 增量检查与全仓审计。 |

## Contracts and boundaries

- Invariants and contracts: Git 内 spec/change/Pack 是跨用户共享事实；私有 Resume Capsule 只给当前 principal 或显式 grant；同 principal 可跨工具继续同一 session；另一 principal 默认只看到 overlap；首轮 Context Bundle 只有一个主 Pack 并受预算约束，但 Agent 必须展开所有行为相关代码边界；superseded Pack 和 Change 正文不进入默认路线；共享 worktree 不等于协调授权。
- Failure / recovery: 多个近似 session 不自动选择，旧 epoch、过期 grant 与未授权写入 fail closed；新 clone 只恢复已提交事实。当前 session 的证据或 Pack 不一致时 `finish` 保留私有草稿；失败验证只保留脱敏 Failure Capsule；其他 session 的 dirty/stale/global-check 不能触发跨任务消息或修复。
- Non-goals: 不解密、导入或同步各工具私有 Memory，不保存完整聊天，不把 Capsule 当作完整环境，也不通过 Git 同步未完成 session。

## Verification

运行 `python -m unittest discover -s tests -p test_ledger.py` 验证 Context Bundle、Resume Capsule、principal 隔离、授权、100 Pack/1,000 Change 规模边界、四类 Adapter 与迁移；运行 Skill Creator 的 `quick_validate.py` 验证 Skill 元数据和目录结构。

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Native Context Bridge](../../specs/native-context-bridge.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:356673863b88619a2a2f88599f24565bd8511e376e02785f6826c41f8153ca9e`
- `skills/repo-context-ledger/SKILL.md` — `sha256:a2d0c1da6e4678924cca45c0f86e9b084c19ec96e0f7d41e56a43b288a9976a4`
- `skills/repo-context-ledger/agents/openai.yaml` — `sha256:77d4dcdebd3300bd9b7920fe8c4eaea5116129dc56f29d993ad8f463da7171a7`
- `skills/repo-context-ledger/assets/handoff-template.md` — `sha256:cfb76dcea9238ffc40384e8118608d3bd89891ef42de622a8aad69478acdf945`
- `skills/repo-context-ledger/references/document-model.md` — `sha256:9515f21bfaa761e06645b871ec5785550c185580048092afa7a6d13ffacd55c1`
- `skills/repo-context-ledger/references/production-workflow.md` — `sha256:40e05d1c683cdd5d1e3ea200990eee6a2d452301bccbffe770f62d18970dc104`
- `tests/test_ledger.py` — `sha256:16bd849cddb25787ed02de4a644866794924b4605e7022f3292f4e1631cd9c04`
<!-- repo-context-ledger:pack-files:end -->
