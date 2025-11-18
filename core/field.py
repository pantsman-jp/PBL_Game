"""
フィールド管理 | core/field.py
プレイヤー移動、NPC 描画、マップ遷移、画面遷移時アニメーション
"""

import pygame
import os
import math

TILE = 12
SCREEN_CENTER_X = 320
SCREEN_CENTER_Y = 200


class Field:
    def __init__(self, app):
        self.app = app
        self.moving = False
        self.dx = 0
        self.dy = 0
        self.offset = 0
        self.speed = 4
        self.map_image = None
        self.transitioning = False
        self.transition_radius = 0
        self.transition_target = None
        self._transition_stage = None
        self.transition_max_radius = math.hypot(SCREEN_CENTER_X, SCREEN_CENTER_Y)
        self.transition_speed = 4  # ゆっくりに設定
        self.load_map("img/world_map.png")

    def update(self, keys):
        if self.transitioning:
            self._update_transition()
            return

        if self.moving:
            self.offset += self.speed
            if self.offset >= TILE:
                self.offset = 0
                self.moving = False
                self.app.x += self.dx
                self.app.y += self.dy
                self._check_transition_trigger()
            return

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_UP]:
            self.start_move(0, -1)
        elif pressed[pygame.K_DOWN]:
            self.start_move(0, 1)
        elif pressed[pygame.K_LEFT]:
            self.start_move(-1, 0)
        elif pressed[pygame.K_RIGHT]:
            self.start_move(1, 0)
        elif keys.get("z"):
            self.app.talk.try_talk()

    def start_move(self, dx, dy):
        nx = self.app.x + dx
        ny = self.app.y + dy
        if nx < 0 or ny < 0 or nx >= self.map_w or ny >= self.map_h:
            return
        self.dx = dx
        self.dy = dy
        self.moving = True
        self.offset = 0

    def draw(self, screen):
        ox = self.offset * (-self.dx)
        oy = self.offset * (-self.dy)
        base_x = SCREEN_CENTER_X - self.app.x * TILE
        base_y = SCREEN_CENTER_Y - self.app.y * TILE
        screen.blit(self.map_image, (base_x + ox, base_y + oy))

        for [_, data] in self.app.talk.dialogues.items():
            pos = data.get("position")
            if not pos:
                continue
            nx, ny = pos[0], pos[1]
            screen_x = SCREEN_CENTER_X + (nx - self.app.x) * TILE + ox
            screen_y = SCREEN_CENTER_Y + (ny - self.app.y) * TILE + oy
            pygame.draw.rect(screen, (200, 120, 80), (screen_x, screen_y, TILE, TILE))
            label = data.get("lines", [""])[0]
            label_surf = self.app.font.render(label[:12], True, (255, 255, 255))
            screen.blit(label_surf, (screen_x, screen_y - 18))

        px = SCREEN_CENTER_X
        py = SCREEN_CENTER_Y
        pygame.draw.rect(screen, (120, 200, 240), (px, py, TILE, TILE))

        # アイリスアウト/イン描画
        if self.transitioning:
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 255))
            # 円形を透明にする
            pygame.draw.circle(
                overlay,
                (0, 0, 0, 0),
                (SCREEN_CENTER_X, SCREEN_CENTER_Y),
                int(self.transition_radius),
            )
            screen.blit(overlay, (0, 0))

    def _check_transition_trigger(self):
        if self.app.x == 0 and self.app.y == 0:
            self._start_transition("img/transition.jpg")

    def _start_transition(self, path):
        if not os.path.isfile(path):
            return
        self.transitioning = True
        self.transition_radius = self.transition_max_radius
        self.transition_target = path
        self._transition_stage = "out"

    def _update_transition(self):
        if self._transition_stage == "out":
            self.transition_radius -= self.transition_speed
            if self.transition_radius <= 0:
                self.load_map(self.transition_target)
                self.app.x = self.map_w // 2
                self.app.y = self.map_h // 2
                self.transition_radius = 0
                self._transition_stage = "in"
        elif self._transition_stage == "in":
            self.transition_radius += self.transition_speed
            if self.transition_radius >= self.transition_max_radius:
                self.transition_radius = self.transition_max_radius
                self.transitioning = False
                self._transition_stage = None

    def load_map(self, path):
        if os.path.isfile(path):
            self.map_image = pygame.image.load(path).convert()
            w, h = self.map_image.get_size()
            self.map_w = w // TILE
            self.map_h = h // TILE
        else:
            self.map_image = None
            self.map_w = 0
            self.map_h = 0
