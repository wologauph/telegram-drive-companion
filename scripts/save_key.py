import os

p1 = r'D:\银月baby的工作玉简\00_Inbox_收集箱\Telegram_Drive_WebDAV挂载档案与凭证.md'
p2 = r'D:\我的电脑工具库\99_工具档案与恢复SOP\05_Telegram-Drive-CN与WebDAV挂载配置.md'

key_block = """
### 🔑 REST 本地自动化 API 核心凭证 (新增归档)
- **REST 本地端口**：`8550`
- **REST 基础接口地址**：`http://127.0.0.1:8550/api/v1`
- **REST API 访问密钥 (X-API-Key)**：
  `a94fb0d897967fc6b7e7455f924d94eb6a18a70e40d350f432c35be46ba41c41`
- **调用示例**：
  `curl -H "X-API-Key: a94fb0d897967fc6b7e7455f924d94eb6a18a70e40d350f432c35be46ba41c41" http://127.0.0.1:8550/api/v1/files`
"""

for path in [p1, p2]:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'a94fb0d897967fc6b7e7455f924d94eb6a18a70e40d350f432c35be46ba41c41' not in content:
            content += '\n' + key_block
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print('Saved key to:', path)
        else:
            print('Key already exists in:', path)
