import asyncio
import websockets

""" -------------------------------------------------------
WebSocketServer: 基于websockets库实现的WebSocket服务器
调度: 对于每次连接采用新的 ConnectionHandler
"""
class WebSocketServer:
    def __init__(self, config: dict):
        self.config = config
        self.active_connections = set()

    async def start(self):
        ...
        async with websockets.serve(
            self._handle_connection, host, port, process_request=self._http_response
        ):
            await asyncio.Future()

    async def _handle_connection(self, websocket):
        """处理新连接，每次创建独立的ConnectionHandler"""
        handler = ConnectionHandler(
            self.config,
            self._vad,
            self._asr,
            self._llm,
            self._memory,
            self._intent,
            self,  # 传入server实例
        )
        self.active_connections.add(handler)
        try:
            await handler.handle_connection(websocket)
        except Exception as e:
            self.logger.bind(tag=TAG).error(f"处理连接时出错: {e}")
        finally:
            # 确保从活动连接集合中移除
            self.active_connections.discard(handler)
            # 强制关闭连接（如果还没有关闭的话）
            ...

    async def _http_response(self, websocket, request_headers):
        # 检查是否为 WebSocket 升级请求
        if request_headers.headers.get("connection", "").lower() == "upgrade":
            # 如果是 WebSocket 请求，返回 None 允许握手继续
            return None
        else:
            # 如果是普通 HTTP 请求，返回 "server is running"
            return websocket.respond(200, "Server is running\n")



""" -------------------------------------------------------
ConnectionHandler: 处理WebSocket连接的类

TODO: 如何设计一个鲁棒的ws服务?
"""
import traceback
import threading
from concurrent.futures import ThreadPoolExecutor
from .auth import AuthMiddleware, AuthenticationError

class ConnectionHandler:
    def __init__(self, config: dict):
        # 线程任务相关
        self.loop = asyncio.get_event_loop()
        self.stop_event = threading.Event()
        self.executor = ThreadPoolExecutor(max_workers=5)

    async def handle_connection(self, ws):
        # TODO: 
        try:
            # 获取并验证headers
            await self.auth.authenticate(self.headers)
            self.websocket = ws
            self.device_id = self.headers.get("device-id", None)

            # 启动超时检查任务
            self.timeout_task = asyncio.create_task(self._check_timeout())

            # 异步初始化
            self.executor.submit(self._initialize_components)

            try:
                async for message in self.websocket:
                    await self._route_message(message)
            except websockets.exceptions.ConnectionClosed:
                self.logger.bind(tag=TAG).info("客户端断开连接")
        except AuthenticationError as e:
            self.logger.bind(tag=TAG).error(f"Authentication failed: {str(e)}")
            return
        except Exception as e:
            stack_trace = traceback.format_exc()
            self.logger.bind(tag=TAG).error(f"Connection error: {str(e)}-{stack_trace}")
            return
        finally:
            try:
                await self._save_and_close(ws)
            except Exception as final_error:
                self.logger.bind(tag=TAG).error(f"最终清理时出错: {final_error}")
                # 确保即使保存记忆失败，也要关闭连接
                try:
                    await self.close(ws)
                except Exception as close_error:
                    self.logger.bind(tag=TAG).error(f"强制关闭连接时出错: {close_error}")
