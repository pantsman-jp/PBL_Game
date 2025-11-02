from ui import Window
from utils import load_json


class Talk:
    def __init__(self, app):
        self.app = app
        self.dialogues = load_json("dialogues.json") or {}
        self.active = None
        self.window = None
        self.quiz_mode = False
        self.quiz_choice = 0

    def try_talk(self):
        for key, data in self.dialogues.items():
            pos = tuple(data.get("position", []))
            if pos and (pos[0], pos[1]) == (self.app.x, self.app.y):
                self.active = key
                self.open_dialog(data)
                return

    def open_dialog(self, data):
        lines = data.get("lines", [""])
        self.window = Window(lines)
        quiz = data.get("quiz")
        if quiz:
            self.quiz_mode = False
            self.current_quiz = quiz

    def update(self, btn):
        if not self.window:
            return
        if hasattr(self, "current_quiz") and self.current_quiz:
            if not self.quiz_mode:
                self.quiz_mode = True
                q = self.current_quiz
                lines = [q.get("question", "")]
                lines += [f"{i + 1}. {c}" for i, c in enumerate(q.get("choices", []))]
                self.window = Window(lines)
                return
            q = self.current_quiz
            if btn["u"]:
                self.quiz_choice = (self.quiz_choice - 1) % len(q.get("choices", []))
            elif btn["d"]:
                self.quiz_choice = (self.quiz_choice + 1) % len(q.get("choices", []))
            elif btn["a"]:
                correct = q.get("answer", 0)
                if self.quiz_choice == correct:
                    reward = q.get("reward")
                    if reward and reward not in self.app.items:
                        self.app.items.append(reward)
                    self.window = Window(["Yes", f"reward: {reward}"])
                else:
                    self.window = Window(
                        ["Oops", f"the correct ans is: {q.get('choices', [])[correct]}"]
                    )
                self.current_quiz = None
                self.active = None
                self.quiz_mode = False
                self.quiz_choice = 0
                return
            choices = q.get("choices", [])
            lines = [q.get("question", "")]
            for i, c in enumerate(choices):
                prefix = ">" if i == self.quiz_choice else " "
                lines.append(f"{prefix} {i + 1}. {c}")
            self.window = Window(lines)
            return
        if btn["q"]:
            self.window = None
            self.active = None

    def draw(self):
        if self.window:
            self.window.draw()
