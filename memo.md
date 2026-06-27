# Thino Memo 開発メモ

## 概要

KeypirinhaからObsidian/Thinoスタイルのメモづくりを支援するプラグインです。`Thino:` などのラベルでメモ入力を受け付け、設定されたフォルダと日付フォーマットに応じた Markdown ファイルの末尾へ、時間付きの一行を追記します。追記後のファイルパスはクリップボードにコピーされるので、Obsidian ですぐに開き直せます。

## リファレンス

公式のリファレンスを参考にすること

- Keypirinha：https://keypirinha.com/api.html
- Obsidian CLI：https://obsidian.md/ja/help/cli
- Thino：https://github.com/Quorafind/Obsidian-Thino

## READMEとの整合

1. インストール・配置は README の PackageControl の指示と `ThinoMemo.keypirinha-package` の手動コピーの両方を想定しています。
2. 使用フローは `Thino:` ラベル入力 → メモ本文入力 → 対象ファイル末尾への `memo_template` による追記、ファイル未作成時は `note_template` による新規作成 → ファイルパスをクリップボードコピーです。
3. `thino.ini` の設定で `folder`（Vault/ルート）、`file_path`（strftime 文字列）、`memo_template`、`note_template`、`ensure_blank_line` を調整可能で、複数 `[custom_item/*]` があれば別ラベル・テンプレートを追加できます。
4. `ensure_blank_line` は既存ファイルに空行を挿入してから追記するため、既存コンテンツとメモがくっつかないようにします。

## 実装メモ（参考）

* 各カタログエントリを `Section` にまとめ、`on_catalog` で `ITEMCAT_ENTRY` を登録。
* 入力時に `Section.file_path` を `strftime` で評価して対象パスを決定し、`memo_template` で行を整形。
* `ensure_blank_line` の状態に応じて空行を挿入し、`open(path, "a")` で末尾に追記。
* `data_bag` を使って `memo`・`timestamp`・`path` を保持し、`on_execute` で再度取り出して追記処理を完了させる構成。

## テスト周り

- `tests/` 以下に Keypirinha/Getutil スタブとテストケースを置き、`pytest` で補助関数（テンプレート整形・パス構築・追記処理・note_template シード）を検証中。`poetry` 環境で `poetry run pytest` を使う方針。
- `.gitignore` に `tests/tmp/`/`tests/__pycache__/` を追加して出力を無視。

## 今後の検討

- `note_template` に YAML フロントマターなどを含めて、新規ファイル作成時によりリッチな構造を与えられるようにする。
- ファイル追記完了を通知や音、トーストなどでフィードバックし、Obsidian への移動体験を強化。
