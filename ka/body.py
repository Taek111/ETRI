import numpy as np
import math
from copy import deepcopy

def delete(body):
    body["bodyID"] = 0
    body["trackingState"] = 0
    body["leanX"] = 0.0
    body["leanY"] = 0.0

    # 3D location of the joint j
    for j in range(len(body["joints"])):
        body["joints"][j]["x"] = 0.0  # x grows to the sensor's left
        body["joints"][j]["y"] = 0.0  # y grows up (based on the sensor's tilt)
        body["joints"][j]["z"] = 0.0  # z grows out in the direction the sensor is facing
        body["joints"][j]["trackingState"] = 0

    # 2D location of the joint j in corresponding RGB frame
    for j in range(len(body["joints"])):
        body["joints"][j]["orientationX"] = 0.0
        body["joints"][j]["orientationY"] = 0.0
        body["joints"][j]["orientationZ"] = 0.0
        body["joints"][j]["orientationW"] = 0.0

    # 2D location of the joint j in corresponding depth frame
    for j in range(len(body["joints"])):
        body["joints"][j]["depthX"] = 0.0
        body["joints"][j]["depthY"] = 0.0


def interpolate(begin, end, out, step):
    out["bodyID"] = end["bodyID"]
    out["trackingState"] = end["trackingState"]
    out["leanX"] = end["leanX"]
    out["leanY"] = end["leanY"]

    # 3D location of the joint j
    for j in range(len(out["joints"])):
        out["joints"][j]["x"] = begin["joints"][j]["x"] + (end["joints"][j]["x"] - begin["joints"][j]["x"]) * step
        out["joints"][j]["y"] = begin["joints"][j]["y"] + (end["joints"][j]["y"] - begin["joints"][j]["y"]) * step
        out["joints"][j]["z"] = begin["joints"][j]["z"] + (end["joints"][j]["z"] - begin["joints"][j]["z"]) * step
        out["joints"][j]["trackingState"] = end["joints"][j]["trackingState"]

    # 2D location of the joint j in corresponding RGB frame
    for j in range(len(out["joints"])):
        out["joints"][j]["orientationX"] = begin["joints"][j]["orientationX"] + (end["joints"][j]["orientationX"] - begin["joints"][j]["orientationX"]) * step
        out["joints"][j]["orientationY"] = begin["joints"][j]["orientationY"] + (end["joints"][j]["orientationY"] - begin["joints"][j]["orientationY"]) * step
        out["joints"][j]["orientationZ"] = begin["joints"][j]["orientationZ"] + (end["joints"][j]["orientationZ"] - begin["joints"][j]["orientationZ"]) * step
        out["joints"][j]["orientationW"] = begin["joints"][j]["orientationW"] + (end["joints"][j]["orientationW"] - begin["joints"][j]["orientationW"]) * step

    # 2D location of the joint j in corresponding depth frame
    for j in range(len(out["joints"])):
        out["joints"][j]["depthX"] = begin["joints"][j]["depthX"] + (end["joints"][j]["depthX"] - begin["joints"][j]["depthX"]) * step
        out["joints"][j]["depthY"] = begin["joints"][j]["depthY"] + (end["joints"][j]["depthY"] - begin["joints"][j]["depthY"]) * step


def convert_to_nao(body):
    # joint information
    shoulderRight = vectorize(body[8])
    shoulderLeft = vectorize(body[4])
    elbowRight = vectorize(body[9])
    elbowLeft = vectorize(body[5])
    wristRight = vectorize(body[10])
    wristLeft = vectorize(body[6])

    spineBase = vectorize(body[0])
    spineShoulder = vectorize(body[20])
    head = vectorize(body[3])
    ankleRight = vectorize(body[18])
    ankleLeft = vectorize(body[14])

    ####### RIGHT ARM #######
    r_8_9_human = elbowRight - shoulderRight
    r_9_10_human = wristRight - elbowRight
    RShoulderPitch = math.atan2(-r_8_9_human[1], -r_8_9_human[2])

    r_8_9_rsp = rotate_x(r_8_9_human, -RShoulderPitch)
    r_9_10_rsp = rotate_x(r_9_10_human, -RShoulderPitch)
    RShoulderRoll = math.atan2(-r_8_9_rsp[0], -r_8_9_rsp[2])

    r_9_10_rsr = rotate_y(r_9_10_rsp, RShoulderRoll)
    new_y = np.cross(r_9_10_rsr, [0, 0, 1])
    RElbowYaw = math.atan2(new_y[0], new_y[1])

    r_9_10_rey = rotate_z(r_9_10_rsr, -RElbowYaw)
    RElbowRoll = math.atan2(-r_9_10_rey[0], -r_9_10_rey[2])

    ####### LEFT ARM #######
    r_4_5_human = elbowLeft - shoulderLeft
    r_5_6_human = wristLeft - elbowLeft
    LShoulderPitch = math.atan2(-r_4_5_human[1], -r_4_5_human[2])

    r_4_5_rsp = rotate_x(r_4_5_human, -LShoulderPitch)
    r_5_6_rsp = rotate_x(r_5_6_human, -LShoulderPitch)
    LShoulderRoll = math.atan2(-r_4_5_rsp[0], -r_4_5_rsp[2])

    r_5_6_rsr = rotate_y(r_5_6_rsp, LShoulderRoll)
    new_y = np.cross([0, 0, 1], r_5_6_rsr)
    LElbowYaw = math.atan2(new_y[0], new_y[1])

    r_5_6_rey = rotate_z(r_5_6_rsr, -LElbowYaw)
    LElbowRoll = math.atan2(-r_5_6_rey[0], -r_5_6_rey[2])

    ####### BODY #######
    r_0_20_human = spineShoulder - spineBase
    r_g_human = [0, 1, 0]
    LHipYawPitch = rotation_angle([r_0_20_human[2], r_0_20_human[1]], [r_g_human[2], r_g_human[1]])
    LHipYawPitch += math.radians(-14.5)

    ####### HEAD #######
    r_20_3_human = head - spineShoulder
    r_0_20_human = spineShoulder - spineBase
    HeadPitch = rotation_angle([r_0_20_human[2], r_0_20_human[1]], [r_20_3_human[2], r_20_3_human[1]])
    HeadPitch += math.radians(6.5)

    return [LHipYawPitch, HeadPitch,
             LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll,
             RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll]


def get_camera(body):
    r_16_kinect = vectorize(body[16])
    r_12_kinect = vectorize(body[12])
    r_20_kinect = vectorize(body[20])
    r_0_kinect = vectorize(body[0])

    # rotation matrix from kinect to human coordinates
    z = normalize(np.cross(r_16_kinect - r_12_kinect, r_16_kinect - r_20_kinect))
    cam_pos = r_0_kinect + z
    cam_dir = -z

    return cam_pos, cam_dir


def move_camera(body, cam_pos, cam_dir):
    # rotation factors (y <-> z axis 라고 생각하고 계산)
    dist = math.sqrt(cam_dir[0] ** 2 + cam_dir[1] ** 2 + cam_dir[2] ** 2)
    dist_y = math.sqrt(cam_dir[0] ** 2 + cam_dir[2] ** 2)
    cos_x = dist_y / dist
    sin_x = -cam_dir[1] / dist
    cos_y = cam_dir[2] / dist_y
    sin_y = cam_dir[0] / dist_y

    # for all the 25 joints within each skeleton
    for j in range(len(body)):
        joint = body[j]

        # 1. translation to the position of robot
        trans_x = joint['x'] - cam_pos[0]
        trans_y = joint['y'] - cam_pos[1]
        trans_z = joint['z'] - cam_pos[2]

        # 2. rotation about x-axis
        rot_x = trans_x
        rot_y = sin_x * trans_z + cos_x * trans_y
        rot_z = cos_x * trans_z - sin_x * trans_y

        # 3. rotation about y-axis
        joint['x'] = cos_y * rot_x - sin_y * rot_z
        joint['y'] = rot_y
        joint['z'] = sin_y * rot_x + cos_y * rot_z


def rotate_x(vector, angle):
    A = np.array([[1, 0, 0],
                  [0, math.cos(angle), math.sin(angle)],
                  [0, -math.sin(angle), math.cos(angle)]])
    return np.dot(A, vector)


def rotate_y(vector, angle):
    A = np.array([[math.cos(angle), 0, -math.sin(angle)],
                  [0, 1, 0],
                  [math.sin(angle), 0, math.cos(angle)]])
    return np.dot(A, vector)


def rotate_z(vector, angle):
    A = np.array([[math.cos(angle), math.sin(angle), 0],
                  [-math.sin(angle), math.cos(angle), 0],
                  [0, 0, 1]])
    return np.dot(A, vector)


def vectorize(joint):
    return np.array([joint['x'], joint['y'], joint['z']])


def normalize(vector):
    norm = norm_2(vector)
    if norm == 0:
        norm = np.finfo(vector.dtype).eps
    return vector / norm


def norm_2(vector):
    return np.linalg.norm(vector, axis=0, ord=2)


def angle_between(v1, v2):
    return math.acos(np.dot(v1, v2) / (norm_2(v1) * norm_2(v2)))


# rotation_angle from v1 to v2 (counterclockwise) in (-pi, pi]
def rotation_angle(v1, v2):
    angle_v1 = math.atan2(v1[1], v1[0])
    angle_v2 = math.atan2(v2[1], v2[0])
    angle_between = angle_v2 - angle_v1
    if math.fabs(angle_between) >= math.pi:
        angle_between -= math.copysign(2 * math.pi, angle_between)
    return angle_between