"""测试 HierarchyLocator 新方案"""
import sys
sys.path.insert(0, '.')

from src.llm.hierarchy_locator import HierarchyLocator
from src.core.u2_manager import get_u2


def test_hierarchy_locator():
    """测试 UI Hierarchy + AI 匹配方案"""
    
    # 1. 连接设备
    print("=" * 50)
    print("测试 HierarchyLocator")
    print("=" * 50)
    
    u2 = get_u2()
    if not u2.connect():
        print("无法连接设备")
        return
    
    # 先打开设置应用
    print("\n[0] 打开设置应用...")
    u2.device.app_start('com.android.settings')
    import time
    time.sleep(2)
    
    # 2. 创建定位器
    locator = HierarchyLocator()
    
    # 3. 获取并解析 UI 层级
    print("\n[1] 解析 UI Hierarchy...")
    elements = locator.dump_and_parse()
    print(f"找到 {len(elements)} 个元素")
    
    # 显示前10个元素
    print("\n前10个元素:")
    for elem in elements[:10]:
        print(f"  [{elem.index}] {elem.display_text} ({elem.short_class}) bounds={elem.bounds}")
    
    # 4. 测试 AI 匹配
    print("\n[2] 测试 AI 元素匹配...")
    test_descriptions = [
        "网络和互联网",
        "显示",
        "通知",
    ]
    
    for desc in test_descriptions:
        print(f"\n查找: '{desc}'")
        try:
            elem = locator.find_element(desc)
            print(f"  [OK] 找到: {elem.display_text}")
            print(f"    bounds: {elem.bounds}")
            print(f"    center: {elem.center}")
        except Exception as e:
            print(f"  [FAIL] 失败: {e}")
    
    # 5. 测试点击（可选）
    print("\n[3] 测试点击 '显示'...")
    try:
        # 保存点击前截图
        u2.save_screenshot("results/hierarchy_before.png")
        
        locator.click_element("显示")
        print("  [OK] 点击成功")
        
        import time
        time.sleep(1)
        
        # 保存点击后截图
        u2.save_screenshot("results/hierarchy_after.png")
        
        # 返回
        u2.press_back()
        
    except Exception as e:
        print(f"  [FAIL] 点击失败: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)


if __name__ == '__main__':
    test_hierarchy_locator()
