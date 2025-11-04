from PIL import Image, ImageDraw, ImageFont
import pyxel

# ====== 1️⃣ 日本語を画像に描く ======
text = "おはよう Pyxel！"

# フォントを設定（フォントファイルは同じフォルダにある前提）
font = ImageFont.truetype("NotoSansJP-Regular.ttf", 20)

# 画像サイズを設定（テキストに合わせて大きめに）
img = Image.new("RGB", (200, 40), color="black")

# 描画オブジェクトを作成
draw = ImageDraw.Draw(img)

# テキストを描く（白色）
draw.text((5, 5), text, font=font, fill="white")

# 保存（Pyxelで読み込むため）
img.save("jp_text.png")


# ====== 2️⃣ Pyxelで読み込み・表示 ======
pyxel.init(200, 80, title="日本語テキスト")

# 画像をPyxelのイメージバンク0に読み込む
pyxel.image(0).load(0, 0, "jp_text.png")


def update():
    pass


def draw():
    pyxel.cls(0)
    # 読み込んだ画像を画面に貼り付ける
    pyxel.blt(10, 20, 0, 0, 0, 200, 40)


pyxel.run(update, draw)
