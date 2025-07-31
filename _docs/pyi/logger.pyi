from loguru import logger, Logger

def setup_logging() -> Logger:
    ...
    return logger

def create_connection_logger(selected_module_str):
    """为连接创建独立的日志器，绑定特定的模块字符串"""
    return logger.bind(selected_module=selected_module_str)
