import os

root = "F:/2017/"

cameras = ["C%03d" %c for c in range(1, 4)]
peoples = ["P%03d" %p for p in range(51, 101)]
actions = ["A%03d" %a for a in range(1, 11)]
scenes = ["S%03d" %s for s in range(1, 6)]
error_file = list()
cnt = 0
ccnt = 0
file_list = list()
try:
    for camera in cameras:
        path = root + "arranged_body_file/"+ camera + "/"

        for people in peoples:
            for action in actions:
                for scene in scenes:

                    file_name = camera + people + action + scene + ".body"
                    if not os.path.isfile(path+file_name):
                        error_file.append(file_name)

                    new_file_name = file_name.replace(".body", ".dat")
                    try:
                        os.rename(path+file_name, path+new_file_name)
                    except:
                        error_file.append(new_file_name)


                    cnt += 1


                    print( "%03d / 7500" %cnt)

except:
    error_file.append(file_name)

print(error_file)