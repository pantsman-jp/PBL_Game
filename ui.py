"""
簡易ウィンドウ描画 | ui.py
会話ウィンドウを作成します．
"""

import pygame


def draw_window(
    surface,
    font,
    lines,
    rect=(48, 320, 544, 128),
    bgcolor=(0, 0, 0),
    fg=(255, 255, 255),
):
    """
    画面下部にテキストウィンドウを表示します．
    rect: (x, y, w, h)
    """
    x, y, w, h = rect
    # 背景
    pygame.draw.rect(surface, bgcolor, (x, y, w, h))
    pygame.draw.rect(surface, (200, 200, 200), (x, y, w, h), 2)
    # テキスト行を描画
    line_h = font.get_linesize()
    for i, line in enumerate(lines):
        surf = font.render(line, True, fg)
        surface.blit(surf, (x + 8, y + 8 + i * line_h))
