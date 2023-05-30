from copy import copy
from threading import Lock, Thread, active_count, current_thread
from time import sleep

from mylib.osc_client import osc_client


class Satellite:
    """
    サテライトを初期化し、情報を保持するクラス
    """
    SENDER_R = 0.01
    RECEIVER_R = 3.0

    def __init__(self, index, position) -> None:
        # Lockオブジェクト
        self.__is_initializing = Lock()
        self.__get_distance_lock = Lock()
        self.__get_distance_lock.acquire()

        # サテライトがアクティブであることを示すフラグ
        self.__del_is_not_called = True

        # サテライトの情報
        self.__index = index
        self.__movement = 0.0
        self.contacts = [0.0, 0.0]
        self.__position = position  # サテライトの座標

        # OSCの送受信関連
        self.__client = osc_client()
        self.__movement_address = (
            f"/avatar/parameters/VPS/sat_{self.index}/movement"
        )
        self.__contact_address = [
            f"/avatar/parameters/VPS/sat_{self.index}/contact_0",
            f"/avatar/parameters/VPS/sat_{self.index}/contact_1"
        ]
        self.client.send_message(self.movement_address, 0.0)

        self.start_automatic_control()

    def __del__(self):
        self.del_is_not_called = False
        print(f"satellite{self.index} destructor called.")

    @property
    def is_initializing(self):
        return self.__is_initializing

    @property
    def get_distance_lock(self):
        return self.__get_distance_lock

    @property
    def del_is_not_called(self):
        return self.__del_is_not_called

    @del_is_not_called.setter
    def del_is_not_called(self, flag: bool):
        if isinstance(flag, bool):
            self.__del_is_not_called = flag
        else:
            raise ValueError

    @property
    def index(self):
        return self.__index

    @property
    def movement(self):
        return self.__movement

    @property
    def position(self):
        return self.__position

    @property
    def client(self):
        return self.__client

    @property
    def movement_address(self):
        return self.__movement_address

    @property
    def contacts_address(self):
        return self.__contact_address

    def start_automatic_control(self):
        """
        サテライトの自動制御を開始する関数
        """
        th_init = Thread(target=self.__init_receiver, daemon=True)
        th_init.start()

        sleep(1)

        th_process_contacts = Thread(target=self.__process_contacts, daemon=True)
        th_process_contacts.start()
        print(f"active_count: {active_count()}")

    def __init_receiver(self) -> None:
        """
        レシーバーを0~1000 mの範囲で動かし、
        プレイヤーにぶつかった(self.is_initializing.locked()==False)ら終了する
        すでに初期化が行われている場合は初期化を行わない()
        """
        
        print(f"[{current_thread().name}]{self.index}-satellite try take initializing lock.", flush=True)
        ret = self.is_initializing.acquire(timeout=1)
        if not ret:
            print(f"[{current_thread().name}]{self.index}-satellite is already initializing.", flush=True)

            return

        print(f"[{current_thread().name}]{self.index}-satellite start init reciver.", flush=True)
        sleep(1)

        m = 0.0
        while self.is_initializing.locked() and self.del_is_not_called:
            message = m / 1000
            self.client.send_message(self.movement_address, message)
            sleep(0.1)
            m += Satellite.RECEIVER_R / 2

            print(f"[{current_thread().name}]{self.index}-satellite move to {m}", flush=True)
            if m > 1000:
                print(f"[{current_thread().name}]{self.index}-satellite return start position.", flush=True)
                m = 0
        print(f"[{current_thread().name}]{self.index}-satellite finished initializing", flush=True)
        return

    def osc_handler(self, address, *args):
        """
        受信したOSC信号に対し、処理を振り分ける関数
        :param address: osc address
        :param args: osc signal
        """

        def __is_init_finished(contact1: float):
            """
            receiverの初期化が終了したか判定し、Lockをリリースする
            :param contact1: contact1の値
            """
            if self.is_initializing.locked():
                if contact1 > 0:
                    print(f"[{current_thread().name}]{self.index}-satellite reached target: {contact1}", flush=True)
                    self.is_initializing.release()

        # 受信した値でインスタンス変数を更新する
        if address == self.movement_address:
            self.__movement = args[0] * 1000
            print(f"[{current_thread().name}]{self.index}-satellite update movement: {self.movement}", flush=True)
        elif address == self.contacts_address[0]:
            self.contacts[0] = args[0]
            print(f"[{current_thread().name}]{self.index}-satellite update contacts: {self.contacts}", flush=True)
        elif address == self.contacts_address[1]:
            self.contacts[1] = args[0]
            print(f"[{current_thread().name}]{self.index}-satellite update contacts: {self.contacts}", flush=True)
            __is_init_finished(args[0])

    def get_distance(self):
        ret = self.get_distance_lock.acquire(timeout=0.02)
        if not ret:
            return None
        else:
            return self.__calc_distance(
                copy(
                    self.movement), copy(
                    self.contacts))

    @staticmethod
    def __calc_distance(movement: float, contacts: list[float]) -> float:
        """
        サテライトからプレイヤーまでの距離を計算する
        計算途中に値が書き換えられるのは困るのでStatic Methoadにする
        """
        if contacts[0] > 0 and contacts[1] > 0:
            distance = movement + \
                (1 - contacts[1]) * Satellite.RECEIVER_R + Satellite.SENDER_R

        elif contacts[0] == 0 and contacts[1] > 0:
            distance = movement - \
                (1 - contacts[1]) * Satellite.RECEIVER_R - Satellite.SENDER_R

        elif contacts[0] > 0 and contacts[1] == 0:
            distance = movement + \
                (1 - contacts[0]) * Satellite.RECEIVER_R + \
                Satellite.SENDER_R + Satellite.RECEIVER_R

        else:
            return None

        return distance

    def __process_contacts(self):
        """
        0.01秒ごとにcontactsの値を評価する関数
        """
        t = 0
        state = ""
        while self.__del_is_not_called:
            # サテライトが初期化中の時はdistanceを取得させない
            if self.is_initializing.locked():
                state = "initializing"
                if not self.get_distance_lock.locked():
                    self.get_distance_lock.acquire()
            else:  # self.is_initializing.locked() == False
                # 両方のcontactが反応している場合
                if self.contacts[0] > 0 and self.contacts[1] > 0:
                    state = "contacting"
                    if self.get_distance_lock.locked():
                        self.get_distance_lock.release()
                # 手前側のcontactのみが反応している場合Receiverを押し出す
                elif self.contacts[0] > 0 and self.contacts[1] == 0:
                    t = 0
                    self.__move_receiver_out()
                    if self.get_distance_lock.locked():
                        self.get_distance_lock.release()
                # 奥側のcontactのみが反応している場合Receiverを内側に動かす
                elif self.contacts[0] == 0 and self.contacts[1] > 0:
                    t = 0
                    self.__move_receiver_in()
                    if self.get_distance_lock.locked():
                        self.get_distance_lock.release()
                # 両方のcontactが反応していない場合初期化する
                else:
                    t = 0
                    if not self.get_distance_lock.locked():
                        self.get_distance_lock.acquire()
                    print(f"[{current_thread().name}]{self.index}-satellite yet initializing in process contacts", flush=True)
                    th = Thread(target=self.__init_receiver, daemon=True)
                    th.start()
                    th.join()
                    print(f"[{current_thread().name}]{self.index}-satellite end initializing in process contacts", flush=True)
            t += 1
            if t == 1000:
                print(f"[{current_thread().name}]{self.index}-satellite waiting contacts...: {state}", flush=True)
                t = 0
            sleep(0.01)

    def __move_receiver_out(self):
        m = (self.movement + Satellite.RECEIVER_R / 2) / 1000
        print(f"[{current_thread().name}]{self.index}-satellite move to 'out': {self.movement} -> {m}", flush=True)
        self.client.send_message(self.movement_address, m)

    def __move_receiver_in(self):
        m = (self.movement - Satellite.RECEIVER_R / 2) / 1000
        print(f"[{current_thread().name}]{self.index}-satellite move to 'in': {self.movement} -> {m}", flush=True)
        self.client.send_message(self.movement_address, m)
