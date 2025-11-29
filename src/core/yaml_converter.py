"""YAML 到 Robot Framework 脚本转换器"""
import yaml
from typing import Dict, List, Any, Union

class YamlToRobotConverter:
    """将 YAML 测试定义转换为 Robot Framework 脚本"""
    
    def convert(self, yaml_content: str) -> str:
        """转换 YAML 字符串为 Robot 脚本内容"""
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise ValueError(f"YAML 解析失败: {e}")
            
        if not isinstance(data, dict):
            raise ValueError("YAML 根节点必须是对象")
            
        name = data.get('name', 'Test Case')
        steps = data.get('steps', [])
        
        return self._build_robot_script(name, steps)
    
    def _build_robot_script(self, name: str, steps: List[Dict]) -> str:
        """构建完整的 Robot 脚本"""
        lines = [
            "*** Settings ***",
            "Library    src/robot_lib/AITestLibrary.py",
            "",
            "*** Test Cases ***",
            f"{name}"
        ]
        
        lines.extend(self._convert_steps(steps, indent_level=1))
        return "\n".join(lines)
    
    def _convert_steps(self, steps: List[Dict], indent_level: int) -> List[str]:
        """递归转换步骤列表"""
        lines = []
        indent = "    " * indent_level
        
        for step in steps:
            # 1. 普通 Action
            if 'action' in step:
                keyword = step['action']
                args = step.get('args', [])
                
                # 处理 args: 支持列表或单值
                if not isinstance(args, list):
                    args = [args]
                
                # 转义参数中的特殊字符（如 Robot 的变量语法）
                safe_args = []
                for arg in args:
                    arg_str = str(arg)
                    # 这里可以添加转义逻辑，暂时直接使用
                    safe_args.append(arg_str)
                
                # 构造行: Keyword    arg1    arg2
                line = f"{indent}{keyword}"
                if safe_args:
                    line += "    " + "    ".join(safe_args)
                lines.append(line)
                
            # 2. Loop 循环 (FOR)
            elif 'loop' in step:
                count = step['loop']
                sub_steps = step.get('steps', [])
                
                # Robot: FOR    ${i}    IN RANGE    count
                lines.append(f"{indent}FOR    ${{i}}    IN RANGE    {count}")
                lines.extend(self._convert_steps(sub_steps, indent_level + 1))
                lines.append(f"{indent}END")
                
            # 3. Try/Except (TRY)
            elif 'try' in step:
                try_steps = step['try'].get('steps', [])
                except_steps = step.get('except', {}).get('steps', [])
                
                lines.append(f"{indent}TRY")
                lines.extend(self._convert_steps(try_steps, indent_level + 1))
                lines.append(f"{indent}EXCEPT")
                lines.extend(self._convert_steps(except_steps, indent_level + 1))
                lines.append(f"{indent}END")
                
            # 4. While 循环
            elif 'while' in step:
                condition = step['while']
                sub_steps = step.get('steps', [])
                
                lines.append(f"{indent}WHILE    {condition}")
                lines.extend(self._convert_steps(sub_steps, indent_level + 1))
                lines.append(f"{indent}END")
                
        return lines

    def convert_file(self, yaml_path: str, output_path: str = None) -> str:
        """转换 YAML 文件到 Robot 文件"""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        robot_content = self.convert(content)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(robot_content)
            return output_path
        
        return robot_content
