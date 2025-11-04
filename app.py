"""
アプリケーションクラス（pygame版） | app.py
ウィンドウ初期化、サブモジュール生成、メインループを担当します．
"""

import os
import sys
import pygame
from utils import KeyTracker
from core.system import System
from core.field import Field
from core.talk import Talk

# ウィンドウサイズ
WIDTH, HEIGHT = 640, 480
FPS = 60


class App:
    def __init__(self):
        # pygame 初期化
        pygame.init()
        self.key_tracker = KeyTracker()
        # --- 将来的な BGM/SE 対応 ---
        # pygame.mixer.init()
        # pygame.mixer.music.load(os.path.join("assets", "bgm_field.ogg"))
        # pygame.mixer.music.play(-1)

        # ウィンドウ作成
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tiny Quiz Field - pygame")
        self.clock = pygame.time.Clock()

        # フォント設定（TTFがあるならそちらを優先）
        # フォントファイルを用意していれば paths に置いてください
        font_path = os.path.join("fonts", "NotoSansJP-Regular.otf")
        if os.path.isfile(font_path):
            self.font = pygame.font.Font(font_path, 16)
        else:
            self.font = pygame.font.SysFont("meiryo", 16)

        # ゲーム状態
        self.x = 8  # グリッド座標
        self.y = 8
        self.items = []

        # サブシステム
        self.system = System(self)
        self.field = Field(self)
        self.talk = Talk(self)

        # セーブデータ読み込み（存在すれば復元）
        self.system.load()

        # 内部フラグ
        self.running = True

    def run(self):
        """メインループを開始します"""
        while self.running:
            # dt = self.clock.tick(FPS)
            self._handle_events()
            self._update()
            self._draw()
            pygame.display.flip()
        pygame.quit()
        sys.exit()

    def _handle_events(self):
        """pygame イベント処理"""
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.running = False
            elif ev.type == pygame.KEYDOWN:
                # グローバルキー：Sでセーブ
                if ev.key == pygame.K_s:
                    self.system.save()
                # ESCで終了
                if ev.key == pygame.K_ESCAPE:
                    self.running = False

    def _update(self):
        """1フレームの更新"""
        keys = self.key_tracker.update()  # ← 変更：1フレーム押下検出
        self.talk.update(keys)
        if self.talk.is_active():
            return
        self.field.update(keys)

    def _draw(self):
        """画面描画"""
        self.screen.fill((50, 50, 80))  # 背景色
        self.field.draw(self.screen)
        # UI（所持アイテム）
        items_text = "ITEMS: " + ", ".join(self.items) if self.items else "ITEMS: -"
        surf = self.font.render(items_text, True, (255, 255, 255))
        self.screen.blit(surf, (8, 8))
        # 会話ウィンドウは talk.draw() が行う
        self.talk.draw(self.screen, self.font)
