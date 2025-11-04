"""
メインエントリポイント | `src/main.py`

- ゲームの起動処理はすべて `app.py` に任せる
- `main.py` は単に `App` クラスを生成して実行するだけ
"""

from app import App
import traceback

if __name__ == "__main__":
    try:
        App().run()
    except Exception:
        traceback.print_exc()
        input("\n[Enter]キーで終了")
