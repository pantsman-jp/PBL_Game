"""
会話・クイズ管理クラス | `src/core/talk.py`

- 外部 JSON (`src/dialogues.json`) の内容を読み込み、プレイヤー位置に応じた会話・クイズを制御する。
- 将来的に BGM 切り替えや SE 追加も可能
"""

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
        """
        プレイヤー位置にNPCが存在すれば会話を開始。
        """
        for key, data in self.dialogues.items():
            pos = tuple(data.get("position", []))
            if pos and (pos[0], pos[1]) == (self.app.x, self.app.y):
                self.active = key
                self.open_dialog(data)
                return

    def open_dialog(self, data):
        """
        会話開始時のウィンドウ生成。
        """
        lines = data.get("lines", [""])
        self.window = Window(lines)

        # --- 将来的にBGM切り替えを追加したい場合 ---
        # たとえば会話開始で専用BGMを再生する：
        # self.app.system.play_bgm(track_id=1)

        quiz = data.get("quiz")
        if quiz:
            self.quiz_mode = False
            self.current_quiz = quiz

    def update(self, btn):
        """
        会話／クイズの更新処理。
        """
        if not self.window:
            return

        # --- クイズモード ---
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
                    self.window = Window(["Correct!", f"Reward: {reward}"])

                    # --- 将来的に正解SEを再生 ---
                    # px.play(3, 2)

                else:
                    self.window = Window(
                        ["Uncorrect!", f"Ans is: {q.get('choices', [])[correct]}"]
                    )

                    # --- 将来的に不正解SEを再生 ---
                    # px.play(3, 3)

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

        # --- 通常会話モード ---
        if btn["q"]:
            # 会話終了時にBGMを戻す?
            # self.app.system.play_bgm(track_id=0)
            self.window = None
            self.active = None

    def draw(self):
        """
        現在のウィンドウを描画する。
        """
        if self.window:
            self.window.draw()
