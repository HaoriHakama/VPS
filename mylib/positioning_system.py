import json
import math
from copy import copy
from dataclasses import asdict, dataclass
from datetime import datetime
from threading import Thread
from time import sleep
from typing import Optional

import numpy as np
from pythonosc import dispatcher

from mylib.satellite3 import Satellite


@dataclass
class PositionData:
    """
    座標と時刻
    座標はfloat 3桁でなければならない
    """
    position: list[float]
    time: str = datetime.now().strftime("%Y%m%d%H%M%S")

    def __post_init__(self):
        if not isinstance(self.position, list) or len(self.position) != 3:
            raise TypeError(
                "position must be a list with exactly three elements")
        for i in self.position:
            if not isinstance(i, float):
                raise TypeError(
                    "All elements of position must be of type float")


class DataList:
    """
    PositionDataのリストを保持するクラス
    """

    def __init__(self) -> None:
        self.__datalist: list[PositionData] = []

    @property
    def datalist(self):
        return self.__datalist

    def add_data(self, data: PositionData):
        self.__datalist.append(data)

    def x_data(self):
        if len(self.__datalist) == 0:
            return None
        return [data.position[0] for data in self.__datalist]

    def y_data(self):
        if len(self.__datalist) == 0:
            return None
        return [data.position[1] for data in self.__datalist]

    def z_data(self):
        if len(self.__datalist) == 0:
            return None
        return [data.position[2] for data in self.__datalist]


class PositioningSystem:
    """
    positioning systemを制御するクラス
    """

    def __init__(self) -> None:
        self.is_mesuring = False
        self.datalist: DataList = None
        self.satellite: list[Satellite]

    def pys_switch(self,
                   address: str,
                   dpt: list[dispatcher.Dispatcher],
                   *args: list[bool]):
        """
        positioning systemを起動/終了するosc_handler
        """
        if address != "/avatar/parameters/VPS":
            raise ValueError

        if not isinstance(args[0], bool):
            raise TypeError

        if args[0]:
            self.is_mesuring = True
            self.start_mesurement(dpt[0])
        else:  # args[0] == False:
            self.is_mesuring = False

    def start_mesurement(self, dpt: dispatcher.Dispatcher):
        """
        座標測定を開始するための関数
        """

        self.datalist = DataList()

        self.satellites = init_satellites()

        while self.is_mesuring:
            position_data = get_position(self.satellites)
            if position_data is not None:
                self.datalist.add_data(position_data)

                sleep(1)

        # when mesurement finish!
        self.stop_mesurement(self.satellites, dpt)

    def satellite_osc_handler(self, address: str, *args):
        if self.is_mesuring:
            for i in range(len(self.satellites)):
                if f"/avatar/parameters/VPS/sat_{i}/" in address:
                    self.satellites[i].osc_handler(address, args[0])
        else:
            pass

    def stop_mesurement(
            self,
            satellites: list[Satellite],
            dpt: dispatcher.Dispatcher):
        if len(self.datalist.datalist) > 0:
            save_data(self.datalist)
        self.datalist = None
        del_satellites(satellites)


def set_satellites_osc_handler(
        satellites: list[Satellite],
        dpt: dispatcher.Dispatcher):
    """
    各サテライトのosc_handlerをdptに設定する
    """
    for i in range(len(satellites)):
        address = f"/avatar/parameters/VPS/sat_{i}/*"
        func = satellites[i].osc_handler
        dpt.map(address, func)


def init_satellites() -> list[Satellite]:
    satellites: list[Satellite] = []
    POS_SATELLITES = [
        [50, 0, 0],
        [-50, 0, 0],
        [0, 50, 0],
        [0, -50, 0],
        [0, 0, 50],
        [0, 0, -50]
    ]
    for i in range(len(POS_SATELLITES)):
        satellites.append(Satellite(i, POS_SATELLITES[i]))

    return satellites


def get_position(satellites: list[Satellite]) -> Optional[PositionData]:
    """
    現在のプレイヤーの座標を計算する一連の工程
    :param satellites:
    :return: player position(class PositionData)
    """
    pos_satellite, distances = __get_sat_data(satellites)
    ret, pos_player = __calc_position(copy(pos_satellite), copy(distances))

    if ret:
        position_data = PositionData(pos_player)
        return position_data
    else:
        return None


def __get_sat_data(satellites: Satellite):
    """
    サテライトの座標と, 各サテライトからの距離を取得する
    """

    def __get_distance(i: int, satellite: Satellite, results: list) -> None:
        results[i] = satellite.get_distance()

    def __print_init_status(results):
        init_status = []
        for r in results:
            if r is None:
                init_status.append("□")
            else:
                init_status.append("■")
        print(init_status)

    def format_data(satellites: list[Satellite], results: list[float]):
        """
        取得した距離がNoneのものをデータから取り除く
        """
        pos_satellite = []
        distances = []
        for i in range(len(satellites)):
            if results[i] is not None:
                pos_satellite.append(satellites[i].position)
                distances.append(results[i])

        return pos_satellite, distances

    results: list = [None for _ in range(len(satellites))]
    threads: list[Thread] = []

    for i in range(len(satellites)):
        th = Thread(
            target=__get_distance,
            args=(
                i,
                satellites[i],
                results,
            ),
            daemon=True)
        threads.append(th)

    for th in threads:
        th.start()

    for th in threads:
        th.join()

    __print_init_status(results)

    pos_satellite, distances = format_data(satellites, results)
    return pos_satellite, distances


def __calc_position(pos_satellites: list[float], distances: list[float]):
    """
    サテライトの座標と各座標からの距離から、プレイヤーの座標を計算する関数
    :param positions: サテライトの座標
    :param distances: サテライトの距離
    :return:
    """
    try:
        if len(pos_satellites) != len(distances) or len(pos_satellites) < 4:
            raise ValueError
    except ValueError:
        return False, [None, None, None]

    LIMIT = 0.00000001

    def dist(p1, p2):
        return math.sqrt(
            (p1[0] - p2[0]) ** 2 +
            (p1[1] - p2[1]) ** 2 +
            (p1[2] - p2[2]) ** 2
        )

    R = distances
    X = np.array([5.0, 2.0, 3.0, 1.0])

    for _ in range(1000):
        DR = np.array([r - dist(X, p) for r, p in zip(R, pos_satellites)])

        A = np.array([
            [
                - (p[0] - X[0]) / dist(X, p),
                - (p[1] - X[1]) / dist(X, p),
                - (p[2] - X[2]) / dist(X, p),
                1
            ] for p in pos_satellites
        ])

        DX = (np.linalg.inv(A.T @ A) @ A.T) @ DR
        # print(f"DX: {DX}")
        if np.inner(DX[:3], DX[:3]) < LIMIT:
            return True, X[:3].tolist()

        if np.isnan(X[0]):
            break
        X[:3] += DX[:3]

    return False, [None, None, None]


def save_data(datalist: DataList):
    l = []
    for data in datalist.datalist:
        l.append(asdict(data))

    now = datetime.now().strftime("%Y%m%d%H%M")
    file = f"./data_{now}.json"
    with open(file, "w", encoding="UTF-8") as f:
        json.dump(l, f, indent=4)

    print(f"file: {file} is saved")


def del_satellites(satellites: list[Satellite]):
    for satellite in satellites:
        satellite.del_is_not_called = True
        del satellite
