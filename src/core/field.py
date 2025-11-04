"""
フィールド移動管理クラス | `src/core/field.py`

- プレイヤーの移動、背景のスクロール、描画を担当する
- 現在は簡易グリッド表示だが、将来的にアセット・BGM 対応可能
"""

import pyxel as px

TILE = 16
MOVE_SPEED = 2


class Field:
    def __init__(self, app):
        self.app = app
        self.moving = False
        self.dx = 0
        self.dy = 0
        self.offset = 0

    def update(self, btn):
        if self.moving:
            self.offset += MOVE_SPEED
            if self.offset >= TILE:
                self.offset = 0
                self.moving = False
                self.app.x += self.dx
                self.app.y += self.dy
            return

        dx = int(btn["r"]) - int(btn["l"])
        dy = int(btn["d"]) - int(btn["u"])
        if (dx != 0) or (dy != 0):
            self.start_move(dx, dy)
        elif btn["a"]:
            self.app.talk.try_talk()
        if btn["save"]:
            self.app.system.save()

    def start_move(self, dx, dy):
        self.dx = dx
        self.dy = dy
        self.moving = True
        self.offset = 0
        # 将来的に歩行SEを追加可能
        # px.play(3, 0)

    def draw(self):
        px.cls(3)

        # --- 背景タイル描画（仮） ---
        for i in range(-1, 9):
            for j in range(-1, 9):
                x = i * TILE - self.offset * self.dx
                y = j * TILE - self.offset * self.dy
                color = 5 if (i + j) % 2 == 0 else 6
                px.rect(x, y, TILE - 1, TILE - 1, color)

        # --- 将来的なアセット対応 ---
        # px.load("assets.pyxres") を app.py で有効化後に使用：
        # map_x = self.app.x * TILE - self.offset * self.dx
        # map_y = self.app.y * TILE - self.offset * self.dy
        # px.bltm(-map_x + 56, -map_y + 56, 0, 0, 0, 128, 128)

        # --- NPC描画 ---
        for [_, data] in self.app.talk.dialogues.items():
            pos = data.get("position")
            if not pos:
                continue
            nx, ny = pos[0], pos[1]
            screen_x = 56 + (nx - self.app.x) * TILE - self.offset * self.dx
            screen_y = 56 + (ny - self.app.y) * TILE - self.offset * self.dy

            # 現在は単色矩形（NPC）
            px.rect(screen_x, screen_y, TILE, TILE, 8)

            # --- 将来的にスプライト対応 ---
            # px.blt(screen_x, screen_y, 0, 16, 0, 16, 16, 0)

        # --- プレイヤー描画 ---
        px.rect(56, 56, TILE, TILE, 11)

        # --- 将来的にプレイヤースプライト化 ---
        # px.blt(56, 56, 0, 0, 0, 16, 16, 0)

        # --- 情報バー ---
        px.rect(0, 0, 128, 8, 1)
        px.text(
            2, 1, f"X:{self.app.x} Y:{self.app.y} ITEMS:{','.join(self.app.items)}", 7
        )
