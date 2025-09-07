import enum


class ControlTable:
    """
    Dynamixel XM430-W350-Rのコントロールテーブルアドレス
    """

    ADDR_TORQUE_ENABLE = 64
    ADDR_GOAL_POSITION = 116
    ADDR_PRESENT_POSITION = 132
    ADDR_OPERATING_MODE = 11


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
BAUDRATE = 57600  # Dynamixelのデフォルトボーレート

# --- Torque Constants ---
TORQUE_ENABLE = 1
TORQUE_DISABLE = 0

# --- Position Constants ---
# XM430-W350の分解能は4096
DXL_MINIMUM_POSITION_VALUE = 1000  # 揺動範囲の下限値
DXL_MAXIMUM_POSITION_VALUE = 3000  # 揺動範囲の上限値
DXL_MOVING_STATUS_THRESHOLD = 20  # この閾値以下になったら移動完了とみなす
