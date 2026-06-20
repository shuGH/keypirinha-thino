# Keypirinha Plugin: Thino Memo

ObsidianのThinoスタイルのメモをKeypirinhaから呼び出すプラグインです。起動して文字を入力すると、指定フォルダ内の当日ファイル（指定した日付書式）にタイムスタンプ付きメモが末尾に追記されます。

## インストール

### マネージド

[PackageControl](https://github.com/ueffel/Keypirinha-PackageControl)から `ThinoMemo` をインストールしてください。

### 手動

1. 最新の `ThinoMemo.keypirinha-package` を [Releases](https://github.com/shuGH/keypirinha-thino/releases) からダウンロードします。
2. 次の `InstalledPackages` フォルダに移動します。
   * ポータブルモード: `Keypirinha\portable\Profile\InstalledPackages`
   * インストールモード: `%APPDATA%\Keypirinha\InstalledPackages`

## 使用方法

1. Keypirinhaを起動し、`Thino:` などの設定済みラベルを入力します。
2. 保存したいメモを入力し、Enterを押します。
3. 設定されたフォルダ内の当日ファイル（`thino.ini` の `file_path` に従う）に `memo_template` に応じた行が追加され、更新先のファイルパスがクリップボードに複写されます。
  - 該当ファイルがない場合は `note_template` にもとづいた新規作成されます

異なるフォルダや別の形式でメモを残したい場合は、`[custom_item/*]` セクションを増やしてラベルやテンプレートを分けてください。

## 設定

`thino.ini` の `[defaults]` もしくは `[custom_item/*]` セクションで以下を調整できます。

- `folder`（必須）: ObsidianのVaultやノートルート。環境変数 `${env:HOME}` などの展開をサポートします。
- `file_path`: メモを追記するファイルパス。Pythonの `strftime` 構文をサポート。デフォルトは `%Y/%m/%Y-%m-%d.md`。
- `memo_template`: `{memo}` を使ったメモテンプレート。Pythonの `strftime` 構文をサポート。デフォルトは `[%Y-%m-%d %H:%M] {memo}`。
- `note_template`: ファイルが存在しないときの新規作成する内容。
- `ensure_blank_line`: `yes` のとき、既存ファイルが空でない場合に空行を挿入してから追記します。

## チェンジログ

### v1.0

- Obsidian ThinoスタイルのメモをKeypirinhaからファイル末尾へ追記する基本機能を実装。

## ライセンス

このパッケージは [MIT](LICENSE) ライセンスのもとで配布されています。

## 作者

[Shuzo.Iwasaki](https://github.com/shuGH)

( • ̀ω•́ )و enjoy!
