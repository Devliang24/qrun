"""AI 测试用例生成器"""
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

from .qianwen_client import QianwenClient
from ..core.config_manager import get_config


class TestGenerator:
    """AI 驱动的测试用例生成器"""
    
    def __init__(self):
        self.qianwen = QianwenClient()
        self.config = get_config()
    
    def generate(self, description: str, output_file: Optional[str] = None) -> Dict:
        """
        从自然语言描述生成测试用例
        
        Args:
            description: 测试场景描述
            output_file: 输出文件路径
        
        Returns:
            dict: {'file': str, 'lines': int, 'keywords': int}
        """
        app_package = self.config.get('app.package', 'com.example.app')
        app_activity = self.config.get('app.activity', '.MainActivity')
        
        prompt = f"""你是一个资深的 Android 自动化测试工程师。请为以下测试场景生成 Robot Framework 测试用例。

测试场景: {description}

应用信息:
- 包名: {app_package}
- Activity: {app_activity}

要求:
1. 使用 Robot Framework 语法
2. 使用以下 AI Keywords（已经封装好的）：
   - AI Open App: 打开应用
   - AI Close App: 关闭应用
   - AI Do    <自然语言指令>: 自动规划并执行多步骤操作
   - AI Click    <元素描述>: 点击元素
   - AI Input    <文本>    <元素描述>: 输入文本
   - AI Swipe    <方向>: 滑动（up/down/left/right）
   - AI Wait For    <条件>    <超时>: 等待条件满足
   - AI Assert    <期望状态>: 验证状态
   - AI Query    <查询描述>: 提取界面数据
   - AI Get Text    <元素描述>: 获取元素文本
3. 元素用自然语言描述，如"登录按钮"、"用户名输入框"
4. 每个关键步骤后添加 AI Assert 验证
5. 使用 AI Wait For 处理异步加载
6. 包含 [Documentation] 和 [Teardown]

生成格式（直接输出代码，不要其他说明）：

*** Settings ***
Library    AITestLibrary

*** Test Cases ***
测试用例名称
    [Documentation]    测试描述
    
    AI Open App
    # 测试步骤...
    
    [Teardown]    AI Close App"""
        
        # 调用千问生成
        test_code = self.qianwen.generate(prompt)
        
        # 清理响应
        test_code = self._clean_code(test_code)
        
        # 生成文件名
        if not output_file:
            # 从描述提取测试名称
            test_name = self._extract_test_name(description)
            output_dir = Path('tests')
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = str(output_dir / f'{test_name}.robot')
        
        # 确保目录存在
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(test_code)
        
        # 统计
        lines = test_code.count('\n') + 1
        keywords = len(re.findall(r'\bAI\s+\w+', test_code))
        
        return {
            'file': output_file,
            'lines': lines,
            'keywords': keywords,
            'content': test_code
        }
    
    def _clean_code(self, code: str) -> str:
        """清理生成的代码"""
        # 移除 markdown 代码块
        code = re.sub(r'^```\w*\n?', '', code)
        code = re.sub(r'\n?```$', '', code)
        
        # 确保以 *** Settings *** 开头
        if not code.strip().startswith('***'):
            # 尝试找到第一个 *** 
            match = re.search(r'\*\*\*', code)
            if match:
                code = code[match.start():]
        
        return code.strip()
    
    def _extract_test_name(self, description: str) -> str:
        """从描述提取测试名称"""
        # 提取中文或英文的前几个字作为名称
        # 移除特殊字符
        name = re.sub(r'[^\w\u4e00-\u9fff\s]', '', description)
        # 取前20个字符
        name = name[:20].strip()
        # 替换空格
        name = re.sub(r'\s+', '_', name)
        return name or 'test_case'
    
    def suggest_scenarios(self, feature: str) -> List[str]:
        """
        AI 建议测试场景
        
        Args:
            feature: 功能名称
        
        Returns:
            list: 建议的测试场景列表
        """
        prompt = f"""你是一个资深的 Android 测试专家。为以下功能设计全面的测试场景。

功能: {feature}

请列出需要测试的场景，包括：
1. 正常流程（Happy Path）
2. 异常场景（错误处理）
3. 边界条件
4. UI 交互测试

每行一个场景，格式：场景名称 - 简短描述

只输出场景列表，不要其他说明。"""
        
        response = self.qianwen.generate(prompt)
        
        # 解析响应
        scenarios = []
        for line in response.strip().split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                # 移除序号
                line = re.sub(r'^\d+[\.\)、]\s*', '', line)
                if line:
                    scenarios.append(line)
        
        return scenarios
