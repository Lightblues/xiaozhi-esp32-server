import json
from ..websocket_server import ConnectionHandler
from .receiveAudio import handleAudioMessage, startToChat

async def handleTextMessage(conn:ConnectionHandler, message:str):
    """处理文本消息"""
    try:
        msg_json = json.loads(message)
        if msg_json["type"] == "hello": ...
        elif msg_json["type"] == "abort": ...
        elif msg_json["type"] == "listen":
            if msg_json["state"] == "start":
                conn.client_have_voice = True
                conn.client_voice_stop = False
            elif msg_json["state"] == "stop":
                conn.client_have_voice = True
                conn.client_voice_stop = True
                if len(conn.asr_audio) > 0:
                    await handleAudioMessage(conn, b"")
            elif msg_json["state"] == "detect":
                conn.client_have_voice = False
                conn.asr_audio.clear()
                if "text" in msg_json:
                    ...
                    # 识别是否是唤醒词
                    is_wakeup_words = filtered_text in conn.config.get("wakeup_words")
                    # 是否开启唤醒词回复
                    enable_greeting = conn.config.get("enable_greeting", True)

                    if is_wakeup_words and not enable_greeting:
                        # 如果是唤醒词，且关闭了唤醒词回复，就不用回答
                        await send_stt_message(conn, original_text)
                        await send_tts_message(conn, "stop", None)
                        conn.client_is_speaking = False
                    elif is_wakeup_words:
                        conn.just_woken_up = True
                        # 上报纯文字数据（复用ASR上报功能，但不提供音频数据）
                        enqueue_asr_report(conn, "嘿，你好呀", [])
                        await startToChat(conn, "嘿，你好呀")
                    else:
                        # 上报纯文字数据（复用ASR上报功能，但不提供音频数据）
                        enqueue_asr_report(conn, original_text, [])
                        # 否则需要LLM对文字内容进行答复
                        await startToChat(conn, original_text)
        elif msg_json["type"] == "iot": ...
        elif msg_json["type"] == "mcp": ...
        elif msg_json["type"] == "server": ...
    except json.JSONDecodeError:
        await conn.websocket.send(message)
