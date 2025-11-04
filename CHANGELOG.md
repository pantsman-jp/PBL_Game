# ChangeLog of PBL_Game

## v0.3.2 (2025-11-04)
- `assets.pyxres` の追加

## v0.3.1 (2025-11-03)
- `CHANGELOG.md` の日本語化
- コードの説明を追加
- 将来的なテクスチャ、BGM 追加に対応

### 対応予定
| 種類 | 対応箇所 | コメント |
| :---: | :---: | :---: |
| プレイヤー表示 | `core/field.py` 内 `# プレイヤー描画` | `px.blt(56, 56, 0, 0, 0, 16, 16, 0)` |
| NPC 表示 | `core/field.py` 内 `# NPC描画` | `px.blt(screen_x, screen_y, 0, 16, 0, 16, 16, 0)` |
| タイルマップ | `core/field.py` 内 `# 将来的なアセット対応` | `px.bltm()` 利用 |
| BGM | `core/system.py` | `px.playm(track_id, loop=True)` |
| SE | `core/field.py`，`core/talk.py` | `px.play()` を適宜挿入 |

**BGM**
| 機能 | 実装箇所 | コメント例 |
| :---: | :---: | :---: |
| BGM再生 | `System.play_bgm()` | `px.playm(track_id, loop=True)` を有効化 |
| BGM停止 | `System.stop_bgm()` | `px.stop()` を有効化 |
| 歩行音 | `Field.start_move()` | `px.play()` を追加 |
| 会話開始BGM切替 | `Talk.open_dialog()` | `self.app.system.play_bgm(track_id)` |
| クイズ正解／不正解SE | `Talk.update()` | `px.play(3, 2)` / `px.play(3, 3)` |

## v0.3.0 (2025-11-02)
- `/src` 以下を大幅に変更し、新たなテンプレートに置き換え

## v0.2.0 (2025-10-28)
- `src/main.py` に <https://github.com/shiromofufactory/pyxel-tiny-drpg> から引用
- `src/sample.py` を削除

## v0.1.1 (2025-10-28)
- リファクタリング

## v0.1.0 (2025-10-28)
- `pyxel` のサンプルを追加

## v0.0.0 (2025-10-28)
- リポジトリを作成
- プロジェクト開始