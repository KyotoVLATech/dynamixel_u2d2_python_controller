# Dynamixel U2D2 Python Controller

Dynamixel XM430-W350-R用のPythonコントローラーライブラリです。非同期処理(asyncio)とGroupSync機能に対応し、複数のバスでの並行操作が可能です。

## 前提条件
- Windows 11
- Dynamixel XM430-W350-R
- U2D2
- Pythonパッケージマネージャにuvを使用

## 使用方法
1. このレポジトリをクローンして移動
2. `uv sync` でパッケージをインストール
3. U2D2をDynamixelに接続し、モーターには電源を供給
4. samples/以下のコードが使用可能です

## 主な機能

### 非同期処理対応
- `asyncio`を使用した非同期I/O処理
- 複数バスでの並行操作が可能
- `async with` 構文によるコンテキスト管理

### GroupSync機能
- GroupSyncWrite: 複数モーターへの一斉送信
- GroupSyncRead: 複数モーターからの一斉受信
- 効率的な通信による高速制御

### 非同期メソッド
- `set_goal_positions_async()`: 複数モーターに目標位置を一斉送信
- `get_present_positions_async()`: 複数モーターから現在位置を一斉受信
- `set_torque_enable_async()`: 複数モーターのトルクON/OFFを一斉送信
- `set_goal_velocities_async()`: 複数モーターに目標速度を一斉送信

## サンプルコード

### 単一バスでの非同期位置制御
```python
import asyncio
from dynamixel import DynamixelController, Dynamixel
from constants import DynamixelSeries, ControlParams, Baudrate

async def main():
    motor1 = Dynamixel(DynamixelSeries.XM430_W350, 1, ControlParams())
    motor2 = Dynamixel(DynamixelSeries.XM430_W350, 2, ControlParams())
    
    controller = DynamixelController("COM3", [motor1, motor2], baudrate=Baudrate.BAUD_57600)
    
    async with controller:
        # 現在位置を取得
        positions = await controller.get_present_positions_async()
        print(f"Current positions: {positions}")
        
        # 目標位置を設定 (複数モーターに一斉送信)
        goal_positions = {1: 1000, 2: 3000}
        await controller.set_goal_positions_async(goal_positions)
        
        await asyncio.sleep(2.0)

if __name__ == "__main__":
    asyncio.run(main())
```

### 複数バスでの並行操作
```python
import asyncio
from dynamixel import DynamixelController, Dynamixel
from constants import DynamixelSeries, ControlParams, Baudrate

async def main():
    # バスA (COM3)
    controller_A = DynamixelController("COM3", [...], baudrate=Baudrate.BAUD_57600)
    # バスB (COM4)
    controller_B = DynamixelController("COM4", [...], baudrate=Baudrate.BAUD_57600)
    
    async with controller_A, controller_B:
        # 両バスの位置を同時に取得
        positions_A, positions_B = await asyncio.gather(
            controller_A.get_present_positions_async(),
            controller_B.get_present_positions_async()
        )
        
        # 両バスに同時に目標位置を送信
        await asyncio.gather(
            controller_A.set_goal_positions_async({1: 1000, 2: 1500}),
            controller_B.set_goal_positions_async({10: 3000, 11: 2500})
        )

if __name__ == "__main__":
    asyncio.run(main())
```

詳細なサンプルは `src/samples/` ディレクトリを参照してください:
- `async_position_sample.py`: 単一バスでの非同期位置制御
- `async_multi_bus_sample.py`: 複数バスでの並行操作
- `position_sample.py`: 従来の同期的な位置制御
- `velocity_sample.py`: 速度制御サンプル
- `multi_motor_position_sample.py`: 複数モーター位置制御サンプル

## 既存コードとの互換性

従来の同期的なメソッド(`connect()`, `disconnect()`, `set_goal_position()` など)も引き続き使用できます。新しい非同期機能は追加機能として提供されています。
