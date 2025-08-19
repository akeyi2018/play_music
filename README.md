---

# 動画再生における既知の問題点

本アプリでは音楽再生は安定しているが、**動画再生に関して以下の問題が確認されている**。

## 問題点一覧

### 1. 再生中に動画をロードするとフリーズする

* 再生中の `VLC MediaPlayer` インスタンスが残ったまま、新しい動画をロードしてしまう。
* `tkinter.after` による進捗更新ループも複数走り、競合状態になりフリーズする。

### 2. スライダー操作で位置変更が効かない場合がある

* ユーザーがスライダーを動かしても、`update_movie_progress` が定期的に走り続けるため、設定した位置が即座に上書きされる。
* その結果「スライダーを動かしても戻る」現象が発生する。

### 3. 再生状態と更新ループの同期不整合

* `self.video_player.playing` フラグと `MediaPlayer.is_playing()` の実際の状態がずれることがある。
* その結果、再生ボタンや停止ボタンの表示が正しく切り替わらない場合がある。

### 4. `set_position` メソッド未実装の問題

* スライダーから動画位置を変更する際に `set_position` を呼んでいるが、`VideoPlayer` クラスに実装されていない。
* 実際には `MediaPlayer.set_position(float)` を直接呼び出す必要がある。

---

## 根本原因

* **VLC MediaPlayer の状態管理**（インスタンスの切り替えや停止処理）が不十分。
* **tkinter の after ループ** が動画ロードや再生状態と同期していない。
* 音楽再生 (`pygame.mixer`) では問題ないが、動画再生 (`vlc.MediaPlayer`) では競合が発生しやすい。

---

## 今後の改善ポイント（要検討）

* 動画ロード前に **必ず再生中インスタンスを stop + release** してから新しい動画をロードする。
* スライダー操作時は `update_movie_progress` のループを一時停止し、操作完了後に再開する。
* `VideoPlayer` クラスに `set_position()` を実装し、UI 側から統一的に呼べるようにする。
* after ジョブの ID を統一的に管理し、ロード時に確実にキャンセルする。

---


### 実行手順

UVインストールと有効化
```terminal

# linux
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

```

UV初期化

```terminal
cd <project name>
uv init
uv install python 3.12 # option
uv add <library name>
```

UV実行
```terminal
uv run <target python file>
```
