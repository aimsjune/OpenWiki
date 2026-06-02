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

func TestPageCreateWithFileFlagContent(t *testing.T) {
	dir := t.TempDir()
	tomlPath := setupTestWiki(t, dir)

	contentFile := filepath.Join(dir, "content.md")
	content := "---\ntitle: 内容测试\ntags: [test]\nscope_level: industry\nscope_code: wisdom\nupdated: 2026-06-02\n---\n\n这是测试页面的正文内容\n"
	if err := os.WriteFile(contentFile, []byte(content), 0644); err != nil {
		t.Fatalf("failed to write content file: %v", err)
	}

	var stdout, stderr bytes.Buffer

	err := cli.RunWithIO([]string{"--config", tomlPath, "page", "create", "content-test", "--file", contentFile, "--json"}, "1.0.0", "2026-06-01T00:00:00Z", &stdout, &stderr)
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
	pagePath := filepath.Join(wikiRoot, "wiki", "pages", "content-test.md")
	pageContent, err := os.ReadFile(pagePath)
	if err != nil {
		t.Fatalf("failed to read page file: %v", err)
	}

	if !bytes.Contains(pageContent, []byte("这是测试页面的正文内容")) {
		t.Errorf("页面内容不包含预期正文，实际内容: %s", string(pageContent))
	}
	if !bytes.Contains(pageContent, []byte("title: 内容测试")) {
		t.Errorf("页面内容不包含预期 frontmatter title")
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

func TestPageUpdateWithFileFlagAfterSlug(t *testing.T) {
	dir := t.TempDir()
	tomlPath := setupTestWiki(t, dir)

	contentFile := filepath.Join(dir, "updated2.md")
	content := "---\ntitle: 页面B更新\ntags: [updated]\nscope_level: industry\nscope_code: test\nupdated: 2026-06-03\n---\n\nslug 在 --file 之前的更新内容\n"
	if err := os.WriteFile(contentFile, []byte(content), 0644); err != nil {
		t.Fatalf("failed to write content file: %v", err)
	}

	var stdout, stderr bytes.Buffer

	err := cli.RunWithIO([]string{"--config", tomlPath, "page", "update", "page-b", "--file", contentFile, "--json"}, "1.0.0", "2026-06-01T00:00:00Z", &stdout, &stderr)
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
	pagePath := filepath.Join(wikiRoot, "wiki", "pages", "page-b.md")
	pageContent, err := os.ReadFile(pagePath)
	if err != nil {
		t.Fatalf("failed to read page file: %v", err)
	}
	if !bytes.Contains(pageContent, []byte("slug 在 --file 之前的更新内容")) {
		t.Errorf("页面内容不包含预期更新内容，实际内容: %s", string(pageContent))
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

func TestPageCreateFileNotFound(t *testing.T) {
	dir := t.TempDir()
	tomlPath := setupTestWiki(t, dir)

	var stdout, stderr bytes.Buffer

	err := cli.RunWithIO([]string{"--config", tomlPath, "page", "create", "new-page", "--file", "/nonexistent/file.md", "--json"}, "1.0.0", "2026-06-01T00:00:00Z", &stdout, &stderr)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	var resp output.Response
	if err := json.Unmarshal(stdout.Bytes(), &resp); err != nil {
		t.Fatalf("failed to unmarshal response: %v", err)
	}

	if resp.Success {
		t.Fatal("expected success=false for nonexistent file")
	}
	if resp.Error == nil {
		t.Fatal("expected error info")
	}
	if resp.Error.Code != "IO_ERROR" {
		t.Errorf("expected error code IO_ERROR, got %s", resp.Error.Code)
	}
}

func TestPageCreateNoSlug(t *testing.T) {
	dir := t.TempDir()
	tomlPath := setupTestWiki(t, dir)

	contentFile := filepath.Join(dir, "content.md")
	content := "---\ntitle: 测试\ntags: [test]\nscope_level: industry\nscope_code: test\nupdated: 2026-06-02\n---\n\n内容\n"
	if err := os.WriteFile(contentFile, []byte(content), 0644); err != nil {
		t.Fatalf("failed to write content file: %v", err)
	}

	var stdout, stderr bytes.Buffer

	err := cli.RunWithIO([]string{"--config", tomlPath, "page", "create", "--file", contentFile}, "1.0.0", "2026-06-01T00:00:00Z", &stdout, &stderr)
	if err == nil {
		t.Fatal("expected error for missing slug")
	}
	if err.Error() != "page create 需要指定 slug" {
		t.Errorf("expected slug error, got: %v", err)
	}
}

func TestPageCreateEmptyFile(t *testing.T) {
	dir := t.TempDir()
	tomlPath := setupTestWiki(t, dir)

	contentFile := filepath.Join(dir, "empty.md")
	if err := os.WriteFile(contentFile, []byte(""), 0644); err != nil {
		t.Fatalf("failed to write empty file: %v", err)
	}

	var stdout, stderr bytes.Buffer

	err := cli.RunWithIO([]string{"--config", tomlPath, "page", "create", "empty-page", "--file", contentFile, "--json"}, "1.0.0", "2026-06-01T00:00:00Z", &stdout, &stderr)
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
	pagePath := filepath.Join(wikiRoot, "wiki", "pages", "empty-page.md")
	if _, err := os.Stat(pagePath); os.IsNotExist(err) {
		t.Error("expected page file to exist even with empty content")
	}
}
