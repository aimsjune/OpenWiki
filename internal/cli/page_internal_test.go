package cli

import (
	"reflect"
	"testing"
)

func TestExtractSubcommandFlags(t *testing.T) {
	tests := []struct {
		name           string
		args           []string
		flagNames      []string
		wantFlags      map[string]string
		wantPositional []string
	}{
		{
			name:           "flag 在 slug 之后",
			args:           []string{"test-slug", "--file", "/tmp/a.md"},
			flagNames:      []string{"file"},
			wantFlags:      map[string]string{"file": "/tmp/a.md"},
			wantPositional: []string{"test-slug"},
		},
		{
			name:           "flag 在 slug 之前",
			args:           []string{"--file", "/tmp/a.md", "test-slug"},
			flagNames:      []string{"file"},
			wantFlags:      map[string]string{"file": "/tmp/a.md"},
			wantPositional: []string{"test-slug"},
		},
		{
			name:           "无 flag 只有 slug",
			args:           []string{"test-slug"},
			flagNames:      []string{"file"},
			wantFlags:      map[string]string{},
			wantPositional: []string{"test-slug"},
		},
		{
			name:           "flag 无值",
			args:           []string{"--file"},
			flagNames:      []string{"file"},
			wantFlags:      map[string]string{},
			wantPositional: nil,
		},
		{
			name:           "flag 无值但后面有 slug",
			args:           []string{"--file", "test-slug"},
			flagNames:      []string{"file"},
			wantFlags:      map[string]string{"file": "test-slug"},
			wantPositional: nil,
		},
		{
			name:           "重复 flag 使用最后一个值",
			args:           []string{"--file", "/tmp/a.md", "--file", "/tmp/b.md", "test-slug"},
			flagNames:      []string{"file"},
			wantFlags:      map[string]string{"file": "/tmp/b.md"},
			wantPositional: []string{"test-slug"},
		},
		{
			name:           "短 flag 形式 -file",
			args:           []string{"test-slug", "-file", "/tmp/a.md"},
			flagNames:      []string{"file"},
			wantFlags:      map[string]string{"file": "/tmp/a.md"},
			wantPositional: []string{"test-slug"},
		},
		{
			name:           "多个 flag 名",
			args:           []string{"test-slug", "--file", "/tmp/a.md", "--title", "测试"},
			flagNames:      []string{"file", "title"},
			wantFlags:      map[string]string{"file": "/tmp/a.md", "title": "测试"},
			wantPositional: []string{"test-slug"},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotFlags, gotPositional := extractSubcommandFlags(tt.args, tt.flagNames...)

			if !reflect.DeepEqual(gotFlags, tt.wantFlags) {
				t.Errorf("flags = %v, want %v", gotFlags, tt.wantFlags)
			}
			if !reflect.DeepEqual(gotPositional, tt.wantPositional) {
				t.Errorf("positional = %v, want %v", gotPositional, tt.wantPositional)
			}
		})
	}
}
