"""
システム管理クラス | `src/core/system.py`

- セーブ・ロード処理など、ゲーム状態全体を扱う
- 将来的に、アセットや BGM 管理を担当する。
"""

from utils import save_json, load_json


class System:
    def __init__(self, app):
        self.app = app
        self.savefile = "save.json"
        self.current_bgm = None  # 現在再生中のBGMトラック番号

    def save(self):
        """
        プレイヤー位置と所持アイテムを保存。
        """
        save_json(
            self.savefile, {"x": self.app.x, "y": self.app.y, "items": self.app.items}
        )

    def load(self):
        """
        保存データを読み込んで復元。
        """
        data = load_json(self.savefile)
        if data:
            self.app.x = data.get("x", self.app.x)
            self.app.y = data.get("y", self.app.y)
            self.app.items = data.get("items", [])
            return True
        return False

    # --- 将来的なBGM再生対応部分 ---
    def play_bgm(self, track_id):
        """
        指定されたトラックを繰り返し再生する。
        `assets.pyxres` に音楽データを追加した後に利用可能。
        """
        if self.current_bgm != track_id:
            # 例: BGM番号を track_id として再生
            # px.playm(track_id, loop=True)
            self.current_bgm = track_id

    def stop_bgm(self):
        """
        現在のBGMを停止する(将来用)
        """
        # px.stop()
        self.current_bgm = None
