package wiki

import (
	"fmt"
	"path/filepath"
	"regexp"
	"strings"
	"time"

	"gopkg.in/yaml.v3"
)

// PageType 页面类型
type PageType string

const (
	PageTypePage    PageType = "page"
	PageTypeEntity  PageType = "entity"
	PageTypeConcept PageType = "concept"
)

// pageDirs 每种类型对应的存储目录（相对于 wiki_root）
var pageDirs = map[PageType]string{
	PageTypePage:    "wiki/pages",
	PageTypeEntity:  "entities",
	PageTypeConcept: "concepts",
}

// searchOrder 跨目录搜索的优先级
var searchOrder = []PageType{PageTypePage, PageTypeEntity, PageTypeConcept}

type PageMeta struct {
	Slug       string   `json:"slug"`
	Title      string   `json:"title"`
	Type       string   `json:"type"`
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
	hasTypeColumn := false
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if strings.HasPrefix(line, "| Slug |") {
			inTable = true
			// 检测是否有"类型"列
			hasTypeColumn = strings.Contains(line, "类型")
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
		minCols := 6
		if hasTypeColumn {
			minCols = 7
		}
		if len(cols) < minCols {
			continue
		}

		slug := strings.TrimSpace(cols[1])
		if slug == "" || slug == "Slug" {
			continue
		}

		title := strings.TrimSpace(cols[2])
		pageType := "page"
		tagsCol := 3
		scopeCol := 4
		updatedCol := 5
		if hasTypeColumn {
			pageType = strings.TrimSpace(cols[3])
			tagsCol = 4
			scopeCol = 5
			updatedCol = 6
		}
		tagsStr := strings.TrimSpace(cols[tagsCol])
		scopeStr := strings.TrimSpace(cols[scopeCol])
		updated := strings.TrimSpace(cols[updatedCol])

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
			Type:       pageType,
			Tags:       tags,
			ScopeLevel: scopeLevel,
			ScopeCode:  scopeCode,
			Updated:    updated,
		})
	}
	return pages
}

func GetPage(fs FS, root, slug string) (*Page, error) {
	pagePath, _, err := resolvePagePath(fs, root, slug)
	if err != nil {
		return nil, err
	}

	data, err := fs.ReadFile(pagePath)
	if err != nil {
		return nil, fmt.Errorf("读取页面失败 %s: %w", slug, err)
	}

	page, err := parsePage(slug, pagePath, string(data))
	if err != nil {
		return nil, fmt.Errorf("解析页面失败 %s: %w", slug, err)
	}
	return page, nil
}

func GetPages(fs FS, root string, slugs []string) ([]*Page, error) {
	var pages []*Page
	for _, slug := range slugs {
		page, err := GetPage(fs, root, slug)
		if err != nil {
			return nil, err
		}
		pages = append(pages, page)
	}
	return pages, nil
}

// resolvePagePath 按 searchOrder 查找页面文件，返回路径和类型
func resolvePagePath(fs FS, root, slug string) (string, PageType, error) {
	for _, pt := range searchOrder {
		dir := pageDirs[pt]
		pagePath := filepath.Join(root, dir, slug+".md")
		if _, err := fs.Stat(pagePath); err == nil {
			return pagePath, pt, nil
		}
	}
	return "", "", fmt.Errorf("页面不存在: %s", slug)
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
			if updated, ok := fm["updated"].(time.Time); ok {
				fm["updated"] = updated.Format("2006-01-02")
			}
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

func CreatePage(fs FS, root string, page *Page, pageType ...PageType) error {
	pt := PageTypePage
	if len(pageType) > 0 {
		pt = pageType[0]
	}

	dir := pageDirs[pt]
	pagePath := filepath.Join(root, dir, page.Slug+".md")
	if _, err := fs.Stat(pagePath); err == nil {
		return fmt.Errorf("页面已存在: %s", page.Slug)
	}

	// 确保目录存在
	if err := fs.MkdirAll(filepath.Join(root, dir), 0755); err != nil {
		return fmt.Errorf("创建目录失败: %w", err)
	}

	content := buildPageContent(page)
	if err := fs.WriteFile(pagePath, []byte(content), 0644); err != nil {
		return fmt.Errorf("写入页面失败: %w", err)
	}

	if err := addToIndex(fs, root, page, pt); err != nil {
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

func addToIndex(fs FS, root string, page *Page, pt PageType) error {
	indexPath := filepath.Join(root, "wiki", "index.md")
	return withFileLock(fs, indexPath, func() error {
		data, err := fs.ReadFile(indexPath)
		if err != nil {
			return err
		}

		title, tags, scopeStr, updated := pageIndexFields(page)
		newLine := fmt.Sprintf("| %s | %s | %s | %s | %s | %s |", page.Slug, title, string(pt), tags, scopeStr, updated)
		lines := strings.Split(string(data), "\n")

		// 找到所有分隔线位置，按类型选择正确的插入位置
		var separatorPositions []int
		for i, line := range lines {
			if strings.HasPrefix(strings.TrimSpace(line), "|---") {
				separatorPositions = append(separatorPositions, i)
			}
		}

		// 根据类型选择插入位置：page→第1个, entity→第2个, concept→第3个
		insertAfter := 0
		switch pt {
		case PageTypeEntity:
			if len(separatorPositions) >= 2 {
				insertAfter = separatorPositions[1]
			} else if len(separatorPositions) >= 1 {
				insertAfter = separatorPositions[0]
			}
		case PageTypeConcept:
			if len(separatorPositions) >= 3 {
				insertAfter = separatorPositions[2]
			} else if len(separatorPositions) >= 1 {
				insertAfter = separatorPositions[0]
			}
		default:
			if len(separatorPositions) >= 1 {
				insertAfter = separatorPositions[0]
			}
		}

		var result []string
		inserted := false
		for i, line := range lines {
			result = append(result, line)
			if !inserted && i == insertAfter {
				result = append(result, newLine)
				inserted = true
			}
		}

		if !inserted {
			result = append(result, newLine)
		}

		return fs.WriteFile(indexPath, []byte(strings.Join(result, "\n")), 0644)
	})
}

func UpdatePage(fs FS, root string, page *Page, newType ...PageType) error {
	pagePath, currentType, err := resolvePagePath(fs, root, page.Slug)
	if err != nil {
		return err
	}

	// 确定目标类型和目录
	targetType := currentType
	if len(newType) > 0 {
		targetType = newType[0]
	}

	content := buildPageContent(page)

	if targetType != currentType {
		// 类型变更：删除原文件，写入新目录
		if err := fs.Remove(pagePath); err != nil {
			return fmt.Errorf("删除原页面失败: %w", err)
		}
		newDir := pageDirs[targetType]
		if err := fs.MkdirAll(filepath.Join(root, newDir), 0755); err != nil {
			return fmt.Errorf("创建目录失败: %w", err)
		}
		newPath := filepath.Join(root, newDir, page.Slug+".md")
		if err := fs.WriteFile(newPath, []byte(content), 0644); err != nil {
			return fmt.Errorf("写入页面失败: %w", err)
		}
	} else {
		if err := fs.WriteFile(pagePath, []byte(content), 0644); err != nil {
			return fmt.Errorf("写入页面失败: %w", err)
		}
	}

	if err := updateIndexRow(fs, root, page); err != nil {
		return fmt.Errorf("更新 index.md 失败: %w", err)
	}

	return nil
}

func DeletePage(fs FS, root, slug string) error {
	pagePath, _, err := resolvePagePath(fs, root, slug)
	if err != nil {
		return err
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
	return withFileLock(fs, indexPath, func() error {
		data, err := fs.ReadFile(indexPath)
		if err != nil {
			return err
		}

		lines := strings.Split(string(data), "\n")
		var result []string
		for _, line := range lines {
			trimmed := strings.TrimSpace(line)
			if strings.HasPrefix(trimmed, "| "+page.Slug+" |") {
				title, tags, scopeStr, updated := pageIndexFields(page)
				result = append(result, fmt.Sprintf("| %s | %s | %s | %s | %s | %s |", page.Slug, title, "page", tags, scopeStr, updated))
			} else {
				result = append(result, line)
			}
		}

		return fs.WriteFile(indexPath, []byte(strings.Join(result, "\n")), 0644)
	})
}

func removeFromIndex(fs FS, root, slug string) error {
	indexPath := filepath.Join(root, "wiki", "index.md")
	return withFileLock(fs, indexPath, func() error {
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
	})
}

func pageIndexFields(page *Page) (title, tags, scope, updated string) {
	if page.Frontmatter == nil {
		return
	}

	title, _ = page.Frontmatter["title"].(string)
	switch values := page.Frontmatter["tags"].(type) {
	case []string:
		tags = strings.Join(values, ", ")
	case []interface{}:
		var tagStrings []string
		for _, value := range values {
			if tag, ok := value.(string); ok {
				tagStrings = append(tagStrings, tag)
			}
		}
		tags = strings.Join(tagStrings, ", ")
	}

	scopeLevel, _ := page.Frontmatter["scope_level"].(string)
	scopeCode, _ := page.Frontmatter["scope_code"].(string)
	scope = scopeLevel
	if scope != "" && scopeCode != "" {
		scope += "/"
	}
	scope += scopeCode

	switch value := page.Frontmatter["updated"].(type) {
	case string:
		updated = value
	case time.Time:
		updated = value.Format("2006-01-02")
	}
	return
}
