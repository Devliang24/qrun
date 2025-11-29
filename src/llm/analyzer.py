"""AI 测试结果分析器"""
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional

from .qianwen_client import QianwenClient


class ResultAnalyzer:
    """AI 驱动的测试结果分析器"""
    
    def __init__(self):
        self.qianwen = QianwenClient()
    
    def parse_output_xml(self, xml_path: str) -> Dict:
        """
        解析 Robot Framework 输出 XML
        
        Args:
            xml_path: output.xml 文件路径
        
        Returns:
            dict: 解析结果
        """
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        result = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'tests': [],
            'failures': []
        }
        
        # 查找所有测试
        for test in root.iter('test'):
            test_name = test.get('name', 'Unknown')
            status_elem = test.find('status')
            
            if status_elem is not None:
                status = status_elem.get('status', 'UNKNOWN')
                result['total'] += 1
                
                test_info = {
                    'name': test_name,
                    'status': status
                }
                
                if status == 'PASS':
                    result['passed'] += 1
                else:
                    result['failed'] += 1
                    
                    # 获取失败信息
                    msg = status_elem.text or ''
                    test_info['message'] = msg
                    
                    # 查找失败的关键字
                    for kw in test.iter('kw'):
                        kw_status = kw.find('status')
                        if kw_status is not None and kw_status.get('status') == 'FAIL':
                            kw_name = kw.get('name', '')
                            kw_msg = kw_status.text or ''
                            
                            # 获取参数
                            args = []
                            for arg in kw.findall('.//arg'):
                                if arg.text:
                                    args.append(arg.text)
                            
                            test_info['failed_keyword'] = {
                                'name': kw_name,
                                'args': args,
                                'message': kw_msg
                            }
                            break
                    
                    result['failures'].append(test_info)
                
                result['tests'].append(test_info)
        
        return result
    
    def analyze(self, xml_path: str) -> str:
        """
        AI 分析测试结果
        
        Args:
            xml_path: output.xml 文件路径
        
        Returns:
            str: 分析报告
        """
        # 解析 XML
        data = self.parse_output_xml(xml_path)
        
        # 如果没有失败，返回简单报告
        if data['failed'] == 0:
            return f"""测试统计:
  总数: {data['total']}
  通过: {data['passed']}
  失败: {data['failed']}

所有测试通过！"""
        
        # 构建失败信息
        failure_details = []
        for failure in data['failures']:
            detail = f"- 测试: {failure['name']}\n"
            if 'failed_keyword' in failure:
                kw = failure['failed_keyword']
                detail += f"  失败步骤: {kw['name']} {' '.join(kw['args'])}\n"
                detail += f"  错误信息: {kw['message']}\n"
            else:
                detail += f"  错误信息: {failure.get('message', 'Unknown')}\n"
            failure_details.append(detail)
        
        failure_text = '\n'.join(failure_details)
        
        # 调用 AI 分析
        prompt = f"""你是一个 Android 自动化测试专家。分析以下测试失败信息，提供原因分析和修复建议。

测试统计:
- 总数: {data['total']}
- 通过: {data['passed']}
- 失败: {data['failed']}

失败详情:
{failure_text}

请提供:
1. 可能的失败原因分析
2. 具体的修复建议
3. 如何避免类似问题

输出格式清晰，便于理解。"""
        
        analysis = self.qianwen.generate(prompt)
        
        # 组合报告
        report = f"""测试统计:
  总数: {data['total']}
  通过: {data['passed']}
  失败: {data['failed']}

失败用例:
{failure_text}

AI 分析:
{analysis}"""
        
        return report
