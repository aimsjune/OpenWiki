package wiki

import (
	"bytes"
	"fmt"
	"path/filepath"

	"github.com/BurntSushi/toml"
)

const indexTemplate = `# Wiki 索引

## 资料页

| Slug | 标题 | 标签 | 适用范围 | 最后更新 |
|------|------|------|----------|----------|

## 概念页

| Slug | 标题 | 标签 | 适用范围 | 最后更新 |
|------|------|------|----------|----------|

## 适用范围

| 范围代号 | 级别 | 页面数 |
|----------|------|--------|

## 快速导航

| 分类 | 页面 |
|------|------|
`

const logTemplate = `# 操作日志

| 时间 | 操作 | 详情 |
|------|------|------|
`

func Init(fs FS, root string, cfg interface{}) error {
	openwikiPath := filepath.Join(root, "openwiki.toml")
	if _, err := fs.Stat(openwikiPath); err == nil {
		return fmt.Errorf("wiki 实例已存在: %s", root)
	}

	return initInternal(fs, root, cfg)
}

func InitForce(fs FS, root string, cfg interface{}) error {
	return initInternal(fs, root, cfg)
}

func initInternal(fs FS, root string, cfg interface{}) error {
	dirs := []string{
		filepath.Join(root, "wiki", "pages"),
		filepath.Join(root, "raw"),
		filepath.Join(root, "concepts"),
	}
	for _, dir := range dirs {
		if err := fs.MkdirAll(dir, 0755); err != nil {
			return fmt.Errorf("创建目录失败 %s: %w", dir, err)
		}
	}

	if err := fs.WriteFile(filepath.Join(root, "wiki", "index.md"), []byte(indexTemplate), 0644); err != nil {
		return fmt.Errorf("创建 index.md 失败: %w", err)
	}

	if err := fs.WriteFile(filepath.Join(root, "wiki", "log.md"), []byte(logTemplate), 0644); err != nil {
		return fmt.Errorf("创建 log.md 失败: %w", err)
	}

	var buf bytes.Buffer
	encoder := toml.NewEncoder(&buf)
	if err := encoder.Encode(cfg); err != nil {
		return fmt.Errorf("编码 TOML 失败: %w", err)
	}

	openwikiPath := filepath.Join(root, "openwiki.toml")
	if err := fs.WriteFile(openwikiPath, buf.Bytes(), 0644); err != nil {
		return fmt.Errorf("创建 openwiki.toml 失败: %w", err)
	}

	return nil
}
