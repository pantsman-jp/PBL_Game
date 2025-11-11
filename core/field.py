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
        self.speed = 0.5  # px/frame
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
        # 簡易に衝突判定なしで移動を開始
        self.dx = dx
        self.dy = dy
        self.moving = True
        self.offset = 0
        # 将来的に歩行SE
        # pygame.mixer.Sound("walk.wav").play()

    def draw(self, screen):
        """背景グリッド、NPC、プレイヤーを描画"""
        # 背景グリッド
        # 世界地図を背景として描画
        # プレイヤー位置を中心にマップをスクロール
        # （self.app.x, self.app.y はプレイヤーのワールド座標）
        offset_x = SCREEN_CENTER_X - self.app.x * TILE
        offset_y = SCREEN_CENTER_Y - self.app.y * TILE
        # マップをスクロール描画
        screen.blit(self.map_image, (offset_x, offset_y))

        # NPC描画：dialogues.json にある position を元に描画
        for [_, data] in self.app.talk.dialogues.items():
            pos = data.get("position")
            if not pos:
                continue
            nx, ny = pos[0], pos[1]
            # ワールド座標 -> スクリーン座標（プレイヤーを中心に）
            screen_x = SCREEN_CENTER_X + (nx - self.app.x) * TILE
            screen_y = (
                SCREEN_CENTER_Y
                + (ny - self.app.y) * TILE
                - (self.offset if self.dy > 0 else 0)
            )
            # 単色矩形でNPCを表示（将来はスプライトに差し替え）
            pygame.draw.rect(screen, (200, 120, 80), (screen_x, screen_y, TILE, TILE))
            # NPCのラベル（1行目表示）
            label = data.get("lines", [""])[0]
            label_surf = self.app.font.render(label[:12], True, (255, 255, 255))
            screen.blit(label_surf, (screen_x, screen_y - 18))

        # プレイヤー描画（中央）
        px = SCREEN_CENTER_X
        py = SCREEN_CENTER_Y
        pygame.draw.rect(screen, (120, 200, 240), (px, py, TILE, TILE))
