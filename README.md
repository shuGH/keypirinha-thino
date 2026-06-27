# Keypirinha Plugin: Thino

ObsidianのThinoスタイルのメモをKeypirinhaから呼び出すプラグインです。起動して文字を入力すると、Obsidian CLI経由で設定したVaultのDaily noteへタイムスタンプ付きメモを追記します。

Thino：https://github.com/Quorafind/Obsidian-Thino

## インストール

### マネージド

[PackageControl](https://github.com/ueffel/Keypirinha-PackageControl)から `Thino` をインストールしてください。

### 手動

1. 最新の `Thino.keypirinha-package` を [Releases](https://github.com/shuGH/keypirinha-thino/releases) からダウンロードします。
2. 次の `InstalledPackages` フォルダに移動します。
   * ポータブルモード: `Keypirinha\portable\Profile\InstalledPackages`
   * インストールモード: `%APPDATA%\Keypirinha\InstalledPackages`

## 使用方法

0. 必須：Obsidian CLIを使用するため有効にすること
  - 参考：https://obsidian.md/ja/help/cli
1. Keypirinhaを起動し、`Thino:` などの設定済みラベルを入力します。
2. 保存したいメモを入力します。
3. `Append` または `Append and Open` を実行します。
   - `Append`: Daily noteへメモを追記します。
   - `Append and Open`: メモを追記し、Obsidianで対象ノートを開きます。

異なるVaultや別の形式でメモを残したい場合は、`[custom/*]` セクションを増やしてラベルやテンプレートを分けてください。

## 設定

`thino.ini` の `[main]` もしくは `[custom/*]` セクションで以下を調整できます。

- `enabled`: この項目を有効にするかどうか。
- `item_label`: Keypirinhaに表示するラベル。
- `vault_name`: Obsidian CLIで使用するVault名。
- `memo_format`: `{MEMO}` を使ったメモテンプレート。Pythonの `strftime` 構文をサポート。デフォルトは `[%Y-%m-%d %H:%M] {MEMO}`。
- `target_heading`: 追記先の見出し。空の場合はDaily noteへ直接追記します。
- `ensure_blank_line`: `yes` のとき、追記前に空行を挿入します。

`memo_format` は日時に `strftime` の `%H:%M` などを使い、入力メモの差し込みに `{MEMO}` を使います。波括弧を文字として出力したい場合は、Python format のルールに従って `{{Memo}}` のように二重に書きます。

## チェンジログ

### v1.0

- Obsidian CLIを使い、Daily noteへThinoスタイルのメモを追記する基本機能を実装。

## ライセンス

このパッケージは [MIT](LICENSE) ライセンスのもとで配布されています。

## 作者

[Shuzo.Iwasaki](https://github.com/shuGH)

( • ̀ω•́ )و enjoy!
