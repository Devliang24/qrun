"""直接坐标点击测试"""
import os
import time

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10796'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10796'

from src.core.u2_manager import get_u2

u2 = get_u2()
u2.connect()

# 获取设备信息
size = u2.get_window_size()
print(f"屏幕尺寸: {size['width']}x{size['height']}")

# 回到桌面，启动设置
print("回到桌面...")
u2.press_home()
time.sleep(1)

print("启动设置...")
u2.launch_app('com.android.settings')
time.sleep(3)

# 截图
u2.save_screenshot('D:/ai_and/test_screen.png')
print("截图: test_screen.png")

# 从截图来看，"显示"大约在 y=706 位置
# 但是 Genymotion 可能使用不同坐标系
# 让我测试点击不同的 y 坐标

print("\n直接点击测试 (x=200, y=706)...")
u2.tap(200, 706)
time.sleep(2)
u2.save_screenshot('D:/ai_and/tap_706.png')

# 返回
u2.press_back()
time.sleep(1)

print("\n直接点击测试 (x=200, y=600)...")
u2.tap(200, 600)
time.sleep(2)
u2.save_screenshot('D:/ai_and/tap_600.png')

# 返回
u2.press_back()
time.sleep(1)

print("\n直接点击测试 (x=200, y=500)...")
u2.tap(200, 500)
time.sleep(2)
u2.save_screenshot('D:/ai_and/tap_500.png')

print("测试完成!")
