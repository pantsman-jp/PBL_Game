"""
アプリケーションクラス（ゲーム本体） | `src/app.py`

- Pyxel初期化、BGM再生管理、サブモジュール連携を担当
"""

import pyxel as px
from utils import get_btn_state
from core.system import System
from core.field import Field
from core.talk import Talk


class App:
    def __init__(self):
        # 画面初期化
        px.init(128, 128, title="Tiny Quiz Field", display_scale=2)

        # --- 将来的なアセット/BGM対応 ---
        # assets.pyxres にタイルや音楽を登録した後、有効化する：
        # px.load("assets.pyxres")
        # self.system.play_bgm(0)  # フィールドBGM開始

        # プレイヤー初期化
        self.x = 8
        self.y = 8
        self.items = []

        # サブシステム初期化
        self.system = System(self)
        self.field = Field(self)
        self.talk = Talk(self)

        # セーブデータ読み込み
        self.system.load()

        # メインループ開始
        px.run(self.update, self.draw)

    def update(self):
        """
        1フレームごとの更新処理。
        """
        btn = get_btn_state()
        self.talk.update(btn)
        if self.talk.window:
            return
        self.field.update(btn)

    def draw(self):
        """
        1フレームごとの描画処理。
        """
        self.field.draw()
        self.talk.draw()
