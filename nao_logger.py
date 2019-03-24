# -*- encoding: UTF-8 -*-
""" Record some sensors values and write them into a file.

"""

# MEMORY_VALUE_NAMES is the list of ALMemory values names you want to save.
ALMEMORY_KEY_NAMES = [
    "RShoulderRoll",
    "RShoulderPitch",
    "RElbowYaw",
    "RElbowRoll",
    "RWristYaw",
    "RHand",
    "LShoulderRoll",
    "LShoulderPitch",
    "LElbowYaw",
    "LElbowRoll",
    "LWristYaw",
    "LHand",
    "RHipPitch",
    "RHipRoll",
    "RKneePitch",
    "RAnklePitch",
    "RAnkleRoll",
    "LHipYawPitch",
    "LHipPitch",
    "LHipRoll",
    "LKneePitch",
    "LAnklePitch",
    "LAnkleRoll",
]

ROBOT_IP = "127.0.0.1"

import os
import sys
import time

from naoqi import ALProxy


def recordData(nao_ip):
    motion_proxy = ALProxy("ALMotion", nao_ip, 9559)

    data = list()

    current_sum = last_sum = sum(motion_proxy.getAngles(ALMEMORY_KEY_NAMES, True))

    print "Waiting for movement..."
    while abs(current_sum - last_sum) < 0.0001:
        time.sleep(0.04)
        current_sum = last_sum
        last_sum = sum(motion_proxy.getAngles(ALMEMORY_KEY_NAMES, True))

    print "Recording data ..."
    for i in range(1, 100):
        line = motion_proxy.getAngles(ALMEMORY_KEY_NAMES, True)
        data.append(line)
        time.sleep(0.04)
    return data


def takePhoto(nao_ip):
    try:
        photoCaptureProxy = ALProxy("ALPhotoCapture", nao_ip, 9559)
    except Exception, e:
        print "Error when creating ALPhotoCapture proxy:"
        print str(e)
        exit(1)
    photoCaptureProxy.setResolution(2)
    photoCaptureProxy.setPictureFormat("jpg")
    photoCaptureProxy.takePicture("/", "image")


def main():
    if len(sys.argv) < 2:
        nao_ip = ROBOT_IP
    else:
        nao_ip = sys.argv[1]

    # takePhoto(nao_ip)

    data = recordData(nao_ip)

    output = os.path.abspath("record.csv")

    with open(output, "w") as fp:
        for line in data:
            fp.write(";".join(str(x) for x in line))
            fp.write("\n")

    print "Results written to", output


if __name__ == "__main__":
    main()
