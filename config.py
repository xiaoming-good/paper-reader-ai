import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """配置管理类"""
    
    # AI API配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY", "")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    
    # 模型配置
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
    
    # 文本处理配置
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "4000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4000"))
    
    # 输出配置
    OUTPUT_LANGUAGE = os.getenv("OUTPUT_LANGUAGE", "zh")
    OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "markdown")
    
    @property
    def api_key(self) -> str:
        """获取优先级最高的API Key"""
        for key in [self.OPENAI_API_KEY, self.MOONSHOT_API_KEY, self.DEEPSEEK_API_KEY]:
            if key:
                return key
        return ""
    
    @property
    def use_moonshot(self) -> bool:
        return bool(self.MOONSHOT_API_KEY and not self.OPENAI_API_KEY)
    
    @property
    def use_deepseek(self) -> bool:
        return bool(self.DEEPSEEK_API_KEY and not self.OPENAI_API_KEY and not self.MOONSHOT_API_KEY)
    
    def get_model_config(self) -> dict:
        """获取模型配置"""
        if self.use_moonshot:
            return {
                "api_key": self.MOONSHOT_API_KEY,
                "base_url": "https://api.moonshot.cn/v1",
                "model": "moonshot-v1-8k"
            }
        elif self.use_deepseek:
            return {
                "api_key": self.DEEPSEEK_API_KEY,
                "base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-chat"
            }
        else:
            return {
                "api_key": self.OPENAI_API_KEY,
                "base_url": self.OPENAI_BASE_URL,
                "model": self.MODEL_NAME
            }

config = Config()
