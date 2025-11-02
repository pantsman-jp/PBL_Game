import pyxel as px
from utils import get_btn_state
from core.system import System
from core.field import Field
from core.talk import Talk


class App:
    def __init__(self):
        px.init(128, 128, title="Tiny Quiz Field", display_scale=2)
        self.x = 8
        self.y = 8
        self.items = []
        self.system = System(self)
        self.field = Field(self)
        self.talk = Talk(self)
        self.system.load()
        px.run(self.update, self.draw)

    def update(self):
        btn = get_btn_state()
        # 先に会話更新を行う．会話中は移動を抑止する
        self.talk.update(btn)
        if self.talk.window:
            return
        self.field.update(btn)

    def draw(self):
        self.field.draw()
        self.talk.draw()
