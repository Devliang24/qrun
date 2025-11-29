"""最终验证测试"""
import os
import time

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10796'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10796'

from src.core.u2_manager import get_u2
from src.llm.visual_locator import VisualLocator

u2 = get_u2()
u2.connect()
locator = VisualLocator()

print("=" * 60)
print("最终验证测试 - AI 定位 + 点击")
print("=" * 60)

results = []

targets = [
    ('网络和互联网', '网络和互联网'),
    ('应用', '应用'),
    ('通知', '通知'),
    ('存储', '存储'),
]

for target, verify_keyword in targets:
    print(f"\n--- 测试: {target} ---")
    
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
    
    # AI 定位
    print(f"AI 定位 '{target}'...")
    result = locator.find_element(target)
    
    if result.get('found'):
        x, y = result['x'], result['y']
        print(f"  定位坐标: ({x}, {y})")
        
        # 点击
        locator.click_element(target)
        time.sleep(1.5)
        
        # 截图
        u2.save_screenshot(f'D:/ai_and/results/final_{target}.png')
        
        # 验证
        verify = locator.verify_state(f"当前页面的标题包含'{verify_keyword}'")
        passed = verify.get('passed', False)
        
        if passed:
            print(f"  结果: 成功!")
        else:
            print(f"  结果: 失败 - {verify.get('reason', '未知')}")
        
        results.append((target, passed))
    else:
        print(f"  定位失败!")
        results.append((target, False))

print("\n" + "=" * 60)
print("测试结果汇总:")
print("=" * 60)
passed_count = 0
for target, passed in results:
    status = "通过" if passed else "失败"
    print(f"  {target}: {status}")
    if passed:
        passed_count += 1

print(f"\n总计: {passed_count}/{len(results)} 通过")
