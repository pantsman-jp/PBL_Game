from utils import save_json, load_json


class System:
    def __init__(self, app):
        self.app = app
        self.savefile = "save.json"

    def save(self):
        data = {"x": self.app.x, "y": self.app.y, "items": self.app.items}
        save_json(self.savefile, data)

    def load(self):
        data = load_json(self.savefile)
        if data:
            self.app.x = data.get("x", self.app.x)
            self.app.y = data.get("y", self.app.y)
            self.app.items = data.get("items", [])
            return True
        return False
