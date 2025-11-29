"""AI 动作规划器 - 自动拆解自然语言指令"""
import json
import time
from typing import List, Dict

from .qianwen_client import QianwenClient
from .visual_locator import VisualLocator
from ..core.u2_manager import get_u2


class ActionPlanner:
    """自动规划并执行自然语言指令"""
    
    def __init__(self):
        self.qianwen = QianwenClient()
        self.locator = VisualLocator()
        self.u2 = get_u2()
    
    def plan_actions(self, instruction: str) -> List[Dict]:
        """
        将自然语言指令拆解为操作步骤
        
        Args:
            instruction: 自然语言指令，如 "打开应用，输入用户名 test，点击登录"
        
        Returns:
            list: 操作步骤列表
        """
        prompt = f"""你是一个 Android 自动化测试专家。将以下自然语言指令拆解为具体的操作步骤。

指令: {instruction}

将指令拆解为操作步骤，每个步骤是一个基本操作。

返回 JSON 数组格式（不要其他内容）：
[
  {{"action": "open_app"}},
  {{"action": "click", "target": "搜索框"}},
  {{"action": "input", "target": "搜索框", "text": "手机"}},
  {{"action": "click", "target": "搜索按钮"}},
  {{"action": "wait", "condition": "搜索结果显示"}},
  {{"action": "verify", "condition": "显示商品列表"}},
  {{"action": "swipe", "direction": "up"}}
]

可用的 action 类型：
- open_app: 打开应用
- close_app: 关闭应用
- click: 点击元素（需要 target）
- input: 输入文本（需要 target 和 text）
- wait: 等待条件（需要 condition）
- verify: 验证状态（需要 condition）
- swipe: 滑动（需要 direction: up/down/left/right）
- back: 按返回键
- home: 按主页键"""
        
        response = self.qianwen.generate(prompt)
        return self.qianwen.parse_json_response(response)
    
    def execute_action(self, action: Dict) -> bool:
        """
        执行单个操作
        
        Args:
            action: 操作字典
        
        Returns:
            bool: 是否成功
        """
        action_type = action.get('action')
        
        if action_type == 'open_app':
            self.u2.launch_app()
            time.sleep(2)
            return True
        
        elif action_type == 'close_app':
            self.u2.stop_app()
            return True
        
        elif action_type == 'click':
            target = action.get('target')
            if not target:
                raise ValueError("click 操作需要 target")
            return self.locator.click_element(target)
        
        elif action_type == 'input':
            target = action.get('target')
            text = action.get('text', '')
            if not target:
                raise ValueError("input 操作需要 target")
            return self.locator.input_text(text, target)
        
        elif action_type == 'wait':
            condition = action.get('condition')
            timeout = action.get('timeout', 30)
            if not condition:
                raise ValueError("wait 操作需要 condition")
            return self.locator.wait_for_condition(condition, timeout)
        
        elif action_type == 'verify':
            condition = action.get('condition')
            if not condition:
                raise ValueError("verify 操作需要 condition")
            result = self.locator.verify_state(condition)
            if not result.get('passed', False):
                raise AssertionError(f"验证失败: {result.get('reason', condition)}")
            return True
        
        elif action_type == 'swipe':
            direction = action.get('direction', 'up')
            size = self.u2.get_window_size()
            center_x = size['width'] // 2
            center_y = size['height'] // 2
            
            if direction == 'up':
                self.u2.swipe(center_x, center_y + 300, center_x, center_y - 300)
            elif direction == 'down':
                self.u2.swipe(center_x, center_y - 300, center_x, center_y + 300)
            elif direction == 'left':
                self.u2.swipe(center_x + 300, center_y, center_x - 300, center_y)
            elif direction == 'right':
                self.u2.swipe(center_x - 300, center_y, center_x + 300, center_y)
            
            time.sleep(0.5)
            return True
        
        elif action_type == 'back':
            self.u2.press_back()
            time.sleep(0.5)
            return True
        
        elif action_type == 'home':
            self.u2.press_home()
            time.sleep(0.5)
            return True
        
        else:
            raise ValueError(f"未知的操作类型: {action_type}")
    
    def execute(self, instruction: str) -> bool:
        """
        规划并执行自然语言指令
        
        Args:
            instruction: 自然语言指令
        
        Returns:
            bool: 是否全部成功
        """
        # 规划步骤
        steps = self.plan_actions(instruction)
        
        # 依次执行
        for i, step in enumerate(steps):
            action_type = step.get('action')
            target = step.get('target', step.get('condition', ''))
            
            print(f"Step {i+1}: {action_type} {target}")
            
            try:
                self.execute_action(step)
                print(f"  ✓ 成功")
            except Exception as e:
                print(f"  ✗ 失败: {e}")
                raise
            
            time.sleep(0.5)
        
        return True
