# -*- encoding: UTF-8 -*-
""" Record some sensors values and write them into a file.

"""

ROBOT_IP = "127.0.0.1"

import math
import os
import cv2
import numpy as np

from lxml import etree
from naoqi import ALProxy

if __name__ == "__main__":
    body_names = ['RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll', 'RWristYaw',
                  'LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 'LElbowRoll', 'LWristYaw']

    _motionProxy = None
    try:
        _motionProxy = ALProxy('ALMotion', '127.0.0.1', 9559)
    except Exception, e:
        print 'Could not create proxy to ALMotion'
        print 'Error was: ', e

    # joint_limits = []
    # for n in body_names:
    #     joint_limits.append(_motionProxy.getLimits(n)[0])

    joint_limits = [[-119.500006171, 119.500006171], [-75.9999998382, 18.0000005009], [-119.500006171, 119.500006171],
                    [1.99999998451, 88.4999973401], [-104.500002339, 104.500002339], [-119.500006171, 119.500006171],
                    [-18.0000005009, 75.9999998382], [-119.500006171, 119.500006171], [-88.4999973401, -1.99999998451],
                    [-104.500002339, 104.500002339]]

    src_img = cv2.imread('P2.jpg')
    dst_img = cv2.cvtColor(src_img, cv2.COLOR_RGB2HSV)

    lower_color = np.array([88, 70, 253])
    upper_color = np.array([92, 190, 255])

    mask = cv2.inRange(dst_img, lower_color, upper_color)
    imask = mask > 0

    filtered = np.zeros_like(src_img, np.uint8)
    filtered[imask] = src_img[imask]

    imgray = cv2.cvtColor(filtered, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 1, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    c = max(contours, key=cv2.contourArea)

    x, y, w, h = cv2.boundingRect(c)
    thresh = thresh[y:y + h, x:x + w]
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    contours.remove(max(contours, key=cv2.contourArea))
    c = max(contours, key=cv2.contourArea)

    print cv2.contourArea(c)
    M = cv2.moments(c)
    height, width, channels = src_img.shape
    hole_x = (float(M['m10'] / M['m00']) + x) / width
    hole_y = (float(M['m01'] / M['m00']) + y) / height

    output = os.path.abspath("target.txt")

    namespace = "http://www.aldebaran-robotics.com/schema/choregraphe/project.xsd";

    tree = etree.parse('behavior.xar')
    root = tree.getroot()

    prev_keyframe = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    keyframe_counter = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, ]
    prev_value = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    cur_rate = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for j in range(0, len(body_names)):
        prev_key = root.find(
            ".//{" + namespace + "}ActuatorCurve[@actuator='" +
            body_names[j] + "']")[0]

        next_key = root.find(
            ".//{" + namespace + "}ActuatorCurve[@actuator='" +
            body_names[j] + "']")[1]

        prev_value[j] = float(prev_key.attrib['value'])
        cur_rate[j] = (float(next_key.attrib['value']) - prev_value[j]) / (
                float(next_key.attrib['frame']) - prev_keyframe[j])

    with open(output, "w") as fp:
        total_frames = range(int(prev_key.attrib["frame"]), int(
            root.find(".//{" + namespace + "}Timeline[@size]").attrib[
                "size"]) + 1)

        for i in total_frames:
            print i
            for j in range(0, len(body_names)):
                next_key = root.find(
                    ".//{" + namespace + "}ActuatorCurve[@actuator='" +
                    body_names[j] + "']")[keyframe_counter[j] + 1]

                if i == int(next_key.attrib['frame']) and i != total_frames[-1]:
                    keyframe_counter[j] += 1
                    cur_rate[j] = (float(root.find(
                        ".//{" + namespace + "}ActuatorCurve[@actuator='" +
                        body_names[j] + "']")[keyframe_counter[j] + 1].attrib["value"]) - float(
                        next_key.attrib['value'])) / (
                                          int(root.find(
                                              ".//{" + namespace + "}ActuatorCurve[@actuator='" +
                                              body_names[j] + "']")[keyframe_counter[j] + 1].attrib["frame"]) - int(
                                      next_key.attrib['frame']))
                    prev_value[j] = float(next_key.attrib['value'])
                    prev_keyframe[j] = int(next_key.attrib['frame'])

                tmp_angle = math.radians(prev_value[j] + cur_rate[j] * (i - prev_keyframe[j]))

                fp.write(str((tmp_angle - math.radians(joint_limits[j][0])) / (
                            math.radians(joint_limits[j][1]) - math.radians(joint_limits[j][0])) * 1.6 - 0.8))
                # fp.write(str(tmp_angle))

                if (j != len(body_names) - 1):
                    fp.write('\t')

            if (i != total_frames[-1]):
                fp.write('\t' + str(hole_x) + '\t' + str(hole_y) + '\n')

        fp.write('\t' + str(hole_x) + '\t' + str(hole_y))
