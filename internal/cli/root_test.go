package cli_test

import (
	"bytes"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/bytedance/openwiki/internal/cli"
)

func TestRootHelp(t *testing.T) {
	var stdout, stderr bytes.Buffer

	err := cli.RunWithIO([]string{"--help"}, "1.0.0", "2026-06-01T00:00:00Z", &stdout, &stderr)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	output := stdout.String()
	if !strings.Contains(output, "openwiki") {
		t.Error("expected help output to contain 'openwiki'")
	}
	if !strings.Contains(output, "Usage") && !strings.Contains(output, "用法") {
		t.Error("expected help output to contain usage information")
	}
}

func TestRootVersion(t *testing.T) {
	var stdout, stderr bytes.Buffer

	err := cli.RunWithIO([]string{"--version"}, "1.0.0", "2026-06-01T00:00:00Z", &stdout, &stderr)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	output := stdout.String()
	if !strings.Contains(output, "1.0.0") {
		t.Errorf("expected version output to contain '1.0.0', got '%s'", output)
	}
}

func TestRootVersionShortFlag(t *testing.T) {
	var stdout, stderr bytes.Buffer

	err := cli.RunWithIO([]string{"-v"}, "2.0.0", "2026-06-01T00:00:00Z", &stdout, &stderr)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	output := stdout.String()
	if !strings.Contains(output, "2.0.0") {
		t.Errorf("expected version output to contain '2.0.0', got '%s'", output)
	}
}

func TestRootConfigFlag(t *testing.T) {
	dir := t.TempDir()
	tomlPath := filepath.Join(dir, "openwiki.toml")
	content := `wiki_root = "/Users/me/wiki"

[wiki]
primary_language = "zh"
secondary_language = "en"
`
	if err := os.WriteFile(tomlPath, []byte(content), 0644); err != nil {
		t.Fatalf("failed to write test toml: %v", err)
	}

	var stdout, stderr bytes.Buffer

	err := cli.RunWithIO([]string{"--config", tomlPath, "config", "show", "--json"}, "1.0.0", "2026-06-01T00:00:00Z", &stdout, &stderr)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	output := stdout.String()
	if !strings.Contains(output, `"success": true`) {
		t.Errorf("expected JSON success response, got '%s'", output)
	}
}

func TestRootJSONFlag(t *testing.T) {
	dir := t.TempDir()
	tomlPath := filepath.Join(dir, "openwiki.toml")
	content := `wiki_root = "/Users/me/wiki"

[wiki]
primary_language = "zh"
secondary_language = "en"
`
	if err := os.WriteFile(tomlPath, []byte(content), 0644); err != nil {
		t.Fatalf("failed to write test toml: %v", err)
	}

	var stdout, stderr bytes.Buffer

	err := cli.RunWithIO([]string{"--config", tomlPath, "--json", "config", "show"}, "1.0.0", "2026-06-01T00:00:00Z", &stdout, &stderr)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	output := stdout.String()
	if !strings.Contains(output, `"success": true`) {
		t.Errorf("expected JSON success response, got '%s'", output)
	}
}

func TestRootUnknownCommand(t *testing.T) {
	var stdout, stderr bytes.Buffer

	err := cli.RunWithIO([]string{"nonexistent"}, "1.0.0", "2026-06-01T00:00:00Z", &stdout, &stderr)
	if err == nil {
		t.Fatal("expected error for unknown command, got nil")
	}
}

func TestRootNoArgs(t *testing.T) {
	var stdout, stderr bytes.Buffer

	err := cli.RunWithIO([]string{}, "1.0.0", "2026-06-01T00:00:00Z", &stdout, &stderr)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	output := stdout.String()
	if !strings.Contains(output, "openwiki") {
		t.Error("expected default output to contain 'openwiki'")
	}
}
