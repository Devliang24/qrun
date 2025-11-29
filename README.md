# QRun - AI 驱动的 Android 业务测试框架

基于 **Robot Framework + 千问 VL + uiautomator2** 的智能化 Android 应用自动化测试工具，融合 **Midscene** 的视觉定位思想 (Set-of-Mark)。

## 核心特性

- **视觉定位 (Visual Grounding)** - 结合截图标记和多模态大模型，精准定位无障碍信息缺失的元素
- **自然语言交互** - 用自然语言描述操作 ("点击右侧的评论按钮")，无需编写复杂选择器
- **一句话自动化** - `qrun generate` 自动生成并执行测试脚本
- **智能数据提取** - `AI Query` 从界面截图中提取结构化数据
- **无需 Appium** - 直接使用 uiautomator2 + ADB，更轻量更稳定

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
pip install -e .
```

### 2. 配置

```bash
# 设置千问 API Key（从阿里云 DashScope 获取）
qrun config set qianwen.api_key "sk-your-key"

# 设置设备（可选，默认连接本地第一台设备）
qrun config set device.serial "127.0.0.1:7555"
```

### 3. 检查环境

```bash
qrun check-env
```

### 4. 生成并执行测试

```bash
# 一句话生成脚本并直接运行 (-y)
qrun generate "打开西瓜视频，向上滑动5个视频，对每个视频评论真好看" -y
```

### 5. 查看报告

```bash
qrun report
```

## AI Keywords

### 自动规划风格

```robot
AI Do    打开应用，输入用户名 test，点击登录
```

### 精确控制风格

```robot
AI Click    右侧的评论按钮
AI Input    真好看    评论输入框
AI Assert   首页已显示
AI Wait For    加载完成
AI Swipe    up
```

### 数据提取

```robot
${items}=    AI Query    返回商品列表，包含名称和价格
```

## 项目结构

```
qrun/
├── src/
│   ├── cli.py                  # CLI 入口 (qrun)
│   ├── llm/                    # LLM 核心模块
│   │   ├── qianwen_client.py   # 千问多模态客户端
│   │   ├── visual_locator.py   # Set-of-Mark 视觉定位器
│   │   ├── action_planner.py   # AI Do 规划
│   │   └── script_generator.py # 脚本生成器
│   ├── robot_lib/
│   │   └── AITestLibrary.py    # Robot Keywords
│   └── core/
│       ├── config_manager.py   # 配置管理
│       ├── u2_manager.py       # uiautomator2 设备管理
│       └── test_manager.py     # 测试执行管理
├── tests/                      # 测试用例
├── results/                    # 测试结果
├── config.yaml                 # 配置文件
└── requirements.txt            # 依赖
```

## CLI 命令

```bash
# 配置
qrun config set <key> <value>
qrun config show

# 测试生成与执行
qrun generate "<描述>" [-y] [-n name]
qrun run <test.robot>
qrun list
qrun show <script_name>
qrun history <script_name>

# 报告与分析
qrun report
qrun analyze <output.xml>
```

## 前置环境

- Python 3.10+
- Android 设备或模拟器 (开启 USB 调试)
- Android SDK Platform Tools (ADB)
- 千问 VL 模型 API Key (DashScope)

## 常见问题

**Q: 为什么点击位置不准确？**
A: 框架使用 Set-of-Mark 方案，会在截图上绘制编号。如果 XML 结构缺失或元素重叠，可能会影响 AI 判断。尝试优化描述，例如增加方位词："点击右下角的更多"。

**Q: 中文输入失败？**
A: 框架会自动尝试使用 ADB Keyboard 或剪贴板粘贴。请确保设备支持 `adb shell input` 或已安装相应的输入法服务 (ATX Agent 会自动处理)。

## License

MIT
