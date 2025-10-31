"""
非同期処理を使った単一バスでの位置制御サンプル

このサンプルは、async/awaitを使ってDynamixelモーターを制御する基本的な例を示しています。
複数のモーターに一斉送信で目標位置を設定し、現在位置を一斉受信で取得します。

注意: 実際の環境に合わせて以下を変更してください:
- ポート名 (Windows では "COM3" など、Linux/Mac では "/dev/ttyUSB0" など)
- モーターID
- ボーレート
"""

import asyncio
import logging

from src.constants import Baudrate, ControlParams, DynamixelSeries
from src.dynamixel import Dynamixel, DynamixelController

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def main() -> None:
    # モーターの定義
    motor1 = Dynamixel(DynamixelSeries.XM430_W350, 1, ControlParams())
    # motor2 = Dynamixel(DynamixelSeries.XM430_W350, 2, ControlParams())

    # コントローラーの作成
    # ポート名は実際の環境に合わせて変更してください
    controller = DynamixelController(
        "COM4",  # Windows の場合。Linux/Mac では "/dev/ttyUSB0" など
        [
            motor1,
            #  motor2
        ],
        baudrate=Baudrate.BAUD_57600,
    )

    try:
        # async with でコントローラーを初期化・接続
        async with controller:
            logger.info("Controller connected and motors torqued on.")

            # 1. 現在位置を取得
            positions = await controller.get_present_positions_async()
            logger.info(f"Current positions: {positions}")

            await asyncio.sleep(0.5)

            # 2. 目標位置を設定 (複数モーターに一斉送信)
            goal_positions = {
                1: 1000,  # モーターID 1 を位置 1000 に移動
                2: 3000,  # モーターID 2 を位置 3000 に移動
            }
            await controller.set_goal_positions_async(goal_positions)
            logger.info(f"Goal positions set: {goal_positions}")

            await asyncio.sleep(2.0)  # モーターが移動するのを待つ

            # 3. 移動後の位置を確認
            new_positions = await controller.get_present_positions_async()
            logger.info(f"New positions: {new_positions}")

            await asyncio.sleep(0.5)

            # 4. 元の位置に戻す
            logger.info("Returning to original positions...")
            original_positions = {
                1: positions.get(1, 2048),
                2: positions.get(2, 2048),
            }
            await controller.set_goal_positions_async(original_positions)

            await asyncio.sleep(2.0)

            # 5. 最終位置を確認
            final_positions = await controller.get_present_positions_async()
            logger.info(f"Final positions: {final_positions}")

        # async with ブロックを抜けると、自動的にトルクOFFとポートクローズが実行されます
        logger.info("Successfully completed position control.")

    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
