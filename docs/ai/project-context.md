# Project context

Quality profile: evidence-v1
Language: zh-CN
Detail: standard

## Repository purpose

本仓库发布 `repo-context-ledger` Agent Skill 及其纯 Python 运行时，供使用多种 AI 编码工具的个人与团队维护可验证、可交接的 Git 原生项目上下文。用户通过自然语言提出开发需求；Agent 自主管理 Context Pack、稳定 spec、变更 handoff、原生适配器与 README 派生索引。

## Architecture map

- `skills/repo-context-ledger/SKILL.md` 定义 Agent 的自主工作流与安全边界。
- `skills/repo-context-ledger/scripts/ledger.py` 提供无第三方依赖的确定性 CLI，并在初始化时复制到目标仓库的 `.context-ledger/ledger.py`。
- `skills/repo-context-ledger/assets/` 和 `references/` 提供记录模板、文档模型与写作质量规则。
- `tests/test_ledger.py` 使用临时仓库覆盖初始化、迁移、验证、团队协作与跨 Agent 桥接行为。

## Shared boundaries

- 不读取或同步任何 Agent 的私有 Memory；Git 中经过代码与测试验证的文档才是共享事实。
- 初始化与升级必须保留已有文档、人工 README 内容及受管标记之外的 Agent 指令。
- 所有配置路径必须位于目标仓库内；写入采用原子替换，修改命令受仓库锁保护。
- 运行时保持 Python 3.10+ 标准库兼容，并在 Windows 与 Linux 的 GitHub Actions 中测试。

## Navigation

- Stable feature context: [`../specs/README.md`](../specs/README.md)
- Change history: [`../changes/README.md`](../changes/README.md)
