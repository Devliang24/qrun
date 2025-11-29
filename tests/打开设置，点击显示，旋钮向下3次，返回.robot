*** Settings ***
Library    src/robot_lib/AITestLibrary.py

*** Test Cases ***
打开设置点击显示旋钮向下3次返回
    AI Open App    设置
    AI Sleep    2
    AI Click    显示
    AI Sleep    1
    AI Rotary    counterclockwise    3
    AI Sleep    1
    AI Back
    AI Sleep    1