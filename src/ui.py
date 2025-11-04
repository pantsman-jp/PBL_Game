import pyxel as px
from PIL import Image, ImageDraw, ImageFont

# 日本語フォントへのパスを指定（環境に合わせて適宜変更してください）
# 例: NotoSansJP-Regular.ttf が src ディレクトリにあると仮定
FONT_PATH = "NotoSansJP-Regular.ttf"
FONT_SIZE = 10  # テキストのフォントサイズ
LINE_HEIGHT = 10  # 行の高さ（フォントサイズより少し大きめに設定）
MARGIN_X = 4  # テキストと枠の左右マージン
MARGIN_Y = 4  # テキストと枠の上下マージン
WINDOW_COLOR = 0  # 窓の背景色 (Pyxelのパレットインデックス: 0=黒)
TEXT_COLOR = (255, 255, 255)  # PILで使う白


class Window:
    def __init__(self, lines, x=0, y=40, img_bank=1):
        """
        lines: 表示する文字列リスト
        x, y: 画面上の表示座標（左上）
        img_bank: テキスト画像をロードするPyxelの画像バンク番号 (0〜2)
        """
        self.lines = lines
        self.x = x
        self.y = y
        self.img_bank = img_bank

        # 窓のサイズを計算
        self.width = max([self._get_text_width(line) for line in lines]) + MARGIN_X * 2
        self.height = len(lines) * LINE_HEIGHT + MARGIN_Y * 2

        # テキスト画像ファイルの一時的なパス
        self._temp_img_path = "tmp_text.png"

        # 画像生成とPyxelへのロード
        self._create_and_load_text_image()

    def _get_text_width(self, text):
        """PILを使用してテキストのピクセル幅を概算する（正確な幅計算には`textbbox`などが必要だが簡易的に）"""
        try:
            font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
            # 簡易的にtextsizeを使う（Pillowのバージョンによっては非推奨）
            # より正確には draw.textbbox((0, 0), text, font=font) を使用
            bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox(
                (0, 0), text, font=font
            )
            return bbox[2] - bbox[0]  # xmax - xmin
        except IOError:
            print(f"Error: Font file not found at {FONT_PATH}")
            return len(text) * FONT_SIZE  # フォントがない場合の代替（不正確）

    def _create_and_load_text_image(self):
        """
        文字列リストをPILで画像に描き、Pyxelの画像バンクにロードする
        """
        try:
            # 画像の生成
            img = Image.new("RGB", (self.width, self.height), color=(0, 0, 0))
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

            for i, line in enumerate(self.lines):
                # テキストの描画位置
                text_x = MARGIN_X
                text_y = MARGIN_Y + i * LINE_HEIGHT

                # 文字列を画像に描画
                draw.text((text_x, text_y), line, font=font, fill=TEXT_COLOR)

            # 一時ファイルとして保存
            img.save(self._temp_img_path)

            # Pyxelの画像バンクにロード
            # ロード先は (0, 0) から開始
            px.image(self.img_bank).load(0, 0, self._temp_img_path)

            # 一時ファイルの削除 (必要に応じて)
            # os.remove(self._temp_img_path)

        except IOError as e:
            print(f"Error: Failed to create or load text image. Check FONT_PATH: {e}")

    def draw(self):
        """
        画面にウィンドウとテキスト画像を表示する。
        """
        # 背景（黒）を描画
        px.rect(self.x, self.y, self.width, self.height, WINDOW_COLOR)

        # テキスト画像をblit (blt) で表示
        # (blt(x, y, img, u, v, w, h, colkey))
        # x, y: 画面上の表示位置
        # img: 画像バンク番号
        # u, v: 画像バンク内の左上座標 (今回は (0, 0))
        # w, h: 画像の幅と高さ
        # colkey: 透明にする色 (今回はなし、背景色が黒で表示される)
        px.blt(self.x, self.y, self.img_bank, 0, 0, self.width, self.height)
