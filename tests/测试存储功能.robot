*** Settings ***
Library    src/robot_lib/AITestLibrary.py

*** Test Cases ***
测试存储功能
    AI Open App
    AI Sleep    2
    AI Click    存储
    AI Sleep    1
    AI Click    存储空间
    AI Sleep    1
    AI Assert    存储空间已显示
    AI Sleep    1
    AI Back
    AI Sleep    1
    AI Close App