import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """配置管理类 - 默认使用 DeepSeek 免费模型"""
    
    # AI API配置（优先级：DeepSeek > Moonshot > OpenAI）
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # 模型配置（默认 DeepSeek）
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1")
    MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-chat")
    
    # 文本处理配置
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "4000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4000"))
    
    # 输出配置
    OUTPUT_LANGUAGE = os.getenv("OUTPUT_LANGUAGE", "zh")
    OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "markdown")
    
    @property
    def api_key(self) -> str:
        """获取优先级最高的API Key（DeepSeek优先）"""
        for key in [self.DEEPSEEK_API_KEY, self.MOONSHOT_API_KEY, self.OPENAI_API_KEY]:
            if key:
                return key
        return ""
    
    @property
    def current_provider(self) -> str:
        """返回当前使用的AI提供商名称"""
        if self.DEEPSEEK_API_KEY:
            return "DeepSeek"
        elif self.MOONSHOT_API_KEY:
            return "Moonshot"
        elif self.OPENAI_API_KEY:
            return "OpenAI"
        return "未配置"
    
    @property
    def current_model(self) -> str:
        """返回当前实际使用的模型名称"""
        if self.DEEPSEEK_API_KEY:
            return "deepseek-chat"
        elif self.MOONSHOT_API_KEY:
            return "moonshot-v1-8k"
        return self.MODEL_NAME
    
    @property
    def use_deepseek(self) -> bool:
        return bool(self.DEEPSEEK_API_KEY)
    
    @property
    def use_moonshot(self) -> bool:
        return bool(self.MOONSHOT_API_KEY and not self.DEEPSEEK_API_KEY)
    
    @property
    def use_openai(self) -> bool:
        return bool(self.OPENAI_API_KEY and not self.DEEPSEEK_API_KEY and not self.MOONSHOT_API_KEY)
    
    def get_model_config(self) -> dict:
        """获取模型配置（DeepSeek 为默认）"""
        if self.use_deepseek:
            return {
                "api_key": self.DEEPSEEK_API_KEY,
                "base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-chat"
            }
        elif self.use_moonshot:
            return {
                "api_key": self.MOONSHOT_API_KEY,
                "base_url": "https://api.moonshot.cn/v1",
                "model": "moonshot-v1-8k"
            }
        else:
            return {
                "api_key": self.OPENAI_API_KEY,
                "base_url": self.OPENAI_BASE_URL,
                "model": self.MODEL_NAME
            }

config = Config()
