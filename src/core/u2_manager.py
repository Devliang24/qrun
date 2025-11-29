"""uiautomator2 设备管理模块"""
import time
import base64
from typing import Optional, Dict, Any

import uiautomator2 as u2

from .config_manager import get_config


class U2Manager:
    """uiautomator2 设备管理器"""
    
    _instance = None
    _device = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.config = get_config()
    
    def connect(self) -> bool:
        """连接设备"""
        if self._device:
            try:
                self._device.info
                return True
            except:
                self._device = None
        
        device_serial = self.config.get('genymotion.device_serial', '127.0.0.1:16384')
        
        try:
            print(f"Connecting to device: {device_serial}")
            self._device = u2.connect(device_serial)
            info = self._device.info
            print(f"Connected: {info.get('productName', 'Unknown')}, SDK {info.get('sdkInt', '?')}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        self._device = None
        print("Device disconnected")
    
    @property
    def device(self):
        """获取设备实例"""
        if not self._device:
            self.connect()
        return self._device
    
    def get_screenshot_base64(self) -> Optional[str]:
        """获取截图的 base64 编码"""
        if self._device:
            try:
                img = self._device.screenshot()
                import io
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                return base64.b64encode(buffer.getvalue()).decode('utf-8')
            except Exception as e:
                print(f"Screenshot failed: {e}")
        return None
    
    def get_screenshot_bytes(self) -> Optional[bytes]:
        """获取截图字节数据"""
        if self._device:
            try:
                img = self._device.screenshot()
                import io
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                return buffer.getvalue()
            except Exception as e:
                print(f"Screenshot failed: {e}")
        return None
    
    def save_screenshot(self, filename: str):
        """保存截图到文件"""
        if self._device:
            try:
                self._device.screenshot(filename)
                return True
            except Exception as e:
                print(f"Save screenshot failed: {e}")
        return False
    
    def get_page_source(self) -> Optional[str]:
        """获取页面 XML 源码"""
        if self._device:
            try:
                return self._device.dump_hierarchy()
            except Exception as e:
                print(f"Get page source failed: {e}")
        return None
    
    def get_window_size(self) -> Dict[str, int]:
        """获取窗口大小"""
        if self._device:
            try:
                info = self._device.info
                return {
                    'width': info.get('displayWidth', 1080),
                    'height': info.get('displayHeight', 1920)
                }
            except:
                pass
        return {'width': 1080, 'height': 1920}
    
    def tap(self, x: int, y: int):
        """点击屏幕坐标"""
        if self._device:
            self._device.click(x, y)
    
    def double_tap(self, x: int, y: int):
        """双击屏幕坐标"""
        if self._device:
            self._device.double_click(x, y)
    
    def long_press(self, x: int, y: int, duration: float = 1.0):
        """长按屏幕坐标"""
        if self._device:
            self._device.long_click(x, y, duration)
    
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5):
        """滑动屏幕"""
        if self._device:
            self._device.swipe(start_x, start_y, end_x, end_y, duration)
    
    def swipe_ext(self, direction: str, scale: float = 0.8):
        """扩展滑动 (up/down/left/right)"""
        if self._device:
            self._device.swipe_ext(direction, scale=scale)
    
    def send_keys(self, text: str, clear: bool = False):
        """发送文本（支持中文）"""
        if self._device:
            if clear:
                self._device.clear_text()
            self._device.send_keys(text)
    
    def send_action(self, action: str = 'search'):
        """发送输入法动作 (search/go/done/next/send)"""
        if self._device:
            self._device.send_action(action)
    
    def press_key(self, key: str):
        """按键 (home/back/recent/power/volume_up/volume_down/enter)"""
        if self._device:
            self._device.press(key)
    
    def press_back(self):
        """按返回键"""
        self.press_key('back')
    
    def press_home(self):
        """按主页键"""
        self.press_key('home')
    
    def press_enter(self):
        """按回车键"""
        self.press_key('enter')
    
    # AAOS 旋钮控制
    def rotary_scroll(self, direction: str, steps: int = 1):
        """旋钮滚动 (AAOS 车载)
        
        Args:
            direction: clockwise(顺时针/向下) 或 counterclockwise(逆时针/向上)
            steps: 滚动步数
        """
        if self._device:
            key = 'dpad_down' if direction == 'clockwise' else 'dpad_up'
            for _ in range(steps):
                self._device.press(key)
                time.sleep(0.2)
    
    def rotary_click(self):
        """旋钮点击确认 (AAOS 车载)"""
        self.press_enter()
    
    def rotary_nudge(self, direction: str):
        """旋钮轻推 (AAOS 车载) - 左右方向
        
        Args:
            direction: left 或 right
        """
        if self._device:
            key = 'dpad_left' if direction == 'left' else 'dpad_right'
            self._device.press(key)
    
    def launch_app(self, package: str = None):
        """启动应用"""
        if not package:
            package = self.config.get('app.package')
        
        if package and self._device:
            self._device.app_start(package)
            time.sleep(2)
    
    def stop_app(self, package: str = None):
        """停止应用"""
        if not package:
            package = self.config.get('app.package')
        
        if package and self._device:
            self._device.app_stop(package)
    
    def clear_app(self, package: str = None):
        """清除应用数据"""
        if not package:
            package = self.config.get('app.package')
        
        if package and self._device:
            self._device.app_clear(package)
    
    def get_current_app(self) -> Dict[str, str]:
        """获取当前应用信息"""
        if self._device:
            try:
                info = self._device.app_current()
                return {
                    'package': info.get('package', ''),
                    'activity': info.get('activity', '')
                }
            except:
                pass
        return {'package': '', 'activity': ''}
    
    def wait_activity(self, activity: str, timeout: float = 10) -> bool:
        """等待指定 Activity"""
        if self._device:
            try:
                return self._device.wait_activity(activity, timeout)
            except:
                pass
        return False
    
    def is_screen_on(self) -> bool:
        """屏幕是否亮着"""
        if self._device:
            try:
                return self._device.info.get('screenOn', False)
            except:
                pass
        return False
    
    def screen_on(self):
        """点亮屏幕"""
        if self._device:
            self._device.screen_on()
    
    def screen_off(self):
        """关闭屏幕"""
        if self._device:
            self._device.screen_off()
    
    def unlock(self):
        """解锁屏幕"""
        if self._device:
            self._device.unlock()
    
    def find_element(self, **kwargs):
        """查找元素
        
        支持的选择器:
        - text: 文本完全匹配
        - textContains: 文本包含
        - textStartsWith: 文本开头
        - resourceId: 资源ID
        - className: 类名
        - description: contentDescription
        - xpath: XPath
        """
        if self._device:
            return self._device(**kwargs)
        return None
    
    def exists(self, **kwargs) -> bool:
        """检查元素是否存在"""
        elem = self.find_element(**kwargs)
        return elem.exists if elem else False
    
    def wait_exists(self, timeout: float = 10, **kwargs) -> bool:
        """等待元素存在"""
        elem = self.find_element(**kwargs)
        return elem.wait(timeout=timeout) if elem else False
    
    def click_element(self, **kwargs):
        """点击元素"""
        elem = self.find_element(**kwargs)
        if elem and elem.exists:
            elem.click()
            return True
        return False
    
    def set_text(self, text: str, **kwargs):
        """设置元素文本"""
        elem = self.find_element(**kwargs)
        if elem and elem.exists:
            elem.set_text(text)
            return True
        return False


def get_u2() -> U2Manager:
    """获取 U2 管理器实例"""
    return U2Manager()
