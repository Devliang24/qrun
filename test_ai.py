"""测试 AI 视觉定位"""
import os
import time

# 设置代理
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10796'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10796'

from src.llm.visual_locator import VisualLocator
from src.core.u2_manager import get_u2

# 连接设备
u2 = get_u2()
u2.connect()

# 启动设置
print("启动设置应用...")
u2.launch_app('com.android.settings')
time.sleep(2)

# 测试 AI 查找
locator = VisualLocator()
print("测试 AI 查找元素: Network...")
result = locator.find_element('Network')
print("结果:", result)
