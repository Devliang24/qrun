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
        将自然语言描述转换为 Robot Framework 脚本
        
        Args:
            description: 测试描述，如 "测试通知功能：点击通知，查看应用设置，返回"
            
        Returns:
            str: 生成的 Robot Framework 脚本内容
        """
        prompt = f"""你是 Robot Framework 测试脚本专家。将测试需求转换为脚本。

测试需求: {description}

可用关键字：
- AI Open App / AI Open App    <应用名>: 打开应用
- AI Close App: 关闭应用
- AI Click    <元素>: 点击
- AI Input    <文本>    <输入框>: 输入
- AI Assert    <条件>: 验证
- AI Swipe    <方向>: 滑动 (up/down/left/right)
- AI Back / AI Home: 返回/主页
- AI Sleep    <秒数>: 等待

高级语法（按需使用）：

1. FOR 循环（重复N次）:
    FOR    ${{i}}    IN RANGE    次数
        操作
    END

2. IF 条件:
    IF    条件
        操作
    ELSE
        其他操作
    END

3. WHILE 循环:
    WHILE    条件    limit=最大次数
        操作
    END

4. TRY-EXCEPT（处理可能失败的操作）:
    TRY
        可能失败的操作
    EXCEPT
        失败时的操作
    END

生成要求：
1. Library 路径: src/robot_lib/AITestLibrary.py
2. 测试用例名称用中文
3. 重复操作必须用 FOR 循环
4. 不确定的操作用 TRY-EXCEPT 包裹
5. 只返回脚本，不要说明

示例：
*** Settings ***
Library    src/robot_lib/AITestLibrary.py

*** Test Cases ***
批量操作示例
    AI Open App    某应用
    AI Sleep    2
    FOR    ${{i}}    IN RANGE    5
        AI Swipe    up
        TRY
            AI Click    按钮
        EXCEPT
            Log    未找到
        END
    END"""

        response = self.qianwen.generate(prompt)
        
        # 清理响应，提取脚本内容
        script = self._clean_script(response)
        return script
    
    def _clean_script(self, response: str) -> str:
        """清理 LLM 响应，提取纯脚本内容"""
        # 移除 markdown 代码块标记
        script = re.sub(r'```(?:robot|robotframework)?\n?', '', response)
        script = re.sub(r'```\n?', '', script)
        
        # 确保以 *** Settings *** 开头
        if '*** Settings ***' in script:
            start = script.find('*** Settings ***')
            script = script[start:]
        
        return script.strip()
    
    def extract_name(self, description: str) -> str:
        """从描述中提取测试名称"""
        # 尝试提取冒号前的部分作为名称
        if '：' in description:
            name = description.split('：')[0]
        elif ':' in description:
            name = description.split(':')[0]
        else:
            # 取前20个字符
            name = description[:20]
        
        # 清理名称
        name = re.sub(r'[\\/:*?"<>|]', '', name)
        name = name.strip()
        
        if not name:
            name = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return name
    
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
        filename = f"{name}.robot"
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
