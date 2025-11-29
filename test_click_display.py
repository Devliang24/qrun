"""测试点击显示菜单"""
import os
import time

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10796'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10796'

from src.llm.visual_locator import VisualLocator
from src.core.u2_manager import get_u2

u2 = get_u2()
u2.connect()

# 回到桌面，启动设置
print("回到桌面...")
u2.press_home()
time.sleep(1)

print("启动设置...")
u2.launch_app('com.android.settings')
time.sleep(3)

# 截图
u2.save_screenshot('D:/ai_and/before_click.png')
print("点击前截图: before_click.png")

# AI 点击
locator = VisualLocator()
print("AI 点击: 显示...")
locator.click_element('显示')
time.sleep(2)

# 截图
u2.save_screenshot('D:/ai_and/after_click.png')
print("点击后截图: after_click.png")

print("测试完成!")
