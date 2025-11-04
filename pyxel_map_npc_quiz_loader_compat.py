# -*- coding: utf-8 -*-
"""
scenario_romaji.json を読み込み、
マップ上のNPCへの話しかけ → 会話 → クイズ → 判定 → 報酬付与
まで実装した Pyxel ローダー（互換性さらに強化版）。

ポイント:
- キー名の差異: KEY_EQUAL/KEY_EQUALS, KEY_RETURN/KEY_ENTER 等に両対応
- btnp(): 位置引数のみ利用し、TypeError時は段階的フォールバック（古いPyxel互換）
- 標準フォントはASCIIのみのため、日本語は '·' で仮表示（実運用は画像フォント推奨）

実行:
    pip install pyxel==2.5.9
    python pyxel_map_npc_quiz_loader_compat.py
"""

from typing import List, Optional, Dict, Any
import json
import pyxel


# ---------------- ユーティリティ（キー互換） ----------------
def get_key(name: str) -> Optional[int]:
    """Pyxelのキー定数を安全に取得（存在しなければNone）"""
    return getattr(pyxel, name, None)


def btn(name: str) -> int:
    """pyxel.btn のラッパー（キーが無ければ 0）"""
    k = get_key(name)
    return pyxel.btn(k) if k is not None else 0


def btnp_key(
    key: Optional[int], hold: Optional[int] = None, period: Optional[int] = None
) -> bool:
    """
    btnp の安全呼び出し（位置引数のみ使用）。
    引数数やシグネチャが合わない環境でも TypeError を避ける。
    """
    if key is None:
        return False
    try:
        if hold is None and period is None:
            return pyxel.btnp(key)
        elif period is None:
            return pyxel.btnp(key, hold)
        else:
            return pyxel.btnp(key, hold, period)
    except TypeError:
        # 古い実装: hold だけ、または引数なしのみ対応している場合に段階的フォールバック
        try:
            if hold is None:
                return pyxel.btnp(key)
            else:
                return pyxel.btnp(key, hold)
        except TypeError:
            try:
                return pyxel.btnp(key)
            except TypeError:
                return False


def btnp(name: str, hold: Optional[int] = None, period: Optional[int] = None) -> bool:
    """キー名を受け取って、安全にbtnpチェック"""
    return btnp_key(get_key(name), hold, period)


def any_btnp(
    names: List[str], hold: Optional[int] = None, period: Optional[int] = None
) -> bool:
    """複数キーのうちいずれかが押されたか（存在するキーのみ判定）"""
    return any(btnp(n, hold, period) for n in names if get_key(n) is not None)


def ascii_fallback(s: str) -> str:
    """日本語など非ASCII文字を '·' に置換して仮表示"""
    return "".join(ch if 32 <= ord(ch) <= 126 else "·" for ch in s)


def clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))


def draw_window(x: int, y: int, w: int, h: int, title: Optional[str] = None) -> None:
    pyxel.rectb(x, y, w, h, 7)
    pyxel.rect(x + 1, y + 1, w - 2, h - 2, 0)
    if title:
        pyxel.text(x + 4, y + 2, title, 10)


def text_box(lines: List[str], x: int, y: int, w: int, h: int, color: int = 7) -> None:
    for i, line in enumerate(lines):
        pyxel.text(x + 6, y + 10 + i * 7, line, color)


def wrap_text(s: str, line_width: int) -> List[str]:
    words = s.split(" ")
    lines: List[str] = []
    cur = ""
    for w in words:
        add = w if not cur else " " + w
        if len(cur) + len(add) <= line_width:
            cur += add
        else:
            if cur:
                lines.append(cur)
            while len(w) > line_width:
                lines.append(w[:line_width])
                w = w[line_width:]
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---------------- 入力（ASCII） ----------------
ASCII_KEYS: Dict[int, str] = {}


def _add_key(const_name: str, ch: str) -> None:
    k = get_key(const_name)
    if k is not None:
        ASCII_KEYS[k] = ch


# 記号キー（存在チェック）
for name, ch in [
    ("KEY_SPACE", " "),
    ("KEY_COMMA", ","),
    ("KEY_PERIOD", "."),
    ("KEY_MINUS", "-"),
    ("KEY_SLASH", "/"),
    ("KEY_SEMICOLON", ";"),
    ("KEY_APOSTROPHE", "'"),
    ("KEY_LEFTBRACKET", "["),
    ("KEY_RIGHTBRACKET", "]"),
    ("KEY_BACKSLASH", "\\"),
    ("KEY_EQUAL", "="),  # 環境によっては存在しない
    ("KEY_EQUALS", "="),  # こちらのみの環境もある
]:
    _add_key(name, ch)

# アルファベット
for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    _add_key(f"KEY_{ch}", ch)

# 数字
for i in range(10):
    _add_key(f"KEY_{i}", str(i))


def capture_ascii_input(current: str, max_len: int = 24) -> str:
    """
    ASCII入力の取得。押下リピート対応。Backspaceで削除。
    btnp は互換ラッパー経由で呼び出し、古いPyxelでも動く。
    """
    updated = current
    for key, ch in ASCII_KEYS.items():
        if btnp_key(
            key, 8, 2
        ):  # ここは位置引数のみ。だめなら内部で段階的フォールバック
            if len(updated) < max_len:
                updated += ch
    # Backspace も存在チェック（ホールド付き。だめなら内部が自動でフォールバック）
    bk = get_key("KEY_BACKSPACE")
    if btnp_key(bk, 8, 2):
        updated = updated[:-1]
    return updated


# ---------------- データ構造 ----------------
class DialogLine:
    """会話1行分（話者とテキスト）"""

    def __init__(self, speaker: str, text: str) -> None:
        self.speaker = speaker
        self.text = text


class DialogPlayer:
    """
    会話ウィンドウ（タイプライター風表示）
    - Z / Enter（RETURN / ENTER）でスキップ・次行
    """

    def __init__(
        self, lines: List[DialogLine], width_chars: int = 36, cps: int = 2
    ) -> None:
        self.width_chars = width_chars
        self.cps = cps
        expanded: List[str] = []
        for ln in lines:
            header = ascii_fallback(f"{ln.speaker}: ")
            body = ascii_fallback(ln.text)
            body_lines = wrap_text(body, width_chars - len(header))
            if body_lines:
                expanded.append(header + body_lines[0])
                for cont in body_lines[1:]:
                    expanded.append(" " * len(header) + cont)
            else:
                expanded.append(header)
        self.lines = expanded
        self.index = 0
        self.char_progress = 0
        self.done = False

    def update(self) -> None:
        if self.done:
            return
        if self.index >= len(self.lines):
            self.done = True
            return
        self.char_progress += self.cps
        if any_btnp(["KEY_Z", "KEY_RETURN", "KEY_ENTER"]):
            line = self.lines[self.index]
            if self.char_progress < len(line):
                self.char_progress = len(line)
            else:
                self.index += 1
                self.char_progress = 0
                if self.index >= len(self.lines):
                    self.done = True

    def draw(self, x: int, y: int, w: int, h: int) -> None:
        draw_window(x, y, w, h, title="Dialog")
        vis: List[str] = []
        start = max(0, self.index - 2)
        for i in range(start, self.index):
            vis.append(self.lines[i])
        if not self.done and self.index < len(self.lines):
            cur = self.lines[self.index]
            cur = cur[: clamp(self.char_progress, 0, len(cur))]
            vis.append(cur)
        text_box(vis[-3:], x, y, w, h)


class Quiz:
    """クイズ（選択式 / 入力式）"""

    def __init__(
        self,
        qtype: str,
        question: str,
        choices: Optional[List[str]],
        answer_index: Optional[int],
        hint: str,
        after_success: List[DialogLine],
        after_fail: List[DialogLine],
    ) -> None:
        self.qtype = qtype
        self.question = question
        self.choices = choices
        self.answer_index = answer_index
        self.hint = hint
        self.after_success = after_success
        self.after_fail = after_fail


class QuizPlayer:
    """
    クイズUI・判定・ヒント表示
    - 選択式: ↑↓ で移動、Z/Enter 決定
    - 入力式: ASCII入力、Backspaceで削除、Z/Enter で判定
    - X でリセット
    """

    def __init__(self, quiz: Quiz, width_chars: int = 36) -> None:
        self.quiz = quiz
        self.width_chars = width_chars
        self.selected = 0
        self.answer_input = ""
        self.result: Optional[bool] = None
        self.show_hint = False
        self.question_lines = wrap_text(ascii_fallback(quiz.question), width_chars)

    def update(self) -> None:
        if self.quiz.qtype == "choice":
            if btnp("KEY_UP"):
                self.selected = (self.selected - 1) % len(self.quiz.choices)
            if btnp("KEY_DOWN"):
                self.selected = (self.selected + 1) % len(self.quiz.choices)
            if any_btnp(["KEY_Z", "KEY_RETURN", "KEY_ENTER"]):
                self.result = self.selected == self.quiz.answer_index
                self.show_hint = not self.result
        else:
            self.answer_input = capture_ascii_input(self.answer_input, max_len=24)
            if any_btnp(["KEY_Z", "KEY_RETURN", "KEY_ENTER"]):
                # ここでは文字列完全一致。必要なら数値比較や正規表現に変更可
                self.result = (
                    self.answer_input.strip().lower()
                    == str(self.quiz.answer_index).strip().lower()
                )
                self.show_hint = not self.result
        # リセット
        if btnp("KEY_X"):
            self.result = None
            self.show_hint = False
            if self.quiz.qtype != "choice":
                self.answer_input = ""

    def draw(self, x: int, y: int, w: int, h: int) -> None:
        draw_window(x, y, w, h, title="Quiz")
        y_text = y + 10
        for ln in self.question_lines:
            pyxel.text(x + 6, y_text, ln, 7)
            y_text += 7
        if self.quiz.qtype == "choice":
            y_choices = y_text + 2
            for i, ch in enumerate(self.quiz.choices):
                prefix = ">" if i == self.selected else " "
                col = 10 if i == self.selected else 7
                pyxel.text(
                    x + 6, y_choices, f"{prefix} {i + 1}. {ascii_fallback(ch)}", col
                )
                y_choices += 8
        else:
            pyxel.text(x + 6, y_text + 2, f"Answer: {self.answer_input}_", 11)
        if self.show_hint and self.result is False:
            pyxel.text(x + 6, y + h - 14, f"Hint: {ascii_fallback(self.quiz.hint)}", 8)


class Inventory:
    """簡易インベントリ（取得アイテム名の表示）"""

    def __init__(self) -> None:
        self.items: List[str] = []

    def add(self, name: str) -> None:
        self.items.append(name)

    def draw(self, x: int, y: int, w: int, h: int) -> None:
        draw_window(x, y, w, h, title="Inventory")
        yy = y + 12
        if not self.items:
            pyxel.text(x + 6, yy, "(empty)", 5)
        else:
            for it in self.items[-8:]:
                pyxel.text(x + 6, yy, f"- {ascii_fallback(it)}", 6)
                yy += 8


class NPC:
    """NPC（位置・会話・クイズ・報酬・クリア状態）"""

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        pre_dialog: List[DialogLine],
        quiz: Quiz,
        reward: str,
    ) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.pre_dialog = pre_dialog
        self.quiz = quiz
        self.reward = reward
        self.cleared = False

    def draw(self) -> None:
        color = 8 if self.cleared else 9
        pyxel.rect(self.x - 4, self.y - 6, 8, 12, color)
        pyxel.text(self.x - 10, self.y - 12, ascii_fallback(self.name), 7)

    def is_near(self, px: int, py: int) -> bool:
        return abs(px - self.x) <= 10 and abs(py - self.y) <= 10


class Player:
    """プレイヤー（移動・描画）"""

    def __init__(self, x: int, y: int, speed: int = 2) -> None:
        self.x = x
        self.y = y
        self.speed = speed

    def update(self, w: int, h: int) -> None:
        dx = (btn("KEY_RIGHT") - btn("KEY_LEFT")) * self.speed
        dy = (btn("KEY_DOWN") - btn("KEY_UP")) * self.speed
        self.x = clamp(self.x + dx, 8, w - 8)
        self.y = clamp(self.y + dy, 8, h - 8)

    def draw(self) -> None:
        pyxel.rect(self.x - 4, self.y - 4, 8, 8, 11)


class GameMap:
    """背景（簡易タイル風）"""

    def __init__(self, w: int, h: int) -> None:
        self.w = w
        self.h = h

    def draw(self) -> None:
        pyxel.cls(3)
        for y in range(0, self.h, 16):
            for x in range(0, self.w, 16):
                pyxel.pset(x, y, 4)


class GameApp:
    """ゲーム全体の状態遷移（map→dialog→quiz→after→map）"""

    def __init__(self, scenario_path: str) -> None:
        pyxel.init(256, 192, title="Scenario Loader (Pyxel)")
        self.map = GameMap(pyxel.width, pyxel.height)
        self.player = Player(40, 40)
        self.inventory = Inventory()
        self.npcs = self._load_scenario(scenario_path)
        self.state = "map"
        self.current_npc: Optional[NPC] = None
        self.dialog_player: Optional[DialogPlayer] = None
        self.quiz_player: Optional[QuizPlayer] = None
        self.after_dialog: Optional[DialogPlayer] = None
        pyxel.run(self.update, self.draw)

    def _load_scenario(self, path: str):
        """scenario_romaji.json からNPC/クイズ/報酬を読み込む"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        npcs = []
        for s in data["scenes"]:
            x, y = s["position"]
            pre = [
                DialogLine(speaker=ln["speaker"], text=ln["text"])
                for ln in s["pre_dialog"]
            ]
            qd = s["quiz"]
            quiz = Quiz(
                qtype=qd["type"],
                question=qd["question"],
                choices=qd.get("choices"),
                answer_index=qd.get("answer_index"),
                hint=qd["hint"],
                after_success=[DialogLine(**ln) for ln in qd["after_success"]],
                after_fail=[DialogLine(**ln) for ln in qd["after_fail"]],
            )
            npcs.append(NPC(s["npc"], x, y, pre, quiz, s["reward"]))
        return npcs

    def update(self) -> None:
        if self.state == "map":
            self._update_map()
        elif self.state == "dialog":
            self.dialog_player.update()
            if self.dialog_player.done and any_btnp(
                ["KEY_Z", "KEY_RETURN", "KEY_ENTER"]
            ):
                self._start_quiz()
        elif self.state == "quiz":
            self.quiz_player.update()
            if self.quiz_player.result is not None:
                self._on_quiz_done()
        elif self.state == "after":
            self.after_dialog.update()
            if self.after_dialog.done and any_btnp(
                ["KEY_Z", "KEY_RETURN", "KEY_ENTER"]
            ):
                if self.quiz_player and self.quiz_player.result:
                    self.state = "map"
                    self.current_npc = None
                else:
                    self._start_quiz()

    def _update_map(self) -> None:
        self.player.update(self.map.w, self.map.h)
        if any_btnp(["KEY_Z", "KEY_RETURN", "KEY_ENTER"]):
            t = self._near_npc()
            if t:
                self.current_npc = t
                self.dialog_player = DialogPlayer(t.pre_dialog, cps=2)
                self.state = "dialog"

    def _near_npc(self) -> Optional[NPC]:
        for npc in self.npcs:
            if npc.is_near(self.player.x, self.player.y):
                return npc
        return None

    def _start_quiz(self) -> None:
        if not self.current_npc:
            self.state = "map"
            return
        self.quiz_player = QuizPlayer(self.current_npc.quiz)
        self.after_dialog = None
        self.state = "quiz"

    def _on_quiz_done(self) -> None:
        npc = self.current_npc
        if self.quiz_player.result:
            self.after_dialog = DialogPlayer(npc.quiz.after_success, cps=2)
            if npc.reward:
                self.inventory.add(npc.reward)
                npc.cleared = True
        else:
            self.after_dialog = DialogPlayer(npc.quiz.after_fail, cps=2)
        self.state = "after"

    def draw(self) -> None:
        self.map.draw()
        for npc in self.npcs:
            npc.draw()
        self.player.draw()
        self.inventory.draw(256 - 90, 4, 86, 88)
        if self.state == "map":
            draw_window(4, 4, 160, 32, "Hint")
            pyxel.text(10, 18, "Move: ARROWS / Talk: Z/Enter", 7)
        elif self.state == "dialog":
            self.dialog_player.draw(8, 116, 240, 68)
        elif self.state == "quiz":
            self.quiz_player.draw(8, 80, 240, 104)
        elif self.state == "after":
            self.after_dialog.draw(8, 116, 240, 68)


if __name__ == "__main__":
    GameApp("scenario_romaji.json")
