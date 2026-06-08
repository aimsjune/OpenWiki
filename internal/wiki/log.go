package wiki

import (
	"fmt"
	"path/filepath"
	"strings"
	"time"
)

type LogEntry struct {
	Time    string `json:"time"`
	Action  string `json:"action"`
	Details string `json:"details"`
}

func ShowLog(fs FS, root string, limit int) ([]LogEntry, error) {
	logPath := filepath.Join(root, "wiki", "log.md")
	data, err := fs.ReadFile(logPath)
	if err != nil {
		return nil, fmt.Errorf("读取 log.md 失败: %w", err)
	}

	entries := parseLogTable(string(data))

	if limit > 0 && limit < len(entries) {
		entries = entries[len(entries)-limit:]
	}

	return entries, nil
}

func parseLogTable(content string) []LogEntry {
	var entries []LogEntry
	lines := strings.Split(content, "\n")
	inTable := false
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if strings.HasPrefix(line, "| 时间 |") {
			inTable = true
			continue
		}
		if strings.HasPrefix(line, "|---") {
			continue
		}
		if !inTable {
			continue
		}
		if line == "" || !strings.HasPrefix(line, "|") {
			continue
		}

		cols := strings.Split(line, "|")
		if len(cols) < 4 {
			continue
		}

		timestamp := strings.TrimSpace(cols[1])
		action := strings.TrimSpace(cols[2])
		details := strings.TrimSpace(cols[3])

		if timestamp == "" || timestamp == "时间" {
			continue
		}

		entries = append(entries, LogEntry{
			Time:    timestamp,
			Action:  action,
			Details: details,
		})
	}
	return entries
}

func AppendLog(fs FS, root, action, details string) error {
	logPath := filepath.Join(root, "wiki", "log.md")
	return withFileLock(fs, logPath, func() error {
		data, err := fs.ReadFile(logPath)
		if err != nil {
			return fmt.Errorf("读取 log.md 失败: %w", err)
		}

		timestamp := time.Now().Format("2006-01-02 15:04:05")
		newLine := fmt.Sprintf("| %s | %s | %s |", timestamp, escapeLogCell(action), escapeLogCell(details))

		content := strings.TrimRight(string(data), "\n")
		content += "\n" + newLine + "\n"

		return fs.WriteFile(logPath, []byte(content), 0644)
	})
}

func escapeLogCell(value string) string {
	value = strings.ReplaceAll(value, "\r", " ")
	value = strings.ReplaceAll(value, "\n", " ")
	return strings.ReplaceAll(value, "|", "&#124;")
}
