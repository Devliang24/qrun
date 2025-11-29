"""精确点击测试 - 先滚动到顶部"""
import os
import time
import json

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10796'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10796'

from src.llm.visual_locator import VisualLocator
from src.core.u2_manager import get_u2

u2 = get_u2()
u2.connect()

print("回到桌面...")
u2.press_home()
time.sleep(1)

print("启动设置...")
u2.launch_app('com.android.settings')
time.sleep(3)

# 向上滚动几次确保在顶部
print("滚动到顶部...")
for _ in range(3):
    u2.swipe_ext('down', scale=0.5)  # down = 向上滚动
    time.sleep(0.5)

time.sleep(1)

# 截图
u2.save_screenshot('D:/ai_and/screen_top.png')
print("顶部截图: screen_top.png")

# AI 定位
locator = VisualLocator()

# 定位网络和互联网（应该在顶部）
print("\n=== 测试定位 '网络和互联网' ===")
result = locator.find_element('网络和互联网')
print(f"定位结果: {json.dumps(result, ensure_ascii=False, indent=2)}")

if result.get('found'):
    print(f"\n点击坐标 ({result['x']}, {result['y']})...")
    u2.tap(result['x'], result['y'])
    time.sleep(2)
    u2.save_screenshot('D:/ai_and/network_page.png')
    print("截图: network_page.png")

print("测试完成!")
