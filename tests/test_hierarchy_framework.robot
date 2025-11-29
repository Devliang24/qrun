*** Settings ***
Library    ../src/robot_lib/AITestLibrary.py

*** Test Cases ***
Test Click Settings Items
    [Documentation]    测试 HierarchyLocator 通过框架点击设置项
    AI Open App
    AI Sleep    2
    
    # 点击通知
    AI Click    通知
    AI Sleep    1
    AI Back
    AI Sleep    1
    
    # 点击存储
    AI Click    存储
    AI Sleep    1
    AI Back
    AI Sleep    1
    
    # 点击显示
    AI Click    显示
    AI Sleep    1
    AI Back
