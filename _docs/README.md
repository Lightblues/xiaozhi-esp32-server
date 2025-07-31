- github: https://github.com/xinnan-tech/xiaozhi-esp32-server
    - fork: https://github.com/Lightblues/xiaozhi-esp32-server
- doc:
    - deepwiki: https://deepwiki.com/xinnan-tech/xiaozhi-esp32-server
- ref:
    - xiaozhi-esp32: https://github.com/78/xiaozhi-esp32


Questions
- [ ] 服务器
    - [ ] 如何同时处理HTTP和WS服务?
    - [ ] 如何管理多连接的?
    - [ ] 配置项? -- 相较于, 这里简单采用 dict (yaml配置)
    - [x] 接收到语音/文本模态是如何处理的? `_route_message` 进行路由
    - [ ] 收到语音后的处理流程?
- [ ] 协议
    - 对于一个连接, 采用一个统一的 `ConnectionHandler` 来管理
- [ ] 各模块
    - [ ] TTS, ASR, LLM, Memory, Intent, Tools
- [ ] agent
    - [ ] Memory 设计
