import numpy as np
import math
from mylib.satellite3 import Satellite
from threading import Thread


class CalcPosition:

    POS_SATELLITES = [
        [50, 0, 0],
        [-50, 0, 0],
        [0, 50, 0],
        [0, -50, 0],
        [0, 0, 50],
        [0, 0, -50]
    ]

    def __init__(self) -> None:
        # プレイヤー座標の初期化
        self.pos_player = [None, None, None]
        # サテライトの数
        self.number_of_sat = len(CalcPosition.POS_SATELLITES)
        # 各サテライトのインスタンス
        self.satellites:list[Satellite] = []
        for i in range(self.number_of_sat):
            satellite = Satellite(i)
            self.satellites.append(satellite)

    def __del__(self):
        for satellite in self.satellites:
            satellite.is_satellite_active = False
            del satellite
        del self.satellites
        print("CalcPosition destructor is called")

    def __get_distances(self, index: int, distances: list, initializing: list):
        distance = self.satellites[index].get_distance()
        if distance is None:
            initializing[index] = "□"
        else:
            initializing[index] = "■"
            distances[index] = distance
        return

    def position_update(self):
        distances = [None for _ in range(self.number_of_sat)]
        initializing = [None for _ in range(self.number_of_sat)]
        
        threads: list[Thread] = []
        for i in range(self.number_of_sat):
            th = Thread(target=self.__get_distances(i, distances, initializing, ), daemon=True)
            threads.append(th)

        for th in threads:
            th.start()

        for th in threads:
            th.join()

        # print(initializing)
        try: 
            ret = self.__calc_position(distances)
        except np.linalg.LinAlgError:
            print("numpy.linalg.LinAlgError: Singular matrix")
            return False, [None, None, None]

        if ret:
            return True, self.pos_player
        else:
            return False, [None, None, None]

    def osc_handler(self, address, *args):
        for i in range(self.number_of_sat):
            if f"sat_{i}" in address:
                self.satellites[i].osc_handler(address, args[0])

    def __calc_position(self, distances):
        LIMIT = 0.00000001
        measured_distances = []
        pos_satellite = []

        # 測定結果の整形
        for i in range(self.number_of_sat):
            if distances[i] != None:
                measured_distances.append(distances[i])
                pos_satellite.append(CalcPosition.POS_SATELLITES[i])

        if len(pos_satellite) < 4:
            return False

        def dist(p1, p2):
            return math.sqrt(
            (p1[0] - p2[0]) ** 2 +
            (p1[1] - p2[1]) ** 2 +
            (p1[2] - p2[2]) ** 2
        )

        # print([round(d) for d in measured_distances])

        R = measured_distances
        X = np.array([5.0, 2.0, 3.0, 1.0])

        for _ in range(1000):
            DR = np.array([r - dist(X, p) for r, p in zip(R, pos_satellite)])

            A = np.array([
                [
                    - (p[0] - X[0]) / dist(X, p), 
                    - (p[1] - X[1]) / dist(X, p), 
                    - (p[2] - X[2]) / dist(X, p), 
                    1
                ] for p in pos_satellite
            ])

            DX = (np.linalg.inv(A.T @ A) @ A.T) @ DR
            # print(f"DX: {DX}")
            if np.inner(DX[:3], DX[:3]) < LIMIT:
                self.pos_player[0] = X[0]
                self.pos_player[1] = X[1]
                self.pos_player[2] = X[2]
                return True

            if np.isnan(X[0]):
                break
            X[:3] += DX[:3]