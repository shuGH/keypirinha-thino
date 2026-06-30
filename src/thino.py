# Keypirinha launcher (keypirinha.com)

import datetime
import os
import re
import subprocess

import keypirinha as kp
import keypirinha_util as kpu
from collections import namedtuple

# 用語
#   Section: 設定ファイル(.ini)内の設定項目をまとめる単位
#   Catalog: 検索対象となる候補項目（CatalogItem）の一覧
#   Suggestions: 入力に応じて動的に生成される候補項目（CatalogItem）の一覧
#   ItemCategory: CatalogItemの種類を表すカテゴリ（KEYWORD、FILE、URLなど）
#   Action: CatalogItemに対して実行できる操作（開く、コピーなど）
# ライフサイクル
#   on_start()   : 初期化
#   on_catalog() : 検索対象(Catalog)を登録
#   on_suggest() : 入力に応じて候補(Suggestions)を生成
#   on_execute() : 選択された候補を実行

class Thino(kp.Plugin):
    """
    ObsidianのThinoプラグインのメモを Keypirinha から追記するプラグイン
    必須： Obsidian CLIを使用するため有効にすること（参考：https://obsidian.md/ja/help/cli）
    """

    _debug = False

    # 設定項目名
    Section = namedtuple(
        "Section",
        (
            "enabled",
            "item_label",
            "vault_name",
            "memo_format",
            # @TODO: ヘッダーに対応する
            "target_heading",
            "append_newline_after_memo"
        )
    )
    Commons = namedtuple(
        "Commons",
        (
            "ensure_blank_line_before_memo",
        )
    )

    CONFIG_SECTION_COMMON = "common"
    CONFIG_SECTION_MAIN = "main"
    CONFIG_SECTION_CUSTOM = "custom"

    # アクション：メモを追記
    ACTION_APPEND = "append"
    # アクション：メモを追記しObsidianで開く（ObsidianCLIを使用）
    ACTION_APPEND_AND_OPEN = "append_and_open"

    # カテゴリ：初回表示
    ITEM_CAT_KEYWORD = kp.ItemCategory.KEYWORD
    # カテゴリ：アクション
    ITEM_CAT_ACTION = kp.ItemCategory.USER_BASE + 1

    DEFAULT_SECTION = Section(True, "Thino:", "Memos", "%H:%M:%S {MEMO}", "", True)
    DEFAULT_COMMONS = Commons(False)

    _commons = DEFAULT_COMMONS
    _sections = []

    # 初期化
    def __init__(self):
        super().__init__()
        self._commons = self.DEFAULT_COMMONS
        self._sections = []

    # 起動時
    def on_start(self):
        self._read_config()

        # アクションを追加
        actions = [
            self.create_action(
                name=self.ACTION_APPEND,
                label="Append",
                short_desc="Append memo to dailynote."),
            self.create_action(
                name=self.ACTION_APPEND_AND_OPEN,
                label="Append and Open",
                short_desc="Append memo and open dailynote in Obsidian."),
        ]
        self.set_actions(self.ITEM_CAT_ACTION, actions)

    # カタログが生成された時
    def on_catalog(self):
        self._read_config()

        # 項目を追加
        catalog = []
        for index, section in enumerate(self._sections):
            if not section.enabled:
                continue

            # CatalogItem
            # category  : CatalogItemの種類（実行時に参照できる、KEYWORD、FILE、URL、ERROR、USER_BASE：プラグイン独自カテゴリの開始値）
            # label     : 検索結果に表示する名前
            # short_desc: 検索結果に表示する説明文
            # target    : 任意のデータ（実行時に参照できる）
            # args_hint : 追加入力の要否（FORBIDDEN：なし、ACCEPTED：どちらでも、REQUIRED：必須）
            # hit_hint  : 検索時の履歴参照方法（履歴にどう残すか、IGNORE：履歴に残さない、NOARGS：残すが入力内容は含めない、KEEPALL：残すし入力内容も含める）
            catalog.append(
                self.create_item(
                    category=self.ITEM_CAT_KEYWORD,
                    label=section.item_label,
                    short_desc="Append Memo ({}): {}".format(section.vault_name, section.target_heading),
                    target=str(index),
                    args_hint=kp.ItemArgsHint.REQUIRED,
                    hit_hint=kp.ItemHitHint.NOARGS
                )
            )
        self.set_catalog(catalog)

    # キー入力時
    def on_suggest(self, user_input, items_chain):
        # 最後のカタログ項目を基点とした候補生成
        if not items_chain:
            return 0

        last_item = items_chain[-1]
        memo = user_input.strip()
        section_index, section = self._get_section(last_item)

        # バリデーション
        if not len(memo):
            self.set_suggestions([], kp.Match.ANY, kp.Sort.NONE)
            return 0

        if section is None:
            self.set_suggestions([], kp.Match.ANY, kp.Sort.NONE)
            return 0

        # 候補を設定
        # Match.ANY：どんな入力でも候補として出してよい
        # Sort.NONE：候補を並び替えない
        suggestion = self.create_item(
            category=self.ITEM_CAT_ACTION,
            label="{}".format(self._format_memo(section, memo)),
            short_desc="Append memo to dailynote. ({}): {}".format(section.vault_name, section.target_heading),
            target=str(section_index),
            args_hint=kp.ItemArgsHint.FORBIDDEN,
            hit_hint=kp.ItemHitHint.NOARGS,
            data_bag=memo
        )
        self.set_suggestions([suggestion], kp.Match.ANY, kp.Sort.NONE)

        return 1

    # アイテム選択時
    def on_execute(self, item, action):
        memo = item.data_bag()
        section_index, section = self._get_section(item)
        action_name = action.name() if action else self.ACTION_APPEND

        # バリデーション
        if not len(memo):
            self.warn("Memo is empty.")
            return 0

        if section is None:
            self.warn("Invalid section: {}".format(item.target()))
            return 0

        # inline指定の要否を判定
        def needs_inline():
            if not self._commons.ensure_blank_line_before_memo:
                return True

            note_path = self._get_daily_note_path(section)
            if not note_path:
                return False

            return self._has_trailing_blank_line(note_path)

        # アクションの分岐
        if action_name == self.ACTION_APPEND:
            self._append_memo(section, memo, needs_inline(), False)
        elif action_name == self.ACTION_APPEND_AND_OPEN:
            self._append_memo(section, memo, needs_inline(), True)
        else:
            self.warn("Unknown action: {}".format(action_name))
            return 0

        return 1

    # 何かしらのイベント発生時
    def on_events(self, flags):
        # コンフィグ変更時
        if flags & (kp.Events.APPCONFIG | kp.Events.PACKCONFIG | kp.Events.NETOPTIONS):
            self._read_config()
            self.on_catalog()

    # LaunchBoxが表示された時
    def on_activated(self):
        # @NOP:
        pass

    # LaunchBoxが非表示になった時
    def on_deactivated(self):
        # @NOP:
        pass

    # コンフィグの読み込み
    def _read_config(self):
        settings = self.load_settings()

        # 共通設定の読み込み
        def read_common():
            return self.Commons(
                settings.get_bool(
                    "ensure_blank_line_before_memo",
                    section=self.CONFIG_SECTION_COMMON,
                    fallback=self.DEFAULT_COMMONS.ensure_blank_line_before_memo
                )
            )

        # 項目の作成
        def create_section(section_label):
            # 旧設定との互換性維持
            append_newline_after_memo = settings.get_bool(
                "append_newline",
                section=section_label,
                fallback=self.DEFAULT_SECTION.append_newline_after_memo
            )

            return self.Section(
                settings.get_bool("enabled", section=section_label, fallback=self.DEFAULT_SECTION.enabled),
                settings.get_stripped("item_label", section=section_label, fallback=self.DEFAULT_SECTION.item_label),
                settings.get_stripped("vault_name", section=section_label, fallback=self.DEFAULT_SECTION.vault_name),
                settings.get_stripped("memo_format", section=section_label, fallback=self.DEFAULT_SECTION.memo_format),
                settings.get_stripped("target_heading", section=section_label, fallback=self.DEFAULT_SECTION.target_heading),
                settings.get_bool("append_newline_after_memo", section=section_label, fallback=append_newline_after_memo)
            )

        self._commons = read_common()
        self._sections = []
        name_text = ""

        # デフォルトセクション
        self._sections.append(create_section(self.CONFIG_SECTION_MAIN))
        name_text = self.CONFIG_SECTION_MAIN
        # 追加セクション
        for section_label in settings.sections():
            if not section_label.lower().startswith(self.CONFIG_SECTION_CUSTOM + "/"):
                continue

            section_name = section_label[len(self.CONFIG_SECTION_CUSTOM) + 1:].strip()
            if not len(section_name):
                self.warn('Invalid section name: "{}".'.format(section_label))
                continue

            self._sections.append(create_section(section_label))
            name_text = "{}, {}".format(name_text, section_name)

        self.dbg("Loaded config sections: {}".format(name_text))

    # アイテムから設定項目を取得
    def _get_section(self, item):
        try:
            section_index = int(item.target())
        except ValueError:
            return None, None

        if section_index < 0 or section_index >= len(self._sections):
            return None, None

        return section_index, self._sections[section_index]

    # メモをフォーマット
    def _format_memo(self, section, memo, now=None):
        if now is None:
            now = datetime.datetime.now()

        # strftime の日時書式と Python format の {MEMO} を使う
        try:
            memo_format = now.strftime(section.memo_format)
            formatted = memo_format.format(MEMO=memo)
        except Exception as exc:
            self.warn("Failed to format memo: {}".format(exc))
            return memo

        self.dbg("Formatted memo: {}".format(formatted))
        return formatted

    # メモの追記
    def _append_memo(self, section, memo, needs_inline, needs_open):
        formatted = self._format_memo(section, memo)
        content = "- {}{}".format(formatted, "\\n" if section.append_newline_after_memo else "")

        # @NOTE: daily:append は Dailynote が存在しない場合でも作成して追記する（テンプレートも適用される）
        args = [
            # @NOTE: 拡張子なしの obsidian は subprocess からだと Obsidian.exe を起動するため、CLI用の Obsidian.com を明示する
            "obsidian.com",
            "vault={}".format(section.vault_name),
            "daily:append",
            "content={}".format(content)
        ]
        if needs_inline:
            args.append("inline")

        if needs_open:
            args.append("open")

        self._run_obsidian_cli(args)

    # Daily noteのパスを取得
    def _get_daily_note_path(self, section):
        success, output = self._run_obsidian_cli([
            "obsidian.com",
            "vault={}".format(section.vault_name),
            "daily:path"
        ])
        if not success:
            return ""

        return output

    # Obsidian CLIを実行
    def _run_obsidian_cli(self, args):
        self.dbg("Obsidian CLI args: {}".format(args))

        startupinfo = None
        # nt: Windows 系OS、posix: macOS/Linux
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0

        try:
            result = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                startupinfo=startupinfo
            )
        except Exception as exc:
            self.warn("Failed to run Obsidian CLI: {}".format(exc))
            return False, ""

        if result.returncode:
            self.warn("Obsidian CLI failed: returncode={}, stdout={}, stderr={}".format(
                result.returncode,
                result.stdout.strip(),
                result.stderr.strip()
            ))
            return False, ""

        self.info("Done: {}, {}".format(args, result.stdout.strip()))

        return True, result.stdout.strip()

    # Dailynote末尾の空行有無を判定
    def _has_trailing_blank_line(self, note_path):
        if not os.path.isfile(note_path):
            self.warn("Dailynote is not found: {}".format(note_path))
            return False

        if not os.access(note_path, os.R_OK):
            self.warn("Dailynote is not readable: {}".format(note_path))
            return False

        try:
            # rb: バイト列として読む
            with open(note_path, "rb") as note_file:
                content = note_file.read()
        except Exception as exc:
            self.warn("Failed to read dailynote: {}".format(exc))
            return False

        return re.search(rb"(?:^|[\r\n])[ \t]*(?:\r\n|\r|\n)\Z", content) is not None

