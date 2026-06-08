package cli

import (
	"flag"
	"fmt"
	"io"
	"strconv"
	"strings"

	"github.com/bytedance/openwiki/internal/output"
	"github.com/bytedance/openwiki/internal/wiki"
)

func runLog(stdout, stderr io.Writer, opts *GlobalOptions, args []string) error {
	if len(args) == 0 {
		return fmt.Errorf("log 需要子命令: show, append")
	}

	subcommand := args[0]
	subArgs := args[1:]

	switch subcommand {
	case "show":
		return runLogShow(stdout, stderr, opts, subArgs)
	case "append":
		return runLogAppend(stdout, stderr, opts, subArgs)
	default:
		return fmt.Errorf("未知 log 子命令: %s", subcommand)
	}
}

func runLogShow(stdout, stderr io.Writer, opts *GlobalOptions, args []string) error {
	showFlags := flag.NewFlagSet("log show", flag.ContinueOnError)
	showFlags.SetOutput(stderr)

	limitStr := showFlags.String("limit", "0", "限制返回数量")

	if err := showFlags.Parse(args); err != nil {
		return err
	}

	limit, err := strconv.Atoi(*limitStr)
	if err != nil {
		limit = 0
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
	entries, err := wiki.ShowLog(fs, cfg.WikiRoot, limit)
	if err != nil {
		if opts.JSON {
			return output.JSON(stdout, false, nil, &output.ErrorInfo{
				Code:    "IO_ERROR",
				Message: err.Error(),
			})
		}
		return err
	}

	if entries == nil {
		entries = []wiki.LogEntry{}
	}

	if opts.JSON {
		return output.JSON(stdout, true, map[string]interface{}{"entries": entries}, nil)
	}

	for _, e := range entries {
		fmt.Fprintf(stdout, "%s | %s | %s\n", e.Time, e.Action, e.Details)
	}
	return nil
}

func runLogAppend(stdout, stderr io.Writer, opts *GlobalOptions, args []string) error {
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

	details := strings.Join(args, " ")
	if details == "" {
		return fmt.Errorf("log append 需要指定日志内容")
	}

	action := "manual"
	if parts := strings.SplitN(details, "|", 2); len(parts) == 2 && strings.TrimSpace(parts[0]) != "" {
		action = strings.TrimSpace(parts[0])
		details = strings.TrimSpace(parts[1])
	}

	fs := wiki.NewOsFS()
	if err := wiki.AppendLog(fs, cfg.WikiRoot, action, details); err != nil {
		if opts.JSON {
			return output.JSON(stdout, false, nil, &output.ErrorInfo{
				Code:    "IO_ERROR",
				Message: err.Error(),
			})
		}
		return err
	}

	if opts.JSON {
		return output.JSON(stdout, true, map[string]string{"status": "appended"}, nil)
	}

	fmt.Fprintf(stdout, "日志已追加\n")
	return nil
}
