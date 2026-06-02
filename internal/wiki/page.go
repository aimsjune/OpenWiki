package wiki

import (
	"fmt"
	"path/filepath"
	"regexp"
	"strings"

	"gopkg.in/yaml.v3"
)

type PageMeta struct {
	Slug       string   `json:"slug"`
	Title      string   `json:"title"`
	Tags       []string `json:"tags"`
	ScopeLevel string   `json:"scope_level"`
	ScopeCode  string   `json:"scope_code"`
	Updated    string   `json:"updated"`
}

type Page struct {
	Slug            string                 `json:"slug"`
	Path            string                 `json:"path"`
	Frontmatter     map[string]interface{} `json:"frontmatter"`
	Body            string                 `json:"body"`
	CrossReferences []string               `json:"cross_references"`
}

func ListPages(fs FS, root string) ([]PageMeta, error) {
	indexPath := filepath.Join(root, "wiki", "index.md")
	data, err := fs.ReadFile(indexPath)
	if err != nil {
		return nil, fmt.Errorf("读取 index.md 失败: %w", err)
	}

	return parseIndexTable(string(data)), nil
}

func parseIndexTable(content string) []PageMeta {
	var pages []PageMeta
	lines := strings.Split(content, "\n")
	inTable := false
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if strings.HasPrefix(line, "| Slug |") {
			inTable = true
			continue
		}
		if strings.HasPrefix(line, "|---") {
			continue
		}
		if !inTable {
			continue
		}
		if line == "" || !strings.HasPrefix(line, "|") {
			inTable = false
			continue
		}

		cols := strings.Split(line, "|")
		if len(cols) < 6 {
			continue
		}

		slug := strings.TrimSpace(cols[1])
		if slug == "" || slug == "Slug" {
			continue
		}

		title := strings.TrimSpace(cols[2])
		tagsStr := strings.TrimSpace(cols[3])
		scopeStr := strings.TrimSpace(cols[4])
		updated := strings.TrimSpace(cols[5])

		var tags []string
		for _, t := range strings.Split(tagsStr, ",") {
			t = strings.TrimSpace(t)
			if t != "" {
				tags = append(tags, t)
			}
		}

		scopeParts := strings.SplitN(scopeStr, "/", 2)
		scopeLevel := ""
		scopeCode := ""
		if len(scopeParts) >= 1 {
			scopeLevel = strings.TrimSpace(scopeParts[0])
		}
		if len(scopeParts) >= 2 {
			scopeCode = strings.TrimSpace(scopeParts[1])
		}

		pages = append(pages, PageMeta{
			Slug:       slug,
			Title:      title,
			Tags:       tags,
			ScopeLevel: scopeLevel,
			ScopeCode:  scopeCode,
			Updated:    updated,
		})
	}
	return pages
}

func GetPage(fs FS, root, slug string) (*Page, error) {
	pages, err := GetPages(fs, root, []string{slug})
	if err != nil {
		return nil, err
	}
	if len(pages) == 0 {
		return nil, fmt.Errorf("页面不存在: %s", slug)
	}
	return pages[0], nil
}

func GetPages(fs FS, root string, slugs []string) ([]*Page, error) {
	var pages []*Page
	for _, slug := range slugs {
		pagePath := filepath.Join(root, "wiki", "pages", slug+".md")
		data, err := fs.ReadFile(pagePath)
		if err != nil {
			return nil, fmt.Errorf("读取页面失败 %s: %w", slug, err)
		}

		page, err := parsePage(slug, pagePath, string(data))
		if err != nil {
			return nil, fmt.Errorf("解析页面失败 %s: %w", slug, err)
		}
		pages = append(pages, page)
	}
	return pages, nil
}

func parsePage(slug, path, content string) (*Page, error) {
	page := &Page{
		Slug: slug,
		Path: path,
	}

	parts := strings.SplitN(content, "---", 3)
	if len(parts) >= 3 {
		fmData := strings.TrimSpace(parts[1])
		var fm map[string]interface{}
		if err := yaml.Unmarshal([]byte(fmData), &fm); err == nil {
			page.Frontmatter = fm
		}
		page.Body = strings.TrimSpace(parts[2])
	} else {
		page.Body = strings.TrimSpace(content)
	}

	re := regexp.MustCompile(`\[\[([a-zA-Z0-9_-]+)\]\]`)
	matches := re.FindAllStringSubmatch(page.Body, -1)
	for _, m := range matches {
		page.CrossReferences = append(page.CrossReferences, m[1])
	}

	return page, nil
}

func ParsePageContent(slug, content string) (*Page, error) {
	return parsePage(slug, "", content)
}

func CreatePage(fs FS, root string, page *Page) error {
	pagePath := filepath.Join(root, "wiki", "pages", page.Slug+".md")
	if _, err := fs.Stat(pagePath); err == nil {
		return fmt.Errorf("页面已存在: %s", page.Slug)
	}

	content := buildPageContent(page)
	if err := fs.WriteFile(pagePath, []byte(content), 0644); err != nil {
		return fmt.Errorf("写入页面失败: %w", err)
	}

	if err := addToIndex(fs, root, page); err != nil {
		return fmt.Errorf("更新 index.md 失败: %w", err)
	}

	return nil
}

func buildPageContent(page *Page) string {
	var sb strings.Builder

	if page.Frontmatter != nil && len(page.Frontmatter) > 0 {
		fmData, err := yaml.Marshal(page.Frontmatter)
		if err == nil {
			sb.WriteString("---\n")
			sb.Write(fmData)
			sb.WriteString("---\n\n")
		}
	}

	sb.WriteString(page.Body)
	sb.WriteString("\n")
	return sb.String()
}

func addToIndex(fs FS, root string, page *Page) error {
	indexPath := filepath.Join(root, "wiki", "index.md")
	data, err := fs.ReadFile(indexPath)
	if err != nil {
		return err
	}

	content := string(data)

	title := ""
	tags := ""
	scopeStr := ""
	updated := ""
	if page.Frontmatter != nil {
		if t, ok := page.Frontmatter["title"].(string); ok {
			title = t
		}
		if t, ok := page.Frontmatter["tags"].([]interface{}); ok {
			var tagStrs []string
			for _, tag := range t {
				if s, ok := tag.(string); ok {
					tagStrs = append(tagStrs, s)
				}
			}
			tags = strings.Join(tagStrs, ", ")
		}
		if sl, ok := page.Frontmatter["scope_level"].(string); ok {
			scopeStr = sl
		}
		if sc, ok := page.Frontmatter["scope_code"].(string); ok {
			if scopeStr != "" {
				scopeStr += "/"
			}
			scopeStr += sc
		}
		if u, ok := page.Frontmatter["updated"].(string); ok {
			updated = u
		}
	}

	newLine := fmt.Sprintf("| %s | %s | %s | %s | %s |", page.Slug, title, tags, scopeStr, updated)

	lines := strings.Split(content, "\n")
	var result []string
	inserted := false
	for i, line := range lines {
		result = append(result, line)
		if !inserted && strings.HasPrefix(strings.TrimSpace(line), "| Slug |") {
			if i+2 < len(lines) && strings.HasPrefix(strings.TrimSpace(lines[i+1]), "|---") {
				result = append(result, newLine)
				inserted = true
			}
		}
	}

	if !inserted {
		result = append(result, newLine)
	}

	return fs.WriteFile(indexPath, []byte(strings.Join(result, "\n")), 0644)
}

func UpdatePage(fs FS, root string, page *Page) error {
	pagePath := filepath.Join(root, "wiki", "pages", page.Slug+".md")
	if _, err := fs.Stat(pagePath); err != nil {
		return fmt.Errorf("页面不存在: %s", page.Slug)
	}

	content := buildPageContent(page)
	if err := fs.WriteFile(pagePath, []byte(content), 0644); err != nil {
		return fmt.Errorf("写入页面失败: %w", err)
	}

	if err := updateIndexRow(fs, root, page); err != nil {
		return fmt.Errorf("更新 index.md 失败: %w", err)
	}

	return nil
}

func DeletePage(fs FS, root, slug string) error {
	pagePath := filepath.Join(root, "wiki", "pages", slug+".md")
	if _, err := fs.Stat(pagePath); err != nil {
		return fmt.Errorf("页面不存在: %s", slug)
	}

	if err := fs.Remove(pagePath); err != nil {
		return fmt.Errorf("删除页面文件失败: %w", err)
	}

	if err := removeFromIndex(fs, root, slug); err != nil {
		return fmt.Errorf("更新 index.md 失败: %w", err)
	}

	return nil
}

func updateIndexRow(fs FS, root string, page *Page) error {
	indexPath := filepath.Join(root, "wiki", "index.md")
	data, err := fs.ReadFile(indexPath)
	if err != nil {
		return err
	}

	lines := strings.Split(string(data), "\n")
	var result []string
	for _, line := range lines {
		trimmed := strings.TrimSpace(line)
		if strings.HasPrefix(trimmed, "| "+page.Slug+" |") {
			title := ""
			tags := ""
			scopeStr := ""
			updated := ""
			if page.Frontmatter != nil {
				if t, ok := page.Frontmatter["title"].(string); ok {
					title = t
				}
				if t, ok := page.Frontmatter["tags"].([]interface{}); ok {
					var tagStrs []string
					for _, tag := range t {
						if s, ok := tag.(string); ok {
							tagStrs = append(tagStrs, s)
						}
					}
					tags = strings.Join(tagStrs, ", ")
				}
				if sl, ok := page.Frontmatter["scope_level"].(string); ok {
					scopeStr = sl
				}
				if sc, ok := page.Frontmatter["scope_code"].(string); ok {
					if scopeStr != "" {
						scopeStr += "/"
					}
					scopeStr += sc
				}
				if u, ok := page.Frontmatter["updated"].(string); ok {
					updated = u
				}
			}
			result = append(result, fmt.Sprintf("| %s | %s | %s | %s | %s |", page.Slug, title, tags, scopeStr, updated))
		} else {
			result = append(result, line)
		}
	}

	return fs.WriteFile(indexPath, []byte(strings.Join(result, "\n")), 0644)
}

func removeFromIndex(fs FS, root, slug string) error {
	indexPath := filepath.Join(root, "wiki", "index.md")
	data, err := fs.ReadFile(indexPath)
	if err != nil {
		return err
	}

	lines := strings.Split(string(data), "\n")
	var result []string
	for _, line := range lines {
		trimmed := strings.TrimSpace(line)
		if strings.HasPrefix(trimmed, "| "+slug+" |") {
			continue
		}
		result = append(result, line)
	}

	return fs.WriteFile(indexPath, []byte(strings.Join(result, "\n")), 0644)
}
