# LLM Wiki — AI駆動の個人知識ベース

**言語 / Language / 语言：** [中文](README.md) ｜ [English](README.en.md) ｜ 日本語（デフォルト）

---

## これは何ですか？

LLM Wiki は `skill.io` 互換エージェント向けの個人知識ベース用スキャフォールドです。原本素材は `raw/`、構造化知識は `wiki/`、保存された分析や回答は `concepts/` に置かれます。公開スキルは `skill/` で管理され、インスタンス単位の実行時契約は `WIKI.md` で表現されます。

**コアアイデア：**
- `WIKI.md` が canonical runtime contract
- `skill/` が唯一の公開 wiki skill ディレクトリ
- `config-dir` と `wiki-root` は完全に分離可能
- `raw/` は不変のソース、`wiki/` は AI が保守する知識層

---

## 実行モデル

```text
<config-dir>/
└── WIKI.md            # 絶対 wiki_root を記録する実行時契約

<wiki-root>/
├── raw/               # 原本素材
├── wiki/
│   ├── index.md       # 全体インデックス
│   ├── log.md         # 操作ログ
│   └── pages/         # トピックページ
└── concepts/          # 分析・回答・レポート
```

公開スキルは次の場所にあります：

```text
skill/
├── wiki-init/
├── wiki-ingest/
├── wiki-query/
├── wiki-lint/
├── wiki-update/
└── agent-browser/
```

---

## クイックスタート

### 前提条件

- 任意の `skill.io` 互換エージェント/ツール
- （任意）[agent-browser](https://github.com/mediar-ai/agent-browser)：Web補完と検証に使用
  ```bash
  brew install mediar-ai/agent-browser/agent-browser
  ```

### インストール

```bash
git clone https://github.com/crabin/llm-wiki.git my-wiki
cd my-wiki
```

互換エージェントにこのリポジトリを読み込ませ、`skill/` 内の公開 wiki skill を参照できるようにします。

### 使い方

1. `wiki-init` を実行する
2. `config-dir` を選ぶ（例：`~/wiki-config/personal-research`）
3. `wiki-root` を選ぶ（例：`~/data/my-wiki`）
4. `wiki-init` に `<config-dir>/WIKI.md` を生成させ、絶対 `wiki_root` を記録する
5. 素材を `<wiki-root>/raw/` に置き、`wiki-ingest` を実行する
6. `wiki-query`、`wiki-lint`、`wiki-update` で運用する

実行時の探索順序：
- ユーザーが明示した `config-dir` を最優先で使う
- 指定がなければ current working directory から上方向に `WIKI.md` を探索する
- 見つからなければ絶対 `config-dir` の入力を求めるか `wiki-init` を先に実行する

---

## リポジトリ構造

```text
llm-wiki/
├── skill/             # 唯一の公開 wiki skill ディレクトリ
│   ├── wiki-init/
│   ├── wiki-ingest/
│   ├── wiki-query/
│   ├── wiki-lint/
│   ├── wiki-update/
│   └── agent-browser/
├── WIKI.md            # このリポジトリ実体用のランタイム契約
├── raw/
├── wiki/
│   ├── index.md
│   ├── log.md
│   └── pages/
├── concepts/
├── README.md
├── README.en.md
└── README.ja.md
```

---

## Skill Asset Boundary

- 公開 wiki skill の境界ルールは `skill/ASSET-LAYOUT.md` を参照する
- `skill-private asset` は owning `skill/<name>/` ディレクトリ配下に置く
- `runtime` wiki object は `WIKI.md` と `wiki_root` 配下の `raw/`、`wiki/`、`concepts/` のまま維持する
- 推奨される skill-local ディレクトリ名:
  - `templates/`
  - `examples/`
  - `fixtures/`
  - `assets/`
  - `scripts/`

---

## スキル説明

### wiki-init

- 独立した `config-dir` と `wiki-root` を収集する
- 設定ディレクトリに `WIKI.md` を書く
- `wiki-root` 配下に `raw/`、`wiki/index.md`、`wiki/log.md`、`wiki/pages/`、`concepts/` を初期化する

### wiki-ingest

- 新規ソースを読み、先にユーザーと要点を議論する
- `WIKI.md` から実行時パスを解決する
- ページ、逆リンク、インデックス、ログを更新する

### wiki-query

- 常に `wiki/index.md` と関連ページを先に読む
- ローカル情報が不足する場合のみ `agent-browser` を使う
- 価値のある回答は常に `concepts/` への保存を提案する

### wiki-lint

- リンク切れ、孤立ページ、矛盾、古い記述を検出する
- レポートを `concepts/lint-<date>.md` に出力する
- 修正前に diff を表示する

### wiki-update

- 既存ページを更新する
- ページごとに確認する
- 下流影響を確認し、変更を必ず記録する

### agent-browser

- Web取得とファクトチェックを担当する
- 権威あるソースを優先する
- wiki ワークフローが引用できる URL と本文を提供する

---

## 設計原則

- **中立ランタイム**：実行時は `WIKI.md` に依存し、特定エージェント名には依存しない
- **単一の公開能力面**：公開スキルは `skill/` のみで管理する
- **知識の複利**：新しい知識は既存グラフへ接続する
- **追跡可能なソース**：重要な主張はファイルパスか URL に結び付ける

---

## ライセンス

MIT
