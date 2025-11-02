import json
from pathlib import Path
import pyxel as px


def get_btn_state():
    return {
        "u": px.btn(px.KEY_UP),
        "d": px.btn(px.KEY_DOWN),
        "l": px.btn(px.KEY_LEFT),
        "r": px.btn(px.KEY_RIGHT),
        "a": px.btnp(px.KEY_Z, 10, 2),
        "q": px.btn(px.KEY_Q),
        "save": px.btnp(px.KEY_S, 10, 2),
    }


def save_json(path, data):
    Path(path).write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_json(path):
    p = Path(path)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))
