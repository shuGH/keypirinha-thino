# Thino 開発メモ

## リファレンス

公式のリファレンスを参考にすること

- Keypirinha：https://keypirinha.com/api.html
- Obsidian CLI：https://obsidian.md/ja/help/cli
- Thino：https://github.com/Quorafind/Obsidian-Thino

## 処理フロー

1. `Thino:` ラベル入力
2. メモ本文入力（１つだけ追記項目のサジェスト）
3. `Append` または `Append and Open` の実行
4. Obsidian CLI 経由で Daily note へ追記

`thino.ini` の設定で、`[custom/*]` により複数の書式や Vault 指定が可能

## タスク

- [x] 設定読み込みの整理 ✅ 2026-06-27
- [x] `on_suggest` 実装 ✅ 2026-06-27
- [x] メモ整形ヘルパー追加 ✅ 2026-06-27
- [x] `on_execute` 実装 ✅ 2026-06-27
- [x] Obsidian CLI 呼び出しヘルパー追加 ✅ 2026-06-27
- [x] 細部調整と実機確認 ✅ 2026-06-27
- [ ] test の整理
- [ ] 空行チェックの追加
- [ ] `target_heading` 機能の追加

## テスト

- 現在の `tests/` は旧仕様の補助関数を前提にしているため、一旦保留
- 実装方針が Obsidian CLI ベースで固まった後、`Thino` クラスと `[main]` / `[custom/*]` 設定に合わせて更新する

## 調査

### メモ前後の空行制御

- ini の `append_newline` はメモ末尾の改行追加の有無
- Obsidian CLI の `inline` はメモ前の空行追加の有無
    - Daily note 末尾に既に空行がある場合、`inline` なしで追記するとメモ前に余分な空行が増える可能性がある

### Obsidian CLI 呼び出し

`subprocess.run(["obsidian", ...])` で `daily:append` が成功しない不具合に遭遇した

- `obsidian daily:append ...` はコマンドプロンプトや PowerShell から直接実行すると成功する
- Python の `subprocess.run(["obsidian", ...])` では `daily:append` が `returncode=4294967295`、stdout/stderr 空で失敗した
- Procmon.exe で確認したところ、拡張子なしの `obsidian` は Python subprocess から `Obsidian.exe` を起動していた
- `where obsidian` では `Obsidian.com` と `Obsidian.exe` が見つかったた
    - CLI 用途では `Obsidian.com` を明示する
- `Obsidian.com` はコンソールアプリのため、Keypirinha から起動すると一瞬プロンプトが出る場合がある
    - `subprocess.STARTUPINFO` で非表示起動する

## メモ

* Obsidian CLI を使えば、パス指定不要で Obsidian を操作可能
  * 有効にするにはインストーラー1.12.7 以上が必要
  * Obsidian で開くことも可能
* Daily note が未作成でも `obsidian vault=<VaultName> daily:append content="test"` により Daily note が作成され、Templates 設定が適用されたうえで追記された
