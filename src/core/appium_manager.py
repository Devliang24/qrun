"""Appium 连接管理模块"""
import time
from typing import Optional, Dict, Any

try:
    from appium import webdriver
    from appium.options.android import UiAutomator2Options
    from appium.webdriver.common.appiumby import AppiumBy
except ImportError:
    webdriver = None
    UiAutomator2Options = None
    AppiumBy = None

from .config_manager import get_config
from .device_manager import DeviceManager


class AppiumManager:
    """Appium 连接管理器"""
    
    _instance = None
    _driver = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        config = get_config()
        self.server_url = config.get('appium.server_url', 'http://localhost:4723')
        self.device_manager = DeviceManager()
    
    def _build_capabilities(self) -> Dict[str, Any]:
        """构建 Appium Capabilities"""
        config = get_config()
        
        udid = self.device_manager.get_device_udid()
        
        capabilities = {
            'platformName': 'Android',
            'automationName': 'UiAutomator2',
            'noReset': True,
            'newCommandTimeout': 300,
        }
        
        # 设备 UDID
        if udid:
            capabilities['udid'] = udid
        
        # 应用配置
        app_package = config.get('app.package')
        app_activity = config.get('app.activity')
        
        if app_package:
            capabilities['appPackage'] = app_package
        if app_activity:
            capabilities['appActivity'] = app_activity
        
        # 合并配置文件中的额外配置
        extra_caps = config.get('appium.capabilities', {})
        capabilities.update(extra_caps)
        
        return capabilities
    
    def connect(self) -> bool:
        """连接到 Appium Server"""
        if not webdriver:
            raise ImportError("Appium-Python-Client 未安装，请运行: pip install Appium-Python-Client")
        
        if self._driver:
            try:
                # 检查连接是否有效
                self._driver.session_id
                return True
            except:
                self._driver = None
        
        # 检查设备是否就绪
        if not self.device_manager.is_device_ready():
            print("Error: No device connected")
            return False
        
        # 构建 capabilities
        capabilities = self._build_capabilities()
        
        try:
            print(f"Connecting to Appium server: {self.server_url}")
            
            if UiAutomator2Options:
                options = UiAutomator2Options()
                for key, value in capabilities.items():
                    setattr(options, key, value)
                self._driver = webdriver.Remote(self.server_url, options=options)
            else:
                self._driver = webdriver.Remote(
                    self.server_url,
                    desired_capabilities=capabilities
                )
            
            print("Appium connected successfully")
            return True
            
        except Exception as e:
            print(f"Appium connection failed: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self._driver:
            try:
                self._driver.quit()
            except:
                pass
            self._driver = None
            print("Appium disconnected")
    
    @property
    def driver(self):
        """获取 Appium driver"""
        if not self._driver:
            self.connect()
        return self._driver
    
    def get_screenshot_base64(self) -> Optional[str]:
        """获取截图的 base64 编码"""
        if self._driver:
            try:
                return self._driver.get_screenshot_as_base64()
            except Exception as e:
                print(f"Screenshot failed: {e}")
        return None
    
    def get_screenshot_bytes(self) -> Optional[bytes]:
        """获取截图字节数据"""
        if self._driver:
            try:
                return self._driver.get_screenshot_as_png()
            except Exception as e:
                print(f"Screenshot failed: {e}")
        return None
    
    def get_page_source(self) -> Optional[str]:
        """获取页面源码（UI 层级结构）"""
        if self._driver:
            try:
                return self._driver.page_source
            except Exception as e:
                print(f"Get page source failed: {e}")
        return None
    
    def get_window_size(self) -> Dict[str, int]:
        """获取窗口大小"""
        if self._driver:
            try:
                return self._driver.get_window_size()
            except:
                pass
        return {'width': 1080, 'height': 1920}
    
    def tap(self, x: int, y: int):
        """点击屏幕坐标"""
        if self._driver:
            self._driver.tap([(x, y)])
    
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 500):
        """滑动屏幕"""
        if self._driver:
            self._driver.swipe(start_x, start_y, end_x, end_y, duration)
    
    def send_keys(self, text: str):
        """发送按键"""
        if self._driver:
            # 使用 adb 输入，解决中文问题
            import subprocess
            subprocess.run(['adb', 'shell', 'input', 'text', text])
    
    def press_back(self):
        """按返回键"""
        if self._driver:
            self._driver.press_keycode(4)
    
    def press_home(self):
        """按主页键"""
        if self._driver:
            self._driver.press_keycode(3)
    
    def launch_app(self):
        """启动应用"""
        config = get_config()
        package = config.get('app.package')
        activity = config.get('app.activity')
        
        if package and activity:
            if self._driver:
                self._driver.activate_app(package)
    
    def close_app(self):
        """关闭应用"""
        config = get_config()
        package = config.get('app.package')
        
        if package and self._driver:
            self._driver.terminate_app(package)


def get_appium() -> AppiumManager:
    """获取 Appium 管理器实例"""
    return AppiumManager()
