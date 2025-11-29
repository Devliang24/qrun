*** Settings ***
Library    src/robot_lib/AITestLibrary.py

*** Test Cases ***
打开西瓜视频并评论10个视频
    AI Open App    西瓜视频
    AI Sleep    2
    FOR    ${i}    IN RANGE    10
        TRY
            AI Click    视频播放区域
            AI Sleep    1
            AI Click    评论按钮
            AI Sleep    1
            AI Input    真好看    评论输入框
            AI Sleep    1
            AI Click    发送按钮
            AI Sleep    1
            AI Back
            AI Sleep    1
        EXCEPT
            Log    评论失败，跳过当前视频
        END
        AI Swipe    up
        AI Sleep    1
    END
    AI Close App