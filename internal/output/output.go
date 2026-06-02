package output

import (
	"encoding/json"
	"fmt"
	"io"
	"time"
)

type Response struct {
	Success   bool        `json:"success"`
	Data      interface{} `json:"data,omitempty"`
	Error     *ErrorInfo  `json:"error,omitempty"`
	Timestamp string      `json:"timestamp"`
}

type ErrorInfo struct {
	Code    string                 `json:"code"`
	Message string                 `json:"message"`
	Details map[string]interface{} `json:"details,omitempty"`
}

func (e *ErrorInfo) Error() string {
	return fmt.Sprintf("[%s] %s", e.Code, e.Message)
}

func JSON(w io.Writer, success bool, data interface{}, err error) error {
	resp := Response{
		Success:   success,
		Data:      data,
		Timestamp: time.Now().UTC().Format(time.RFC3339),
	}

	if err != nil {
		if ei, ok := err.(*ErrorInfo); ok {
			resp.Error = ei
		} else {
			resp.Error = &ErrorInfo{
				Code:    "INTERNAL",
				Message: err.Error(),
			}
		}
	}

	encoder := json.NewEncoder(w)
	encoder.SetIndent("", "  ")
	return encoder.Encode(resp)
}

func Text(w io.Writer, format string, args ...interface{}) {
	fmt.Fprintf(w, format+"\n", args...)
}
