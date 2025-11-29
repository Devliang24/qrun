"""坐标系统测试 - 直接点击验证"""
import os
import time

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10796'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10796'

from src.core.u2_manager import get_u2

u2 = get_u2()
u2.connect()

print("=" * 60)
print("坐标系统测试")
print("=" * 60)

# 准备
u2.press_home()
time.sleep(1)
u2.launch_app('com.android.settings')
time.sleep(3)

# 滚动到顶部
for _ in range(5):
    u2.swipe_ext('down', scale=0.8)
    time.sleep(0.3)
time.sleep(3)

# 截图
u2.save_screenshot('D:/ai_and/results/coord_test.png')
print("截图保存: coord_test.png")

# 获取屏幕尺寸
size = u2.get_window_size()
print(f"屏幕尺寸: {size}")

# 从截图分析，菜单项位置大约：
# 网络和互联网: y ≈ 85
# 应用: y ≈ 190
# 通知: y ≈ 295
# 存储: y ≈ 400

print("\n" + "-" * 40)
print("测试1: 点击 y=295（预期通知）")
print("-" * 40)
u2.tap(540, 295)
time.sleep(2)
u2.save_screenshot('D:/ai_and/results/tap_295.png')
print("截图: tap_295.png")
u2.press_back()
time.sleep(1)

# 回到设置并滚动到顶部
u2.launch_app('com.android.settings')
time.sleep(2)
for _ in range(5):
    u2.swipe_ext('down', scale=0.8)
    time.sleep(0.3)
time.sleep(2)

print("\n" + "-" * 40)
print("测试2: 点击 y=400（预期存储）")
print("-" * 40)
u2.tap(540, 400)
time.sleep(2)
u2.save_screenshot('D:/ai_and/results/tap_400.png')
print("截图: tap_400.png")
u2.press_back()
time.sleep(1)

# 回到设置
u2.launch_app('com.android.settings')
time.sleep(2)
for _ in range(5):
    u2.swipe_ext('down', scale=0.8)
    time.sleep(0.3)
time.sleep(2)

print("\n" + "-" * 40)
print("测试3: 点击 y=500（预期虚拟身份管理）")
print("-" * 40)
u2.tap(540, 500)
time.sleep(2)
u2.save_screenshot('D:/ai_and/results/tap_500_v2.png')
print("截图: tap_500_v2.png")

print("\n测试完成!")
