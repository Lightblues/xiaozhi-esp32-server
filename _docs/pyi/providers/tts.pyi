from abc import ABC, abstractmethod

""" -------------------------------------------------------
TTSProviderBase: 
"""
# main/xiaozhi-server/core/providers/tts/base.py
class TTSProviderBase(ABC):
    @abstractmethod
    async def text_to_speak(self, text, output_file):
        pass


""" -------------------------------------------------------
TTSProvider: 每个文件对应一个TTS实现
main/xiaozhi-server/core/utils/modules_initialize.py | tts.py 提供创建TTS实例的接口 create_instance
"""
# main/xiaozhi-server/core/providers/tts/openai.py
class TTSProvider(TTSProviderBase):
    def __init__(self, config, delete_audio_file):
        super().__init__(config, delete_audio_file)
        self.api_key = config.get("api_key")
        self.api_url = config.get("api_url", "https://api.openai.com/v1/audio/speech")
        self.model = config.get("model", "tts-1")
        ...

    async def text_to_speak(self, text, output_file):
        response = requests.post(self.api_url, json=data, headers=headers)
        if response.status_code == 200:
            return response.content
        ...
