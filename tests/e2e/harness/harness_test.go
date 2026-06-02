package harness_test

import (
	"testing"

	"github.com/bytedance/openwiki/tests/e2e/harness"
)

func TestHarnessBuildBinary(t *testing.T) {
	h := harness.New(t)

	result, err := h.Run("--version")
	if err != nil {
		t.Fatalf("run binary: %v", err)
	}

	if result.Stdout == "" {
		t.Error("expected version output, got empty")
	}
}

func TestHarnessRunCommand(t *testing.T) {
	h := harness.New(t)

	result, err := h.Run("--help")
	if err != nil {
		t.Fatalf("run binary: %v", err)
	}

	if result.Stdout == "" {
		t.Error("expected help output, got empty")
	}
}
