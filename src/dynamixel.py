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
# Improved logger configuration
logger = getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler_format = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler = StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(handler_format)
logger.addHandler(stream_handler)


class Dynamixel:
    def __init__(self, port: str, motor_id: int):
        self.port = port
        self.motor_id = motor_id
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

    def _write_4byte(self, address: int, value: int) -> bool:
        """4バイトのデータを書き込みます。"""
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

    def _read_4byte(self) -> tuple[int, bool]:
        """4バイトのデータを読み取ります。"""
        value, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(
            self.portHandler, self.motor_id, ControlTable.ADDR_PRESENT_POSITION
        )
        if dxl_comm_result != 0:
            logger.error(self.packetHandler.getTxRxResult(dxl_comm_result))
            return 0, False
        if dxl_error != 0:
            logger.error(self.packetHandler.getRxPacketError(dxl_error))
            return 0, False
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
        return self._read_4byte()

    def __enter__(self) -> 'Dynamixel':
        """with構文の開始時に接続とトルクONを行います。"""
        if not self.connect():
            raise IOError("Failed to connect to Dynamixel.")
        # デフォルトで位置制御モードに設定
        self.set_operating_mode(OperatingMode.POSITION_CONTROL)
        if not self.enable_torque():
            self.disconnect()
            raise IOError("Failed to enable torque.")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """with構文の終了時にトルクOFFと切断を行います。"""
        logger.info("Safely shutting down...")
        self.disable_torque()
        time.sleep(0.1)
        self.disconnect()
