import logging
import time
from logging import Formatter, StreamHandler, getLogger
from typing import Any

from dynamixel_sdk import PacketHandler, PortHandler

from src.constants import (
    BAUDRATE,
    PROTOCOL_VERSION,
    TORQUE_DISABLE,
    TORQUE_ENABLE,
    ControlTable,
    OperatingMode,
)

# Logger configuration
logger = getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler_format = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler = StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(handler_format)
logger.addHandler(stream_handler)


class Dynamixel:
    def __init__(
        self,
        port: str,
        motor_id: int,
        operating_mode: OperatingMode = OperatingMode.POSITION_CONTROL,
    ):
        self.port = port
        self.motor_id = motor_id
        self.operating_mode = operating_mode  # モードをインスタンス変数として保持
        self.portHandler = PortHandler(self.port)
        self.packetHandler = PacketHandler(PROTOCOL_VERSION)

    def connect(self) -> bool:
        """シリアルポートを開き、ボーレートを設定して接続を試みます。"""
        logger.info(f"Connecting to port {self.port} at {BAUDRATE} bps...")
        if not self.portHandler.openPort():
            logger.error("Failed to open the port.")
            return False
        if not self.portHandler.setBaudRate(BAUDRATE):
            logger.error("Failed to change the baudrate.")
            return False
        logger.info("Successfully connected to the motor.")
        return True

    def disconnect(self) -> None:
        """シリアルポートを閉じます。"""
        if self.portHandler.is_open:
            self.portHandler.closePort()
            logger.info("Serial port closed.")

    def _write_1byte(self, address: int, value: int) -> bool:
        """1バイトのデータを書き込みます。"""
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(
            self.portHandler, self.motor_id, address, value
        )
        if dxl_comm_result != 0:
            logger.error(self.packetHandler.getTxRxResult(dxl_comm_result))
            return False
        if dxl_error != 0:
            logger.error(self.packetHandler.getRxPacketError(dxl_error))
            return False
        return True

    def _write_2byte(self, address: int, value: int) -> bool:
        """2バイトのデータを書き込みます。"""
        # 符号付き16bit整数に対応
        if value < 0:
            value = value + 65536

        dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(
            self.portHandler, self.motor_id, address, value
        )
        if dxl_comm_result != 0:
            logger.error(self.packetHandler.getTxRxResult(dxl_comm_result))
            return False
        if dxl_error != 0:
            logger.error(self.packetHandler.getRxPacketError(dxl_error))
            return False
        return True

    def _read_2byte(self, address: int) -> tuple[int, bool]:
        """指定したアドレスから2バイトのデータを読み取ります。"""
        value, dxl_comm_result, dxl_error = self.packetHandler.read2ByteTxRx(
            self.portHandler, self.motor_id, address
        )
        if dxl_comm_result != 0:
            logger.error(self.packetHandler.getTxRxResult(dxl_comm_result))
            return 0, False
        if dxl_error != 0:
            logger.error(self.packetHandler.getRxPacketError(dxl_error))
            return 0, False

        # 符号付き16bit整数に対応
        if value > 32767:
            value = value - 65536
        return value, True

    def _write_4byte(self, address: int, value: int) -> bool:
        """4バイトのデータを書き込みます。"""
        # 符号付き32bit整数に対応するため、負の値の場合は変換を行う
        if value < 0:
            value = value + 4294967296

        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(
            self.portHandler, self.motor_id, address, value
        )
        if dxl_comm_result != 0:
            logger.error(self.packetHandler.getTxRxResult(dxl_comm_result))
            return False
        if dxl_error != 0:
            logger.error(self.packetHandler.getRxPacketError(dxl_error))
            return False
        return True

    def _read_4byte(self, address: int) -> tuple[int, bool]:
        """指定したアドレスから4バイトのデータを読み取ります。"""
        value, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(
            self.portHandler, self.motor_id, address
        )
        if dxl_comm_result != 0:
            logger.error(self.packetHandler.getTxRxResult(dxl_comm_result))
            return 0, False
        if dxl_error != 0:
            logger.error(self.packetHandler.getRxPacketError(dxl_error))
            return 0, False

        # 符号付き32bit整数に対応するため、正の値に変換する
        if value > 2147483647:
            value = value - 4294967296
        return value, True

    def set_operating_mode(self, mode: OperatingMode) -> bool:
        """オペレーティングモードを設定します。トルクOFFの状態で呼び出す必要があります。"""
        logger.info(f"Setting operating mode to {mode.name}...")
        return self._write_1byte(ControlTable.ADDR_OPERATING_MODE, mode.value)

    def enable_torque(self) -> bool:
        """モーターのトルクを有効にします。"""
        logger.info("Enabling torque...")
        return self._write_1byte(ControlTable.ADDR_TORQUE_ENABLE, TORQUE_ENABLE)

    def disable_torque(self) -> bool:
        """モーターのトルクを無効にします。"""
        logger.info("Disabling torque...")
        return self._write_1byte(ControlTable.ADDR_TORQUE_ENABLE, TORQUE_DISABLE)

    def set_goal_position(self, position: int) -> bool:
        """目標位置を設定します。"""
        logger.info(f"Setting goal position to {position}")
        return self._write_4byte(ControlTable.ADDR_GOAL_POSITION, position)

    def get_present_position(self) -> tuple[int, bool]:
        """現在の位置を取得します。"""
        return self._read_4byte(ControlTable.ADDR_PRESENT_POSITION)

    def set_goal_velocity(self, velocity: int) -> bool:
        """目標速度を設定します。"""
        logger.info(f"Setting goal velocity to {velocity}")
        return self._write_4byte(ControlTable.ADDR_GOAL_VELOCITY, velocity)

    def get_present_velocity(self) -> tuple[int, bool]:
        """現在の速度を取得します。"""
        return self._read_4byte(ControlTable.ADDR_PRESENT_VELOCITY)

    def set_goal_pwm(self, pwm: int) -> bool:
        """目標PWMを設定します。"""
        logger.info(f"Setting goal PWM to {pwm}")
        return self._write_2byte(ControlTable.ADDR_GOAL_PWM, pwm)

    def get_present_pwm(self) -> tuple[int, bool]:
        """現在のPWMを取得します。"""
        return self._read_2byte(ControlTable.ADDR_PRESENT_PWM)

    def set_goal_current(self, current: int) -> bool:
        """目標電流を設定します。"""
        logger.info(f"Setting goal current to {current}")
        return self._write_2byte(ControlTable.ADDR_GOAL_CURRENT, current)

    def get_present_current(self) -> tuple[int, bool]:
        """現在の電流を取得します。"""
        return self._read_2byte(ControlTable.ADDR_PRESENT_CURRENT)

    def __enter__(self) -> 'Dynamixel':
        """with構文の開始時に接続とトルクONを行います。"""
        if not self.connect():
            raise IOError("Failed to connect to Dynamixel.")
        # 指定されたオペレーティングモードに設定
        if not self.set_operating_mode(self.operating_mode):
            self.disconnect()
            raise IOError(
                f"Failed to set operating mode to {self.operating_mode.name}."
            )
        if not self.enable_torque():
            self.disconnect()
            raise IOError("Failed to enable torque.")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """with構文の終了時にモーターを停止し、トルクOFFと切断を行います。"""
        logger.info("Safely shutting down...")

        # モードに応じて安全に停止させる
        if self.operating_mode == OperatingMode.VELOCITY_CONTROL:
            self.set_goal_velocity(0)
        elif self.operating_mode == OperatingMode.PWM_CONTROL:
            self.set_goal_pwm(0)
        elif self.operating_mode in [
            OperatingMode.CURRENT_CONTROL,
            OperatingMode.CURRENT_BASED_POSITION_CONTROL,
        ]:
            # 電流モードでは0に設定して力を抜く
            self.set_goal_current(0)

        time.sleep(0.2)  # 停止命令が反映されるのを待つ
        self.disable_torque()
        time.sleep(0.1)
        self.disconnect()
