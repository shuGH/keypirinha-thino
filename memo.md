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
* 入力メモは `memo_format` に `{memo}` と `strftime` を適用して整形する想定。
* `target_heading` が指定されている場合は、その見出し配下へ追記する想定。
* `Append and Open` では Obsidian CLI を使って対象ノートを開く想定。

## テスト周り

- 現在の `tests/` は旧仕様の補助関数を前提にしているため、一旦保留。
- 実装方針が Obsidian CLI ベースで固まった後、`Thino` クラスと `[main]` / `[custom/*]` 設定に合わせて更新する。

## 今後の検討

- `on_suggest` で入力メモを候補として表示する。
- `on_execute` で `Append` / `Append and Open` の処理を実装する。
- Obsidian CLI 実行失敗時のエラー表示を整える。
- `target_heading` が存在しない場合の扱いを決める。
