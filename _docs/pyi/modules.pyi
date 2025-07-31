from typing import Dict, Any


# main/xiaozhi-server/core/utils/modules_initialize.py
def initialize_modules(
    logger,
    config: Dict[str, Any],
    init_vad=False,
    init_asr=False,
    init_llm=False,
    init_tts=False,
    init_memory=False,
    init_intent=False,
) -> Dict[str, Any]:
    """初始化所有模块组件"""

def initialize_tts(config):
    select_tts_module = config["selected_module"]["TTS"]
    new_tts = tts.create_instance(
        config["TTS"][select_tts_module]["type"],
        config["TTS"][select_tts_module],
        str(config.get("delete_audio", True)).lower() in ("true", "1", "yes"),
    )


# main/xiaozhi-server/core/utils/tts.py
import os, sys
def create_instance(class_name, *args, **kwargs):
    # 创建TTS实例
    if os.path.exists(os.path.join('core', 'providers', 'tts', f'{class_name}.py')):
        lib_name = f'core.providers.tts.{class_name}'
        return sys.modules[lib_name].TTSProvider(*args, **kwargs)
