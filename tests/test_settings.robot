*** Settings ***
Documentation    设置应用 AI 测试示例
Library          ../src/robot_lib/AITestLibrary.py

*** Test Cases ***
测试打开声音设置
    [Documentation]    测试 AI 点击进入声音设置
    [Tags]    设置    声音
    
    AI Open App
    AI Click    声音
    AI Assert    显示音量调节滑块
    AI Back
    
    [Teardown]    AI Close App

测试查询设置菜单
    [Documentation]    测试 AI Query 提取菜单项
    [Tags]    设置    查询
    
    AI Open App
    ${menus}=    AI Query    返回当前显示的所有设置菜单项名称
    Log    菜单项: ${menus}
    AI Close App

测试滑动操作
    [Documentation]    测试滑动浏览设置
    [Tags]    设置    滑动
    
    AI Open App
    AI Swipe    down    500
    AI Sleep    1
    AI Screenshot    settings_scrolled.png
    AI Close App
