import datetime
import keypirinha as kp
import keypirinha_util as kpu
from collections import namedtuple


class ThinoMemo(kp.Plugin):
    """Thinoメモの雛形。詳細実装はTODOで埋める。"""

    Section = namedtuple(
        "Section",
        (
            "enabled",
            "item_label",
            "folder",
            "file_path",
            "memo_template",
            "note_template",
            "ensure_blank_line",
        ),
    )

    CONFIG_SECTION_DEFAULTS = "defaults"
    CONFIG_SECTION_CUSTOM_ITEM = "custom_item"

    DEFAULT_SECTION = Section(True, "Thino: Memo", "", "{date}.md", "[{timestamp}] {memo}", "", False)

    def __init__(self):
        super().__init__()
        self._sections = []

    def on_start(self):
        settings = self.load_settings()
        self._sections = self._build_sections_from_settings(settings)
        self.dbg("Loaded sections", len(self._sections))

    def on_catalog(self):
        catalog = []
        for idx, section in enumerate(self._sections):
            if not section.item_label:
                continue

            desc_parts = []
            if section.folder:
                desc_parts.append(section.folder)
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

    def on_suggest(self, user_input, items_chain):
        if not items_chain:
            return 0

        last_item = items_chain[-1]
        section_idx = self._parse_section_index(last_item.data_bag())
        if section_idx is None or section_idx >= len(self._sections):
            return 0

        memo_text = user_input
        if not memo_text.strip():
            return 0

        section = self._sections[section_idx]
        entry = self._prepare_memo_entry(section, memo_text)

        desc_parts = []
        if section.folder:
            desc_parts.append(section.folder)
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

    def on_execute(self, item, action):
        # @TODO: 選ばれたメモを対象ファイルへ追記し、パスをクリップボードへ
        pass

    def on_events(self, flags):
        if flags & (kp.Events.APPCONFIG | kp.Events.PACKCONFIG | kp.Events.NETOPTIONS):
            settings = self.load_settings()
            self._sections = self._build_sections_from_settings(settings)
            self.dbg("Reloaded sections", len(self._sections))
            self.on_catalog()

    # @TODO: 以下の補助関数を必要に応じて追加

    def _build_sections_from_settings(self, settings):
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

    def _create_section(self, settings, section_label, fallback, display_name=None):
        enabled = settings.get_bool("enable", section=section_label, fallback=fallback.enabled)
        item_label = settings.get_stripped(
            "item_label", section=section_label, fallback=display_name or fallback.item_label
        )
        folder = settings.get_stripped("folder", section=section_label, fallback=fallback.folder)
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
            folder,
            file_path,
            memo_template,
            note_template,
            ensure_blank_line,
        )

    def _prepare_memo_entry(self, section, memo_text):
        now = datetime.datetime.now()
        template = section.memo_template or self.DEFAULT_SECTION.memo_template
        applied = now.strftime(template)

        class _SafeDict(dict):
            def __missing__(self, key):
                return "{" + key + "}"

        values = _SafeDict(
            memo=memo_text,
            timestamp=now.strftime("%Y-%m-%d %H:%M"),
            date=now.strftime("%Y-%m-%d"),
        )

        return applied.format_map(values)

    def _parse_section_index(self, data_bag):
        if not data_bag:
            return None

        try:
            return int(data_bag)
        except (TypeError, ValueError):
            decoded = kpu.kwargs_decode(data_bag)
            if not isinstance(decoded, dict):
                return None

            section_value = decoded.get("section")
            try:
                return int(section_value)
            except (TypeError, ValueError):
                return None

    def _append_to_file(self, path, entry, ensure_blank_line):
        # @TODO: ディレクトリ作成 → ファイル追記を実装
        pass
