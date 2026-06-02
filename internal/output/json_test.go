package output_test

import (
	"bytes"
	"encoding/json"
	"strings"
	"testing"
	"time"

	"github.com/bytedance/openwiki/internal/output"
)

func TestJSONSuccessResponse(t *testing.T) {
	var buf bytes.Buffer
	data := map[string]interface{}{"key": "value"}

	err := output.JSON(&buf, true, data, nil)
	if err != nil {
		t.Fatalf("JSON failed: %v", err)
	}

	var resp output.Response
	if err := json.Unmarshal(buf.Bytes(), &resp); err != nil {
		t.Fatalf("failed to unmarshal response: %v", err)
	}

	if !resp.Success {
		t.Error("expected success=true")
	}
	if resp.Data == nil {
		t.Error("expected data to be non-nil")
	}
	if resp.Timestamp == "" {
		t.Error("expected timestamp to be non-empty")
	}
}

func TestJSONErrorResponse(t *testing.T) {
	var buf bytes.Buffer
	errInfo := &output.ErrorInfo{
		Code:    "TEST_ERROR",
		Message: "测试错误",
		Details: map[string]interface{}{"field": "test"},
	}

	err := output.JSON(&buf, false, nil, errInfo)
	if err != nil {
		t.Fatalf("JSON failed: %v", err)
	}

	var resp output.Response
	if err := json.Unmarshal(buf.Bytes(), &resp); err != nil {
		t.Fatalf("failed to unmarshal response: %v", err)
	}

	if resp.Success {
		t.Error("expected success=false")
	}
	if resp.Error == nil {
		t.Fatal("expected error to be non-nil")
	}
	if resp.Error.Code != "TEST_ERROR" {
		t.Errorf("expected code=TEST_ERROR, got %s", resp.Error.Code)
	}
}

func TestJSONTimestampFormat(t *testing.T) {
	var buf bytes.Buffer

	output.JSON(&buf, true, nil, nil)

	var resp output.Response
	json.Unmarshal(buf.Bytes(), &resp)

	_, err := time.Parse(time.RFC3339, resp.Timestamp)
	if err != nil {
		t.Errorf("timestamp not in RFC3339 format: %s", resp.Timestamp)
	}
}

func TestTextOutput(t *testing.T) {
	var buf bytes.Buffer

	output.Text(&buf, "状态: %s", "正常")

	result := buf.String()
	if !strings.Contains(result, "状态: 正常") {
		t.Errorf("expected '状态: 正常', got '%s'", result)
	}
}
