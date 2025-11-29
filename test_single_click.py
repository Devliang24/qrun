"""单次点击测试 - 排查问题"""
import os
import time

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10796'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10796'

from src.llm.visual_locator import VisualLocator
from src.core.u2_manager import get_u2

u2 = get_u2()
u2.connect()
locator = VisualLocator()

print("=" * 60)
print("单次点击测试 - 点击通知")
print("=" * 60)

# 准备
u2.press_home()
time.sleep(1)
u2.launch_app('com.android.settings')
time.sleep(3)

# 滚动到顶部
print("\n滚动到顶部...")
for _ in range(5):
    u2.swipe_ext('down', scale=0.8)
    time.sleep(0.3)
time.sleep(3)  # 更长的等待

# 截图确认
u2.save_screenshot('D:/ai_and/results/single_before.png')
print("截图: single_before.png")

# 获取屏幕信息
size = u2.get_window_size()
print(f"屏幕尺寸: {size}")

# AI 定位通知
print("\nAI 定位 '通知'...")
result = locator.find_element('通知')
print(f"定位结果: {result}")

if result.get('found'):
    x, y = result['x'], result['y']
    print(f"\n原始坐标: ({x}, {y})")
    
    # 手动转换坐标
    adj_x, adj_y = locator._adjust_coordinates(x, y)
    print(f"转换后坐标: ({adj_x}, {adj_y})")
    
    # 直接点击（不通过 click_element）
    print(f"\n直接点击 ({adj_x}, {adj_y})...")
    u2.tap(adj_x, adj_y)
    time.sleep(2)
    
    u2.save_screenshot('D:/ai_and/results/single_after.png')
    print("截图: single_after.png")
    
    # 验证
    print("\n验证页面...")
    verify = locator.verify_state("当前页面标题是'通知'")
    print(f"验证结果: {verify}")

print("\n测试完成!")
