# VRC Positioning System

## What is this ?
* oscとcontactでアバターの絶対値座標を取得する測量ギミック
* 座標を取得し続けて3次元マッピングがしたい

## クラス・変数名など
* VrcPositioningSystem: メインに当たる部分
    * satelliteN: 各サテライトのインスタンス
    * distances: 各サテライトからの距離を保持するリスト
    * last_update: 前回の座標計算時刻
    * calc_position(): 座標を計算する -> いつ？(Threadingかなぁやっぱり)
* Satellite: サテライトの情報を保持するクラス 
    * initialize(): 初期化処理(movementを0から1000まで動かす)を行う
    * bool initializing: 初期化中かどうか
    * movement: サテライトの移動量
    * contacts[]: サテライトの4つのレシーバーの値を保持するクラス
    * osc_handler(): oscの受信関数
    * update_sat_pos(): サテライトの位置を動かす
    * calc_distance(): サテライトからの距離を計算(受信したら勝手に計算しようそうしよう)
* CalcPosition: 座標を計算するクラス
    * CalcPosition.POS_SATELLITE: サテライトの座標
    * get_distances(): 各サテライトから座標を取得
    * calc_position(): 座標を計算する
* OscServer: OSC信号を受信するクラス
    * ちなみにこれは実質Threadingなので適当にやればOKです