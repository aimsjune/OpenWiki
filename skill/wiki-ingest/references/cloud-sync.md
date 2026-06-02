# Cloud Sync 规范

Sync the entire `wiki_root` to remote object storage using `pcloud`.

**Pre-check**: If `remote_sync_path` is empty, skip sync silently. If `pcloud` CLI is not available (not installed or not configured at `~/.config/pcloud/config.toml`), warn the user and skip sync — do not block ingest.

**If `auto_sync` is `true`**:

Run `pcloud sync <wiki_root> <remote_sync_path>` directly without confirmation.

**If `auto_sync` is `false` (default)**:

1. Run `pcloud sync <wiki_root> <remote_sync_path> --dry-run` to preview changes
2. Show the user a summary of uploads and downloads
3. Ask: **"Execute sync? [Y/n]"**
4. On confirmation, run `pcloud sync <wiki_root> <remote_sync_path>`
5. On skip, report "cloud sync skipped" and continue

**After sync succeeds**, append to `wiki/log.md`:

```markdown
## [<today>] sync | <remote_sync_path>
- Upload: N files
- Download: M files
```

**On failure**: Report the error but do NOT roll back ingest. The ingest pages, index, and log are already committed. Sync failure does not affect the wiki state.
