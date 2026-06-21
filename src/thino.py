import datetime
import os
import re

import keypirinha as kp
import keypirinha_util as kpu
from collections import namedtuple


class _MissingToken(dict):
    def __missing__(self, key):
        return "{" + key + "}"


class ThinoMemo(kp.Plugin):
    """Obsidian/Thinoスタイルのメモを Keypirinha から追記するプラグイン

    カタログ登録→入力→ファイル追記の順で処理を進める構成を採用し、各種設定を Section で集約しています"""

    # 各カスタムラベルの設定を保持するための構造体定義
    Section = namedtuple(
        "Section",
        (
            "enabled",
            "item_label",
            "vault_folder",
            "file_path",
            "memo_template",
            "note_template",
            "ensure_blank_line",
        ),
    )

    CONFIG_SECTION_DEFAULTS = "defaults"
    CONFIG_SECTION_CUSTOM_ITEM = "custom_item"

    DEFAULT_SECTION = Section(True, "Thino: Memo", "", "{date}.md", "[{timestamp}] {memo}", "", False)

    # インスタンス生成時の状態初期化
    def __init__(self):
        super().__init__()
        self._sections = []

    # 起動時に設定を読み込み、セクション情報を構築します
    def on_start(self):
        settings = self.load_settings()
        self._sections = self._build_sections_from_settings(settings)
        self.dbg("Loaded sections", len(self._sections))

    # 設定済みのセクションをカタログアイテムとして登録します
    def on_catalog(self):
        # 設定された Section を KEYWORD カテゴリでカタログ登録
        catalog = []
        for idx, section in enumerate(self._sections):
            if not section.item_label:
                continue

            desc_parts = []
            if section.vault_folder:
                desc_parts.append(section.vault_folder)
            if section.file_path:
                desc_parts.append(section.file_path)

            item = self.create_item(
                category=kp.ItemCategory.KEYWORD,
                label=section.item_label,
                short_desc=" / ".join(desc_parts),
                target=f"thino:{idx}",
                args_hint=kp.ItemArgsHint.ACCEPTED,
                hit_hint=kp.ItemHitHint.KEEPALL,
                data_bag=str(idx),
            )
            catalog.append(item)

        self.set_catalog(catalog)

    # 入力中テキストからメモ候補生成と候補リスト返却
    def on_suggest(self, user_input, items_chain):
        # 最後のカタログ項目を基点とした候補生成
        if not items_chain:
            return 0

        last_item = items_chain[-1]
        section_idx, _ = self._decode_item_data_bag(last_item.data_bag())
        if section_idx is None or section_idx >= len(self._sections):
            return 0

        memo_text = user_input
        if not memo_text.strip():
            return 0

        section = self._sections[section_idx]
        entry = self._prepare_memo_entry(section, memo_text)

        desc_parts = []
        if section.vault_folder:
            desc_parts.append(section.vault_folder)
        if section.file_path:
            desc_parts.append(section.file_path)

        suggestion = self.create_item(
            category=kp.ItemCategory.USER_BASE,
            label=entry,
            short_desc=" / ".join(desc_parts) if desc_parts else "Thino memo",
            target=last_item.target(),
            args_hint=kp.ItemArgsHint.NOARGS,
            hit_hint=kp.ItemHitHint.KEEPALL,
            data_bag=kpu.kwargs_encode(section=section_idx, memo=memo_text),
        )

        self.set_suggestions([suggestion], kp.Match.ANY, kp.Sort.SCORE_DESC)
        return 1

    # 確定項目に対するファイル書き換えとパスコピー
    def on_execute(self, item, action):
        section_idx, metadata = self._decode_item_data_bag(item.data_bag())
        if section_idx is None or section_idx >= len(self._sections):
            return

        memo_text = metadata.get("memo", "") if metadata else ""
        if not memo_text or not memo_text.strip():
            return

        section = self._sections[section_idx]
        now = datetime.datetime.now()
        entry = self._prepare_memo_entry(section, memo_text, now)
        target_path = self._build_target_path(section, now)
        if not target_path:
            self.warn("セクション '{}' のファイルパスが不正です".format(section.item_label))
            return

        self._seed_note_template(target_path, section, memo_text, now)
        self._append_to_file(target_path, entry, section.ensure_blank_line)
        # 処理完了後に対象ファイルパスをクリップボードへコピーする
        kpu.set_clipboard(target_path)

    # 外部設定変更時のセクション再読み込み
    def on_events(self, flags):
        if flags & (kp.Events.APPCONFIG | kp.Events.PACKCONFIG | kp.Events.NETOPTIONS):
            settings = self.load_settings()
            self._sections = self._build_sections_from_settings(settings)
            self.dbg("Reloaded sections", len(self._sections))
            self.on_catalog()

    # @TODO: 以下の補助関数を必要に応じて追加

    # 設定ファイルから Section リスト構築
    def _build_sections_from_settings(self, settings):
        # 設定からセクション一覧を構築し、custom_item/* を複数追加できる形にします
        sections = []
        default_section = self._create_section(settings, self.CONFIG_SECTION_DEFAULTS, self.DEFAULT_SECTION)
        if default_section.enabled:
            sections.append(default_section)

        for section_label in settings.sections():
            if not section_label.lower().startswith(self.CONFIG_SECTION_CUSTOM_ITEM + "/"):
                continue

            display_name = section_label[len(self.CONFIG_SECTION_CUSTOM_ITEM) + 1 :].strip()
            if not display_name:
                self.warn("Invalid section name '{}'.".format(section_label))
                continue

            section = self._create_section(settings, section_label, self.DEFAULT_SECTION, display_name)
            if section.enabled:
                sections.append(section)

        return sections

    # 個別セクション設定の取得と Section まとめ
    def _create_section(self, settings, section_label, fallback, display_name=None):
        enabled = settings.get_bool("enable", section=section_label, fallback=fallback.enabled)
        item_label = settings.get_stripped(
            "item_label", section=section_label, fallback=display_name or fallback.item_label
        )
        vault_folder = settings.get_stripped("vault_folder", section=section_label, fallback=fallback.vault_folder)
        file_path = settings.get_stripped("file_path", section=section_label, fallback=fallback.file_path)
        memo_template = settings.get_stripped(
            "memo_template", section=section_label, fallback=fallback.memo_template
        )
        note_template = settings.get_stripped(
            "note_template", section=section_label, fallback=fallback.note_template
        )
        ensure_blank_line = settings.get_bool(
            "ensure_blank_line", section=section_label, fallback=fallback.ensure_blank_line
        )

        return self.Section(
            enabled,
            item_label,
            vault_folder,
            file_path,
            memo_template,
            note_template,
            ensure_blank_line,
        )

    # memo_template 適用による追記文字列整形
    def _prepare_memo_entry(self, section, memo_text, now=None):
        now = now or datetime.datetime.now()
        template = section.memo_template or self.DEFAULT_SECTION.memo_template
        formatted = self._format_template(template, memo_text, now)
        return formatted or memo_text

    # ファイル末尾追記時のディレクトリ・空行処理
    def _append_to_file(self, path, entry, ensure_blank_line):
        # まずディレクトリを書き出し可能な状態にしてから追記します
        self._ensure_directory(path)
        needs_blank = False
        if ensure_blank_line and os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    f.seek(0, os.SEEK_END)
                    if f.tell():
                        f.seek(-1, os.SEEK_END)
                        needs_blank = f.read(1) not in (b"\n", b"\r")
            except OSError:
                needs_blank = False

        final_entry = entry if entry.endswith("\n") else entry + "\n"
        with open(path, "a", encoding="utf-8") as f:
            if needs_blank:
                f.write("\n")
            f.write(final_entry)

    # data_bag からセクション番号とメタ情報抽出
    def _decode_item_data_bag(self, data_bag):
        if not data_bag:
            return None, {}

        try:
            section_idx = int(data_bag)
            return section_idx, {}
        except (TypeError, ValueError):
            pass

        try:
            decoded = kpu.kwargs_decode(data_bag)
        except Exception:
            return None, {}

        if not isinstance(decoded, dict):
            return None, {}

        section_value = decoded.get("section")
        try:
            section_idx = int(section_value)
        except (TypeError, ValueError):
            section_idx = None

        return section_idx, decoded

    # strftime＋format_map によるテンプレート評価
    def _format_template(self, template, memo_text, now):
        if not template:
            return ""
        context = self._build_template_context(memo_text, now)
        formatted = now.strftime(template)
        return formatted.format_map(_MissingToken(context))

    # テンプレート用プレースホルダ辞書生成
    def _build_template_context(self, memo_text, now):
        return {
            "memo": memo_text,
            "timestamp": now.strftime("%Y-%m-%d %H:%M"),
            "date": now.strftime("%Y-%m-%d"),
        }

    # Section folder/file_path からファイルパス組み立て
    def _build_target_path(self, section, now):
        file_template = section.file_path or self.DEFAULT_SECTION.file_path
        relative_path = now.strftime(file_template) if file_template else ""
        if not relative_path:
            relative_path = now.strftime(self.DEFAULT_SECTION.file_path)

        folder = self._expand_path(section.vault_folder)
        if not folder:
            self.warn("セクション '{}' に vault_folder が未設定のためファイルパスを計算できません".format(section.item_label))
            return ""

        return os.path.abspath(os.path.normpath(os.path.join(folder, relative_path)))

    # 環境変数・ホームディレクトリを含む値展開
    def _expand_path(self, value):
        if not value:
            return ""
        expanded = os.path.expanduser(value)
        expanded = os.path.expandvars(expanded)
        return self._expand_env_placeholders(expanded)

    # ${env:VAR} 形式を環境変数値へ置換
    def _expand_env_placeholders(self, value):
        pattern = re.compile(r"\$\{env:([^}]+)\}")
        return pattern.sub(lambda m: os.environ.get(m.group(1), ""), value)

    # パス先ディレクトリ作成
    def _ensure_directory(self, path):
        directory = os.path.dirname(path)
        if not directory:
            return
        os.makedirs(directory, exist_ok=True)

    # note_template によるファイル先行作成
    def _seed_note_template(self, path, section, memo_text, now):
        # note_template を埋めてファイルの雛形を作ったうえで本文を処理します
        if os.path.exists(path):
            return

        template = section.note_template
        if not template:
            return

        content = self._format_template(template, memo_text, now)
        if not content:
            return

        self._ensure_directory(path)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
            if not content.endswith("\n"):
                f.write("\n")
