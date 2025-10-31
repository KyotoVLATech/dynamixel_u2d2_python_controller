"""
BulkWriteを使った位置・電流同時制御サンプル

このサンプルは、GroupBulkWriteを使って複数のモーターに対して
「目標位置」と「目標電流(電流制限)」を同時に設定する例を示しています。

電流ベース位置制御モード(CURRENT_BASED_POSITION_CONTROL)を使用することで、
位置制御と同時に電流制限を設定でき、より精密で安全な制御が可能になります。

注意: 実際の環境に合わせて以下を変更してください:
- ポート名 (Windows では "COM3" など、Linux/Mac では "/dev/ttyUSB0" など)
- モーターID
- ボーレート
- 目標位置と電流制限値
"""

import asyncio
import logging
import sys
from pathlib import Path

# プロジェクトのsrcディレクトリをパスに追加
sys.path.append(str(Path(__file__).parent.parent))

from constants import (  # noqa: E402
    Baudrate,
    ControlParams,
    DynamixelSeries,
    OperatingMode,
)
from dynamixel import Dynamixel, DynamixelController  # noqa: E402

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def main() -> None:
    # 電流ベースの位置制御モードを使用するパラメータ
    current_pos_params = ControlParams(
        ctrl_mode=OperatingMode.CURRENT_BASED_POSITION_CONTROL, offset=0
    )

    # モーターの定義
    motor1 = Dynamixel(DynamixelSeries.XM430_W350, 1, current_pos_params)
    motor2 = Dynamixel(DynamixelSeries.XM430_W350, 2, current_pos_params)

    # コントローラーの作成
    # ポート名は実際の環境に合わせて変更してください
    controller = DynamixelController(
        "COM3",  # Windows の場合。Linux/Mac では "/dev/ttyUSB0" など
        [motor1, motor2],
        baudrate=Baudrate.BAUD_57600,
    )

    try:
        # async with でコントローラーを初期化・接続
        # __aenter__ が呼ばれ、モードが「CURRENT_BASED_POSITION_CONTROL」に設定されます
        async with controller:
            logger.info(
                "Controller connected with CURRENT_BASED_POSITION_CONTROL mode."
            )

            # 1. 現在位置を取得
            positions = await controller.get_present_positions_async()
            logger.info(f"Current positions: {positions}")

            await asyncio.sleep(0.5)

            # 2. BulkWriteで目標位置と目標電流を同時に設定
            # 辞書の形式: { motor_id: (position, current_limit) }
            # 注: current_limit の単位はDynamixel内部単位です
            #     XM430では約2.69mA/unit なので、例えば500mA ≈ 186 units

            # 例: モーター1は位置2000、電流制限186units(約500mA)
            #     モーター2は位置3000、電流制限112units(約300mA)
            goals = {1: (2000, 186), 2: (3000, 112)}

            await controller.set_position_and_current_goals_async(goals)
            logger.info(f"BulkWrite: Position and Current goals set: {goals}")

            await asyncio.sleep(3.0)  # モーターが移動するのを待つ

            # 3. 移動後の位置を確認
            new_positions = await controller.get_present_positions_async()
            logger.info(f"New positions: {new_positions}")

            await asyncio.sleep(0.5)

            # 4. 別の目標値を設定（より大きな電流制限で高速移動）
            # モーター1は位置1000、電流制限372units(約1000mA)
            # モーター2は位置1500、電流制限372units(約1000mA)
            goals2 = {1: (1000, 372), 2: (1500, 372)}

            await controller.set_position_and_current_goals_async(goals2)
            logger.info(f"BulkWrite: New goals set: {goals2}")

            await asyncio.sleep(3.0)

            # 5. 最終位置を確認
            final_positions = await controller.get_present_positions_async()
            logger.info(f"Final positions: {final_positions}")

        # async with ブロックを抜けると、自動的にトルクOFFとポートクローズが実行されます
        logger.info("Successfully completed bulk write control.")

    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
