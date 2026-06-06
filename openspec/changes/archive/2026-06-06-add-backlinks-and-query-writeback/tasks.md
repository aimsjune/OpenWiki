# Tasks: add-backlinks-and-query-writeback

## TDD Workflow: RED → GREEN → REFACTOR

**注意：此改动已实现完成，以下任务记录实现过程。**

---

## Behavior 1: ComputeBacklinks 计算反向链接

### Phase 1: RED - Write Failing Test

- [x] **1.1** 编写单元测试 `TestComputeBacklinks`，验证多页面引用场景
- [x] **1.2** 运行测试确认失败（函数未实现）

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** 实现 `ComputeBacklinks(fs, root, targetSlug)` 函数
  - 扫描 `wiki/pages/` 下所有 `.md` 文件
  - 正则匹配 `[[slug]]` 引用
  - 排除自身引用
- [x] **2.2** 运行测试确认通过

### Phase 3: REFACTOR - Improve

- [x] **3.1** 确保 `backlinks` 为 nil 时返回空数组 `[]string{}`
- [x] **3.2** 运行全部测试确认通过

---

## Behavior 2: Page 结构体 + GetPageWithBacklinks

### Phase 1: RED - Write Failing Test

- [x] **1.1** 编写单元测试 `TestGetPageWithBacklinks`，验证 JSON 输出包含 `backlinks`
- [x] **1.2** 运行测试确认失败（字段不存在）

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** `Page` 结构体新增 `Backlinks []string` 字段（`json:"backlinks"`）
- [x] **2.2** 实现 `GetPageWithBacklinks(fs, root, slug)` 函数
  - 调用 `GetPage` 读取页面
  - 调用 `ComputeBacklinks` 计算反向链接
  - 计算失败时降级返回空数组
- [x] **2.3** 运行测试确认通过

### Phase 3: REFACTOR - Improve

- [x] **3.1** 运行全部测试确认无回归

---

## Behavior 3: CLI --backlinks 标志

### Phase 1: RED - Write Failing Test

- [x] **1.1** 编写 e2e 测试 `TestPageGetWithBacklinks`
- [x] **1.2** 运行测试确认失败（CLI 不支持 `--backlinks`）

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** `runPageGet` 通过 `extractSubcommandFlags(args, "backlinks")` 解析标志
- [x] **2.2** 有 `--backlinks` 时调用 `GetPageWithBacklinks`，否则调用 `GetPage`
- [x] **2.3** 非 JSON 模式下，有反向链接时输出 `## 反向链接` 区域
- [x] **2.4** 运行测试确认通过

### Phase 3: REFACTOR - Improve

- [x] **3.1** 运行全部测试确认无回归

---

## Behavior 4: wiki-query SKILL.md 回写机制

### Phase 1: RED - Write Failing Test

- [x] **1.1** 文档审查：确认当前 Step 5 仅有简单的 "Worth saving?" 逻辑
- [x] **1.2** 确认不符合结构化回写要求

### Phase 2: GREEN - Make Test Pass

- [x] **2.1** Step 5 重写为"回写评估与保存"
  - 5.1 回写判断条件（4 个条件表格）
  - 5.2 回写页面格式模板（含 `query_date`、`query_sources`、`external_refs`）
  - 5.3 回写后操作（存入 `wiki/pages/`、更新 index.md、不修改源页面）
  - 5.4 不满足条件时仅追加日志
- [x] **2.2** Step 2 新增 `--backlinks` 用法说明
- [x] **2.3** 文档审查确认所有必需内容存在

### Phase 3: REFACTOR - Improve

- [x] **3.1** 确认文档格式一致，无遗留旧内容

---

## Verification

- [x] 运行完整测试套件：`go test ./...` — 全部通过
- [x] 编译通过：`go build ./...` — 无错误
- [x] 实现匹配 acceptance criteria
- [x] 反向链接计算失败时降级返回空数组（不阻塞页面读取）
- [x] `GetPage` 默认行为不变（向后兼容）

## Test Quality Checklist

- [x] 测试描述行为而非实现
- [x] 测试使用公开接口（`GetPageWithBacklinks`、`ComputeBacklinks`、CLI）
- [x] 测试不依赖内部实现细节
- [x] 使用 `MemFS` 注入文件系统依赖
