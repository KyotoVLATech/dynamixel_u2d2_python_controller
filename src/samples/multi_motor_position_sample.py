import math
import time

from src.constants import DynamixelLimits, DynamixelSeries, OperatingMode
from src.dynamixel import Dynamixel, DynamixelController

# --- 設定項目 ---
DEVICENAME = "COM7"
MOTOR_IDS = [
    # 5,
    # 6,
    7,
    # 8,
]  # 制御する4つのモーターID
# -----------------


def create_dynamixel_motors() -> list[Dynamixel]:
    """4つのDynamixelモーターオブジェクトを作成します。"""
    # 基本的な制限値を設定（必要に応じて調整してください）
    limits = DynamixelLimits(
        max_pwm=885,
        max_current=1193,
        max_velocity=1000,
        max_position=4095,
        min_position=0,
    )

    motors = []
    for motor_id in MOTOR_IDS:
        motor = Dynamixel(series=DynamixelSeries.XM430_W350, id=motor_id, limits=limits)
        motors.append(motor)

    return motors


def main() -> None:
    """
    4つのDynamixelモーターを位置制御モードで同時制御するサンプル。
    """
    print("--- Multi-Motor Dynamixel Position Control Sample ---")

    try:
        # Dynamixelモーターリストを作成
        motors = create_dynamixel_motors()

        # DynamixelControllerの初期化
        with DynamixelController(
            port=DEVICENAME,
            motors=motors,
            operating_mode=OperatingMode.POSITION_CONTROL,
        ) as controller:

            print("✅ Connection successful. All motors are ready to move.")

            # 全モーター共通の目標角度パターンを定義: 0 -> π/4 -> 0
            target_angles = [0.0, math.pi / 4, 0.0]
            step_names = [
                "Initial Position (0 rad)",
                "Middle Position (π/4 rad)",
                "Return to Start (0 rad)",
            ]

            for step, target_angle in enumerate(target_angles):
                print(f"\n🎯 Step {step + 1}: {step_names[step]}")
                print(
                    f"   Target angle: {target_angle:.3f} rad ({math.degrees(target_angle):.1f}°)"
                )

                # 全てのモーターに同じ目標位置を同時設定
                for motor_id in MOTOR_IDS:
                    if not controller.set_goal_position_rad(motor_id, target_angle):
                        print(
                            f"Failed to set goal position for motor ID {motor_id}. Exiting."
                        )
                        return

                # 全てのモーターが目標位置に到達するまで監視
                print("\n📊 Position monitoring:")
                while True:
                    all_reached = True
                    status_line = ""

                    for motor_id in MOTOR_IDS:
                        present_pos_rad, success = controller.get_present_position_rad(
                            motor_id
                        )
                        if not success:
                            print(
                                f"Failed to get present position for motor ID {motor_id}."
                            )
                            break

                        position_error = abs(target_angle - present_pos_rad)

                        # 各モーターの状態を表示
                        status_line += f"[ID{motor_id}] {present_pos_rad:.3f}rad "

                        # radian値での位置差を計算（約0.02rad = 1.15°の精度）
                        if position_error > 0.02:
                            all_reached = False

                    print(f"  {status_line}")

                    if all_reached:
                        print("  ✅ All motors reached their goal positions.")
                        break

                    time.sleep(0.1)

                # 次のステップまで待機
                if step < len(target_angles) - 1:  # 最後のステップでは待機しない
                    print("  ⏰ Waiting for 3 seconds before next step...")
                    time.sleep(3.0)

            print("\n🎉 Multi-motor test sequence finished successfully!")

            # 最終位置の確認
            print("\n📋 Final positions:")
            for motor_id in MOTOR_IDS:
                final_pos_rad, success = controller.get_present_position_rad(motor_id)
                if success:
                    print(
                        f"  Motor ID {motor_id}: {final_pos_rad:.3f} rad ({math.degrees(final_pos_rad):.1f}°)"
                    )

    except IOError as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
# python -m src.samples.multi_motor_position_sample
