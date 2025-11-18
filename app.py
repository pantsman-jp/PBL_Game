"""
アプリケーションクラス | app.py
ウィンドウ初期化、サブモジュール生成、メインループを担当
シーン管理（タイトル／ゲーム本編）機能を追加
"""

import os
import sys
import pygame
from utils import KeyTracker
from core.system import System
from core.field import Field
from core.talk import Talk

# ウィンドウサイズ
WIDTH, HEIGHT = 900, 700
FPS = 60

# シーン定義
SCENE_TITLE = 0  # タイトル画面
SCENE_GAME = 1  # ゲーム本編


class App:
    def __init__(self):
        # pygame 初期化
        pygame.init()
        # サウンド初期化（短い効果音用）
        try:
            pygame.mixer.init()
        except Exception:
            # Mixer 初期化失敗してもクラッシュさせない
            pass
        # 効果音読み込み（存在しなければ None）
        sdir = os.path.join("sounds")

        def _load_sound(name):
            """
            効果音を読み込む補助関数(issa)
            """
            p = os.path.join(sdir, name)
            if os.path.isfile(p):
                try:
                    return pygame.mixer.Sound(p)
                except Exception:
                    return None
            return None

        self.sfx_inv_open = _load_sound("chestopen.mp3")
        self.sfx_inv_close = _load_sound("chestclose.mp3")

        self.key_tracker = KeyTracker()
        # --- BGM/SE 対応 ---
        # (シーン切り替え時に音楽を再生すると良いでしょう)
        # pygame.mixer.init()
        # ウィンドウ作成
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tiny Quiz Field - pygame")
        self.clock = pygame.time.Clock()
        # --- フォント設定 ---
        font_path = os.path.join("assets", "fonts", "NotoSansJP-Regular.otf")
        if os.path.isfile(font_path):
            self.font = pygame.font.Font(font_path, 16)
            self.title_font = pygame.font.Font(font_path, 32)  # タイトル用
            self.prompt_font = pygame.font.Font(font_path, 20)  # クリック誘導用
        else:
            self.font = pygame.font.SysFont("meiryo", 16)
            self.title_font = pygame.font.SysFont("meiryo", 32)
            self.prompt_font = pygame.font.SysFont("meiryo", 20)

        # --- タイトル画面アセット ---
        self.title_image = None
        title_img_path = os.path.join("img", "960.jpg")
        if os.path.isfile(title_img_path):
            self.title_image = pygame.image.load(title_img_path).convert()
        # --- ゲーム状態 (SCENE_GAME で使用) ---
        self.x = 8  # グリッド座標
        self.y = 8
        self.items = []
        self.inventory_open = False
        # --- サブシステム (SCENE_GAME で使用) ---
        self.system = System(self)
        self.field = Field(self)
        self.talk = Talk(self)
        # --- シーン管理 ---
        self.scene_state = SCENE_TITLE  # 初期シーンをタイトルに設定
        self.running = True

    def start_game(self):
        """
        ゲーム本編の初期化（セーブ読み込みなど）
        """
        # セーブデータ読み込み（存在すれば復元）
        self.system.load()
        self.scene_state = SCENE_GAME
        # --- 将来的に BGM 再生 ---
        # pygame.mixer.music.load(os.path.join("assets", "sounds", "bgm_field.ogg"))
        # pygame.mixer.music.play(-1)

    def run(self):
        """
        メインループを開始します
        """
        while self.running:
            # dt = self.clock.tick(FPS)
            self.clock.tick(FPS)  # FPS制御

            # シーンに応じて処理を分岐
            events = pygame.event.get()
            self._handle_events(events)
            self._update()
            self._draw()
            pygame.display.flip()
        pygame.quit()
        sys.exit()

    def _handle_events(self, events):
        """pygame イベント処理"""
        # --- 全シーン共通イベント ---
        for ev in events:
            if ev.type == pygame.QUIT:
                self.running = False
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.running = False  # ESCで終了

        # --- シーン別イベント ---
        if self.scene_state == SCENE_TITLE:
            for ev in events:
                # マウスクリックでゲーム開始
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    self.start_game()  # ゲーム本編の準備をしてシーン切り替え
        elif self.scene_state == SCENE_GAME:
            for ev in events:
                if ev.type == pygame.KEYDOWN:
                    # グローバルキー：Sでセーブ
                    if ev.key == pygame.K_s:
                        self.system.save()
                    # Iキーでインベントリ開閉
                    if ev.key == pygame.K_i:
                        self.inventory_open = not self.inventory_open
                        # 効果音を再生（存在すれば）
                        try:
                            if self.inventory_open and self.sfx_inv_open:
                                self.sfx_inv_open.play()
                            elif (not self.inventory_open) and self.sfx_inv_close:
                                self.sfx_inv_close.play()
                        except Exception:
                            pass

    def _update(self):
        """1フレームの更新"""

        # --- シーン別更新 ---
        if self.scene_state == SCENE_TITLE:
            # タイトル画面では特に更新処理なし (例: アニメーションなど)
            pass
        elif self.scene_state == SCENE_GAME:
            # (既存の更新処理)
            keys = self.key_tracker.update()  # 1フレーム押下検出
            self.talk.update(keys)
            if self.talk.is_active():
                return
            self.field.update(keys)

    def _draw(self):
        """画面描画"""
        # --- シーン別描画 ---
        if self.scene_state == SCENE_TITLE:
            # --- タイトル画面描画 ---
            if self.title_image:
                # 画像を中央に配置
                rect = self.title_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                self.screen.blit(self.title_image, rect)
            else:
                # 画像がない場合は背景色とタイトルテキスト
                self.screen.fill((20, 20, 40))  # 暗い青
                title_surf = self.title_font.render(
                    "Tiny Quiz Field", True, (255, 255, 255)
                )
                rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
                self.screen.blit(title_surf, rect)

            # クリック誘導テキスト (点滅)
            if pygame.time.get_ticks() % 1000 < 500:  # 0.5秒ごとに点滅
                prompt_surf = self.prompt_font.render(
                    "CLICK TO START", True, (255, 255, 200)
                )
                rect = prompt_surf.get_rect(center=(WIDTH // 2, HEIGHT - 80))
                self.screen.blit(prompt_surf, rect)

        elif self.scene_state == SCENE_GAME:
            # --- ゲーム本編描画 (既存の描画処理) ---
            self.screen.fill((50, 50, 80))  # 背景色
            self.field.draw(self.screen)

            # UI（所持アイテム）
            items_text = "ITEMS: " + ", ".join(self.items) if self.items else "ITEMS: -"
            surf = self.font.render(items_text, True, (255, 255, 255))
            self.screen.blit(surf, (8, 8))

            # 会話ウィンドウは talk.draw() が行う
            self.talk.draw(self.screen, self.font)

            # インベントリ表示（Iでトグル）-------------------
            if self.inventory_open:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                self.screen.blit(overlay, (0, 0))
                box_w, box_h = 480, 360
                bx = (WIDTH - box_w) // 2
                by = (HEIGHT - box_h) // 2
                pygame.draw.rect(self.screen, (30, 30, 40), (bx, by, box_w, box_h))
                pygame.draw.rect(
                    self.screen, (200, 200, 200), (bx, by, box_w, box_h), 2
                )
                title_surf = self.title_font.render(
                    "INVENTORY (I to close)", True, (255, 255, 255)
                )
                self.screen.blit(title_surf, (bx + 12, by + 8))
                # アイテムリスト描画
                for i, item in enumerate(self.items):
                    it_surf = self.font.render(f"- {item}", True, (220, 220, 220))
                    self.screen.blit(it_surf, (bx + 16, by + 48 + i * 22))
            # -----------------------------------------------
