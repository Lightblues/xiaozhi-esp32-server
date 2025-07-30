import asyncio
from aiohttp import web


class SimpleHttpServer:
    async def start(self):
        app = web.Application()
        # 添加路由
        app.add_routes(
            [
                web.get("/mcp/vision/explain", self.vision_handler.handle_get),
                web.post("/mcp/vision/explain", self.vision_handler.handle_post),
                web.options("/mcp/vision/explain", self.vision_handler.handle_post),
            ]
        )

        # 运行服务
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()

        # 保持服务运行
        while True:
            await asyncio.sleep(3600)  # 每隔 1 小时检查一次