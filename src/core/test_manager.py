"""测试执行和管理"""
import os
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Optional


class TestManager:
    """测试脚本执行和历史管理"""
    
    def __init__(self):
        self.tests_dir = "tests"
        self.results_dir = "results"
    
    def run_test(self, script_path: str, output_dir: Optional[str] = None) -> Dict:
        """
        执行测试脚本
        
        Args:
            script_path: 脚本路径
            output_dir: 输出目录（可选）
            
        Returns:
            dict: 执行结果 {success, output_dir, passed, failed, message}
        """
        # 确定输出目录
        if output_dir is None:
            script_name = os.path.splitext(os.path.basename(script_path))[0]
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = os.path.join(self.results_dir, script_name, timestamp)
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 检查是否为 YAML 脚本
        robot_path = script_path
        if script_path.endswith('.yaml') or script_path.endswith('.yml'):
            from src.core.yaml_converter import YamlToRobotConverter
            converter = YamlToRobotConverter()
            
            # 生成临时 robot 文件
            temp_robot_path = script_path.rsplit('.', 1)[0] + '.robot'
            converter.convert_file(script_path, temp_robot_path)
            robot_path = temp_robot_path
            print(f"[Info] Converted YAML to Robot: {robot_path}")
        
        # 构建 robot 命令
        cmd = [
            'python', '-m', 'robot',
            '--outputdir', output_dir,
            robot_path
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # 解析结果
            output = result.stdout + result.stderr
            
            # 从输出中提取通过/失败数
            passed = 0
            failed = 0
            for line in output.split('\n'):
                if 'passed' in line.lower() and 'failed' in line.lower():
                    # 格式: "1 test, 1 passed, 0 failed"
                    import re
                    match = re.search(r'(\d+)\s+passed.*?(\d+)\s+failed', line)
                    if match:
                        passed = int(match.group(1))
                        failed = int(match.group(2))
                        break
            
            success = result.returncode == 0
            
            # 记录到历史
            self._save_history(script_path, {
                'timestamp': datetime.now().isoformat(),
                'success': success,
                'passed': passed,
                'failed': failed,
                'output_dir': output_dir
            })
            
            return {
                'success': success,
                'output_dir': output_dir,
                'passed': passed,
                'failed': failed,
                'message': f"{passed} passed, {failed} failed",
                'report': os.path.join(output_dir, 'report.html')
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output_dir': output_dir,
                'passed': 0,
                'failed': 0,
                'message': '执行超时'
            }
        except Exception as e:
            return {
                'success': False,
                'output_dir': output_dir,
                'passed': 0,
                'failed': 0,
                'message': str(e)
            }
    
    def _save_history(self, script_path: str, record: Dict):
        """保存执行历史"""
        script_name = os.path.splitext(os.path.basename(script_path))[0]
        history_dir = os.path.join(self.results_dir, script_name)
        history_file = os.path.join(history_dir, 'history.json')
        
        os.makedirs(history_dir, exist_ok=True)
        
        # 读取现有历史
        history = []
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                pass
        
        # 添加新记录
        history.append(record)
        
        # 保存
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def get_history(self, script_name: str) -> List[Dict]:
        """获取脚本执行历史"""
        history_file = os.path.join(self.results_dir, script_name, 'history.json')
        
        if not os.path.exists(history_file):
            return []
        
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def get_script_content(self, script_name: str) -> Optional[str]:
        """获取脚本内容"""
        # 尝试 .yaml
        script_path = os.path.join(self.tests_dir, f"{script_name}.yaml")
        if os.path.exists(script_path):
            with open(script_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        # 尝试 .robot
        script_path = os.path.join(self.tests_dir, f"{script_name}.robot")
        if os.path.exists(script_path):
            with open(script_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        return None
    
    def list_tests(self) -> List[str]:
        """列出所有测试脚本"""
        if not os.path.exists(self.tests_dir):
            return []
        
        tests = []
        for f in os.listdir(self.tests_dir):
            if f.endswith('.robot'):
                tests.append(f[:-6])
            elif f.endswith('.yaml'):
                tests.append(f[:-5])
        return tests
