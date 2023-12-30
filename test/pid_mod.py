from simple_pid import PID
import time
def pid_pwm_control(pid,current_angle, target_angle, pwm_duty_cycle, k_p, k_i, k_d, setpoint_range=(0, 100)):
    # 创建PID控制器
    # pid = PID(k_p, k_i, k_d, output_limits=(0, 30))

    # 设置目标值
    pid.setpoint = target_angle

    # 计算PID控制输出
    pid_output = pid(current_angle)

    # 更新PWM占空比
    new_pwm_duty_cycle = pid_output #+ pwm_duty_cycle

    # 确保PWM占空比保持在给定范围内
    new_pwm_duty_cycle = max(setpoint_range[0], min(setpoint_range[1], new_pwm_duty_cycle))

    return new_pwm_duty_cycle

# 主控制循环
def pid_ctrl(target_angle,get_angle,apply_DR):
    # ratio = 0.02
    (k_p, k_i, k_d) = (16,20.5,0.28)# (3.8,10,0.1)#Extensor (2.8,4,0.02) Flexor(2.5,2.35,0.068) # (60,80,4) *0.02 (160,80,3)
    # (k_p, k_i, k_d) = (k_p*ratio, k_i*ratio,k_d*ratio)
    limit_DR =  (0,40)                    
    durance = 2.5
    # P调大，反应速度快了，但是出现了超调，指针出现抖动，
    # I调大，在原来基础上，误差变小了
    # D调大，反应速度慢了，但是抖动消失了，且指针存在一定误差（没和下面对准）
    labels = ['DutyRatio','Time']
    # 初始PWM占空比和目标角度
    dutyRatio = 0  # 读取到当前的PWM 占空比 # (个人习惯)占空比 此处采用DR(dutyRatio)
    
    contorller = PID(k_p, k_i, k_d,sample_time=1/60,output_limits= limit_DR) # # 创建PID控制器
    contorller.setpoint = target_angle

    time_st = time.time()
    ctrl_DR_history = []
    while time.time() - time_st < durance:
        current_angle = get_angle()  # 获取当前角度
        # print(current_angle,current_DR)
        while True: # abs(current_angle - target_angle) > 0.05
            current_angle = get_angle()  # 获取当前角度
                     
            # current_DR = pid_pwm_control(contorller,current_angle, target_angle, current_DR, k_p, k_i, k_d,output_limits)# 调整PWM占空比  
            # 计算PID控制输出
            pid_output = contorller(current_angle)
            # print(pid_output)
            dutyRatio =  max(limit_DR[0], min(limit_DR[1], pid_output))# 确保PWM占空比保持在给定范围内 pid_output*output_limits*0.01 #
            
            apply_DR(pid_output) # 打印出来PWM/实际系统中是应用在系统里
            # print(f"Current Angle: {current_angle:.2f}°, PWM Duty Cycle: {current_DR:.2f}%")
            # print("Adjusting, Tar: ",target_angle," Cur delta:",current_angle-target_angle," DR: ",pid_output)
            if not (time.time() - time_st < durance): break
            ctrl_DR_history.append([pid_output,time.time()- RUNTIME])

    apply_DR(0)
    return ctrl_DR_history


if __name__ == "__main__":
    main([],[],[])