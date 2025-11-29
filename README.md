# AI 驱动的 Android 业务测试框架

基于 **Robot Framework + 千问 VL + Appium** 的智能化 Android 应用自动化测试工具，融合 Midscene 的纯视觉理解思想。

## 核心特性

- **纯视觉理解** - 基于截图定位元素，不依赖 UI 树
- **自然语言 API** - 用人话描述操作，无需 xpath
- **AI Query** - 智能提取界面数据
- **AI Assert** - 智能验证界面状态
- **AI Do** - 自动规划风格，一句话完成多步骤

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
pip install -e .
```

### 2. 配置

```bash
# 设置千问 API Key（从阿里云 DashScope 获取）
ai-test config set qianwen.api_key "sk-your-key"

# 设置应用信息
ai-test config set app.package "com.example.app"
ai-test config set app.activity ".MainActivity"
```

### 3. 检查环境

```bash
ai-test check-env
```

### 4. 启动设备

```bash
# 终端 1: 启动 Appium
appium

# 终端 2: 启动 Genymotion 设备
ai-test start
```

### 5. 生成测试

```bash
ai-test generate "测试登录：输入用户名密码，点击登录，验证首页"
```

### 6. 运行测试

```bash
ai-test run tests/测试登录.robot
```

### 7. 查看报告

```bash
ai-test report
```

## AI Keywords

### 自动规划风格

```robot
AI Do    打开应用，输入用户名 test，点击登录
```

### 精确控制风格

```robot
AI Click    登录按钮
AI Input    testuser    用户名输入框
AI Assert   首页已显示
AI Wait For    加载完成
```

### 数据提取

```robot
${items}=    AI Query    返回商品列表，包含名称和价格
```

## 项目结构

```
ai_and/
├── src/
│   ├── cli.py                  # CLI 入口
│   ├── llm/                    # LLM 核心模块
│   │   ├── qianwen_client.py   # 千问客户端
│   │   ├── visual_locator.py   # 纯视觉定位
│   │   ├── action_planner.py   # AI Do 规划
│   │   └── test_generator.py   # 测试生成
│   ├── robot_lib/
│   │   └── AITestLibrary.py    # Robot Keywords
│   └── core/
│       ├── config_manager.py   # 配置管理
│       ├── device_manager.py   # Genymotion
│       └── appium_manager.py   # Appium
├── tests/                      # 测试用例
├── results/                    # 测试结果
├── config.yaml                 # 配置文件
└── requirements.txt            # 依赖
```

## CLI 命令

```bash
# 配置
ai-test config set <key> <value>
ai-test config show

# 环境
ai-test check-env
ai-test start
ai-test stop
ai-test status

# 测试
ai-test generate "<描述>"
ai-test run <test.robot>
ai-test report

# 分析
ai-test analyze <output.xml>
ai-test suggest --feature <功能>
```

## 前置环境

- Java JDK 8+
- Node.js 16+
- Appium (`npm install -g appium && appium driver install uiautomator2`)
- Android SDK Platform Tools（ADB）
- Genymotion + 虚拟设备
- Python 3.10+

## 配置文件

```yaml
qianwen:
  api_key: ""
  model: "qwen-vl-max"

genymotion:
  device_name: "Google Pixel 3 XL"
  auto_start: true

appium:
  server_url: "http://localhost:4723"

app:
  package: ""
  activity: ""
```

## License

MIT
