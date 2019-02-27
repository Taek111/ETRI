import struct
import os

BODY_COUNT = 6
JOINT_COUNT = 25
PATH = "D:/HRI DB/AiR Project (2nd)/"
DATA_NAME = 'AiR'


def get_files(actions, cameras, people, scenes):
    files = []
    for action in actions:
        for camera in cameras:
            for person in people:
                for scene in scenes:
                    file_name = PATH + camera + person + action + scene + ".joints"
                    files.append(file_name)
    return files


def gen_body_info(files):
    for file in files:
        body_info = read_body(file)
        yield file, body_info


def read_body(path):
    with open(path, "rb") as fp:

        frame_count = int(os.path.getsize(path) / 6152)  # no of the recorded frames
        body_info = list()
        for f in range(frame_count):
            time = fp.read(8)  # time span

            bodies = list()
            for b in range(BODY_COUNT):

                body = dict()
                body["bodyID"] = struct.unpack('q', fp.read(8))[0]
                body["trackingState"] = struct.unpack('q', fp.read(8))[0]  # not sure
                body["leanX"] = struct.unpack('f', fp.read(4))[0]
                body["leanY"] = struct.unpack('f', fp.read(4))[0]
                body["time"] = time

                joints = list()
                # 3D location of the joint j
                for j in range(JOINT_COUNT):
                    joint = dict()
                    joint["x"] = struct.unpack('f', fp.read(4))[0]  # x grows to the sensor's left
                    joint["y"] = struct.unpack('f', fp.read(4))[0]  # y grows up (based on the sensor's tilt)
                    joint["z"] = struct.unpack('f', fp.read(4))[0]  # z grows out in the direction the sensor is facing
                    joint["trackingState"] = struct.unpack('i', fp.read(4))[0]
                    joints.append(joint)

                # 2D location of the joint j in corresponding RGB frame
                for j in range(JOINT_COUNT):
                    joints[j]["orientationX"] = struct.unpack('f', fp.read(4))[0]
                    joints[j]["orientationY"] = struct.unpack('f', fp.read(4))[0]
                    joints[j]["orientationZ"] = struct.unpack('f', fp.read(4))[0]
                    joints[j]["orientationW"] = struct.unpack('f', fp.read(4))[0]

                # 2D location of the joint j in corresponding depth frame
                for j in range(JOINT_COUNT):
                    joints[j]["depthX"] = struct.unpack('f', fp.read(4))[0]
                    joints[j]["depthY"] = struct.unpack('f', fp.read(4))[0]

                body["joints"] = joints
                bodies.append(body)

            body_info.append(bodies)

    return body_info


def write_body(path, body_info):
    with open(path, "wb+") as fp:

        for f in range(len(body_info)):
            fp.write(body_info[f][0]["time"])

            for b in range(BODY_COUNT):

                fp.write(struct.pack('q', body_info[f][b]["bodyID"]))
                fp.write(struct.pack('q', body_info[f][b]["trackingState"]))
                fp.write(struct.pack('f', body_info[f][b]["leanX"]))
                fp.write(struct.pack('f', body_info[f][b]["leanY"]))

                # 3D location of the joint j
                for j in range(JOINT_COUNT):
                    fp.write(struct.pack('f', body_info[f][b]["joints"][j]["x"]))
                    fp.write(struct.pack('f', body_info[f][b]["joints"][j]["y"]))
                    fp.write(struct.pack('f', body_info[f][b]["joints"][j]["z"]))
                    fp.write(struct.pack('i', body_info[f][b]["joints"][j]["trackingState"]))

                # 2D location of the joint j in corresponding RGB frame
                for j in range(JOINT_COUNT):
                    fp.write(struct.pack('f', body_info[f][b]["joints"][j]["orientationX"]))
                    fp.write(struct.pack('f', body_info[f][b]["joints"][j]["orientationY"]))
                    fp.write(struct.pack('f', body_info[f][b]["joints"][j]["orientationZ"]))
                    fp.write(struct.pack('f', body_info[f][b]["joints"][j]["orientationW"]))

                # 2D location of the joint j in corresponding depth frame
                for j in range(JOINT_COUNT):
                    fp.write(struct.pack('f', body_info[f][b]["joints"][j]["depthX"]))
                    fp.write(struct.pack('f', body_info[f][b]["joints"][j]["depthY"]))

