import datetime
import os
import pathlib
import tempfile

import pytest

from src import thino


class DummySection(thino.ThinoMemo.Section):
    def __new__(cls, **kwargs):
        defaults = {
            "enabled": True,
            "item_label": "Thino",
            "folder": "",
            "file_path": "{date}.md",
            "memo_template": "[{timestamp}] {memo}",
            "note_template": "",
            "ensure_blank_line": False,
        }
        defaults.update(kwargs)
        return super().__new__(cls, **defaults)


@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path


def test_format_template_with_placeholders():
    memo_text = "test"
    now = datetime.datetime(2026, 1, 2, 3, 4)
    formatted = thino.ThinoMemo()._format_template("[{timestamp}] {memo}", memo_text, now)
    assert "2026-01-02 03:04" in formatted
    assert "test" in formatted


def test_build_target_path_respects_folder_and_template(tmp_path):
    section = DummySection(folder=str(tmp_path), file_path="%Y/%m/test.md")
    path = thino.ThinoMemo()._build_target_path(section, datetime.datetime(2026, 1, 2))
    assert path.endswith(os.path.join("2026", "01", "test.md"))


def test_append_to_file_creates_blank_line(tmp_path):
    section = DummySection(ensure_blank_line=True)
    memo = "first"
    path = tmp_path / "memo.md"
    path.write_text("existing", encoding="utf-8")
    thino.ThinoMemo()._append_to_file(str(path), memo, True)
    data = path.read_text(encoding="utf-8")
    assert "existing" in data
    assert data.endswith("first\n")


def test_seed_note_template_creates_file(tmp_path):
    section = DummySection(note_template="# header\n")
    target = tmp_path / "new.md"
    thino.ThinoMemo()._seed_note_template(str(target), section, "memo", datetime.datetime.utcnow())
    assert target.exists()
