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
@click.version_option(version='0.1.0', prog_name='qrun')
def cli():
    """QRun - AI 驱动的 Android 测试框架"""
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


# ============== 测试生成 ==============

@cli.command('generate')
@click.argument('description')
@click.option('-y', '--yes', is_flag=True, help='免交互，直接保存并执行')
@click.option('-n', '--name', default=None, help='指定脚本名称')
@click.option('-s', '--save-only', is_flag=True, help='只保存，不执行')
def generate_test(description, yes, name, save_only):
    """一句话生成并执行测试脚本
    
    示例:
        qrun g "测试通知功能：点击通知，查看设置，返回" -y
        qrun generate "测试存储" -y
        qrun g "测试显示" -n test_display -s
    """
    from src.llm.script_generator import ScriptGenerator
    from src.core.test_manager import TestManager
    
    generator = ScriptGenerator()
    manager = TestManager()
    
    click.echo(f"\n{Fore.CYAN}[生成中]{Style.RESET_ALL} 正在生成脚本...")
    
    try:
        # 1. 生成脚本
        script = generator.generate(description)
        script_name = name or generator.extract_name(description)
        
        # 2. 显示脚本
        click.echo(f"\n{Fore.GREEN}[生成脚本]{Style.RESET_ALL} {script_name}.robot")
        click.echo("-" * 50)
        click.echo(script)
        click.echo("-" * 50)
        
        # 3. 交互或直接执行
        if yes:
            # 免交互模式：直接保存并执行
            path = generator.save(script_name, script)
            click.echo(f"\n{Fore.GREEN}[已保存]{Style.RESET_ALL} {path}")
            
            if not save_only:
                click.echo(f"\n{Fore.CYAN}[执行中]{Style.RESET_ALL} ...")
                result = manager.run_test(path)
                
                if result['success']:
                    click.echo(f"{Fore.GREEN}[完成]{Style.RESET_ALL} {result['message']}")
                else:
                    click.echo(f"{Fore.RED}[失败]{Style.RESET_ALL} {result['message']}")
                click.echo(f"[报告] {result.get('report', 'N/A')}")
        else:
            # 交互模式
            click.echo(f"\n{Fore.YELLOW}[?] 操作选择:{Style.RESET_ALL}")
            click.echo("    [y] 保存并执行")
            click.echo("    [n] 仅保存，不执行")
            click.echo("    [q] 取消")
            
            choice = click.prompt("选择", type=click.Choice(['y', 'n', 'q']), default='y')
            
            if choice == 'q':
                click.echo("已取消")
                return
            
            # 保存脚本
            path = generator.save(script_name, script)
            click.echo(f"\n{Fore.GREEN}[已保存]{Style.RESET_ALL} {path}")
            
            if choice == 'y':
                click.echo(f"\n{Fore.CYAN}[执行中]{Style.RESET_ALL} ...")
                result = manager.run_test(path)
                
                if result['success']:
                    click.echo(f"{Fore.GREEN}[完成]{Style.RESET_ALL} {result['message']}")
                else:
                    click.echo(f"{Fore.RED}[失败]{Style.RESET_ALL} {result['message']}")
                click.echo(f"[报告] {result.get('report', 'N/A')}")
            else:
                click.echo(f"\n可用 'qrun r {path}' 执行")
                
    except Exception as e:
        click.echo(f"{Fore.RED}[FAIL]{Style.RESET_ALL} 生成失败: {e}")
        sys.exit(1)


@cli.command('list')
def list_tests():
    """列出所有测试脚本"""
    from src.core.test_manager import TestManager
    
    manager = TestManager()
    tests = manager.list_tests()
    
    if not tests:
        click.echo("暂无测试脚本")
        return
    
    click.echo(f"\n{Fore.CYAN}测试脚本列表:{Style.RESET_ALL}")
    click.echo("-" * 30)
    for i, test in enumerate(tests, 1):
        click.echo(f"  {i}. {test}")
    click.echo("-" * 30)
    click.echo(f"共 {len(tests)} 个脚本")


@cli.command('show')
@click.argument('script_name')
def show_script(script_name):
    """查看脚本内容"""
    from src.core.test_manager import TestManager
    
    manager = TestManager()
    content = manager.get_script_content(script_name)
    
    if content is None:
        click.echo(f"{Fore.RED}[ERROR]{Style.RESET_ALL} 脚本不存在: {script_name}")
        return
    
    click.echo(f"\n{Fore.CYAN}[{script_name}.robot]{Style.RESET_ALL}")
    click.echo("-" * 50)
    click.echo(content)
    click.echo("-" * 50)


@cli.command('history')
@click.argument('script_name')
def show_history(script_name):
    """查看脚本执行历史"""
    from src.core.test_manager import TestManager
    
    manager = TestManager()
    history = manager.get_history(script_name)
    
    if not history:
        click.echo(f"暂无执行历史: {script_name}")
        return
    
    click.echo(f"\n{Fore.CYAN}执行历史 - {script_name}{Style.RESET_ALL}")
    click.echo("-" * 60)
    
    for i, record in enumerate(reversed(history[-10:]), 1):  # 最近10条
        status = f"{Fore.GREEN}PASS{Style.RESET_ALL}" if record['success'] else f"{Fore.RED}FAIL{Style.RESET_ALL}"
        time = record['timestamp'][:19].replace('T', ' ')
        click.echo(f"  {i}. [{status}] {time} - {record['passed']}passed/{record['failed']}failed")
    
    click.echo("-" * 60)


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


# ============== 命令别名 ==============
cli.add_command(generate_test, name='g')
cli.add_command(list_tests, name='ls')
cli.add_command(show_script, name='s')
cli.add_command(show_history, name='h')
cli.add_command(run_test, name='r')


if __name__ == '__main__':
    cli()
