package cli

import (
	"fmt"
	"io"

	"github.com/bytedance/openwiki/internal/config"
	"github.com/bytedance/openwiki/internal/output"
)

func runConfig(stdout, stderr io.Writer, opts *GlobalOptions, args []string) error {
	if len(args) == 0 {
		return fmt.Errorf("config 需要子命令: show, get, set, validate, path")
	}

	subcommand := args[0]
	subArgs := args[1:]

	switch subcommand {
	case "show":
		return runConfigShow(stdout, stderr, opts, subArgs)
	case "get":
		return runConfigGet(stdout, stderr, opts, subArgs)
	case "set":
		return runConfigSet(stdout, stderr, opts, subArgs)
	case "validate":
		return runConfigValidate(stdout, stderr, opts, subArgs)
	case "path":
		return runConfigPath(stdout, stderr, opts, subArgs)
	default:
		return fmt.Errorf("未知 config 子命令: %s", subcommand)
	}
}

func runConfigShow(stdout, stderr io.Writer, opts *GlobalOptions, args []string) error {
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

	if opts.JSON {
		return output.JSON(stdout, true, cfg, nil)
	}

	fmt.Fprintf(stdout, "wiki_root = %s\n", cfg.WikiRoot)
	fmt.Fprintf(stdout, "wiki.primary_language = %s\n", cfg.Wiki.PrimaryLanguage)
	fmt.Fprintf(stdout, "wiki.secondary_language = %s\n", cfg.Wiki.SecondaryLanguage)
	if cfg.Remote.SyncPath != "" {
		fmt.Fprintf(stdout, "remote.sync_path = %s\n", cfg.Remote.SyncPath)
	}
	fmt.Fprintf(stdout, "remote.auto_sync = %v\n", cfg.Remote.AutoSync)
	return nil
}

func runConfigGet(stdout, stderr io.Writer, opts *GlobalOptions, args []string) error {
	if len(args) == 0 {
		return fmt.Errorf("config get 需要指定键名")
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

	key := args[0]
	val, err := getConfigValue(cfg, key)
	if err != nil {
		if opts.JSON {
			return output.JSON(stdout, false, nil, &output.ErrorInfo{
				Code:    "CONFIG_INVALID_FIELD",
				Message: err.Error(),
			})
		}
		return err
	}

	if opts.JSON {
		return output.JSON(stdout, true, map[string]string{"key": key, "value": val}, nil)
	}

	fmt.Fprintf(stdout, "%s\n", val)
	return nil
}

func runConfigSet(stdout, stderr io.Writer, opts *GlobalOptions, args []string) error {
	if len(args) < 2 {
		return fmt.Errorf("config set 需要指定键名和值")
	}

	cfg, result, err := discoverConfig(opts)
	if err != nil {
		if opts.JSON {
			return output.JSON(stdout, false, nil, &output.ErrorInfo{
				Code:    "CONFIG_NOT_FOUND",
				Message: err.Error(),
			})
		}
		return err
	}

	key := args[0]
	value := args[1]

	oldVal, newVal, err := config.Set(result.Path, key, value)
	if err != nil {
		if opts.JSON {
			return output.JSON(stdout, false, nil, &output.ErrorInfo{
				Code:    "CONFIG_INVALID_FIELD",
				Message: err.Error(),
			})
		}
		return err
	}

	if opts.JSON {
		return output.JSON(stdout, true, map[string]string{
			"key":       key,
			"old_value": oldVal,
			"new_value": newVal,
		}, nil)
	}

	fmt.Fprintf(stdout, "%s: %s -> %s\n", key, oldVal, newVal)
	_ = cfg
	return nil
}

func runConfigValidate(stdout, stderr io.Writer, opts *GlobalOptions, args []string) error {
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

	if err := config.Validate(cfg); err != nil {
		if opts.JSON {
			return output.JSON(stdout, false, nil, &output.ErrorInfo{
				Code:    "CONFIG_INVALID_FIELD",
				Message: err.Error(),
			})
		}
		return err
	}

	if opts.JSON {
		return output.JSON(stdout, true, map[string]string{"status": "valid"}, nil)
	}

	fmt.Fprintln(stdout, "配置有效")
	return nil
}

func runConfigPath(stdout, stderr io.Writer, opts *GlobalOptions, args []string) error {
	_, result, err := discoverConfig(opts)
	if err != nil {
		if opts.JSON {
			return output.JSON(stdout, false, nil, &output.ErrorInfo{
				Code:    "CONFIG_NOT_FOUND",
				Message: err.Error(),
			})
		}
		return err
	}

	if opts.JSON {
		return output.JSON(stdout, true, result, nil)
	}

	fmt.Fprintf(stdout, "配置路径: %s (来源: %s)\n", result.Path, result.Source)
	return nil
}

func getConfigValue(cfg *config.Config, key string) (string, error) {
	switch key {
	case "wiki_root":
		return cfg.WikiRoot, nil
	case "wiki.primary_language":
		return cfg.Wiki.PrimaryLanguage, nil
	case "wiki.secondary_language":
		return cfg.Wiki.SecondaryLanguage, nil
	case "remote.sync_path":
		return cfg.Remote.SyncPath, nil
	case "remote.auto_sync":
		if cfg.Remote.AutoSync {
			return "true", nil
		}
		return "false", nil
	default:
		return "", fmt.Errorf("未知配置项: %s", key)
	}
}
