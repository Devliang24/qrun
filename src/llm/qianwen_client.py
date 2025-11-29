"""千问多模态 VL 客户端"""
import json
import base64
from typing import Optional, Union
from pathlib import Path

try:
    from dashscope import MultiModalConversation
    import dashscope
except ImportError:
    MultiModalConversation = None
    dashscope = None

from ..core.config_manager import get_config


class QianwenClient:
    """千问 VL 多模态客户端"""
    
    def __init__(self, api_key: Optional[str] = None):
        config = get_config()
        self.api_key = api_key or config.get('qianwen.api_key', '')
        self.model = config.get('qianwen.model', 'qwen-vl-max')
        self.timeout = config.get('qianwen.timeout', 60)
        
        if dashscope:
            dashscope.api_key = self.api_key
    
    def _encode_image(self, image_data: Union[str, bytes, Path]) -> str:
        """编码图片为 base64"""
        if isinstance(image_data, Path):
            with open(image_data, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        elif isinstance(image_data, bytes):
            return base64.b64encode(image_data).decode('utf-8')
        elif isinstance(image_data, str):
            # 假设已经是 base64
            return image_data
        return ""
    
    def generate(self, prompt: str, image_path: str = None) -> str:
        """调用通义千问 VL 模型
        
        Args:
            prompt: 提示词
            image_path: 图片路径（本地文件路径，str）
        """
        if not MultiModalConversation:
            raise ImportError("dashscope 未安装，请运行: pip install dashscope")
        
        content = []
        if image_path:
            # DashScope Python SDK 支持直接传 file:// 路径
            # 或者我们可以手动转 base64
            # 官方文档建议直接传路径：file://path/to/image.png
            abs_path = Path(image_path).absolute()
            content.append({'image': f'file://{str(abs_path)}'})
            
        content.append({'text': prompt})
        
        messages = [
            {
                'role': 'user',
                'content': content
            }
        ]
        
        response = MultiModalConversation.call(
            model=self.model,
            messages=messages,
        )
        
        if response.status_code == 200:
            return response.output.choices[0].message.content[0]['text']
        else:
            raise Exception(f"千问 API 调用失败: {response.code} - {response.message}")
    
    def analyze_image(self, prompt: str, image_data: Union[str, bytes, Path]) -> str:
        """分析图片（多模态）"""
        if not MultiModalConversation:
            raise ImportError("dashscope 未安装，请运行: pip install dashscope")
        
        image_base64 = self._encode_image(image_data)
        
        messages = [
            {
                'role': 'user',
                'content': [
                    {'image': f'data:image/png;base64,{image_base64}'},
                    {'text': prompt}
                ]
            }
        ]
        
        response = MultiModalConversation.call(
            model=self.model,
            messages=messages,
        )
        
        if response.status_code == 200:
            return response.output.choices[0].message.content[0]['text']
        else:
            raise Exception(f"千问 API 调用失败: {response.code} - {response.message}")
    
    def parse_json_response(self, response: str) -> dict:
        """解析 JSON 响应"""
        # 尝试提取 JSON
        try:
            # 直接解析
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # 尝试从 markdown 代码块提取
        import re
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # 尝试查找 JSON 对象
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # 尝试查找 JSON 数组
        json_match = re.search(r'\[[\s\S]*\]', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        raise ValueError(f"无法解析 JSON 响应: {response[:200]}")
