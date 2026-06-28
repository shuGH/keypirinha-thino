class ItemCategory:
    KEYWORD = 1
    USER_BASE = 2


class ItemArgsHint:
    FORBIDDEN = 0
    ACCEPTED = 1
    REQUIRED = 2


class ItemHitHint:
    NOARGS = 0
    KEEPALL = 1


class Match:
    ANY = 1


class Sort:
    NONE = 0
    SCORE_DESC = 1


class Events:
    APPCONFIG = 1
    PACKCONFIG = 2
    NETOPTIONS = 4


class CatalogItem:
    def __init__(
        self,
        category=None,
        label="",
        short_desc="",
        target="",
        args_hint=None,
        hit_hint=None,
        data_bag=None,
    ):
        self.category = category
        self._label = label
        self.short_desc = short_desc
        self._target = target
        self.args_hint = args_hint
        self.hit_hint = hit_hint
        self._data_bag = data_bag

    def label(self):
        return self._label

    def target(self):
        return self._target

    def data_bag(self):
        return self._data_bag


class Action:
    def __init__(self, name="", label="", short_desc=""):
        self._name = name
        self._label = label
        self.short_desc = short_desc

    def name(self):
        return self._name

    def label(self):
        return self._label


class Plugin:
    def __init__(self):
        pass

    def create_item(self, **kwargs):
        return CatalogItem(**kwargs)

    def create_action(self, **kwargs):
        return Action(**kwargs)

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

    def info(self, *args, **kwargs):
        pass
