"""配置管理 - 首次运行引导和配置验证"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
import rumps


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = Path(config_path)
        self.example_path = Path(config_path + ".example")
        self.config: Optional[Dict[str, Any]] = None
    
    def check_and_init(self) -> bool:
        """检查配置并初始化（首次运行引导）"""
        if self.config_path.exists():
            # 配置文件存在，验证
            try:
                self.config = self._load_config()
                if self._validate_config():
                    return True
                else:
                    # 配置无效，提示修复
                    self._show_config_error()
                    return False
            except Exception as e:
                self._show_config_error(str(e))
                return False
        else:
            # 首次运行，创建配置
            return self._first_run_setup()
    
    def _first_run_setup(self) -> bool:
        """首次运行设置"""
        # 检查示例配置是否存在
        if not self.example_path.exists():
            # 创建默认配置
            self._create_default_config()
        else:
            # 从示例配置复制
            import shutil
            shutil.copy(self.example_path, self.config_path)
        
        # 提示用户配置 API 密钥
        response = rumps.alert(
            title="首次运行设置",
            message="需要配置 OpenAI API 密钥。\n\n是否现在打开配置文件？",
            ok="打开配置",
            cancel="稍后"
        )
        
        if response:  # 点击了"打开配置"
            self._open_config_file()
            # 再次验证
            if self.config_path.exists():
                try:
                    self.config = self._load_config()
                    if self._validate_config():
                        return True
                except:
                    pass
        
        return False
    
    def _create_default_config(self):
        """创建默认配置文件"""
        default_config = {
            "openai": {
                "api_key": "your-api-key-here",
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2000
            },
            "paths": {
                "home_directory": os.path.expanduser("~"),
                "allowed_domains": []
            },
            "session": {
                "auto_continue": False,
                "max_steps": 100
            }
        }
        
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _validate_config(self) -> bool:
        """验证配置有效性"""
        if not self.config:
            return False
        
        # 检查 OpenAI API 密钥
        api_key = self.config.get("openai", {}).get("api_key", "")
        if not api_key or api_key == "your-api-key-here":
            return False
        
        return True
    
    def _show_config_error(self, error: str = ""):
        """显示配置错误提示"""
        msg = "配置文件无效或 API 密钥未设置。"
        if error:
            msg += f"\n\n错误: {error}"
        msg += "\n\n是否打开配置文件进行修复？"
        
        response = rumps.alert(
            title="配置错误",
            message=msg,
            ok="打开配置",
            cancel="取消"
        )
        
        if response:
            self._open_config_file()
    
    def _open_config_file(self):
        """打开配置文件"""
        import subprocess
        config_dir = self.config_path.parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # 如果文件不存在，先创建
        if not self.config_path.exists():
            self._create_default_config()
        
        # 使用默认编辑器打开
        subprocess.run(["open", "-t", str(self.config_path.resolve())])
    
    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        if not self.config:
            self.config = self._load_config()
        return self.config
    
    def get_openai_key(self) -> str:
        """获取 OpenAI API 密钥"""
        config = self.get_config()
        return config.get("openai", {}).get("api_key", "")
