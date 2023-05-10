from mylib.calc_position import CalcPosition
from pythonosc import dispatcher
import datetime
import json
from time import sleep
from copy import copy
import numpy as np


class PositioningSystem:


    def __init__(self) -> None:
        self.calc_position = None
        self.position_mesuring = False # 座標を測定中かどうか
        self.position = [None, None, None]
        self.INTERVAL = 1 # 座標の計算間隔

    def dpt_map(self, dpt: dispatcher.Dispatcher):
        dpt.map("/avatar/parameters/VPS*", self.osc_handler)

    def osc_handler(self, address, *args):
        if address == "/avatar/parameters/VPS":
            self.position_mesuring = args[0]
            if self.position_mesuring:
                self.calc_position = CalcPosition()
                self.__get_positions()
            else:
                del self.calc_position
                self.calc_position = None

        elif "/avatar/parameters/VPS/sat" in address:
            if self.calc_position is not None:
                self.calc_position.osc_handler(address, args[0])
                return
        else:
            pass # ここには来ないよ

    def __get_positions(self):
        json_log = []
        while self.position_mesuring:
            dt_now = datetime.datetime.now()
            ret, pos = self.calc_position.position_update()
            if ret:
                # jsonに保存するために整形
                json_log.append([dt_now.strftime("%H:%M:%S:%f"), copy(pos)])
                # cmdへの表示
                # 値を丸める
                pos_round = [np.round(pos[i], decimals=1) for i in range(len(pos))]
                print(dt_now.strftime("%H:%M:%S") + str(pos_round))

                self.position = pos_round
            # 約1秒ごとに座標を更新する
            sleep(self.INTERVAL)

        # if self.positioning_mesuring == False
        self.save_json(json_log)

    def save_json(self, data):

        file_name = "./data/" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"

        with open(file_name, "w") as f:
            json.dump(data, f, indent=4)