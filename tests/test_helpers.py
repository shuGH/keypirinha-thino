import configparser
import datetime
import os
from pathlib import Path

import pytest

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


@pytest.fixture
def example_section(tmp_path):
    path = Path(__file__).parent / "thino_test.ini"
    if not path.exists():
        raise FileNotFoundError("thino_test.ini not found for tests")
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(path)
    tests_vault_root = tmp_path / "vault"
    tests_vault_root.mkdir()
    parser.set("custom_item/example", "vault_folder", str(tests_vault_root))
    settings = ConfigSettings(parser)
    plugin = thino.ThinoMemo()
    section = plugin._create_section(settings, "custom_item/example", plugin.DEFAULT_SECTION, "Example")
    return section


def test_format_template_with_placeholders(example_section):
    memo_text = "test"
    now = datetime.datetime(2026, 1, 2, 3, 4)
    formatted = thino.ThinoMemo()._format_template(example_section.memo_template, memo_text, now)
    print("format_template", example_section.memo_template, "->", formatted)
    assert "2026-01-02 03:04" in formatted
    assert "test" in formatted


def test_prepare_memo_entry_records_timestamp(example_section):
    now = datetime.datetime(2026, 1, 2, 3, 4)
    entry = thino.ThinoMemo()._prepare_memo_entry(example_section, "memo text", now)
    print("prepare_memo_entry", entry)
    assert "2026-01-02 03:04" in entry
    assert "memo text" in entry
    assert entry.startswith("[2026-01-02 03:04]")


def test_build_target_path_respects_folder_and_template(tmp_path, example_section):
    customized = example_section._replace(vault_folder=str(tmp_path))
    path = thino.ThinoMemo()._build_target_path(customized, datetime.datetime(2026, 1, 2))
    print("build_target_path", customized.vault_folder, customized.file_path, "->", path)
    assert path.endswith(os.path.join("2026", "01", "2026-01-02.md"))


def test_append_to_file_records_entry_with_timestamp(tmp_path, example_section):
    entry = thino.ThinoMemo()._prepare_memo_entry(example_section, "memo", datetime.datetime(2026, 1, 2, 3, 4))
    path = tmp_path / "post.md"
    thino.ThinoMemo()._append_to_file(str(path), entry, ensure_blank_line=False)
    contents = path.read_text(encoding="utf-8")
    print("append_to_file entry", entry, "file", str(path), "content", contents)
    assert contents.strip().endswith("memo")
    assert contents.count("2026-01-02 03:04") == 1


def test_append_to_file_creates_blank_line(tmp_path, example_section):
    memo = "first"
    path = tmp_path / "memo.md"
    path.write_text("existing", encoding="utf-8")
    entry = thino.ThinoMemo()._prepare_memo_entry(example_section, memo, datetime.datetime(2026, 1, 2, 3, 4))
    thino.ThinoMemo()._append_to_file(str(path), entry, True)
    data = path.read_text(encoding="utf-8")
    print("append_with_blank_line", str(path), "content", data.replace('\n', '\\n'))
    assert "existing" in data
    assert data.endswith("first\n")


def test_seed_note_template_creates_file(tmp_path, example_section):
    target = tmp_path / "new.md"
    now = datetime.datetime.now(datetime.timezone.utc)
    thino.ThinoMemo()._seed_note_template(str(target), example_section, "memo", now)
    assert target.exists()
    content = target.read_text(encoding="utf-8")
    print("seed_note_template", str(target), "template", example_section.note_template, "content", content.replace('\n', '\\n'))
    assert content.startswith("# header")
