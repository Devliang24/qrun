"""复杂场景测试 - 多步骤操作"""
import os
import time

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10796'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10796'

from src.llm.visual_locator import VisualLocator
from src.core.u2_manager import get_u2

def test_settings_navigation():
    """测试1: 设置页面多级导航"""
    print("\n" + "=" * 60)
    print("测试1: 设置页面多级导航")
    print("=" * 60)
    
    u2 = get_u2()
    u2.connect()
    locator = VisualLocator()
    
    # 准备
    u2.press_home()
    time.sleep(1)
    u2.launch_app('com.android.settings')
    time.sleep(2)
    
    # 滚动到顶部
    for _ in range(3):
        u2.swipe_ext('down', scale=0.5)
        time.sleep(0.3)
    time.sleep(1)
    
    # 步骤1: 点击"显示"
    print("\n[Step 1] 点击 '显示'...")
    try:
        locator.click_element('显示')
        time.sleep(2)
        u2.save_screenshot('D:/ai_and/results/step1_display.png')
        print("    成功 -> 截图: step1_display.png")
    except Exception as e:
        print(f"    失败: {e}")
        return False
    
    # 步骤2: 在显示页面验证状态
    print("\n[Step 2] AI 验证当前是显示设置页面...")
    result = locator.verify_state("当前页面是显示设置，标题显示'显示'")
    print(f"    验证结果: passed={result.get('passed')}, confidence={result.get('confidence')}")
    
    # 步骤3: 返回
    print("\n[Step 3] 返回上一级...")
    u2.press_back()
    time.sleep(1)
    
    # 步骤4: 点击"声音"
    print("\n[Step 4] 点击 '声音'...")
    try:
        locator.click_element('声音')
        time.sleep(2)
        u2.save_screenshot('D:/ai_and/results/step4_sound.png')
        print("    成功 -> 截图: step4_sound.png")
    except Exception as e:
        print(f"    失败: {e}")
        return False
    
    # 步骤5: 验证声音页面
    print("\n[Step 5] AI 验证当前是声音设置页面...")
    result = locator.verify_state("当前页面是声音设置")
    print(f"    验证结果: passed={result.get('passed')}")
    
    u2.press_back()
    print("\n测试1 完成!")
    return True


def test_scroll_and_click():
    """测试2: 滑动后点击"""
    print("\n" + "=" * 60)
    print("测试2: 滑动后点击隐藏元素")
    print("=" * 60)
    
    u2 = get_u2()
    u2.connect()
    locator = VisualLocator()
    
    # 准备
    u2.press_home()
    time.sleep(1)
    u2.launch_app('com.android.settings')
    time.sleep(2)
    
    # 滚动到顶部
    for _ in range(3):
        u2.swipe_ext('down', scale=0.5)
        time.sleep(0.3)
    time.sleep(1)
    
    # 向下滑动找到更多选项
    print("\n[Step 1] 向下滑动...")
    u2.swipe_ext('up', scale=0.6)
    time.sleep(1)
    u2.save_screenshot('D:/ai_and/results/scrolled.png')
    print("    截图: scrolled.png")
    
    # 查询当前可见的菜单项
    print("\n[Step 2] AI 查询当前可见菜单项...")
    items = locator.query_data("返回当前页面可见的所有设置菜单项名称，格式为JSON数组")
    print(f"    可见菜单: {items}")
    
    # 点击"关于手机"或"系统"
    print("\n[Step 3] 尝试点击 '系统' 或 '关于手机'...")
    try:
        locator.click_element('系统')
        time.sleep(2)
        u2.save_screenshot('D:/ai_and/results/system_page.png')
        print("    成功点击'系统' -> 截图: system_page.png")
    except:
        try:
            locator.click_element('关于手机')
            time.sleep(2)
            u2.save_screenshot('D:/ai_and/results/about_page.png')
            print("    成功点击'关于手机' -> 截图: about_page.png")
        except Exception as e:
            print(f"    失败: {e}")
            return False
    
    u2.press_back()
    print("\n测试2 完成!")
    return True


def test_ai_query():
    """测试3: AI 数据提取"""
    print("\n" + "=" * 60)
    print("测试3: AI 数据提取")
    print("=" * 60)
    
    u2 = get_u2()
    u2.connect()
    locator = VisualLocator()
    
    # 准备 - 进入存储页面
    u2.press_home()
    time.sleep(1)
    u2.launch_app('com.android.settings')
    time.sleep(2)
    
    # 滚动到顶部
    for _ in range(3):
        u2.swipe_ext('down', scale=0.5)
        time.sleep(0.3)
    time.sleep(1)
    
    # 点击存储
    print("\n[Step 1] 进入存储页面...")
    try:
        locator.click_element('存储')
        time.sleep(2)
        u2.save_screenshot('D:/ai_and/results/storage_page.png')
    except Exception as e:
        print(f"    进入存储失败: {e}")
        return False
    
    # AI 提取存储信息
    print("\n[Step 2] AI 提取存储使用情况...")
    storage_info = locator.query_data("""
分析存储页面，提取以下信息：
1. 已使用存储空间
2. 总存储空间
3. 各类别占用情况（如系统、应用等）
返回JSON格式
""")
    print(f"    存储信息: {storage_info}")
    
    u2.press_back()
    print("\n测试3 完成!")
    return True


def test_wifi_toggle():
    """测试4: WiFi 开关切换"""
    print("\n" + "=" * 60)
    print("测试4: WiFi 开关切换")
    print("=" * 60)
    
    u2 = get_u2()
    u2.connect()
    locator = VisualLocator()
    
    # 准备
    u2.press_home()
    time.sleep(1)
    u2.launch_app('com.android.settings')
    time.sleep(2)
    
    # 滚动到顶部
    for _ in range(3):
        u2.swipe_ext('down', scale=0.5)
        time.sleep(0.3)
    time.sleep(1)
    
    # 进入网络设置
    print("\n[Step 1] 进入网络和互联网...")
    locator.click_element('网络和互联网')
    time.sleep(2)
    
    # 查询 WiFi 状态
    print("\n[Step 2] AI 查询 WiFi 当前状态...")
    wifi_status = locator.query_data("查看互联网/WiFi的当前状态是开启还是关闭，返回JSON: {status: 'on'或'off'}")
    print(f"    WiFi 状态: {wifi_status}")
    
    # 点击互联网/WiFi
    print("\n[Step 3] 点击互联网选项...")
    try:
        locator.click_element('互联网')
        time.sleep(2)
        u2.save_screenshot('D:/ai_and/results/wifi_page.png')
        print("    成功 -> 截图: wifi_page.png")
    except Exception as e:
        print(f"    失败: {e}")
    
    u2.press_back()
    u2.press_back()
    print("\n测试4 完成!")
    return True


if __name__ == '__main__':
    # 确保结果目录存在
    import os
    os.makedirs('D:/ai_and/results', exist_ok=True)
    
    print("=" * 60)
    print("开始复杂场景测试")
    print("=" * 60)
    
    results = {}
    
    # 运行测试
    results['设置导航'] = test_settings_navigation()
    results['滑动点击'] = test_scroll_and_click()
    results['数据提取'] = test_ai_query()
    results['WiFi切换'] = test_wifi_toggle()
    
    # 汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for name, passed in results.items():
        status = "通过" if passed else "失败"
        print(f"  {name}: {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\n总计: {passed}/{total} 通过")
