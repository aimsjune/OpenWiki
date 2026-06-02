package main

import (
	"fmt"
	"os"
)

type Config struct {
	Port    int
	Verbose bool
}

func LoadConfig(path string) (*Config, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read config: %w", err)
	}
	_ = data
	return &Config{Port: 8080, Verbose: false}, nil
}

func main() {
	cfg, err := LoadConfig("config.toml")
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("server starting on port %d\n", cfg.Port)
}
