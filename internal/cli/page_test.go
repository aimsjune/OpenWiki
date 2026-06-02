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

func TestPageList(t *testing.T) {
	dir := t.TempDir()
	tomlPath := setupTestWiki(t, dir)

	var stdout, stderr bytes.Buffer

	err := cli.RunWithIO([]string{"--config", tomlPath, "page", "list", "--json"}, "1.0.0", "2026-06-01T00:00:00Z", &stdout, &stderr)
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

	pages, ok := data["pages"].([]interface{})
	if !ok {
		t.Fatal("expected pages to be an array")
	}
	if len(pages) != 2 {
		t.Errorf("expected 2 pages, got %d", len(pages))
	}
}

func TestPageGet(t *testing.T) {
	dir := t.TempDir()
	tomlPath := setupTestWiki(t, dir)

	var stdout, stderr bytes.Buffer

	err := cli.RunWithIO([]string{"--config", tomlPath, "page", "get", "page-a", "--json"}, "1.0.0", "2026-06-01T00:00:00Z", &stdout, &stderr)
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
	if data["slug"] != "page-a" {
		t.Errorf("expected slug=page-a, got %v", data["slug"])
	}
}

func TestPageGetNotFound(t *testing.T) {
	dir := t.TempDir()
	tomlPath := setupTestWiki(t, dir)

	var stdout, stderr bytes.Buffer

	err := cli.RunWithIO([]string{"--config", tomlPath, "page", "get", "nonexistent", "--json"}, "1.0.0", "2026-06-01T00:00:00Z", &stdout, &stderr)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	var resp output.Response
	if err := json.Unmarshal(stdout.Bytes(), &resp); err != nil {
		t.Fatalf("failed to unmarshal response: %v", err)
	}

	if resp.Success {
		t.Fatal("expected success=false for nonexistent page")
	}
}

func TestPageCreate(t *testing.T) {
	dir := t.TempDir()
	tomlPath := setupTestWiki(t, dir)

	contentFile := filepath.Join(dir, "new-page.md")
	content := "---\ntitle: 新页面\ntags: [new, test]\nscope_level: industry\nscope_code: wisdom\nupdated: 2026-06-02\n---\n\n这是新页面的内容\n"
	if err := os.WriteFile(contentFile, []byte(content), 0644); err != nil {
		t.Fatalf("failed to write content file: %v", err)
	}

	var stdout, stderr bytes.Buffer

	err := cli.RunWithIO([]string{"--config", tomlPath, "page", "create", "new-page", "--file", contentFile, "--json"}, "1.0.0", "2026-06-01T00:00:00Z", &stdout, &stderr)
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

	wikiRoot := filepath.Dir(tomlPath)
	pagePath := filepath.Join(wikiRoot, "wiki", "pages", "new-page.md")
	if _, err := os.Stat(pagePath); os.IsNotExist(err) {
		t.Error("expected page file to exist")
	}
}

func TestPageCreateDuplicate(t *testing.T) {
	dir := t.TempDir()
	tomlPath := setupTestWiki(t, dir)

	contentFile := filepath.Join(dir, "dup.md")
	content := "---\ntitle: 重复\ntags: [test]\nscope_level: industry\nscope_code: wisdom\nupdated: 2026-06-02\n---\n\n内容\n"
	if err := os.WriteFile(contentFile, []byte(content), 0644); err != nil {
		t.Fatalf("failed to write content file: %v", err)
	}

	var stdout, stderr bytes.Buffer

	err := cli.RunWithIO([]string{"--config", tomlPath, "page", "create", "page-a", "--file", contentFile, "--json"}, "1.0.0", "2026-06-01T00:00:00Z", &stdout, &stderr)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	var resp output.Response
	if err := json.Unmarshal(stdout.Bytes(), &resp); err != nil {
		t.Fatalf("failed to unmarshal response: %v", err)
	}

	if resp.Success {
		t.Fatal("expected success=false for duplicate page")
	}
}

func TestPageUpdate(t *testing.T) {
	dir := t.TempDir()
	tomlPath := setupTestWiki(t, dir)

	contentFile := filepath.Join(dir, "updated.md")
	content := "---\ntitle: 页面A更新\ntags: [updated]\nscope_level: industry\nscope_code: test\nupdated: 2026-06-03\n---\n\n更新后的内容\n"
	if err := os.WriteFile(contentFile, []byte(content), 0644); err != nil {
		t.Fatalf("failed to write content file: %v", err)
	}

	var stdout, stderr bytes.Buffer

	err := cli.RunWithIO([]string{"--config", tomlPath, "page", "update", "--file", contentFile, "page-a", "--json"}, "1.0.0", "2026-06-01T00:00:00Z", &stdout, &stderr)
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

	wikiRoot := filepath.Dir(tomlPath)
	pagePath := filepath.Join(wikiRoot, "wiki", "pages", "page-a.md")
	pageContent, _ := os.ReadFile(pagePath)
	if !bytes.Contains(pageContent, []byte("更新后的内容")) {
		t.Error("expected page content to be updated")
	}
}

func TestPageDelete(t *testing.T) {
	dir := t.TempDir()
	tomlPath := setupTestWiki(t, dir)

	var stdout, stderr bytes.Buffer

	err := cli.RunWithIO([]string{"--config", tomlPath, "page", "delete", "page-a", "--force", "--json"}, "1.0.0", "2026-06-01T00:00:00Z", &stdout, &stderr)
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

	wikiRoot := filepath.Dir(tomlPath)
	pagePath := filepath.Join(wikiRoot, "wiki", "pages", "page-a.md")
	if _, err := os.Stat(pagePath); !os.IsNotExist(err) {
		t.Error("expected page file to be deleted")
	}
}
