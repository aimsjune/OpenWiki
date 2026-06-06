package wiki_test

import (
	"path/filepath"
	"testing"

	"github.com/bytedance/openwiki/internal/wiki"
)

func TestInitCreatesEntitiesDir(t *testing.T) {
	fs := wiki.NewMemFS()
	root := "/test-wiki"

	cfg := map[string]interface{}{
		"wiki_root": root,
	}

	err := wiki.Init(fs, root, cfg)
	if err != nil {
		t.Fatalf("Init failed: %v", err)
	}

	entitiesDir := filepath.Join(root, "entities")
	if _, err := fs.Stat(entitiesDir); err != nil {
		t.Errorf("expected entities/ directory to exist at %s, got error: %v", entitiesDir, err)
	}
}
