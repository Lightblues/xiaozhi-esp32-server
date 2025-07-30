""" -------------------------------------------------------
- 服务启动: 两个异步任务
- 信号/服务管理: 这里的 wait_for_exit 配置为永久等待
"""

import sys
import signal
import asyncio
from aioconsole import ainput

from .http_server import SimpleHttpServer
from .websocket_server import WebSocketServer


async def wait_for_exit() -> None:
    """
    阻塞直到收到 Ctrl‑C / SIGTERM。
    - Unix: 使用 add_signal_handler
    - Windows: 依赖 KeyboardInterrupt
    """
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    if sys.platform != "win32":  # Unix / macOS
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, stop_event.set)
        await stop_event.wait()
    else:
        # Windows：await一个永远pending的fut，
        # 让 KeyboardInterrupt 冒泡到 asyncio.run，以此消除遗留普通线程导致进程退出阻塞的问题
        try:
            await asyncio.Future()
        except KeyboardInterrupt:  # Ctrl‑C
            pass

async def monitor_stdin():
    """监控标准输入，消费回车键"""
    while True:
        await ainput()  # 异步等待输入，消费回车

async def main():
    config = load_config()

    # 添加 stdin 监控任务
    stdin_task = asyncio.create_task(monitor_stdin())
    # 启动 WebSocket 服务器
    ws_server = WebSocketServer(config)
    ws_task = asyncio.create_task(ws_server.start())
    # 启动 Simple http 服务器
    ota_server = SimpleHttpServer(config)
    ota_task = asyncio.create_task(ota_server.start())

    try:
        await wait_for_exit()  # 阻塞直到收到退出信号
    except asyncio.CancelledError:
        print("任务被取消，清理资源中...")
    finally:
        # 取消所有任务
        stdin_task.cancel()
        ws_task.cancel()
        ota_task.cancel()

        # 等待任务终止（必须加超时）
        await asyncio.wait(
            [stdin_task, ws_task, ota_task],
            timeout=3.0,
            return_when=asyncio.ALL_COMPLETED,
        )