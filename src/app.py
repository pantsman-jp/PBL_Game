"""
アプリケーションクラス | src/app.py
ウィンドウ初期化、サブモジュール生成、メインループを担当
"""

import os
import sys
import pygame
from .utils import KeyTracker
from .core.system import System
from .core.field import Field
from .core.talk import Talk

WIDTH, HEIGHT = 900, 700
FPS = 60

SCENE_TITLE = 0
SCENE_GAME = 1

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))


class App:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except Exception:
            pass

        sdir = os.path.join(BASE_DIR, "sounds")

        def _load_sound(name):
            p = os.path.join(sdir, name)
            if os.path.isfile(p):
                try:
                    return pygame.mixer.Sound(p)
                except Exception:
                    return None
            return None

        self.sfx_inv_open = _load_sound("chestopen.mp3")
        self.sfx_inv_close = _load_sound("chestclese.mp3")

        # サウンドの ON/OFF 管理フラグ
        self.sound_enabled = True
        # 初期ボリュームを設定
        try:
            self._set_volume(1.0)
        except Exception:
            pass

        self.key_tracker = KeyTracker()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tiny Quiz Field - pygame")
        self.clock = pygame.time.Clock()

        font_path = os.path.join(BASE_DIR, "fonts", "NotoSansJP-Regular.otf")
        if os.path.isfile(font_path):
            self.font = pygame.font.Font(font_path, 16)
            self.title_font = pygame.font.Font(font_path, 32)
            self.prompt_font = pygame.font.Font(font_path, 20)
        else:
            self.font = pygame.font.SysFont("meiryo", 16)
            self.title_font = pygame.font.SysFont("meiryo", 32)
            self.prompt_font = pygame.font.SysFont("meiryo", 20)

        title_img_path = os.path.join(BASE_DIR, "img", "title.jpg")
        self.title_image = (
            pygame.image.load(title_img_path).convert()
            if os.path.isfile(title_img_path)
            else None
        )

        self.x = 8
        self.y = 8
        self.items = []
        self.inventory_open = False

        self.system = System(self)
        self.field = Field(self)
        self.talk = Talk(self)

        self.scene_state = SCENE_TITLE
        self.running = True

    def start_game(self):
        self.system.load()
        self.scene_state = SCENE_GAME

    def _set_volume(self, vol: float):
        """内部: ロード済みのサウンドと music のボリュームを設定する。"""
        try:
            if pygame.mixer.get_init():
                if self.sfx_inv_open:
                    self.sfx_inv_open.set_volume(vol)
                if self.sfx_inv_close:
                    self.sfx_inv_close.set_volume(vol)
                try:
                    pygame.mixer.music.set_volume(vol)
                except Exception:
                    pass
        except Exception:
            pass

    def toggle_sound(self):
        """サウンドの ON/OFF を切り替える。Mキーで呼び出す。"""
        self.sound_enabled = not self.sound_enabled
        try:
            self._set_volume(1.0 if self.sound_enabled else 0.0)
        except Exception:
            pass

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            events = pygame.event.get()
            self._handle_events(events)
            self._update()
            self._draw()
            pygame.display.flip()
        pygame.quit()
        sys.exit()

    def _handle_events(self, events):
        for ev in events:
            if ev.type == pygame.QUIT:
                self.running = False
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.running = False

        if self.scene_state == SCENE_TITLE:
            for ev in events:
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    self.start_game()
        elif self.scene_state == SCENE_GAME:
            for ev in events:
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_s:
                        self.system.save()
                    # サウンドのトグル（Mキー）
                    if ev.key == pygame.K_m:
                        self.toggle_sound()
                    if ev.key == pygame.K_i:
                        self.inventory_open = not self.inventory_open
                        try:
                            # サウンドが有効なときのみ効果音を鳴らす
                            if self.inventory_open and self.sfx_inv_open and self.sound_enabled:
                                self.sfx_inv_open.play()
                            elif (
                                not self.inventory_open and self.sfx_inv_close and self.sound_enabled
                            ):
                                self.sfx_inv_close.play()
                        except Exception:
                            pass

    def _update(self):
        if self.scene_state == SCENE_TITLE:
            pass
        elif self.scene_state == SCENE_GAME:
            keys = self.key_tracker.update()
            self.talk.update(keys)
            if self.talk.is_active():
                return
            self.field.update(keys)

    def _draw(self):
        if self.scene_state == SCENE_TITLE:
            if self.title_image:
                rect = self.title_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                self.screen.blit(self.title_image, rect)
            else:
                self.screen.fill((20, 20, 40))
                title_surf = self.title_font.render(
                    "Tiny Quiz Field", True, (255, 255, 255)
                )
                rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
                self.screen.blit(title_surf, rect)

            if pygame.time.get_ticks() % 1000 < 500:
                prompt_surf = self.prompt_font.render(
                    "CLICK TO START", True, (255, 255, 200)
                )
                rect = prompt_surf.get_rect(center=(WIDTH // 2, HEIGHT - 80))
                self.screen.blit(prompt_surf, rect)
        elif self.scene_state == SCENE_GAME:
            self.screen.fill((50, 50, 80))
            self.field.draw(self.screen)
            items_text = "ITEMS: " + ", ".join(self.items) if self.items else "ITEMS: -"
            surf = self.font.render(items_text, True, (255, 255, 255))
            self.screen.blit(surf, (8, 8))
            # サウンド状態を表示
            sound_text = "SOUND: ON" if self.sound_enabled else "SOUND: OFF"
            sound_surf = self.font.render(sound_text, True, (200, 200, 200))
            self.screen.blit(sound_surf, (8, 32))
            self.talk.draw(self.screen, self.font)

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
                for i, item in enumerate(self.items):
                    it_surf = self.font.render(f"- {item}", True, (220, 220, 220))
                    self.screen.blit(it_surf, (bx + 16, by + 48 + i * 22))
