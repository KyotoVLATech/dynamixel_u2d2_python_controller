import enum


class ControlTable:
    """
    Dynamixel XM430-W350-Rのコントロールテーブルアドレス
    """

    ADDR_TORQUE_ENABLE = 64
    ADDR_OPERATING_MODE = 11

    # Position Control
    ADDR_GOAL_POSITION = 116
    ADDR_PRESENT_POSITION = 132

    # Velocity Control
    ADDR_GOAL_VELOCITY = 104
    ADDR_PRESENT_VELOCITY = 128

    # --- 以下を追記 ---
    # PWM Control
    ADDR_GOAL_PWM = 100
    ADDR_PRESENT_PWM = 124

    # Current Control
    ADDR_GOAL_CURRENT = 102
    ADDR_PRESENT_CURRENT = 126


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
