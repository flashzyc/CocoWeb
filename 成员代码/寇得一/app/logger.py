"""完整的日志系统 - 运行日志 + 审计日志"""

import logging
import logging.handlers
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum


class LogLevel(Enum):
    """日志级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Logger:
    """统一的日志管理器"""
    
    _instance: Optional['Logger'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: str = "config/logging.yaml"):
        """初始化日志系统（单例模式）"""
        if self._initialized:
            return
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.logs_dir = Path(self.config.get("logs_dir", "logs"))
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # 运行日志目录
        self.runtime_logs_dir = self.logs_dir / "runtime"
        self.runtime_logs_dir.mkdir(parents=True, exist_ok=True)
        
        # 审计日志目录（会话日志）
        self.audit_logs_dir = self.logs_dir / "sessions"
        self.audit_logs_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化运行日志
        self._setup_runtime_logging()
        
        self._initialized = True
    
    def _load_config(self) -> Dict[str, Any]:
        """加载日志配置"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        
        # 返回默认配置
        return {
            "level": "INFO",
            "logs_dir": "logs",
            "console": True,
            "file": True,
            "rotation": {
                "max_bytes": 10485760,  # 10MB
                "backup_count": 5
            },
            "modules": {
                "app": "INFO",
                "tools": "INFO",
                "api": "DEBUG"
            }
        }
    
    def _setup_runtime_logging(self):
        """设置运行日志"""
        config = self.config
        
        # 根日志级别
        root_level = getattr(logging, config.get("level", "INFO"))
        logging.basicConfig(level=root_level)
        
        # 创建根 logger
        self.root_logger = logging.getLogger()
        self.root_logger.setLevel(root_level)
        
        # 清除已有的处理器
        self.root_logger.handlers.clear()
        
        # 日志格式
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台输出
        if config.get("console", True):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(root_level)
            console_handler.setFormatter(formatter)
            self.root_logger.addHandler(console_handler)
        
        # 文件输出
        if config.get("file", True):
            log_file = self.runtime_logs_dir / "app.log"
            
            # 日志轮转
            rotation_config = config.get("rotation", {})
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=rotation_config.get("max_bytes", 10485760),  # 10MB
                backupCount=rotation_config.get("backup_count", 5),
                encoding='utf-8'
            )
            file_handler.setLevel(root_level)
            file_handler.setFormatter(formatter)
            self.root_logger.addHandler(file_handler)
        
        # 错误日志单独文件
        error_log_file = self.runtime_logs_dir / "error.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=rotation_config.get("max_bytes", 10485760),
            backupCount=rotation_config.get("backup_count", 5),
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.root_logger.addHandler(error_handler)
        
        # 为不同模块设置级别
        modules_config = config.get("modules", {})
        for module_name, level_str in modules_config.items():
            module_logger = logging.getLogger(module_name)
            module_logger.setLevel(getattr(logging, level_str))
    
    def get_logger(self, name: str) -> logging.Logger:
        """获取指定名称的 logger"""
        return logging.getLogger(name)
    
    def debug(self, message: str, module: str = "app", **kwargs):
        """记录 DEBUG 级别日志"""
        logger = self.get_logger(module)
        logger.debug(message, **kwargs)
    
    def info(self, message: str, module: str = "app", **kwargs):
        """记录 INFO 级别日志"""
        logger = self.get_logger(module)
        logger.info(message, **kwargs)
    
    def warning(self, message: str, module: str = "app", **kwargs):
        """记录 WARNING 级别日志"""
        logger = self.get_logger(module)
        logger.warning(message, **kwargs)
    
    def error(self, message: str, module: str = "app", exc_info=None, **kwargs):
        """记录 ERROR 级别日志"""
        logger = self.get_logger(module)
        logger.error(message, exc_info=exc_info, **kwargs)
    
    def critical(self, message: str, module: str = "app", exc_info=None, **kwargs):
        """记录 CRITICAL 级别日志"""
        logger = self.get_logger(module)
        logger.critical(message, exc_info=exc_info, **kwargs)
    
    def log_api_call(self, provider: str, endpoint: str, method: str, 
                     status_code: Optional[int] = None, duration: Optional[float] = None,
                     error: Optional[str] = None):
        """记录 API 调用"""
        log_data = {
            "provider": provider,
            "endpoint": endpoint,
            "method": method,
            "timestamp": datetime.now().isoformat()
        }
        
        if status_code:
            log_data["status_code"] = status_code
        if duration:
            log_data["duration"] = duration
        if error:
            log_data["error"] = error
        
        if error or (status_code and status_code >= 400):
            self.error(f"API 调用失败: {json.dumps(log_data, ensure_ascii=False)}", module="api")
        else:
            self.info(f"API 调用: {json.dumps(log_data, ensure_ascii=False)}", module="api")
    
    def log_action(self, action_type: str, action_data: Dict[str, Any], 
                   module: str = "app", level: LogLevel = LogLevel.INFO):
        """记录动作（结构化日志）"""
        log_entry = {
            "type": action_type,
            "timestamp": datetime.now().isoformat(),
            "data": action_data
        }
        
        message = f"[{action_type}] {json.dumps(action_data, ensure_ascii=False)}"
        
        if level == LogLevel.DEBUG:
            self.debug(message, module=module)
        elif level == LogLevel.INFO:
            self.info(message, module=module)
        elif level == LogLevel.WARNING:
            self.warning(message, module=module)
        elif level == LogLevel.ERROR:
            self.error(message, module=module)
        elif level == LogLevel.CRITICAL:
            self.critical(message, module=module)


# 全局日志实例
_logger_instance: Optional[Logger] = None


def get_logger(name: str = "app") -> logging.Logger:
    """获取 logger（便捷函数）"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = Logger()
    return _logger_instance.get_logger(name)


def init_logger(config_path: str = "config/logging.yaml") -> Logger:
    """初始化日志系统"""
    global _logger_instance
    _logger_instance = Logger(config_path)
    return _logger_instance
