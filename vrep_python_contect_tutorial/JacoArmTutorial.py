from __future__ import division #导入python未来支持的语言特征division(精确除法)，当我们没有在程序中导入该特征时，"/"操作符执行的是截断除法(Truncating Division),当我们导入精确除法之后，"/"执行的是精确除法
import time
import math
import numpy as np
import sys
sys.path.append('./vrep_remoteAPI')
import sim
#教程地址:https://blog.csdn.net/weixin_41754912/article/details/82353012?utm_medium=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-1.channel_param&depth_1-utm_source=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-1.channel_param

RAD2DEG = 180 / math.pi   # 常数，弧度转度数
tstep = 0.005             # 定义仿真步长
# 配置关节信息
jointNum = 6
baseName = 'Jaco'
jointName = 'Jaco_joint'

if __name__ == '__main__':
    print('Program started')
    # 关闭潜在的连接
    sim.simxFinish(-1)
    # 每隔0.2s检测一次，直到连接上V-rep
    while True:
        clientID = sim.simxStart('127.0.0.1', 19999, True, True, 5000, 5)
        if clientID > -1:
            break
        else:
            time.sleep(0.2)
            print("Failed connecting to remote API server!")
    print("Connection success!")
    # 设置仿真步长，为了保持API端与V-rep端相同步长
    sim.simxSetFloatingParameter(clientID, sim.sim_floatparam_simulation_time_step, tstep, sim.simx_opmode_oneshot)
    # 然后打开同步模式
    sim.simxSynchronous(clientID, True)
    sim.simxStartSimulation(clientID, sim.simx_opmode_oneshot)

    # 然后读取Base和Joint的句柄
    jointHandle = np.zeros((jointNum,), dtype=np.int)  # 注意是整型
    for i in range(jointNum):
        _, returnHandle = sim.simxGetObjectHandle(clientID, jointName + str(i + 1), sim.simx_opmode_blocking)
        jointHandle[i] = returnHandle

    _, baseHandle = sim.simxGetObjectHandle(clientID, baseName, sim.simx_opmode_blocking)

    print('Handles available!')

    # 然后首次读取关节的初始值，以streaming的形式
    jointConfig = np.zeros((jointNum,))
    for i in range(jointNum):
        _, jpos = sim.simxGetJointPosition(clientID, jointHandle[i], sim.simx_opmode_streaming)
        jointConfig[i] = jpos
    lastCmdTime = sim.simxGetLastCmdTime(clientID)  # 记录当前时间
    sim.simxSynchronousTrigger(clientID)  # 让仿真走一步
    # 开始仿真
    while sim.simxGetConnectionId(clientID) != -1:
        currCmdTime = sim.simxGetLastCmdTime(clientID)  # 记录当前时间
        dt = currCmdTime - lastCmdTime  # 记录时间间隔，用于控制
        print("curr time is: %ds cost time is : %ds" %(currCmdTime, dt))
        # ***
        #此处添加控制代码
        # 读取当前的状态值，之后都用buffer形式读取
        for i in range(jointNum):
            _, jpos = sim.simxGetJointPosition(clientID, jointHandle[i], sim.simx_opmode_buffer)
            print(round(jpos * RAD2DEG, 2))
            jointConfig[i] = jpos

        # 控制命令需要同时方式，故暂停通信，用于存储所有控制命令一起发送
        sim.simxPauseCommunication(clientID, True)
        for i in range(jointNum):
            sim.simxSetJointTargetPosition(clientID, jointHandle[i], 120/RAD2DEG, sim.simx_opmode_oneshot)
        sim.simxPauseCommunication(clientID, False)
        # ***

        lastCmdTime = currCmdTime  # 记录当前时间
        sim.simxSynchronousTrigger(clientID)  # 进行下一步
        _, contectTime = sim.simxGetPingTime(clientID)  # 使得该仿真步走完
        print("contect Time is: %ds" %contectTime)