"""CLI 入口"""
import os
import sys
import click
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from colorama import init, Fore, Style

# 初始化 colorama
init()


@click.group()
@click.version_option(version='0.1.0', prog_name='ai-test')
def cli():
    """AI 驱动的 Android 业务测试框架"""
    pass


# ============== 配置命令 ==============

@cli.group()
def config():
    """配置管理"""
    pass


@config.command('set')
@click.argument('key')
@click.argument('value')
def config_set(key, value):
    """设置配置项"""
    from src.core.config_manager import get_config
    
    config = get_config()
    config.set(key, value)
    click.echo(f"{Fore.GREEN}[OK]{Style.RESET_ALL} Set {key} = {value}")


@config.command('get')
@click.argument('key')
def config_get(key):
    """获取配置项"""
    from src.core.config_manager import get_config
    
    config = get_config()
    value = config.get(key)
    if value is not None:
        click.echo(f"{key} = {value}")
    else:
        click.echo(f"{Fore.YELLOW}未设置{Style.RESET_ALL}")


@config.command('show')
def config_show():
    """显示所有配置"""
    from src.core.config_manager import get_config
    import yaml
    
    config = get_config()
    click.echo(yaml.dump(config.show(), default_flow_style=False, allow_unicode=True))


@config.command('validate')
def config_validate():
    """验证配置"""
    from src.core.config_manager import get_config
    
    config = get_config()
    valid, errors = config.validate()
    
    if valid:
        click.echo(f"{Fore.GREEN}[OK]{Style.RESET_ALL} Config validation passed")
    else:
        click.echo(f"{Fore.RED}[FAIL]{Style.RESET_ALL} Config validation failed:")
        for error in errors:
            click.echo(f"  - {error}")


# ============== 环境检查 ==============

@cli.command('check-env')
def check_env():
    """检查运行环境"""
    import subprocess
    
    checks = []
    
    # 检查 Java
    try:
        result = subprocess.run(['java', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stderr.split('\n')[0] if result.stderr else 'unknown'
            checks.append(('Java', True, version))
        else:
            checks.append(('Java', False, '未安装'))
    except FileNotFoundError:
        checks.append(('Java', False, '未安装'))
    
    # 检查 Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            checks.append(('Node.js', True, result.stdout.strip()))
        else:
            checks.append(('Node.js', False, '未安装'))
    except FileNotFoundError:
        checks.append(('Node.js', False, '未安装'))
    
    # 检查 Appium
    try:
        result = subprocess.run(['appium', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            checks.append(('Appium', True, result.stdout.strip()))
        else:
            checks.append(('Appium', False, '未安装'))
    except FileNotFoundError:
        checks.append(('Appium', False, '未安装 (npm install -g appium)'))
    
    # 检查 ADB
    try:
        result = subprocess.run(['adb', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0] if result.stdout else 'unknown'
            checks.append(('ADB', True, version))
        else:
            checks.append(('ADB', False, '未安装'))
    except FileNotFoundError:
        checks.append(('ADB', False, '未安装 (需要 Android SDK Platform Tools)'))
    
    # 检查 Genymotion
    from src.core.config_manager import get_config
    config = get_config()
    player_path = config.get('genymotion.player_path', '')
    if Path(player_path).exists():
        checks.append(('Genymotion', True, player_path))
    else:
        checks.append(('Genymotion', False, '未找到 (检查 genymotion.player_path 配置)'))
    
    # 检查 Python 包
    try:
        import dashscope
        checks.append(('dashscope', True, dashscope.__version__ if hasattr(dashscope, '__version__') else 'installed'))
    except ImportError:
        checks.append(('dashscope', False, '未安装 (pip install dashscope)'))
    
    try:
        import robot
        checks.append(('robotframework', True, robot.__version__))
    except ImportError:
        checks.append(('robotframework', False, '未安装 (pip install robotframework)'))
    
    try:
        from AppiumLibrary import AppiumLibrary
        checks.append(('AppiumLibrary', True, 'installed'))
    except ImportError:
        checks.append(('AppiumLibrary', False, '未安装 (pip install robotframework-appiumlibrary)'))
    
    # 输出结果
    click.echo("\n环境检查结果:")
    click.echo("=" * 50)
    
    passed = 0
    total = len(checks)
    
    for name, status, info in checks:
        if status:
            click.echo(f"{Fore.GREEN}[OK]{Style.RESET_ALL} {name}: {info}")
            passed += 1
        else:
            click.echo(f"{Fore.RED}[X]{Style.RESET_ALL} {name}: {info}")
    
    click.echo("=" * 50)
    
    if passed == total:
        click.echo(f"{Fore.GREEN}环境检查通过 ({passed}/{total}){Style.RESET_ALL}")
    else:
        click.echo(f"{Fore.YELLOW}环境检查: {passed}/{total} 通过{Style.RESET_ALL}")
        click.echo(f"\n请安装缺失的组件后重新运行 'ai-test check-env'")


# ============== 设备管理 ==============

@cli.command('start')
def start_device():
    """启动 Genymotion 设备"""
    from src.core.device_manager import DeviceManager
    
    manager = DeviceManager()
    success = manager.start()
    
    if success:
        click.echo(f"{Fore.GREEN}[OK]{Style.RESET_ALL} Device started")
    else:
        click.echo(f"{Fore.RED}[FAIL]{Style.RESET_ALL} Device start failed")
        sys.exit(1)


@cli.command('stop')
def stop_device():
    """停止 Genymotion 设备"""
    from src.core.device_manager import DeviceManager
    
    manager = DeviceManager()
    manager.stop()
    click.echo(f"{Fore.GREEN}[OK]{Style.RESET_ALL} Device stopped")


@cli.command('status')
@click.option('--json', 'as_json', is_flag=True, help='输出 JSON 格式')
def device_status(as_json):
    """查看设备状态"""
    from src.core.device_manager import DeviceManager
    import json
    
    manager = DeviceManager()
    status = manager.get_status()
    
    if as_json:
        click.echo(json.dumps(status, indent=2))
    else:
        if status['running']:
            click.echo(f"{Fore.GREEN}[Running]{Style.RESET_ALL} {status['device_name']}")
            click.echo(f"  UDID: {status['udid']}")
        else:
            click.echo(f"{Fore.YELLOW}[Stopped]{Style.RESET_ALL} {status['device_name']}")


@cli.command('screenshot')
@click.argument('output', default='screenshot.png')
def take_screenshot(output):
    """截取屏幕截图"""
    from src.core.appium_manager import get_appium
    
    appium = get_appium()
    screenshot = appium.get_screenshot_bytes()
    
    if screenshot:
        with open(output, 'wb') as f:
            f.write(screenshot)
        click.echo(f"{Fore.GREEN}[OK]{Style.RESET_ALL} Screenshot saved: {output}")
    else:
        click.echo(f"{Fore.RED}[FAIL]{Style.RESET_ALL} Screenshot failed")


# ============== 测试生成 ==============

@cli.command('generate')
@click.argument('description')
@click.option('--output', '-o', help='输出文件路径')
def generate_test(description, output):
    """AI 生成测试用例"""
    from src.llm.test_generator import TestGenerator
    
    generator = TestGenerator()
    
    click.echo(f"正在生成测试用例...")
    
    try:
        result = generator.generate(description, output)
        click.echo(f"{Fore.GREEN}[OK]{Style.RESET_ALL} Generated: {result['file']}")
        click.echo(f"  Lines: {result['lines']}")
        click.echo(f"  AI Keywords: {result['keywords']}")
    except Exception as e:
        click.echo(f"{Fore.RED}[FAIL]{Style.RESET_ALL} Generation failed: {e}")
        sys.exit(1)


@cli.command('suggest')
@click.option('--feature', '-f', required=True, help='功能名称')
def suggest_scenarios(feature):
    """AI 建议测试场景"""
    from src.llm.test_generator import TestGenerator
    
    generator = TestGenerator()
    
    click.echo(f"正在分析 {feature} 功能...")
    
    try:
        scenarios = generator.suggest_scenarios(feature)
        click.echo(f"\n{Fore.CYAN}测试场景建议 - {feature}{Style.RESET_ALL}")
        click.echo("=" * 50)
        for i, scenario in enumerate(scenarios, 1):
            click.echo(f"{i}. {scenario}")
        click.echo("=" * 50)
        click.echo(f"\n生成测试: ai-test generate \"<场景描述>\"")
    except Exception as e:
        click.echo(f"{Fore.RED}[FAIL]{Style.RESET_ALL} Suggestion failed: {e}")
        sys.exit(1)


# ============== 测试运行 ==============

@cli.command('run')
@click.argument('test_file')
@click.option('--retry', '-r', default=0, help='失败重试次数')
def run_test(test_file, retry):
    """运行测试用例"""
    import subprocess
    from src.core.config_manager import get_config
    
    config = get_config()
    output_dir = config.get('robot.output_dir', './results')
    
    # 确保输出目录存在
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 构建 robot 命令
    cmd = [
        'python', '-m', 'robot',
        '--outputdir', output_dir,
        '--pythonpath', str(Path(__file__).parent.parent),
    ]
    
    if retry > 0:
        cmd.extend(['--rerunfailed', f'{output_dir}/output.xml', '--rerunfailedsuites'])
    
    cmd.append(test_file)
    
    click.echo(f"Running: {test_file}")
    click.echo("-" * 50)
    
    result = subprocess.run(cmd)
    
    click.echo("-" * 50)
    if result.returncode == 0:
        click.echo(f"{Fore.GREEN}Result: PASS{Style.RESET_ALL}")
    else:
        click.echo(f"{Fore.RED}Result: FAIL{Style.RESET_ALL}")
    
    click.echo(f"Report: {output_dir}/report.html")
    
    return result.returncode


@cli.command('report')
@click.argument('report_file', required=False)
def open_report(report_file):
    """打开测试报告"""
    import webbrowser
    from src.core.config_manager import get_config
    
    if not report_file:
        config = get_config()
        output_dir = config.get('robot.output_dir', './results')
        report_file = Path(output_dir) / 'report.html'
    
    report_path = Path(report_file)
    if report_path.exists():
        webbrowser.open(f'file://{report_path.absolute()}')
        click.echo(f"已打开报告: {report_path}")
    else:
        click.echo(f"{Fore.YELLOW}报告文件不存在: {report_path}{Style.RESET_ALL}")


# ============== 分析 ==============

@cli.command('analyze')
@click.argument('output_xml')
@click.option('--output', '-o', help='分析结果输出文件')
def analyze_results(output_xml, output):
    """AI 分析测试结果"""
    from src.llm.analyzer import ResultAnalyzer
    
    analyzer = ResultAnalyzer()
    
    click.echo(f"正在分析: {output_xml}")
    
    try:
        analysis = analyzer.analyze(output_xml)
        
        click.echo(f"\n{Fore.CYAN}AI 分析报告{Style.RESET_ALL}")
        click.echo("=" * 50)
        click.echo(analysis)
        click.echo("=" * 50)
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(analysis)
            click.echo(f"\n已保存到: {output}")
            
    except Exception as e:
        click.echo(f"{Fore.RED}[FAIL]{Style.RESET_ALL} Analysis failed: {e}")
        sys.exit(1)


@cli.command('clean')
@click.option('--older-than', default=7, help='清理多少天前的结果')
def clean_results(older_than):
    """清理测试结果"""
    import shutil
    from datetime import datetime, timedelta
    from src.core.config_manager import get_config
    
    config = get_config()
    output_dir = Path(config.get('robot.output_dir', './results'))
    
    if not output_dir.exists():
        click.echo("无结果目录")
        return
    
    cutoff = datetime.now() - timedelta(days=older_than)
    removed = 0
    
    for item in output_dir.iterdir():
        if item.is_file():
            mtime = datetime.fromtimestamp(item.stat().st_mtime)
            if mtime < cutoff:
                item.unlink()
                removed += 1
    
    click.echo(f"已清理 {removed} 个文件")


if __name__ == '__main__':
    cli()
