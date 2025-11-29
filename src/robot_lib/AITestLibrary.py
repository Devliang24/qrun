"""Robot Framework AI 测试库"""
import os
import sys
import time
from typing import Any, Optional

# 添加项目根目录到 sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_current_dir))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from robot.api.deco import keyword, library

# 延迟导入以避免循环引用
_locator = None
_planner = None
_u2 = None


def _get_locator():
    """获取定位器实例"""
    global _locator
    if _locator is None:
        from src.llm.hierarchy_locator import HierarchyLocator
        _locator = HierarchyLocator()
    return _locator


def _get_planner():
    global _planner
    if _planner is None:
        from src.llm.action_planner import ActionPlanner
        _planner = ActionPlanner()
    return _planner


def _get_u2():
    global _u2
    if _u2 is None:
        from src.core.u2_manager import get_u2
        _u2 = get_u2()
    return _u2


@library(scope='GLOBAL', auto_keywords=False)
class AITestLibrary:
    """
    AI 驱动的 Android 测试关键字库
    
    融合 Midscene 思想，提供纯视觉理解和自然语言 API。
    
    核心 Keywords:
    - AI Do: 自动规划风格，一句话完成多步骤
    - AI Click: 点击元素
    - AI Input: 输入文本
    - AI Assert: 智能验证
    - AI Query: 数据提取
    - AI Wait For: 智能等待
    """
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def __init__(self):
        self._connected = False
    
    def _ensure_connected(self):
        """确保已连接"""
        if not self._connected:
            u2 = _get_u2()
            if u2.connect():
                self._connected = True
            else:
                raise Exception("无法连接设备")
    
    # 常用应用包名映射
    APP_PACKAGES = {
        '设置': 'com.android.settings',
        '微信': 'com.tencent.mm',
        '支付宝': 'com.eg.android.AlipayGphone',
        '淘宝': 'com.taobao.taobao',
        '抖音': 'com.ss.android.ugc.aweme',
        '京东': 'com.jingdong.app.mall',
        '美团': 'com.sankuai.meituan',
        '饿了么': 'me.ele',
        '百度': 'com.baidu.searchbox',
        '高德地图': 'com.autonavi.minimap',
        'QQ': 'com.tencent.mobileqq',
        '网易云音乐': 'com.netease.cloudmusic',
        '哔哩哔哩': 'tv.danmaku.bili',
        'bilibili': 'tv.danmaku.bili',
        'b站': 'tv.danmaku.bili',
        '西瓜视频': 'com.ss.android.article.video',
        '今日头条': 'com.ss.android.article.news',
    }
    
    @keyword('AI Open App')
    def ai_open_app(self, app_name: str = None):
        """
        打开应用
        
        Args:
            app_name: 应用名称或包名（可选，默认打开配置的应用）
        
        Examples:
            | AI Open App |                    # 打开默认应用
            | AI Open App | 设置 |             # 打开设置
            | AI Open App | 微信 |             # 打开微信
            | AI Open App | com.tencent.mm |   # 用包名打开
        """
        self._ensure_connected()
        u2 = _get_u2()
        
        package = None
        if app_name:
            # 先查映射表
            if app_name in self.APP_PACKAGES:
                package = self.APP_PACKAGES[app_name]
            elif '.' in app_name:
                # 看起来像包名
                package = app_name
            else:
                # 尝试模糊匹配
                for name, pkg in self.APP_PACKAGES.items():
                    if app_name in name or name in app_name:
                        package = pkg
                        break
        
        if package:
            u2.device.app_start(package)
        else:
            u2.launch_app()
        time.sleep(2)
    
    @keyword('AI Close App')
    def ai_close_app(self):
        """
        关闭应用
        
        Examples:
            | AI Close App |
        """
        u2 = _get_u2()
        u2.stop_app()
    
    @keyword('AI Do')
    def ai_do(self, instruction: str):
        """
        自动规划风格 - 一句话完成多步骤操作
        
        AI 自动将自然语言指令拆解为具体操作并执行。
        
        Args:
            instruction: 自然语言指令
        
        Examples:
            | AI Do | 打开应用，输入用户名 test，点击登录 |
            | AI Do | 搜索商品手机，点击第一个，加入购物车 |
        """
        self._ensure_connected()
        planner = _get_planner()
        planner.execute(instruction)
    
    @keyword('AI Click')
    def ai_click(self, element_description: str):
        """
        点击元素（纯视觉定位）
        
        Args:
            element_description: 元素的自然语言描述
        
        Examples:
            | AI Click | 登录按钮 |
            | AI Click | 第一个商品 |
            | AI Click | 购物车图标 |
        """
        self._ensure_connected()
        locator = _get_locator()
        locator.click_element(element_description)
    
    @keyword('AI Input')
    def ai_input(self, text: str, element_description: str):
        """
        输入文本
        
        Args:
            text: 要输入的文本
            element_description: 输入框的描述
        
        Examples:
            | AI Input | testuser | 用户名输入框 |
            | AI Input | password123 | 密码输入框 |
            | AI Input | 手机 | 搜索框 |
        """
        self._ensure_connected()
        locator = _get_locator()
        locator.input_text(text, element_description)
    
    @keyword('AI Swipe')
    def ai_swipe(self, direction: str, distance: int = 500):
        """
        滑动屏幕
        
        Args:
            direction: 方向 (up/down/left/right)
            distance: 滑动距离（像素）
        
        Examples:
            | AI Swipe | up |
            | AI Swipe | down | 800 |
        """
        self._ensure_connected()
        u2 = _get_u2()
        size = u2.get_window_size()
        center_x = size['width'] // 2
        center_y = size['height'] // 2
        
        if direction == 'up':
            u2.swipe(center_x, center_y + distance//2, center_x, center_y - distance//2)
        elif direction == 'down':
            u2.swipe(center_x, center_y - distance//2, center_x, center_y + distance//2)
        elif direction == 'left':
            u2.swipe(center_x + distance//2, center_y, center_x - distance//2, center_y)
        elif direction == 'right':
            u2.swipe(center_x - distance//2, center_y, center_x + distance//2, center_y)
        else:
            raise ValueError(f"未知方向: {direction}")
        
        time.sleep(0.5)
    
    @keyword('AI Scroll To')
    def ai_scroll_to(self, element_description: str, max_scrolls: int = 5):
        """
        滚动直到元素可见
        
        Args:
            element_description: 元素描述
            max_scrolls: 最大滚动次数
        
        Examples:
            | AI Scroll To | 加载更多按钮 |
        """
        self._ensure_connected()
        locator = _get_locator()
        
        for i in range(max_scrolls):
            try:
                result = locator.find_element(element_description)
                if result.get('found', False):
                    return
            except:
                pass
            
            self.ai_swipe('up')
        
        raise Exception(f"滚动 {max_scrolls} 次后仍未找到: {element_description}")
    
    @keyword('AI Assert')
    def ai_assert(self, expected_state: str):
        """
        智能验证界面状态
        
        Args:
            expected_state: 期望的状态描述
        
        Examples:
            | AI Assert | 首页已显示 |
            | AI Assert | 购物车数量为 1 |
            | AI Assert | 显示登录成功提示 |
        
        Raises:
            AssertionError: 如果验证失败
        """
        self._ensure_connected()
        locator = _get_locator()
        result = locator.verify_state(expected_state)
        
        if not result.get('passed', False):
            reason = result.get('reason', expected_state)
            raise AssertionError(f"验证失败: {reason}")
    
    @keyword('AI Wait For')
    def ai_wait_for(self, condition: str, timeout: str = '30s'):
        """
        等待条件满足
        
        Args:
            condition: 条件描述
            timeout: 超时时间（如 30s, 1m）
        
        Examples:
            | AI Wait For | 页面加载完成 |
            | AI Wait For | 至少显示一个商品 | 60s |
        
        Raises:
            TimeoutError: 如果超时
        """
        self._ensure_connected()
        
        # 解析超时时间
        timeout_sec = self._parse_timeout(timeout)
        
        locator = _get_locator()
        locator.wait_for_condition(condition, timeout_sec)
    
    @keyword('AI Query')
    def ai_query(self, query_description: str) -> Any:
        """
        从界面提取数据
        
        Args:
            query_description: 查询描述
        
        Returns:
            提取的数据（通常是 list 或 dict）
        
        Examples:
            | ${items}= | AI Query | 返回商品列表，包含名称和价格 |
            | ${price}= | AI Query | 返回第一个商品的价格 |
        """
        self._ensure_connected()
        locator = _get_locator()
        return locator.query_data(query_description)
    
    @keyword('AI Get Text')
    def ai_get_text(self, element_description: str) -> str:
        """
        获取元素的文本内容
        
        Args:
            element_description: 元素描述
        
        Returns:
            str: 文本内容
        
        Examples:
            | ${text}= | AI Get Text | 价格标签 |
            | ${name}= | AI Get Text | 用户昵称 |
        """
        self._ensure_connected()
        locator = _get_locator()
        return locator.get_text(element_description)
    
    @keyword('AI Screenshot')
    def ai_screenshot(self, filename: str = 'screenshot.png'):
        """
        截取屏幕截图
        
        Args:
            filename: 保存文件名
        
        Examples:
            | AI Screenshot |
            | AI Screenshot | login_page.png |
        """
        self._ensure_connected()
        u2 = _get_u2()
        u2.save_screenshot(filename)
    
    @keyword('AI Back')
    def ai_back(self):
        """
        按返回键
        
        Examples:
            | AI Back |
        """
        self._ensure_connected()
        u2 = _get_u2()
        u2.press_back()
        time.sleep(0.5)
    
    @keyword('AI Home')
    def ai_home(self):
        """
        按主页键
        
        Examples:
            | AI Home |
        """
        self._ensure_connected()
        u2 = _get_u2()
        u2.press_home()
        time.sleep(0.5)
    
    @keyword('AI Sleep')
    def ai_sleep(self, seconds: str):
        """
        等待指定时间
        
        Args:
            seconds: 等待秒数
        
        Examples:
            | AI Sleep | 2 |
            | AI Sleep | 0.5 |
        """
        time.sleep(float(seconds))
    
    def _parse_timeout(self, timeout: str) -> int:
        """解析超时时间字符串"""
        timeout = timeout.strip().lower()
        
        if timeout.endswith('s'):
            return int(timeout[:-1])
        elif timeout.endswith('m'):
            return int(timeout[:-1]) * 60
        else:
            return int(timeout)
