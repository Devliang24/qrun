"""测试 Midscene 风格坐标转换"""
import os
import time

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10796'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10796'

from src.llm.visual_locator import VisualLocator
from src.core.u2_manager import get_u2

u2 = get_u2()
u2.connect()

print("=" * 60)
print("Midscene 风格坐标转换测试")
print("=" * 60)

# 回到桌面，启动设置
print("\n[1] 回到桌面...")
u2.press_home()
time.sleep(1)

print("[2] 启动设置...")
u2.launch_app('com.android.settings')
time.sleep(3)

# 向上滚动确保在顶部
print("[3] 滚动到顶部...")
for _ in range(3):
    u2.swipe_ext('down', scale=0.5)
    time.sleep(0.5)
time.sleep(1)

# 截图
u2.save_screenshot('D:/ai_and/before_test.png')
print("[4] 截图保存: before_test.png")

# 使用改进后的 VisualLocator
locator = VisualLocator()

print("\n[5] AI 定位并点击 '网络和互联网'...")
print("-" * 40)
locator.click_element('网络和互联网')
time.sleep(2)

# 截图验证
u2.save_screenshot('D:/ai_and/after_test.png')
print("-" * 40)
print("[6] 点击后截图: after_test.png")

# 返回
u2.press_back()
time.sleep(1)

print("\n[7] 再次测试：点击 '应用'...")
print("-" * 40)
locator.click_element('应用')
time.sleep(2)

u2.save_screenshot('D:/ai_and/apps_page.png')
print("-" * 40)
print("[8] 应用页面截图: apps_page.png")

print("\n" + "=" * 60)
print("测试完成!")
print("=" * 60)
