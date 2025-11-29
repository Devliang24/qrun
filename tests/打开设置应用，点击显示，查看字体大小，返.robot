*** Settings ***
Library    src/robot_lib/AITestLibrary.py

*** Test Cases ***
打开设置应用并查看字体大小
    AI Open App
    AI Sleep    2
    AI Click    设置
    AI Sleep    1
    AI Click    显示
    AI Sleep    1
    AI Click    字体大小
    AI Sleep    1
    AI Back
    AI Sleep    1
    AI Close App