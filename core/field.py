"""
フィールド管理 | core/field.py
グリッド移動と NPC の描画を担当します．
"""

import pygame
import os

# グリッドと画面描画設定
TILE = 12  # 1マスのサイズ（ピクセル）
GRID_W = 1000  # 横マス数
GRID_H = 800  # 縦マス数
SCREEN_CENTER_X = 320
SCREEN_CENTER_Y = 200  # プレイヤーを中心よりやや上に配置


class Field:
    def __init__(self, app):
        self.app = app
        self.moving = False
        self.dx = 0
        self.dy = 0
        self.offset = 0
        self.speed = 4 #1フレームあたりに移動するピクセルの数
        self.map_image = None
        self.load_map("img/world_map.png")

    def update(self, keys):
        if self.moving:
            self.offset += self.speed
            if self.offset >= TILE:
                self.offset = 0
                self.moving = False
                self.app.x += self.dx
                self.app.y += self.dy

                # ---- 画面遷移判定 ----
                if (self.app.x == 0) and (self.app.y == 0):
                    self.load_map("img/transition.jpg")
                    self.app.x = self.map_w // 2
                    self.app.y = self.map_h // 2
                # -----------------------
            return

        # 長押しで連続移動させるため、ここではpygame.key.get_pressed()を用いて
        # 押下保持（held）を判定する。会話zは単押しのままkeys["z"]
        pressed = pygame.key.get_pressed()
        up = pressed[pygame.K_UP]
        down = pressed[pygame.K_DOWN]
        left = pressed[pygame.K_LEFT]
        right = pressed[pygame.K_RIGHT]

        if up:
            self.start_move(0, -1)
        elif down:
            self.start_move(0, 1)
        elif left:
            self.start_move(-1, 0)
        elif right:
            self.start_move(1, 0)
        elif keys.get("z"):
            self.app.talk.try_talk()

    def start_move(self, dx, dy):
        """
        移動開始処理．
        背景画像の範囲外に出ないように制限します．
        """
        # 背景マップのタイル数を算出
        map_w = self.map_image.get_width() // TILE
        map_h = self.map_image.get_height() // TILE
        # 目的地タイル座標
        nx = self.app.x + dx
        ny = self.app.y + dy
        # 範囲外なら移動しない
        if (nx < 0) or (ny < 0) or (nx >= map_w) or (ny >= map_h):
            return
        # 範囲内なら移動開始
        self.dx = dx
        self.dy = dy
        self.moving = True
        self.offset = 0

    def draw(self, screen):
        """
        背景マップ、NPC、プレイヤーの描画します。
        プレイヤー移動中のスクロール量を全描画物に一貫して適用し、
        かくつきを防止。
        """
        # プレイヤー移動方向に応じたスクロール量を算出
        ox = self.offset * (-self.dx)
        oy = self.offset * (-self.dy)

        # 背景マップの基準位置を算出
        base_x = SCREEN_CENTER_X - self.app.x * TILE
        base_y = SCREEN_CENTER_Y - self.app.y * TILE

        # 背景マップをスクロール量を加えて描画
        screen.blit(self.map_image, (base_x + ox, base_y + oy))

        # NPC を全て描画
        for [_, data] in self.app.talk.dialogues.items():
            pos = data.get("position")
            if not pos:
                continue

            nx, ny = pos[0], pos[1]

            # NPC のスクリーン座標を算出
            screen_x = SCREEN_CENTER_X + (nx - self.app.x) * TILE + ox
            screen_y = SCREEN_CENTER_Y + (ny - self.app.y) * TILE + oy

            # NPC を描画
            pygame.draw.rect(screen, (200, 120, 80), (screen_x, screen_y, TILE, TILE))

            # NPC のラベルを描画
            label = data.get("lines", [""])[0]
            label_surf = self.app.font.render(label[:12], True, (255, 255, 255))
            screen.blit(label_surf, (screen_x, screen_y - 18))

        # プレイヤーをスクリーン中央に描画
        px = SCREEN_CENTER_X
        py = SCREEN_CENTER_Y
        pygame.draw.rect(screen, (120, 200, 240), (px, py, TILE, TILE))

    def load_map(self, path):
        if os.path.isfile(path):
            self.map_image = pygame.image.load(path).convert()
            w, h = self.map_image.get_width(), self.map_image.get_height()
            self.map_w = w // TILE
            self.map_h = h // TILE
        else:
            self.map_image = None
            self.map_w = 0
            self.map_h = 0
