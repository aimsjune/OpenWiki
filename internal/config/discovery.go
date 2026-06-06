package config

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

var ErrConfigNotFound = errors.New("未找到 openwiki.toml 配置文件")

type DiscoveryResult struct {
	Path   string `json:"path"`
	Source string `json:"source"`
}

type Discoverer interface {
	Discover(explicitPath string) (*DiscoveryResult, error)
}

type DefaultDiscoverer struct {
	HomeDir string
	Getenv  func(string) string
	Getwd   func() (string, error)
}

func NewDefaultDiscoverer() *DefaultDiscoverer {
	homeDir, _ := os.UserHomeDir()
	return &DefaultDiscoverer{
		HomeDir: homeDir,
		Getenv:  os.Getenv,
		Getwd:   os.Getwd,
	}
}

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

func expandPath(path string) string {
	if strings.HasPrefix(path, "~/") {
		homeDir, err := os.UserHomeDir()
		if err == nil {
			return filepath.Join(homeDir, path[2:])
		}
	}
	return path
}
