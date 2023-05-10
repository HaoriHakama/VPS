from time import sleep
from threading import Thread, Lock, Timer
from mylib.osc_client import osc_client
from copy import copy


# サテライトの情報を取得・保持・更新するクラス
class Satellite:

    SENDER_R = 0.01
    RECEIVER_R = 3.0

    def __init__(self, index: int) -> None:
        self.is_initializing = Lock()
        self.initialize_movement_lock = Lock()
        self.get_distance_lock = Lock()
        self.get_distance_lock.acquire()
        self.is_satellite_active = True

        # サテライトの情報
        self.index = index
        self.contacts = [0.0, 0.0]
        self.movement = 0.0
        # OSCの送受信
        self.client = osc_client()
        self.movement_address = f"/avatar/parameters/VPS/sat_{self.index}/movement"
        self.contact_address = [
            f"/avatar/parameters/VPS/sat_{self.index}/contact_0",
            f"/avatar/parameters/VPS/sat_{self.index}/contact_1"
        ]

        # レシーバーの位置の初期化
        self.client.send_message(self.movement_address, 0)
        th0 = Thread(target=self.__receiver_initialize, daemon=True)
        th0.start()

        th1 = Thread(target=self.__process_contacts, args=(th0, ), daemon=True)
        th1.start()

    def __del__(self):
        self.is_satellite_active = False
        print(f"sat{self.index} destructor is called")

    def get_distance(self):
        ret = self.get_distance_lock.acquire(timeout=0.02)
        if not ret:
            return None
        else:
            return self.__calc_distances(copy(self.contacts), copy(self.movement))


    def __receiver_initialize(self):
        ret = self.is_initializing.acquire(timeout=3)
        if not ret:
            return

        sleep(2)

        m = 0.0
        while self.is_initializing.locked():
            message = m / 1000
            self.client.send_message(self.movement_address, message)

            # self.initialize_movement_lock.acquire()

            sleep(0.1)

            m += Satellite.RECEIVER_R / 2

            if m > 500:
                m = 0

    # OSCの受信処理
    def osc_handler(self, address, arg):
        if address == self.movement_address:
            self.movement = arg * 1000

            # if self.initialize_movement_lock.locked():
                # self.initialize_movement_lock.release()

        elif address == self.contact_address[0]:
            self.contacts[0] = arg
        elif address == self.contact_address[1]:
            self.contacts[1] = arg
            
            if self.is_initializing.locked() and arg > 0:
                self.is_initializing.release()

    def __calc_distances(self, contacts, movement):

        if contacts[0] > 0 and contacts[1] > 0:
            distance = movement + (1 - contacts[1]) * Satellite.RECEIVER_R + Satellite.SENDER_R

        elif contacts[0] == 0 and contacts[1] > 0:
            distance = movement - (1 - contacts[1]) * Satellite.RECEIVER_R - Satellite.SENDER_R

        elif contacts[0] > 0 and contacts[1] == 0:
            distance = movement + (1 - contacts[0]) * Satellite.RECEIVER_R + Satellite.SENDER_R + Satellite.RECEIVER_R

        else:
            return None

        return distance


    # コンタクトの値を評価する
    def __process_contacts(self, initializing_thread: Thread):

        initializing_thread.join()

        while self.is_satellite_active:
            # サテライトが初期化中の時はdistanceを取得させない
            if self.is_initializing.locked():
                if not self.get_distance_lock.locked():
                    self.get_distance_lock.acquire()
            else: # self.is_initializing.locked() == False
                # 両方のcontactが反応している場合
                if self.contacts[0] > 0 and self.contacts[1] > 0:
                    if self.get_distance_lock.locked():
                        self.get_distance_lock.release()
                # 手前側のcontactのみが反応している場合Receiverを押し出す
                elif self.contacts[0] > 0 and self.contacts[1] == 0:
                    self.__move_receiver_out()
                    if self.get_distance_lock.locked():
                        self.get_distance_lock.release()
                # 奥側のcontactのみが反応している場合Receiverを内側に動かす
                elif self.contacts[0] == 0 and self.contacts[1] > 0:
                    self.__move_receiver_in()
                    if self.get_distance_lock.locked():
                        self.get_distance_lock.release()
                # 両方のcontactが反応していない場合初期化する
                else:
                    if not self.get_distance_lock.locked():
                        self.get_distance_lock.acquire()
                    th = Thread(target=self.__receiver_initialize, daemon=True)
                    th.start()
                    th.join()

            sleep(0.01)

    def __move_receiver_out(self):
        m = (self.movement + Satellite.RECEIVER_R / 2) / 1000
        self.client.send_message(self.movement_address, m)

    def __move_receiver_in(self):
        m = (self.movement - Satellite.RECEIVER_R / 2) / 1000
        self.client.send_message(self.movement_address, m)

