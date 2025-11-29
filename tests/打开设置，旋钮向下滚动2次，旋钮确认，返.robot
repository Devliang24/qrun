*** Settings ***
Library    src/robot_lib/AITestLibrary.py

*** Test Cases ***
打开设置并操作旋钮
    AI Open App    设置
    AI Sleep    2
    AI Rotary    counterclockwise    2
    AI Sleep    1
    AI Rotary    click
    AI Sleep    1
    AI Back
    AI Sleep    1