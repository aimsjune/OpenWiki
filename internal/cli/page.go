package cli

import (
	"fmt"
	"io"

	"github.com/bytedance/openwiki/internal/output"
	"github.com/bytedance/openwiki/internal/wiki"
)

func runPage(stdout, stderr io.Writer, opts *GlobalOptions, args []string) error {
	if len(args) == 0 {
		return fmt.Errorf("page 需要子命令: list, get, create, update, delete")
	}

	subcommand := args[0]
	subArgs := args[1:]

	switch subcommand {
	case "list":
		return runPageList(stdout, stderr, opts, subArgs)
	case "get":
		return runPageGet(stdout, stderr, opts, subArgs)
	case "create":
		return runPageCreate(stdout, stderr, opts, subArgs)
	case "update":
		return runPageUpdate(stdout, stderr, opts, subArgs)
	case "delete":
		return runPageDelete(stdout, stderr, opts, subArgs)
	default:
		return fmt.Errorf("未知 page 子命令: %s", subcommand)
	}
}

func runPageList(stdout, stderr io.Writer, opts *GlobalOptions, args []string) error {
	cfg, _, err := discoverConfig(opts)
	if err != nil {
		if opts.JSON {
			return output.JSON(stdout, false, nil, &output.ErrorInfo{
				Code:    "CONFIG_NOT_FOUND",
				Message: err.Error(),
			})
		}
		return err
	}

	fs := wiki.NewOsFS()
	pages, err := wiki.ListPages(fs, cfg.WikiRoot)
	if err != nil {
		if opts.JSON {
			return output.JSON(stdout, false, nil, &output.ErrorInfo{
				Code:    "IO_ERROR",
				Message: err.Error(),
			})
		}
		return err
	}

	if opts.JSON {
		return output.JSON(stdout, true, map[string]interface{}{"pages": pages}, nil)
	}

	for _, p := range pages {
		fmt.Fprintf(stdout, "%s | %s | %s/%s | %s\n", p.Slug, p.Title, p.ScopeLevel, p.ScopeCode, p.Updated)
	}
	return nil
}

func runPageGet(stdout, stderr io.Writer, opts *GlobalOptions, args []string) error {
	if len(args) == 0 {
		return fmt.Errorf("page get 需要指定 slug")
	}

	cfg, _, err := discoverConfig(opts)
	if err != nil {
		if opts.JSON {
			return output.JSON(stdout, false, nil, &output.ErrorInfo{
				Code:    "CONFIG_NOT_FOUND",
				Message: err.Error(),
			})
		}
		return err
	}

	fs := wiki.NewOsFS()
	slug := args[0]

	page, err := wiki.GetPage(fs, cfg.WikiRoot, slug)
	if err != nil {
		if opts.JSON {
			return output.JSON(stdout, false, nil, &output.ErrorInfo{
				Code:    "PAGE_NOT_FOUND",
				Message: err.Error(),
			})
		}
		return err
	}

	if opts.JSON {
		return output.JSON(stdout, true, page, nil)
	}

	fmt.Fprintf(stdout, "---\n")
	for k, v := range page.Frontmatter {
		fmt.Fprintf(stdout, "%s: %v\n", k, v)
	}
	fmt.Fprintf(stdout, "---\n\n")
	fmt.Fprintf(stdout, "%s\n", page.Body)
	return nil
}

func extractSubcommandFlags(args []string, flagNames ...string) (flags map[string]string, positional []string) {
	flags = make(map[string]string)
	for i := 0; i < len(args); i++ {
		arg := args[i]
		matched := false
		for _, name := range flagNames {
			if arg == "--"+name || arg == "-"+name {
				if i+1 < len(args) {
					flags[name] = args[i+1]
					i++
				}
				matched = true
				break
			}
		}
		if !matched {
			positional = append(positional, arg)
		}
	}
	return
}

func parsePageType(s string) (wiki.PageType, error) {
	switch s {
	case "", "page":
		return wiki.PageTypePage, nil
	case "entity":
		return wiki.PageTypeEntity, nil
	case "concept":
		return wiki.PageTypeConcept, nil
	default:
		return "", fmt.Errorf("无效的页面类型: %s（支持: page, entity, concept）", s)
	}
}

func runPageCreate(stdout, stderr io.Writer, opts *GlobalOptions, args []string) error {
	flags, positional := extractSubcommandFlags(args, "file", "type")
	filePath := flags["file"]
	typeStr := flags["type"]

	if len(positional) == 0 {
		return fmt.Errorf("page create 需要指定 slug")
	}

	slug := positional[0]

	cfg, _, err := discoverConfig(opts)
	if err != nil {
		if opts.JSON {
			return output.JSON(stdout, false, nil, &output.ErrorInfo{
				Code:    "CONFIG_NOT_FOUND",
				Message: err.Error(),
			})
		}
		return err
	}

	fs := wiki.NewOsFS()

	var content []byte
	if filePath != "" {
		content, err = fs.ReadFile(filePath)
		if err != nil {
			if opts.JSON {
				return output.JSON(stdout, false, nil, &output.ErrorInfo{
					Code:    "IO_ERROR",
					Message: fmt.Sprintf("读取文件失败: %s", filePath),
				})
			}
			return fmt.Errorf("读取文件失败: %s", filePath)
		}
	}

	page, err := wiki.ParsePageContent(slug, string(content))
	if err != nil {
		if opts.JSON {
			return output.JSON(stdout, false, nil, &output.ErrorInfo{
				Code:    "INVALID_ARG",
				Message: err.Error(),
			})
		}
		return err
	}

	pt, err := parsePageType(typeStr)
	if err != nil {
		if opts.JSON {
			return output.JSON(stdout, false, nil, &output.ErrorInfo{
				Code:    "INVALID_ARG",
				Message: err.Error(),
			})
		}
		return err
	}

	if err := wiki.CreatePage(fs, cfg.WikiRoot, page, pt); err != nil {
		code := "INTERNAL"
		if err.Error() == fmt.Sprintf("页面已存在: %s", slug) {
			code = "PAGE_ALREADY_EXISTS"
		}

		if opts.JSON {
			return output.JSON(stdout, false, nil, &output.ErrorInfo{
				Code:    code,
				Message: err.Error(),
			})
		}
		return err
	}

	if opts.JSON {
		return output.JSON(stdout, true, map[string]string{"slug": slug, "status": "created"}, nil)
	}

	fmt.Fprintf(stdout, "页面已创建: %s\n", slug)
	return nil
}

func runPageUpdate(stdout, stderr io.Writer, opts *GlobalOptions, args []string) error {
	flags, positional := extractSubcommandFlags(args, "file", "type")
	filePath := flags["file"]
	typeStr := flags["type"]

	if len(positional) == 0 {
		return fmt.Errorf("page update 需要指定 slug")
	}

	slug := positional[0]

	cfg, _, err := discoverConfig(opts)
	if err != nil {
		if opts.JSON {
			return output.JSON(stdout, false, nil, &output.ErrorInfo{
				Code:    "CONFIG_NOT_FOUND",
				Message: err.Error(),
			})
		}
		return err
	}

	fs := wiki.NewOsFS()

	var content []byte
	if filePath != "" {
		content, err = fs.ReadFile(filePath)
		if err != nil {
			if opts.JSON {
				return output.JSON(stdout, false, nil, &output.ErrorInfo{
					Code:    "IO_ERROR",
					Message: fmt.Sprintf("读取文件失败: %s", filePath),
				})
			}
			return fmt.Errorf("读取文件失败: %s", filePath)
		}
	}

	page, err := wiki.ParsePageContent(slug, string(content))
	if err != nil {
		if opts.JSON {
			return output.JSON(stdout, false, nil, &output.ErrorInfo{
				Code:    "INVALID_ARG",
				Message: err.Error(),
			})
		}
		return err
	}

	if typeStr != "" {
		pt, err := parsePageType(typeStr)
		if err != nil {
			if opts.JSON {
				return output.JSON(stdout, false, nil, &output.ErrorInfo{
					Code:    "INVALID_ARG",
					Message: err.Error(),
				})
			}
			return err
		}
		if err := wiki.UpdatePage(fs, cfg.WikiRoot, page, pt); err != nil {
			code := "INTERNAL"
			if err.Error() == fmt.Sprintf("页面不存在: %s", slug) {
				code = "PAGE_NOT_FOUND"
			}

			if opts.JSON {
				return output.JSON(stdout, false, nil, &output.ErrorInfo{
					Code:    code,
					Message: err.Error(),
				})
			}
			return err
		}
	} else {
		if err := wiki.UpdatePage(fs, cfg.WikiRoot, page); err != nil {
			code := "INTERNAL"
			if err.Error() == fmt.Sprintf("页面不存在: %s", slug) {
				code = "PAGE_NOT_FOUND"
			}

			if opts.JSON {
				return output.JSON(stdout, false, nil, &output.ErrorInfo{
					Code:    code,
					Message: err.Error(),
				})
			}
			return err
		}
	}

	if opts.JSON {
		return output.JSON(stdout, true, map[string]string{"slug": slug, "status": "updated"}, nil)
	}

	fmt.Fprintf(stdout, "页面已更新: %s\n", slug)
	return nil
}

func runPageDelete(stdout, stderr io.Writer, opts *GlobalOptions, args []string) error {
	if len(args) == 0 {
		return fmt.Errorf("page delete 需要指定 slug")
	}

	slug := args[0]

	cfg, _, err := discoverConfig(opts)
	if err != nil {
		if opts.JSON {
			return output.JSON(stdout, false, nil, &output.ErrorInfo{
				Code:    "CONFIG_NOT_FOUND",
				Message: err.Error(),
			})
		}
		return err
	}

	fs := wiki.NewOsFS()

	if err := wiki.DeletePage(fs, cfg.WikiRoot, slug); err != nil {
		code := "INTERNAL"
		if err.Error() == fmt.Sprintf("页面不存在: %s", slug) {
			code = "PAGE_NOT_FOUND"
		}

		if opts.JSON {
			return output.JSON(stdout, false, nil, &output.ErrorInfo{
				Code:    code,
				Message: err.Error(),
			})
		}
		return err
	}

	if opts.JSON {
		return output.JSON(stdout, true, map[string]string{"slug": slug, "status": "deleted"}, nil)
	}

	fmt.Fprintf(stdout, "页面已删除: %s\n", slug)
	return nil
}
