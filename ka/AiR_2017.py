import struct
import os
import numpy as np

JOINT_COUNT = 25
BODY_COUNT = 6
px = 255
py = 211
hfov = 70 * np.pi / 180
vfov = 60 * np.pi / 180
fx = px / np.tan(hfov*0.5)
fy = py / np.tan(vfov*0.5)

def read_body(file):
    body_info = list()
    with open(file, 'rb') as fp:
        frame_count = int(os.path.getsize(file) / (22 * JOINT_COUNT * BODY_COUNT))
        for f in range(frame_count):
            bodies = list()
            for b in range(BODY_COUNT):
                body = dict()

                joints = list()
                for j in range(JOINT_COUNT):
                    joint = dict()
                    joint["depthX"] = struct.unpack('i', fp.read(4))[0]
                    joint["depthY"] = struct.unpack("i", fp.read(4))[0]
                    joint["unknown_z"] = struct.unpack("H", fp.read(2))[0]
                    joint["x"] = struct.unpack("f", fp.read(4))[0]
                    joint["y"] = struct.unpack("f", fp.read(4))[0]
                    joint["z"] = struct.unpack("f", fp.read(4))[0]
                    joints.append(joint)
                body["joints"] = joints
                bodies.append(body)
            body_info.append(bodies)
    return body_info

def write_body(path, body_info):
    with open(path, "wb+") as fp:

        for f in range(len(body_info)):
            for b in range(BODY_COUNT):
                for j in range(JOINT_COUNT):
                    fp.write(struct.pack('i', body_info[f][b]["joints"][j]["depthX"]))
                    fp.write(struct.pack('i', body_info[f][b]["joints"][j]["depthY"]))
                    fp.write(struct.pack('H', body_info[f][b]["joints"][j]["unknown_z"]))
                    fp.write(struct.pack('f', body_info[f][b]["joints"][j]["x"]))
                    fp.write(struct.pack('f', body_info[f][b]["joints"][j]["y"]))
                    fp.write(struct.pack('f', body_info[f][b]["joints"][j]["z"]))


def read_bodyXY(file):
    body_info = list()
    with open(file, 'rb') as fp:
        frame_count = int(os.path.getsize(file) / (10 * JOINT_COUNT * BODY_COUNT))
        for f in range(frame_count):
            bodies = list()
            for b in range(BODY_COUNT):
                body = dict()

                joints = list()
                for j in range(JOINT_COUNT):
                    joint = dict()
                    joint["depthX"] = struct.unpack('i', fp.read(4))[0]
                    joint["depthY"] = struct.unpack("i", fp.read(4))[0]
                    joint["unknown_z"] = struct.unpack("H", fp.read(2))[0]
                    joints.append(joint)
                body["joints"] = joints
                bodies.append(body)
            body_info.append(bodies)
    return body_info

def write_bodyXY(path, body_info):
    with open(path, "wb+") as fp:

        for f in range(len(body_info)):
            for b in range(BODY_COUNT):
                for j in range(JOINT_COUNT):
                    fp.write(struct.pack('i', body_info[f][b]["joints"][j]["depthX"]))
                    fp.write(struct.pack('i', body_info[f][b]["joints"][j]["depthY"]))
                    fp.write(struct.pack('H', body_info[f][b]["joints"][j]["unknown_z"]))


def make_bodyXYZ(file):
    body_info = list()
    with open(file, 'rb') as fp:
        frame_count = int(os.path.getsize(file) / (10 * JOINT_COUNT * BODY_COUNT))
        for f in range(frame_count):
            bodies = list()
            for b in range(BODY_COUNT):
                body = dict()

                joints = list()
                for j in range(JOINT_COUNT):
                    joint = dict()
                    joint["depthX"] = struct.unpack('i', fp.read(4))[0]
                    joint["depthY"] = struct.unpack("i", fp.read(4))[0]
                    joint["unknown_z"] = struct.unpack("H", fp.read(2))[0]
                    joint["x"] = 0
                    joint["y"] = 0
                    joint["z"] = 0
                    joints.append(joint)
                body["joints"] = joints
                bodies.append(body)
            body_info.append(bodies)
    depth_file = file.replace(file.split(".")[-1], "bin")
    with open(depth_file, 'rb') as dat:
        for f in range(len(body_info)):
            data = dat.read(512*424*2)
            depth_data = struct.unpack('H'*512*424, data)
            depth_data = np.reshape(depth_data, (424,512))
            for b in range(BODY_COUNT):
                for j in range(JOINT_COUNT):
                    if body_info[f][b]["joints"][j]["depthX"]:
                        depth = depth_data[body_info[f][b]["joints"][j]["depthY"]]\
                                          [body_info[f][b]["joints"][j]["depthX"]] / 1000
                        body_info[f][b]["joints"][j]["x"] = (body_info[f][b]["joints"][j]["depthX"] - px)\
                                                            * (depth) / fx
                        body_info[f][b]["joints"][j]["y"] = (py - body_info[f][b]["joints"][j]["depthY"])\
                                                            * (depth) / fy
                        body_info[f][b]["joints"][j]["z"] = depth

    return body_info

def remakeXY_from_Z(body_info):
    for f in range(len(body_info)):
        for b in range(BODY_COUNT):
            for j in range(JOINT_COUNT):
                if not body_info[f][b]["joints"][j]["z"]:
                    continue
                depth = body_info[f][b]["joints"][j]["z"]
                body_info[f][b]["joints"][j]["x"] = (body_info[f][b]["joints"][j]["depthX"] - px)\
                                                    * depth / fx
                body_info[f][b]["joints"][j]["y"] = (py - body_info[f][b]["joints"][j]["depthY"]) \
                                                    * depth / fy

    return body_info



