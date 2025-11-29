"""基于视觉标记 (Set-of-Mark) 的元素定位器"""
import io
import re
import time
import base64
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional

from PIL import Image, ImageDraw, ImageFont

from .qianwen_client import QianwenClient
from ..core.u2_manager import get_u2
from ..core.config_manager import get_config


@dataclass
class VisualElement:
    """视觉元素数据类"""
    id: int
    bounds: Tuple[int, int, int, int]  # x1, y1, x2, y2
    center: Tuple[int, int]
    elem_node: ET.Element  # 原始 XML 节点
    
    @property
    def width(self):
        return self.bounds[2] - self.bounds[0]
        
    @property
    def height(self):
        return self.bounds[3] - self.bounds[1]


class VisualLocator:
    """基于 Set-of-Mark 的视觉定位器
    
    原理：
    1. 获取截图 + XML
    2. 解析 XML 提取可交互元素
    3. 在截图上绘制编号标记 (Set-of-Mark)
    4. 让 VLM (Qwen-VL) 根据编号选择元素
    """
    
    def __init__(self):
        self.qianwen = QianwenClient()
        self.u2 = get_u2()
        self.config = get_config()
        self.retry_count = self.config.get('ai.locator.retry_count', 3)

    def _parse_bounds(self, bounds_str: str) -> Tuple[int, int, int, int]:
        """解析 bounds 字符串 [x1,y1][x2,y2]"""
        match = re.findall(r'\[(\d+),(\d+)\]', bounds_str)
        if len(match) == 2:
            x1, y1 = int(match[0][0]), int(match[0][1])
            x2, y2 = int(match[1][0]), int(match[1][1])
            return (x1, y1, x2, y2)
        return (0, 0, 0, 0)

    def _get_interactable_elements(self, xml_str: str, screen_w: int, screen_h: int) -> List[VisualElement]:
        """从 XML 解析所有可交互元素"""
        elements = []
        try:
            root = ET.fromstring(xml_str)
        except ET.ParseError:
            print("XML 解析失败，将使用纯视觉模式（暂不支持纯视觉无标记）")
            return elements

        # 计数器
        count = 1
        
        for node in root.iter():
            # 基本属性过滤
            bounds_str = node.get('bounds', '')
            if not bounds_str: continue
            
            clickable = node.get('clickable', 'false') == 'true'
            long_clickable = node.get('long-clickable', 'false') == 'true'
            checkable = node.get('checkable', 'false') == 'true'
            focusable = node.get('focusable', 'false') == 'true'
            
            # 文本属性（辅助判断）
            text = node.get('text', '')
            desc = node.get('content-desc', '')
            
            # 核心逻辑：只标记真正可交互的元素，或者有明确文本内容的元素
            is_interactable = clickable or long_clickable or checkable or focusable
            has_content = bool(text or desc)
            
            # 过滤条件
            if is_interactable or has_content:
                bounds = self._parse_bounds(bounds_str)
                w = bounds[2] - bounds[0]
                h = bounds[3] - bounds[1]
                
                # 1. 过滤全屏容器 (通常是背景)
                if w >= screen_w * 0.95 and h >= screen_h * 0.95:
                    continue
                    
                # 2. 过滤微小元素 (通常是装饰点)
                if w < 20 or h < 20:
                    continue
                
                # 3. 过滤屏幕外的元素
                if bounds[2] < 0 or bounds[3] < 0 or bounds[0] > screen_w or bounds[1] > screen_h:
                    continue

                cx = (bounds[0] + bounds[2]) // 2
                cy = (bounds[1] + bounds[3]) // 2
                
                elements.append(VisualElement(
                    id=count,
                    bounds=bounds,
                    center=(cx, cy),
                    elem_node=node
                ))
                count += 1
                
        return elements

    def _draw_marks(self, image_bytes: bytes, elements: List[VisualElement]) -> Tuple[str, Image.Image]:
        """在截图上绘制标记，返回 base64 和图片对象"""
        img = Image.open(io.BytesIO(image_bytes))
        draw = ImageDraw.Draw(img)
        
        # 尝试加载字体，失败则使用默认
        try:
            # Windows 常用字体
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()

        for elem in elements:
            # 绘制边界框
            # 颜色轮换，方便区分
            colors = ['red', 'blue', 'green', 'orange', 'purple']
            color = colors[elem.id % len(colors)]
            
            draw.rectangle(elem.bounds, outline=color, width=3)
            
            # 绘制编号背景和文字
            label = str(elem.id)
            # 标签位置：左上角
            x, y = elem.bounds[0], elem.bounds[1]
            # 确保标签在屏幕内
            if y < 30: y = 30
            
            # 绘制标签背景
            # 计算文本大小
            left, top, right, bottom = draw.textbbox((x, y), label, font=font)
            w, h = right - left, bottom - top
            draw.rectangle((x, y - h - 5, x + w + 10, y + 5), fill=color)
            
            # 绘制文字
            draw.text((x + 5, y - h - 5), label, fill='white', font=font)
            
        # 保存到 buffer
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        base64_str = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        return base64_str, img

    def find_element(self, description: str) -> VisualElement:
        """通过视觉定位元素"""
        print(f"[VisualLocator] Finding: {description}")
        
        # 1. 获取截图和 XML
        screenshot = self.u2.get_screenshot_bytes()
        xml_str = self.u2.get_page_source()
        window_size = self.u2.get_window_size()
        
        if not screenshot or not xml_str:
            raise Exception("无法获取设备截图或 UI 结构")

        # 2. 提取元素
        elements = self._get_interactable_elements(xml_str, window_size['width'], window_size['height'])
        
        if not elements:
            raise Exception("当前界面未检测到可交互元素")
            
        # 3. 绘制标记
        marked_base64, marked_img = self._draw_marks(screenshot, elements)
        
        # 保存调试图片
        marked_img.save("last_marked_screenshot.png")
        print("[VisualLocator] Debug image saved to last_marked_screenshot.png")

        # 4. 构造 Prompt
        prompt = f"""
任务：你是一个 UI 自动化测试助手。我会在截图上给所有可交互元素打上数字标签。
请根据我的描述，找到对应的元素，并返回它的数字编号。

用户描述："{description}"

要求：
1. 仔细观察截图中的视觉特征（颜色、形状、图标、文字）。
2. 结合上下文判断（例如"右侧的按钮"、"底部的输入框"）。
3. 只返回一个数字编号，不要解释。如果不确定或找不到，返回 -1。

格式示例：
User: 点击搜索框
Assistant: 5
"""
        
        # 5. 调用大模型
        for attempt in range(self.retry_count):
            try:
                # 构造多模态消息
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"image": f"data:image/png;base64,{marked_base64}"},
                            {"text": prompt}
                        ]
                    }
                ]
                
                # 调用 Qwen-VL
                # 注意：这里我们需要复用 QianwenClient，但它目前的 generate 方法可能只支持纯文本或单图
                # 我们需要稍微 hack 一下或者确保 QianwenClient 支持这种格式
                # 假设 QianwenClient.generate 已经支持处理 base64 图片（之前实现是支持的）
                
                # 为了稳妥，我们这里直接调用 generate，但在 QianwenClient 中可能需要适配
                # 之前的 QianwenClient 实现是支持 prompt 中包含 image 的
                
                # 简单起见，我们传递带 image 标记的 prompt 给 QianwenClient
                # 假设 QianwenClient 内部会处理 DashScope 的多模态格式
                
                response = self.qianwen.generate(prompt, image_path="last_marked_screenshot.png")
                print(f"[VisualLocator] AI Response: {response}")
                
                # 解析结果
                match = re.search(r'(\d+)', response)
                if match:
                    elem_id = int(match.group(1))
                    if elem_id == -1:
                        raise Exception(f"AI 未找到元素: {description}")
                    
                    # 查找对应 ID 的元素
                    for elem in elements:
                        if elem.id == elem_id:
                            return elem
                    
                    print(f"[VisualLocator] AI 返回了无效的 ID: {elem_id}")
                
            except Exception as e:
                print(f"[VisualLocator] Attempt {attempt+1} failed: {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(1)
                    continue
        
        raise Exception(f"无法定位元素: {description}")

    def click_element(self, description: str) -> bool:
        """点击元素"""
        elem = self.find_element(description)
        x, y = elem.center
        print(f"[VisualLocator] Clicking ID:{elem.id} @ ({x}, {y})")
        self.u2.tap(x, y)
        return True

    def input_text(self, text: str, description: str) -> bool:
        """输入文本"""
        # 1. 点击
        self.click_element(description)
        time.sleep(1)
        
        # 2. 输入 (剪贴板方案)
        try:
            self.u2.device.set_clipboard(text)
            time.sleep(0.5)
            self.u2.device.shell('input keyevent 279') # Paste
            time.sleep(0.5)
            
            # 尝试回车确认
            print("Attempting Enter key...")
            self.u2.device.press('enter')
            return True
        except Exception as e:
            print(f"Input failed: {e}")
            # 降级
            try:
                safe = text.replace(' ', '%s').replace("'", "\\'")
                self.u2.device.shell(f'input text "{safe}"')
                return True
            except:
                return False
    
    def get_text(self, description: str) -> str:
        """获取文本"""
        elem = self.find_element(description)
        node = elem.elem_node
        return node.get('text') or node.get('content-desc') or ""
        
    def verify_state(self, expected_state: str) -> Dict:
        """验证状态 (复用 AI 视觉能力)"""
        # 同样使用截图+Prompt
        screenshot = self.u2.get_screenshot_bytes()
        if not screenshot:
            return {'passed': False, 'reason': 'Screenshot failed'}
            
        # 保存临时图片
        with open("verify_temp.png", "wb") as f:
            f.write(screenshot)
            
        prompt = f"""
任务：判断当前界面是否满足条件 "{expected_state}"
请仔细观察截图内容。

返回 JSON 格式：
{{"passed": true/false, "reason": "判断理由"}}
"""
        response = self.qianwen.generate(prompt, image_path="verify_temp.png")
        return self.qianwen.parse_json_response(response)

    def wait_for_condition(self, condition: str, timeout: int = 30) -> bool:
        start = time.time()
        while time.time() - start < timeout:
            try:
                res = self.verify_state(condition)
                if res.get('passed'): return True
            except:
                pass
            time.sleep(2)
        raise TimeoutError(f"Wait timeout: {condition}")
        
    def query_data(self, query: str) -> any:
        # 类似 verify_state，让 AI 看图提取
        screenshot = self.u2.get_screenshot_bytes()
        with open("query_temp.png", "wb") as f:
            f.write(screenshot)
            
        prompt = f"任务：{query}\n请根据截图提取数据，返回 JSON 格式。"
        response = self.qianwen.generate(prompt, image_path="query_temp.png")
        return self.qianwen.parse_json_response(response)
