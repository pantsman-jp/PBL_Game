"""
汎用ユーティリティ関数群 | `src/utils.py`

- JSONの読み書きと、キー入力状態の取得を担当する。
"""

import json
from pathlib import Path
import pyxel as px


def get_btn_state():
    """
    現在のキー入力状態を辞書で返す。
    各キーは True/False で表現される。
    """
    return {
        "u": px.btn(px.KEY_UP),  # 上
        "d": px.btn(px.KEY_DOWN),  # 下
        "l": px.btn(px.KEY_LEFT),  # 左
        "r": px.btn(px.KEY_RIGHT),  # 右
        "a": px.btnp(px.KEY_Z, 10, 2),  # 決定/会話（Zキー）
        "q": px.btnp(px.KEY_Q),  # 会話離脱
        "save": px.btnp(px.KEY_S, 10, 2),  # セーブ（Sキー）
    }


def save_json(path, data):
    """
    JSON形式で辞書データを保存する。
    """
    Path(path).write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_json(path):
    """
    JSONファイルを読み込み、辞書として返す。
    ファイルが存在しない場合は None を返す。
    """
    p = Path(path)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))
