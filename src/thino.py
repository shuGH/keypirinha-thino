import keypirinha as kp
import keypirinha_util as kpu


class ThinoMemo(kp.Plugin):
    """Thinoメモの雛形。詳細実装はTODOで埋める。"""

    def __init__(self):
        super().__init__()
        self._sections = []

    def on_start(self):
        # @TODO: `thino.ini` を読み込み、`self._sections` を構築
        pass

    def on_catalog(self):
        # @TODO: カタログに表示するアイテムを作って `set_catalog` する
        pass

    def on_suggest(self, user_input, items_chain):
        # @TODO: ユーザー入力からメモ候補を作成し `set_suggestions` で返す
        pass

    def on_execute(self, item, action):
        # @TODO: 選ばれたメモを対象ファイルへ追記し、パスをクリップボードへ
        pass

    def on_events(self, flags):
        if flags & (kp.Events.APPCONFIG | kp.Events.PACKCONFIG | kp.Events.NETOPTIONS):
            # @TODO: 設定変更時の再読込を行う
            pass

    # @TODO: 以下の補助関数を必要に応じて追加

    def _build_sections_from_settings(self, settings):
        # @TODO: `folder` / `file_path` / `memo_template` などをパースしてセクションを返す
        return []

    def _prepare_memo_entry(self, section, memo_text):
        # @TODO: `memo_template` から行を整形する
        return memo_text

    def _append_to_file(self, path, entry, ensure_blank_line):
        # @TODO: ディレクトリ作成 → ファイル追記を実装
        pass
