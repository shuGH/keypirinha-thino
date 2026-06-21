class ItemCategory:
    KEYWORD = 1
    USER_BASE = 2

class ItemArgsHint:
    ACCEPTED = 1
    NOARGS = 0

class ItemHitHint:
    KEEPALL = 1

class Match:
    ANY = 1

class Sort:
    SCORE_DESC = 1

class Events:
    APPCONFIG = 1
    PACKCONFIG = 2
    NETOPTIONS = 4

class Plugin:
    def __init__(self):
        pass

    def create_item(self, *args, **kwargs):
        return None

    def set_catalog(self, items):
        self._last_catalog = items

    def set_suggestions(self, suggestions, *args, **kwargs):
        self._last_suggestions = suggestions

    def set_actions(self, category, actions):
        self._actions = actions

    def load_settings(self):
        class Settings:
            def sections(self):
                return []

            def get_bool(self, *args, **kwargs):
                return False

            def get_stripped(self, *args, **kwargs):
                return ""

        return Settings()

    def load_text_resource(self, name):
        return ""

    def dbg(self, *args, **kwargs):
        pass

    def warn(self, *args, **kwargs):
        pass
