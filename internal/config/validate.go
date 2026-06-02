package config

import (
	"fmt"
	"os"
	"slices"
)

var allowedLanguages = []string{"zh", "en"}

func Validate(cfg *Config) error {
	if cfg.WikiRoot == "" {
		return &ValidationError{
			Code:    "CONFIG_MISSING_FIELD",
			Message: "缺少必填字段 wiki_root",
			Details: map[string]interface{}{"field": "wiki_root"},
		}
	}

	if _, err := os.Stat(cfg.WikiRoot); os.IsNotExist(err) {
		return &ValidationError{
			Code:    "CONFIG_INVALID_PATH",
			Message: fmt.Sprintf("wiki_root 路径不存在: %s", cfg.WikiRoot),
			Details: map[string]interface{}{"field": "wiki_root", "path": cfg.WikiRoot},
		}
	}

	if !slices.Contains(allowedLanguages, cfg.Wiki.PrimaryLanguage) {
		return &ValidationError{
			Code:    "CONFIG_INVALID_FIELD",
			Message: fmt.Sprintf("primary_language 值无效: '%s'，支持的值: %v", cfg.Wiki.PrimaryLanguage, allowedLanguages),
			Details: map[string]interface{}{
				"field":   "wiki.primary_language",
				"value":   cfg.Wiki.PrimaryLanguage,
				"allowed": allowedLanguages,
			},
		}
	}

	if !slices.Contains(allowedLanguages, cfg.Wiki.SecondaryLanguage) {
		return &ValidationError{
			Code:    "CONFIG_INVALID_FIELD",
			Message: fmt.Sprintf("secondary_language 值无效: '%s'，支持的值: %v", cfg.Wiki.SecondaryLanguage, allowedLanguages),
			Details: map[string]interface{}{
				"field":   "wiki.secondary_language",
				"value":   cfg.Wiki.SecondaryLanguage,
				"allowed": allowedLanguages,
			},
		}
	}

	return nil
}

type ValidationError struct {
	Code    string
	Message string
	Details map[string]interface{}
}

func (e *ValidationError) Error() string {
	return fmt.Sprintf("[%s] %s", e.Code, e.Message)
}
