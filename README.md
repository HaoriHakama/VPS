# VPS
* VRChat Positioning System (VPS) is an avatar gimmick to mesure player's absolute coordinates.

## 使用方法
### アバターギミックをアバターにセットアップ
1. アバターのUnity ProjectにModular Avatar(https://modular-avatar.nadena.dev/ja/)をインポート
2. `VRChatPositioningSystem.unitypackage`をUnity Progjectにインポート
3. `Assets/VRCPositioningSystem/VPS.prefab`をHierarchyのアバター直下にD & D
4. AvatarをVRChatにアップロード

### appの起動
1. 作業ディレクトリを`VPS`にする(`cd /nyan/VPS`)
2. `py -m mylib`を実行 -> OSCを受信できる状態になります

### VRChat上で測定開始
* Expression Menuの`VPS/測定開始`をONにすると測定開始、OFFにすると測定終了
* `VPS/Receiver表示`でContact Receiverを可視化できます