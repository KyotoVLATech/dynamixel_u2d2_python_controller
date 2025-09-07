import time

from src.constants import OperatingMode  # OperatingModeをインポート
from src.constants import (
    DXL_MAXIMUM_POSITION_VALUE,
    DXL_MINIMUM_POSITION_VALUE,
    DXL_MOVING_STATUS_THRESHOLD,
)
from src.dynamixel import Dynamixel

# --- 設定項目 ---
DEVICENAME = "COM4"
DXL_ID = 1
# -----------------


def main() -> None:
    """
    Dynamixelモーターを位置制御モードで動作させるサンプル。
    """
    print("--- Dynamixel Position Control Sample ---")

    try:
        # Dynamixelの初期化時にオペレーティングモードを指定
        with Dynamixel(
            port=DEVICENAME,
            motor_id=DXL_ID,
            operating_mode=OperatingMode.POSITION_CONTROL,
        ) as motor:

            print("\n✅ Connection successful. Motor is ready to move.")

            goal_positions = [DXL_MINIMUM_POSITION_VALUE, DXL_MAXIMUM_POSITION_VALUE]

            for i in range(2):
                for goal_pos in goal_positions:
                    if not motor.set_goal_position(goal_pos):
                        print("Failed to set goal position. Exiting.")
                        return

                    while True:
                        present_pos, success = motor.get_present_position()
                        if not success:
                            print("Failed to get present position.")
                            break

                        print(
                            f"[ID:{DXL_ID:03d}] GoalPos:{goal_pos:03d}  PresPos:{present_pos:03d}"
                        )

                        if abs(goal_pos - present_pos) <= DXL_MOVING_STATUS_THRESHOLD:
                            print("  -> Reached goal position.")
                            break
                        time.sleep(0.1)
                    time.sleep(0.5)

            print("\nSample sequence finished successfully.")

    except IOError as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
# python -m src.samples.position_sample
