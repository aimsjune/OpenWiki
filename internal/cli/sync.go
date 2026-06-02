package cli

import (
	"flag"
	"fmt"
	"io"

	"github.com/bytedance/openwiki/internal/output"
)

type Syncer interface {
	Sync(wikiRoot, syncPath string, dryRun bool) (*SyncResult, error)
}

type SyncResult struct {
	DryRun  bool     `json:"dry_run"`
	Changes []string `json:"changes,omitempty"`
	Status  string   `json:"status"`
}

type defaultSyncer struct{}

func (s *defaultSyncer) Sync(wikiRoot, syncPath string, dryRun bool) (*SyncResult, error) {
	return &SyncResult{
		DryRun: dryRun,
		Status: "stub",
	}, nil
}

var syncer Syncer = &defaultSyncer{}

func runSync(stdout, stderr io.Writer, opts *GlobalOptions, args []string) error {
	syncFlags := flag.NewFlagSet("sync", flag.ContinueOnError)
	syncFlags.SetOutput(stderr)

	dryRun := syncFlags.Bool("dry-run", false, "预览变更")

	if err := syncFlags.Parse(args); err != nil {
		return err
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

	if cfg.Remote.SyncPath == "" {
		if opts.JSON {
			return output.JSON(stdout, false, nil, &output.ErrorInfo{
				Code:    "CONFIG_MISSING_FIELD",
				Message: "未配置 remote.sync_path，无法同步",
			})
		}
		return fmt.Errorf("未配置 remote.sync_path，无法同步")
	}

	result, err := syncer.Sync(cfg.WikiRoot, cfg.Remote.SyncPath, *dryRun)
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
		return output.JSON(stdout, true, result, nil)
	}

	if result.DryRun {
		fmt.Fprintf(stdout, "预览模式:\n")
		for _, c := range result.Changes {
			fmt.Fprintf(stdout, "  %s\n", c)
		}
	} else {
		fmt.Fprintf(stdout, "同步完成: %s\n", result.Status)
	}

	return nil
}

func SetSyncer(s Syncer) {
	syncer = s
}

func ResetSyncer() {
	syncer = &defaultSyncer{}
}
