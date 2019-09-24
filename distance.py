import RPi.GPIO as GPIO
import time


class Getdistance():

    # 超声波引脚定义
    EchoPin = 0
    TrigPin = 1

    # 设置GPIO口为BCM编码方式
    GPIO.setmode(GPIO.BCM)

    # 忽略警告信息
    GPIO.setwarnings(False)

    # 电机引脚初始化为输出模式
    # 按键引脚初始化为输入模式
    # 超声波引脚初始化
    def init(self):
        GPIO.setup(self.EchoPin, GPIO.IN)
        GPIO.setup(self.TrigPin, GPIO.OUT)
        # 设置pwm引脚和频率为2000hz

    # 超声波函数
    def Distance_test(self):
        GPIO.output(self.TrigPin, GPIO.HIGH)
        time.sleep(0.000015)
        GPIO.output(self.TrigPin, GPIO.LOW)
        while not GPIO.input(self.EchoPin):
            pass
        t1 = time.time()
        while GPIO.input(self.EchoPin):
            pass
        t2 = time.time()
        print("distance is %d " % (((t2 - t1) * 340 / 2) * 100))
        time.sleep(0.01)
        return ((t2 - t1) * 340 / 2) * 100

    # try/except语句用来检测try语句块中的错误，
    # 从而让except语句捕获异常信息并处理。
    def get_thedistance(self):
        try:
            self.init()
            while True:
                distance = self.Distance_test()
                time.sleep(2)
                # 这里写返回distance的代码
                return distance
        except KeyboardInterrupt:
            pass
    GPIO.cleanup()
