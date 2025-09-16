import math
import time

from src.constants import OperatingMode  # OperatingModeをインポート
from src.dynamixel import Dynamixel

# --- 設定項目 ---
DEVICENAME = "COM7"
DXL_ID = 7
# -----------------


def main() -> None:
    """
    Dynamixelモーターを位置制御モードで指定されたradian角度に移動させるサンプル。
    """
    print("--- Dynamixel Position Control Sample (Radian) ---")

    try:
        # Dynamixelの初期化時にオペレーティングモードを指定
        with Dynamixel(
            port=DEVICENAME,
            motor_id=DXL_ID,
            operating_mode=OperatingMode.POSITION_CONTROL,
        ) as motor:

            print("\n✅ Connection successful. Motor is ready to move.")

            # 目標角度をradianで指定
            goal_angles_rad = [0.0, math.pi / 2, math.pi, 3 * math.pi / 2, 2 * math.pi]

            for angle_rad in goal_angles_rad:
                print(
                    f"\n🎯 Moving to {angle_rad:.3f} rad ({math.degrees(angle_rad):.1f}°)"
                )

                if not motor.set_goal_position_rad(angle_rad):
                    print("Failed to set goal position. Exiting.")
                    return

                # 目標位置に到達するまで待機
                while True:
                    present_pos_rad, success = motor.get_present_position_rad()
                    if not success:
                        print("Failed to get present position.")
                        break

                    print(
                        f"[ID:{DXL_ID:03d}] Goal:{angle_rad:.3f}rad  Present:{present_pos_rad:.3f}rad"
                    )

                    # radian値での位置差を計算（約0.01rad = 0.57°の精度）
                    if abs(angle_rad - present_pos_rad) <= 0.01:
                        print("  -> Reached goal position.")
                        break
                    time.sleep(0.1)

                # 3秒間待機
                print("  ⏰ Waiting for 3 seconds...")
                time.sleep(3.0)

            print("\nSample sequence finished successfully.")

    except IOError as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
# python -m src.samples.position_sample
