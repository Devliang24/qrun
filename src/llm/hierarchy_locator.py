"""基于 UI Hierarchy 的元素定位器 - 精确坐标 + AI 语义匹配"""
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .qianwen_client import QianwenClient
from ..core.u2_manager import get_u2
from ..core.config_manager import get_config


@dataclass
class UIElement:
    """UI 元素数据类"""
    index: int
    text: str
    content_desc: str
    resource_id: str
    class_name: str
    bounds: Tuple[int, int, int, int]  # x1, y1, x2, y2
    clickable: bool
    enabled: bool
    focused: bool
    selected: bool
    
    @property
    def center(self) -> Tuple[int, int]:
        """返回元素中心坐标"""
        x1, y1, x2, y2 = self.bounds
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    
    @property
    def display_text(self) -> str:
        """返回用于显示的文本"""
        if self.text:
            return self.text
        if self.content_desc:
            return self.content_desc
        if self.resource_id:
            # 提取 resource-id 的最后部分
            parts = self.resource_id.split('/')
            return parts[-1] if len(parts) > 1 else self.resource_id
        return self.class_name.split('.')[-1]
    
    @property
    def short_class(self) -> str:
        """返回简短类名"""
        return self.class_name.split('.')[-1]


class HierarchyLocator:
    """基于 UI Hierarchy 的元素定位器
    
    核心思想：
    1. 用 UI Hierarchy 获取精确的元素坐标
    2. 用 AI 进行语义匹配（找到用户描述的元素）
    3. 结合两者优势：精确 + 智能
    """
    
    def __init__(self):
        self.qianwen = QianwenClient()
        self.u2 = get_u2()
        
        config = get_config()
        self.retry_count = config.get('ai.locator.retry_count', 3)
    
    def _parse_bounds(self, bounds_str: str) -> Tuple[int, int, int, int]:
        """解析 bounds 字符串，如 '[0,0][1080,1920]'"""
        match = re.findall(r'\[(\d+),(\d+)\]', bounds_str)
        if len(match) == 2:
            x1, y1 = int(match[0][0]), int(match[0][1])
            x2, y2 = int(match[1][0]), int(match[1][1])
            return (x1, y1, x2, y2)
        return (0, 0, 0, 0)
    
    def _parse_hierarchy(self, xml_str: str) -> List[UIElement]:
        """解析 UI Hierarchy XML，提取所有可交互元素"""
        elements = []
        
        try:
            root = ET.fromstring(xml_str)
        except ET.ParseError as e:
            print(f"XML 解析错误: {e}")
            return elements
        
        index = 0
        for node in root.iter():
            # 获取属性
            text = node.get('text', '')
            content_desc = node.get('content-desc', '')
            resource_id = node.get('resource-id', '')
            class_name = node.get('class', '')
            bounds_str = node.get('bounds', '')
            clickable = node.get('clickable', 'false') == 'true'
            enabled = node.get('enabled', 'true') == 'true'
            focused = node.get('focused', 'false') == 'true'
            selected = node.get('selected', 'false') == 'true'
            
            # 过滤：只保留有意义的元素
            has_text = bool(text or content_desc or resource_id)
            has_bounds = bool(bounds_str)
            
            if has_bounds and (has_text or clickable):
                bounds = self._parse_bounds(bounds_str)
                # 过滤掉太小或无效的元素
                width = bounds[2] - bounds[0]
                height = bounds[3] - bounds[1]
                if width > 10 and height > 10:
                    elements.append(UIElement(
                        index=index,
                        text=text,
                        content_desc=content_desc,
                        resource_id=resource_id,
                        class_name=class_name,
                        bounds=bounds,
                        clickable=clickable,
                        enabled=enabled,
                        focused=focused,
                        selected=selected
                    ))
                    index += 1
        
        return elements
    
    def _build_element_prompt(self, elements: List[UIElement]) -> str:
        """构建元素列表提示词"""
        lines = ["当前界面的 UI 元素列表：", ""]
        
        for elem in elements:
            # 构建描述
            attrs = []
            if elem.text:
                attrs.append(f'文本="{elem.text}"')
            if elem.content_desc:
                attrs.append(f'描述="{elem.content_desc}"')
            if elem.resource_id:
                short_id = elem.resource_id.split('/')[-1] if '/' in elem.resource_id else elem.resource_id
                attrs.append(f'ID={short_id}')
            
            status = []
            if elem.clickable:
                status.append("可点击")
            if elem.focused:
                status.append("聚焦")
            if elem.selected:
                status.append("已选中")
            if not elem.enabled:
                status.append("禁用")
            
            attr_str = ", ".join(attrs) if attrs else elem.short_class
            status_str = f" [{', '.join(status)}]" if status else ""
            
            lines.append(f"[{elem.index}] {attr_str} ({elem.short_class}){status_str}")
        
        return "\n".join(lines)
    
    def dump_and_parse(self) -> List[UIElement]:
        """获取并解析 UI 层级"""
        xml_str = self.u2.get_page_source()
        if not xml_str:
            raise Exception("无法获取 UI Hierarchy")
        return self._parse_hierarchy(xml_str)
    
    def find_element(self, description: str) -> UIElement:
        """用 AI 匹配元素
        
        Args:
            description: 元素的自然语言描述
            
        Returns:
            UIElement: 匹配的元素
        """
        elements = self.dump_and_parse()
        
        if not elements:
            raise Exception("界面上没有找到任何元素")
        
        prompt = self._build_element_prompt(elements)
        prompt += f"""

任务：找到最匹配 "{description}" 的元素。

要求：
1. 根据文本、描述、ID 综合判断
2. 只返回元素的序号数字，不要其他内容
3. 如果找不到匹配的元素，返回 -1

回答（只需要数字）："""
        
        for attempt in range(self.retry_count):
            try:
                response = self.qianwen.generate(prompt)
                
                # 提取数字
                match = re.search(r'-?\d+', response)
                if match:
                    index = int(match.group())
                    if index == -1:
                        raise Exception(f"未找到匹配的元素: {description}")
                    if 0 <= index < len(elements):
                        return elements[index]
                
                if attempt < self.retry_count - 1:
                    time.sleep(0.5)
                    continue
                    
            except Exception as e:
                if attempt < self.retry_count - 1:
                    time.sleep(0.5)
                    continue
                raise
        
        raise Exception(f"无法定位元素: {description}")
    
    def click_element(self, description: str) -> bool:
        """查找并点击元素
        
        Args:
            description: 元素描述
            
        Returns:
            bool: 是否成功
        """
        elem = self.find_element(description)
        x, y = elem.center
        
        print(f"[HierarchyLocator] 找到元素: {elem.display_text}")
        print(f"[HierarchyLocator] bounds: {elem.bounds}, 点击坐标: ({x}, {y})")
        
        self.u2.tap(x, y)
        return True
    
    def input_text(self, text: str, description: str) -> bool:
        """查找输入框并输入文本
        
        Args:
            text: 要输入的文本
            description: 输入框描述
            
        Returns:
            bool: 是否成功
        """
        # 先点击输入框
        self.click_element(description)
        time.sleep(0.5)
        
        # 输入文本
        self.u2.send_keys(text)
        return True
    
    def verify_state(self, expected_state: str) -> Dict:
        """验证界面状态
        
        Args:
            expected_state: 期望的状态描述
            
        Returns:
            dict: {'passed': bool, 'reason': str}
        """
        elements = self.dump_and_parse()
        prompt = self._build_element_prompt(elements)
        prompt += f"""

任务：判断当前界面是否满足条件 "{expected_state}"

要求：
1. 根据界面元素列表判断
2. 返回 JSON 格式

返回格式（只返回JSON）：
{{"passed": true/false, "reason": "判断理由"}}"""
        
        response = self.qianwen.generate(prompt)
        return self.qianwen.parse_json_response(response)
    
    def wait_for_condition(self, condition: str, timeout: int = 30) -> bool:
        """等待条件满足
        
        Args:
            condition: 条件描述
            timeout: 超时时间（秒）
            
        Returns:
            bool: 条件是否满足
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                result = self.verify_state(condition)
                if result.get('passed', False):
                    return True
            except:
                pass
            time.sleep(2)
        
        raise TimeoutError(f"等待超时: {condition}")
    
    def query_data(self, query: str) -> any:
        """从界面提取数据
        
        Args:
            query: 查询描述
            
        Returns:
            提取的数据
        """
        elements = self.dump_and_parse()
        prompt = self._build_element_prompt(elements)
        prompt += f"""

任务：{query}

要求：
1. 根据界面元素列表提取数据
2. 返回 JSON 格式的数据

返回（只返回JSON）："""
        
        response = self.qianwen.generate(prompt)
        return self.qianwen.parse_json_response(response)
    
    def get_text(self, description: str) -> str:
        """获取元素的文本内容
        
        Args:
            description: 元素描述
            
        Returns:
            str: 文本内容
        """
        elem = self.find_element(description)
        return elem.text or elem.content_desc or ""
