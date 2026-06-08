package wiki_test

import (
	"fmt"
	"path/filepath"
	"strings"
	"sync"
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

func TestAppendLogEscapesMarkdownTableSeparators(t *testing.T) {
	fs, root := setupTestWikiWithLog(t)

	err := wiki.AppendLog(fs, root, "ingest", "source | created page")
	if err != nil {
		t.Fatalf("AppendLog failed: %v", err)
	}

	data, err := fs.ReadFile(filepath.Join(root, "wiki", "log.md"))
	if err != nil {
		t.Fatalf("ReadFile failed: %v", err)
	}
	if strings.Contains(string(data), "| source | created page |") {
		t.Fatalf("unescaped separator broke log table: %s", string(data))
	}
	if !strings.Contains(string(data), "source &#124; created page") {
		t.Fatalf("expected escaped separator, got: %s", string(data))
	}
}

func TestConcurrentAppendLogKeepsEveryEntry(t *testing.T) {
	fs := wiki.NewOsFS()
	root := t.TempDir()
	if err := fs.MkdirAll(filepath.Join(root, "wiki"), 0755); err != nil {
		t.Fatalf("MkdirAll failed: %v", err)
	}
	initialLog := "# 操作日志\n\n| 时间 | 操作 | 详情 |\n|------|------|------|\n"
	if err := fs.WriteFile(filepath.Join(root, "wiki", "log.md"), []byte(initialLog), 0644); err != nil {
		t.Fatalf("WriteFile failed: %v", err)
	}

	const entryCount = 20
	var wg sync.WaitGroup
	errors := make(chan error, entryCount)
	for i := 0; i < entryCount; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			errors <- wiki.AppendLog(fs, root, "ingest", fmt.Sprintf("entry-%02d", i))
		}(i)
	}
	wg.Wait()
	close(errors)
	for err := range errors {
		if err != nil {
			t.Fatalf("concurrent AppendLog failed: %v", err)
		}
	}

	entries, err := wiki.ShowLog(fs, root, 0)
	if err != nil {
		t.Fatalf("ShowLog failed: %v", err)
	}
	if len(entries) != entryCount {
		t.Fatalf("expected %d log entries, got %d", entryCount, len(entries))
	}
}
