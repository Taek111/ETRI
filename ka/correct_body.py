"""
correcting (or removing) inaccurate data
"""
from pre_processing.utils import AiR, NTU, body

data = AiR  # [AiR, NTU]
b = 0
Path = "C:/Users/wrko/Desktop/C001/"
newPath = "C:/Users/wrko/Desktop/C001/new/"
BODY_PART =  {'LA': [5, 6, 7, 21, 22],
              'RA': [9, 10, 11, 23, 24],
              'BA': [5, 6, 7, 21, 22, 9, 10, 11, 23, 24],
              'LL': [13, 14],
              'RL': [17, 18],
              'ALL': [j for j in range(25)],
              'LS': [4],
              'RS': [8]}


def main():
    state = 1

    while state:
        command = input("Press \'file_name mode(I/F/E) begin end (reference) part\':")
        n = command.split(" ")
        body_info = data.read_body(Path+n[0]+".joints")
        newFile = newPath + n[0] + ".joints"
        com_list = command.split("AND ")

        for c in com_list:
            i = c.split(" ")
            if len(i[0]) < 3:
                i.insert(0, n[0])

#INTERPOLATION MODE                (filename, mode, start frame, end frame, body part)

            if i[1] == 'I':
                for f in range(int(i[2]), int(i[3])+1):
                    interpolate(body_info[int(i[2])-1][b], body_info[int(i[3])+1][b], body_info[f][b],
                                (f-int(i[2])) / (int(i[3]) - int(i[2])), BODY_PART[i[4]])

#FIX MODE                          (filename, mode, start frame, end frame , reference frame, body part)
            elif i[1] == 'F':
                fix_body(body_info, int(i[2]), int(i[3]), BODY_PART[i[5]], int(i[4]))

#EXTRACT MODE                      (filename, mode, start frame, end frame ,reference file, reference frame, body part)
            elif i[1] == 'E':
                ref_body_info = data.read_body(Path+i[4]+".joints")
                for f in range(int(i[2]),int(i[3])+1):
                    for j in BODY_PART[i[6]]:
                        body_info[f][b]["joints"][j] = ref_body_info[int(i[5])][b]["joints"][j]

            else:
                print("다시 입력해주세요")
                continue

#WRITE BODY
        data.write_body(newFile, body_info)






def fix_body(body_info, begin, end, part, ref_frame):
    for f in range(begin, end+1):
        for j in part:
            body_info[f][b]["joints"][j] = body_info[ref_frame][b]["joints"][j]




def interpolate(begin, end, out, step,part):
    out["bodyID"] = end["bodyID"]
    out["trackingState"] = end["trackingState"]
    out["leanX"] = end["leanX"]
    out["leanY"] = end["leanY"]

    # 3D location of the joint j
    for j in part:
        out["joints"][j]["x"] = begin["joints"][j]["x"] + (end["joints"][j]["x"] - begin["joints"][j]["x"]) * step
        out["joints"][j]["y"] = begin["joints"][j]["y"] + (end["joints"][j]["y"] - begin["joints"][j]["y"]) * step
        out["joints"][j]["z"] = begin["joints"][j]["z"] + (end["joints"][j]["z"] - begin["joints"][j]["z"]) * step
        out["joints"][j]["trackingState"] = end["joints"][j]["trackingState"]

    # 2D location of the joint j in corresponding RGB frame
    for j in part:
        out["joints"][j]["orientationX"] = begin["joints"][j]["orientationX"] + (end["joints"][j]["orientationX"] - begin["joints"][j]["orientationX"]) * step
        out["joints"][j]["orientationY"] = begin["joints"][j]["orientationY"] + (end["joints"][j]["orientationY"] - begin["joints"][j]["orientationY"]) * step
        out["joints"][j]["orientationZ"] = begin["joints"][j]["orientationZ"] + (end["joints"][j]["orientationZ"] - begin["joints"][j]["orientationZ"]) * step
        out["joints"][j]["orientationW"] = begin["joints"][j]["orientationW"] + (end["joints"][j]["orientationW"] - begin["joints"][j]["orientationW"]) * step

    # 2D location of the joint j in corresponding depth frame
    for j in part:
        out["joints"][j]["depthX"] = begin["joints"][j]["depthX"] + (end["joints"][j]["depthX"] - begin["joints"][j]["depthX"]) * step
        out["joints"][j]["depthY"] = begin["joints"][j]["depthY"] + (end["joints"][j]["depthY"] - begin["joints"][j]["depthY"]) * step

if __name__ == "__main__":
    main()
