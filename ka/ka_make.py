import AiR_2017
import arrange_2017
import os
import nao
import transform_2017

root = "F:/2017/new/"
new_root = "F:/2017/new/"

cameras = ["C%03d" %c for c in range(2, 3)]
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
                file_name = camera + people + action + scene + ".dat"
                if not os.path.isfile(path+file_name):
                    error_file.append(file_name)
                    continue

                try:
                    nao.make_nao(path+file_name)


                except:

                    error_file.append(file_name)


                cnt += 1
                print('({} / {})'.format(cnt, 2500), end=' ')
                print("에러파일 개수:%d" % len(error_file))


print(error_file)

