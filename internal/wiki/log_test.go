package wiki_test

import (
	"path/filepath"
	"testing"

	"github.com/bytedance/openwiki/internal/wiki"
)

func setupTestWikiWithLog(t *testing.T) (wiki.FS, string) {
	t.Helper()
	fs := wiki.NewMemFS()
	root := "/test-wiki"

	fs.MkdirAll(filepath.Join(root, "wiki", "pages"), 0755)

	logContent := `# 操作日志

| 时间 | 操作 | 详情 |
|------|------|------|
| 2026-06-01 10:00:00 | ingest | test-page |
| 2026-06-01 11:00:00 | lint | 健康检查通过 |
| 2026-06-01 12:00:00 | update | test-page |
`
	fs.WriteFile(filepath.Join(root, "wiki", "log.md"), []byte(logContent), 0644)

	return fs, root
}

func TestShowLog(t *testing.T) {
	fs, root := setupTestWikiWithLog(t)

	entries, err := wiki.ShowLog(fs, root, 0)
	if err != nil {
		t.Fatalf("ShowLog failed: %v", err)
	}

	if len(entries) != 3 {
		t.Errorf("expected 3 entries, got %d", len(entries))
	}
}

func TestShowLogWithLimit(t *testing.T) {
	fs, root := setupTestWikiWithLog(t)

	entries, err := wiki.ShowLog(fs, root, 2)
	if err != nil {
		t.Fatalf("ShowLog failed: %v", err)
	}

	if len(entries) != 2 {
		t.Errorf("expected 2 entries, got %d", len(entries))
	}
}

func TestShowLogEmpty(t *testing.T) {
	fs := wiki.NewMemFS()
	root := "/test-wiki"
	fs.MkdirAll(filepath.Join(root, "wiki"), 0755)
	fs.WriteFile(filepath.Join(root, "wiki", "log.md"), []byte(`# 操作日志

| 时间 | 操作 | 详情 |
|------|------|------|
`), 0644)

	entries, err := wiki.ShowLog(fs, root, 0)
	if err != nil {
		t.Fatalf("ShowLog failed: %v", err)
	}

	if len(entries) != 0 {
		t.Errorf("expected 0 entries, got %d", len(entries))
	}
}

func TestAppendLog(t *testing.T) {
	fs, root := setupTestWikiWithLog(t)

	err := wiki.AppendLog(fs, root, "ingest", "new-page")
	if err != nil {
		t.Fatalf("AppendLog failed: %v", err)
	}

	entries, _ := wiki.ShowLog(fs, root, 0)
	if len(entries) != 4 {
		t.Errorf("expected 4 entries after append, got %d", len(entries))
	}
}
