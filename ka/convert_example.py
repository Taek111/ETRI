import os
import convert2png

root = "F:/2017/data/"
png_root = "C:/Users/wrko/Desktop/compressed_file/bin/2017/"

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

                file_name = camera + people + action + scene + ".bin"
                path = root + camera + "/"
                png_path = png_root + camera + "/" + file_name.replace(".bin", "_depth/")

                if not os.path.isfile(path+file_name):
                    error_file.append(file_name)
                    continue

                try:
                    convert2png.convert_bin2png(path+file_name, png_path)

                except:
                    error_file.append(file_name)
                    print("변환오류(%s)"%file_name)

                cnt += 1
                print('({} / {})'.format(cnt, 7500), end=' ')
                print("에러파일 개수:%d" % len(error_file))


print(error_file)
