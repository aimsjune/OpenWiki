# 配置发现顺序：local > global

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 openwiki CLI 的配置发现顺序从 `explicit → env → global → local` 改为 `explicit → env → local → global`，使项目本地配置优先于全局配置。

**Architecture:** 修改 `internal/config/discovery.go` 中 `Discover` 方法的检查顺序，将 local（CWD 向上搜索）移到 global（`~/.openwiki/openwiki.toml`）之前。新增测试验证 local 优先于 global 的场景。

**Tech Stack:** Go 1.26.3, 标准库 `os`/`path/filepath`/`testing`

---

### Task 1: 调整 local 和 global 的检查顺序

**Files:**
- Modify: `internal/config/discovery.go:37-74`

- [ ] **Step 1: 将 local 检查移到 global 之前**

在 `internal/config/discovery.go` 中，将第 54-57 行的 global 检查块与第 59-71 行的 local 检查块交换位置。

当前代码（第 37-74 行）：

```go
func (d *DefaultDiscoverer) Discover(explicitPath string) (*DiscoveryResult, error) {
	if explicitPath != "" {
		path := expandPath(explicitPath)
		if _, err := os.Stat(path); err != nil {
			return nil, fmt.Errorf("%w: %s", ErrConfigNotFound, path)
		}
		return &DiscoveryResult{Path: path, Source: "explicit"}, nil
	}

	if envPath := d.Getenv("OPENWIKI_CONFIG"); envPath != "" {
		path := expandPath(envPath)
		if _, err := os.Stat(path); err != nil {
			return nil, fmt.Errorf("%w: OPENWIKI_CONFIG=%s", ErrConfigNotFound, envPath)
		}
		return &DiscoveryResult{Path: path, Source: "env"}, nil
	}

	globalPath := filepath.Join(d.HomeDir, ".openwiki", "openwiki.toml")
	if _, err := os.Stat(globalPath); err == nil {
		return &DiscoveryResult{Path: globalPath, Source: "global"}, nil
	}

	cwd, err := d.Getwd()
	if err != nil {
		return nil, fmt.Errorf("获取当前工作目录失败: %w", err)
	}
	for dir := cwd; dir != "/" && dir != "."; dir = filepath.Dir(dir) {
		candidate := filepath.Join(dir, "openwiki.toml")
		if _, err := os.Stat(candidate); err == nil {
			return &DiscoveryResult{Path: candidate, Source: "local"}, nil
		}
		if dir == filepath.Dir(dir) {
			break
		}
	}

	return nil, ErrConfigNotFound
}
```

改为：

```go
func (d *DefaultDiscoverer) Discover(explicitPath string) (*DiscoveryResult, error) {
	if explicitPath != "" {
		path := expandPath(explicitPath)
		if _, err := os.Stat(path); err != nil {
			return nil, fmt.Errorf("%w: %s", ErrConfigNotFound, path)
		}
		return &DiscoveryResult{Path: path, Source: "explicit"}, nil
	}

	if envPath := d.Getenv("OPENWIKI_CONFIG"); envPath != "" {
		path := expandPath(envPath)
		if _, err := os.Stat(path); err != nil {
			return nil, fmt.Errorf("%w: OPENWIKI_CONFIG=%s", ErrConfigNotFound, envPath)
		}
		return &DiscoveryResult{Path: path, Source: "env"}, nil
	}

	cwd, err := d.Getwd()
	if err != nil {
		return nil, fmt.Errorf("获取当前工作目录失败: %w", err)
	}
	for dir := cwd; dir != "/" && dir != "."; dir = filepath.Dir(dir) {
		candidate := filepath.Join(dir, "openwiki.toml")
		if _, err := os.Stat(candidate); err == nil {
			return &DiscoveryResult{Path: candidate, Source: "local"}, nil
		}
		if dir == filepath.Dir(dir) {
			break
		}
	}

	globalPath := filepath.Join(d.HomeDir, ".openwiki", "openwiki.toml")
	if _, err := os.Stat(globalPath); err == nil {
		return &DiscoveryResult{Path: globalPath, Source: "global"}, nil
	}

	return nil, ErrConfigNotFound
}
```

- [ ] **Step 2: 运行现有测试确保无回归**

```bash
cd /Users/bytedance/git/OpenWiki && go test ./internal/config/... -v -count=1
```

Expected: 所有现有测试 PASS（`TestDiscoverGlobalConfig` 仍然通过，因为其 CWD 是 `/`，没有 local config）。

- [ ] **Step 3: Commit**

```bash
git add internal/config/discovery.go
git commit -m "$(cat <<'EOF'
feat: 配置发现顺序改为 local 优先于 global

将 CWD 向上搜索的本地配置检查移到全局配置之前，使项目本地
openwiki.toml 优先于 ~/.openwiki/openwiki.toml。
EOF
)"
```

---

### Task 2: 新增 local 优先于 global 的测试

**Files:**
- Modify: `internal/config/discovery_test.go`（在文件末尾追加）

- [ ] **Step 1: 添加测试函数**

在 `internal/config/discovery_test.go` 文件末尾追加：

```go
func TestDiscoverLocalPriorityOverGlobal(t *testing.T) {
	// 同时创建 local 和 global 配置
	homeDir := t.TempDir()
	openwikiDir := filepath.Join(homeDir, ".openwiki")
	if err := os.MkdirAll(openwikiDir, 0755); err != nil {
		t.Fatalf("failed to create .openwiki dir: %v", err)
	}
	createTestTOML(t, openwikiDir) // global config

	localDir := t.TempDir()
	localTomlPath := createTestTOML(t, localDir) // local config

	d := &config.DefaultDiscoverer{
		HomeDir: homeDir,
		Getenv:  func(string) string { return "" },
		Getwd:   func() (string, error) { return localDir, nil },
	}

	result, err := d.Discover("")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result.Path != localTomlPath {
		t.Errorf("expected local config path=%s, got %s", localTomlPath, result.Path)
	}
	if result.Source != "local" {
		t.Errorf("expected source=local, got %s", result.Source)
	}
}
```

- [ ] **Step 2: 运行新测试验证通过**

```bash
cd /Users/bytedance/git/OpenWiki && go test ./internal/config/... -v -run TestDiscoverLocalPriorityOverGlobal -count=1
```

Expected: PASS

- [ ] **Step 3: 运行全部 config 测试**

```bash
cd /Users/bytedance/git/OpenWiki && go test ./internal/config/... -v -count=1
```

Expected: 全部 PASS

- [ ] **Step 4: Commit**

```bash
git add internal/config/discovery_test.go
git commit -m "$(cat <<'EOF'
feat: 新增 local 优先于 global 配置的测试用例

验证当本地和全局 openwiki.toml 同时存在时，本地配置优先被选中。
EOF
)"
```
