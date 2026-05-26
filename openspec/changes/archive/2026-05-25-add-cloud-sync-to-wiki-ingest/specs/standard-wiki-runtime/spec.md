# Delta Spec: standard-wiki-runtime (cloud sync)

## Overview

本 delta spec 为 `standard-wiki-runtime` 规格新增云端同步相关需求。定义 `WIKI.md` 中 sync 字段的契约、`wiki-ingest` 中的自动同步流程，以及 `wiki-init` 模板的同步字段初始化。

## Requirements

### REQ-14: `WIKI.md` 包含 `remote_sync_path` 和 `auto_sync` 字段

**Behavior**: `WIKI.md` frontmatter 必须支持 `remote_sync_path`（pcloud 远端逻辑路径，默认 `"wiki"`，空字符串表示跳过同步）和 `auto_sync`（布尔值，默认 `false`）两个可选字段。wiki workflow 在读取 `WIKI.md` 时应正确解析这些字段。

**Test Verification**: 构造包含 sync 字段的 `WIKI.md` fixture，通过 `wiki-ingest` SKILL.md 的 pre-condition 声明验证字段被识别。同时验证 `WIKI.md` 不包含这些字段时（旧格式），workflow 仍能正常运行（向后兼容）。

```
Given: WIKI.md frontmatter 包含 remote_sync_path: "wiki" 和 auto_sync: false
When:  wiki-ingest 读取 WIKI.md 解析运行时状态
Then:  识别 remote_sync_path 为 "wiki"，auto_sync 为 false
```

```
Given: WIKI.md frontmatter 不包含 remote_sync_path 或 auto_sync（旧格式）
When:  wiki-ingest 读取 WIKI.md 解析运行时状态
Then:  remote_sync_path 视为空字符串，auto_sync 视为 false（向后兼容，跳过同步）
```

**Interfaces to Test Through**: `WIKI.md` 静态分析、`skill/wiki-ingest/SKILL.md` 中 pre-condition 字段声明

---

### REQ-15: `wiki-init` 模板写入 sync 字段默认值

**Behavior**: `wiki-init` 初始化新 wiki 时，生成的 `WIKI.md` 模板必须包含 `remote_sync_path: wiki` 和 `auto_sync: false` 作为默认值。

**Test Verification**: 读取 `skill/wiki-init/templates/WIKI.md`，验证 frontmatter 中包含这两个字段且默认值正确。

```
Given: wiki-init 模板文件 skill/wiki-init/templates/WIKI.md
When:  读取模板内容
Then:  frontmatter 包含 remote_sync_path: wiki 和 auto_sync: false
```

**Interfaces to Test Through**: `skill/wiki-init/templates/WIKI.md` 静态分析

---

### REQ-16: `wiki-ingest` pre-condition 声明 sync 字段解析

**Behavior**: `wiki-ingest` SKILL.md 的 Pre-condition 节必须声明从 `WIKI.md` 解析 `remote_sync_path` 和 `auto_sync`，与已有的 `wiki_root` 等字段并列。

**Test Verification**: 静态读取 `skill/wiki-ingest/SKILL.md`，验证 Pre-condition 节中在 "Read WIKI.md to resolve" 列表中包含 `remote_sync_path` 和 `auto_sync`。

```
Given: skill/wiki-ingest/SKILL.md
When:  读取 Pre-condition 节的字段解析列表
Then:  列表包含 remote_sync_path 和 auto_sync
```

**Interfaces to Test Through**: `skill/wiki-ingest/SKILL.md` 静态分析

---

### REQ-17: `wiki-ingest` 在摄入完成后执行云端同步

**Behavior**: `wiki-ingest` 在完成现有 11 步摄入流程后，新增第 12 步 "Cloud Sync"。该步骤按以下逻辑执行：

1. 若 `remote_sync_path` 为空字符串，静默跳过同步
2. 若 `pcloud` CLI 不可用（未安装或未配置），发出警告但不阻塞 ingest 主流程
3. 若 `auto_sync = true`，直接执行 `pcloud sync <wiki_root> <remote_sync_path>`
4. 若 `auto_sync = false`（默认），先执行 `pcloud sync <wiki_root> <remote_sync_path> --dry-run` 展示同步计划（上传/下载文件列表），询问用户确认后执行实际同步
5. 同步完成后追加 `sync` 记录到 `wiki/log.md`，包含上传和下载文件计数

**Test Verification**: 静态读取 `skill/wiki-ingest/SKILL.md`，验证步骤 12 存在且描述了上述完整逻辑。

```
Given: skill/wiki-ingest/SKILL.md
When:  读取流程步骤
Then:  步骤 12 存在，标题为 "Cloud Sync" 或类似，包含:
       - remote_sync_path 为空时跳过的逻辑
       - pcloud 不可用时的警告逻辑
       - auto_sync = true 时的直接同步逻辑
       - auto_sync = false 时的 dry-run → 确认 → 执行交互序列
       - sync 完成后追加 log.md 的记录格式
```

**Interfaces to Test Through**: `skill/wiki-ingest/SKILL.md` 静态分析

---

### REQ-18: 云端同步失败不阻塞 ingest 主流程

**Behavior**: 若云端同步步骤执行失败（如网络错误、pcloud 返回非零退出码），`wiki-ingest` 应报告错误但不回滚已完成的摄入操作。ingest 的页面写入、index 更新和 log 记录不受 sync 失败影响。

**Test Verification**: 静态验证 `skill/wiki-ingest/SKILL.md` 步骤 12 中明确声明 sync 失败不影响 ingest 主流程。

```
Given: skill/wiki-ingest/SKILL.md 步骤 12
When:  读取错误处理描述
Then:  明确声明 sync 失败不阻塞、不回滚 ingest 结果
```

**Interfaces to Test Through**: `skill/wiki-ingest/SKILL.md` 静态分析

---

### REQ-19: `wiki-init` 复用已有配置时同步字段参与提问裁剪

**Behavior**: 当 `wiki-init` 进入已有配置复用路径时，若 `WIKI.md` 已包含 `remote_sync_path` 和 `auto_sync`，不应重复询问这些字段。若缺失（旧格式 `WIKI.md`），应补问并接受默认值。

**Test Verification**: 提供包含完整 sync 字段的 `WIKI.md` fixture，验证复用路径不询问 sync 字段。提供缺失 sync 字段的旧格式 `WIKI.md`，验证补问时展示默认值 `"wiki"` / `false`。

```
Given: 已有 WIKI.md 包含 remote_sync_path: "wiki" 和 auto_sync: false
When:  wiki-init 识别为已有配置并进入复用路径
Then:  不询问 remote_sync_path 和 auto_sync（提问裁剪）
```

```
Given: 已有 WIKI.md 不包含 remote_sync_path 和 auto_sync（旧格式）
When:  wiki-init 识别为已有配置并进入复用路径
Then:  补问 sync 字段，默认值分别为 "wiki" 和 false
```

**Interfaces to Test Through**: `wiki-init` 技能交互输出、`skill/wiki-init/SKILL.md` 中的提问裁剪逻辑

---

## Test Structure

### 静态分析测试

```python
def test_wiki_md_template_contains_sync_fields(self):
    """验证 wiki-init 模板包含 sync 字段默认值"""
    template = read_file("skill/wiki-init/templates/WIKI.md")
    assert "remote_sync_path: wiki" in template
    assert "auto_sync: false" in template

def test_wiki_ingest_precondition_declares_sync_fields(self):
    """验证 wiki-ingest pre-condition 声明 sync 字段"""
    skill_md = read_file("skill/wiki-ingest/SKILL.md")
    assert "remote_sync_path" in skill_md
    assert "auto_sync" in skill_md

def test_wiki_ingest_has_step_12_cloud_sync(self):
    """验证 wiki-ingest 包含第 12 步 Cloud Sync"""
    skill_md = read_file("skill/wiki-ingest/SKILL.md")
    assert "Cloud Sync" in skill_md or "cloud sync" in skill_md.lower()
    assert "pcloud sync" in skill_md
    assert "--dry-run" in skill_md

def test_wiki_md_runtime_contains_sync_fields(self):
    """验证运行时 WIKI.md 包含 sync 字段"""
    wiki_md = read_file("WIKI.md")
    assert "remote_sync_path" in wiki_md
    assert "auto_sync" in wiki_md

def test_wiki_ingest_sync_non_blocking(self):
    """验证 sync 失败不阻塞 ingest"""
    skill_md = read_file("skill/wiki-ingest/SKILL.md")
    # 步骤 12 中应有非阻塞声明
    step12_section = extract_step(skill_md, 12)
    assert "不阻塞" in step12_section or "non-blocking" in step12_section.lower()
```

### Test Files to Create

| File | Purpose |
|------|---------|
| `tests/test_cloud_sync_static.py` | 静态分析：验证 WIKI.md 模板、SKILL.md、运行时 WIKI.md 中的 sync 字段 |
| `tests/test_agent_skill_smoke_e2e.py` | 扩展：验证 wiki-init 复用路径对 sync 字段的提问裁剪 |

## Edge Cases

- `remote_sync_path` 为空字符串时，`wiki-ingest` 静默跳过同步，不调用 `pcloud`
- `pcloud` CLI 未安装在 PATH 中时，发出警告 "pcloud not found, skipping cloud sync"，不阻塞
- `pcloud` 已安装但未配置 `~/.config/pcloud/config.toml` 时，发出警告 "pcloud not configured, run pcloud config init first"，不阻塞
- `pcloud sync --dry-run` 显示 0 变更时，告知用户 "云端已是最新" 并视为成功
- `pcloud sync` 执行中途失败（网络错误等），报告错误但不回滚已完成的摄入操作
- `WIKI.md` 不存在 `remote_sync_path` 字段（旧格式），视为空字符串，向后兼容跳过同步
- `remote_sync_path` 包含特殊字符或空格，由 `pcloud` 自行校验和处理
- 用户在 dry-run 预览后选择跳过（回答 "n"），不执行同步但 ingest 已成功完成
