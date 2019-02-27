import os
import AiR_2017
import math


root = "F:/2017/arranged_body_file/"

cameras = ["C%03d" %c for c in range(1,4)]


cnt = 0
for camera in cameras:
    path = root + camera + "/"
    files = os.listdir(path)
    for file in files:
        body_info = AiR_2017.read_body(path + file)

        for f in range(len(body_info)):
            if f > 0:
                for b in range(len(body_info[f])):
                    curr = body_info[f][b]
                    prev = body_info[f-1][b]
                    diff = math.fabs(curr['joints'][0]['depthX'] - prev['joints'][0]['depthX']) + \
                           math.fabs(curr['joints'][0]['depthY'] - prev['joints'][0]['depthY'])

                    if prev['joints'][0]["depthX"] != 0 and curr['joints'][0]["depthX"] != 0 and diff > 30:
                        print("{} {}".format(file, f))
                        cnt += 1


print("count: %d" %cnt)
print("Scan Completed")