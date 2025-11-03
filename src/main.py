"""
メインエントリポイント | `src/main.py`

- ゲームの起動処理はすべて `app.py` に任せる
- `main.py` は単に `App` クラスを生成して実行するだけ
"""

from app import App

if __name__ == "__main__":
    App()
