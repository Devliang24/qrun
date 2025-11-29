*** Settings ***
Library    src/robot_lib/AITestLibrary.py

*** Test Cases ***
测试通知功能：点击通知，查看应用设置，返回
    AI Open App
    AI Sleep    2
    AI Click    通知
    AI Sleep    1
    AI Click    应用设置
    AI Sleep    1
    AI Back
    AI Sleep    1
    AI Close App