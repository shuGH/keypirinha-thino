import json

_clipboard = []


def kwargs_encode(**kwargs):
    return json.dumps(kwargs)


def kwargs_decode(value):
    if not value:
        return {}
    try:
        return json.loads(value)
    except Exception:
        return {}


def set_clipboard(value):
    _clipboard.append(value)
