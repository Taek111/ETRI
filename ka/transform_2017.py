import AiR_2017
import os
import struct
import numpy as np
from constants import connecting_joint

BODY_COUNT = 6
JOINT_COUNT = 25
joints_of_interest = [0, 3, 4, 5, 6, 8, 9, 10, 20]
n_humans = 2
depth_frame_size = 512 * 424 * 2

def main():
    src = "F:/2017/C002/"
    skeleton_file = src + "C002P051A004S003.dat"\

def read_depth(depth_file, frame_num):
    depth_file.seek(depth_frame_size*frame_num, 0)
    depth_data = depth_file.read(depth_frame_size)

    depth_info = struct.unpack('H'*int(depth_frame_size/2), depth_data)
    depth_info = [i/1000 for i in depth_info]
    depth_info = np.reshape(depth_info, (424, 512))
    return depth_info






def transform_body_info(skeleton_file):
    body_info = AiR_2017.read_body(skeleton_file)
    depth_file = open(skeleton_file.replace("dat", "bin"), 'rb')


    for f in range(1, len(body_info)):
        for j in range(JOINT_COUNT):
            if isError(body_info, f, j) and not body_info[f-1][0]["joints"][j]["z"] == 0:
                #print('{}/424, {}/512'.format(body_info[f][0]["joints"][j]["depthY"], body_info[f][0]["joints"][j]["depthX"]))
                depth_info = read_depth(depth_file, f)
                square = list()



                for c in range(11):
                    for r in range(11):
                        if not 424 > body_info[f][0]["joints"][j]["depthY"] - 5 + c >= 0 or \
                         not 512 > body_info[f][0]["joints"][j]["depthX"] - 5 + r >= 0:
                            square.append(0)
                        else:
                            square.append(depth_info[body_info[f][0]["joints"][j]["depthY"] - 5 + c]\
                                                   [body_info[f][0]["joints"][j]["depthX"] - 5 + r])
                # body_info[f][body_id[0]]["joints"][j]["z"] = min([x for x in square if x != 0]) / 1000
                difference_matrix = [abs(body_info[f-1][0]["joints"][j]["z"]-x) for x in square]
                body_info[f][0]["joints"][j]["z"] = square[difference_matrix.index(min(difference_matrix))]
                if isError(body_info, f, j):
                    body_info[f][0]["joints"][j]["z"] = body_info[f-1][0]["joints"][connecting_joint[j]]["z"]
    body_info = AiR_2017.remakeXY_from_Z(body_info)
    return body_info


def isError(body_info, frame, joint):
    if abs(body_info[frame][0]["joints"][joint]["z"] - body_info[frame-1][0]["joints"][joint]["z"]) > 0.3:
        return True
    else:
        return False

def transform_body_info_2(skeleton_file):
    body_info = AiR_2017.read_body(skeleton_file)
    depth_file = open(skeleton_file.replace("dat", "bin"), 'rb')


    for f in range(1, len(body_info)):
        for j in range(JOINT_COUNT):
            if isError(body_info, f, j) and not body_info[f-1][0]["joints"][j]["z"] == 0:

                depth_info = read_depth(depth_file, f)
                square = list()
                for c in range(11):
                    for r in range(11):

                        square.append(depth_info[body_info[f][0]["joints"][j]["depthY"] - 5 + c]\
                                                   [body_info[f][0]["joints"][j]["depthX"] - 5 + r])
                # body_info[f][body_id[0]]["joints"][j]["z"] = min([x for x in square if x != 0]) / 1000
                difference_matrix = [abs(body_info[f-1][0]["joints"][j]["z"]-x) for x in square]
                body_info[f][0]["joints"][j]["z"] = square[difference_matrix.index(min(difference_matrix))]

    body_info = AiR_2017.remakeXY_from_Z(body_info)
    return body_info

if __name__ == "__main__":
    main()