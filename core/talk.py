"""
会話・クイズ管理 | core/talk.py
dialogues.json を読み込み、Zで進行、Qで離脱、矢印で選択、正解で報酬を付与します．
"""

import os
from ui import draw_window
from utils import load_json


class Talk:
    def __init__(self, app):
        self.app = app
        self.dialogues = load_json(os.path.join("dialogues.json")) or {}
        self.active = None
        self.window_lines = []
        self.line_index = 0
        self.current_quiz = None
        self.quiz_mode = False
        self.quiz_choice = 0
        self.wait_frames = 0

    def update(self, keys):
        """会話とクイズの更新．Zで進行、Qで離脱、↑↓で選択"""
        if not (self.window_lines or self.quiz_mode or self.current_quiz):
            return

        if self.wait_frames > 0:
            self.wait_frames -= 1
            return

        if keys["q"]:
            self.window_lines = []
            self.current_quiz = None
            self.quiz_mode = False
            self.active = None
            return

        # --- クイズモード ---
        if self.quiz_mode and self.current_quiz:
            self._handle_quiz(keys)
            return

        # --- 通常会話モード ---
        if keys["z"]:
            self.line_index += 1
            if self.line_index < len(self.window_lines):
                pass
            else:
                # 全行終わった
                if self.current_quiz:
                    # ← 修正：会話終了時に window_lines を消してクイズ開始
                    self.window_lines = []
                    self.quiz_mode = True
                    self.quiz_choice = 0
                    self.wait_frames = 10
                else:
                    self.window_lines = []
                    self.active = None

    def draw(self, screen, font):
        """会話ウィンドウの描画"""
        # --- クイズ描画優先 ---
        if self.quiz_mode and self.current_quiz:
            q = self.current_quiz
            lines = [q.get("question", "")]
            for i, c in enumerate(q.get("choices", [])):
                prefix = ">" if i == self.quiz_choice else " "
                lines.append(f"{prefix} {i + 1}. {c}")
            draw_window(screen, font, lines)
            return

        # --- 通常会話描画 ---
        if self.window_lines:
            idx = min(self.line_index, max(0, len(self.window_lines) - 1))
            lines = [self.window_lines[idx]]
            draw_window(screen, font, lines)

    def try_talk(self):
        """プレイヤー位置に一致するNPCを探索し会話を開始する"""
        for key, data in self.dialogues.items():
            pos = data.get("position")
            if pos and (pos[0], pos[1]) == (self.app.x, self.app.y):
                self.active = key
                self.open_dialog(data)
                return

    def open_dialog(self, data):
        """会話開始処理：行インデックスを初期化して１行目を表示"""
        self.window_lines = data.get("lines", [])
        self.line_index = 0
        self.current_quiz = data.get("quiz")
        self.quiz_mode = False
        self.quiz_choice = 0
        self.wait_frames = 10  # ← 少し長めに設定（押しっぱなし防止）

    def is_active(self):
        """会話中かどうか"""
        return self.window_lines or self.quiz_mode

    def _handle_quiz(self, keys):
        q = self.current_quiz
        if keys["up"]:
            self.quiz_choice = (self.quiz_choice - 1) % len(q["choices"])
        elif keys["down"]:
            self.quiz_choice = (self.quiz_choice + 1) % len(q["choices"])
        elif keys["z"]:
            # 決定
            correct = q.get("answer", 0)
            if self.quiz_choice == correct:
                reward = q.get("reward")
                if reward and reward not in self.app.items:
                    self.app.items.append(reward)
                self.window_lines = ["Correct!", f"Reward: {reward}"]
            else:
                self.window_lines = ["Wrong.", f"Answer: {q['choices'][correct]}"]
            # クイズ終了
            self.current_quiz = None
            self.quiz_mode = False
            self.active = None
