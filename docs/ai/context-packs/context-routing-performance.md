# Context Routing Performance context pack

Status: current
Feature: context-routing-performance
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Source commit: 645a736f8220153a77d8cb041d6317eb85d10b9d
Base branch: main
Base commit: dd283c73130ec672e183fe8018c4b19217efdf52
Last refreshed: 2026-08-27T03:25:20+08:00

## Purpose

本功能把大型仓库的自然语言任务快速路由成一个有预算的 Context Bundle。它使用 Git metadata 中的可丢弃私有缓存、current Pack 反向索引和可选 PR baseline 减少重复解析与指纹计算，同时继续以 Git 文件、当前代码和实际验证作为权威事实。

## Load order

- Read first: `skills/repo-context-ledger/scripts/ledger.py` 中的 `load_live_context_packs`、`context_search`、`route_resume_sessions` 与 `build_resume_capsule`。
- Read if needed: `tests/test_ledger.py` 中的 Context Bundle/cache/baseline 场景，以及 `benchmarks/context_router_benchmark.py` 的纯合成 59-Pack 性能夹具。
- Do not load by default: completed Change 正文、Agent adapter 生成细节、README 派生索引与不相关 Coverage 门禁。

## Entry points and code map

| Path / symbol | Role |
| --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::load_live_context_packs` | 缓存或解析 current Pack 元数据，并以当前 tracked file 校验指纹。 |
| `skills/repo-context-ledger/scripts/ledger.py::build_context_reverse_index` | 将 query token、feature、title 与 tracked path 映射为有限 Pack 候选。 |
| `skills/repo-context-ledger/scripts/ledger.py::context_baseline` | 从显式 ref 计算 merge-base delta，并给相关 Pack 增加可解释优先级。 |
| `skills/repo-context-ledger/scripts/ledger.py::context_search` | 生成 `context-bundle-v1`、Required reads、预算和匿名 cache/performance 指标。 |
| `skills/repo-context-ledger/scripts/ledger.py::build_resume_capsule` | 按主 Pack 过滤旧 evidence 噪声，保留恢复所需最小路线。 |
| `tests/test_ledger.py` | 验证 cold/warm 等价、失效、隐私、baseline 与 fallback 边界。 |

## Contracts and boundaries

- Invariants and contracts: cache cold/warm、缺失或损坏时必须选择同一个正确主 Pack与 Required reads；Pack、tracked file 或 Git text mode 变化必须失效；所有输出路径保持仓库相对；Required reads 只是首轮路线，不限制后续代码核验。
- Failure / recovery: 缓存不可读写时回退到实时解析；无索引命中时确定性扫描；baseline ref 无法解析时返回 guided warning；旧 evidence 中与主 Pack 无关的路径仅计数省略，不能被当作已核验边界。
- Non-goals: 不缓存模型 Memory、源码正文、Change 正文、聊天或原始日志；不读取其他 principal 私有 session；不让缓存替代 Git、代码与验证事实。

## Verification

`python -m unittest discover -s tests -p "test_ledger.py" -v` 验证路由正确性、cache 失效、baseline、Capsule 过滤和隐私；`python benchmarks/context_router_benchmark.py` 在临时合成仓库测量 59-Pack cold/warm 路由，不读取真实项目资料。

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Context Routing Performance](../../specs/context-routing-performance.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:86474076e7bc9a017add5f7bc2876ff5673ea1f070ed3e9db92e798dba9e5335`
- `tests/test_ledger.py` — `sha256:f0e658499374846c84e107a55a30d150d49ffaf60bf788e9be2fb8a952b81bad`
- `benchmarks/context_router_benchmark.py` — `sha256:78762f66163af15cb0ee502e4944c2c20bc4035503d0517c026074042be96935`
- `benchmarks/README.md` — `sha256:de0652843383c2dc91f1ab2ed0fab184c857e500ffd81dcb4d4ba1138bdc89f1`
<!-- repo-context-ledger:pack-files:end -->
