import body
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as gridspec
import AiR
import AiR_2017
from mpl_toolkits.mplot3d import Axes3D
import math
from copy import deepcopy
import numpy as np
import transform_2017
import os
import struct

n_humans = 1
joints_of_interest = [0, 3, 4, 5, 6, 8, 9, 10, 20]
body_id = list()
BODY_COUNT = 6
JOINT_COUNT = 25

def main():
    src = "C:/Users/wrko/Desktop/C001/new/"
    skeleton_file = src + "C001P001A005S003.joints"

    # draw skeletons
    # fig = plt.figure(figsize=(16,8))
    # ax = [fig.add_subplot(121, projection='3d'), fig.add_subplot(122, projection='3d')]
    fig = plt.figure(figsize=(16, 5))  # width, height
    gridspec.GridSpec(1, 3)
    ax=[plt.subplot2grid((1, 3), (0, 0), colspan=1, rowspan=1, projection='3d'),
        plt.subplot2grid((1, 3), (0, 1), colspan=1, rowspan=1, projection='3d'),
        plt.subplot2grid((1, 3), (0, 2), colspan=1, rowspan=1, projection='3d')]
    for axis in ax:
        set_axis_3d(axis)

    # get body information
    body_info = [AiR.read_body(skeleton_file),
                 AiR.read_body(skeleton_file),
                 AiR.read_body(skeleton_file)
                 ]
    #cam_pos, cam_dir = body.get_camera(body_info[0][1]["joints"])

    # show results

    anim = animation.FuncAnimation(fig, animate_3d, interval=50, blit=True,
                                   fargs=(body_info, ax),
                                   frames=len(body_info[0]), repeat=True)

    writer = animation.writers['ffmpeg'](fps=10)

    #anim.save('changed.mp4', writer=writer, dpi=250)

    plt.show()
    plt.close('all')
    for f in range(len(body_info[1])):
        for j in range(JOINT_COUNT):
            print(f, j, body_info[1][f][0]["joints"][j]["z"])


def set_axis_3d(ax):
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    ax.set_xlim3d(-1.5, 1.5)
    ax.set_ylim3d(-1, 1)
    ax.set_zlim3d(0, 3)

    ax.view_init(-45, 45)


def animate_3d(f, body_info, ax):
    # initialize
    for b in range(n_humans):
        ax[b].clear()
        set_axis_3d(ax[b])

    # settings
    connecting_joint = [1, 0, 20, 2, 20, 4, 5, 6, 20, 8, 9, 10, 0, 12, 13, 14, 0, 16, 17, 18, 1, 7, 7, 11, 11]
    colors = ['b', 'r']\


    # for all the detected skeletons in the current frame
    lines = []
    texts = []
    for b in range(3):
        # for all the 25 joints within each skeleton
        for j in range(JOINT_COUNT):
            try:
                if j == 0:
                    human = body_info[b][f][0]["joints"]
                    r_16_kinect = body.vectorize(human[16])
                    r_12_kinect = body.vectorize(human[12])
                    r_20_kinect = body.vectorize(human[20])
                    r_0_kinect = body.vectorize(human[0])

                    # transformation matrix
                    z = body.normalize(np.cross(r_16_kinect - r_20_kinect, r_16_kinect - r_12_kinect))
                    x = body.normalize(r_16_kinect - r_12_kinect)
                    y = np.cross(z, x)
                    A = [x, y, z]

                    # lobj = ax[b].plot([r_0_kinect[0], r_0_kinect[0] + z[0]],
                    #                   [r_0_kinect[1], r_0_kinect[1] + z[1]],
                    #                   [r_0_kinect[2], r_0_kinect[2] + z[2]],
                    #                   color='g')[0]
                    # lines.append(lobj)

                # elif j in [0, 1, 2, 8, 9, 10, 11, 16, 17, 18, 19, 20]:
                else:
                    k = connecting_joint[j]
                    joint1 = body_info[b][f][0]["joints"][j]
                    joint2 = body_info[b][f][0]["joints"][k]

                    # transferred to the NAO robot
                    # new_joint1 = np.dot(A, vectorize(joint1) - vectorize(human[0]))
                    # new_joint2 = np.dot(A, vectorize(joint2) - vectorize(human[0]))
                    new_joint1 = body.vectorize(joint1)
                    new_joint2 = body.vectorize(joint2)

                    lobj = ax[b].plot([new_joint1[0], new_joint2[0]],
                                      [new_joint1[1], new_joint2[1]],
                                      [new_joint1[2], new_joint2[2]],
                                      color=colors[0])[0]
                    lines.append(lobj)
            except:
                pass

        # for the current frame number
        texts.append(ax[b].text(0, 0, 0, '{0}/{1}'.format(f, len(body_info[0]))))
    return tuple(lines) + tuple(texts)


if __name__ == "__main__":
    main()