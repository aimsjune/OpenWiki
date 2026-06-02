package main

import (
	"fmt"
	"os"

	"github.com/bytedance/openwiki/internal/cli"
)

var (
	Version   = "dev"
	BuildTime = "unknown"
)

func main() {
	if err := cli.Run(os.Args[1:], Version, BuildTime); err != nil {
		fmt.Fprintf(os.Stderr, "错误: %v\n", err)
		os.Exit(1)
	}
}
