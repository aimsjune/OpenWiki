package config_test

import (
	"testing"

	"github.com/bytedance/openwiki/internal/config"
)

func TestValidateValidConfig(t *testing.T) {
	dir := t.TempDir()
	cfg := &config.Config{
		WikiRoot: dir,
		Wiki: config.WikiConfig{
			PrimaryLanguage:   "zh",
			SecondaryLanguage: "en",
		},
	}

	err := config.Validate(cfg)
	if err != nil {
		t.Errorf("expected no error for valid config, got: %v", err)
	}
}

func TestValidateMissingWikiRoot(t *testing.T) {
	cfg := &config.Config{
		WikiRoot: "",
		Wiki: config.WikiConfig{
			PrimaryLanguage:   "zh",
			SecondaryLanguage: "en",
		},
	}

	err := config.Validate(cfg)
	if err == nil {
		t.Fatal("expected error for missing wiki_root, got nil")
	}
}

func TestValidateInvalidPrimaryLanguage(t *testing.T) {
	dir := t.TempDir()
	cfg := &config.Config{
		WikiRoot: dir,
		Wiki: config.WikiConfig{
			PrimaryLanguage:   "fr",
			SecondaryLanguage: "en",
		},
	}

	err := config.Validate(cfg)
	if err == nil {
		t.Fatal("expected error for invalid primary_language, got nil")
	}
}

func TestValidateInvalidSecondaryLanguage(t *testing.T) {
	dir := t.TempDir()
	cfg := &config.Config{
		WikiRoot: dir,
		Wiki: config.WikiConfig{
			PrimaryLanguage:   "zh",
			SecondaryLanguage: "de",
		},
	}

	err := config.Validate(cfg)
	if err == nil {
		t.Fatal("expected error for invalid secondary_language, got nil")
	}
}
