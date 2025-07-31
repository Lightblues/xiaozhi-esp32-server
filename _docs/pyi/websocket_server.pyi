import asyncio
import websockets
from .modules import initialize_modules
from .logger import create_connection_logger
""" -------------------------------------------------------
WebSocketServer: 基于websockets库实现的WebSocket服务器
调度: 对于每次连接采用新的 ConnectionHandler (1 对多的服务!)
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

- 初始化: 这里初始化了一堆的组件
- 超时中断机制: 对于一个连接, 超过指定时间没有活动, 则自动关闭连接
- close: 资源清理方法. 包括: timeout后台任务, 触发stop_event, 清空任务队列, 关闭WebSocket连接, 关闭线程池, 关闭TTS

TODO: 如何设计一个鲁棒的ws服务?
"""
import time
import traceback
import threading
from concurrent.futures import ThreadPoolExecutor
from .auth import AuthMiddleware, AuthenticationError
from .handle.text import handleTextMessage

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

            # 获取差异化配置
            self._initialize_private_config()
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

    async def _route_message(self, message):
        """消息路由"""
        if isinstance(message, str):
            await handleTextMessage(self, message)
        elif isinstance(message, bytes):
            self.asr_audio_queue.put(message)

    def _initialize_private_config(self):
        """如果是从配置文件获取，则进行二次实例化"""
        if not self.read_config_from_api:
            return
        """从接口获取差异化的配置进行二次实例化，非全量重新实例化"""
        ...

        try:
            modules = initialize_modules(...)
        except Exception as e:
            modules = {}
        if modules.get("tts", None) is not None:
            self.tts = modules["tts"]
        if modules.get("vad", None) is not None:
            self.vad = modules["vad"]
        if modules.get("asr", None) is not None:
            self.asr = modules["asr"]
        if modules.get("llm", None) is not None:
            self.llm = modules["llm"]
        if modules.get("intent", None) is not None:
            self.intent = modules["intent"]
        if modules.get("memory", None) is not None:
            self.memory = modules["memory"]

    def _initialize_components(self):
        try:
            self.logger = create_connection_logger(self.selected_module_str)

            """初始化组件"""
            ...
            """初始化本地组件"""
            if self.vad is None:
                self.vad = self._vad
            if self.asr is None:
                self.asr = self._initialize_asr()
            # 初始化声纹识别
            self._initialize_voiceprint()
            # 打开语音识别通道
            asyncio.run_coroutine_threadsafe(
                self.asr.open_audio_channels(self), self.loop
            )
            if self.tts is None:
                self.tts = self._initialize_tts()
            # 打开语音合成通道
            asyncio.run_coroutine_threadsafe(
                self.tts.open_audio_channels(self), self.loop
            )
            """加载记忆"""
            self._initialize_memory()
            """加载意图识别"""
            self._initialize_intent()
            """初始化上报线程"""
            self._init_report_threads()
            """更新系统提示词"""
            self._init_prompt_enhancement()
        except Exception as e: ...

    async def _check_timeout(self):
        """检查连接超时"""
        try:
            while not self.stop_event.is_set():
                # 检查是否超时（只有在时间戳已初始化的情况下）
                if self.last_activity_time > 0.0:
                    current_time = time.time() * 1000
                    if (
                    ):
                        if not self.stop_event.is_set():
                            # 设置停止事件，防止重复处理
                            self.stop_event.set()
                            # 使用 try-except 包装关闭操作，确保不会因为异常而阻塞
                            try:
                                await self.close(self.websocket)
                            except Exception as close_error: ...
                # 每10秒检查一次，避免过于频繁
                await asyncio.sleep(10)
        except Exception as e: ...

    async def close(self, ws=None):
        """资源清理方法"""
        try:
            # 取消超时任务
            if self.timeout_task and not self.timeout_task.done():
                self.timeout_task.cancel()
            # 触发停止事件
            if self.stop_event:
                self.stop_event.set()
            # 清空任务队列
            self.clear_queues()
            # 关闭WebSocket连接
            try:
                # 安全地检查WebSocket状态并关闭
                await ws.close()
            except Exception: ...
            if self.tts:
                await self.tts.close()
            # 最后关闭线程池（避免阻塞）
            if self.executor:
                try:
                    self.executor.shutdown(wait=False)
                except Exception: ...
        except Exception as e: ...

    def clear_queues(self):
        """清空所有任务队列"""
        if self.tts:
            # 使用非阻塞方式清空队列
            for q in [
                self.tts.tts_text_queue,
                self.tts.tts_audio_queue,
                self.report_queue,
            ]:
                while True:
                    try:
                        q.get_nowait()
                    except queue.Empty:
                        break
