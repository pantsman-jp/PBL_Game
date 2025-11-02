import pyxel as px


class Window:
    def __init__(self, lines):
        self.lines = lines

    def draw(self):
        px.rect(8, 80, 112, 40, 0)  # 背景
        for i, line in enumerate(self.lines):
            px.text(12, 84 + i * 8, line, 7)
