"""运行 Robot Framework 测试"""
import os
import sys
import subprocess

# 设置代理
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10796'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10796'

# 运行测试
result = subprocess.run([
    sys.executable, '-m', 'robot',
    '--outputdir', 'results',
    'tests/test_settings.robot'
], cwd=r'D:\ai_and')

sys.exit(result.returncode)
