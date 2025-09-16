import enum
from dataclasses import dataclass


class DynamixelSeries(enum.Enum):
    """Dynamixelシリーズの列挙型"""

    XM430_W350 = 1
    XM540_W270 = 2
    # 他のシリーズもここに追加可能


@dataclass
class Param:
    """
    Dynamixel XM430-W350-Rのパラメータ
    """

    # Control Table Addresses #
    ADDR_TORQUE_ENABLE = 64
    ADDR_OPERATING_MODE = 11

    # Position Control
    ADDR_GOAL_POSITION = 116
    ADDR_PRESENT_POSITION = 132

    # Velocity Control
    ADDR_GOAL_VELOCITY = 104
    ADDR_PRESENT_VELOCITY = 128

    # PWM Control
    ADDR_GOAL_PWM = 100
    ADDR_PRESENT_PWM = 124

    # Current Control
    ADDR_GOAL_CURRENT = 102
    ADDR_PRESENT_CURRENT = 126
    ###############################

    # Dynamixel Parameters #
    TORQUE_ENABLE = 1
    TORQUE_DISABLE = 0
    RESOLUTION = 4096  # 0-4095 (12-bit)
    PULSE_PER_REVOLUTION = 4096  # 1回転あたりのパルス数


@dataclass
class DynamixelLimits:
    """Dynamixelモーターの制限値"""

    max_pwm: int
    max_current: int
    max_velocity: int
    max_position: int
    min_position: int
    pulse_per_revolution: int
    max_pulse: int


class DynamixelParams:
    """Dynamixelモーターの基本クラス"""

    def __init__(self, series: DynamixelSeries):
        self.series = series
        # 他の初期化コード

    @property
    def control_table(self) -> Param:
        """Dynamixelシリーズに応じたコントロールテーブルを返す"""
        if self.series == DynamixelSeries.XM430_W350:
            return Param()
        elif self.series == DynamixelSeries.XM540_W270:
            return Param()
        else:
            raise ValueError("Unsupported Dynamixel series")


class OperatingMode(enum.Enum):
    """
    Dynamixelのオペレーティングモード
    """

    CURRENT_CONTROL = 0
    VELOCITY_CONTROL = 1
    POSITION_CONTROL = 3
    EXTENDED_POSITION_CONTROL = 4
    CURRENT_BASED_POSITION_CONTROL = 5
    PWM_CONTROL = 16


# --- Protocol Constants ---
PROTOCOL_VERSION = 2.0
BAUDRATE = 57600

# --- Torque Constants ---
TORQUE_ENABLE = 1
TORQUE_DISABLE = 0

# --- Position Constants ---
DXL_MINIMUM_POSITION_VALUE = 1000
DXL_MAXIMUM_POSITION_VALUE = 3000
DXL_MOVING_STATUS_THRESHOLD = 20

# --- Default Limits (for safe sample codes) ---
# XM430-W350のPWMリミットの初期値は885
SAFE_PWM_VALUE = 150
# XM430-W350の電流リミットの初期値は1193 (約3.2A)
SAFE_CURRENT_VALUE = 40  # 約108mAに相当 (40 * 2.69mA)
