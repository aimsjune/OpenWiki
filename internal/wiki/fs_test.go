package wiki_test

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/bytedance/openwiki/internal/config"
	"github.com/bytedance/openwiki/internal/wiki"
)

func TestMemFSReadWrite(t *testing.T) {
	fs := wiki.NewMemFS()

	err := fs.WriteFile("/test/file.txt", []byte("hello"), 0644)
	if err != nil {
		t.Fatalf("WriteFile failed: %v", err)
	}

	data, err := fs.ReadFile("/test/file.txt")
	if err != nil {
		t.Fatalf("ReadFile failed: %v", err)
	}
	if string(data) != "hello" {
		t.Errorf("expected 'hello', got '%s'", string(data))
	}
}

func TestMemFSMkdirAll(t *testing.T) {
	fs := wiki.NewMemFS()

	err := fs.MkdirAll("/a/b/c", 0755)
	if err != nil {
		t.Fatalf("MkdirAll failed: %v", err)
	}

	err = fs.WriteFile("/a/b/c/file.txt", []byte("ok"), 0644)
	if err != nil {
		t.Fatalf("WriteFile after MkdirAll failed: %v", err)
	}
}

func TestMemFSRemove(t *testing.T) {
	fs := wiki.NewMemFS()

	fs.WriteFile("/test.txt", []byte("data"), 0644)
	err := fs.Remove("/test.txt")
	if err != nil {
		t.Fatalf("Remove failed: %v", err)
	}

	_, err = fs.ReadFile("/test.txt")
	if err == nil {
		t.Fatal("expected error after remove, got nil")
	}
}

func TestMemFSStat(t *testing.T) {
	fs := wiki.NewMemFS()

	fs.WriteFile("/test.txt", []byte("data"), 0644)
	info, err := fs.Stat("/test.txt")
	if err != nil {
		t.Fatalf("Stat failed: %v", err)
	}
	if info.Name() != "test.txt" {
		t.Errorf("expected name=test.txt, got %s", info.Name())
	}
}

func TestMemFSReadDir(t *testing.T) {
	fs := wiki.NewMemFS()

	fs.MkdirAll("/dir", 0755)
	fs.WriteFile("/dir/a.txt", []byte("a"), 0644)
	fs.WriteFile("/dir/b.txt", []byte("b"), 0644)

	entries, err := fs.ReadDir("/dir")
	if err != nil {
		t.Fatalf("ReadDir failed: %v", err)
	}
	if len(entries) != 2 {
		t.Errorf("expected 2 entries, got %d", len(entries))
	}
}

func TestMemFSGlob(t *testing.T) {
	fs := wiki.NewMemFS()

	fs.WriteFile("/dir/a.md", []byte("a"), 0644)
	fs.WriteFile("/dir/b.md", []byte("b"), 0644)
	fs.WriteFile("/dir/c.txt", []byte("c"), 0644)

	matches, err := fs.Glob("/dir/*.md")
	if err != nil {
		t.Fatalf("Glob failed: %v", err)
	}
	if len(matches) != 2 {
		t.Errorf("expected 2 matches, got %d", len(matches))
	}
}

func TestInitCreatesDirectoryStructure(t *testing.T) {
	fs := wiki.NewMemFS()
	root := "/test-wiki"

	cfg := &config.Config{
		WikiRoot: root,
		Wiki: config.WikiConfig{
			PrimaryLanguage:   "zh",
			SecondaryLanguage: "en",
		},
	}

	err := wiki.Init(fs, root, cfg)
	if err != nil {
		t.Fatalf("Init failed: %v", err)
	}

	dirs := []string{
		filepath.Join(root, "wiki", "pages"),
		filepath.Join(root, "raw"),
		filepath.Join(root, "concepts"),
	}
	for _, dir := range dirs {
		if _, err := fs.Stat(dir); err != nil {
			t.Errorf("expected directory %s to exist", dir)
		}
	}

	files := []string{
		filepath.Join(root, "openwiki.toml"),
		filepath.Join(root, "wiki", "index.md"),
		filepath.Join(root, "wiki", "log.md"),
	}
	for _, f := range files {
		if _, err := fs.ReadFile(f); err != nil {
			t.Errorf("expected file %s to exist", f)
		}
	}
}

func TestInitAlreadyExists(t *testing.T) {
	fs := wiki.NewMemFS()
	root := "/test-wiki"

	cfg := &config.Config{
		WikiRoot: root,
		Wiki: config.WikiConfig{
			PrimaryLanguage:   "zh",
			SecondaryLanguage: "en",
		},
	}

	err := wiki.Init(fs, root, cfg)
	if err != nil {
		t.Fatalf("first Init failed: %v", err)
	}

	err = wiki.Init(fs, root, cfg)
	if err == nil {
		t.Fatal("expected error for already existing wiki, got nil")
	}
}

func TestInitForceOverwrite(t *testing.T) {
	fs := wiki.NewMemFS()
	root := "/test-wiki"

	cfg := &config.Config{
		WikiRoot: root,
		Wiki: config.WikiConfig{
			PrimaryLanguage:   "zh",
			SecondaryLanguage: "en",
		},
	}

	err := wiki.Init(fs, root, cfg)
	if err != nil {
		t.Fatalf("first Init failed: %v", err)
	}

	cfg2 := &config.Config{
		WikiRoot: root,
		Wiki: config.WikiConfig{
			PrimaryLanguage:   "en",
			SecondaryLanguage: "zh",
		},
	}

	err = wiki.InitForce(fs, root, cfg2)
	if err != nil {
		t.Fatalf("InitForce failed: %v", err)
	}

	tomlData, _ := fs.ReadFile(filepath.Join(root, "openwiki.toml"))
	if len(tomlData) == 0 {
		t.Error("openwiki.toml should not be empty after force init")
	}
}

func TestOsFSReadWrite(t *testing.T) {
	dir := t.TempDir()
	fs := wiki.NewOsFS()

	testPath := filepath.Join(dir, "test.txt")
	err := fs.WriteFile(testPath, []byte("hello os"), 0644)
	if err != nil {
		t.Fatalf("WriteFile failed: %v", err)
	}

	data, err := fs.ReadFile(testPath)
	if err != nil {
		t.Fatalf("ReadFile failed: %v", err)
	}
	if string(data) != "hello os" {
		t.Errorf("expected 'hello os', got '%s'", string(data))
	}

	err = fs.Remove(testPath)
	if err != nil {
		t.Fatalf("Remove failed: %v", err)
	}

	_, err = os.Stat(testPath)
	if !os.IsNotExist(err) {
		t.Error("expected file to be removed")
	}
}
