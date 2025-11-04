"""
システム管理 | core/system.py
セーブ／ロードと将来的なBGM制御用フックを提供します．
"""

from utils import save_json, load_json, SAVEFILE
# pygame mixer を使う場合の参考（コメントアウト）
# import pygame


class System:
    def __init__(self, app):
        self.app = app
        self.savefile = SAVEFILE

    def save(self):
        data = {"x": self.app.x, "y": self.app.y, "items": self.app.items}
        save_json(self.savefile, data)
        print("Saved:", self.savefile)

    def load(self):
        data = load_json(self.savefile)
        if data:
            self.app.x = data.get("x", self.app.x)
            self.app.y = data.get("y", self.app.y)
            self.app.items = data.get("items", [])
            print("Loaded save:", self.savefile)
            return True
        return False

    # 将来のBGM制御フック（コメントアウト）
    def play_bgm(self, path):
        # pygame.mixer.music.load(path)
        # pygame.mixer.music.play(-1)
        pass

    def stop_bgm(self):
        # pygame.mixer.music.stop()
        pass
