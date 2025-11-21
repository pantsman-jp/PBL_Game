"""
システム管理 | src/core/system.py
セーブ/ロードおよび将来的なBGM制御用フックを提供
"""

from ..utils import save_json, load_json, SAVEFILE
# pygame mixer を使う場合の参考（コメントアウト）
# import pygame


class System:
    """
    ゲームシステム管理クラス
    - セーブ/ロード
    - BGM制御（将来的なフック）
    """

    def __init__(self, app):
        self.app = app
        self.savefile = SAVEFILE  # 保存ファイルパス

    def save(self):
        """
        ゲーム状態を保存
        """
        data = {"x": self.app.x, "y": self.app.y, "items": self.app.items}
        save_json(self.savefile, data)
        print("Saved:", self.savefile)

    def load(self):
        """
        ゲーム状態をロード
        """
        data = load_json(self.savefile)
        if data:
            self.app.x = data.get("x", self.app.x)
            self.app.y = data.get("y", self.app.y)
            self.app.items = data.get("items", [])
            print("Loaded save:", self.savefile)
            return True
        return False

    def play_bgm(self, path):
        """
        BGM再生フック（将来的使用）
        path: 音楽ファイルパス
        """
        # pygame.mixer.music.load(path)
        # pygame.mixer.music.play(-1)
        pass

    def stop_bgm(self):
        """
        BGM停止フック（将来的使用）
        """
        # pygame.mixer.music.stop()
        pass
