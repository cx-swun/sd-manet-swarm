# -*- coding:UTF-8 -*-

import socket
import requests

import RPi.GPIO as GPIO
import time
from flask import Flask

key = 8
speed = 20  # 设置初始速度
app: Flask = Flask(__name__)
# 小车电机引脚定义
IN1 = 20
IN2 = 21
IN3 = 19
IN4 = 26
ENA = 16
ENB = 13

# 设置GPIO口为BCM编码方式
GPIO.setmode(GPIO.BCM)

# 忽略警告信息
GPIO.setwarnings(False)
# 光敏电阻引脚定义
LdrSensorLeft = 7
LdrSensorRight = 6


@app.route('/')  # host page
def hello_world():
    return 'Hello World!'


# 电机引脚初始化操作
def motor_init():
    global pwm_ENA
    global pwm_ENB
    GPIO.setup(ENA, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(IN1, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(IN2, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(ENB, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(IN3, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(IN4, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(key, GPIO.IN)
    GPIO.setup(LdrSensorLeft, GPIO.IN)
    GPIO.setup(LdrSensorRight, GPIO.IN)
    # 设置pwm引脚和频率为2000hz
    pwm_ENA = GPIO.PWM(ENA, 2000)
    pwm_ENB = GPIO.PWM(ENB, 2000)
    pwm_ENA.start(0)
    pwm_ENB.start(0)


@app.route('/api/car/speed_up', methods=['get'])  # 速度增加，最高为100
def speed_up():
    global speed
    if speed < 100:
        speed = speed + 5
        return str(speed)
    else:
        return 'It is already the highest speed.'


@app.route('/api/car/speed_down', methods=['get'])  # 速度减少，最低为0
def speed_down():
    global speed
    if speed > 0:
        speed = speed - 5
        return str(speed)
    else:
        return 'It is already the lowest speed.'


@app.route('/api/car/run', methods=['get'])  # 前进
def run():
    global speed
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(speed)
    pwm_ENB.ChangeDutyCycle(speed)
    time.sleep(1)


@app.route('/api/car/back', methods=['get'])  # 后退
def back():
    global speed
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwm_ENA.ChangeDutyCycle(speed)
    pwm_ENB.ChangeDutyCycle(speed)
    time.sleep(1)


@app.route('/api/car/left', methods=['get'])  # 左转
def left():
    global speed
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(speed)
    pwm_ENB.ChangeDutyCycle(speed)
    time.sleep(1)


@app.route('/api/car/right', methods=['get'])  # 右转
def right():
    global speed
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(speed)
    pwm_ENB.ChangeDutyCycle(speed)
    time.sleep(1)


@app.route('/api/car/spin_left', methods=['get'])  # 原地左转
def spin_left():
    global speed
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(speed)
    pwm_ENB.ChangeDutyCycle(speed)
    time.sleep(3)


@app.route('/api/car/spin_right', methods=['get'])  # 原地右转
def spin_right():
    global speed
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwm_ENA.ChangeDutyCycle(speed)
    pwm_ENB.ChangeDutyCycle(speed)
    time.sleep(3)


@app.route('/api/car/stop', methods=['get'])  # 小车停止
def brake():
    global speed
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(speed)
    pwm_ENB.ChangeDutyCycle(speed)
    time.sleep(2)


@app.route('/api/act/findlight')  # 寻光行走
def findlight():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]  # host ip
    # motor_init()  # 初始化
    t1 = time.time()
    for i in range(1, 31):
        t2 = time.time()
        usetime = t2-t1
        if usetime < 30:                   # 设置最长30秒就停止
            # 遇到光线,寻光模块的指示灯灭,端口电平为HIGH
            # 未遇光线,寻光模块的指示灯亮,端口电平为LOW
            LdrSersorLeftValue = GPIO.input(LdrSensorLeft)
            LdrSersorRightValue = GPIO.input(LdrSensorRight)
            if LdrSersorLeftValue == True and LdrSersorRightValue == True:
                requests.get('http://' + ip + ':5000/api/car/run')
                # run()  # 两侧均有光时信号为HIGH，光敏电阻指示灯灭,小车前进
            elif LdrSersorLeftValue == True and LdrSersorRightValue == False:
                requests.get('http://' + ip + ':5000/api/car/spin_left')
                # spin_left()  # 左边探测到有光，有信号返回，向左转
                time.sleep(0.002)
            elif LdrSersorRightValue \
                    == True and LdrSersorLeftValue == False:
                requests.get('http://' + ip + ':5000/api/car/spin_right')
                # spin_right()  # 右边探测到有光，有信号返回，向右转
                time.sleep(0.002)
            elif LdrSersorRightValue == False and LdrSersorLeftValue == False:
                requests.get('http://' + ip + ':5000/api/car/stop')
                # brake()


# 延时2s
time.sleep(2)

if __name__ == '__main__':
    motor_init()  # 初始化
    app.run(
        host='0.0.0.0',  # url
        port='5000',  # 端口
        debug=True
    )
    pwm_ENA.stop()
    pwm_ENB.stop()
    GPIO.cleanup()
