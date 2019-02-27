import os
import numpy as np
import struct
import cv2
from PIL import Image

DEPTH_FRAME_SIZE = 512 * 424 * 2
BODY_FRAME_SIZE = 512 * 424 * 1


def main():
    # depth영상(bin 파일)을 png 파일로 만들기
    # bin_file = "C:/Users/wrko/Desktop/C001/C001P001A005S001.bin"
    # depth_path = bin_file.replace(".bin", "_depth/")
    # convert_bin2png(bin_file, depth_path)
    #
    # body id 정보(body 파일)를 png 파일로 만들기
    # body_file = "C:/Users/wrko/Desktop/C001/C001P001A005S001.body"
    # body_path = body_file.replace(".body", "_body/")
    # convert_body2png(body_file, body_path)
    #
    # depth영상에 대한 png파일을 다시 bin 파일로 만들기
    # new_bin = "C:/Users/wrko/Desktop/C001/new_bin.bin"
    # convert_png2bin(depth_path, new_bin)
    #
    # body id 정보에 대한 png파일을 다시 body 파일로 만들기
    # new_body = "C:/Users/wrko/Desktop/C001/new_body.body"
    # convert_png2body(body_path, new_body)
    pass

def convert_bin2png(bin_file, png_path):

    frame_num = int(os.path.getsize(bin_file)/DEPTH_FRAME_SIZE)
    if not os.path.isdir(png_path):
        os.makedirs(png_path)

    with open(bin_file, 'rb') as depth_file:
        for f in range(frame_num):
            depth = depth_file.read(DEPTH_FRAME_SIZE)
            depth = struct.unpack('H' * (512 * 424), depth)
            depth = np.reshape(depth, (424, 512))
            png_file = png_path + "frame_" + str(f).zfill(3) + ".png"
            cv2.imwrite(png_file, depth, [cv2.IMWRITE_PNG_COMPRESSION, 9])


def convert_png2bin(png_path, bin_file):

    with open(bin_file, 'wb') as bin:
        for i in range(len(os.listdir(png_path))):
            png_file = png_path + "frame_" + str(i).zfill(3) + ".png"
            if not os.path.isfile(png_file):
                print("png 파일을 불러올 수 없습니다.")
                break
            img = Image.open(png_file)
            img_data = np.asarray(img)
            for r in range(len(img_data)):
                for c in range(len(img_data[0])):
                    bin.write(struct.pack('H', img_data[r][c]))


def convert_body2png(body_file, png_path):

    frame_num = int(os.path.getsize(body_file)/BODY_FRAME_SIZE)
    if not os.path.isdir(png_path):
        os.makedirs(png_path)

    with open(body_file, 'rb') as file:
        for f in range(frame_num):
            body_data = file.read(BODY_FRAME_SIZE)
            body_data = struct.unpack('B' * (512 * 424), body_data)
            body_data = np.reshape(body_data, (424, 512))
            png_file = png_path + "frame_" + str(f).zfill(3) + ".png"
            cv2.imwrite(png_file, body_data, [cv2.IMWRITE_PNG_COMPRESSION, 9])


def convert_png2body(png_path, body_file):

    with open(body_file, 'wb') as body:
        for i in range(len(os.listdir(png_path))):
            png_file = png_path + "frame_" + str(i).zfill(3) + ".png"
            if not os.path.isfile(png_file):
                print("png 파일을 불러올 수 없습니다.")
                break
            img = Image.open(png_file)
            img_data = np.asarray(img)
            for r in range(len(img_data)):
                for c in range(len(img_data[0])):
                    body.write(struct.pack('B', img_data[r][c]))



if __name__ == '__main__':
    main()


