# VPS
* VRChat Positioning System (VPS) is an avatar gimmick to mesure player's absolute coordinates.

## 使用方法

### 環境
Python3.9以上

### アバターギミックをアバターにセットアップ
1. アバターのUnity ProjectにModular Avatar(https://modular-avatar.nadena.dev/ja/)をインポート
2. `VRChatPositioningSystem.unitypackage`をUnity Progjectにインポート
3. `Assets/VRCPositioningSystem/VPS.prefab`をHierarchyのアバター直下にD & D
4. AvatarをVRChatにアップロード

### appの起動

#### Windows

1. 作業ディレクトリを`VPS`にする(`cd /nyan/VPS`)
2. (TODO: `requirements.txt` からライブラリをインストールする)
3. `py -m mylib`を実行 -> OSCを受信できる状態になります

#### Linux

1. 作業ディレクトリを`VPS`にする(`cd /nyan/VPS`)
2. `python3 -m venv .venv` を実行
3. `source .venv/bin/activate` を実行
3. `pip install -r requirements.txt` を実行
4. `python3 -m mylib` を実行

注意: Linux環境下ではmatplotlibのGUI出力が動作しないため、適宜コメントアウトしてください

### VRChat上で測定開始
* Expression Menuの`VPS/測定開始`をONにすると測定開始、OFFにすると測定終了
* `VPS/Receiver表示`でContact Receiverを可視化できます
