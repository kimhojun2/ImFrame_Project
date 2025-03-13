# -*- coding: utf-8 -*-
import Jetson.GPIO as GPIO
import time

SERVO_PIN = 33

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(7.5)  # 중앙값(0도)에 해당하는 듀티 사이클 시작

try:
    while True:
        user_input = input("각도(-180 ~ 180) : ")
        
        if user_input.lower() == 'q':
            break
        
        angle = float(user_input)
        if -180 <= angle <= 180:
            # -180도는 듀티 사이클 2.5, 0도는 7.5, 180도는 12.5로 설정
            DC = (angle + 180) * (10.0 / 360.0) + 2.5
            pwm.ChangeDutyCycle(DC)
        else:
            print("Please enter an angle between -180 and 180.")
        
except KeyboardInterrupt:
    pass

pwm.stop()
GPIO.cleanup()
