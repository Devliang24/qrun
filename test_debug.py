"""调试 AI 定位精度"""
import os
import time
import json

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10796'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10796'

from src.llm.visual_locator import VisualLocator
from src.core.u2_manager import get_u2

u2 = get_u2()
u2.connect()

# 回到桌面，启动设置
print("回到桌面...")
u2.press_home()
time.sleep(1)

print("启动设置...")
u2.launch_app('com.android.settings')
time.sleep(3)

# 截图保存
u2.save_screenshot('D:/ai_and/screen.png')
print("截图保存: screen.png")

# 获取屏幕尺寸
size = u2.get_window_size()
print(f"屏幕尺寸: {size['width']}x{size['height']}")

# 测试 AI 定位
locator = VisualLocator()

# 测试定位"显示"
print("\n=== 测试定位 '显示' ===")
result = locator.find_element('显示')
print(f"定位结果: {json.dumps(result, ensure_ascii=False, indent=2)}")

# 测试定位"声音"
print("\n=== 测试定位 '声音' ===")
result2 = locator.find_element('声音')
print(f"定位结果: {json.dumps(result2, ensure_ascii=False, indent=2)}")

print("\n调试完成！")
