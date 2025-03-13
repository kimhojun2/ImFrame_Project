import smbus2 as smbus
import threading
import time
import subprocess

I2C_CH = 0
BH1750_DEV_ADDR = 0x23

CONT_H_RES_MODE     = 0x10 # 연속 고해상도 모드

'''
 조도값 읽는 함수
'''
def readIlluminance():
    i2c = smbus.SMBus(I2C_CH)
    luxBytes = i2c.read_i2c_block_data(BH1750_DEV_ADDR, CONT_H_RES_MODE, 2)
    lux = int.from_bytes(luxBytes, byteorder='big')
    i2c.close()
    return lux

'''
 디스플레이 밝기 설정 함수
'''
def set_display_brightness(brightness):
    try:
        subprocess.run(['xrandr', '--output', 'HDMI-0', '--brightness', str(brightness)])
        print(f"디스플레이 밝기가 {brightness}로 설정되었습니다.")
    except Exception as e:
        print("디스플레이 밝기 설정 중 오류 발생:", e)

'''
 조도값에 따라 디스플레이 밝기 조절
'''
def readIlluminanceAndAdjustBrightness():
    while True:
        lux = readIlluminance()
        print(f'{lux} lux')
        
        if lux < 100:
            set_display_brightness(0.1)  # 어두운 환경
        elif lux < 600:
            set_display_brightness(0.5)  # 중간 밝기
        else:
            set_display_brightness(1.0)  # 밝은 환경

        time.sleep(1)  # 0.1초 간격으로 반복

print('조도 센서를 통한 디스플레이 밝기 조절 시작')
print('Press Enter key to exit')

# 쓰레드 생성 및 시작
thd = threading.Thread(target=readIlluminanceAndAdjustBrightness)
thd.daemon = True
thd.start()

# 프로그램 종료 대기
input()
print('done')
