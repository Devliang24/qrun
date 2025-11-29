"""精确坐标映射测试"""
import os
import time

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10796'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10796'

from src.core.u2_manager import get_u2
from src.llm.visual_locator import VisualLocator

u2 = get_u2()
u2.connect()
locator = VisualLocator()

def test_click(y_coord, expected):
    """测试点击指定 y 坐标"""
    # 准备
    u2.press_home()
    time.sleep(0.5)
    u2.launch_app('com.android.settings')
    time.sleep(2)
    
    # 滚动到顶部
    for _ in range(5):
        u2.swipe_ext('down', scale=0.8)
        time.sleep(0.2)
    time.sleep(2)
    
    # 点击
    print(f"点击 y={y_coord}, 期望: {expected}")
    u2.tap(300, y_coord)
    time.sleep(1)
    
    # 验证
    result = locator.verify_state(f"页面标题是'{expected}'")
    actual = "正确" if result.get('passed') else result.get('reason', '未知')
    print(f"  结果: {actual}")
    return result.get('passed', False)

print("=" * 60)
print("精确坐标映射测试")
print("=" * 60)

# 测试不同的 y 坐标
# 从截图分析，菜单项中心位置约为:
# 网络和互联网: 85, 应用: 190, 通知: 295, 存储: 400

results = []

# 测试网络和互联网
print("\n--- 测试网络和互联网 ---")
for y in [50, 85, 100, 150]:
    r = test_click(y, '网络')
    results.append((y, '网络', r))
    if r:
        print(f"  *** 找到正确坐标: y={y} ***")
        break

# 测试应用
print("\n--- 测试应用 ---")
for y in [150, 190, 220, 250]:
    r = test_click(y, '应用')
    results.append((y, '应用', r))
    if r:
        print(f"  *** 找到正确坐标: y={y} ***")
        break

print("\n" + "=" * 60)
print("测试结果汇总:")
for y, target, passed in results:
    status = "通过" if passed else "失败"
    print(f"  y={y} -> {target}: {status}")
