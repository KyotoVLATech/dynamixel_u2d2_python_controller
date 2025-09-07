import time

from src.constants import (
    DXL_MAXIMUM_POSITION_VALUE,
    DXL_MINIMUM_POSITION_VALUE,
    DXL_MOVING_STATUS_THRESHOLD,
)
from src.dynamixel import Dynamixel

# --- 設定項目 ---
# ご自身の環境に合わせて変更してください
DEVICENAME = "COM13"  # Linuxの場合は"/dev/ttyUSB0"など
DXL_ID = 1  # 制御するモーターのID（デフォルト値は1）
# -----------------


def main() -> None:
    """
    Dynamixelモーターを位置制御モードで動作させるサンプル。
    with構文を使い、安全な接続・切断を保証します。
    """
    print("--- Dynamixel Position Control Sample ---")

    try:
        # with構文により、ブロックを抜ける際に自動でトルクOFFと切断が呼ばれます
        with Dynamixel(port=DEVICENAME, motor_id=DXL_ID) as motor:

            print("\n✅ Connection successful. Motor is ready to move.")

            goal_positions = [DXL_MINIMUM_POSITION_VALUE, DXL_MAXIMUM_POSITION_VALUE]

            for i in range(5):  # 5往復させる
                for goal_pos in goal_positions:
                    # --- ステップ1: 目標位置を指令 ---
                    if not motor.set_goal_position(goal_pos):
                        print("Failed to set goal position. Exiting.")
                        return

                    # --- ステップ2: 目標位置に到達するまで待機 ---
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

                        time.sleep(0.1)  # CPU負荷軽減のための短い待機

                    time.sleep(0.5)  # 次の動作までの待機

            print("\nSample sequence finished successfully.")

    except IOError as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
# python -m src.samples.position_sample
