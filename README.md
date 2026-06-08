# LLM Wiki — AI 驱动的个人知识库

**语言 / Language / 言語：** 中文（默认）｜ [English](README.en.md) ｜ [日本語](README.ja.md)

---

## 这是什么

LLM Wiki 是一个面向 `skill.io` 兼容智能体的个人知识库脚手架。原始素材保存在 `raw/`，结构化知识保存在 `wiki/`，分析和沉淀保存在 `concepts/`。仓库通过 `skill/` 暴露公开技能，通过 `openwiki.toml` 提供实例级运行时契约。

**核心思路：**
- `openwiki.toml` 是唯一 canonical runtime contract
- `skill/` 是唯一公开 wiki skill 目录
- `config-dir` 与 `wiki-root` 可以完全分离
- `raw/` 只存放原始素材，`wiki/` 由 AI 维护

---

## 运行模型

```text
<config-dir>/
└── openwiki.toml            # 运行时契约，记录绝对 wiki_root

<wiki-root>/
├── raw/               # 原始素材（只读）
├── wiki/
│   ├── index.md       # 全库索引
│   ├── log.md         # 操作日志
│   └── pages/         # 主题页面
└── concepts/          # 分析、回答、报告
```

仓库公开技能位于：

```text
skill/
├── wiki-init/
├── wiki-ingest/
├── wiki-query/
├── wiki-lint/
├── wiki-update/
└── agent-browser/
```

---

## 快速开始

### 前置条件

- 任意兼容 `skill.io` 的智能体/工具
- （可选）[agent-browser](https://github.com/mediar-ai/agent-browser)：用于联网补充与查证
  ```bash
  brew install mediar-ai/agent-browser/agent-browser
  ```

### 安装

```bash
git clone https://github.com/crabin/llm-wiki.git my-wiki
cd my-wiki
```

在你的 `skill.io` 兼容智能体中加载本仓库，并确保能读取 `skill/` 中的公开 wiki 技能。

### 开始使用

1. **初始化**：运行 `wiki-init`
2. **指定配置目录**：例如 `~/.openwiki`
3. **指定 wiki 根目录**：例如 `~/data/my-wiki`，可与 `config-dir` 分离
4. **生成契约**：`wiki-init` 会在 `<config-dir>/openwiki.toml` 中写入绝对 `wiki_root`
5. **开始摄入**：将素材放入 `<wiki-root>/raw/`，再运行 `wiki-ingest`
6. **查询和维护**：使用 `wiki-query`、`wiki-lint`、`wiki-update`

`openwiki.toml` 包含本机绝对路径，不应提交到 Git。仓库根目录已忽略该文件，并提供脱敏的 `openwiki.example.toml` 作为配置示例。

运行时查找规则：
- 优先使用用户显式提供的 `config-dir`
- 否则检查默认配置目录 `~/.openwiki/openwiki.toml`
- 如果默认目录未初始化或无效，从 current working directory 向上搜索 `openwiki.toml`
- 仍找不到时，要求用户提供绝对 `config-dir` 或先运行 `wiki-init`

如果显式提供的 `config-dir` 已经包含有效 `openwiki.toml`，`wiki-init` 会提示"已连接现有 wiki"，复用同一份运行时配置，并建议继续使用同一个 `config-dir` 运行 `wiki-query`、`wiki-ingest`、`wiki-lint`、`wiki-update`。

### E2E 测试

- 快速 deterministic Artifact E2E：
  ```bash
  python3 -m unittest tests.test_wiki_skill_workflow_e2e -v
  ```
- 全量 fast 测试：
  ```bash
  python3 -m unittest discover -s tests -p "test_*.py"
  ```
- 慢速真实 agent smoke E2E：
  ```bash
  SKILL_AGENT_E2E=1 SKILL_AGENT_RUNNER=/path/to/compatible-agent-wrapper python3 -m unittest tests.test_agent_skill_smoke_e2e -v
  ```

说明：
- `tests.test_wiki_skill_workflow_e2e` 只依赖本地夹具和临时目录，不需要网络。
- `tests.test_agent_skill_smoke_e2e` 默认会跳过真实 runner 用例；只有设置 `SKILL_AGENT_E2E=1` 后才执行。
- `SKILL_AGENT_RUNNER` 需要指向一个可执行的兼容 wrapper，可使用绝对路径，也可使用相对于仓库根目录的路径。
- 兼容 wrapper 协议：无额外参数启动，从 `stdin` 读取 prompt，把结果写到 `stdout`；默认在仓库根目录下执行，但 smoke 用例可能覆盖工作目录以验证 `openwiki.toml` 的向上发现逻辑。

---

## 目录结构

```text
llm-wiki/
├── skill/             # 唯一公开 wiki skill 目录
│   ├── wiki-init/
│   ├── wiki-ingest/
│   ├── wiki-query/
│   ├── wiki-lint/
│   ├── wiki-update/
│   └── agent-browser/
├── openwiki.example.toml    # 可提交的脱敏配置示例
├── openwiki.toml            # 本机运行时契约（Git 忽略）
├── raw/
├── wiki/
│   ├── index.md
│   ├── log.md
│   └── pages/
├── concepts/
├── README.md
├── README.en.md
└── README.ja.md
```

---

## Skill 资产边界

- 公开 wiki skill 的边界说明见 `skill/ASSET-LAYOUT.md`
- `skill-private asset` 必须放在拥有它的 `skill/<name>/` 目录树内
- `runtime` wiki 对象仍然是 `openwiki.toml` 与 `wiki_root` 下的 `raw/`、`wiki/`、`concepts/`
- 推荐的 skill-local 目录词汇：
  - `templates/`
  - `examples/`
  - `fixtures/`
  - `assets/`
  - `scripts/`

---

## 技能说明

### wiki-init

- 询问独立的 `config-dir` 与 `wiki-root`
- 在 `config-dir` 中写入 `openwiki.toml`
- 在 `wiki-root` 中初始化 `raw/`、`wiki/index.md`、`wiki/log.md`、`wiki/pages/`、`concepts/`

### wiki-ingest

- 读取新素材并先与用户讨论重点
- 通过 `openwiki.toml` 解析 `wiki_root`
- 更新页面、反向链接、索引与日志

### wiki-query

- 始终先读 `wiki/index.md` 和相关页面
- 本地信息不足时再使用 `agent-browser`
- 回答后总是提议保存到 `concepts/`

### wiki-lint

- 检测断链、孤立页面、矛盾、过期内容
- 输出到 `concepts/lint-<date>.md`
- 修复前先展示 diff

### wiki-update

- 更新现有 wiki 页面
- 每页单独确认
- 检查下游影响并记录日志

### agent-browser

- 联网抓取和查证能力
- 优先选择权威来源
- 为 wiki 工作流提供可引用的 URL 与页面内容

---

## 设计理念

- **中立契约**：运行时只依赖 `openwiki.toml`，不依赖特定智能体命名
- **能力单点暴露**：公开技能只在 `skill/` 维护一份
- **知识复利**：新知识要织入已有网络，而不是孤立存档
- **来源可追溯**：所有关键结论都应绑定文件路径或 URL

---

## License

MIT
