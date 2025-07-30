
class AuthenticationError(Exception):
    pass

class AuthMiddleware:
    async def authenticate(self, headers):
        """验证连接请求"""
