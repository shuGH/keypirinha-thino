import configparser
import datetime
from types import SimpleNamespace

import keypirinha as kp

from src import thino


class ConfigSettings:
    def __init__(self, parser):
        self.parser = parser

    def sections(self):
        return self.parser.sections()

    def get_bool(self, key, section=None, fallback=None):
        try:
            return self.parser.getboolean(section, key)
        except Exception:
            return fallback

    def get_stripped(self, key, section=None, fallback=""):
        try:
            value = self.parser.get(section, key)
            return value.strip()
        except Exception:
            return fallback


def make_settings(config_text):
    parser = configparser.ConfigParser(interpolation=None)
    parser.read_string(config_text)
    return ConfigSettings(parser)


def make_plugin(settings):
    plugin = thino.Thino()
    plugin.load_settings = lambda: settings
    return plugin


DEFAULT_CONFIG = """
[main]
enabled = yes
item_label = Thino:
vault_name = Memos
memo_format = %H:%M:%S {MEMO}
target_heading =
append_newline = yes

[custom/work]
enabled = yes
item_label = Thino: Work
vault_name = Work
memo_format = %Y-%m-%d %H:%M {MEMO}
target_heading = ## Memos
append_newline = no
"""


def test_read_config_loads_main_and_custom_sections():
    plugin = make_plugin(make_settings(DEFAULT_CONFIG))

    plugin._read_config()

    assert len(plugin._sections) == 2

    main_section = plugin._sections[0]
    assert main_section.enabled is True
    assert main_section.item_label == "Thino:"
    assert main_section.vault_name == "Memos"
    assert main_section.memo_format == "%H:%M:%S {MEMO}"
    assert main_section.target_heading == ""
    assert main_section.append_newline is True

    custom_section = plugin._sections[1]
    assert custom_section.enabled is True
    assert custom_section.item_label == "Thino: Work"
    assert custom_section.vault_name == "Work"
    assert custom_section.memo_format == "%Y-%m-%d %H:%M {MEMO}"
    assert custom_section.target_heading == "## Memos"
    assert custom_section.append_newline is False


def test_read_config_ignores_non_custom_sections():
    config = DEFAULT_CONFIG + """

[other/work]
enabled = yes
item_label = Ignored
vault_name = Ignored
"""
    plugin = make_plugin(make_settings(config))

    plugin._read_config()

    assert len(plugin._sections) == 2
    assert [section.item_label for section in plugin._sections] == [
        "Thino:",
        "Thino: Work",
    ]


def test_format_memo_expands_strftime_and_memo_placeholder():
    section = thino.Thino.DEFAULT_SECTION._replace(
        memo_format="%Y-%m-%d %H:%M {MEMO}"
    )
    now = datetime.datetime(2026, 1, 2, 3, 4)

    formatted = thino.Thino()._format_memo(section, "memo text", now)

    assert formatted == "2026-01-02 03:04 memo text"


def test_format_memo_returns_original_memo_when_format_fails():
    section = thino.Thino.DEFAULT_SECTION._replace(memo_format="{UNKNOWN}")

    formatted = thino.Thino()._format_memo(section, "memo text")

    assert formatted == "memo text"


def test_on_catalog_creates_items_for_enabled_sections_only():
    config = DEFAULT_CONFIG + """

[custom/private]
enabled = no
item_label = Thino: Private
vault_name = Private
"""
    plugin = make_plugin(make_settings(config))

    plugin.on_catalog()

    assert len(plugin._last_catalog) == 2
    assert [item.label() for item in plugin._last_catalog] == [
        "Thino:",
        "Thino: Work",
    ]
    assert [item.target() for item in plugin._last_catalog] == ["0", "1"]
    assert plugin._last_catalog[0].category == kp.ItemCategory.KEYWORD
    assert plugin._last_catalog[0].args_hint == kp.ItemArgsHint.REQUIRED
    assert plugin._last_catalog[0].hit_hint == kp.ItemHitHint.NOARGS


def test_on_suggest_clears_suggestions_for_empty_input():
    plugin = make_plugin(make_settings(DEFAULT_CONFIG))
    plugin._read_config()

    result = plugin.on_suggest("   ", [kp.CatalogItem(target="0")])

    assert result == 0
    assert plugin._last_suggestions == []


def test_on_suggest_creates_action_item_for_valid_input():
    config = """
[main]
enabled = yes
item_label = Thino:
vault_name = Memos
memo_format = fixed {MEMO}
target_heading =
append_newline = yes
"""
    plugin = make_plugin(make_settings(config))
    plugin._read_config()

    result = plugin.on_suggest("  hello  ", [kp.CatalogItem(target="0")])

    assert result == 1
    assert len(plugin._last_suggestions) == 1
    suggestion = plugin._last_suggestions[0]
    assert suggestion.category == thino.Thino.ITEM_CAT_ACTION
    assert suggestion.label() == "fixed hello"
    assert suggestion.target() == "0"
    assert suggestion.data_bag() == "hello"
    assert suggestion.args_hint == kp.ItemArgsHint.FORBIDDEN
    assert suggestion.hit_hint == kp.ItemHitHint.NOARGS


def test_on_execute_defaults_to_append_action():
    plugin = thino.Thino()
    plugin._sections = [thino.Thino.DEFAULT_SECTION]
    called = {}

    def fake_append(section, memo, needs_open):
        called["section"] = section
        called["memo"] = memo
        called["needs_open"] = needs_open

    plugin._append_memo = fake_append
    item = kp.CatalogItem(target="0", data_bag="memo")

    result = plugin.on_execute(item, None)

    assert result == 1
    assert called == {
        "section": thino.Thino.DEFAULT_SECTION,
        "memo": "memo",
        "needs_open": False,
    }


def test_on_execute_uses_append_and_open_action():
    plugin = thino.Thino()
    plugin._sections = [thino.Thino.DEFAULT_SECTION]
    called = {}

    def fake_append(section, memo, needs_open):
        called["section"] = section
        called["memo"] = memo
        called["needs_open"] = needs_open

    plugin._append_memo = fake_append
    item = kp.CatalogItem(target="0", data_bag="memo")
    action = kp.Action(name=thino.Thino.ACTION_APPEND_AND_OPEN)

    result = plugin.on_execute(item, action)

    assert result == 1
    assert called["section"] == thino.Thino.DEFAULT_SECTION
    assert called["memo"] == "memo"
    assert called["needs_open"] is True


def test_append_memo_builds_cli_args_with_open():
    plugin = thino.Thino()
    section = thino.Thino.DEFAULT_SECTION._replace(
        vault_name="Work",
        memo_format="fixed {MEMO}",
        append_newline=True,
    )
    called = {}

    def fake_run(args):
        called["args"] = args
        return True

    plugin._run_obsidian_cli = fake_run

    plugin._append_memo(section, "hello", True)

    assert called["args"] == [
        "obsidian.com",
        "vault=Work",
        "daily:append",
        "content=- fixed hello\\n",
        "inline",
        "open",
    ]


def test_append_memo_omits_open_and_trailing_newline_when_disabled():
    plugin = thino.Thino()
    section = thino.Thino.DEFAULT_SECTION._replace(
        vault_name="Work",
        memo_format="fixed {MEMO}",
        append_newline=False,
    )
    called = {}

    def fake_run(args):
        called["args"] = args
        return True

    plugin._run_obsidian_cli = fake_run

    plugin._append_memo(section, "hello", False)

    assert called["args"] == [
        "obsidian.com",
        "vault=Work",
        "daily:append",
        "content=- fixed hello",
        "inline",
    ]


def test_run_obsidian_cli_returns_true_when_subprocess_succeeds(monkeypatch):
    def fake_run(*args, **kwargs):
        return SimpleNamespace(returncode=0, stdout="ok\n", stderr="")

    monkeypatch.setattr(thino.subprocess, "run", fake_run)

    assert thino.Thino()._run_obsidian_cli(["obsidian.com"]) is True


def test_run_obsidian_cli_returns_false_when_subprocess_raises(monkeypatch):
    def fake_run(*args, **kwargs):
        raise OSError("boom")

    monkeypatch.setattr(thino.subprocess, "run", fake_run)

    assert thino.Thino()._run_obsidian_cli(["obsidian.com"]) is False


def test_run_obsidian_cli_returns_false_when_subprocess_fails(monkeypatch):
    def fake_run(*args, **kwargs):
        return SimpleNamespace(returncode=1, stdout="", stderr="failed")

    monkeypatch.setattr(thino.subprocess, "run", fake_run)

    assert thino.Thino()._run_obsidian_cli(["obsidian.com"]) is False
