# Implement native context bridge

Status: completed
Feature: native-context-bridge
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Handoff ID: 20260811211310-gviiisen-5a44822643
Actor: gviiisen
Branch: main
Started: 2026-08-11T21:13:10+08:00
Completed: 2026-08-11T21:26:32+08:00
Paused:
Resumed:
Base commit: da095bc00c8acfa6f0fd60c88ba9b8f117ce0e98
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/native-context-bridge.md
Spec exception: none

## Intent

将 v0.4.1 升级为 v0.5.0 Native Context Bridge，使 Codex、Claude、Cursor、GitHub Copilot、Grok 等 Agent 通过各自原生仓库入口读取同一份 Git 上下文。验收结果是初始化仓库会生成可检查的 adapters 与 Context Manifest，活动任务可保存跨 Agent checkpoint，并能用 Git diff 覆盖门禁发现缺少 handoff、spec 或 Context Pack 的行为修改。

## Changed behavior

Before: v0.4.1 只生成 `AGENTS.md`、`CLAUDE.md` 和 Cursor Rule，缺少 Copilot 入口、统一机器索引、不暂停任务的 checkpoint 以及代码变更文档覆盖检查；是否完整记录仍较依赖 Agent 遵循 Prompt。

After: v0.5.0 生成并校验四类原生 adapters，派生 `docs/ai/context-manifest.json`，支持活动 handoff checkpoint，并由 `check --coverage` 将 Git 变更路径与 handoff 证据、稳定 spec/例外和 Context Pack 对照。

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py` | 提供目标仓库内的确定性上下文生命周期与校验运行时。 | 升级 schema v5，增加 Manifest、adapter、checkpoint、coverage 命令和迁移逻辑。 |
| `skills/repo-context-ledger/SKILL.md` | 告诉不同 Agent 何时以及如何自主维护 Ledger。 | 增加跨 Agent 入口、私有 Memory 边界、checkpoint 和覆盖门禁工作流。 |
| `tests/test_ledger.py` | 在隔离临时仓库验证运行时行为和兼容迁移。 | 新增 adapters、Manifest、checkpoint、coverage 测试，并将旧配置迁移断言升级到 schema v5。 |
| `skills/repo-context-ledger/assets/handoff-template.md` | 定义新 handoff 的持久元数据与语义章节。 | 增加 checkpoint 时间和 actor 字段，同时保持旧 handoff 可迁移。 |

## Boundaries and risks

- Invariant: spec 保存当前事实、change 保存时间证据、Context Pack 只保存最小加载路线；Agent 私有 Memory 永远不能覆盖代码、测试或 Git 中已验证文档。
- Failure / recovery: adapter 缺失或漂移、Manifest 过期、Context Pack 指纹变化、行为路径缺少文档覆盖时返回非零状态；可分别通过 adapter/manifest 同步或补齐关联记录恢复。
- Not changed: 不读取、解密、导出或同步任何厂商的私有 Memory，也不保存完整聊天记录；已有成熟 changes 目录、人工 README 和受管标记外的 Agent 指令继续保留。

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `git diff --check`
  - Status: passed
  - Exit code: 0
  - Duration: 0.06s
  - Recorded: 2026-08-11T21:24:05+08:00
  - Output evidence: sha256:8daa48cf93c810586b5ccff4b7f86870a8be210a1ef5c14f3ce9a91a83334b3d (882 characters captured; content not persisted)
- Command: `python C:\Users\Administrator\.codex\skills\.system\skill-creator\scripts\quick_validate.py skills\repo-context-ledger`
  - Status: passed
  - Exit code: 0
  - Duration: 0.08s
  - Recorded: 2026-08-11T21:24:05+08:00
  - Output evidence: sha256:db349825903d66adffea3ecf1bd8e1803043e8a71cf1a051235dabc5371f5bb0 (16 characters captured; content not persisted)
- Command: `python -m unittest discover -s tests -v`
  - Status: passed
  - Exit code: 0
  - Duration: 76.41s
  - Recorded: 2026-08-11T21:24:32+08:00
  - Output evidence: sha256:4f67a5a0f4781eacd2987370b3440749d840ef26ea677d8389501d520cd232e9 (4879 characters captured; content not persisted)
- Command: `python .context-ledger\ledger.py check --strict --coverage`
  - Status: passed
  - Exit code: 0
  - Duration: 0.89s
  - Recorded: 2026-08-11T21:26:24+08:00
  - Output evidence: sha256:74952ea792336837ef8400c980dc0f9978862f98d9f3a3af55dc87a68840e681 (34 characters captured; content not persisted)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`、`README.zh-CN.md`、`skills/repo-context-ledger/SKILL.md`、`skills/repo-context-ledger/references/document-model.md`、`docs/ai/project-context.md`、`docs/specs/native-context-bridge.md`、`docs/ai/context-packs/native-context-bridge.md`

Reason: 记录 v0.5.0 的可观察能力、跨 Agent 数据优先级、用户使用方式、稳定契约和实现导航，并让本仓库从本版本开始自举使用自己的 Ledger。

## Open questions

None.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `da095bc00c8acfa6f0fd60c88ba9b8f117ce0e98`
- Current commit: `da095bc00c8acfa6f0fd60c88ba9b8f117ce0e98`
- Changed paths:
  - `.context-ledger/config.json`
  - `.context-ledger/ledger.py`
  - `.context-ledger/templates/context-pack-template.md`
  - `.context-ledger/templates/handoff-template.md`
  - `.context-ledger/templates/project-context-template.md`
  - `.context-ledger/templates/spec-template.md`
  - `.context-ledger/writing-quality.md`
  - `.cursor/rules/repo-context-ledger.mdc`
  - `.github/copilot-instructions.md`
  - `AGENTS.md`
  - `CLAUDE.md`
  - `README.md`
  - `README.zh-CN.md`
  - `docs/ai/context-manifest.json`
  - `docs/ai/context-packs/native-context-bridge.md`
  - `docs/ai/project-context.md`
  - `docs/changes/2026/08/20260811211310-gviiisen-5a44822643-implement-native-context-bridge.md`
  - `docs/changes/2026/08/README.md`
  - `docs/changes/README.md`
  - `docs/specs/README.md`
  - `docs/specs/native-context-bridge.md`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/agents/openai.yaml`
  - `skills/repo-context-ledger/assets/handoff-template.md`
  - `skills/repo-context-ledger/references/document-model.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `tests/test_ledger.py`
<!-- repo-context-ledger:evidence:end -->
