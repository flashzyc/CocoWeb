# API 调用层

这个文件夹包含所有外部 API 的调用封装，方便独立使用、测试和切换不同的 API 提供商。

## 目录结构

```text
api/
├── __init__.py              # 导出所有 API 客户端
├── openai_client.py         # OpenAI API 客户端
├── _template_client.py      # API 客户端模板（用于创建新客户端）
├── config_example.yaml      # API 配置示例
├── README.md                # 本文档
└── ADD_NEW_API.md           # 如何添加新 API 的详细指南
```

## 快速开始

### 1. 配置 API 密钥

编辑 `config/config.yaml`，填入你的 API 密钥：

```yaml
openai:
  api_key: "sk-your-api-key-here"
  model: "gpt-4"
  temperature: 0.7
  max_tokens: 2000
```

### 2. 使用 API 客户端

```python
from api.openai_client import OpenAIClient
from app.schema import Context

# 初始化客户端（自动从 config/config.yaml 读取配置）
client = OpenAIClient()

# 使用客户端
response = client.generate_next_action(
    task="整理桌面文件",
    context=Context(),
    history=[]
)
```

## API 客户端说明

### OpenAI 客户端 (`openai_client.py`)

封装了 OpenAI API 的所有调用，包括：

- **生成下一步动作** (`generate_next_action`): 根据任务和上下文生成结构化的动作
- **通用聊天补全** (`chat_completion`): 通用的对话接口
- **文本嵌入** (`get_embedding`): 获取文本的向量表示

#### 配置选项

```yaml
openai:
  api_key: "sk-..."           # 必需：API 密钥
  model: "gpt-4"              # 模型名称
  temperature: 0.7            # 温度参数（0-2）
  max_tokens: 2000            # 最大 token 数
  base_url: null              # 可选：自定义 API 端点
```

#### 使用示例

**生成下一步动作：**

```python
from api.openai_client import OpenAIClient
from app.schema import Context

client = OpenAIClient("config/config.yaml")

context = Context(
    front_app="Finder",
    front_window="Desktop",
    file_context={}
)

response = client.generate_next_action(
    task="整理桌面上的文件",
    context=context,
    history=[],
    max_retries=3
)

print(f"工具: {response.next_action.tool}")
print(f"参数: {response.next_action.args}")
print(f"原因: {response.next_action.why}")
```

**通用聊天：**

```python
from api.openai_client import OpenAIClient

client = OpenAIClient()

messages = [
    {"role": "system", "content": "你是一个有用的助手"},
    {"role": "user", "content": "解释一下什么是 Python"}
]

response = client.chat_completion(messages)
print(response)
```

**获取嵌入向量：**

```python
from api.openai_client import OpenAIClient

client = OpenAIClient()

text = "这是一个示例文本"
embedding = client.get_embedding(text)

print(f"嵌入向量维度: {len(embedding)}")
```

## 切换 API 提供商

### 方法 1: 修改配置文件

如果你使用的是兼容 OpenAI API 格式的其他服务（如本地模型、代理服务），只需修改 `config/config.yaml`：

```yaml
openai:
  api_key: "your-key"
  model: "your-model"
  base_url: "http://your-api-endpoint/v1"  # 自定义端点
```

### 方法 2: 添加新的 API 客户端

如果需要使用完全不兼容的 API（如 Claude、本地 Ollama），可以：

1. **创建新的客户端文件**，如 `api/claude_client.py`：

```python
# api/claude_client.py
class ClaudeClient:
    def __init__(self, config_path: str = "config/config.yaml"):
        # 加载配置
        pass
    
    def generate_next_action(self, task, context, history):
        # 实现 Claude API 调用
        pass
```

2. **在 `api/__init__.py` 中导出**：

```python
from api.openai_client import OpenAIClient
from api.claude_client import ClaudeClient

__all__ = ['OpenAIClient', 'ClaudeClient']
```

3. **修改 `app/llm_client.py` 以支持切换**：

```python
# app/llm_client.py
from api.openai_client import OpenAIClient
from api.claude_client import ClaudeClient

class LLMClient:
    def __init__(self, config_path: str = "config/config.yaml"):
        config = self._load_config(config_path)
        provider = config.get("api_provider", "openai")
        
        if provider == "openai":
            self.api_client = OpenAIClient(config_path)
        elif provider == "claude":
            self.api_client = ClaudeClient(config_path)
        # ...
```

## 错误处理

所有 API 调用都包含错误处理和重试机制：

```python
from api.openai_client import OpenAIClient

client = OpenAIClient()

try:
    response = client.generate_next_action(...)
except ValueError as e:
    print(f"JSON 解析错误: {e}")
except Exception as e:
    print(f"API 调用失败: {e}")
```

## 配置管理

- **配置文件位置**: `config/config.yaml`
- **示例配置**: `api/config_example.yaml`
- **配置验证**: 首次运行时自动检查配置

## 注意事项

1. **API 密钥安全**:
   - 不要将 `config/config.yaml` 提交到版本控制
   - 已添加到 `.gitignore`

2. **API 限制**:
   - 注意 API 的速率限制
   - 大任务可能需要多次调用

3. **成本控制**:
   - 监控 API 使用量
   - 根据任务复杂度选择合适的模型
