package cli_test

import (
	"bytes"
	"encoding/json"
	"os"
	"path/filepath"
	"testing"

	"github.com/bytedance/openwiki/internal/cli"
	"github.com/bytedance/openwiki/internal/output"
)

func TestSyncDryRun(t *testing.T) {
	dir := t.TempDir()
	tomlPath := setupTestWiki(t, dir)

	cfgContent := `wiki_root = "` + filepath.Join(dir, "test-wiki") + `"

[wiki]
primary_language = "zh"
secondary_language = "en"

[wiki.source_types]
types = ["doc", "article"]

[wiki.index]
categories = ["资料页", "概念页"]

[remote]
sync_path = "/tmp/test-sync"
auto_sync = false
`
	if err := os.WriteFile(tomlPath, []byte(cfgContent), 0644); err != nil {
		t.Fatalf("write config failed: %v", err)
	}

	var stdout, stderr bytes.Buffer

	err := cli.RunWithIO([]string{"--config", tomlPath, "sync", "--dry-run", "--json"}, "1.0.0", "2026-06-01T00:00:00Z", &stdout, &stderr)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	var resp output.Response
	if err := json.Unmarshal(stdout.Bytes(), &resp); err != nil {
		t.Fatalf("failed to unmarshal response: %v", err)
	}

	if !resp.Success {
		t.Fatalf("expected success=true, got error: %v", resp.Error)
	}

	data, ok := resp.Data.(map[string]interface{})
	if !ok {
		t.Fatal("expected data to be a map")
	}

	if data["dry_run"] != true {
		t.Error("expected dry_run=true")
	}
}

func TestSyncNoRemote(t *testing.T) {
	dir := t.TempDir()
	tomlPath := setupTestWiki(t, dir)

	var stdout, stderr bytes.Buffer

	err := cli.RunWithIO([]string{"--config", tomlPath, "sync", "--json"}, "1.0.0", "2026-06-01T00:00:00Z", &stdout, &stderr)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	var resp output.Response
	if err := json.Unmarshal(stdout.Bytes(), &resp); err != nil {
		t.Fatalf("failed to unmarshal response: %v", err)
	}

	if resp.Success {
		t.Fatal("expected success=false for sync without remote config")
	}

	if resp.Error == nil {
		t.Fatal("expected error to be non-nil")
	}
}
