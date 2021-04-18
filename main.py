from time import sleep
from serial import Serial
from pynvml import *
import json


def nvidia_max_temp():
    nvmlInit()

    device_count = nvmlDeviceGetCount()
    nvidia_temps = []

    for i in range(device_count):
        handle = nvmlDeviceGetHandleByIndex(i)
        nvidia_temps.append(nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU))

    nvmlShutdown()

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
            arduino.write(0)
        elif temp_max > configs["MAX_TEMP"]:
            arduino.write(100)
        else:
            m = (configs["MAX_FAN"] - configs["MIN_FAN"]) / (configs["MAX_TEMP"] - configs["MIN_TEMP"])
            b = configs["MIN_FAN"] - (m * configs["MIN_TEMP"])
            fan_speed = (m * temp_max) + b

            arduino.write(int(fan_speed))

        print("new value", temp_max, fan_speed)
        arduino.close()
        sleep(15)
