import time

from src.constants import OperatingMode
from src.dynamixel import Dynamixel

# --- 設定項目 ---
DEVICENAME = "COM4"
DXL_ID = 1
GOAL_VELOCITY_VALUE = 100  # 目標速度（0.229 rpm/unit）
# -----------------


def main() -> None:
    """
    Dynamixelモーターを速度制御モードで動作させるサンプル。
    正転 -> 停止 -> 逆転 -> 停止 を繰り返します。
    """
    print("--- Dynamixel Velocity Control Sample ---")

    try:
        # Dynamixelの初期化時にオペレーティングモードを速度制御に指定
        with Dynamixel(
            port=DEVICENAME,
            motor_id=DXL_ID,
            operating_mode=OperatingMode.VELOCITY_CONTROL,
        ) as motor:

            print("\n✅ Connection successful. Motor is ready to move.")

            velocities_to_test = [
                GOAL_VELOCITY_VALUE,  # 正転
                0,  # 停止
                -GOAL_VELOCITY_VALUE,  # 逆転
                0,  # 停止
            ]

            for goal_vel in velocities_to_test:
                print(f"\nSetting Goal Velocity to {goal_vel}...")

                # --- ステップ1: 目標速度を指令 ---
                if not motor.set_goal_velocity(goal_vel):
                    print("Failed to set goal velocity. Exiting.")
                    return

                # --- ステップ2: 2秒間、現在の速度をモニタリング ---
                start_time = time.time()
                while time.time() - start_time < 2.0:
                    present_vel, success = motor.get_present_velocity()
                    if not success:
                        print("Failed to get present velocity.")
                        break

                    print(
                        f"[ID:{DXL_ID:03d}] GoalVel:{goal_vel:04d}  PresVel:{present_vel:04d}"
                    )
                    time.sleep(0.1)

            print("\nSample sequence finished successfully.")

    except IOError as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
# python -m src.samples.velocity_sample
