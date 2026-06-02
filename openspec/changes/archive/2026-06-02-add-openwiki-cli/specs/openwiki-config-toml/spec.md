# Specification: openwiki-config-toml

## Overview

将 wiki 配置从 Markdown + YAML frontmatter（WIKI.md）迁移为纯 TOML 格式（openwiki.toml），并统一配置发现机制。

## Requirements

### REQ-1: openwiki.toml 配置结构

**Behavior**: 系统使用 TOML 格式存储 wiki 配置，包含 wiki_root、语言设置、源类型、远程同步等字段。

**Test Verification**: 解析已知 TOML 文件，验证所有字段正确映射到 Go 结构体。

```
Given: 一个有效的 openwiki.toml 文件，包含所有配置字段
When:  调用 config.Load(path)
Then:  返回的 Config 结构体所有字段与 TOML 内容一致
```

**Interfaces to Test Through**: `internal/config/config.go` 的 `Load(path string) (*Config, error)`

**TOML 结构定义**:

```toml
wiki_root = "/Users/me/wiki"

[wiki]
primary_language = "zh"
secondary_language = "en"

[wiki.source_types]
types = ["papers", "urls", "code", "docs", "transcripts"]

[wiki.index]
categories = ["资料页", "概念页", "适用范围", "快速导航"]

[remote]
sync_path = "wiki"
auto_sync = false
```

---

### REQ-2: 配置发现优先级链

**Behavior**: 系统按以下优先级发现配置：
1. `--config/-c` 显式指定路径
2. `OPENWIKI_CONFIG` 环境变量
3. `~/.openwiki/openwiki.toml`（全局默认）
4. 从 CWD 向上逐层搜索 `openwiki.toml`

**Test Verification**: 4 种场景分别验证返回正确的配置路径和来源标记。

```
Given: 未设置 --config 和 OPENWIKI_CONFIG，~/.openwiki/openwiki.toml 存在
When:  调用 discovery.Discover("")
Then:  返回 ~/.openwiki/openwiki.toml，source 为 "global"

Given: 设置环境变量 OPENWIKI_CONFIG=/custom/path/openwiki.toml
When:  调用 discovery.Discover("")
Then:  返回 /custom/path/openwiki.toml，source 为 "env"

Given: 传入 --config /explicit/path/openwiki.toml
When:  调用 discovery.Discover("/explicit/path/openwiki.toml")
Then:  返回 /explicit/path/openwiki.toml，source 为 "explicit"

Given: 当前目录 /home/user/project/wiki/ 含 openwiki.toml
When:  调用 discovery.Discover("")，从 CWD 向上搜索
Then:  返回 /home/user/project/wiki/openwiki.toml，source 为 "local"
```

**Interfaces to Test Through**: `internal/config/discovery.go` 的 `Discover(explicitPath string) (*DiscoveryResult, error)`

---

### REQ-3: 配置校验

**Behavior**: 系统验证 openwiki.toml 的必填字段和字段值有效性。

**Test Verification**: 给定各种无效配置，验证返回具体错误码和详情。

```
Given: openwiki.toml 缺少 wiki_root 字段
When:  调用 config.Validate(cfg)
Then:  返回 error，code 为 "CONFIG_MISSING_FIELD"，details 含 "wiki_root"

Given: openwiki.toml 的 primary_language 值为 "fr"
When:  调用 config.Validate(cfg)
Then:  返回 error，code 为 "CONFIG_INVALID_FIELD"，details 含 allowed 列表 ["zh", "en"]

Given: openwiki.toml 的 wiki_root 指向不存在的目录
When:  调用 config.Validate(cfg)
Then:  返回 error，code 为 "CONFIG_INVALID_PATH"
```

**Interfaces to Test Through**: `internal/config/validate.go` 的 `Validate(cfg *Config) error`

---

### REQ-4: 配置读写

**Behavior**: 系统支持读取完整配置、获取单个配置项、设置配置项。

**Test Verification**: 通过 CLI 命令验证配置读写。

```
Given: 一个有效的 openwiki.toml
When:  执行 openwiki config show --json
Then:  JSON 输出含所有配置字段

Given: 一个有效的 openwiki.toml，wiki.primary_language = "zh"
When:  执行 openwiki config get wiki.primary_language --json
Then:  data.value = "zh"

Given: 一个有效的 openwiki.toml
When:  执行 openwiki config set wiki.primary_language en --json
Then:  data.old_value = "zh", data.new_value = "en"，文件已更新
```

**Interfaces to Test Through**: CLI 命令 `openwiki config show/get/set`

---

### REQ-5: 配置路径查询

**Behavior**: `openwiki config path` 输出当前使用的配置路径和来源。

**Test Verification**: 验证输出含 path 和 source 字段。

```
Given: 使用全局默认配置
When:  执行 openwiki config path --json
Then:  data.path = "~/.openwiki/openwiki.toml", data.source = "global"
```

**Interfaces to Test Through**: CLI 命令 `openwiki config path`

---

## Test Structure

### 单元测试

```go
func TestConfigLoad(t *testing.T) {
    // Given: 临时目录中的有效 openwiki.toml
    dir := t.TempDir()
    tomlPath := filepath.Join(dir, "openwiki.toml")
    os.WriteFile(tomlPath, []byte(validTOML), 0644)

    // When
    cfg, err := config.Load(tomlPath)

    // Then
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
    if cfg.WikiRoot != "/Users/me/wiki" {
        t.Errorf("expected wiki_root=/Users/me/wiki, got %s", cfg.WikiRoot)
    }
}
```

### Test Files to Create

| File | Purpose |
|------|---------|
| `internal/config/config_test.go` | TOML 解析测试 |
| `internal/config/discovery_test.go` | 配置发现优先级测试 |
| `internal/config/validate_test.go` | 配置校验测试 |

## Edge Cases

- TOML 文件不存在时返回明确错误
- TOML 语法错误时返回解析错误（含行号）
- 配置路径含 `~` 时正确展开为 HOME 目录
- CWD 向上搜索到达文件系统根目录仍未找到时返回 `ErrConfigNotFound`
- 环境变量 `OPENWIKI_CONFIG` 指向不存在的文件时返回错误
