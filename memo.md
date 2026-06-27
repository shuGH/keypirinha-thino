# Thino 開発メモ

## 概要

KeypirinhaからObsidian/Thinoスタイルのメモづくりを支援するプラグインです。`Thino:` などのラベルでメモ入力を受け付け、`vault_name` で指定したObsidian VaultのDaily noteへ、`memo_format` に応じた時間付きの一行を追記します。`target_heading` が指定されている場合は、その見出し配下への追記を想定します。

## リファレンス

公式のリファレンスを参考にすること

- Keypirinha：https://keypirinha.com/api.html
- Obsidian CLI：https://obsidian.md/ja/help/cli
- Thino：https://github.com/Quorafind/Obsidian-Thino

## READMEとの整合

1. インストール・配置は README の PackageControl の指示と `Thino.keypirinha-package` の手動コピーの両方を想定しています。
2. 使用フローは `Thino:` ラベル入力 → メモ本文入力 → `Append` または `Append and Open` の実行 → Obsidian CLI経由でDaily noteへ追記です。
3. `thino.ini` の設定で `enabled`、`item_label`、`vault_name`、`memo_format`、`target_heading`、`ensure_blank_line` を調整可能で、複数 `[custom/*]` があれば別ラベル・テンプレートを追加できます。
4. `ensure_blank_line` は追記前に空行を挿入し、既存コンテンツとメモがくっつかないようにします。

## 実装メモ（参考）

* 各カタログエントリを `Section` にまとめ、`on_catalog` で `ITEM_CAT_KEYWORD` を登録。
* `on_start` で `Append` と `Append and Open` のアクションを登録。
* 入力メモは `memo_format` に `{MEMO}` と `strftime` を適用して整形する想定。
* `target_heading` が指定されている場合は、その見出し配下へ追記する想定。
* `Append and Open` では Obsidian CLI を使って対象ノートを開く想定。

## テスト周り

- 現在の `tests/` は旧仕様の補助関数を前提にしているため、一旦保留。
- 実装方針が Obsidian CLI ベースで固まった後、`Thino` クラスと `[main]` / `[custom/*]` 設定に合わせて更新する。

## 実装タスク

| Task |              タスク               |                                      内容                                       |                  備考                  |
| ---- | --------------------------------- | ------------------------------------------------------------------------------- | -------------------------------------- |
| 1    | 設定読み込みの整理                | `Section`、`enabled`、`ensure_blank_line`、`[main]` / `[custom/*]` の扱いを整理 | 完了                                   |
| 2    | `on_suggest` 実装                 | 入力メモから suggestion を生成し、section index と memo を保持                  | 完了                                   |
| 3    | メモ整形ヘルパー追加              | `memo_format` に `{MEMO}` と `strftime` を適用する                              | 完了                                   |
| 4    | `on_execute` 実装                 | `Append` / `Append and Open` の実行分岐を作る                                   | CLI 呼び出しは一旦スタブ               |
| 5    | Obsidian CLI 呼び出しヘルパー追加 | Daily note への追記、`vault_name`、`ensure_blank_line`、エラー処理を実装        | `target_heading` は扱わない            |
| 6    | 細部調整と実機確認                | 表示文言、空入力、heading 未指定時、失敗時ログ、`build` / `deploy` 確認         | 通常の Daily note 追記を完成状態にする |
| 7    | `target_heading` 追記機能         | ノート内の特定ヘッダー配下へメモを追記する                                      | ノート解析が必要な追加機能として後回し |

## `target_heading` の扱い

- `target_heading` は設定項目としては残す。
- Task 1-6 では `target_heading` が指定されていても、未対応としてログに出す程度に留める。
- Task 5 の CLI 連携は、Daily note への通常追記だけを完成対象にする。
- Task 7 で Markdown ノート解析、見出し検出、追記位置決定を別途実装する。

## `memo_format` の扱い

- 日時の展開には Python の `strftime` 書式を使う。
- 入力メモの差し込みには `{MEMO}` を使う。
- 波括弧を文字として出力したい場合は、Python format のルールに従って `{{Memo}}` のように二重に書く。
