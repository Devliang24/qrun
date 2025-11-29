*** Settings ***
Documentation    登录功能测试示例
Library          ../src/robot_lib/AITestLibrary.py

*** Test Cases ***
测试正常登录流程
    [Documentation]    测试使用正确的用户名和密码登录
    [Tags]    登录    正常流程
    
    AI Open App
    
    # 输入登录信息
    AI Input    testuser    用户名输入框
    AI Input    password123    密码输入框
    
    # 点击登录
    AI Click    登录按钮
    
    # 验证登录成功
    AI Wait For    首页加载完成    30s
    AI Assert    首页已显示
    
    [Teardown]    AI Close App


测试使用AI Do登录
    [Documentation]    使用自动规划风格测试登录
    [Tags]    登录    AI规划
    
    AI Do    打开应用，输入用户名 testuser，输入密码 password123，点击登录按钮
    AI Assert    首页已显示用户昵称
    
    [Teardown]    AI Close App


测试提取商品信息
    [Documentation]    测试 AI Query 提取数据能力
    [Tags]    搜索    数据提取
    
    AI Open App
    
    # 搜索商品
    AI Do    搜索 手机
    AI Wait For    搜索结果显示
    
    # 提取商品数据
    ${items}=    AI Query    返回前3个商品的名称和价格
    Log    找到商品: ${items}
    
    # 验证数据
    Should Not Be Empty    ${items}
    
    [Teardown]    AI Close App
