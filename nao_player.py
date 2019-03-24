# -*- encoding: UTF-8 -*-
import csv
import sys
import time

from naoqi import ALProxy

ALMEMORY_KEY_NAMES = [
    'RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll',
    'LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 'LElbowRoll'
]

ROBOT_IP = "127.0.0.1"


def play_data(nao_ip):
    print("Recording data ...")
    motionProxy = ALProxy("ALMotion", nao_ip, 9559)

    with open('target000000.txt', 'rb') as csvfile:
        data = csv.reader(csvfile, delimiter=' ')
        i = 0
        for row in data:
            i = i + 1
            fractionMaxSpeed = 1
            motionProxy.setAngles(ALMEMORY_KEY_NAMES, map(float, row), fractionMaxSpeed)
            time.sleep(0.01)
            print('Sample:', i)

    return data


def main():
    if len(sys.argv) < 2:
        nao_ip = ROBOT_IP
    else:
        nao_ip = sys.argv[1]

    play_data(nao_ip)

    print("Finished playing data. Exiting.")


if __name__ == "__main__":
    main()
