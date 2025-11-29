"""Genymotion 设备管理模块"""
import subprocess
import time
import re
from pathlib import Path
from typing import Optional, Dict, List

from .config_manager import get_config


class DeviceManager:
    """Genymotion 设备管理器"""
    
    def __init__(self):
        config = get_config()
        self.player_path = config.get('genymotion.player_path', 
            'C:/Program Files/Genymobile/Genymotion/player.exe')
        self.device_name = config.get('genymotion.device_name', 'Google Pixel 3 XL')
        self.startup_timeout = config.get('genymotion.startup_timeout', 120)
        self._process = None
    
    def _run_adb(self, *args) -> subprocess.CompletedProcess:
        """运行 ADB 命令"""
        cmd = ['adb'] + list(args)
        return subprocess.run(cmd, capture_output=True, text=True)
    
    def get_connected_devices(self) -> List[Dict]:
        """获取已连接的设备列表"""
        result = self._run_adb('devices')
        devices = []
        
        for line in result.stdout.strip().split('\n')[1:]:
            if line.strip() and 'device' in line:
                parts = line.split()
                if len(parts) >= 2:
                    devices.append({
                        'udid': parts[0],
                        'status': parts[1]
                    })
        
        return devices
    
    def is_device_ready(self) -> bool:
        """检查设备是否就绪"""
        devices = self.get_connected_devices()
        return len(devices) > 0 and any(d['status'] == 'device' for d in devices)
    
    def get_device_udid(self) -> Optional[str]:
        """获取当前设备 UDID"""
        devices = self.get_connected_devices()
        for device in devices:
            if device['status'] == 'device':
                return device['udid']
        return None
    
    def start(self) -> bool:
        """启动 Genymotion 设备"""
        print(f"Starting device: {self.device_name}")
        
        # 检查是否已经运行
        if self.is_device_ready():
            udid = self.get_device_udid()
            print(f"Device already running: {udid}")
            return True
        
        # 检查 Genymotion player 是否存在
        player_path = Path(self.player_path)
        if not player_path.exists():
            print(f"Error: Genymotion player not found at {self.player_path}")
            return False
        
        # 启动设备
        print(f"[1/4] Starting VM...")
        cmd = f'"{self.player_path}" --vm-name "{self.device_name}"'
        self._process = subprocess.Popen(cmd, shell=True)
        
        # 等待设备启动
        print(f"[2/4] Booting Android...")
        start_time = time.time()
        while time.time() - start_time < self.startup_timeout:
            if self.is_device_ready():
                break
            time.sleep(2)
        else:
            print("Error: Device startup timeout")
            return False
        
        # 等待系统完全启动
        print(f"[3/4] Connecting ADB...")
        time.sleep(5)
        
        # 验证连接
        print(f"[4/4] Verifying connection...")
        udid = self.get_device_udid()
        if udid:
            print(f"\nDevice ready: {udid}")
            return True
        
        return False
    
    def stop(self) -> bool:
        """停止设备"""
        print(f"Stopping device: {self.device_name}")
        
        # 尝试使用 adb 关闭
        udid = self.get_device_udid()
        if udid:
            self._run_adb('emu', 'kill')
        
        # 关闭进程
        if self._process:
            self._process.terminate()
            self._process = None
        
        print("Device stopped")
        return True
    
    def restart(self) -> bool:
        """重启设备"""
        self.stop()
        time.sleep(3)
        return self.start()
    
    def get_status(self) -> Dict:
        """获取设备状态"""
        devices = self.get_connected_devices()
        udid = self.get_device_udid()
        
        return {
            'running': self.is_device_ready(),
            'udid': udid,
            'devices': devices,
            'device_name': self.device_name
        }
    
    def take_screenshot(self, output_path: str) -> bool:
        """截取屏幕截图"""
        try:
            # 使用 adb 截图
            result = self._run_adb('exec-out', 'screencap', '-p')
            if result.returncode == 0:
                with open(output_path, 'wb') as f:
                    f.write(result.stdout.encode('latin-1'))
                return True
        except Exception as e:
            print(f"Screenshot failed: {e}")
        return False
    
    def get_screenshot_bytes(self) -> Optional[bytes]:
        """获取截图字节数据"""
        try:
            result = subprocess.run(
                ['adb', 'exec-out', 'screencap', '-p'],
                capture_output=True
            )
            if result.returncode == 0:
                return result.stdout
        except Exception as e:
            print(f"Screenshot failed: {e}")
        return None
