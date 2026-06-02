package wiki_test

import (
	"path/filepath"
	"testing"

	"github.com/bytedance/openwiki/internal/wiki"
)

func setupTestWiki(t *testing.T) (wiki.FS, string) {
	t.Helper()
	fs := wiki.NewMemFS()
	root := "/test-wiki"

	fs.MkdirAll(filepath.Join(root, "wiki", "pages"), 0755)

	indexContent := `# Wiki 索引

## 资料页

| Slug | 标题 | 标签 | 适用范围 | 最后更新 |
|------|------|------|----------|----------|
| test-page | 测试页面 | test, demo | repo/test-repo | 2026-06-01 |
| another-page | 另一个页面 | demo | domain/test-domain | 2026-05-30 |
`
	fs.WriteFile(filepath.Join(root, "wiki", "index.md"), []byte(indexContent), 0644)

	pageContent := `---
title: 测试页面
tags: [test, demo]
scope_level: repo
scope_code: test-repo
updated: 2026-06-01
---

# 测试页面

这是测试内容，引用 [[another-page]]。
`
	fs.WriteFile(filepath.Join(root, "wiki", "pages", "test-page.md"), []byte(pageContent), 0644)

	page2Content := `---
title: 另一个页面
tags: [demo]
scope_level: domain
scope_code: test-domain
updated: 2026-05-30
---

# 另一个页面

另一个页面的内容。
`
	fs.WriteFile(filepath.Join(root, "wiki", "pages", "another-page.md"), []byte(page2Content), 0644)

	return fs, root
}

func TestListPages(t *testing.T) {
	fs, root := setupTestWiki(t)

	pages, err := wiki.ListPages(fs, root)
	if err != nil {
		t.Fatalf("ListPages failed: %v", err)
	}

	if len(pages) != 2 {
		t.Errorf("expected 2 pages, got %d", len(pages))
	}

	if pages[0].Slug != "test-page" {
		t.Errorf("expected first slug=test-page, got %s", pages[0].Slug)
	}
	if pages[0].Title != "测试页面" {
		t.Errorf("expected title=测试页面, got %s", pages[0].Title)
	}
}

func TestGetPage(t *testing.T) {
	fs, root := setupTestWiki(t)

	page, err := wiki.GetPage(fs, root, "test-page")
	if err != nil {
		t.Fatalf("GetPage failed: %v", err)
	}

	if page.Slug != "test-page" {
		t.Errorf("expected slug=test-page, got %s", page.Slug)
	}
	if page.Frontmatter["title"] != "测试页面" {
		t.Errorf("expected title=测试页面, got %v", page.Frontmatter["title"])
	}
	if len(page.CrossReferences) != 1 {
		t.Errorf("expected 1 cross reference, got %d", len(page.CrossReferences))
	}
	if page.CrossReferences[0] != "another-page" {
		t.Errorf("expected cross reference=another-page, got %s", page.CrossReferences[0])
	}
}

func TestGetPageNotFound(t *testing.T) {
	fs, root := setupTestWiki(t)

	_, err := wiki.GetPage(fs, root, "nonexistent")
	if err == nil {
		t.Fatal("expected error for nonexistent page, got nil")
	}
}

func TestGetPagesBatch(t *testing.T) {
	fs, root := setupTestWiki(t)

	pages, err := wiki.GetPages(fs, root, []string{"test-page", "another-page"})
	if err != nil {
		t.Fatalf("GetPages failed: %v", err)
	}

	if len(pages) != 2 {
		t.Errorf("expected 2 pages, got %d", len(pages))
	}
}

func TestCreatePage(t *testing.T) {
	fs, root := setupTestWiki(t)

	page := &wiki.Page{
		Slug: "new-page",
		Frontmatter: map[string]interface{}{
			"title":       "新页面",
			"tags":        []string{"new"},
			"scope_level": "repo",
			"scope_code":  "new-repo",
			"updated":     "2026-06-01",
		},
		Body: "# 新页面\n\n这是新页面的内容。",
	}

	err := wiki.CreatePage(fs, root, page)
	if err != nil {
		t.Fatalf("CreatePage failed: %v", err)
	}

	created, err := wiki.GetPage(fs, root, "new-page")
	if err != nil {
		t.Fatalf("GetPage after create failed: %v", err)
	}
	if created.Slug != "new-page" {
		t.Errorf("expected slug=new-page, got %s", created.Slug)
	}

	pages, _ := wiki.ListPages(fs, root)
	found := false
	for _, p := range pages {
		if p.Slug == "new-page" {
			found = true
			break
		}
	}
	if !found {
		t.Error("new-page not found in index after create")
	}
}

func TestCreatePageAlreadyExists(t *testing.T) {
	fs, root := setupTestWiki(t)

	page := &wiki.Page{
		Slug: "test-page",
		Frontmatter: map[string]interface{}{
			"title": "重复",
		},
		Body: "重复内容",
	}

	err := wiki.CreatePage(fs, root, page)
	if err == nil {
		t.Fatal("expected error for duplicate page, got nil")
	}
}

func TestUpdatePage(t *testing.T) {
	fs, root := setupTestWiki(t)

	page := &wiki.Page{
		Slug: "test-page",
		Frontmatter: map[string]interface{}{
			"title":       "更新后的标题",
			"tags":        []string{"updated"},
			"scope_level": "repo",
			"scope_code":  "test-repo",
			"updated":     "2026-06-02",
		},
		Body: "# 更新后的内容",
	}

	err := wiki.UpdatePage(fs, root, page)
	if err != nil {
		t.Fatalf("UpdatePage failed: %v", err)
	}

	updated, err := wiki.GetPage(fs, root, "test-page")
	if err != nil {
		t.Fatalf("GetPage after update failed: %v", err)
	}
	if updated.Frontmatter["title"] != "更新后的标题" {
		t.Errorf("expected title=更新后的标题, got %v", updated.Frontmatter["title"])
	}
	if updated.Body != "# 更新后的内容" {
		t.Errorf("expected body=# 更新后的内容, got %s", updated.Body)
	}
}

func TestUpdatePageNotFound(t *testing.T) {
	fs, root := setupTestWiki(t)

	page := &wiki.Page{
		Slug: "nonexistent",
		Body: "content",
	}

	err := wiki.UpdatePage(fs, root, page)
	if err == nil {
		t.Fatal("expected error for nonexistent page, got nil")
	}
}

func TestDeletePage(t *testing.T) {
	fs, root := setupTestWiki(t)

	err := wiki.DeletePage(fs, root, "test-page")
	if err != nil {
		t.Fatalf("DeletePage failed: %v", err)
	}

	_, err = wiki.GetPage(fs, root, "test-page")
	if err == nil {
		t.Fatal("expected error after delete, got nil")
	}

	pages, _ := wiki.ListPages(fs, root)
	for _, p := range pages {
		if p.Slug == "test-page" {
			t.Error("test-page should not be in index after delete")
		}
	}
}

func TestDeletePageNotFound(t *testing.T) {
	fs, root := setupTestWiki(t)

	err := wiki.DeletePage(fs, root, "nonexistent")
	if err == nil {
		t.Fatal("expected error for nonexistent page, got nil")
	}
}
