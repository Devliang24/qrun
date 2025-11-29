"""自然语言转 Robot Framework 脚本生成器"""
import os
import re
from datetime import datetime
from typing import Optional

from .qianwen_client import QianwenClient
from ..core.config_manager import get_config


class ScriptGenerator:
    """将自然语言描述转换为 Robot Framework 测试脚本"""
    
    def __init__(self):
        self.qianwen = QianwenClient()
        self.config = get_config()
        self.tests_dir = "tests"
    
    def generate(self, description: str) -> str:
        """
        将自然语言描述转换为 YAML 测试脚本
        
        Args:
            description: 测试描述
            
        Returns:
            str: 生成的 YAML 脚本内容
        """
        prompt = f"""你是一个自动化测试专家。请将以下测试需求转换为 YAML 格式的测试脚本。

测试需求: {description}

YAML 格式规范：
```yaml
name: 测试名称
description: 简短描述
steps:
  - action: AI Open App
    args: [应用名]
  - action: AI Click
    args: [元素描述]
  - action: AI Input
    args: [文本, 元素描述]
  - action: AI Swipe
    args: [up/down/left/right]
  - action: AI Back / AI Home / AI Sleep
    args: [参数(可选)]
    
  # 循环结构
  - loop: 5
    steps:
      - action: ...
      
  # 错误处理
  - try:
      steps: [...]
    except:
      steps: [...]
```

要求：
1. 只返回 YAML 内容，不要包含 ```yaml 标记
2. 确保缩进正确 (2空格)
3. 步骤逻辑合理
"""

        response = self.qianwen.generate(prompt)
        
        # 清理响应
        script = self._clean_script(response)
        return script
    
    def _clean_script(self, response: str) -> str:
        """清理 LLM 响应，提取纯 YAML 内容"""
        # 移除 markdown 代码块标记
        script = re.sub(r'```(?:yaml)?\n?', '', response)
        script = re.sub(r'```\n?', '', script)
        return script.strip()
    
    def save(self, name: str, content: str) -> str:
        """
        保存脚本到文件
        
        Args:
            name: 脚本名称（不含扩展名）
            content: 脚本内容
            
        Returns:
            str: 保存的文件路径
        """
        # 确保目录存在
        os.makedirs(self.tests_dir, exist_ok=True)
        
        # 生成文件名
        filename = f"{name}.yaml"
        filepath = os.path.join(self.tests_dir, filename)
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def list_scripts(self) -> list:
        """列出所有测试脚本"""
        if not os.path.exists(self.tests_dir):
            return []
        
        scripts = []
        for f in os.listdir(self.tests_dir):
            if f.endswith('.robot'):
                scripts.append(f[:-6])  # 去掉 .robot 扩展名
        return scripts
