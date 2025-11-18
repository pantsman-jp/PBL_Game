"""
フィールド管理 | core/field.py
グリッド移動と NPC の描画を担当します．
"""

import pygame
import os

# グリッドと画面描画設定
TILE = 32  # 1マスのサイズ（ピクセル）
GRID_W = 16  # 横マス数（論理）
GRID_H = 12  # 縦マス数（論理）
SCREEN_CENTER_X = 320
SCREEN_CENTER_Y = 200  # プレイヤーを中心よりやや上に配置


class Field:
    def __init__(self, app):
        self.app = app
        # 移動アニメーション用
        self.moving = False
        self.dx = 0
        self.dy = 0
        self.offset = 0
        self.speed = 1  # px/frame
        # 全体マップ（世界地図）アセット
        self.map_image = None
        map_img_path = os.path.join("img", "world_map.png")
        if os.path.isfile(map_img_path):
            self.map_image = pygame.image.load(map_img_path).convert()

    def update(self, keys):
        """移動の入力とアニメーション処理"""
        if self.moving:
            self.offset += self.speed
            if self.offset >= TILE:
                # 移動完了
                self.offset = 0
                self.moving = False
                self.app.x += self.dx
                self.app.y += self.dy
            return

        # 入力を受けて移動開始
        if keys["up"]:
            self.start_move(0, -1)
        elif keys["down"]:
            self.start_move(0, 1)
        elif keys["left"]:
            self.start_move(-1, 0)
        elif keys["right"]:
            self.start_move(1, 0)
        elif keys["z"]:
            # Zで会話（会話開始は talk.try_talk() 内で位置照合）
            self.app.talk.try_talk()

    def start_move(self, dx, dy):
        """移動開始処理．背景画像の範囲外に出ないように制限します．"""
        # 背景マップのタイル数を算出
        map_w = self.map_image.get_width() // TILE
        map_h = self.map_image.get_height() // TILE

        # 目的地タイル座標
        nx = self.app.x + dx
        ny = self.app.y + dy

        # 範囲外なら移動しない
        if nx < 0 or ny < 0 or nx >= map_w or ny >= map_h:
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
