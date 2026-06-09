import requests
import json
import threading

class AIClient:
    """AI 客户端：支持 DeepSeek、OpenAI 等兼容接口"""

    BUILT_IN_MODELS = {
        "MiMo v2.5 Pro": {
            "base_url": "https://token-plan-cn.xiaomimimo.com/v1",
            "model": "mimo-v2.5-pro",
            "description": "小米 MiMo 模型"
        },
        "DeepSeek V3.2": {
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
            "description": "推荐：最具性价比"
        },
        "千问 Qwen-Plus": {
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "model": "qwen-plus",
            "description": "中文表达细腻"
        },
        "OpenAI GPT-4o": {
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4o",
            "description": "创意能力强"
        },
    }

    def __init__(self, config=None):
        self.config = config or {}
        self.api_key = self.config.get("api_key", "tp-cy1vke78kdzqmz70lbqo99k999s9y5jl7ryd5ukvxxi8c2k2")
        self.base_url = self.config.get("base_url", "https://token-plan-cn.xiaomimimo.com/v1")
        self.model = self.config.get("model", "mimo-v2.5-pro")
        self.temperature = self.config.get("temperature", 0.8)
        self.max_tokens = self.config.get("max_tokens", 4096)
        self.system_prompt = self.config.get("system_prompt", self._default_system_prompt())

    def _default_system_prompt(self):
        return (
            "你是一位专业的小说写作AI助手。你的任务是帮助作者创作高质量的小说。\n\n"
            "你的能力包括：\n"
            "1. 帮助作者构思剧情、设计角色、构建世界观\n"
            "2. 根据作者的要求续写、改写、润色小说内容\n"
            "3. 检查小说中的逻辑漏洞和前后矛盾\n"
            "4. 提供专业的写作建议和技巧\n\n"
            "请用中文回复，保持专业和友好的语气。\n"
            "如果用户提供了小说文件内容，请基于这些内容来创作。\n"
            "如果用户要求续写，请保持风格和逻辑的一致性。"
        )

    def update_config(self, config):
        self.config.update(config)
        self.api_key = self.config.get("api_key", self.api_key)
        self.base_url = self.config.get("base_url", self.base_url)
        self.model = self.config.get("model", self.model)
        self.temperature = self.config.get("temperature", self.temperature)
        self.max_tokens = self.config.get("max_tokens", self.max_tokens)
        if "system_prompt" in self.config:
            self.system_prompt = self.config["system_prompt"]

    def chat(self, messages, callback=None):
        """
        发送对话请求
        messages: [{"role": "user"/"assistant", "content": "..."}]
        callback: 流式回调 callback(token)
        """
        if not self.api_key:
            return "请先在设置中配置 API Key"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        full_messages = [{"role": "system", "content": self.system_prompt}]
        full_messages.extend(messages)

        payload = {
            "model": self.model,
            "messages": full_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": callback is not None
        }

        try:
            url = f"{self.base_url.rstrip('/')}/chat/completions"
            response = requests.post(url, headers=headers, json=payload, stream=callback is not None, timeout=120)
            response.raise_for_status()

            if callback:
                return self._handle_stream(response, callback)
            else:
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except requests.exceptions.ConnectionError:
            return f"连接失败，请检查网络连接和 API 地址: {self.base_url}"
        except requests.exceptions.Timeout:
            return "请求超时，请稍后重试"
        except requests.exceptions.HTTPError as e:
            return f"API 错误: {e.response.status_code} - {e.response.text[:200]}"
        except Exception as e:
            return f"未知错误: {str(e)}"

    def _handle_stream(self, response, callback):
        full_content = ""
        for line in response.iter_lines():
            if not line:
                continue
            line = line.decode("utf-8")
            if line.startswith("data: "):
                data = line[6:]
                if data.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    token = delta.get("content", "")
                    if token:
                        full_content += token
                        callback(token)
                except json.JSONDecodeError:
                    continue
        return full_content

    def test_connection(self):
        """测试 API 连接"""
        if not self.api_key:
            return False, "未配置 API Key"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": "你好，请回复'连接成功'"}],
            "max_tokens": 50
        }
        try:
            url = f"{self.base_url.rstrip('/')}/chat/completions"
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            return True, "连接成功"
        except Exception as e:
            return False, str(e)

    def build_writing_context(self, project_context, user_message, history=None):
        """构建写作上下文消息"""
        messages = []
        if project_context:
            ctx_msg = f"以下是当前小说项目的上下文信息：\n\n{project_context}\n\n请基于以上上下文来理解和回应用户的请求。"
            messages.append({"role": "user", "content": ctx_msg})
            messages.append({"role": "assistant", "content": "好的，我已经了解了小说的上下文信息，会基于这些信息来帮助你创作。"})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        return messages
