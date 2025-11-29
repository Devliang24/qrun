*** Settings ***
Library    src/robot_lib/AITestLibrary.py

*** Test Cases ***
打开设置查看字体大小并返回
    AI Open App    设置
    AI Sleep    2
    AI Click    显示
    AI Sleep    1
    AI Assert    字体大小可见
    AI Sleep    1
    AI Back
    AI Sleep    1