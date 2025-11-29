"""配置管理模块"""
import os
import yaml
from pathlib import Path
from typing import Any, Optional

DEFAULT_CONFIG_FILE = "config.yaml"

class ConfigManager:
    """配置管理器"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._config_path = self._find_config_file()
            self._config = self._load_config()
    
    def _find_config_file(self) -> Path:
        """查找配置文件"""
        # 优先级: 当前目录 > 项目根目录
        current_dir = Path.cwd()
        config_file = current_dir / DEFAULT_CONFIG_FILE
        
        if config_file.exists():
            return config_file
        
        # 向上查找
        for parent in current_dir.parents:
            config_file = parent / DEFAULT_CONFIG_FILE
            if config_file.exists():
                return config_file
        
        # 默认使用当前目录
        return current_dir / DEFAULT_CONFIG_FILE
    
    def _load_config(self) -> dict:
        """加载配置文件"""
        if self._config_path.exists():
            with open(self._config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def save(self):
        """保存配置到文件"""
        with open(self._config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项（支持点号分隔的嵌套键）"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """设置配置项（支持点号分隔的嵌套键）"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save()
    
    def show(self) -> dict:
        """返回所有配置"""
        return self._config
    
    def validate(self) -> tuple[bool, list]:
        """验证必要配置项"""
        errors = []
        
        # 检查千问 API Key
        if not self.get('qianwen.api_key'):
            errors.append("qianwen.api_key 未设置")
        
        # 检查应用包名
        if not self.get('app.package'):
            errors.append("app.package 未设置")
        
        return len(errors) == 0, errors
    
    @property
    def config_path(self) -> Path:
        return self._config_path


def get_config() -> ConfigManager:
    """获取配置管理器实例"""
    return ConfigManager()
