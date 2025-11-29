"""稳定版测试 - 每次操作前确认页面状态"""
import os
import time

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10796'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10796'

from src.llm.visual_locator import VisualLocator
from src.core.u2_manager import get_u2

def ensure_settings_top(u2):
    """确保设置页面在顶部"""
    # 多次向下滑动确保到顶
    for _ in range(5):
        u2.swipe_ext('down', scale=0.8)
        time.sleep(0.3)
    # 等待页面完全稳定（滚动惯性消失）
    time.sleep(2)

def click_with_verification(locator, u2, target, expected_title):
    """点击并验证结果"""
    print(f"\n点击 '{target}'...")
    
    # 点击前截图
    u2.save_screenshot(f'D:/ai_and/results/before_{target}.png')
    
    # 执行点击
    locator.click_element(target)
    time.sleep(2)
    
    # 点击后截图
    u2.save_screenshot(f'D:/ai_and/results/after_{target}.png')
    
    # 验证
    result = locator.verify_state(f"页面标题包含'{expected_title}'")
    success = result.get('passed', False)
    
    if success:
        print(f"  成功! 进入了 {expected_title} 页面")
    else:
        print(f"  失败! 期望 {expected_title}，实际: {result.get('reason', '未知')}")
    
    return success

def main():
    print("=" * 60)
    print("稳定版测试 - 智能验证")
    print("=" * 60)
    
    u2 = get_u2()
    u2.connect()
    locator = VisualLocator()
    
    os.makedirs('D:/ai_and/results', exist_ok=True)
    
    results = []
    
    # ========== 测试1: 网络和互联网 ==========
    print("\n" + "-" * 40)
    print("测试1: 进入网络和互联网")
    print("-" * 40)
    
    u2.press_home()
    time.sleep(1)
    u2.launch_app('com.android.settings')
    time.sleep(2)
    ensure_settings_top(u2)
    
    # 先查询页面确认
    print("查询当前页面菜单项...")
    items = locator.query_data("返回前3个可见的设置菜单项名称")
    print(f"  前3项: {items}")
    
    success = click_with_verification(locator, u2, '网络和互联网', '网络')
    results.append(('网络和互联网', success))
    u2.press_back()
    time.sleep(1)
    
    # ========== 测试2: 应用 ==========
    print("\n" + "-" * 40)
    print("测试2: 进入应用")
    print("-" * 40)
    
    ensure_settings_top(u2)
    success = click_with_verification(locator, u2, '应用', '应用')
    results.append(('应用', success))
    u2.press_back()
    time.sleep(1)
    
    # ========== 测试3: 通知 ==========
    print("\n" + "-" * 40)
    print("测试3: 进入通知")
    print("-" * 40)
    
    ensure_settings_top(u2)
    success = click_with_verification(locator, u2, '通知', '通知')
    results.append(('通知', success))
    u2.press_back()
    time.sleep(1)
    
    # ========== 测试4: 存储 ==========
    print("\n" + "-" * 40)
    print("测试4: 进入存储")
    print("-" * 40)
    
    ensure_settings_top(u2)
    success = click_with_verification(locator, u2, '存储', '存储')
    results.append(('存储', success))
    
    if success:
        # 额外测试：提取存储数据
        print("\n  提取存储使用信息...")
        storage = locator.query_data("返回已使用存储空间大小和总空间大小")
        print(f"  存储信息: {storage}")
    
    u2.press_back()
    
    # ========== 汇总 ==========
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    for name, success in results:
        status = "通过" if success else "失败"
        print(f"  {name}: {status}")
        if success:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 通过")
    
    return passed == len(results)

if __name__ == '__main__':
    main()
