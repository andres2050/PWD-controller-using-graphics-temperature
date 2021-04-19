from time import sleep
from serial import Serial
import nvsmi
import json
import struct


def nvidia_max_temp():
    nvidia_temps = []

    for gpu in nvsmi.get_gpus():
        nvidia_temps.append(gpu.temperature)

    return max(nvidia_temps)


def amd_max_temp():
    return 10


if __name__ == '__main__':
    while True:
        with open('config.json', 'r') as f:
            configs = json.load(f)

        arduino = Serial(configs["ARDUINO_PORT"], configs["ARDUINO_FREQ"])

        temp_max = max([nvidia_max_temp(), amd_max_temp()])
        if temp_max < configs["MIN_TEMP"]:
            arduino.write(struct.pack('>B', 0))
            print("new value", temp_max, 0)
        elif temp_max > configs["MAX_TEMP"]:
            arduino.write(struct.pack('>B', 100))
            print("new value", temp_max, 100)
        else:
            m = (configs["MAX_FAN"] - configs["MIN_FAN"]) / (configs["MAX_TEMP"] - configs["MIN_TEMP"])
            b = configs["MIN_FAN"] - (m * configs["MIN_TEMP"])
            fan_speed = (m * temp_max) + b

            arduino.write(struct.pack('>B', int(fan_speed)))
            print("new value", temp_max, fan_speed)

        print(arduino.readline())

        arduino.close()
        sleep(15)
