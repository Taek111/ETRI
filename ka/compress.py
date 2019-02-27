import sys
sys.path.insert(0, 'C:/Users/wrko/Desktop/project-2018-HumanCare/act2act/pre_processing/utils/')
import AiR_2017
import arrange_2017
import os
import nao
import transform_2017
from PIL import Image
import numpy as np
import struct
import cv2
#
# path = "F:/2017/test/png/"
# file= "C003P044A003S004"
# new_bin = "F:/2017/test/new_bin.bin"
#
# with open(new_bin, 'wb') as fp:
#
#     for i in range(len(os.listdir(path))):
#         file_name = path + file + "_frame_" + str(i) + ".png"
#         img = Image.open(file_name)
#         data = np.asarray(img)
#         for r in range(len(data)):
#             for c in range(len(data[0])):
#                 fp.write(struct.pack('H', data[r][c]))
#         print(i)
#
# print("completed")
#####압축하기
# new_bin = "F:/2017/test/new_bin.bin"
# file = "F:/2017/test/png/C003P044A003S004_frame_0.png"
# new_file = "F:/2017/test/png/new.png"
# with open(new_bin, 'rb') as dat:
#
#     data = dat.read(512*424*2)
#     depth_data = struct.unpack('H' * 512 * 424, data)
#     img = np.reshape(depth_data, (424, 512))
#
#     cv2.imwrite(new_file, img,  [cv2.IMWRITE_PNG_COMPRESSION, 9])

DEPTH_FRAME_SIZE = 512 * 424 * 2
BODY_FRAME_SIZE = 512 * 424 * 1

root = "F:/2017/data/"
new_root = "C:/Users/wrko/Desktop/compressed_file/bin/2017/"

cameras = ["C%03d" %c for c in range(1, 4)]
peoples = ["P%03d" %p for p in range(51, 101)]
actions = ["A%03d" %a for a in range(1, 11)]
scenes = ["S%03d" %s for s in range(1, 6)]
error_file = list()
cnt = 0

for camera in cameras:
    for people in peoples:
        for action in actions:
            for scene in scenes:


                path = root + camera + "/"
                new_path = new_root + camera + "/"
                file_name = camera + people + action + scene + ".bin"

                if not os.path.isfile(path+file_name):
                    error_file.append(file_name)
                    continue
                #
                # try:
                #     file_folder = new_path + file_name.replace(".bin", "") + "/"
                #     if not os.path.isdir(file_folder):
                #         os.mkdir(file_folder)
                #     frame_num = os.path.getsize(path + file_name) / (DEPTH_FRAME_SIZE)
                #     with open(path + file_name, 'rb') as depth_file:
                #         for f in range(frame_num):
                #             depth = depth_file.read(DEPTH_FRAME_SIZE)
                #             depth = struct.unpack('H' * (512 * 424), depth)
                #             depth = np.reshape(depth, (424, 512))
                #             new_file = file_folder + "frame_" + str(f).zfill(3) + ".png"
                #             cv2.imwrite(new_file, depth, [cv2.IMWRITE_PNG_COMPRESSION, 9])
                #
                # except:
                #     error_file.append(file_name)
                #     print("변환오류")
                #
                try:
                    file_folder = new_path + file_name.replace(".bin", "") + "/"
                    if not os.path.isdir(file_folder):
                        os.mkdir(file_folder)
                    frame_num = int(os.path.getsize(path + file_name) / (DEPTH_FRAME_SIZE))
                    with open(path + file_name, 'rb') as depth_file:
                        for f in range(frame_num):
                            depth = depth_file.read(DEPTH_FRAME_SIZE)
                            depth = struct.unpack('H' * (512 * 424), depth)
                            depth = np.reshape(depth, (424, 512))
                            new_file = file_folder + "frame_" + str(f).zfill(3) + ".png"
                            cv2.imwrite(new_file, depth, [cv2.IMWRITE_PNG_COMPRESSION, 9])
                except:
                    error_file.append(file_name)
                    print("변환오류(%s)"%file_name)

                cnt += 1
                print('({} / {})'.format(cnt, 7500), end=' ')
                print("에러파일 개수:%d" % len(error_file))


print(error_file)


