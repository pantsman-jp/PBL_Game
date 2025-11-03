"""
簡易ウィンドウ描画クラス | `src/ui.py`

- テキストを複数行で表示する枠を提供する。
- 現時点ではグラフィカル装飾なしのシンプルな実装。
"""

import pyxel as px


class Window:
    def __init__(self, lines):
        """
        lines: 表示する文字列リスト
        """
        self.lines = lines

    def draw(self):
        """
        画面下部に黒背景と白文字でメッセージを表示する。
        """
        px.rect(8, 80, 112, 40, 0)  # 背景（黒）
        for i, line in enumerate(self.lines):
            px.text(12, 84 + i * 8, line, 7)
