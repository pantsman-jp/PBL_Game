import pyxel as px

TILE = 16
MOVE_SPEED = 2  # 移動スピード（px/frame）


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
        if dx != 0 or dy != 0:
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

    def draw(self):
        px.cls(3)
        # 背景グリッド描画
        for i in range(-1, 9):
            for j in range(-1, 9):
                x = i * TILE - self.offset * self.dx
                y = j * TILE - self.offset * self.dy
                color = 5 if (i + j) % 2 == 0 else 6
                px.rect(x, y, TILE - 1, TILE - 1, color)
        # プレイヤーを中央に固定して描画
        px.rect(56, 56, TILE, TILE, 11)
        # 情報バー
        px.rect(0, 0, 128, 8, 1)
        px.text(
            2, 1, f"X:{self.app.x} Y:{self.app.y} ITEMS:{','.join(self.app.items)}", 7
        )
