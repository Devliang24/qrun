"""完整的 AI 自动化测试示例"""
import os
import time

# 设置代理
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10796'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10796'

from src.llm.visual_locator import VisualLocator
from src.core.u2_manager import get_u2

def main():
    print("=" * 50)
    print("AI 自动化测试 Demo")
    print("=" * 50)
    
    # 连接设备
    u2 = get_u2()
    u2.connect()
    locator = VisualLocator()
    
    # 1. 回到桌面
    print("\n[Step 1] 回到桌面")
    u2.press_home()
    time.sleep(1)
    
    # 2. 启动设置
    print("[Step 2] 启动设置应用")
    u2.launch_app('com.android.settings')
    time.sleep(2)
    
    # 3. 截图并使用 AI 分析当前页面
    print("[Step 3] AI 分析当前页面")
    result = locator.verify_state("当前是设置页面")
    print(f"    验证结果: {result}")
    
    # 4. 使用 AI 查询页面内容
    print("[Step 4] AI 查询页面菜单项")
    data = locator.query_data("返回当前页面显示的所有设置菜单项名称列表")
    print(f"    菜单项: {data}")
    
    # 5. 点击显示
    print("[Step 5] AI 点击 '显示'")
    try:
        locator.click_element('显示')
        time.sleep(1)
        u2.save_screenshot('D:/ai_and/display_page.png')
        print("    成功，截图: display_page.png")
    except Exception as e:
        print(f"    失败: {e}")
    
    # 6. 返回
    print("[Step 6] 返回上一页")
    u2.press_back()
    time.sleep(1)
    
    print("\n" + "=" * 50)
    print("测试完成!")
    print("=" * 50)

if __name__ == '__main__':
    main()
