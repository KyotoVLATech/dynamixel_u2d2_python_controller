import logging
import time
from logging import Formatter, StreamHandler, getLogger
from typing import Any

from dynamixel_sdk import PacketHandler, PortHandler

from .constants import (
    Baudrate,
    ControlParams,
    DynamixelParams,
    DynamixelSeries,
    OperatingMode,
    ProtocolVersion,
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
    def __init__(self, series: DynamixelSeries, id: int, param: ControlParams):
        self.dynamixel_params: DynamixelParams = DynamixelParams(series)
        self.control_params: ControlParams = param
        self.id: int = id


class DynamixelController:
    def __init__(
        self,
        port: str,
        motors: list[Dynamixel],
        protocol_version: ProtocolVersion = ProtocolVersion.V2_0,
        baudrate: Baudrate = Baudrate.BAUD_57600,
    ):
        self.port = port
        self.motors = {motor.id: motor for motor in motors}  # IDをキーとする辞書
        self.portHandler = PortHandler(self.port)
        self.packetHandler = PacketHandler(protocol_version)
        self.baudrate = baudrate

    def connect(self) -> bool:
        """シリアルポートを開き、全てのモーターとの接続を確認します。"""
        logger.info(f"Connecting to port {self.port} at {self.baudrate.value} bps...")
        if not self.portHandler.openPort():
            logger.error("Failed to open the port.")
            return False
        if not self.portHandler.setBaudRate(self.baudrate.value):
            logger.error("Failed to change the baudrate.")
            return False

        # 全てのモーターとの接続を確認
        for motor_id in self.motors.keys():
            _, success = self._read_2byte(
                motor_id,
                self.motors[motor_id].dynamixel_params.param.ADDR_PRESENT_POSITION,
            )
            if not success:
                logger.error(f"Failed to connect to motor ID {motor_id}")
                return False
            logger.info(f"Successfully connected to motor ID {motor_id}")

        logger.info("Successfully connected to all motors.")
        return True

    def disconnect(self) -> None:
        """シリアルポートを閉じます。"""
        if self.portHandler.is_open:
            self.portHandler.closePort()
            logger.info("Serial port closed.")

    def _write_1byte(self, motor_id: int, address: int, value: int) -> bool:
        """1バイトのデータを書き込みます。"""
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(
            self.portHandler, motor_id, address, value
        )
        if dxl_comm_result != 0:
            logger.error(self.packetHandler.getTxRxResult(dxl_comm_result))
            return False
        if dxl_error != 0:
            logger.error(self.packetHandler.getRxPacketError(dxl_error))
            return False
        return True

    def _write_2byte(self, motor_id: int, address: int, value: int) -> bool:
        """2バイトのデータを書き込みます。"""
        # 符号付き16bit整数に対応
        if value < 0:
            value = value + 65536

        dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(
            self.portHandler, motor_id, address, value
        )
        if dxl_comm_result != 0:
            logger.error(self.packetHandler.getTxRxResult(dxl_comm_result))
            return False
        if dxl_error != 0:
            logger.error(self.packetHandler.getRxPacketError(dxl_error))
            return False
        return True

    def _read_2byte(self, motor_id: int, address: int) -> tuple[int, bool]:
        """指定したアドレスから2バイトのデータを読み取ります。"""
        value, dxl_comm_result, dxl_error = self.packetHandler.read2ByteTxRx(
            self.portHandler, motor_id, address
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

    def _write_4byte(self, motor_id: int, address: int, value: int) -> bool:
        """4バイトのデータを書き込みます。"""
        # 符号付き32bit整数に対応するため、負の値の場合は変換を行う
        if value < 0:
            value = value + 4294967296

        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(
            self.portHandler, motor_id, address, value
        )
        if dxl_comm_result != 0:
            logger.error(self.packetHandler.getTxRxResult(dxl_comm_result))
            return False
        if dxl_error != 0:
            logger.error(self.packetHandler.getRxPacketError(dxl_error))
            return False
        return True

    def _read_4byte(self, motor_id: int, address: int) -> tuple[int, bool]:
        """指定したアドレスから4バイトのデータを読み取ります。"""
        value, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(
            self.portHandler, motor_id, address
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

    def set_operating_mode(self, motor_id: int, mode: OperatingMode) -> bool:
        """オペレーティングモードを設定します。トルクOFFの状態で呼び出す必要があります。"""
        logger.info(f"Setting operating mode to {mode.name} for motor ID {motor_id}...")
        return self._write_1byte(
            motor_id,
            self.motors[motor_id].dynamixel_params.param.ADDR_OPERATING_MODE,
            mode.value,
        )

    def enable_torque(self, motor_id: int) -> bool:
        """モーターのトルクを有効にします。"""
        logger.info(f"Enabling torque for motor ID {motor_id}...")
        return self._write_1byte(
            motor_id,
            self.motors[motor_id].dynamixel_params.param.ADDR_TORQUE_ENABLE,
            self.motors[motor_id].dynamixel_params.param.TORQUE_ENABLE,
        )

    def disable_torque(self, motor_id: int) -> bool:
        """モーターのトルクを無効にします。"""
        logger.info(f"Disabling torque for motor ID {motor_id}...")
        return self._write_1byte(
            motor_id,
            self.motors[motor_id].dynamixel_params.param.ADDR_TORQUE_ENABLE,
            self.motors[motor_id].dynamixel_params.param.TORQUE_DISABLE,
        )

    def set_goal_position(self, motor_id: int, position: int) -> bool:
        """目標位置を設定します。"""
        logger.info(f"Setting goal position to {position} for motor ID {motor_id}")
        return self._write_4byte(
            motor_id,
            self.motors[motor_id].dynamixel_params.param.ADDR_GOAL_POSITION,
            position + self.motors[motor_id].control_params.offset,
        )

    def get_present_position(self, motor_id: int) -> tuple[int, bool]:
        """現在の位置を取得します。"""
        val = self._read_4byte(
            motor_id,
            self.motors[motor_id].dynamixel_params.param.ADDR_PRESENT_POSITION,
        )
        return (val - self.motors[motor_id].control_params.offset, True)

    def set_goal_velocity(self, motor_id: int, velocity: int) -> bool:
        """目標速度を設定します。"""
        logger.info(f"Setting goal velocity to {velocity} for motor ID {motor_id}")
        return self._write_4byte(
            motor_id,
            self.motors[motor_id].dynamixel_params.param.ADDR_GOAL_VELOCITY,
            velocity,
        )

    def get_present_velocity(self, motor_id: int) -> tuple[int, bool]:
        """現在の速度を取得します。"""
        return self._read_4byte(
            motor_id,
            self.motors[motor_id].dynamixel_params.param.ADDR_PRESENT_VELOCITY,
        )

    def pulse_to_radian(self, pulse: int, pulse_per_revolution: int) -> float:
        """パルス値をradian値に変換します."""
        return (pulse / pulse_per_revolution) * 2 * 3.14159265359

    def radian_to_pulse(self, radian: float, pulse_per_revolution: int) -> int:
        """radian値をパルス値に変換します."""
        pulse = int((radian / (2 * 3.14159265359)) * pulse_per_revolution)
        return pulse

    def set_goal_position_rad(self, motor_id: int, position_rad: float) -> bool:
        """目標位置をradian値で設定します."""
        pulse_position = self.radian_to_pulse(
            position_rad,
            self.motors[motor_id].dynamixel_params.param.PULSE_PER_REVOLUTION,
        )
        logger.info(
            f"Setting goal position to {position_rad:.3f} rad ({pulse_position} pulse) for motor ID {motor_id}"
        )
        return self._write_4byte(
            motor_id,
            self.motors[motor_id].dynamixel_params.param.ADDR_GOAL_POSITION,
            pulse_position + self.motors[motor_id].control_params.offset,
        )

    def get_present_position_rad(self, motor_id: int) -> tuple[float, bool]:
        """現在の位置をradian値で取得します."""
        pulse_position, success = self._read_4byte(
            motor_id,
            self.motors[motor_id].dynamixel_params.param.ADDR_PRESENT_POSITION,
        )
        if success:
            radian_position = self.pulse_to_radian(
                pulse_position - self.motors[motor_id].control_params.offset,
                self.motors[motor_id].dynamixel_params.param.PULSE_PER_REVOLUTION,
            )
            return radian_position, True
        return 0.0, False

    def __enter__(self) -> 'DynamixelController':
        """with構文の開始時に接続と全モーターのトルクONを行います。"""
        if not self.connect():
            raise IOError("Failed to connect to Dynamixel.")

        # 全てのモーターに対してオペレーティングモードを設定してトルクを有効化
        for motor_id in self.motors.keys():
            if not self.set_operating_mode(
                motor_id, self.motors[motor_id].control_params.ctrl_mode
            ):
                self.disconnect()
                raise IOError(
                    f"Failed to set operating mode to {self.motors[motor_id].control_params.ctrl_mode.name} for motor ID {motor_id}."
                )
            if not self.enable_torque(motor_id):
                self.disconnect()
                raise IOError(f"Failed to enable torque for motor ID {motor_id}.")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """with構文の終了時に全モーターを停止し、トルクOFFと切断を行います。"""
        logger.info("Safely shutting down...")

        # 全てのモーターを安全に停止させる
        for motor_id in self.motors.keys():
            if (
                self.motors[motor_id].control_params.ctrl_mode
                == OperatingMode.VELOCITY_CONTROL
            ):
                self.set_goal_velocity(motor_id, 0)

        time.sleep(0.2)  # 停止命令が反映されるのを待つ

        # 全てのモーターのトルクを無効化
        for motor_id in self.motors.keys():
            self.disable_torque(motor_id)

        time.sleep(0.1)
        self.disconnect()
