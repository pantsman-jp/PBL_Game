"""
アプリケーションクラス（ゲーム本体） | `src/app.py`
Pyxel初期化、BGM再生管理、サブモジュール連携を担当。
"""

import os
import pyxel as px
from utils import get_btn_state
from core.system import System
from core.field import Field
from core.talk import Talk


class App:
    def __init__(self):
        # --- フォント設定（Pyxel 1.x 系用） ---
        os.environ["PYXEL_FONT"] = "k8x12S.bdf"

        # --- Pyxel初期化 ---
        px.init(128, 128, title="Tiny Quiz Field", display_scale=2)

        # --- 将来的なアセット/BGM対応 ---
        # px.load("assets.pyxres")
        # self.system.play_bgm(0)

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
        btn = get_btn_state()
        self.talk.update(btn)
        if self.talk.window:
            return
        self.field.update(btn)

    def draw(self):
        self.field.draw()
        self.talk.draw()
